import sqlite3
import logging
from .protos.mobiflow_service_pb2_grpc import MobiFlowQueryServicer
from .protos.mobiflow_service_pb2 import MobiFlowStreamResponse

class MobiFlowService(MobiFlowQueryServicer):
    def __init__(self, db_path, rpc_port=50051):
        self.db_path = db_path
        self.rpc_port = rpc_port
        self.MOBIFLOW_DELIMITER = ";"

    def open_db_conn(self):
        # Connect to SQLite database (local.db)
        if self.db_path is not None and self.db_path != "":
            return sqlite3.connect(self.db_path, check_same_thread=False)
        else:
            logging.error(f"[Server] Invalid DB Path {self.db_path}")
            return None

    def MobiFlowStream(self, request, context):
        request_initiator = request.name
        request_table = request.table
        logging.info(f"[Server] MobiFlow Streaming Request from {request_initiator} for {request_table}")

        # Read data from the database
        db = self.open_db_conn()
        if db is None:
            logging.error(f"[Server] DB instance is NULL, exiting...")
            return
        cursor = db.cursor()
        cursor.execute(f'SELECT * FROM {request_table} ORDER BY timestamp DESC')
        for row in cursor.fetchall():
            str_list = [str(a) for a in row]
            msg = str(self.MOBIFLOW_DELIMITER.join(str_list))
            yield MobiFlowStreamResponse(message=msg)
        db.close()
