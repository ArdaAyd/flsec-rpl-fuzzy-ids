import math

import pytest

from flsec.config import Phase3Params
from flsec.features import NeighborList
from flsec.validation import Status, ValidationBlocking, max_detection, quarantine_period


def feed(nl, src, times):
    for t in times:
        nl.record_dio(src, float(t))
    return nl.close_window()


def test_steady_replay_has_zero_stia():
    nl = NeighborList()
    feed(nl, 7, [-1.0])
    (obs,) = feed(nl, 7, range(1, 30, 2))  # ARI = 2 s
    assert obs.dio_counter == 15
    assert obs.dti == pytest.approx(2.0)
    assert obs.stia == pytest.approx(0.0)


def test_first_attack_window_has_high_stia():
    # Previous DIO long ago: DTI_1 is capped at 30 s, so the jump to 1 s intervals inflates STIA.
    nl = NeighborList()
    feed(nl, 7, [-100.0])
    first = feed(nl, 7, range(0, 30))
    second = feed(nl, 7, range(30, 60))
    assert first[0].stia > 9
    assert second[0].stia == pytest.approx(0.0)


def test_trickle_burst_stia():
    times = [0.0, 4.0, 12.0, 28.0]  # intervals 4, 8, 16 s
    within = NeighborList(stia_mode="within")
    (obs,) = feed(within, 3, times)
    assert obs.stia == pytest.approx(math.sqrt((3.6 ** 2 + 10.44 ** 2) / 4))
    assert obs.dti == pytest.approx(16.0)

    literal = NeighborList()
    feed(literal, 3, [-300.0])
    (obs,) = feed(literal, 3, times)
    assert obs.stia > 10


def test_window_reset():
    nl = NeighborList()
    nl.record_dio(5, 10.0)
    nl.record_rdt(5)
    (first,) = nl.close_window()
    assert first.rdt_flag and first.dti == 30.0
    (second,) = feed(nl, 5, [50.0])
    assert second.dio_counter == 1 and not second.rdt_flag
    assert second.dti == 30.0 and second.stia == 0.0
    assert nl.close_window() == []


def test_persistent_mode():
    nl = NeighborList(stia_mode="persistent")
    feed(nl, 1, [0.0, 30.0])
    (obs,) = feed(nl, 1, [31.0, 32.0, 33.0])
    assert obs.stia > 10


def test_decay_bounds():
    p = Phase3Params()
    assert max_detection(0.5, p) == pytest.approx(6.0)
    assert max_detection(1.0, p) == pytest.approx(1.0)
    assert quarantine_period(0.5, p) == pytest.approx(180.0)
    assert quarantine_period(1.0, p) == pytest.approx(30.0)
    assert max_detection(5 / 6, p) == pytest.approx(1.817, abs=1e-3)


def test_block_escalation():
    vb = ValidationBlocking()
    assert vb.on_detection(9, 5 / 6, False, 120.0) == Status.QUARANTINE
    assert vb.on_detection(9, 5 / 6, False, 150.0) == Status.SOFT_BLOCKED
    assert vb.is_blocked(9, 449.0) and not vb.is_blocked(9, 450.0)
    t = 450.0
    for period in (600.0, 1200.0):
        vb.on_detection(9, 5 / 6, False, t)
        vb.on_detection(9, 5 / 6, False, t + 30)
        assert vb.states[9].block_end == pytest.approx(t + 30 + period)
        t += 30 + period
    vb.on_detection(9, 5 / 6, False, t)
    assert vb.on_detection(9, 5 / 6, False, t + 30) == Status.HARD_BLOCKED
    assert vb.is_blocked(9, 1e9)


def test_rdt_flag_uses_max_values():
    vb = ValidationBlocking()
    for i in range(5):
        assert vb.on_detection(4, 0.8, True, 120.0 + 30 * i) == Status.QUARANTINE
    assert vb.states[4].qp_total == pytest.approx(5 * 180.0)
    assert vb.on_detection(4, 0.8, True, 270.0) == Status.SOFT_BLOCKED


def test_quarantine_release():
    vb = ValidationBlocking()
    vb.on_detection(2, 0.55, False, 120.0)
    qp = quarantine_period(0.55)
    assert vb.is_quarantined(2, 120.0 + qp - 1)
    assert vb.status(2, 120.0 + qp) == Status.NORMAL
    assert vb.states[2].dc == 0
