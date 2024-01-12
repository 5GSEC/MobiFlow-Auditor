import datetime
from pymongo import MongoClient
from .lockutil import *
from .mobiflow import *
from .factbase import FactBase

class MobiFlowWriter:
    def __init__(self, csv_file, db_name, port):
        self.csv_file = csv_file
        self.db_name = db_name
        # init csv file if necessary
        if self.csv_file != "":
            self.clear_file()
        self.last_write_time = 0
        # init db if necessary
        self.client = None
        self.db = None
        self.db_port = port
        self.ue_mobiflow_table_name = "ue_mobiflow"
        self.bs_mobiflow_table_name = "bs_mobiflow"
        if self.db_name != "":
            self.init_db()
        # start a new threat to track maintenance event
        # self.maintenance_time_threshold = maintenance_time_threshold  # in ms
        # self.maintenance_thread = threading.Thread(target=self.pbest_write_maintenance)
        # self.maintenance_thread.start()

    def init_db(self):
        self.client = MongoClient(f"mongodb://{self.db_name}:{self.db_port}/")
        self.db = self.client[f"{self.db_name}"]
        #
        # self.db = sqlite3.connect(self.db_name)
        # cursor = self.db.cursor()
        # # Create tables if not exist
        # cursor.execute(self.generate_create_table_statement(UEMobiFlow(), self.ue_mobiflow_table_name))
        # cursor.execute(self.generate_create_table_statement(BSMobiFlow(), self.bs_mobiflow_table_name))
        # self.db.commit()

    @staticmethod
    def generate_create_table_statement(class_instance, table_name):
        attributes = []
        for a in class_instance.__dict__.keys():
            if str(a) == "":
                attributes.append(" ")  # avoid parse error in C
            else:
                attributes.append(str(a))

        columns = []
        for attr in attributes:
            value = getattr(class_instance, attr)
            data_type = "VARCHAR(255)" if isinstance(value, str) else "INT" if isinstance(value, int) else "TEXT"
            columns.append(f"{attr} {data_type}")

        create_table_statement = f"CREATE TABLE {table_name} (\n    {', '.join(columns)}\n);"
        return create_table_statement

    @staticmethod
    def generate_insert_statement(class_instance, table_name):
        attributes = []
        for a in class_instance.__dict__.keys():
            if str(a) == "":
                attributes.append(" ")  # avoid parse error in C
            else:
                attributes.append(str(a))

        columns = []
        values = []
        for attr in attributes:
            value = getattr(class_instance, attr)
            columns.append(attr)
            if isinstance(value, str):
                values.append(f"'{value}'")
            else:
                values.append(str(value))

        insert_statement = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
        return insert_statement

    @staticmethod
    def generate_key_value_mobiflow(class_instance):
        attributes = {}
        for a in class_instance.__dict__.keys():
            if str(a) != "":
                attributes[str(a)] = getattr(class_instance, str(a))
        return attributes

    def clear_db(self):
        if self.db is None:
            return
        cursor = self.db.cursor()
        cursor.execute(f"DELETE FROM {self.ue_mobiflow_table_name};")
        cursor.execute(f"DELETE FROM {self.ue_mobiflow_table_name};")
        self.db.commit()

    def close_db(self):
        if self.db is not None:
            self.db.close()

    def write_mobiflow(self, fb: FactBase) -> None:
        if self.csv_file != "":
            self.write_mobiflow_csv(fb)
        elif self.db_name != "":
            self.write_mobiflow_db(fb)

    # write mobiflow to a CSV file
    def write_mobiflow_csv(self, fb: FactBase) -> None:
        f = open(self.csv_file, "a")
        while True:
            write_should_end = True
            for ue in fb.get_all_ue():
                if ue.should_report:
                    write_should_end = False
                    # generate UE mobiflow record
                    umf, prev_rrc, prev_nas, prev_sec, rrc, nas, sec = ue.generate_mobiflow()
                    logging.info("[MobiFlow] Writing UE Mobiflow to CSV: " + umf.__str__())
                    self.last_write_time = get_time_ms()
                    # Assign lock
                    acquire_lock(f)
                    f.write(umf.__str__() + "\n")
                    f.flush()
                    release_lock(f)
                    # update BS
                    bs = fb.get_bs(umf.bs_id)
                    if bs is not None:
                        bs.update_counters(prev_rrc, prev_nas, prev_sec, rrc, nas, sec)
            for bs in fb.get_all_bs():
                if bs.should_report:
                    write_should_end = False
                    # generate BS mobiflow record
                    bmf = bs.generate_mobiflow()
                    logging.info("[MobiFlow] Writing BS Mobiflow to CSV: " + bmf.__str__())
                    self.last_write_time = get_time_ms()
                    # Assign lock
                    acquire_lock(f)
                    f.write(bmf.__str__() + "\n")
                    f.flush()
                    release_lock(f)
            if write_should_end:  # end writing if no mobiflow record to update
                break
        f.close()

    # write mobiflow to a database
    def write_mobiflow_db(self, fb: FactBase) -> None:
        collection_bs_mobiflow = self.db[self.bs_mobiflow_table_name]
        collection_ue_mobiflow = self.db[self.ue_mobiflow_table_name]
        while True:
            write_should_end = True
            for ue in fb.get_all_ue():
                if ue.should_report:
                    write_should_end = False
                    # generate UE mobiflow record
                    umf, prev_rrc, prev_nas, prev_sec, rrc, nas, sec = ue.generate_mobiflow()
                    self.last_write_time = get_time_ms()
                    # mongodb will handle concurrent write
                    ue_mf_data = self.generate_key_value_mobiflow(umf)
                    logging.info("[MobiFlow] Writing UE Mobiflow to DB: " + str(ue_mf_data))
                    collection_ue_mobiflow.insert_one(ue_mf_data)
                    # update BS
                    bs = fb.get_bs(umf.bs_id)
                    if bs is not None:
                        bs.update_counters(prev_rrc, prev_nas, prev_sec, rrc, nas, sec)
            for bs in fb.get_all_bs():
                if bs.should_report:
                    write_should_end = False
                    # generate BS mobiflow record
                    bmf = bs.generate_mobiflow()
                    self.last_write_time = get_time_ms()
                    # mongodb will handle concurrent write
                    bs_mf_data = self.generate_key_value_mobiflow(bmf)
                    logging.info("[MobiFlow] Writing BS Mobiflow to DB: " + str(bs_mf_data))
                    collection_bs_mobiflow.insert_one(bs_mf_data)
            if write_should_end:  # end writing if no mobiflow record to update
                break

    def clear_file(self) -> None:
        f = open(self.csv_file, "w")
        acquire_lock(f)
        f.write("")
        release_lock(f)
        f.close()

    @staticmethod
    def timestamp2str(ts):
        return datetime.datetime.fromtimestamp(ts/1000).__str__() # convert ms into s
