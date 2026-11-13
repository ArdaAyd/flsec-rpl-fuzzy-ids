"""Intrusion detectors run by every legitimate node: FLSec-RPL, CoSec-RPL and Anomaly-Based IDS."""

from dataclasses import dataclass

import numpy as np

from .config import Phase3Params
from .features import NeighborList
from .fuzzy import build_paper_fls
from .validation import Status, ValidationBlocking


class Detector:
    """No-op detector; also the common interface used by the simulator."""

    kind = "none"
    batched = False

    def __init__(self):
        self.first_suspected = {}  # neighbor -> first time judged suspicious
        self.ever_blocked = {}  # neighbor -> first time blocked

    def observe_dio(self, src, t):
        pass

    def observe_rdt(self, src, t):
        pass

    def is_blocked(self, src, t):
        return False

    def is_isolated(self, src, t):
        """Isolated neighbors are not used as parents."""
        return self.is_blocked(src, t)

    def end_window(self, t, evaluate):
        pass


@dataclass
class FLSecOptions:
    defuzz: str = "paper"
    input_mfs: dict | None = None
    stia_mode: str = "window"
    dti_mode: str = "last"
    use_stia: bool = True  # False feeds STIA = 0 (ablation)
    use_rdt: bool = True
    validation: bool = True  # False blocks on the first detection (ablation)
    adaptive_md: bool = True
    fixed_md: float = 3.0
    passive: bool = False  # score only, never quarantine or block


class FLSecDetector(Detector):
    kind = "flsec"
    batched = True  # the simulator scores all FLSec detectors of a window in one call

    def __init__(self, fls, options, params=Phase3Params()):
        super().__init__()
        self.fls = fls
        self.options = options
        self.delta = params.delta
        self.neighbors = NeighborList(stia_mode=options.stia_mode, dti_mode=options.dti_mode)
        if options.validation:
            self.vb = ValidationBlocking(params, options.adaptive_md, options.fixed_md, options.use_rdt)
        else:
            self.vb = ValidationBlocking(params, adaptive=False, fixed_md=1.0, use_rdt=False)

    def observe_dio(self, src, t):
        self.neighbors.record_dio(src, t)

    def observe_rdt(self, src, t):
        if self.options.use_rdt:
            self.neighbors.record_rdt(src)

    def is_blocked(self, src, t):
        return self.vb.is_blocked(src, t)

    def is_isolated(self, src, t):
        return self.vb.status(src, t) != Status.NORMAL

    def collect_window(self):
        return self.neighbors.close_window()

    def fuzzy_inputs(self, observations):
        X = np.array([o.as_input() for o in observations], dtype=float).reshape(-1, 3)
        if not self.options.use_stia:
            X[:, 2] = 0.0
        return X

    def apply_window(self, t, observations, omegas):
        for obs, omega in zip(observations, omegas):
            if omega <= self.delta:
                continue
            self.first_suspected.setdefault(obs.node_id, t)
            if self.options.passive:
                continue
            status = self.vb.on_detection(obs.node_id, float(omega), obs.rdt_flag, t)
            if status in (Status.SOFT_BLOCKED, Status.HARD_BLOCKED):
                self.ever_blocked.setdefault(obs.node_id, t)
                self.neighbors.remove(obs.node_id)

    def end_window(self, t, evaluate):
        observations = self.collect_window()
        if evaluate and observations:
            self.apply_window(t, observations, self.fls.infer(self.fuzzy_inputs(observations)))


def tukey_hinges(values):
    """Q1 and Q3 as medians of the lower and upper halves."""
    x = np.sort(np.asarray(values, dtype=float))
    n = len(x)
    if n == 1:
        return float(x[0]), float(x[0])
    return float(np.median(x[: n // 2])), float(np.median(x[(n + 1) // 2:]))


class CoSecDetector(Detector):
    """CoSec-RPL (Verma and Ranga, 2020).

    Suspect if the cumulative DIO count is above Q3 + iqr_factor * IQR and the last inter-DIO gap
    is at most sigma seconds; permanent block after beta detections.
    """

    kind = "cosec"

    def __init__(self, sigma=0.5, iqr_factor=1.0, beta=5):
        super().__init__()
        self.sigma, self.iqr_factor, self.beta = sigma, iqr_factor, beta
        self.table = {}  # src -> [count, t_previous, t_recent]
        self.detection_count = {}
        self.blocked = set()

    def observe_dio(self, src, t):
        rec = self.table.setdefault(src, [0, 0.0, 0.0])
        rec[0] += 1
        rec[1], rec[2] = rec[2], t

    def is_blocked(self, src, t):
        return src in self.blocked

    def end_window(self, t, evaluate):
        if not evaluate or not self.table:
            return
        q1, q3 = tukey_hinges([rec[0] for rec in self.table.values()])
        upper = q3 + self.iqr_factor * (q3 - q1)
        for src, (count, t_prev, t_recent) in list(self.table.items()):
            if count > upper and t_recent - t_prev <= self.sigma:
                self.first_suspected.setdefault(src, t)
                self.detection_count[src] = self.detection_count.get(src, 0) + 1
                if self.detection_count[src] >= self.beta:
                    self.blocked.add(src)
                    self.ever_blocked.setdefault(src, t)
                    del self.table[src]


class AnomalyDetector(Detector):
    """Anomaly-Based IDS (Farzaneh et al., 2019) as described in the FLSec-RPL paper.

    A neighbor whose DIO count in the window exceeds mean + k_std * std over all known neighbors
    is blocked permanently.
    """

    kind = "anomaly"

    def __init__(self, k_std=1.0):
        super().__init__()
        self.k_std = k_std
        self.known = set()
        self.window_counts = {}
        self.blocked = set()

    def observe_dio(self, src, t):
        self.known.add(src)
        self.window_counts[src] = self.window_counts.get(src, 0) + 1

    def is_blocked(self, src, t):
        return src in self.blocked

    def end_window(self, t, evaluate):
        if evaluate:
            ids = [s for s in self.known if s not in self.blocked]
            if ids:
                counts = np.array([self.window_counts.get(s, 0) for s in ids], dtype=float)
                threshold = counts.mean() + self.k_std * counts.std()
                for src, count in zip(ids, counts):
                    if count > threshold:
                        self.first_suspected.setdefault(src, t)
                        self.blocked.add(src)
                        self.ever_blocked.setdefault(src, t)
        self.window_counts.clear()


def make_detector_factory(kind, options=None):
    """Returns a callable creating one detector per node (the FIS is shared)."""
    options = dict(options or {})
    if kind == "flsec":
        opts = FLSecOptions(**options)
        fls = build_paper_fls(defuzz=opts.defuzz, input_mfs=opts.input_mfs)
        return lambda: FLSecDetector(fls, opts)
    if kind == "cosec":
        return lambda: CoSecDetector(**options)
    if kind == "anomaly":
        return lambda: AnomalyDetector(**options)
    if kind == "none":
        return Detector
    raise ValueError(f"unknown detector: {kind}")
