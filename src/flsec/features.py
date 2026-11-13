"""Neighbor list and attack activity variables (phase I).

stia_mode selects how PTI and SoE are kept (Eqs. 2-5):
    "window"      t = 1..N over the DIOs of the window, PTI_1 = DTI_1; DTI_1 is measured from the
                  neighbor's previous DIO even if it fell in the previous window (default)
    "within"      only intervals between two DIOs of the same window are used
    "persistent"  PTI is never reset
Intervals are clipped to dti_cap before smoothing.
"""

import math
from dataclasses import dataclass, field

from . import config


@dataclass
class NeighborRecord:
    node_id: int
    dio_counter: int = 0
    total_dio: int = 0
    last_rx: float | None = None
    dti: float | None = None
    pti: float | None = None
    soe: float = 0.0
    window_dti_sum: float = 0.0
    window_dti_count: int = 0
    rdt_flag: bool = False


@dataclass(frozen=True)
class WindowObservation:
    node_id: int
    dio_counter: int
    dti: float
    stia: float
    rdt_flag: bool

    def as_input(self):
        return (float(self.dio_counter), self.dti, self.stia)


@dataclass
class NeighborList:
    alpha: float = config.SMOOTHING_ALPHA
    dti_cap: float = config.INPUT_UNIVERSE[1]
    stia_mode: str = "window"
    dti_mode: str = "last"  # "last" or "mean" DTI of the window as fuzzy input
    records: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.stia_mode not in ("window", "within", "persistent"):
            raise ValueError(f"unknown stia_mode: {self.stia_mode}")
        if self.dti_mode not in ("last", "mean"):
            raise ValueError(f"unknown dti_mode: {self.dti_mode}")

    def _record(self, src):
        rec = self.records.get(src)
        if rec is None:
            rec = self.records[src] = NeighborRecord(src)
        return rec

    def record_dio(self, src, t):
        rec = self._record(src)
        rec.dio_counter += 1
        rec.total_dio += 1
        interval = None if rec.last_rx is None else t - rec.last_rx  # Eq. 2
        if interval is not None:
            rec.dti = interval
            rec.window_dti_sum += min(interval, self.dti_cap)
            rec.window_dti_count += 1
        if self.stia_mode == "within":
            if rec.dio_counter > 1 and interval is not None:
                self._smooth(rec, min(interval, self.dti_cap))
        else:
            self._smooth(rec, self.dti_cap if interval is None else min(interval, self.dti_cap))
        rec.last_rx = t
        return rec

    def _smooth(self, rec, dti):
        if rec.pti is None:
            rec.pti = dti  # PTI_1 = DTI_1
            return
        rec.pti = self.alpha * dti + (1.0 - self.alpha) * rec.pti  # Eq. 3
        rec.soe += (dti - rec.pti) ** 2  # Eq. 4

    def record_rdt(self, src):
        self._record(src).rdt_flag = True

    def remove(self, src):
        self.records.pop(src, None)

    def close_window(self):
        """Observations of the neighbors heard in this window; resets the per-window fields."""
        observations = []
        for rec in self.records.values():
            if rec.dio_counter > 0:
                stia = math.sqrt(rec.soe / rec.dio_counter)  # Eq. 5
                if self.dti_mode == "mean" and rec.window_dti_count:
                    dti = rec.window_dti_sum / rec.window_dti_count
                else:
                    dti = self.dti_cap if rec.dti is None else min(rec.dti, self.dti_cap)
                observations.append(WindowObservation(rec.node_id, rec.dio_counter, dti, stia, rec.rdt_flag))
            rec.dio_counter = 0
            rec.soe = 0.0
            rec.window_dti_sum = 0.0
            rec.window_dti_count = 0
            rec.rdt_flag = False
            if self.stia_mode != "persistent":
                rec.pti = None
        return observations
