"""
Stores E2SM-CP events in the SDL namespace E2SM-CP (UTF-8 JSON values):

  stream:<me>              the event stream of an E2 node (written last for
                           each indication): head (index of the newest
                           event), low (index of the oldest event kept),
                           epoch, next_seq, dropped, lost, ...
  ev:<me>:<index>          one event; index: 10 digits, assigned by the xApp,
                           contiguous per E2 node (also across epochs)
  ue:<me>:<ranUEID>        the context of one UE connection: its IDs, cell,
                           first and last event, event count, release time
  ues:<me>                 group: the ranUEIDs that have a UE context
  ue_ev:<me>:<ranUEID>     group: the event indexes of a UE

The E2 node numbers its events per subscription (sequence numbers), so they
start over when the xApp subscribes again; an epoch (the collection start
time, in ms, of the first indication after that) tells such runs apart. The
xApp index keeps growing across epochs, so that a reader can follow the
stream of a node with the indexes alone: read stream:<me>, then the events
from the last one read + 1 to head (those below low have been removed).

Retention (SdlConfig): beyond cp_max_events_per_node events, the oldest of a
node are removed; a UE context and its event group are removed
cp_ue_retention_s after the last event of the UE. A UE event group can thus
list an event already removed, which a reader skips.

One E2SM-CP RAN function per E2 node is assumed (one stream per node).
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..utils.config import SdlConfig
from ..utils.constants import Constants
from .SdlManager import SdlManager

RECORD_VERSION = 1
MAX_REMOVALS_PER_INDICATION = 10000  # events removed at once, the rest at the next indications
UE_PRUNE_INTERVAL_S = 10


def _now_ms() -> int:
    return int(time.time() * 1000)


def stream_key(me_id: str) -> str:
    return f"stream:{me_id}"


def event_key(me_id: str, index: int) -> str:
    return f"ev:{me_id}:{index:010d}"


def ue_key(me_id: str, ran_ue_id: str) -> str:
    return f"ue:{me_id}:{ran_ue_id}"


def ues_group(me_id: str) -> str:
    return f"ues:{me_id}"


def ue_events_group(me_id: str, ran_ue_id: str) -> str:
    return f"ue_ev:{me_id}:{ran_ue_id}"


@dataclass
class CpEvent:
    """An event of an indication, as built by CpIndicationHandler."""
    seq: int
    t_us: Optional[int]             # Unix time, us
    ue_ref: Optional[dict]          # decoded UE-Reference (ran_ue_id, F1AP IDs, C-RNTI, ...)
    cell: Optional[str]             # "<MCC>-<MNC>:<cell ID>"
    record: dict                    # the stored event, without index and epoch
    release: bool = False           # releases the UE context (e.g. F1AP UE Context Release)


# UE-Reference IDs copied to the UE context (the latest value is kept)
UE_ID_FIELDS = ("gnb_du_id", "gnb_du_ue_f1ap_id", "gnb_cu_ue_f1ap_id", "c_rnti")


@dataclass
class _NodeState:
    stream: dict
    ues: Dict[str, dict] = field(default_factory=dict)   # ranUEID -> UE context
    last_ue_prune: float = 0.0                           # time.monotonic()


class CpEventStore:

    def __init__(self, sdl_mgr: SdlManager, config: SdlConfig, logger,
                 namespace: str = Constants.SDL_NAMESPACE_BY_SM[Constants.SM_CP]):
        self.sdl = sdl_mgr
        self.config = config
        self.logger = logger
        self.ns = namespace
        self._lock = threading.Lock()
        self._nodes: Dict[str, _NodeState] = {}   # cache of what is in the SDL, per E2 node

    def store_indication(self, me_id: str, ran_function_id: int, header: dict, events: List[CpEvent]):
        """Stores the events of one indication. On an SDL error the cached
        state of the node is dropped (it is read again from the SDL at the
        next indication) and the error raised."""
        with self._lock:
            try:
                self._store(me_id, ran_function_id, header, events)
            except Exception:
                self._nodes.pop(me_id, None)
                raise

    # ------------------------------------------------------------------

    def _node(self, me_id: str, ran_function_id: int) -> _NodeState:
        state = self._nodes.get(me_id)
        if state is not None:
            return state
        # first indication since the xApp started: continue the stored stream
        stream = self.sdl.get_json(self.ns, [stream_key(me_id)]).get(stream_key(me_id))
        if stream is None:
            stream = {"v": RECORD_VERSION, "me_id": me_id, "ran_function_id": ran_function_id,
                      "epoch": None, "head": -1, "low": 0, "next_seq": None, "dropped": 0, "lost": 0,
                      "schema_version": None, "updated_at_ms": None}
        ran_ue_ids = self.sdl.get_members(self.ns, ues_group(me_id))
        contexts = self.sdl.get_json(self.ns, [ue_key(me_id, u) for u in ran_ue_ids])
        ues = {}
        for u in ran_ue_ids:
            ctx = contexts.get(ue_key(me_id, u))
            if ctx is not None:
                ues[u] = ctx
        missing = ran_ue_ids - set(ues)
        if missing:  # listed without a context (e.g. an interrupted removal)
            self.sdl.remove_members(self.ns, ues_group(me_id), missing)
        state = _NodeState(stream=stream, ues=ues)
        self._nodes[me_id] = state
        self.logger.info(f"[E2SM-CP] SDL {self.ns}: stream of {me_id} at index {stream['head']} "
                         f"(epoch {stream['epoch']}), {len(ues)} UE contexts")
        return state

    def _store(self, me_id: str, ran_function_id: int, header: dict, events: List[CpEvent]):
        state = self._node(me_id, ran_function_id)
        s = state.stream
        now_ms = _now_ms()
        self._update_sequence(me_id, s, header, events)
        s["ran_function_id"] = ran_function_id
        s["schema_version"] = header.get("schema_version", s["schema_version"])

        values = {}
        ue_events: Dict[str, List[int]] = {}
        new_ues = []
        for ev in sorted(events, key=lambda e: e.seq):
            s["head"] += 1
            index = s["head"]
            ran_ue_id = ev.ue_ref.get("ran_ue_id") if ev.ue_ref else None
            values[event_key(me_id, index)] = dict(ev.record, v=RECORD_VERSION, idx=index, epoch=s["epoch"],
                                                   seq=ev.seq, ue=ran_ue_id)
            if ran_ue_id is None:
                continue
            ctx = state.ues.get(ran_ue_id)
            if ctx is None:
                ctx = {"v": RECORD_VERSION, "ran_ue_id": ran_ue_id, "epoch": s["epoch"],
                       "first_idx": index, "first_seq": ev.seq, "first_t_us": ev.t_us,
                       "n_events": 0, "released_t_us": None}
                state.ues[ran_ue_id] = ctx
                new_ues.append(ran_ue_id)
            for k in UE_ID_FIELDS:
                if k in ev.ue_ref:
                    ctx[k] = ev.ue_ref[k]
            if ev.cell:
                ctx["cell"] = ev.cell
            ctx.update(last_idx=index, last_seq=ev.seq, last_t_us=ev.t_us, updated_at_ms=now_ms)
            ctx["n_events"] += 1
            if ev.release:
                ctx["released_t_us"] = ev.t_us
            ue_events.setdefault(ran_ue_id, []).append(index)

        for ran_ue_id in ue_events:
            values[ue_key(me_id, ran_ue_id)] = state.ues[ran_ue_id]
        self.sdl.set_json(self.ns, values)
        self.sdl.add_members(self.ns, ues_group(me_id), new_ues)
        for ran_ue_id, indexes in ue_events.items():
            self.sdl.add_members(self.ns, ue_events_group(me_id, ran_ue_id), indexes)

        self._remove_old_events(me_id, s)
        self._remove_old_ues(me_id, state)
        s["updated_at_ms"] = now_ms
        self.sdl.set_json(self.ns, {stream_key(me_id): s})

    def _update_sequence(self, me_id: str, s: dict, header: dict, events: List[CpEvent]):
        """Epoch, expected sequence number and loss counters of the stream
        (the sequence gaps and drops are logged by CpIndicationHandler)."""
        first = header.get("first_seq", 0)
        dropped = header.get("dropped", 0)
        if s["next_seq"] is None or first < s["next_seq"]:
            # first indication, or the sequence numbers started over (new subscription)
            epoch = header.get("collection_start_ms") or _now_ms()
            if s["epoch"] is not None:
                self.logger.info(f"[E2SM-CP] SDL {self.ns}: new epoch {epoch} for {me_id} (sequence number "
                                 f"{first}, expected {s['next_seq']}), from index {s['head'] + 1}")
            s["epoch"], s["dropped"] = epoch, 0
        elif first > s["next_seq"]:
            s["lost"] += first - s["next_seq"]
        s["dropped"] = max(s["dropped"], dropped)
        s["next_seq"] = max(e.seq for e in events) + 1 if events else first

    def _remove_old_events(self, me_id: str, s: dict):
        keep_from = s["head"] - self.config.cp_max_events_per_node + 1
        if s["low"] >= keep_from:
            return
        upto = min(keep_from, s["low"] + MAX_REMOVALS_PER_INDICATION)
        self.sdl.remove_keys(self.ns, [event_key(me_id, i) for i in range(s["low"], upto)])
        s["low"] = upto

    def _remove_old_ues(self, me_id: str, state: _NodeState):
        now = time.monotonic()
        if now - state.last_ue_prune < UE_PRUNE_INTERVAL_S:
            return
        state.last_ue_prune = now
        cutoff_ms = _now_ms() - self.config.cp_ue_retention_s * 1000
        expired = [u for u, ctx in state.ues.items() if (ctx.get("updated_at_ms") or 0) < cutoff_ms]
        if not expired:
            return
        self.sdl.remove_members(self.ns, ues_group(me_id), expired)
        self.sdl.remove_keys(self.ns, [ue_key(me_id, u) for u in expired])
        for u in expired:
            self.sdl.remove_group(self.ns, ue_events_group(me_id, u))
            del state.ues[u]
        self.logger.info(f"[E2SM-CP] SDL {self.ns}: removed {len(expired)} UE contexts of {me_id} "
                         f"(no event for {self.config.cp_ue_retention_s} s)")
