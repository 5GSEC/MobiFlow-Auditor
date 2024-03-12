import json
import binascii
from ricxappframe.xapp_frame import RMRXapp, rmr
from mdclogpy import Level
from ._BaseHandler import _BaseHandler
from ..asn1 import AsnProxy
from ..utils.utils import find_all_values

class KpmIndicationHandler(_BaseHandler):

    def __init__(self, rmr_xapp: RMRXapp, msgtype, asn_proxy: AsnProxy):
        super().__init__(rmr_xapp, msgtype)
        self.logger.set_level(Level.INFO)
        self.asn_proxy = asn_proxy

    def request_handler(self, rmr_xapp, summary, sbuf):
        """
                Handles Indication messages.

                Parameters
                ----------
                rmr_xapp: rmr Instance Context

                summary: dict (required)
                    buffer content

                sbuf: str (required)
                    length of the message
        """
        binary_payload = summary[rmr.RMR_MS_PAYLOAD]
        # print(f"KpmIndicationHandler.request_handler:: Handler processing request {binary_payload}")
        # start decoding
        e2ap_hex_payload = str(binascii.hexlify(binary_payload), "utf-8")
        e2ap_dict = self.asn_proxy.decode_e2ap_pdu(e2ap_hex_payload)
        if e2ap_dict is None or e2ap_dict is {}:
            self.logger.error(f"E2AP payload decode error from {e2ap_hex_payload}")
            return

        kpm_indication_msg_hex_payload = find_all_values(e2ap_dict, "RICindicationMessage")
        if kpm_indication_msg_hex_payload is None or kpm_indication_msg_hex_payload is []:
            self.logger.error(f"KPM indication message not found from E2AP structure {e2ap_dict}")
            return

        kpm_indication_msg_hex_payload = kpm_indication_msg_hex_payload[0].strip().replace(" ", "").replace("\n", "")
        kpm_indication_msg_dict = self.asn_proxy.decode_e2sm_kpm_indication_message(kpm_indication_msg_hex_payload)
        if kpm_indication_msg_dict is None or kpm_indication_msg_dict is {}:
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

        # try:
        #     req = json.loads(summary[rmr.RMR_MS_PAYLOAD])  # input should be a json encoded as bytes
        #     self.logger.info("KpmIndicationHandler.request_handler:: Handler processing request")
        # except (json.decoder.JSONDecodeError, KeyError):
        #     self.logger.error("KpmIndicationHandler.request_handler:: Handler failed to parse request")
        #     return

        # if self.verify_indication(req):
        #     self.logger.info("KpmIndicationHandler.request_handler:: Handler processed request: {}".format(req))
        # else:
        #     self.logger.error("KpmIndicationHandler.request_handler:: Request verification failed: {}".format(req))
        #     return
        # self.logger.debug("KpmIndicationHandler.request_handler:: Request verification success: {}".format(req))

        self._rmr_xapp.rmr_free(sbuf)

    def verify_indication(self, req: dict):
        # TODO
        return True

