# ==================================================================================
#
#       Copyright (c) 2020 Samsung Electronics Co., Ltd. All Rights Reserved.
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
import time
import json
import threading
import requests
from os import getenv
from ricxappframe.xapp_frame import RMRXapp, rmr
from .utils.constants import Constants
from .manager import *
from .handler import *
from .asn1 import StandardAsnProxy, OnosAsnProxy
from .mobiflow import FactBase, BS, BS_MOBIFLOW_NS, BsStatus
from mdclogpy import Level

class HWXapp:

    __XAPP_CONFIG_PATH = "/tmp/init/config-file.json"
    __XAPP_NAME = "mobiflow-auditor"
    __XAPP_VERSION = "0.0.3"
    __XAPP_NAME_SPACE = "ricxapp"
    __PLT_NAME_SPACE = "ricplt"
    __HTTP_PORT = 8080
    __RMR_PORT = 4560
    __XAPP_HTTP_END_POINT = "service-%s-%s-http.%s:%d" % (__XAPP_NAME_SPACE, __XAPP_NAME, __XAPP_NAME_SPACE, __HTTP_PORT)
    __XAPP_RMR_END_POINT = "service-%s-%s-rmr.%s:%d" % (__XAPP_NAME_SPACE, __XAPP_NAME, __XAPP_NAME_SPACE, __RMR_PORT)
    __CONFIG_PATH = "/ric/v1/config"
    __ASN_WRAPPER_PATH = "/tmp/src/asn1/wrapper"

    def __init__(self):
        fake_sdl = getenv("USE_FAKE_SDL", False)
        self.asn_proxy = StandardAsnProxy(self.__ASN_WRAPPER_PATH)
        self._rmr_xapp = RMRXapp(self._default_handler,
                                 config_handler=self._handle_config_change,
                                 rmr_port=self.__RMR_PORT,
                                 post_init=self._post_init,
                                 use_fake_sdl=bool(fake_sdl))

    def _post_init(self, rmr_xapp):
        """
        Function that runs when xapp initialization is complete
        """
        rmr_xapp.logger.set_level(Level.INFO)
        rmr_xapp.logger.info("HWXapp.post_init :: post_init called")
        self.sdl_mgr = SdlManager(rmr_xapp)
        self.sub_mgr = SubscriptionManager(rmr_xapp, self.asn_proxy, self.sdl_mgr)
        # self.sdl_alarm_mgr = SdlAlarmManager()
        # a1_mgr = A1PolicyManager(rmr_xapp)
        # a1_mgr.startup()
        # metric_mgr = MetricManager(rmr_xapp)
        # metric_mgr.send_metric()

        self._register(rmr_xapp)

        # load xApp config
        with open(self.__XAPP_CONFIG_PATH, 'r') as config_file:
            config_json = json.loads(config_file.read())
            self.target_oid_list = config_json["ran"]["target_oid_list"]
        
        # Start subscription processing in a separate thread
        subscription_thread = threading.Thread(target=self._process_subscription, args=(rmr_xapp,), daemon=True)
        subscription_thread.start()

    
    def _process_subscription(self, rmr_xapp):
        """
        Function to obtain nodeb list and handle subscriptions in an infinite loop
        """
        fb = FactBase() # init fact base

        while True:
            # obtain nodeb list for subscription.
            time.sleep(5) # query at each interval
            # enb_list = self.sdl_mgr.get_enb_list()
            # for enb_nb_identity in enb_list:
            #     inventory_name = enb_nb_identity.inventory_name
            #     nodeb_info_json = self.sdl_mgr.get_nodeb_info_by_inventory_name(inventory_name)
            gnb_list = self.sdl_mgr.get_gnb_list()
            for gnb_nb_identity in gnb_list:
                inventory_name = gnb_nb_identity.inventory_name
                connection_status = gnb_nb_identity.connection_status
                nodeb_info_json = self.sdl_mgr.get_nodeb_info_by_inventory_name(inventory_name)
                # rmr_xapp.logger.info(f"RAN {inventory_name} status {connection_status}")
                for ran_func in nodeb_info_json["gnb"]["ranFunctions"]:
                    rf_oid = ran_func["ranFunctionOid"]
                    if rf_oid in self.target_oid_list:
                        rmr_xapp.logger.debug(f"Found target ran function for gNB {inventory_name}: {ran_func}")
                        # Subscribe to NodeB
                        rmr_xapp.logger.debug(f"connection status {connection_status}")
                        if connection_status == 1:
                            self.sub_mgr.send_subscription_request(gnb_nb_identity, ran_func)
                        elif connection_status == 2:
                            # create or update BS state
                            me_id = inventory_name
                            bs = BS()
                            bs.name = me_id  # gnb_208_099_00000e00
                            bs.mcc = me_id.split("_")[1]
                            bs.mnc = me_id.split("_")[2]
                            bs.nr_cell_id = int(me_id.split("_")[3], 16)
                            bs.status = BsStatus.DISCONNECTED
                            if fb.get_bs_index_by_name(bs.name) != -1:
                                # only track when the cell transit from connected to disconnected
                                fb.add_or_update_bs(bs)
                                bs = fb.get_bs(bs.nr_cell_id)
                                if bs.should_report:
                                    # report only when there's new update to the BS
                                    mf = bs.generate_mobiflow()
                                    # store Mobiflow to SDL
                                    rmr_xapp.logger.info(f"[MobiFlow] Storing MobiFlow record to SDL {mf.__str__()}")
                                    self.sdl_mgr.store_data_to_sdl(BS_MOBIFLOW_NS, str(mf.msg_id), mf.__str__())

    def _register(self, rmr_xapp):
        # Register xApp to the App mgr
        url = "http://service-%s-appmgr-http.%s:8080/ric/v1/register" % (self.__PLT_NAME_SPACE, self.__PLT_NAME_SPACE)
        with open(self.__XAPP_CONFIG_PATH, 'r') as config_file:
            config_json_str = config_file.read()
        body = {
            "appName": self.__XAPP_NAME,
            "httpEndpoint": self.__XAPP_HTTP_END_POINT,
            "rmrEndpoint": self.__XAPP_RMR_END_POINT,
            "appInstanceName": self.__XAPP_NAME,
            "appVersion": self.__XAPP_VERSION,
            "configPath": self.__CONFIG_PATH,
            "config": config_json_str
        }
        try:
            rmr_xapp.logger.info(f"Sending registration request to {url} {body}")
            response = requests.post(url, json=body)
            rmr_xapp.logger.info(f"Registration response {response.status_code} {response.text}")
            if response.status_code == 201:  # registration request success
                rmr_xapp.logger.info(f"Registration success")

        except IOError as err_h:
            rmr_xapp.logger.error("An IO Error occurred:" + repr(err_h))

    def _deregister(self, rmr_xapp):
        # Deregister xApp to the App mgr
        url = "http://service-%s-appmgr-http.%s:8080/ric/v1/deregister" % (self.__PLT_NAME_SPACE, self.__PLT_NAME_SPACE)
        body = {
            "appName": self.__XAPP_NAME,
            "appInstanceName": f"{self.__XAPP_NAME}_{self.__XAPP_VERSION}",
        }
        try:
            rmr_xapp.logger.info(f"Sending deregistration request to {url}")
            response = requests.post(url, json=body)
            rmr_xapp.logger.info(f"Deregistration response {response.status_code} {response.text}")
            if response.status_code == 201:  # registration request success
                rmr_xapp.logger.info(f"Deregistration success")

        except IOError as err_h:
            rmr_xapp.logger.error("An IO Error occurred:" + repr(err_h))

    def _handle_config_change(self, rmr_xapp, config):
        """
        Function that runs at start and on every configuration file change.
        """
        rmr_xapp.logger.info("HWXapp.handle_config_change:: config: {}".format(config))
        rmr_xapp.config = config  # No mutex required due to GIL

    def _default_handler(self, rmr_xapp, summary, sbuf):
        """
        Function that processes messages for which no handler is defined
        """
        rmr_xapp.logger.info("HWXapp.default_handler called for msg type = " +
                                   str(summary[rmr.RMR_MS_MSG_TYPE]))
        rmr_xapp.rmr_free(sbuf)

    def createHandlers(self):
        """
        Function that creates all the handlers for RMR Messages
        """
        HealthCheckHandler(self._rmr_xapp, Constants.RIC_HEALTH_CHECK_REQ)
        A1PolicyHandler(self._rmr_xapp, Constants.A1_POLICY_REQ)
        SubscriptionHandler(self._rmr_xapp, Constants.SUBSCRIPTION_REQ)
        KpmIndicationHandler(self._rmr_xapp, Constants.INDICATION_REQ, self.asn_proxy, self.sdl_mgr)

    def start(self, thread=False):
        """
        This is a convenience function that allows this xapp to run in Docker
        for "real" (no thread, real SDL), but also easily modified for unit testing
        (e.g., use_fake_sdl). The defaults for this function are for the Dockerized xapp.
        """
        self.createHandlers()
        self._rmr_xapp.run(thread)

    def stop(self):
        """
        can only be called if thread=True when started
        TODO: could we register a signal handler for Docker SIGTERM that calls this?
        """
        self._rmr_xapp.stop()



