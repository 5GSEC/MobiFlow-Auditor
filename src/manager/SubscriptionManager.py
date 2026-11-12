# ==================================================================================
#
#       Copyright (c) 2021 Samsung Electronics Co., Ltd. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ==================================================================================
"""

"""
"""
Subscribes to the RAN functions of the E2 nodes through the RIC subscription
manager REST API, one subscription per (E2 node, RAN function). E2SM-KPM and
E2SM-CP are handled by separate functions: each builds its own event trigger
and action definitions, and handles its own subscription responses.
"""

import requests
import json
import threading
import http.server
import socketserver
from dataclasses import dataclass, field
from typing import Optional
from ricxappframe.xapp_frame import RMRXapp
from ricxappframe.entities.rnib.nb_identity_pb2 import NbIdentity
from ..manager import SdlManager
from ..asn1 import AsnProxy
from ._BaseManager import _BaseManager
from ..mobiflow import FactBase, BS, BS_MOBIFLOW_NS, BsStatus
from ..utils import Constants, find_all_values
from mdclogpy import Level


@dataclass
class Subscription:
    """A subscription of the xApp to one RAN function of one E2 node."""
    me_id: str                      # E2 node inventory name, e.g. gnb_208_099_00000e00
    ran_function_id: int
    service_model: str              # Constants.SM_KPM / Constants.SM_CP
    oid: str = ""
    subscription_id: Optional[str] = None   # assigned by the subscription manager
    ran_function_definition: Optional[dict] = None  # decoded (E2SM-CP)
    actions: list = field(default_factory=list)     # (action ID, RIC style type) (E2SM-CP)


