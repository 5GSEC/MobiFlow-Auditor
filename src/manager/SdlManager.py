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
from typing import List, Dict, Optional
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
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            self.logger.error(f"SdlManager [get_nodeb_info_by_inventory_name] {inventory_name}: "
                              f"{response.status_code} {response.text}")
            return dict()

    def store_data_to_sdl(self, ns: str, key: str, value):
        self._rmr_xapp.sdl.set(ns, key, value)

    # ------------------------------------------------------------------
    # E2 node registry: in the namespace of each service model (E2SM-CP,
    # E2SM-KPM), the group NODES_GROUP lists the E2 nodes the xApp is
    # subscribed to, and the key "node:<E2 node ID>" describes the node and
    # its subscribed RAN functions (UTF-8 JSON, not msgpack, so that any
    # xApp or redis-cli can read it).
    # ------------------------------------------------------------------

    NODES_GROUP = "nodes"

    @staticmethod
    def node_key(me_id: str) -> str:
        return f"node:{me_id}"

    def set_node(self, ns: str, me_id: str, record: dict):
        """Adds or replaces the record of an E2 node."""
        sdl = self._rmr_xapp.sdl
        sdl.set(ns, self.node_key(me_id), json.dumps(record, sort_keys=True).encode(), usemsgpack=False)
        sdl.add_member(ns, self.NODES_GROUP, me_id.encode(), usemsgpack=False)

    def remove_node(self, ns: str, me_id: str):
        """Removes the record of an E2 node (no-op if there is none)."""
        sdl = self._rmr_xapp.sdl
        sdl.remove_member(ns, self.NODES_GROUP, me_id.encode(), usemsgpack=False)
        sdl.delete(ns, self.node_key(me_id))

    def get_nodes(self, ns: str) -> List[str]:
        """The E2 nodes listed in a namespace."""
        members = self._rmr_xapp.sdl.get_members(ns, self.NODES_GROUP, usemsgpack=False) or set()
        return sorted(m.decode() if isinstance(m, bytes) else str(m) for m in members)

    def get_node(self, ns: str, me_id: str) -> Optional[Dict]:
        """The record of an E2 node, None if there is none."""
        value = self._rmr_xapp.sdl.get(ns, self.node_key(me_id), usemsgpack=False)
        return json.loads(value) if value is not None else None

    def clear_nodes(self, ns: str):
        """Removes every E2 node record of a namespace."""
        for me_id in self.get_nodes(ns):
            self._rmr_xapp.sdl.delete(ns, self.node_key(me_id))
        self._rmr_xapp.sdl.remove_group(ns, self.NODES_GROUP)

