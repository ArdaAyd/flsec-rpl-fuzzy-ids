"""Discrete-event simulation of the RPL control plane under DIO neighbor suppression attacks.

Node 0 is the DODAG root. The model covers what the detectors observe: DIO, DIS and RDT messages
over a unit-disk radio, Trickle timers (RFC 6206), rank-based parent selection, random waypoint
mobility and attackers that replay a captured DIO every `ari` seconds after `attack_start`.

Topology, attacker set and mobility depend only on the seed and the network size, so all
detectors and attack settings of a seed run on the same network (attacker sets are nested
across PAN levels).
"""

import heapq
import math
from dataclasses import asdict, dataclass, field

import numpy as np

from . import config as C
from .detectors import make_detector_factory
from .metrics import summarize

EV_TRICKLE_FIRE, EV_TRICKLE_END, EV_RX, EV_REPLAY, EV_DATA, EV_DIS, EV_WINDOW, EV_ATTACK = range(8)
PKT_DIO, PKT_DIS, PKT_RDT = range(3)

INF = math.inf
ROOT_RANK = 256.0


@dataclass
class SimConfig:
    n_sensors: int = 16
    pan: float = 0.2
    ari: float = 2.0
    mobile: bool = False
    detector: str = "flsec"
    detector_options: dict = field(default_factory=dict)
    seed: int = 0
    duration: float = C.SIM_DURATION_S
    area: float = C.AREA_M
    radio_range: float = C.RADIO_RANGE_M
    p_loss: float = 0.02
    mac_delay_max: float = 0.125  # ContikiMAC channel check interval
    attack_start: float = C.ATTACK_START_S
    detection_start: float = C.DETECTION_START_S
    window: float = C.OBSERVATION_WINDOW_S
    trickle_imin: float = C.TRICKLE_IMIN_S
    trickle_doublings: int = C.TRICKLE_DOUBLINGS
    trickle_k: int = C.TRICKLE_K
    data_period: float = 60.0
    dis_start_delay: float = 5.0
    dis_interval: float = 60.0
    neighbor_timeout: float = INF
    etx_model: str = "unit"  # "unit": ETX = 1 in range (UDGM); "distance": 1 + (d/R)^2
    speed_min: float = 1.0
    speed_max: float = 2.0
    parent_switch_threshold: float = 128.0
    rank_increase: float = 256.0
    position_step: float = 0.5
    record_windows: bool = False

    @property
    def n_attackers(self):
        return int(math.floor(self.pan * self.n_sensors + 0.5))


