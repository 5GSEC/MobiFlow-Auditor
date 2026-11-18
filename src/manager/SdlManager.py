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
from typing import Any, Dict, Iterable, List, Optional, Set
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
    # JSON values and groups. Values are UTF-8 JSON, not msgpack, so that
    # any xApp (or redis-cli) can read them; group members are UTF-8
    # strings. The multi-key operations go to the ricsdl SyncStorage behind
    # the ricxappframe SDL wrapper, whose own calls take one key at a time:
    # one round trip (and one atomic write) for all the keys of an indication.
    # ------------------------------------------------------------------

    def _storage(self):
        return self._rmr_xapp.sdl._sdl

    @staticmethod
    def encode_json(value) -> bytes:
        return json.dumps(value, separators=(",", ":"), sort_keys=True).encode()

    def set_json(self, ns: str, values: Dict[str, Any]):
        """Writes several keys at once (atomically)."""
        if values:
            self._storage().set(ns, {k: self.encode_json(v) for k, v in values.items()})

    def get_json(self, ns: str, keys: Iterable[str]) -> Dict[str, Any]:
        """The values of the keys that exist."""
        keys = set(keys)
        if not keys:
            return {}
        return {k: json.loads(v) for k, v in self._storage().get(ns, keys).items()}

    def remove_keys(self, ns: str, keys: Iterable[str]):
        keys = set(keys)
        if keys:
            self._storage().remove(ns, keys)

    def add_members(self, ns: str, group: str, members: Iterable):
        members = {str(m).encode() for m in members}
        if members:
            self._storage().add_member(ns, group, members)

    def remove_members(self, ns: str, group: str, members: Iterable):
        members = {str(m).encode() for m in members}
        if members:
            self._storage().remove_member(ns, group, members)

    def get_members(self, ns: str, group: str) -> Set[str]:
        return {m.decode() if isinstance(m, bytes) else str(m)
                for m in (self._storage().get_members(ns, group) or set())}

    def remove_group(self, ns: str, group: str):
        self._storage().remove_group(ns, group)

    # ------------------------------------------------------------------
    # E2 node registry: in the namespace of each service model (E2SM-CP,
    # E2SM-KPM), the group NODES_GROUP lists the E2 nodes the xApp is
    # subscribed to, and the key "node:<E2 node ID>" describes the node and
    # its subscribed RAN functions.
    # ------------------------------------------------------------------

    NODES_GROUP = "nodes"

    @staticmethod
    def node_key(me_id: str) -> str:
        return f"node:{me_id}"

    def set_node(self, ns: str, me_id: str, record: dict):
        """Adds or replaces the record of an E2 node."""
        self.set_json(ns, {self.node_key(me_id): record})
        self.add_members(ns, self.NODES_GROUP, [me_id])

    def remove_node(self, ns: str, me_id: str):
        """Removes the record of an E2 node (no-op if there is none)."""
        self.remove_members(ns, self.NODES_GROUP, [me_id])
        self.remove_keys(ns, [self.node_key(me_id)])

    def get_nodes(self, ns: str) -> List[str]:
        """The E2 nodes listed in a namespace."""
        return sorted(self.get_members(ns, self.NODES_GROUP))

    def get_node(self, ns: str, me_id: str) -> Optional[Dict]:
        """The record of an E2 node, None if there is none."""
        return self.get_json(ns, [self.node_key(me_id)]).get(self.node_key(me_id))
