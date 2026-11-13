from itertools import product

import numpy as np
import pytest

from flsec import config
from flsec.fuzzy import build_paper_fls, trapmf


def test_trapezoid_breakpoints():
    low, mid, high = (config.PAPER_INPUT_MFS["dio_counter"][t] for t in config.TERMS)
    assert trapmf(0, *low) == 1 and trapmf(2, *low) == 1
    assert trapmf(3.5, *low) == pytest.approx(0.5)
    assert trapmf(5, *low) == 0
    assert trapmf(1, *mid) == 0 and trapmf(3, *mid) == pytest.approx(0.5)
    assert trapmf(6, *mid) == 1 and trapmf(9, *mid) == pytest.approx(0.5)
    assert trapmf(11, *mid) == 0
    assert trapmf(9, *high) == pytest.approx(0.5) and trapmf(30, *high) == 1


def test_inputs_are_clipped_to_universe():
    mus = build_paper_fls().fuzzify([[45.0, -3.0, 100.0]])
    assert mus[0][0].tolist() == [0.0, 0.0, 1.0]
    assert mus[1][0].tolist() == [1.0, 0.0, 0.0]
    assert mus[2][0].tolist() == [0.0, 0.0, 1.0]


def test_output_centroids():
    assert build_paper_fls().output_centroids == pytest.approx([1 / 6, 1 / 2, 5 / 6])


def test_rule_base_is_complete():
    antecedents = [rule[:3] for rule in config.PAPER_RULES]
    assert len(antecedents) == 27
    assert set(antecedents) == set(product(config.TERMS, repeat=3))


def test_single_rule_extremes():
    fls = build_paper_fls()
    assert fls.infer([[30, 0, 0]])[0] == pytest.approx(5 / 6)  # rule 1 only
    assert fls.infer([[0, 30, 30]])[0] == pytest.approx(1 / 6)  # rule 27 only


def test_hand_calculation_ari_8s():
    # 4 DIOs, DTI = 8 s, STIA = 0: rules 10, 13, 19 and 22 fire.
    strengths = {10: 2 / 7, 13: 5 / 7, 19: 2 / 7, 22: 1 / 3}
    centroid = {10: 5 / 6, 13: 0.5, 19: 0.5, 22: 0.5}
    expected = sum(strengths[r] * centroid[r] for r in strengths) / sum(strengths.values())

    trace = build_paper_fls().explain([4, 8, 0])
    assert {r["rule"]: r["strength"] for r in trace["fired_rules"]} == pytest.approx(strengths)
    assert trace["omega"] == pytest.approx(expected)
    assert expected == pytest.approx(0.5588, abs=1e-4)


def test_batch_equals_single():
    X = np.random.default_rng(0).uniform(0, 30, size=(200, 3))
    fls = build_paper_fls()
    batch = fls.infer(X)
    assert batch == pytest.approx([fls.infer(row[None])[0] for row in X])
    assert np.all((batch >= 1 / 6 - 1e-12) & (batch <= 5 / 6 + 1e-12))


def test_cog_matches_scikit_fuzzy():
    skfuzzy = pytest.importorskip("skfuzzy")
    from skfuzzy import control as ctrl

    grid = np.linspace(0, 30, 3001)
    ants = {name: ctrl.Antecedent(grid, name) for name in config.INPUT_NAMES}
    for name, ant in ants.items():
        for term, params in config.PAPER_INPUT_MFS[name].items():
            ant[term] = skfuzzy.trapmf(grid, list(params))
    out = ctrl.Consequent(np.linspace(0, 1, 1001), "omega", defuzzify_method="centroid")
    for term, params in config.PAPER_OUTPUT_MFS.items():
        out[term] = skfuzzy.trimf(out.universe, list(params))
    rules = [ctrl.Rule(ants["dio_counter"][a] & ants["dti"][b] & ants["stia"][c], out[o])
             for a, b, c, o in config.PAPER_RULES]
    sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))

    ours = build_paper_fls(defuzz="cog")
    for x in np.random.default_rng(1).uniform(0, 30, size=(25, 3)):
        for name, value in zip(config.INPUT_NAMES, x):
            sim.input[name] = value
        sim.compute()
        assert ours.infer(x[None])[0] == pytest.approx(sim.output["omega"], abs=2e-3)
