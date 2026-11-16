#!/usr/bin/env python3
"""
Offline check of the E2SM-CP and E2SM-KPM paths, without a RIC: replays E2AP
PDUs recorded from the 5G-eBPF MobiFlow agent through the xApp code and prints
its log.

  1. The first PDU (E2 setup request) gives the E2 node's RAN functions, as
     the R-NIB would; the xApp subscribes to those of a supported OID (the
     subscription manager REST API is simulated, the request it would get is
     printed). E2SM-KPM: reporting period 10 s, granularity period 1 s.
  2. Every RIC indication goes through IndicationHandler (E2AP layer) to
     CpIndicationHandler or KpmIndicationHandler, which log them.

The ricxappframe and mdclogpy modules are stubbed, so only the wrappers are
needed:  src/asn1/wrapper_compile.sh

Usage:  tests/e2_replay/replay.py [<pdus file>]    (default: normal_tmsi_attach_0.pdus)
        one hex-encoded E2AP PDU per line, the E2 setup request first

Exit status 1 if an indication could not be handled.
"""

import importlib.abc
import importlib.machinery
import json
import os
import subprocess
import sys
import types
import xml.etree.ElementTree as ET
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ME_ID = "gnb_208_099_00000e00"


class _StubFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Imports ricxappframe.* and mdclogpy.* as mocks."""

    def find_spec(self, name, path, target=None):
        if name.split(".")[0] in ("ricxappframe", "mdclogpy"):
            return importlib.machinery.ModuleSpec(name, self, is_package=True)
        return None

    def create_module(self, spec):
        m = mock.MagicMock(name=spec.name)
        m.__path__, m.__spec__ = [], spec
        return m

    def exec_module(self, module):
        pass


sys.meta_path.insert(0, _StubFinder())
import ricxappframe.xapp_frame as xapp_frame  # noqa: E402

xapp_frame.rmr.RMR_MS_PAYLOAD, xapp_frame.rmr.RMR_MS_MEID = "payload", "meid"

sys.path.insert(0, REPO)
from src.asn1 import StandardAsnProxy  # noqa: E402
from src.handler import IndicationHandler, CpIndicationHandler, KpmIndicationHandler  # noqa: E402
from src.manager.SubscriptionManager import SubscriptionManager  # noqa: E402
from src.utils.constants import Constants  # noqa: E402
from src.utils.config import RanConfig, KpmConfig  # noqa: E402


class Logger:
    def __init__(self):
        self.errors = 0

    def _log(self, level, msg):
        print(f"{level:5} {msg}")

    def info(self, msg):
        self._log("INFO", msg)

    def warning(self, msg):
        self._log("WARN", msg)

    def error(self, msg):
        self.errors += 1
        self._log("ERROR", msg)

    def debug(self, msg):
        pass

    def set_level(self, level):
        pass


class FakeXapp:
    def __init__(self):
        self.logger = Logger()
        self.callbacks = {}

    def register_callback(self, cb, msgtype):
        self.callbacks[msgtype] = cb

    def rmr_free(self, sbuf):
        pass


def ran_functions(asn, setup_hex):
    """RAN functions of an E2 setup request, as the R-NIB lists them."""
    xer = subprocess.run([asn.wrapper_path, "decode", "E2AP_PDU", setup_hex],
                         capture_output=True, text=True).stdout
    x = ET.fromstring(xer)
    return [{"ranFunctionId": int(i.find("ranFunctionID").text),
             "ranFunctionDefinition": "".join(i.find("ranFunctionDefinition").text.split()),
             "ranFunctionRevision": int(i.find("ranFunctionRevision").text),
             "ranFunctionOid": i.find("ranFunctionOID").text}
            for i in x.iter("RANfunction-Item")]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "normal_tmsi_attach_0.pdus")
    pdus = open(path).read().split()
    xapp = FakeXapp()
    asn = StandardAsnProxy(os.path.join(REPO, "src/asn1/wrapper"), os.path.join(REPO, "src/asn1/wrapper_cp"))

    subscription_ids = []

    def fake_post(url, json=None, **kwargs):
        print("REST POST", url, json)
        subscription_ids.append(f"replay-{len(subscription_ids) + 1}")
        return types.SimpleNamespace(status_code=201, text=f'{{"SubscriptionId":"{subscription_ids[-1]}"}}')

    with mock.patch.object(SubscriptionManager, "regsiter_subscription_handler"), \
            mock.patch("requests.post", fake_post):
        sub_mgr = SubscriptionManager(xapp, asn, mock.MagicMock(),
                                      RanConfig(kpm=KpmConfig(reporting_period_ms=10000, granularity_period_ms=1000)))
        nb = types.SimpleNamespace(inventory_name=ME_ID, connection_status=1)
        for rf in ran_functions(asn, pdus[0]):
            if sub_mgr.service_model_of(rf["ranFunctionOid"]) is not None:
                sub_mgr.send_subscription_request(nb, rf)
    for subscription_id in subscription_ids:
        sub_mgr.handle_subscription_response(json.dumps({"SubscriptionId": subscription_id, "SubscriptionInstances": [
            {"XappEventInstanceId": 1, "E2EventInstanceId": 1, "ErrorCause": "", "ErrorSource": "",
             "TimeoutType": ""}]}).encode())

    IndicationHandler(xapp, Constants.INDICATION_REQ, asn, sub_mgr, {
        Constants.SM_KPM: KpmIndicationHandler(xapp, asn, sub_mgr),
        Constants.SM_CP: CpIndicationHandler(xapp, asn, sub_mgr),
    })
    handler = xapp.callbacks[Constants.INDICATION_REQ]
    for pdu in pdus[1:]:
        if "RICindication" in json.dumps(asn.decode_e2ap_pdu(pdu)):
            handler(xapp, {"payload": bytes.fromhex(pdu), "meid": ME_ID.encode()}, None)
    return 1 if xapp.logger.errors else 0


if __name__ == "__main__":
    sys.exit(main())
