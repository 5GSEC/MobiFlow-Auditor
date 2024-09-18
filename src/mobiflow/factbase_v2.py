import threading
import logging
from .mobiflow_v2 import *
from .encoding import *
from .constant import *

class FactBase:

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.facts = {}
            self.nr_cell_id_counter = 0
            self.bs_name_map = {}
            self.initialized = True

    def __new__(cls, *args, **kwargs):
        # singleton class
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def update_mobiflow(self) -> list:
        mf_list = []
        while True:
            write_should_end = True
            for ue in self.get_all_ue():
                if ue.should_report:
                    write_should_end = False
                    # generate UE mobiflow record
                    umf, prev_rrc, prev_nas, prev_rrc_sec, rrc, nas, sec = ue.generate_mobiflow()
                    mf_list.append(umf)
                    # update BS
                    bs = self.get_bs(umf.nr_cell_id)
                    if bs is not None:
                        bs.update_counters(prev_rrc, prev_nas, prev_rrc_sec, rrc, nas, sec)
            for bs in self.get_all_bs():
                if bs.should_report:
                    write_should_end = False
                    # generate BS mobiflow record
                    bmf = bs.generate_mobiflow()
                    mf_list.append(bmf)
            if write_should_end:  # end writing if no mobiflow record to update
                break
        return mf_list

    def add_bs(self, bs: BS):
        with self._lock:
            if not self.facts.keys().__contains__(bs.nr_cell_id):
                bs.ts = time.time() * 1000
                bs.nr_cell_id = self.nr_cell_id_counter
                self.bs_name_map[bs.name] = bs.nr_cell_id
                self.nr_cell_id_counter += 1
                self.facts[bs.nr_cell_id] = bs
            else:
                self.facts[bs.nr_cell_id].ts = time.time()

    def add_ue(self, bsId, ue: UE):
        with self._lock:
            if not self.facts.keys().__contains__(bsId):
                print("[Error] BS id not exist when trying to add UE: %s" % bsId)
                return
            else:
                ue.ts = time.time() * 1000
                ue.nr_cell_id = bsId
                if self.facts[bsId] is not None:
                    self.facts[bsId].add_ue(ue)

    def get_bs_index_by_name(self, bs_name: str):
        if self.bs_name_map.keys().__contains__(bs_name):
            return self.bs_name_map[bs_name]
        else:
            return -1

    # BS related operations
    def get_all_bs(self):
        bss = []
        for bsId in self.facts.keys():
            bss.append(self.facts[bsId])
        return bss

    def get_bs(self, bsId):
        return self.facts.get(bsId)

    def remove_bs(self, bsId):
        if bsId in self.facts.keys():
            del self.facts[bsId]
            return True
        else:
            return False

    # UE related operations
    def get_all_ue(self):
        ues = []
        for bsId in self.facts.keys():
            ues += self.facts[bsId].ue
        return ues

    def get_ue(self, rnti: int):
        ues = self.get_all_ue()
        for ue in ues:
            if ue.rnti == rnti:
                return ue
        return None

    def remove_ue(self, rnti: int):
        ue_to_remove = None
        for bsId in self.facts.keys():
            for ue in self.facts[bsId].ue:
                if ue.rnti == rnti:
                    ue_to_remove = ue
                    break
            if ue_to_remove is not None:
                self.facts[bsId].ue.remove(ue_to_remove)
                return True
        return False


    def update_fact_base(self, kpm_measurement_dict: dict, me_id: str):
        if int(kpm_measurement_dict["gnb_du_ue_f1ap_id"]) == 0:
            return  # ignore empty indication records

        logging.info(f"[FactBase] KPM indication reported metrics: {kpm_measurement_dict}")
        # update fact base
        ue = UE()
        ue.timestamp = int(kpm_measurement_dict["timestamp"])
        ue.nr_cell_id = int(kpm_measurement_dict["nr_cell_id"])
        ue.gnb_du_ue_f1ap_id = int(kpm_measurement_dict["gnb_du_ue_f1ap_id"])
        ue.gnb_cu_ue_f1ap_id = int(kpm_measurement_dict["gnb_cu_ue_f1ap_id"])
        ue.rnti = int(kpm_measurement_dict["rnti"])
        ue.s_tmsi = int(kpm_measurement_dict["s_tmsi"])
        ue.establish_cause = int(kpm_measurement_dict["establish_cause"])
        ue.cipher_alg = int(kpm_measurement_dict["cipher_alg"])
        ue.integrity_alg = int(kpm_measurement_dict["integrity_alg"])
        msg_len = UE_MOBIFLOW_ITEM_LEN - UE_META_DATA_ITEM_LEN
        for i in range(1, msg_len+1):
            msg_val = int(kpm_measurement_dict[f"msg{i}"])
            if msg_val & 1 == 1:
                # RRC
                dcch = (msg_val >> 1) & 1
                downlink = (msg_val >> 2) & 1
                msg_id = (msg_val >> 3)
                msg_name = decode_rrc_msg(dcch, downlink, msg_id, 1)
                if msg_name != "" and msg_name is not None:
                    ue.msg_trace.append(msg_name)
                elif msg_id != 0:
                    logging.error(f"[FactBase] Invalid RRC Msg dcch={dcch}, downlink={downlink} {msg_id}")
            else:
                # NAS
                dis = (msg_val >> 1) & 1
                msg_id = (msg_val >> 2)
                msg_name = decode_nas_msg(dis, msg_id, 1)
                if msg_name != "" and msg_name is not None:
                    ue.msg_trace.append(msg_name)
                elif msg_id != 0:
                    logging.error(f"[FactBase] Invalid NAS Msg: discriminator={dis} {msg_id}")

        self.add_ue(self.get_bs_index_by_name(me_id), ue)
        
