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

import json
import requests
from typing import List, Dict
from ricxappframe.xapp_frame import RMRXapp
from ricxappframe.entities.rnib.nb_identity_pb2 import NbIdentity
from ._BaseManager import _BaseManager
from mdclogpy import Level


class SdlManager(_BaseManager):

    __E2_namespace = "e2Manager"
    __E2_msgr_endpoint = "http://service-ricplt-e2mgr-http.ricplt.svc.cluster.local:3800/v1/nodeb/"

    def __init__(self, rmr_xapp: RMRXapp) -> None:
        super().__init__(rmr_xapp)
        self.logger.set_level(Level.INFO)

    def get_sdl_keys(self, ns) -> List:
        return self._rmr_xapp.sdl.find_keys(ns, "")

    def get_sdl_with_key(self, ns, key):
        return self._rmr_xapp.sdl_find_and_get(ns, key, usemsgpack=False)

    def get_gnb_list(self) -> List[NbIdentity]:
        return self._rmr_xapp.get_list_gnb_ids()

    def get_enb_list(self) -> List[NbIdentity]:
        return self._rmr_xapp.get_list_enb_ids()

    def get_nodeb_info_by_inventory_name(self, inventory_name) -> Dict:
        url = self.__E2_msgr_endpoint + inventory_name
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            self.logger.error('SdlManager [get_nodeb_info_by_id] Error:', response.status_code)
            return dict()

    def store_data_to_sdl(self, ns: str, key: str, value):
        self._rmr_xapp.sdl.set(ns, key, value)

