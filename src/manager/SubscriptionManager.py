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

import requests
import json
import threading
import http.server
import socketserver
from ricxappframe.xapp_frame import RMRXapp
from ricxappframe.entities.rnib.nb_identity_pb2 import NbIdentity
from ..manager import SdlManager
from ..asn1 import AsnProxy
from ._BaseManager import _BaseManager
from ..mobiflow import FactBase, BS, BS_MOBIFLOW_NS
from ..utils import Constants, find_all_values
from mdclogpy import Level


class SubscriptionManager(_BaseManager):

    __namespace = "e2Manager"
    __SUBSCRIPTION_URL = "http://service-ricplt-submgr-http.ricplt:8088/ric/v1/subscriptions/"
    __CLIENT_END_POINT = "service-ricxapp-mobiflow-auditor-http.ricxapp"

    def __init__(self, rmr_xapp: RMRXapp, asn_proxy: AsnProxy, sdl_mgr: SdlManager,
                 local_address="0.0.0.0", http_port=8080, rmr_port=4560, report_period=1000) -> None:
        super().__init__(rmr_xapp)
        self.asn_proxy = asn_proxy
        self.sdl_mgr = sdl_mgr
        self.gnb_list = []
        self.enb_list = []
        self.logger.set_level(Level.INFO)
        self.subscription_list = {}
        self.local_address = local_address
        self.client_http_port = http_port
        self.client_rmr_port = rmr_port
        self.report_period = report_period
        # subscription response
        self.subscription_resp_handler = None
        self.responseCB = None
        self.regsiter_subscription_handler(response_cb=self.handle_subscription_response)

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
        me_id = nb_identity.inventory_name
        rf_id = ran_function["ranFunctionId"]
        rf_def = ran_function["ranFunctionDefinition"]

        decoded_rf_def = self.asn_proxy.decode_e2sm_kpm_ran_function_definition(rf_def)
        if decoded_rf_def == None:
            self.logger.error(f"Fail to decode RAN function def. Payload {rf_def}")
            return
        self.logger.debug(f"Decode RAN function def:\n {decoded_rf_def}")
        
        kpm_measurement_names = find_all_values(decoded_rf_def, "measName")
        meas_list = ";".join(kpm_measurement_names)

        if me_id in self.subscription_list.keys():
            return  # subscription already exist
        subscription_params = {"ClientEndPoint": {"Host": self.__CLIENT_END_POINT,
                                                  "HTTPPort": self.client_http_port,
                                                  "RMRPort": self.client_rmr_port
                                                 },
                               "Meid": me_id,
                               "RANFunctionID": rf_id,
                               "E2SubscriptionDirectives":{
                                   "E2TimeoutTimerValue": 10,
                                   "E2RetryCount": 2,
                                   "RMRRoutingNeeded": True
                                },
                               "SubscriptionDetails": [{"XappEventInstanceID": 1,  # ??
                                                        "EventTriggers": self.encode_report_period(),
                                                        "ActionToBeSetupList": [
                                                            {"ActionID": 0,
                                                             "ActionType": "report",
                                                             "ActionDefinition": self.encode_action_definition(meas_list=meas_list),
                                                             "SubsequentActionType": "continue",
                                                             "TimeToWait": "w10ms"}
                                                       ]}]
                               }

        self.logger.info(f"Sending subscription request: {self.__SUBSCRIPTION_URL}")
        try:
            response = requests.post(self.__SUBSCRIPTION_URL, json=subscription_params)

            self.logger.info(f"Subscription response {response.status_code} {response.text}")
            if response.status_code == 201:  # subscription request success
                resp = json.loads(response.text)
                if "SubscriptionId" in resp.keys():
                    # save subscription info
                    self.subscription_list[me_id] = resp["SubscriptionId"]
                    # add base station Info
                    bs = BS()
                    fb = FactBase()
                    bs.name = me_id  # gnb_208_099_00000e00
                    bs.mcc = me_id.split("_")[1]
                    bs.mnc = me_id.split("_")[2]
                    bs.nr_cell_id = int(me_id.split("_")[3], 16)
                    bs.report_period = self.report_period
                    fb.add_bs(bs)
                    mf_list = fb.update_mobiflow()
                    for mf in mf_list:
                        # store Mobiflow to SDL
                        self.logger.info(f"[MobiFlow] Storing MobiFlow record to SDL {mf.__str__()}")
                        self.sdl_mgr.store_data_to_sdl(BS_MOBIFLOW_NS, str(mf.msg_id), mf.__str__())

                    return None

        except requests.exceptions.HTTPError as err_h:
            return "An Http Error occurred:" + repr(err_h)
        except requests.exceptions.ConnectionError as err_c:
            return "An Error Connecting to the API occurred:" + repr(err_c)
        except requests.exceptions.Timeout as err_t:
            return "A Timeout Error occurred:" + repr(err_t)
        except requests.exceptions.RequestException as err:
            return "An Unknown Error occurred" + repr(err)

    def handle_subscription_response(self, resp_data):
        if resp_data is None:
            self.logger.info(f"Empty subscription response received")
            return

        resp_json = json.loads(resp_data)
        self.logger.info(f"Handling subscription response: {resp_json}")

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



