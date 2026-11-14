import numpy as np
import pytest

from flsec import config
from flsec.fuzzy import build_paper_fls
from flsec.optimize import _set_data, decode, encode, negative_score, objective_terms, omega, paper_vector


def test_paper_vector_decodes_to_paper_mfs():
    mfs = decode(paper_vector())
    for name in config.INPUT_NAMES:
        for term in config.TERMS:
            assert mfs[name][term] == pytest.approx(config.PAPER_INPUT_MFS[name][term])


def test_fast_omega_matches_fls():
    X = np.random.default_rng(0).uniform(0, 30, size=(500, 3))
    mfs = decode(np.random.default_rng(1).uniform(0, 30, 24))
    assert omega(X, mfs) == pytest.approx(build_paper_fls(input_mfs=mfs).infer(X))


def test_decoded_sets_are_ordered_and_cover_the_universe():
    grid = np.linspace(0, 30, 601)
    for seed in range(50):
        mfs = decode(np.random.default_rng(seed).uniform(0, 30, 24))
        for sets in mfs.values():
            for a, b, c, d in sets.values():
                assert a <= b <= c <= d
            low, mid, high = sets["L"], sets["M"], sets["H"]
            assert low[2] <= mid[1] and low[3] <= mid[2]  # Low's core and support end before Medium's core
            assert mid[2] <= high[1]  # High's core starts after Medium's core
        for j in range(3):
            Xj = np.zeros((len(grid), 3))
            Xj[:, j] = grid
            fls = build_paper_fls(input_mfs=mfs)
            assert fls.firing_strengths(Xj).sum(axis=1).min() > 0


def test_objective_on_toy_data():
    # attackers fire rule 1 only (omega = 5/6), legitimate windows rules 25/27 only (omega = 1/6)
    X = np.array([[30, 1, 0], [30, 1, 0], [1, 30, 0], [1, 30, 20]], dtype=float)
    y = np.array([True, True, False, False])
    terms = objective_terms(paper_vector(), X, y, np.ones(4))
    assert terms["f1"] == pytest.approx(1.0)
    assert terms["separation"] == pytest.approx(2 / 3)
    assert terms["distance"] == pytest.approx(0.0)
    _set_data(X, y, np.ones(4))
    assert negative_score(paper_vector()) == pytest.approx(-(1.0 + 0.1 * 2 / 3))


def test_encode_inverts_decode():
    x = np.random.default_rng(3).uniform(0, 30, 24)
    mfs = decode(x)
    assert decode(encode(mfs)) == mfs
