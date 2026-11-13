"""
Handles E2SM-CP (MobiFlow control plane telemetry) indications: decodes the
indication header and message and logs every reported event, one line each.
Nothing is stored yet.

Log format (one line per indication, then one per event):

  [E2SM-CP] <node> RAN function <id> indication SN <sn> action <id>: <n> events (seq a..b), dropped <d>, ...
  [E2SM-CP]   seq=<n> <time> <UL|DL> ue=<ranUEID> du_ue=.. cu_ue=.. rnti=.. cell=<mcc>-<mnc>:<cell ID>
              | <message> {<attribute>=<value>, ...} > <inner message> {...}
"""

import json
import threading
from datetime import datetime, timedelta
from typing import Optional
from mdclogpy import Level
from ricxappframe.xapp_frame import RMRXapp
from ..asn1 import AsnProxy
from ..manager import SubscriptionManager
from ..mobiflow.encoding import decode_rrc_msg, nas_emm_code_NR
from ..utils.utils import ntp_to_datetime, format_time
from .IndicationHandler import E2Indication, ServiceModelIndicationHandler

DIRECTION = {0: "UL", 1: "DL"}
INTERFACE = {0: "NGAP", 1: "XnAP", 2: "F1AP", 3: "E1AP", 4: "S1AP", 5: "X2AP", 6: "W1AP"}
OUTCOME = {0: "initiating", 1: "successful", 2: "unsuccessful"}
RRC_NR_CLASS = {0: "BCCH-BCH", 1: "BCCH-DL-SCH", 2: "DL-CCCH", 3: "DL-DCCH", 4: "PCCH",
                5: "UL-CCCH", 6: "UL-CCCH1", 7: "UL-DCCH"}
PROTOCOL = {0: "F1AP", 1: "NGAP", 2: "E1AP", 3: "XnAP", 4: "NR-RRC", 5: "LTE-RRC", 6: "NAS-5GS", 7: "NAS-EPS"}
OPAQUE_REASON = {0: "ciphered", 1: "decoding error", 2: "unsupported"}
PROTECTION = {0: "none", 1: "integrity protected", 2: "ciphered", 3: "integrity protected and ciphered"}
NAS_EPD = {126: "5GMM", 46: "5GSM"}

# F1AP procedure codes (TS 38.473)
F1AP_PROCEDURE = {
    0: "Reset", 1: "F1Setup", 2: "ErrorIndication", 3: "gNBDUConfigurationUpdate",
    4: "gNBCUConfigurationUpdate", 5: "UEContextSetup", 6: "UEContextRelease",
    7: "UEContextModification", 8: "UEContextModificationRequired", 9: "UEMobilityCommand",
    10: "UEContextReleaseRequest", 11: "InitialULRRCMessageTransfer", 12: "DLRRCMessageTransfer",
    13: "ULRRCMessageTransfer", 14: "PrivateMessage", 15: "UEInactivityNotification",
    16: "GNBDUResourceCoordination", 17: "SystemInformationDeliveryCommand", 18: "Paging",
    19: "Notify", 20: "WriteReplaceWarning", 21: "PWSCancel", 22: "PWSRestartIndication",
    23: "PWSFailureIndication", 24: "GNBDUStatusIndication", 25: "RRCDeliveryReport",
    26: "F1Removal", 27: "NetworkAccessRateReduction", 28: "TraceStart", 29: "DeactivateTrace",
    30: "DUCURadioInformationTransfer", 31: "CUDURadioInformationTransfer",
}

# RRC classes whose message names are known (mobiflow.encoding): (dcch, downlink)
RRC_NAMED_CLASSES = {2: (0, 1), 3: (1, 1), 5: (0, 0), 7: (1, 0)}


def plmn_to_str(plmn_hex: str) -> str:
    """PLMN identity (TS 38.413, 3 octets, BCD) -> "MCC-MNC"."""
    if len(plmn_hex) != 6:
        return plmn_hex
    d = plmn_hex
    mcc = d[1] + d[0] + d[3]
    mnc = d[5] + d[4] + ("" if d[2] in "fF" else d[2])
    return f"{mcc}-{mnc}"


def message_name(msg: dict) -> str:
    if msg is None:
        return "unknown"
    if "interface" in msg:
        iface, proc = msg["interface"], msg["procedure"]
        name = F1AP_PROCEDURE.get(proc, "") if iface == 2 else ""
        return (f"{INTERFACE.get(iface, f'interface{iface}')} {name or 'procedure'}({proc}) "
                f"{OUTCOME.get(msg['outcome'], msg['outcome'])}")
    if "rrc_msg" in msg:
        if "rrc_nr_class" in msg:
            cls = msg["rrc_nr_class"]
            name = ""
            if cls in RRC_NAMED_CLASSES:
                dcch, downlink = RRC_NAMED_CLASSES[cls]
                # E2SM-CP RRC message ID: position in the c1 CHOICE from 0;
                # mobiflow.encoding counts from 1
                name = decode_rrc_msg(dcch, downlink, msg["rrc_msg"] + 1, 1) or ""
            return f"NR-RRC {RRC_NR_CLASS.get(cls, cls)} {name or 'message'}({msg['rrc_msg']})"
        return f"LTE-RRC class{msg['rrc_lte_class']} message({msg['rrc_msg']})"
    if "nas_msg" in msg:
        epd, mt = msg["nas_epd"], msg["nas_msg"]
        name = nas_emm_code_NR.get(mt, "") if epd in NAS_EPD else ""
        return f"NAS {NAS_EPD.get(epd, f'EPD{epd}')} {name or 'message'}(0x{mt:02x})"
    if "opaque_protocol" in msg:
        s = f"opaque {PROTOCOL.get(msg['opaque_protocol'], msg['opaque_protocol'])}"
        if "rrc_nr_class" in msg:
            s += f" {RRC_NR_CLASS.get(msg['rrc_nr_class'], msg['rrc_nr_class'])}"
        return f"{s} ({OPAQUE_REASON.get(msg['reason'], msg['reason'])})"
    return json.dumps(msg, sort_keys=True)


