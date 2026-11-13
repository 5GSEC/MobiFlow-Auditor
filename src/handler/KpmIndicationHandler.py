"""
Handles E2SM-KPM indications (format 1, E2 Node Measurement): decodes the
indication header and message and logs the reported measurements. Nothing is
stored yet; MobiFlow telemetry comes over E2SM-CP (CpIndicationHandler).

An indication covers one reporting period, with one record of measurement
values per granularity period. Log format (one line per indication, then one
per record):

  [E2SM-KPM] <node> RAN function <id> indication SN <sn> action <id>: <n> records of <g> ms
             from <collection start time>, totals <name>=<sum> ...
  [E2SM-KPM]   record <i> <start of its granularity period> <name>=<value> ...
"""

from datetime import timedelta
from typing import Optional
from mdclogpy import Level
from ricxappframe.xapp_frame import RMRXapp
from ..asn1 import AsnProxy
from ..manager import SubscriptionManager
from ..utils.utils import find_all_values, ntp_to_datetime, format_time
from .IndicationHandler import E2Indication, ServiceModelIndicationHandler


def _first(d, key: str):
    values = find_all_values(d, key)
    return values[0] if values else None


def _to_int(value) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def record_values(record: list) -> list:
    """Values of a measRecord (decoded XER): int (integer), float (real) or
    None (noValue)."""
    values = []
    for item in record:
        if not isinstance(item, dict) or len(item) != 1:
            continue
        kind, value = next(iter(item.items()))
        if kind == "integer":
            values.append(_to_int(value))
        elif kind == "real":
            try:
                values.append(float(value))
            except (TypeError, ValueError):
                values.append(None)
        else:  # noValue
            values.append(None)
    return values


def measurement_names(fmt1: dict) -> list:
    """Measurement names of the measInfoList of an indication message format 1
    (a measurement given by ID is named "measID <id>")."""
    names = []
    for meas_type in find_all_values(fmt1, "measType"):
        name = _first({"t": meas_type}, "measName")
        if name is None:
            name = f"measID {_first({'t': meas_type}, 'measID')}"
        names.append(name)
    return names


class KpmIndicationHandler(ServiceModelIndicationHandler):
    """Handles E2SM-KPM indications (dispatched by IndicationHandler)."""

    def __init__(self, rmr_xapp: RMRXapp, asn_proxy: AsnProxy, sub_mgr: SubscriptionManager):
        self.logger = rmr_xapp.logger
        self.logger.set_level(Level.INFO)
        self.asn_proxy = asn_proxy
        self.sub_mgr = sub_mgr

    def handle_indication(self, indication: E2Indication):
        src = f"{indication.me_id} RAN function {indication.ran_function_id}"
        message = self.asn_proxy.decode_e2sm_kpm_indication_message(indication.message_hex)
        if not message:
            self.logger.error(f"[E2SM-KPM] {src}: indication message decode error from {indication.message_hex}")
            return
        self.logger.debug(f"[E2SM-KPM] {src}: message {message}")
        fmt1 = find_all_values(message, "indicationMessage-Format1")
        if not fmt1:
            self.logger.error(f"[E2SM-KPM] {src}: unsupported indication message format: {message}")
            return
        fmt1 = {"format1": fmt1[0]}

        # collection start time (indication header format 1)
        start = None
        if indication.header_hex:
            header = self.asn_proxy.decode_e2sm_kpm_indication_header(indication.header_hex)
            start = ntp_to_datetime(_first(header, "colletStartTime")) if header else None
            if start is None:
                self.logger.warning(f"[E2SM-KPM] {src}: no collection start time in indication header "
                                    f"{indication.header_hex}")

        # measInfoList is optional: the subscribed measurements otherwise
        names = measurement_names(fmt1)
        if not names:
            sub = self.sub_mgr.get_subscription(indication.me_id, indication.ran_function_id)
            names = list(sub.measurements) if sub is not None else []
        granul_ms = _to_int(_first(fmt1, "granulPeriod"))
        records = [record_values(r) for r in find_all_values(fmt1, "measRecord")]

        totals = {}
        for record in records:
            for name, value in zip(names, record):
                if value is not None:
                    totals[name] = totals.get(name, 0) + value
        period = f"{granul_ms} ms" if granul_ms is not None else "unknown granularity period"
        self.logger.info(f"[E2SM-KPM] {src} indication SN {indication.sn} action {indication.action_id}: "
                         f"{len(records)} records of {period} from {format_time(start)}, totals "
                         + (" ".join(f"{n}={totals.get(n, 0)}" for n in names) or "-"))

        for i, record in enumerate(records):
            t = start + timedelta(milliseconds=i * granul_ms) if start is not None and granul_ms else None
            if len(record) != len(names):
                self.logger.error(f"[E2SM-KPM] {src}: record {i} has {len(record)} values for "
                                  f"{len(names)} measurements {names}: {record}")
                continue
            values = " ".join(f"{n}={'-' if v is None else v}" for n, v in zip(names, record))
            self.logger.info(f"[E2SM-KPM]   record {i} {format_time(t)} {values}")
