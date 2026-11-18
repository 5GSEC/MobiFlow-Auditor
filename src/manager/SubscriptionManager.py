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
manager REST API, one subscription per (E2 node, RAN function). start() polls
the R-NIB for E2 nodes every RanConfig.poll_interval_ms and subscribes to the
RAN functions of RanConfig.target_oid_list of each connected node. E2SM-KPM
and E2SM-CP are handled by separate functions: each builds its own event
trigger and action definitions, and handles its own subscription responses.

The subscribed E2 nodes are recorded in the SDL, in the namespace of each
service model (Constants.SDL_NAMESPACE_BY_SM): the group "nodes" lists them,
and "node:<E2 node ID>" describes the node and its subscribed RAN functions
(see node_record). A record is written when a subscription is created,
updated when the subscription manager reports its outcome, and removed when
the subscriptions to the node are deleted.
"""

import requests
import json
import threading
import time
import http.server
import socketserver
from dataclasses import dataclass, field
from typing import Optional
from ricxappframe.xapp_frame import RMRXapp
from ricxappframe.entities.rnib.nb_identity_pb2 import NbIdentity, CONNECTED, DISCONNECTED
from ..manager import SdlManager
from ..asn1 import AsnProxy
from ._BaseManager import _BaseManager
from ..utils import Constants, RanConfig, find_all_values
from mdclogpy import Level

HTTP_TIMEOUT_S = 10  # subscription manager REST API
NODE_RECORD_VERSION = 1  # of the SDL E2 node records
MAX_UNMATCHED_NOTIFICATIONS = 64

# subscription status (SDL E2 node records)
STATUS_REQUESTED = "requested"  # accepted by the subscription manager, outcome not reported yet
STATUS_ACTIVE = "active"
STATUS_FAILED = "failed"

# E2SM-CP AttributeValueType and Stability
CP_VALUE_TYPE = {0: "boolean", 1: "integer", 2: "real", 3: "bitString", 4: "octetString", 5: "printableString"}
CP_STABILITY = {0: "experimental", 1: "stable", 2: "deprecated"}


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class Subscription:
    """A subscription of the xApp to one RAN function of one E2 node."""
    me_id: str                      # E2 node inventory name, e.g. gnb_208_099_00000e00
    ran_function_id: int
    service_model: str              # Constants.SM_KPM / Constants.SM_CP
    oid: str = ""
    plmn_id: str = ""               # global E2 node ID (R-NIB)
    nb_id: str = ""
    subscription_id: Optional[str] = None   # assigned by the subscription manager
    status: str = STATUS_REQUESTED
    e2_instance_id: Optional[int] = None    # E2 subscription instance, once active
    subscribed_at_ms: Optional[int] = None  # when the subscription manager accepted it
    ran_function_definition: Optional[dict] = None  # decoded (E2SM-CP)
    actions: list = field(default_factory=list)     # (action ID, RIC style type)
    measurements: list = field(default_factory=list)  # subscribed measurement names (E2SM-KPM)

    @staticmethod
    def global_ids(nb_identity: NbIdentity) -> dict:
        """plmn_id / nb_id of an R-NIB node identity (empty if absent)."""
        global_nb_id = getattr(nb_identity, "global_nb_id", None)
        return {"plmn_id": str(getattr(global_nb_id, "plmn_id", "") or ""),
                "nb_id": str(getattr(global_nb_id, "nb_id", "") or "")}


class SubscriptionManager(_BaseManager):

    __namespace = "e2Manager"
    __SUBSCRIPTION_URL = "http://service-ricplt-submgr-http.ricplt:8088/ric/v1/subscriptions/"
    __CLIENT_END_POINT = "service-ricxapp-mobiflow-auditor-http.ricxapp"

    def __init__(self, rmr_xapp: RMRXapp, asn_proxy: AsnProxy, sdl_mgr: SdlManager,
                 ran_config: Optional[RanConfig] = None,
                 local_address="0.0.0.0", http_port=8080, rmr_port=4560) -> None:
        super().__init__(rmr_xapp)
        self.asn_proxy = asn_proxy
        self.sdl_mgr = sdl_mgr
        self.logger.set_level(Level.INFO)
        # validated by RanConfig.from_dict
        self.config = ran_config if ran_config is not None else RanConfig()
        self._lock = threading.Lock()
        self.subscriptions = {}  # (me_id, ran function ID) -> Subscription
        # notifications that came before the subscription request returned its
        # subscription ID: subscription ID -> notification
        self._unmatched_notifications = {}
        # serializes the SDL E2 node record writes, so that an older record
        # never replaces a newer one
        self._registry_lock = threading.Lock()
        self.local_address = local_address
        self.client_http_port = http_port
        self.client_rmr_port = rmr_port
        # R-NIB polling (start / stop)
        self._stop_event = threading.Event()
        self._poll_thread: Optional[threading.Thread] = None
        # subscription response
        self.subscription_resp_handler = None
        self.responseCB = None
        self.regsiter_subscription_handler(response_cb=self.handle_subscription_response)

    # ------------------------------------------------------------------
    # E2 node discovery: polls the R-NIB, subscribes to connected nodes
    # ------------------------------------------------------------------

    def start(self):
        """Starts polling the R-NIB for E2 nodes in a daemon thread (no-op if already started)."""
        if self._poll_thread is not None and self._poll_thread.is_alive():
            return
        self.reconcile_node_registry()
        self._stop_event.clear()
        self._poll_thread = threading.Thread(target=self._poll_loop, name="subscription-poll", daemon=True)
        self._poll_thread.start()
        self.logger.info(f"Polling the R-NIB for E2 nodes every {self.config.poll_interval_ms} ms, target RAN "
                         f"function OIDs {list(self.config.target_oid_list)}")

    def stop(self, timeout_s: Optional[float] = None):
        """Stops polling; subscriptions already made are kept."""
        self._stop_event.set()
        if self._poll_thread is not None:
            self._poll_thread.join(timeout_s)
            self._poll_thread = None

    def _poll_loop(self):
        # wait one interval before the first poll, so that the xApp registration
        # (and its RMR routes) are in place before subscribing
        while not self._stop_event.wait(self.config.poll_interval_ms / 1000):
            try:
                self.poll_once()
            except Exception as e:  # keep polling: a failed poll is retried at the next interval
                self.logger.error(f"Polling the R-NIB for E2 nodes failed: {e!r}")

    def poll_once(self):
        """Subscribes to the target RAN functions of every connected gNB, and
        forgets the subscriptions to disconnected ones."""
        for nb_identity in self.sdl_mgr.get_gnb_list():
            try:
                self._reconcile_node(nb_identity)
            except Exception as e:  # one failing node must not keep the others from being subscribed to
                self.logger.error(f"Handling E2 node {nb_identity.inventory_name} failed: {e!r}")

    def _reconcile_node(self, nb_identity: NbIdentity):
        me_id = nb_identity.inventory_name
        status = nb_identity.connection_status
        if status == DISCONNECTED:
            # no RAN state is kept: forget the subscriptions so that they are
            # made again when the node reconnects
            self.delete_subscription(me_id)
            return
        if status != CONNECTED:
            return  # e.g. connecting, shutting down: retried at the next poll
        nodeb_info = self.sdl_mgr.get_nodeb_info_by_inventory_name(me_id)
        ran_functions = (nodeb_info.get("gnb") or {}).get("ranFunctions") or []
        if not ran_functions:
            self.logger.debug(f"No RAN function found for E2 node {me_id}: {nodeb_info}")
        for ran_func in ran_functions:
            if ran_func.get("ranFunctionOid") in self.config.target_oid_list:
                self.logger.debug(f"Found target RAN function for E2 node {me_id}: {ran_func}")
                self.send_subscription_request(nb_identity, ran_func)

    @staticmethod
    def service_model_of(oid: str) -> Optional[str]:
        """The service model of a RAN function OID (exact match), None if not supported."""
        return Constants.SERVICE_MODEL_BY_OID.get(oid)

    def get_subscription(self, me_id: str, ran_function_id) -> Optional[Subscription]:
        with self._lock:
            return self.subscriptions.get((me_id, int(ran_function_id)))

    def _find_subscription(self, subscription_id) -> Optional[Subscription]:
        with self._lock:
            return self._find_subscription_locked(subscription_id)

    def _find_subscription_locked(self, subscription_id) -> Optional[Subscription]:
        """_find_subscription, with self._lock held."""
        if subscription_id is None:
            return None
        for sub in self.subscriptions.values():
            if sub.subscription_id is not None and str(sub.subscription_id) == str(subscription_id):
                return sub
        return None

    def _is_subscribed(self, me_id: str, ran_function_id) -> bool:
        return self.get_subscription(me_id, ran_function_id) is not None

    def query_subscriptions(self):
        try:
            response = requests.get(self.__SUBSCRIPTION_URL, timeout=HTTP_TIMEOUT_S)

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
            response = requests.post(self.__SUBSCRIPTION_URL, json=subscription_params, timeout=HTTP_TIMEOUT_S)
            self.logger.info(f"Subscription response {response.status_code} {response.text}")
            if response.status_code != 201:  # subscription request failed
                return None
            resp = json.loads(response.text)
            if "SubscriptionId" not in resp.keys():
                return None
            # save subscription info
            sub.subscription_id = resp["SubscriptionId"]
            sub.subscribed_at_ms = _now_ms()
            with self._lock:
                self.subscriptions[(sub.me_id, sub.ran_function_id)] = sub
                early = self._unmatched_notifications.pop(str(sub.subscription_id), None)
            self.publish_node(sub.me_id, sub.service_model)
            if early is not None:  # the outcome was reported before the request returned
                self._handle_notification(sub, early)
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
        """
        Subscribes to the measurements of an E2SM-KPM RAN function: every
        measurement of its first report style with action definition format 1
        (E2 Node Measurement), reported every reporting period, one record per
        granularity period.
        """
        me_id = nb_identity.inventory_name
        rf_id = int(ran_function["ranFunctionId"])
        rf_def = ran_function["ranFunctionDefinition"]

        if self._is_subscribed(me_id, rf_id):
            return  # subscription already exist

        decoded_rf_def = self.asn_proxy.decode_e2sm_kpm_ran_function_definition(rf_def)
        if decoded_rf_def is None:
            self.logger.error(f"[E2SM-KPM] {me_id} RAN function {rf_id}: fail to decode RAN function def. "
                              f"Payload {rf_def}")
            return
        self.logger.debug(f"Decode RAN function def:\n {decoded_rf_def}")

        style = self._kpm_report_style(decoded_rf_def)
        if style is None:
            self.logger.warning(f"[E2SM-KPM] {me_id} RAN function {rf_id}: not subscribing, no report style "
                                f"with action definition format 1 and measurements in {decoded_rf_def}")
            return
        style_type, meas_names = style
        self.logger.info(f"[E2SM-KPM] {me_id} RAN function {rf_id}: report style {style_type}, "
                         f"measurements {meas_names}")

        action_def = self.encode_action_definition(meas_list=";".join(meas_names), ric_style_type=style_type)
        if not action_def:
            self.logger.error(f"[E2SM-KPM] {me_id} RAN function {rf_id}: fail to encode the action definition")
            return
        sub = Subscription(me_id=me_id, ran_function_id=rf_id, service_model=Constants.SM_KPM,
                           oid=ran_function.get("ranFunctionOid", ""), **Subscription.global_ids(nb_identity),
                           actions=[(0, style_type)], measurements=meas_names)
        actions = [{"ActionID": 0,
                    "ActionType": "report",
                    "ActionDefinition": action_def,
                    "SubsequentActionType": "continue",
                    "TimeToWait": "w10ms"}]
        self._post_subscription(sub, self.encode_report_period(), actions)

    @staticmethod
    def _kpm_report_style(decoded_rf_def: dict):
        """(RIC style type, measurement names) of the first report style with
        action definition format 1 and measurements, None if there is none."""
        for item in find_all_values(decoded_rf_def, "RIC-ReportStyle-Item"):
            fields = {"item": item}
            try:
                style_type = int(find_all_values(fields, "ric-ReportStyle-Type")[0])
                action_format = int(find_all_values(fields, "ric-ActionFormat-Type")[0])
            except (IndexError, TypeError, ValueError):
                continue
            meas_names = find_all_values(fields, "measName")
            if action_format == 1 and meas_names:
                return style_type, meas_names
        return None

    def handle_kpm_subscription_response(self, sub: Subscription, resp_json: dict):
        self._log_subscription_status(
            "[E2SM-KPM]", sub, resp_json,
            f", reporting period {self.config.kpm.reporting_period_ms} ms, granularity period "
            f"{self.config.kpm.granularity_period_ms} ms, measurements {sub.measurements}")

    def encode_report_period(self) -> list:
        """
        E2SM-KPM event trigger definition format 1 (APER): reportingPeriod
        INTEGER (1..4294967295), so the value minus 1 in 1 to 4 octets, after
        a byte that holds the octet count minus 1 (bits 4-3), e.g. 1000 ms ->
        [0x08, 0x03, 0xe7].
        """
        value = self.config.kpm.reporting_period_ms - 1
        octets = max(1, (value.bit_length() + 7) // 8)
        return [(octets - 1) << 3] + list(value.to_bytes(octets, "big"))

    def encode_action_definition(self, meas_list: str, ric_style_type: int, action_format=1) -> list:
        """E2SM-KPM action definition format 1: the measurements (names, ";"
        separated) and the granularity period."""
        delimiter = ","
        action_def_params = delimiter.join([str(action_format), str(ric_style_type),
                                            str(self.config.kpm.granularity_period_ms), meas_list])
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
        event_trigger = self.asn_proxy.encode_e2sm_cp_event_trigger(self.config.cp.max_batch_size,
                                                                     self.config.cp.max_batch_delay_ms)
        if event_trigger is None:
            self.logger.error(f"[E2SM-CP] Fail to encode event trigger: {self.asn_proxy.last_error}")
            return

        attribute_ids = [a["id"] for a in rf_def["attributes"]]
        sub = Subscription(me_id=me_id, ran_function_id=rf_id, service_model=Constants.SM_CP,
                           oid=ran_function.get("ranFunctionOid", ""), **Subscription.global_ids(nb_identity),
                           ran_function_definition=rf_def)
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
                         f"{trigger_style['type']} (max batch size {self.config.cp.max_batch_size or '-'}, "
                         f"max batch delay {self.config.cp.max_batch_delay_ms or '-'} ms), actions "
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
        Logs the outcome of a subscription notification, and records it in
        sub.status. The subscription manager reports a failure with
        E2EventInstanceId 0; a non-zero ID means the E2 subscription is
        active, even if ErrorCause is set (e.g. the E2 node did not admit
        every action).
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
                if sub.status != STATUS_ACTIVE:
                    sub.status = STATUS_FAILED
                continue
            sub.status, sub.e2_instance_id = STATUS_ACTIVE, e2_instance_id
            if cause:
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
        if not isinstance(resp_json, dict):
            self.logger.error(f"Invalid subscription response: {resp_data}")
            return
        subscription_id = resp_json.get("SubscriptionId")
        with self._lock:
            sub = self._find_subscription_locked(subscription_id)
            if sub is None and subscription_id is not None:
                # the subscription request may not have returned yet: kept
                # for _post_subscription (the oldest is dropped beyond the limit)
                if len(self._unmatched_notifications) >= MAX_UNMATCHED_NOTIFICATIONS:
                    self._unmatched_notifications.pop(next(iter(self._unmatched_notifications)))
                self._unmatched_notifications[str(subscription_id)] = resp_json
        if sub is None:
            self.logger.info(f"Handling subscription response (no known subscription yet): {resp_json}")
            return
        self._handle_notification(sub, resp_json)

    def _handle_notification(self, sub: Subscription, resp_json: dict):
        if sub.service_model == Constants.SM_KPM:
            self.handle_kpm_subscription_response(sub, resp_json)
        elif sub.service_model == Constants.SM_CP:
            self.handle_cp_subscription_response(sub, resp_json)
        else:
            self.logger.warning(f"Subscription response for {sub.me_id} RAN function {sub.ran_function_id} "
                                f"with no handler for service model {sub.service_model}: {resp_json}")
        self.publish_node(sub.me_id, sub.service_model)

    # ------------------------------------------------------------------
    # SDL E2 node registry
    # ------------------------------------------------------------------

    def node_record(self, me_id: str, service_model: str) -> Optional[dict]:
        """
        The SDL record of an E2 node for one service model, None if the xApp
        has no subscription to it:

          {"v": 1, "me_id": ..., "plmn_id": ..., "nb_id": ..., "service_model": ...,
           "updated_at_ms": ..., "ran_functions": [<RAN function>, ...]}

        A RAN function holds its subscription (ran_function_id, oid,
        subscription_id, status, e2_instance_id, subscribed_at_ms, actions)
        and, for E2SM-CP, the RAN function name, the event trigger and the
        attributes; for E2SM-KPM, the reporting and granularity periods and
        the measurements.
        """
        with self._lock:
            subs = sorted((s for s in self.subscriptions.values()
                           if s.me_id == me_id and s.service_model == service_model),
                          key=lambda s: s.ran_function_id)
            if not subs:
                return None
            ran_functions = [self._ran_function_record(s) for s in subs]
        return {"v": NODE_RECORD_VERSION,
                "me_id": me_id,
                "plmn_id": subs[0].plmn_id,
                "nb_id": subs[0].nb_id,
                "service_model": service_model,
                "updated_at_ms": _now_ms(),
                "ran_functions": ran_functions}

    def _ran_function_record(self, sub: Subscription) -> dict:
        record = {"ran_function_id": sub.ran_function_id,
                  "oid": sub.oid,
                  "subscription_id": sub.subscription_id,
                  "status": sub.status,
                  "e2_instance_id": sub.e2_instance_id,
                  "subscribed_at_ms": sub.subscribed_at_ms,
                  "actions": [{"action_id": a, "report_style": s} for a, s in sub.actions]}
        if sub.service_model == Constants.SM_CP:
            rf_def = sub.ran_function_definition or {}
            record["ran_function"] = {k: rf_def.get(k) for k in
                                      ("short_name", "description", "instance", "schema_version")}
            record["event_trigger"] = {"max_batch_size": self.config.cp.max_batch_size,
                                       "max_batch_delay_ms": self.config.cp.max_batch_delay_ms}
            record["attributes"] = [
                dict(a, type=CP_VALUE_TYPE.get(a.get("type"), a.get("type")),
                     stability=CP_STABILITY.get(a.get("stability"), a.get("stability")))
                for a in rf_def.get("attributes", [])]
        elif sub.service_model == Constants.SM_KPM:
            record["reporting_period_ms"] = self.config.kpm.reporting_period_ms
            record["granularity_period_ms"] = self.config.kpm.granularity_period_ms
            record["measurements"] = list(sub.measurements)
        return record

    def publish_node(self, me_id: str, service_model: str):
        """Writes (or removes, if the xApp has no subscription to it) the SDL
        record of an E2 node; an SDL failure is logged, not raised."""
        ns = Constants.SDL_NAMESPACE_BY_SM.get(service_model)
        if ns is None:
            return
        with self._registry_lock:
            record = self.node_record(me_id, service_model)
            try:
                if record is None:
                    self.sdl_mgr.remove_node(ns, me_id)
                    self.logger.info(f"SDL {ns}: removed E2 node {me_id}")
                else:
                    self.sdl_mgr.set_node(ns, me_id, record)
                    self.logger.info(f"SDL {ns}: recorded E2 node {me_id}, RAN functions "
                                     + ", ".join(f"{rf['ran_function_id']} ({rf['status']})"
                                                 for rf in record["ran_functions"]))
            except Exception as e:
                self.logger.error(f"SDL {ns}: failed to update E2 node {me_id}: {e!r}")

    def reconcile_node_registry(self):
        """Removes the SDL records of the E2 nodes the xApp has no subscription
        to (e.g. left by a previous run), and writes the others."""
        for service_model, ns in Constants.SDL_NAMESPACE_BY_SM.items():
            try:
                stored = set(self.sdl_mgr.get_nodes(ns))
            except Exception as e:
                self.logger.error(f"SDL {ns}: failed to list E2 nodes: {e!r}")
                continue
            with self._lock:
                current = {s.me_id for s in self.subscriptions.values() if s.service_model == service_model}
            for me_id in sorted(stored | current):
                self.publish_node(me_id, service_model)

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
            service_models = {self.subscriptions.pop(k).service_model for k in keys}
        if not keys:
            self.logger.debug(f"Subscription not found for {me_id}")
            return -1
        # delete subscription
        self.logger.info(f"Deleting subscription for {me_id} RAN function(s) {[k[1] for k in keys]}")
        for service_model in sorted(service_models):
            self.publish_node(me_id, service_model)
        return 0
