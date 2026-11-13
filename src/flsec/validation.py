"""Detection validation (quarantine) and blocking (phase III)."""

import math
from dataclasses import dataclass
from enum import Enum

from .config import Phase3Params


class Status(str, Enum):
    NORMAL = "normal"
    QUARANTINE = "quarantine"
    SOFT_BLOCKED = "soft_blocked"
    HARD_BLOCKED = "hard_blocked"


def _decay(omega, lower, upper, p):
    k = math.log(lower / upper) / (p.beta - p.delta)
    return upper * math.exp(k * (omega - p.delta))


def max_detection(omega, p=Phase3Params()):
    """Eq. 13."""
    return _decay(omega, p.md_lower, p.md_upper, p)


def quarantine_period(omega, p=Phase3Params()):
    """Eq. 14, in seconds."""
    return _decay(omega, p.qp_lower, p.qp_upper, p)


@dataclass
class SuspectState:
    status: Status = Status.NORMAL
    dc: int = 0  # detection counter
    bc: int = 0  # block counter
    md: float | None = None
    quarantine_start: float | None = None
    qp_total: float = 0.0
    block_end: float | None = None


class ValidationBlocking:
    """Per-detector quarantine and blacklist.

    adaptive=False uses fixed_md instead of Eq. 13; use_rdt=False ignores RDT flags.
    """

    def __init__(self, params=Phase3Params(), adaptive=True, fixed_md=3.0, use_rdt=True):
        self.p = params
        self.adaptive = adaptive
        self.fixed_md = fixed_md
        self.use_rdt = use_rdt
        self.states = {}

    def status(self, nid, t):
        state = self.states.get(nid)
        if state is None:
            return Status.NORMAL
        self._expire(state, t)
        return state.status

    def is_blocked(self, nid, t):
        return self.status(nid, t) in (Status.SOFT_BLOCKED, Status.HARD_BLOCKED)

    def is_quarantined(self, nid, t):
        return self.status(nid, t) == Status.QUARANTINE

    def _expire(self, state, t):
        if state.status == Status.QUARANTINE and t >= state.quarantine_start + state.qp_total:
            state.status, state.dc, state.qp_total = Status.NORMAL, 0, 0.0
        elif state.status == Status.SOFT_BLOCKED and t >= state.block_end:
            state.status, state.dc = Status.NORMAL, 0

    def on_detection(self, nid, omega, rdt_flag, t):
        """Called when a neighbor's aggressive weight exceeds delta."""
        state = self.states.setdefault(nid, SuspectState())
        self._expire(state, t)
        if state.status in (Status.SOFT_BLOCKED, Status.HARD_BLOCKED):
            return state.status

        state.dc += 1
        if self.use_rdt and rdt_flag:
            md, qp = self.p.md_upper, self.p.qp_upper
        else:
            md = max_detection(omega, self.p) if self.adaptive else self.fixed_md
            qp = quarantine_period(omega, self.p)
        state.md = md

        if state.status == Status.NORMAL:
            state.status, state.quarantine_start, state.qp_total = Status.QUARANTINE, t, qp
        else:
            state.qp_total += qp  # Eq. 15

        if state.dc >= md - 1e-9:
            self._block(state, t)
        return state.status

    def _block(self, state, t):
        state.bc += 1
        state.dc, state.qp_total, state.quarantine_start = 0, 0.0, None
        if state.bc > self.p.lam:
            state.status, state.block_end = Status.HARD_BLOCKED, math.inf
        else:
            state.status = Status.SOFT_BLOCKED
            state.block_end = t + self.p.bp0 * self.p.q ** (state.bc - 1)  # Eq. 16
