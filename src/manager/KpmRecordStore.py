"""
Stores E2SM-KPM measurement records in the SDL namespace E2SM-KPM (UTF-8
JSON values), one per granularity period:

  rec:<me>:<start_ms>      the measurements of one granularity period;
                           start_ms: 13 digits, Unix time of its start
  recs:<me>                group: the start_ms of the stored records
  latest:<me>              a copy of the newest record of the node

A record: {"v": 1, "me_id": ..., "ran_function_id": ..., "start_ms": ...,
"granularity_ms": ..., "values": {<measurement name>: <value or null>}}.
Records more than kpm_retention_s (SdlConfig) older than the newest record
of the node are removed. The same period reported again replaces its record.
"""

import threading
from typing import Dict, List, Optional, Set, Tuple

from ..utils.config import SdlConfig
from ..utils.constants import Constants
from .SdlManager import SdlManager

RECORD_VERSION = 1


def record_key(me_id: str, start_ms: int) -> str:
    return f"rec:{me_id}:{start_ms:013d}"


def records_group(me_id: str) -> str:
    return f"recs:{me_id}"


def latest_key(me_id: str) -> str:
    return f"latest:{me_id}"


class KpmRecordStore:

    def __init__(self, sdl_mgr: SdlManager, config: SdlConfig, logger,
                 namespace: str = Constants.SDL_NAMESPACE_BY_SM[Constants.SM_KPM]):
        self.sdl = sdl_mgr
        self.config = config
        self.logger = logger
        self.ns = namespace
        self._lock = threading.Lock()
        self._starts: Dict[str, Set[int]] = {}   # cache of records_group, per E2 node

    def store_records(self, me_id: str, ran_function_id: int, granularity_ms: Optional[int],
                      records: List[Tuple[int, Dict[str, Optional[float]]]]):
        """Stores (start_ms, {measurement name: value}) records. On an SDL
        error the cached state of the node is dropped and the error raised."""
        if not records:
            return
        with self._lock:
            try:
                self._store(me_id, ran_function_id, granularity_ms, records)
            except Exception:
                self._starts.pop(me_id, None)
                raise

    def _store(self, me_id: str, ran_function_id: int, granularity_ms: Optional[int],
               records: List[Tuple[int, Dict[str, Optional[float]]]]):
        starts = self._starts.get(me_id)
        if starts is None:  # first indication since the xApp started
            starts = {int(s) for s in self.sdl.get_members(self.ns, records_group(me_id)) if s.isdigit()}
            self._starts[me_id] = starts
        previous_newest = max(starts) if starts else None

        values = {}
        for start_ms, measurements in records:
            values[record_key(me_id, start_ms)] = {"v": RECORD_VERSION, "me_id": me_id,
                                                   "ran_function_id": ran_function_id, "start_ms": start_ms,
                                                   "granularity_ms": granularity_ms, "values": measurements}
        new_starts = {start_ms for start_ms, _ in records}
        newest = max(new_starts)
        if previous_newest is None or newest >= previous_newest:
            values[latest_key(me_id)] = values[record_key(me_id, newest)]
        self.sdl.set_json(self.ns, values)
        self.sdl.add_members(self.ns, records_group(me_id), new_starts)
        starts |= new_starts

        cutoff = max(starts) - self.config.kpm_retention_s * 1000
        expired = {s for s in starts if s < cutoff}
        if expired:
            self.sdl.remove_members(self.ns, records_group(me_id), expired)
            self.sdl.remove_keys(self.ns, [record_key(me_id, s) for s in expired])
            starts -= expired