class SubscriptionManager(_BaseManager):

    __namespace = "e2Manager"
    __SUBSCRIPTION_URL = "http://service-ricplt-submgr-http.ricplt:8088/ric/v1/subscriptions/"
    __CLIENT_END_POINT = "service-ricxapp-mobiflow-auditor-http.ricxapp"

    def __init__(self, rmr_xapp: RMRXapp, asn_proxy: AsnProxy, sdl_mgr: SdlManager,
                 local_address="0.0.0.0", http_port=8080, rmr_port=4560, report_period=1000,
                 cp_max_batch_size=0, cp_max_batch_delay_ms=0) -> None:
        super().__init__(rmr_xapp)
        self.asn_proxy = asn_proxy
        self.sdl_mgr = sdl_mgr
        self.gnb_list = []
        self.enb_list = []
        self.logger.set_level(Level.INFO)
        self._lock = threading.Lock()
        self.subscriptions = {}  # (me_id, ran function ID) -> Subscription
        self.local_address = local_address
        self.client_http_port = http_port
        self.client_rmr_port = rmr_port
        self.report_period = report_period  # E2SM-KPM
        # E2SM-CP event trigger: report events as they occur; 0 leaves a limit
        # out (each event is reported in its own indication)
        self.cp_max_batch_size = cp_max_batch_size
        self.cp_max_batch_delay_ms = cp_max_batch_delay_ms
        # subscription response
        self.subscription_resp_handler = None
        self.responseCB = None
        self.regsiter_subscription_handler(response_cb=self.handle_subscription_response)

    @staticmethod
    def service_model_of(oid: str) -> Optional[str]:
        """The service model of a RAN function OID (exact match), None if not supported."""
        return Constants.SERVICE_MODEL_BY_OID.get(oid)

    def get_subscription(self, me_id: str, ran_function_id) -> Optional[Subscription]:
        with self._lock:
            return self.subscriptions.get((me_id, int(ran_function_id)))

    def _find_subscription(self, subscription_id) -> Optional[Subscription]:
        with self._lock:
            for sub in self.subscriptions.values():
                if sub.subscription_id is not None and str(sub.subscription_id) == str(subscription_id):
                    return sub
        return None

    def _is_subscribed(self, me_id: str, ran_function_id) -> bool:
        return self.get_subscription(me_id, ran_function_id) is not None

    def query_subscriptions(self):
        try:
            response = requests.get(self.__SUBSCRIPTION_URL)

            if response.status_code == 201:  # subscription request success
                resp = json.loads(response.text)
                self.logger.info(f"Subscription query succeeded, response: {resp}")
            else:
                self.logger.error(f"Subscription query failed {response.status_code} {response.text} ")

        except requests.exceptions.HTTPError as err_h:
            return "An Http Error occurred:" + repr(err_h)
        except requests.exceptions.ConnectionError as err_c:
            return "An Error Connecting to the API occurred:" + repr(err_c)
        except requests.exceptions.Timeout as err_t:
            return "A Timeout Error occurred:" + repr(err_t)
        except requests.exceptions.RequestException as err:
            return "An Unknown Error occurred" + repr(err)

    def send_subscription_request(self, nb_identity: NbIdentity, ran_function: dict):
        """Subscribe to a RAN function (from the R-NIB) with the service model of its OID."""
        oid = ran_function.get("ranFunctionOid", "")
        service_model = self.service_model_of(oid)
        if service_model == Constants.SM_KPM:
            return self.send_kpm_subscription_request(nb_identity, ran_function)
        if service_model == Constants.SM_CP:
            return self.send_cp_subscription_request(nb_identity, ran_function)
        self.logger.warning(f"Not subscribing to {nb_identity.inventory_name} RAN function "
                            f"{ran_function.get('ranFunctionId')}: no service model for OID {oid}")
        return None

    def _post_subscription(self, sub: Subscription, event_trigger: list, actions: list) -> Optional[str]:
        """
        Sends a subscription request to the subscription manager; actions are
        the REST ActionToBeSetupList items. Returns the subscription ID, None on
        failure (the subscription is not recorded and will be retried).
        """
        subscription_params = {"ClientEndPoint": {"Host": self.__CLIENT_END_POINT,
                                                  "HTTPPort": self.client_http_port,
                                                  "RMRPort": self.client_rmr_port
                                                 },
                               "Meid": sub.me_id,
                               "RANFunctionID": sub.ran_function_id,
                               "E2SubscriptionDirectives":{
                                   "E2TimeoutTimerValue": 10,
                                   "E2RetryCount": 2,
                                   "RMRRoutingNeeded": True
                                },
                               "SubscriptionDetails": [{"XappEventInstanceID": 1,  # ??
                                                        "EventTriggers": event_trigger,
                                                        "ActionToBeSetupList": actions}]
                               }

        self.logger.info(f"Sending {sub.service_model} subscription request for {sub.me_id} "
                         f"RAN function {sub.ran_function_id}: {self.__SUBSCRIPTION_URL}")
        try:
            response = requests.post(self.__SUBSCRIPTION_URL, json=subscription_params)
            self.logger.info(f"Subscription response {response.status_code} {response.text}")
            if response.status_code != 201:  # subscription request failed
                return None
            resp = json.loads(response.text)
            if "SubscriptionId" not in resp.keys():
                return None
            # save subscription info
            sub.subscription_id = resp["SubscriptionId"]
            with self._lock:
                self.subscriptions[(sub.me_id, sub.ran_function_id)] = sub
            return sub.subscription_id

        except requests.exceptions.HTTPError as err_h:
            self.logger.error("An Http Error occurred:" + repr(err_h))
        except requests.exceptions.ConnectionError as err_c:
            self.logger.error("An Error Connecting to the API occurred:" + repr(err_c))
        except requests.exceptions.Timeout as err_t:
            self.logger.error("A Timeout Error occurred:" + repr(err_t))
        except requests.exceptions.RequestException as err:
            self.logger.error("An Unknown Error occurred" + repr(err))
        except json.JSONDecodeError as err:
            self.logger.error("Invalid subscription response: " + repr(err))
        return None

    # ------------------------------------------------------------------
    # E2SM-KPM
    # ------------------------------------------------------------------

    def send_kpm_subscription_request(self, nb_identity: NbIdentity, ran_function: dict):
        me_id = nb_identity.inventory_name
        rf_id = int(ran_function["ranFunctionId"])
        rf_def = ran_function["ranFunctionDefinition"]

        if self._is_subscribed(me_id, rf_id):
            return  # subscription already exist

        decoded_rf_def = self.asn_proxy.decode_e2sm_kpm_ran_function_definition(rf_def)
        if decoded_rf_def == None:
            self.logger.error(f"Fail to decode RAN function def. Payload {rf_def}")
            return
        self.logger.debug(f"Decode RAN function def:\n {decoded_rf_def}")

        kpm_measurement_names = find_all_values(decoded_rf_def, "measName")
        meas_list = ";".join(kpm_measurement_names)

        sub = Subscription(me_id=me_id, ran_function_id=rf_id, service_model=Constants.SM_KPM,
                           oid=ran_function.get("ranFunctionOid", ""))
        actions = [{"ActionID": 0,
                    "ActionType": "report",
                    "ActionDefinition": self.encode_action_definition(meas_list=meas_list),
                    "SubsequentActionType": "continue",
                    "TimeToWait": "w10ms"}]
        if self._post_subscription(sub, self.encode_report_period(), actions) is None:
            return

        # add base station Info
        bs = BS()
        bs.name = me_id  # gnb_208_099_00000e00
        bs.mcc = me_id.split("_")[1]
        bs.mnc = me_id.split("_")[2]
        bs.nr_cell_id = int(me_id.split("_")[3], 16)
        bs.report_period = self.report_period
        bs.status = BsStatus.CONNECTED
        fb = FactBase()
        fb.add_or_update_bs(bs)
        bs = fb.get_bs(bs.nr_cell_id)
        if bs.should_report:
            # report only when there's new update to the BS
            mf = bs.generate_mobiflow()
            # store Mobiflow to SDL
            self.logger.info(f"[MobiFlow] Storing MobiFlow record to SDL {mf.__str__()}")
            self.sdl_mgr.store_data_to_sdl(BS_MOBIFLOW_NS, str(mf.msg_id), mf.__str__())

    def handle_kpm_subscription_response(self, sub: Subscription, resp_json: dict):
        self._log_subscription_status("[E2SM-KPM]", sub, resp_json)

    def encode_report_period(self) -> list:
        # [0x08, 0x03, 0xe7],  # 0x3e7 -> 1000
        return [0x08, (self.report_period-1) // 256, (self.report_period-1) % 256]

    def encode_action_definition(self, meas_list: str, action_format=1, ric_style_type=6):
        delimiter = ","
        action_def_params = delimiter.join([str(action_format), str(ric_style_type),
                                            str(self.report_period), meas_list])
        action_def_hex = self.asn_proxy.encode_e2sm_kpm_action_definition(action_def_params)
        self.logger.debug(f"Encoded action definition hex payload: {action_def_hex}")
        action_def_encoded = [int(action_def_hex[i:i + 2], 16) for i in range(0, len(action_def_hex), 2)]
        return action_def_encoded

    # ------------------------------------------------------------------
    # E2SM-CP
    # ------------------------------------------------------------------

    def send_cp_subscription_request(self, nb_identity: NbIdentity, ran_function: dict):
        """
        Subscribes to every report style of an E2SM-CP RAN function, with
        every attribute it defines, reported upon event (event trigger format 1).
        """
        me_id = nb_identity.inventory_name
        rf_id = int(ran_function["ranFunctionId"])
        rf_def_hex = ran_function["ranFunctionDefinition"]

        if self._is_subscribed(me_id, rf_id):
            return  # subscription already exist

        rf_def = self.asn_proxy.decode_e2sm_cp_ran_function_definition(rf_def_hex)
        if rf_def is None:
            self.logger.error(f"[E2SM-CP] Fail to decode RAN function definition of {me_id} RAN function "
                              f"{rf_id}: {self.asn_proxy.last_error}. Payload {rf_def_hex}")
            return
        self.logger.info(f"[E2SM-CP] RAN function definition of {me_id} RAN function {rf_id}: {rf_def}")

        trigger_style = next((s for s in rf_def["event_trigger_styles"] if s["format"] == 1), None)
        if trigger_style is None:
            self.logger.error(f"[E2SM-CP] {me_id} RAN function {rf_id} has no event trigger style of format 1")
            return
        event_trigger = self.asn_proxy.encode_e2sm_cp_event_trigger(self.cp_max_batch_size,
                                                                     self.cp_max_batch_delay_ms)
        if event_trigger is None:
            self.logger.error(f"[E2SM-CP] Fail to encode event trigger: {self.asn_proxy.last_error}")
            return

        attribute_ids = [a["id"] for a in rf_def["attributes"]]
        sub = Subscription(me_id=me_id, ran_function_id=rf_id, service_model=Constants.SM_CP,
                           oid=ran_function.get("ranFunctionOid", ""), ran_function_definition=rf_def)
        actions = []
        for style in rf_def["report_styles"]:
            if style["action_format"] != 1 or trigger_style["type"] not in style["event_trigger_styles"]:
                self.logger.info(f"[E2SM-CP] Skipping report style {style['type']} ({style['name']}): "
                                 f"action format {style['action_format']}, event trigger styles "
                                 f"{style['event_trigger_styles']}")
                continue
            action_def = self.asn_proxy.encode_e2sm_cp_action_definition(style["type"], attribute_ids)
            if action_def is None:
                self.logger.error(f"[E2SM-CP] Fail to encode action definition: {self.asn_proxy.last_error}")
                return
            action_id = len(actions) + 1
            sub.actions.append((action_id, style["type"]))
            actions.append({"ActionID": action_id,
                            "ActionType": "report",
                            "ActionDefinition": list(bytes.fromhex(action_def)),
                            "SubsequentActionType": "continue",
                            "TimeToWait": "w10ms"})
        if not actions:
            self.logger.error(f"[E2SM-CP] {me_id} RAN function {rf_id} has no usable report style")
            return

        self.logger.info(f"[E2SM-CP] Subscribing to {me_id} RAN function {rf_id}: event trigger style "
                         f"{trigger_style['type']} (max batch size {self.cp_max_batch_size or '-'}, "
                         f"max batch delay {self.cp_max_batch_delay_ms or '-'} ms), actions "
                         f"(ID, report style) {sub.actions}, {len(attribute_ids)} attributes")
        self._post_subscription(sub, list(bytes.fromhex(event_trigger)), actions)

    def handle_cp_subscription_response(self, sub: Subscription, resp_json: dict):
        self._log_subscription_status("[E2SM-CP]", sub, resp_json,
                                      f", actions (ID, report style) {sub.actions}")

    # ------------------------------------------------------------------
    # subscription responses (REST notifications from the subscription manager)
    # ------------------------------------------------------------------

    def _log_subscription_status(self, tag: str, sub: Subscription, resp_json: dict, detail: str = ""):
        """
        Logs the outcome of a subscription notification. The subscription
        manager reports a failure with E2EventInstanceId 0; a non-zero ID means
        the E2 subscription is active, even if ErrorCause is set (e.g. the E2
        node did not admit every action).
        """
        name = f"Subscription {sub.subscription_id} to {sub.me_id} RAN function {sub.ran_function_id}"
        self.logger.info(f"{tag} {name}: notification {json.dumps(resp_json)}")
        for inst in resp_json.get("SubscriptionInstances") or []:
            try:
                e2_instance_id = int(inst.get("E2EventInstanceId") or 0)
            except (TypeError, ValueError):
                e2_instance_id = 0
            cause = inst.get("ErrorCause")
            reason = (f"cause {cause!r}, source {inst.get('ErrorSource')!r}, "
                      f"timeout {inst.get('TimeoutType')!r}")
            if e2_instance_id == 0:
                self.logger.error(f"{tag} {name} failed: {reason}")
            elif cause:
                self.logger.warning(f"{tag} {name} active (E2 instance ID {e2_instance_id}), but the "
                                    f"subscription manager reported {reason}{detail}")
            else:
                self.logger.info(f"{tag} {name} active: E2 instance ID {e2_instance_id}{detail}")

    def handle_subscription_response(self, resp_data):
        if resp_data is None:
            self.logger.info(f"Empty subscription response received")
            return

        try:
            resp_json = json.loads(resp_data)
        except json.JSONDecodeError:
            self.logger.error(f"Invalid subscription response: {resp_data}")
            return
        sub = self._find_subscription(resp_json.get("SubscriptionId"))
        if sub is None:
            self.logger.info(f"Handling subscription response: {resp_json}")
        elif sub.service_model == Constants.SM_KPM:
            self.handle_kpm_subscription_response(sub, resp_json)
        elif sub.service_model == Constants.SM_CP:
            self.handle_cp_subscription_response(sub, resp_json)
        else:
            self.logger.warning(f"Subscription response for {sub.me_id} RAN function {sub.ran_function_id} "
                                f"with no handler for service model {sub.service_model}: {resp_json}")

    def regsiter_subscription_handler(self, response_cb=None):
        # Create the thread HTTP server
        if self.subscription_resp_handler is None:
            # Create the server handler if not provided
            class SubscriptionRespHandler(http.server.BaseHTTPRequestHandler):
                def do_POST(self):
                    # Check if the request path is /ric/v1/subscriptions/response
                    if self.path == "/ric/v1/subscriptions/response":
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        if response_cb:
                            response_cb(post_data)
                        self.send_response(200)
                        self.end_headers()
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b"404 Not Found")

            class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
                pass

            self.subscription_resp_handler = ThreadedHTTPServer((self.local_address, self.client_http_port), SubscriptionRespHandler)

            # Start the server in a separate thread
            server_thread = threading.Thread(target=self.subscription_resp_handler.serve_forever)
            server_thread.daemon = True  # Terminate thread when main program exits
            server_thread.start()

        if self.subscription_resp_handler is not None:
            if response_cb is not None:
                self.responseCB = response_cb
            return True
        else:
            return False

    def delete_subscription(self, me_id: str, ran_function_id=None):
        """Forgets the subscriptions to an E2 node (all, or one RAN function's)."""
        with self._lock:
            keys = [k for k in self.subscriptions
                    if k[0] == me_id and (ran_function_id is None or k[1] == int(ran_function_id))]
            for k in keys:
                self.subscriptions.pop(k)
        if not keys:
            self.logger.debug(f"Subscription not found for {me_id}")
            return -1
        # delete subscription
        self.logger.info(f"Deleting subscription for {me_id} RAN function(s) {[k[1] for k in keys]}")
        return 0