class Simulation:
    def __init__(self, cfg: SimConfig):
        self.cfg = cfg
        self.n = n = cfg.n_sensors + 1
        self.R = cfg.radio_range
        self.imin = cfg.trickle_imin
        self.imax = cfg.trickle_imin * 2 ** cfg.trickle_doublings

        topo_rng = np.random.default_rng([cfg.seed, 11, cfg.n_sensors])
        self.pos0 = self._connected_positions(topo_rng)
        order = topo_rng.permutation(np.arange(1, n))
        self.is_attacker = np.zeros(n, dtype=bool)
        self.is_attacker[order[:cfg.n_attackers]] = True
        self.legit = [i for i in range(n) if not self.is_attacker[i]]

        if cfg.mobile:
            self._build_waypoints(np.random.default_rng([cfg.seed, 22, cfg.n_sensors]))
            self._pos_cache = {}
        else:
            d = np.linalg.norm(self.pos0[:, None, :] - self.pos0[None, :, :], axis=2)
            self.static_dist = d
            self.static_nbrs = [np.nonzero((d[i] <= self.R) & (np.arange(n) != i))[0] for i in range(n)]

        # Shared by all detectors of a scenario, so paired runs only diverge through detection.
        self.rng = np.random.default_rng(
            [cfg.seed, 33, cfg.n_sensors, int(cfg.mobile), round(cfg.pan * 100), round(cfg.ari * 10)])

        self.rank = np.full(n, INF)
        self.parent = [None] * n
        self.joined = np.zeros(n, dtype=bool)
        self.nbr = [dict() for _ in range(n)]  # src -> (advertised rank, last heard)

        self.tr_I = np.full(n, self.imax)
        self.tr_c = np.zeros(n, dtype=int)
        self.tr_gen = np.zeros(n, dtype=int)
        self.tr_running = np.zeros(n, dtype=bool)
        self.dis_active = np.zeros(n, dtype=bool)

        self.attacking = np.zeros(n, dtype=bool)
        self.captured = [None] * n

        factory = make_detector_factory(cfg.detector, cfg.detector_options)
        self.detectors = [None if self.is_attacker[i] else factory() for i in range(n)]
        self.rdt_enabled = cfg.detector == "flsec" and cfg.detector_options.get("use_rdt", True)

        self.heard_after = [set() for _ in range(n)]
        self.stat = {key: np.zeros(n, dtype=int) for key in (
            "dio_tx", "dio_suppressed", "dio_rx", "dio_dropped", "attack_dio_processed",
            "trickle_resets", "parent_changes", "dis_tx", "rdt_tx")}
        self.window_records = []
        self._heap = []
        self._seq = 0

    # topology and mobility

    def _connected_positions(self, rng):
        for _ in range(10_000):
            pos = rng.uniform(0, self.cfg.area, size=(self.n, 2))
            adj = np.linalg.norm(pos[:, None, :] - pos[None, :, :], axis=2) <= self.R
            seen, stack = {0}, [0]
            while stack:
                u = stack.pop()
                for v in np.nonzero(adj[u])[0]:
                    if int(v) not in seen:
                        seen.add(int(v))
                        stack.append(int(v))
            if len(seen) == self.n:
                return pos
        raise RuntimeError("could not draw a connected topology")

    def _build_waypoints(self, rng):
        """Random waypoint traces as (segment start times, start points, velocities)."""
        self.wp = []
        for i in range(self.n):
            if i == 0:
                self.wp.append((np.array([0.0]), self.pos0[:1].copy(), np.zeros((1, 2))))
                continue
            t0s, p0s, vs = [], [], []
            t, p = 0.0, self.pos0[i].copy()
            while t < self.cfg.duration + 1.0:
                dest = rng.uniform(0, self.cfg.area, size=2)
                speed = rng.uniform(self.cfg.speed_min, self.cfg.speed_max)
                dist = float(np.linalg.norm(dest - p))
                if dist < 1e-6:
                    continue
                t0s.append(t)
                p0s.append(p.copy())
                vs.append((dest - p) / dist * speed)
                t += dist / speed
                p = dest
            self.wp.append((np.array(t0s), np.array(p0s), np.array(vs)))

    def positions_at(self, t):
        if not self.cfg.mobile:
            return self.pos0
        step = int(t / self.cfg.position_step)
        pos = self._pos_cache.get(step)
        if pos is None:
            tq = step * self.cfg.position_step
            pos = np.empty((self.n, 2))
            for i, (t0s, p0s, vs) in enumerate(self.wp):
                k = int(np.searchsorted(t0s, tq, side="right") - 1)
                pos[i] = p0s[k] + vs[k] * (tq - t0s[k])
            self._pos_cache[step] = pos
        return pos

    def distance(self, i, j, t):
        if not self.cfg.mobile:
            return float(self.static_dist[i, j])
        p = self.positions_at(t)
        return math.hypot(p[i, 0] - p[j, 0], p[i, 1] - p[j, 1])

    # events and radio

    def push(self, t, kind, payload):
        self._seq += 1
        heapq.heappush(self._heap, (t, self._seq, kind, payload))

    def broadcast(self, src, pkt, t, rank=INF, origin=-1):
        if self.cfg.mobile:
            p = self.positions_at(t)
            d = np.hypot(p[:, 0] - p[src, 0], p[:, 1] - p[src, 1])
            receivers = np.nonzero(d <= self.R)[0]
            receivers = receivers[receivers != src]
        else:
            receivers = self.static_nbrs[src]
        if len(receivers) == 0:
            return
        delivered = self.rng.random(len(receivers)) >= self.cfg.p_loss
        delays = self.rng.uniform(0.0, self.cfg.mac_delay_max, len(receivers))
        for j, ok, delay in zip(receivers, delivered, delays):
            if ok:
                self.push(t + delay, EV_RX, (int(j), pkt, src, rank, origin))

    # Trickle

    def _start_interval(self, i, t, interval):
        self.tr_gen[i] += 1
        self.tr_I[i] = interval
        self.tr_c[i] = 0
        self.tr_running[i] = True
        gen = int(self.tr_gen[i])
        self.push(t + self.rng.uniform(interval / 2, interval), EV_TRICKLE_FIRE, (i, gen))
        self.push(t + interval, EV_TRICKLE_END, (i, gen))

    def trickle_reset(self, i, t):
        # Like ContikiRPL: no reset if the timer already runs at Imin.
        if self.tr_running[i] and self.tr_I[i] <= self.imin + 1e-9:
            return
        self._start_interval(i, t, self.imin)
        self.stat["trickle_resets"][i] += 1
        if self.rdt_enabled and not self.is_attacker[i]:
            self.stat["rdt_tx"][i] += 1
            self.broadcast(i, PKT_RDT, t)

    def _stop_trickle(self, i):
        self.tr_gen[i] += 1
        self.tr_running[i] = False

    # RPL

    def link_cost(self, d):
        if self.cfg.etx_model == "distance":
            return self.cfg.rank_increase * (1.0 + (d / self.R) ** 2)
        return self.cfg.rank_increase

    def select_parent(self, i, t):
        det = self.detectors[i]
        current = self.parent[i]
        best, best_cost, current_cost = None, INF, INF
        for nb, (nb_rank, heard) in self.nbr[i].items():
            if nb_rank == INF or t - heard > self.cfg.neighbor_timeout or self.parent[nb] == i:
                continue
            if det is not None and det.is_isolated(nb, t):
                continue
            d = self.distance(i, nb, t)
            if d > self.R:
                continue
            cost = nb_rank + self.link_cost(d)
            if nb == current:
                current_cost = cost
            if cost < best_cost:
                best, best_cost = nb, cost
        if current is not None and current_cost < INF:
            if best != current and best_cost < current_cost - self.cfg.parent_switch_threshold:
                self._change_parent(i, best, best_cost, t)
            else:
                self.rank[i] = current_cost
        elif best is not None:
            self._change_parent(i, best, best_cost, t)
        elif current is not None or self.joined[i]:
            self._detach(i, t)

    def _change_parent(self, i, new_parent, cost, t):
        self.parent[i] = new_parent
        self.rank[i] = cost
        self.stat["parent_changes"][i] += 1
        if not self.joined[i]:
            self.joined[i] = True
            self.dis_active[i] = False
        self.trickle_reset(i, t)

    def _detach(self, i, t):
        self.parent[i] = None
        self.rank[i] = INF
        self.joined[i] = False
        self._stop_trickle(i)
        if not self.dis_active[i]:
            self.dis_active[i] = True
            self.push(t, EV_DIS, i)

    # handlers

    def on_trickle_fire(self, i, gen, t):
        if gen != self.tr_gen[i] or self.attacking[i]:
            return
        if self.tr_c[i] < self.cfg.trickle_k:
            self.stat["dio_tx"][i] += 1
            self.broadcast(i, PKT_DIO, t, rank=float(self.rank[i]), origin=i)
        else:
            self.stat["dio_suppressed"][i] += 1

    def on_trickle_end(self, i, gen, t):
        if gen != self.tr_gen[i] or self.attacking[i]:
            return
        self._start_interval(i, t, min(2.0 * self.tr_I[i], self.imax))

    def on_rx(self, j, pkt, src, rank, origin, t):
        if pkt == PKT_DIO:
            self.on_dio(j, src, rank, origin, t)
        elif pkt == PKT_DIS:
            if self.joined[j] and not self.attacking[j]:
                self.trickle_reset(j, t)
        elif self.detectors[j] is not None:
            self.detectors[j].observe_rdt(src, t)

    def on_dio(self, j, src, rank, origin, t):
        if self.is_attacker[j]:
            if not self.is_attacker[src]:
                self.captured[j] = (rank, origin)
            if self.attacking[j]:
                return
        det = self.detectors[j]
        if det is not None:
            self.stat["dio_rx"][j] += 1
            if t >= self.cfg.detection_start:
                self.heard_after[j].add(src)
            if det.is_blocked(src, t):
                self.stat["dio_dropped"][j] += 1
                return
            det.observe_dio(src, t)
            if self.is_attacker[src]:
                self.stat["attack_dio_processed"][j] += 1
        self.nbr[j][src] = (rank, t)
        if self.tr_running[j]:
            self.tr_c[j] += 1
        if j != 0:
            self.select_parent(j, t)

    def on_data(self, i, t):
        if not self.attacking[i] and (self.joined[i] or self.parent[i] is not None):
            self.select_parent(i, t)
        self.push(t + self.cfg.data_period, EV_DATA, i)

    def on_dis_timer(self, i, t):
        if self.joined[i] or self.attacking[i]:
            self.dis_active[i] = False
            return
        self.stat["dis_tx"][i] += 1
        self.broadcast(i, PKT_DIS, t)
        self.push(t + self.cfg.dis_interval, EV_DIS, i)

    def on_attack_start(self, i, t):
        self.attacking[i] = True
        self._stop_trickle(i)
        self.push(t + self.rng.uniform(0.0, self.cfg.ari), EV_REPLAY, i)

    def on_replay(self, i, t):
        if self.captured[i] is not None:
            rank, origin = self.captured[i]
            self.stat["dio_tx"][i] += 1
            self.broadcast(i, PKT_DIO, t, rank=rank, origin=origin)
        self.push(t + self.cfg.ari, EV_REPLAY, i)

    def on_window(self, t):
        evaluate = t >= self.cfg.detection_start - 1e-9
        batched = []
        for i, det in enumerate(self.detectors):
            if det is None:
                continue
            if det.batched:
                obs = det.collect_window()
                if evaluate and obs:
                    batched.append((i, det, obs))
            else:
                det.end_window(t, evaluate)
        if batched:
            X = np.vstack([det.fuzzy_inputs(obs) for _, det, obs in batched])
            omegas = batched[0][1].fls.infer(X)
            k = 0
            for i, det, obs in batched:
                part = omegas[k:k + len(obs)]
                k += len(obs)
                if self.cfg.record_windows:
                    self.window_records.extend(
                        (t, i, o.node_id, o.dio_counter, o.dti, o.stia, o.rdt_flag, float(w),
                         bool(self.is_attacker[o.node_id])) for o, w in zip(obs, part))
                det.apply_window(t, obs, part)
        if t + self.cfg.window <= self.cfg.duration + 1e-9:
            self.push(t + self.cfg.window, EV_WINDOW, None)

    def run(self):
        cfg = self.cfg
        self.rank[0], self.joined[0] = ROOT_RANK, True
        self._start_interval(0, 0.0, self.imin)
        for i in range(1, self.n):
            self.dis_active[i] = True
            self.push(cfg.dis_start_delay + self.rng.uniform(0, 1.0), EV_DIS, i)
            self.push(self.rng.uniform(0, cfg.data_period), EV_DATA, i)
            if self.is_attacker[i]:
                self.push(cfg.attack_start, EV_ATTACK, i)
        self.push(cfg.window, EV_WINDOW, None)

        handlers = {
            EV_TRICKLE_FIRE: lambda p, t: self.on_trickle_fire(*p, t),
            EV_TRICKLE_END: lambda p, t: self.on_trickle_end(*p, t),
            EV_RX: lambda p, t: self.on_rx(*p, t),
            EV_REPLAY: self.on_replay,
            EV_DATA: self.on_data,
            EV_DIS: self.on_dis_timer,
            EV_WINDOW: lambda p, t: self.on_window(t),
            EV_ATTACK: self.on_attack_start,
        }
        heap = self._heap
        while heap and heap[0][0] <= cfg.duration:
            t, _, kind, payload = heapq.heappop(heap)
            handlers[kind](payload, t)
        return self.results()

    def results(self):
        out = asdict(self.cfg)
        out["detector_options"] = repr(self.cfg.detector_options)
        out["n_attackers"] = self.cfg.n_attackers
        out.update(summarize(self))
        return out


def run_simulation(cfg):
    return Simulation(cfg).run()
