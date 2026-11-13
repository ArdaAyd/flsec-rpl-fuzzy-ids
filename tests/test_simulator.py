import numpy as np

from flsec.simulator import SimConfig, Simulation, run_simulation


def short(**kw):
    return SimConfig(duration=600.0, **kw)


def test_network_forms_without_attackers():
    r = run_simulation(short(pan=0.0, detector="none"))
    assert r["joined_at_end"] == 1.0
    assert r["n_attackers"] == 0


def test_aggressive_attackers_are_blocked():
    r = run_simulation(short(pan=0.2, ari=1.0, detector="flsec"))
    assert r["recall"] == 1.0
    assert r["node_detection_rate"] == 1.0


def test_same_seed_same_result():
    cfg = short(pan=0.3, ari=2.0, mobile=True, seed=3)
    a, b = run_simulation(cfg), run_simulation(cfg)
    assert {k: a[k] for k in ("tp", "fp", "tn", "fn", "ftd_mean")} == \
           {k: b[k] for k in ("tp", "fp", "tn", "fn", "ftd_mean")}


def test_attacker_sets_are_nested():
    small = Simulation(short(pan=0.1)).is_attacker
    large = Simulation(short(pan=0.5)).is_attacker
    assert np.all(large[small])
    assert small.sum() == 2 and large.sum() == 8
