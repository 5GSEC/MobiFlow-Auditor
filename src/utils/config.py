"""
The "ran" section of the xApp config file (init/config-file.json): which RAN
functions to subscribe to, how often to poll the R-NIB for E2 nodes, and the
subscription settings of each service model, and how much of the reported
data is kept in the SDL.

    "ran": {
        "target_oid_list": ["1.3.6.1.4.1.53148.1.2.2.2", "1.3.6.1.4.1.32473.1.1.2.1"],
        "poll_interval_ms": 5000,
        "e2sm_kpm": {"reporting_period_ms": 10000, "granularity_period_ms": 1000},
        "e2sm_cp": {"max_batch_size": 0, "max_batch_delay_ms": 0},
        "sdl": {"cp_max_events_per_node": 100000, "cp_ue_retention_s": 600, "kpm_retention_s": 3600}
    }

Every key is optional: a missing key takes its default. A value of the wrong
type or out of range raises ConfigError, which names the key. Unknown keys
(e.g. a typo) and unsupported OIDs are reported through the warn callback and
otherwise ignored.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple

from .constants import Constants

__all__ = ["ConfigError", "KpmConfig", "CpConfig", "SdlConfig", "RanConfig"]

_UINT32_MAX = 4294967295


class ConfigError(ValueError):
    """An invalid value in the xApp config file."""


def _check_section(section: str, value) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"{section} must be an object, got {value!r}")
    return value


def _warn_unknown_keys(section: str, d: dict, known, warn: Callable[[str], None]):
    for key in d:
        if key not in known:
            warn(f"Config: ignoring unknown key {section}.{key}")


def _get_int(section: str, d: dict, key: str, default: int, lo: int, hi: Optional[int] = None) -> int:
    value = d.get(key, default)
    # JSON true/false are Python bools, which are ints: reject them explicitly
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{section}.{key} must be an integer, got {value!r}")
    if value < lo or (hi is not None and value > hi):
        bounds = f"{lo}..{hi}" if hi is not None else f">= {lo}"
        raise ConfigError(f"{section}.{key} must be {bounds}, got {value}")
    return value


def _ignore(_msg: str):
    pass


@dataclass(frozen=True)
class KpmConfig:
    """
    E2SM-KPM: the E2 node sends an indication every reporting period (event
    trigger), with one record of measurement values per granularity period
    (action definition). The granularity period must divide the reporting period.
    """
    SECTION = "ran.e2sm_kpm"

    reporting_period_ms: int = 1000
    granularity_period_ms: int = 1000

    def __post_init__(self):
        if self.reporting_period_ms < 1 or self.granularity_period_ms < 1:
            raise ConfigError(f"{self.SECTION} periods must be >= 1 ms, got reporting period "
                              f"{self.reporting_period_ms}, granularity period {self.granularity_period_ms}")
        if self.reporting_period_ms % self.granularity_period_ms != 0:
            raise ConfigError(f"{self.SECTION}.granularity_period_ms ({self.granularity_period_ms}) must divide "
                              f"{self.SECTION}.reporting_period_ms ({self.reporting_period_ms})")

    @classmethod
    def from_dict(cls, d, warn: Callable[[str], None] = _ignore) -> "KpmConfig":
        d = _check_section(cls.SECTION, d)
        _warn_unknown_keys(cls.SECTION, d, ("reporting_period_ms", "granularity_period_ms"), warn)
        # E2SM-KPM ReportingPeriod and GranularityPeriod: INTEGER (1..4294967295)
        reporting = _get_int(cls.SECTION, d, "reporting_period_ms", cls.reporting_period_ms, 1, _UINT32_MAX)
        # the granularity period defaults to the reporting period (one record per indication)
        granularity = _get_int(cls.SECTION, d, "granularity_period_ms", reporting, 1, _UINT32_MAX)
        return cls(reporting_period_ms=reporting, granularity_period_ms=granularity)


@dataclass(frozen=True)
class CpConfig:
    """
    E2SM-CP event trigger (format 1, upon event): the E2 node reports pending
    events once max_batch_size of them are pending or max_batch_delay_ms has
    elapsed. 0 leaves a limit out; with both 0 each event is reported in its
    own indication as it occurs.
    """
    SECTION = "ran.e2sm_cp"

    max_batch_size: int = 0
    max_batch_delay_ms: int = 0

    @classmethod
    def from_dict(cls, d, warn: Callable[[str], None] = _ignore) -> "CpConfig":
        d = _check_section(cls.SECTION, d)
        _warn_unknown_keys(cls.SECTION, d, ("max_batch_size", "max_batch_delay_ms"), warn)
        # E2SM-CP maxBatchSize INTEGER (1..65535), maxBatchDelay INTEGER (1..4294967295), 0: absent
        return cls(max_batch_size=_get_int(cls.SECTION, d, "max_batch_size", cls.max_batch_size, 0, 65535),
                   max_batch_delay_ms=_get_int(cls.SECTION, d, "max_batch_delay_ms", cls.max_batch_delay_ms,
                                               0, _UINT32_MAX))


@dataclass(frozen=True)
class SdlConfig:
    """
    Retention of the data stored in the SDL (the SDL has no expiry, the xApp
    removes old data itself):
      cp_max_events_per_node: E2SM-CP events kept per E2 node, the oldest
        are removed beyond it
      cp_ue_retention_s: an E2SM-CP UE context (and its event index) is
        removed this long after the last event of the UE
      kpm_retention_s: E2SM-KPM records older than this (from the newest
        record of the E2 node) are removed
    """
    SECTION = "ran.sdl"

    cp_max_events_per_node: int = 100000
    cp_ue_retention_s: int = 600
    kpm_retention_s: int = 3600

    def __post_init__(self):
        for name in ("cp_max_events_per_node", "cp_ue_retention_s", "kpm_retention_s"):
            if getattr(self, name) < 1:
                raise ConfigError(f"{self.SECTION}.{name} must be >= 1, got {getattr(self, name)}")

    @classmethod
    def from_dict(cls, d, warn: Callable[[str], None] = _ignore) -> "SdlConfig":
        d = _check_section(cls.SECTION, d)
        _warn_unknown_keys(cls.SECTION, d, ("cp_max_events_per_node", "cp_ue_retention_s", "kpm_retention_s"), warn)
        return cls(cp_max_events_per_node=_get_int(cls.SECTION, d, "cp_max_events_per_node",
                                                   cls.cp_max_events_per_node, 1),
                   cp_ue_retention_s=_get_int(cls.SECTION, d, "cp_ue_retention_s", cls.cp_ue_retention_s, 1),
                   kpm_retention_s=_get_int(cls.SECTION, d, "kpm_retention_s", cls.kpm_retention_s, 1))


@dataclass(frozen=True)
class RanConfig:
    """
    target_oid_list: OIDs of the RAN functions to subscribe to, each one of a
    supported service model (Constants.SERVICE_MODEL_BY_OID); defaults to all
    of them. poll_interval_ms: how often the R-NIB is polled for E2 nodes and
    their connection status, i.e. how soon a new or reconnected node is
    subscribed to.
    """
    SECTION = "ran"

    target_oid_list: Tuple[str, ...] = tuple(Constants.SERVICE_MODEL_BY_OID)
    poll_interval_ms: int = 5000
    kpm: KpmConfig = field(default_factory=KpmConfig)
    cp: CpConfig = field(default_factory=CpConfig)
    sdl: SdlConfig = field(default_factory=SdlConfig)

    @classmethod
    def from_dict(cls, d, warn: Callable[[str], None] = _ignore) -> "RanConfig":
        d = _check_section(cls.SECTION, d)
        _warn_unknown_keys(cls.SECTION, d, ("target_oid_list", "poll_interval_ms", "e2sm_kpm", "e2sm_cp", "sdl"),
                           warn)
        return cls(target_oid_list=cls._target_oids(d, warn),
                   poll_interval_ms=_get_int(cls.SECTION, d, "poll_interval_ms", cls.poll_interval_ms, 100),
                   kpm=KpmConfig.from_dict(d.get("e2sm_kpm"), warn),
                   cp=CpConfig.from_dict(d.get("e2sm_cp"), warn),
                   sdl=SdlConfig.from_dict(d.get("sdl"), warn))

    @classmethod
    def _target_oids(cls, d: dict, warn: Callable[[str], None]) -> Tuple[str, ...]:
        key = f"{cls.SECTION}.target_oid_list"
        if "target_oid_list" not in d:
            warn(f"Config: {key} not set, subscribing to every supported RAN function OID "
                 f"{list(Constants.SERVICE_MODEL_BY_OID)}")
            return cls.target_oid_list
        oids = d["target_oid_list"]
        if not isinstance(oids, list) or not all(isinstance(o, str) for o in oids):
            raise ConfigError(f"{key} must be a list of OID strings, got {oids!r}")
        supported = []
        for oid in oids:
            if oid not in Constants.SERVICE_MODEL_BY_OID:
                warn(f"Config: ignoring {key} entry {oid}: no supported service model has this OID "
                     f"(supported: {Constants.SERVICE_MODEL_BY_OID})")
            elif oid not in supported:
                supported.append(oid)
        if not supported:
            raise ConfigError(f"{key} has no supported OID, nothing would be subscribed to: {oids!r}")
        return tuple(supported)
