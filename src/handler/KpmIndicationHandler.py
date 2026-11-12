from mdclogpy import Level
from ricxappframe.xapp_frame import RMRXapp
from ..asn1 import AsnProxy
from ..manager import SdlManager
from .IndicationHandler import E2Indication, ServiceModelIndicationHandler
from ..utils.utils import find_all_values
from ..mobiflow import UE_MOBIFLOW_NS, parse_measurement_into_mobiflow

class KpmIndicationHandler(ServiceModelIndicationHandler):
    """Handles E2SM-KPM indications (dispatched by IndicationHandler)."""

    def __init__(self, rmr_xapp: RMRXapp, asn_proxy: AsnProxy, sdl_mgr: SdlManager):
        self.logger = rmr_xapp.logger
        self.logger.set_level(Level.INFO)
        self.asn_proxy = asn_proxy
        self.sdl_mgr = sdl_mgr

    def handle_indication(self, indication: E2Indication):
        kpm_indication_msg_hex_payload = indication.message_hex
        kpm_indication_msg_dict = self.asn_proxy.decode_e2sm_kpm_indication_message(kpm_indication_msg_hex_payload)
        if not kpm_indication_msg_dict:
            self.logger.error(f"KPM indication message decode error from {kpm_indication_msg_hex_payload}")
            return

        # extract measurement items
        kpm_measurement_names = find_all_values(kpm_indication_msg_dict, "measName")
        kpm_measurement_values = find_all_values(kpm_indication_msg_dict, "integer")

        if len(kpm_measurement_names) != len(kpm_measurement_values):
            self.logger.error(f"KPM indication message items mismatched, names {kpm_measurement_names}, values: {kpm_measurement_values}")
            return

        kpm_measurement_dict = {}
        for i in range(len(kpm_measurement_values)):
            kpm_measurement_dict[kpm_measurement_names[i]] = kpm_measurement_values[i]

        self.logger.info(f"KPM indication reported metrics: {kpm_measurement_dict}")

        ue_mfs = parse_measurement_into_mobiflow(kpm_measurement_dict)
        for mf in ue_mfs:
            self.logger.info(f"[MobiFlow] Storing MobiFlow record to SDL {mf.__str__()}")
            self.sdl_mgr.store_data_to_sdl(UE_MOBIFLOW_NS, str(mf.msg_id), mf.__str__())

        # fb = FactBase()
        # fb.update_fact_base(kpm_measurement_dict, me_id)
        # mf_list = fb.update_mobiflow()
        # for mf in mf_list:
        #     # store Mobiflow to SDL
        #     self.logger.info(f"[FactBase] Storing MobiFlow record to SDL {mf.__str__()}")
        #     if mf.msg_type == "UE":
        #         self.sdl_mgr.store_data_to_sdl(UE_MOBIFLOW_NS, str(mf.msg_id), mf.__str__())
        #     elif mf.msg_type == "BS":
        #         self.sdl_mgr.store_data_to_sdl(BS_MOBIFLOW_NS, str(mf.msg_id), mf.__str__())
        #     else:
        #         raise NotImplementedError
