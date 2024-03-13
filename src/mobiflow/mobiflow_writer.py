import datetime
from .factbase import FactBase

class MobiFlowWriter:
    def __init__(self):
        self.ue_mobiflow_table_name = "ue_mobiflow"
        self.bs_mobiflow_table_name = "bs_mobiflow"

    def write_mobiflow(self, fb: FactBase) -> None:
        while True:
            write_should_end = True
            for ue in fb.get_all_ue():
                if ue.should_report:
                    write_should_end = False
                    # generate UE mobiflow record
                    umf, prev_rrc, prev_nas, prev_sec, rrc, nas, sec = ue.generate_mobiflow()
                    print("[MobiFlow] Writing UE Mobiflow: " + umf.__str__())
                    # update BS
                    bs = fb.get_bs(umf.bs_id)
                    if bs is not None:
                        bs.update_counters(prev_rrc, prev_nas, prev_sec, rrc, nas, sec)
            for bs in fb.get_all_bs():
                if bs.should_report:
                    write_should_end = False
                    # generate BS mobiflow record
                    bmf = bs.generate_mobiflow()
                    print("[MobiFlow] Writing BS Mobiflow: " + bmf.__str__())
            if write_should_end:  # end writing if no mobiflow record to update
                break

    @staticmethod
    def timestamp2str(ts):
        return datetime.datetime.fromtimestamp(ts/1000).__str__() # convert ms into s


