"""
Handles RIC indications at the E2AP layer: decodes the E2AP PDU and hands the
indication header and message to the handler of the service model the RAN
function was subscribed with (E2SM-KPM or E2SM-CP).
"""

import binascii
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from mdclogpy import Level
from ricxappframe.xapp_frame import RMRXapp, rmr
from ..asn1 import AsnProxy
from ..manager import SubscriptionManager
from ..utils.constants import Constants
from ..utils.utils import find_all_values
from ._BaseHandler import _BaseHandler


@dataclass
class E2Indication:
    """The E2AP fields of a RIC indication."""
    me_id: str                      # E2 node inventory name
    ran_function_id: int
    action_id: Optional[int]
    sn: Optional[int]               # RIC indication SN
    requestor_id: Optional[int]
    instance_id: Optional[int]
    header_hex: str                 # RIC indication header (service model encoded)
    message_hex: str                # RIC indication message (service model encoded)


class ServiceModelIndicationHandler(ABC):
    """Handles the indications of one service model."""

    @abstractmethod
    def handle_indication(self, indication: E2Indication):
        pass


def _first_int(d: dict, key: str) -> Optional[int]:
    values = find_all_values(d, key)
    try:
        return int(values[0]) if values else None
    except (TypeError, ValueError):
        return None


def _first_hex(d: dict, key: str) -> str:
    values = find_all_values(d, key)
    if not values or not isinstance(values[0], str):
        return ""
    return "".join(values[0].split())


class IndicationHandler(_BaseHandler):

    def __init__(self, rmr_xapp: RMRXapp, msgtype, asn_proxy: AsnProxy, sub_mgr: SubscriptionManager,
                 sm_handlers: dict):
        """sm_handlers: service model (Constants.SM_*) -> ServiceModelIndicationHandler"""
        super().__init__(rmr_xapp, msgtype)
        self.logger.set_level(Level.INFO)
        self.asn_proxy = asn_proxy
        self.sub_mgr = sub_mgr
        self.sm_handlers = sm_handlers

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
        try:
            indication = self.decode_indication(summary)
            if indication is not None:
                self.dispatch(indication)
        except Exception as e:  # never let one bad indication stop the RMR loop
            self.logger.error(f"IndicationHandler: failed to handle indication: {e!r}")
        finally:
            self._rmr_xapp.rmr_free(sbuf)

    def decode_indication(self, summary) -> Optional[E2Indication]:
        binary_payload = summary[rmr.RMR_MS_PAYLOAD]
        me_id = str(summary[rmr.RMR_MS_MEID], "utf-8")
        e2ap_hex_payload = str(binascii.hexlify(binary_payload), "utf-8")
        e2ap_dict = self.asn_proxy.decode_e2ap_pdu(e2ap_hex_payload)
        if not e2ap_dict:
            self.logger.error(f"E2AP payload decode error from {e2ap_hex_payload}")
            return None
        if not find_all_values(e2ap_dict, "RICindication"):
            self.logger.error(f"E2AP PDU from {me_id} is not a RIC indication: {e2ap_dict}")
            return None

        ran_function_id = _first_int(e2ap_dict, "RANfunctionID")
        message_hex = _first_hex(e2ap_dict, "RICindicationMessage")
        if ran_function_id is None or not message_hex:
            self.logger.error(f"RAN function ID or indication message not found from E2AP structure {e2ap_dict}")
            return None
        return E2Indication(me_id=me_id,
                            ran_function_id=ran_function_id,
                            action_id=_first_int(e2ap_dict, "RICactionID"),
                            sn=_first_int(e2ap_dict, "RICindicationSN"),
                            requestor_id=_first_int(e2ap_dict, "ricRequestorID"),
                            instance_id=_first_int(e2ap_dict, "ricInstanceID"),
                            header_hex=_first_hex(e2ap_dict, "RICindicationHeader"),
                            message_hex=message_hex)

    def dispatch(self, indication: E2Indication):
        sub = self.sub_mgr.get_subscription(indication.me_id, indication.ran_function_id)
        # indications of an unknown subscription (e.g. made before an xApp
        # restart) are handled as E2SM-KPM, as before E2SM-CP was supported
        service_model = sub.service_model if sub is not None else Constants.SM_KPM
        handler = self.sm_handlers.get(service_model)
        if handler is None:
            self.logger.error(f"No handler for {service_model} indications from {indication.me_id} "
                              f"RAN function {indication.ran_function_id}")
            return
        handler.handle_indication(indication)