class CpIndicationHandler(ServiceModelIndicationHandler):
    """Handles E2SM-CP indications (dispatched by IndicationHandler)."""

    def __init__(self, rmr_xapp: RMRXapp, asn_proxy: AsnProxy, sub_mgr: SubscriptionManager):
        self.logger = rmr_xapp.logger
        self.logger.set_level(Level.INFO)
        self.asn_proxy = asn_proxy
        self.sub_mgr = sub_mgr
        self._lock = threading.Lock()
        self._streams = {}  # (me_id, RAN function ID) -> {"next_seq": int, "dropped": int}

    def handle_indication(self, indication: E2Indication):
        src = f"{indication.me_id} RAN function {indication.ran_function_id}"
        header = self.asn_proxy.decode_e2sm_cp_indication_header(indication.header_hex)
        if header is None:
            self.logger.error(f"[E2SM-CP] {src}: indication header decode error "
                              f"({self.asn_proxy.last_error}) from {indication.header_hex}")
            return
        message = self.asn_proxy.decode_e2sm_cp_indication_message(indication.message_hex)
        if message is None:
            self.logger.error(f"[E2SM-CP] {src}: indication message decode error "
                              f"({self.asn_proxy.last_error}) from {indication.message_hex}")
            return
        self.logger.debug(f"[E2SM-CP] {src}: header {header}, message {message}")

        start = ntp_to_datetime(header.get("collection_start_time"))
        groups = message.get("groups", [])
        seqs = [e["seq"] for g in groups for e in g.get("events", [])]
        seq_range = f"seq {min(seqs)}..{max(seqs)}" if seqs else "no event"
        self.logger.info(f"[E2SM-CP] {src} indication SN {indication.sn} action {indication.action_id}: "
                         f"{len(seqs)} events ({seq_range}), dropped {header.get('dropped')}, "
                         f"schema {header.get('schema_version')}, collection start {format_time(start)}")
        self._check_stream(indication, src, header, seqs)

        attr_names = self._attribute_names(indication)
        events = []
        for g in groups:
            ue = self._format_ue(g)
            for e in g.get("events", []):
                events.append((e["seq"], self._format_event(e, start, ue, attr_names)))
        for _, line in sorted(events, key=lambda x: x[0]):
            self.logger.info(f"[E2SM-CP]   {line}")

    def _check_stream(self, indication: E2Indication, src: str, header: dict, seqs: list):
        """Warns about events lost on the way (sequence gaps) or dropped by the E2 node."""
        key = (indication.me_id, indication.ran_function_id)
        first, dropped = header.get("first_seq", 0), header.get("dropped", 0)
        with self._lock:
            stream = self._streams.get(key)
            if stream is not None:
                if first != stream["next_seq"]:
                    self.logger.warning(f"[E2SM-CP] {src}: sequence gap, expected seq {stream['next_seq']}, "
                                        f"got {first}")
                if dropped > stream["dropped"]:
                    self.logger.warning(f"[E2SM-CP] {src}: E2 node dropped {dropped - stream['dropped']} "
                                        f"events ({dropped} in total)")
            self._streams[key] = {"next_seq": (max(seqs) + 1) if seqs else first, "dropped": dropped}

    def _attribute_names(self, indication: E2Indication) -> dict:
        """Attribute ID -> name, from the RAN function definition of the subscription."""
        sub = self.sub_mgr.get_subscription(indication.me_id, indication.ran_function_id)
        if sub is None or not sub.ran_function_definition:
            return {}
        return {a["id"]: a["name"] for a in sub.ran_function_definition.get("attributes", [])}

    @staticmethod
    def _format_ue(group: dict) -> str:
        parts = []
        ue = group.get("ue")
        if ue:
            parts.append(f"ue={ue['ran_ue_id']}")
            for key, label in (("gnb_du_ue_f1ap_id", "du_ue"), ("gnb_cu_ue_f1ap_id", "cu_ue"), ("c_rnti", "rnti")):
                if key in ue:
                    parts.append(f"{label}={ue[key]}")
        else:
            parts.append("ue=-")
        cell = group.get("cell")
        if cell:
            cell_id = cell.get("nr_cell_id", cell.get("eutra_cell_id"))
            parts.append(f"cell={plmn_to_str(cell.get('plmn', ''))}:{cell_id}")
        return " ".join(parts)

    @staticmethod
    def _format_event(event: dict, start: Optional[datetime], ue: str, attr_names: dict) -> str:
        t = None
        if start is not None:
            t = start + timedelta(microseconds=event.get("time_offset_us", 0))
        layers = []
        for layer in event.get("layers", []):
            s = message_name(layer.get("msg"))
            if "protection" in layer:
                s += f" [{PROTECTION.get(layer['protection'], layer['protection'])}]"
            attrs = layer.get("attrs")
            if attrs:
                s += " {" + ", ".join(f"{attr_names.get(int(k), 'attr' + k)}={v}" for k, v in attrs.items()) + "}"
            layers.append(s)
        return (f"seq={event['seq']} {format_time(t)} {DIRECTION.get(event.get('direction'), '?')} {ue} | "
                + " > ".join(layers))
