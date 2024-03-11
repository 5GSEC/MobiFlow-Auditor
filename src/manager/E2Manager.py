from ricxappframe.xapp_frame import RMRXapp
from mdclogpy import Level
from ._BaseManager import _BaseManager
from .onos_e2_sm.e2smkpmv2.v2 import E2SmKpmRanfunctionDescription

import binascii

class E2Manager(_BaseManager):

    def __init__(self, rmr_xapp: RMRXapp) -> None:
        super().__init__(rmr_xapp)
        self.logger.set_level(Level.INFO)

    def decode_ran_function_description_hex_str(self, ran_func_description_hex_str: str):
        hex_bytes = self.hex2str(ran_func_description_hex_str)
        e2sm_kpm_ran_function_description = E2SmKpmRanfunctionDescription()
        print(e2sm_kpm_ran_function_description.to_dict())
        try:
            # Parse the bytes using the protobuf message class
            e2sm_kpm_ran_function_description = e2sm_kpm_ran_function_description.parse(hex_bytes)
        except Exception as e:
            self.logger.error(f"[decode_ran_function_description_hex_str] decode error {e}")
            return None

        print(e2sm_kpm_ran_function_description.ran_function_name.ran_function_e2_sm_oid)
        return e2sm_kpm_ran_function_description

    @staticmethod
    def hex2str(hex_str):
        return binascii.unhexlify(hex_str)

