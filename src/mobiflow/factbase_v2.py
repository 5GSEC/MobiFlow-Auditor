import threading
import logging
from .mobiflow_v2 import *
from .encoding import *
from .constant import *
from ..utils import get_time_sec

class FactBase:

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.facts = {}
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

    def add_or_update_bs(self, bs: BS):
        with self._lock:
            if not self.facts.keys().__contains__(bs.nr_cell_id):
                bs.ts = get_time_sec()
                self.bs_name_map[bs.name] = bs.nr_cell_id
                self.facts[bs.nr_cell_id] = bs
                self.facts[bs.nr_cell_id].should_report = True
            else:
                if self.facts[bs.nr_cell_id].status != bs.status:
                    self.facts[bs.nr_cell_id].ts = get_time_sec()
                    self.facts[bs.nr_cell_id].status = bs.status # update BS status
                    self.facts[bs.nr_cell_id].should_report = True

    def add_ue(self, bsId, ue: UE):
        with self._lock:
            if not self.facts.keys().__contains__(bsId):
                print("[Error] BS id not exist when trying to add UE: %s" % bsId)
                return
            else:
                ue.ts = get_time_sec()
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
        ue.rrc_cipher_alg = int(kpm_measurement_dict["rrc_cipher_alg"])
        ue.integrity_alg = int(kpm_measurement_dict["integrity_alg"])
        msg_len = UE_MOBIFLOW_ITEM_LEN - UE_META_DATA_ITEM_LEN

        for i in range(1, msg_len+1):
            msg_val = int(kpm_measurement_dict[f"msg{i}"])
            rrc_msg_id = (msg_val >> 25) & 0x1F
            dcch_ccch = (msg_val >> 24) & 0x01               # 1 bit
            downlink_uplink = (msg_val >> 23) & 0x01         # 1 bit
            nas_msg_id = (msg_val >> 17) & 0x3F              # 6 bits
            emm_esm = (msg_val >> 16) & 0x01                 # 1 bit
            rrc_state = (msg_val >> 14) & 0x03               # 2 bits
            nas_state = (msg_val >> 12) & 0x03               # 2 bits
            sec_state = (msg_val >> 10) & 0x03               # 2 bits
            reserved_field_1 = (msg_val >> 8) & 0x03         # 2 bits
            reserved_field_2 = (msg_val >> 6) & 0x03         # 2 bits
            reserved_field_3 = (msg_val >> 4) & 0x03         # 2 bits
            reserved_field_4 = (msg_val >> 2) & 0x03         # 2 bits
            reserved_field_5 = msg_val & 0x03                # 2 bits

            rrc_msg_name = decode_rrc_msg(dcch_ccch, downlink_uplink, rrc_msg_id, 1)
            if rrc_msg_name != "" and rrc_msg_name is not None:
                ue.msg_trace.append(rrc_msg_name)
            elif rrc_msg_id != 0:
                logging.error(f"[FactBase] Invalid RRC Msg dcch={dcch_ccch}, downlink={downlink_uplink} {rrc_msg_id}")

            if emm_esm != 0:
                nas_msg_id = nas_msg_id + list(nas_emm_code_NR.keys())[0] # add nas message offset
                nas_msg_name = decode_nas_msg(emm_esm, nas_msg_id, 1)
                if nas_msg_name != "" and nas_msg_name is not None:
                    ue.msg_trace.append(nas_msg_name)
                elif nas_msg_id != 0:
                    logging.error(f"[FactBase] Invalid NAS Msg: discriminator={emm_esm} {nas_msg_id}")

        # for i in range(1, msg_len+1):
        #     msg_val = int(kpm_measurement_dict[f"msg{i}"])
        #     if msg_val & 1 == 1:
        #         # RRC
        #         dcch = (msg_val >> 1) & 1
        #         downlink = (msg_val >> 2) & 1
        #         msg_id = (msg_val >> 3)
        #         msg_name = decode_rrc_msg(dcch, downlink, msg_id, 1)
        #         if msg_name != "" and msg_name is not None:
        #             ue.msg_trace.append(msg_name)
        #         elif msg_id != 0:
        #             logging.error(f"[FactBase] Invalid RRC Msg dcch={dcch}, downlink={downlink} {msg_id}")
        #     else:
        #         # NAS
        #         dis = (msg_val >> 1) & 1
        #         msg_id = (msg_val >> 2)
        #         msg_name = decode_nas_msg(dis, msg_id, 1)
        #         if msg_name != "" and msg_name is not None:
        #             ue.msg_trace.append(msg_name)
        #         elif msg_id != 0:
        #             logging.error(f"[FactBase] Invalid NAS Msg: discriminator={dis} {msg_id}")

        self.add_ue(self.get_bs_index_by_name(me_id), ue)
        
