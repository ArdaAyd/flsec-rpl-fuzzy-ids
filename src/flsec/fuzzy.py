"""Type-1 Mamdani fuzzy inference system (phase II)."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from . import config


def trapmf(x, a, b, c, d):
    """Trapezoidal membership function (Eq. 6). a == b or c == d gives a shoulder."""
    x = np.asarray(x, dtype=float)
    rising = np.ones_like(x) if b == a else (x - a) / (b - a)
    falling = np.ones_like(x) if d == c else (d - x) / (d - c)
    mu = np.clip(np.minimum(rising, falling), 0.0, 1.0)
    if b == a:
        mu = np.where(x < a, 0.0, mu)
    if d == c:
        mu = np.where(x > d, 0.0, mu)
    return mu


def trimf(x, a, b, c):
    return trapmf(x, a, b, b, c)


def gaussmf(x, mean, sigma):
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * ((x - mean) / sigma) ** 2)


@dataclass(frozen=True)
class FuzzySet:
    """kind: "trap" (a, b, c, d), "tri" (a, b, c), "gauss" / "gauss_left" / "gauss_right" (mean, sigma)."""

    name: str
    kind: str
    params: tuple

    def __call__(self, x):
        if self.kind == "trap":
            return trapmf(x, *self.params)
        if self.kind == "tri":
            return trimf(x, *self.params)
        x = np.asarray(x, dtype=float)
        mean, sigma = self.params
        if self.kind == "gauss":
            return gaussmf(x, mean, sigma)
        if self.kind == "gauss_left":
            return np.where(x <= mean, 1.0, gaussmf(x, mean, sigma))
        if self.kind == "gauss_right":
            return np.where(x >= mean, 1.0, gaussmf(x, mean, sigma))
        raise ValueError(f"unknown membership function: {self.kind}")

    def centroid(self, universe, resolution=200_001):
        if self.kind == "tri":
            return float(sum(self.params) / 3.0)
        y = np.linspace(universe[0], universe[1], resolution)
        mu = self(y)
        return float((y * mu).sum() / mu.sum())


@dataclass(frozen=True)
class LinguisticVariable:
    name: str
    universe: tuple
    sets: Mapping[str, FuzzySet]

    @property
    def terms(self):
        return tuple(self.sets)

    def memberships(self, x):
        """Membership degrees, shape (n, n_terms). Inputs are clipped to the universe."""
        x = np.clip(np.asarray(x, dtype=float).reshape(-1), *self.universe)
        return np.stack([s(x) for s in self.sets.values()], axis=1)


@dataclass(frozen=True)
class Rule:
    antecedent: tuple
    consequent: str


class MamdaniFLS:
    """Mamdani FIS with min t-norm (Eq. 7).

    defuzz:
        "paper"  Eq. 8, centroids of the output sets weighted by rule strength
        "cog"    centroid of the max-aggregated, min-clipped output sets
        "mom"    mean of maximum of the aggregated output
    """

    DEFUZZIFIERS = ("paper", "cog", "mom")

    def __init__(self, inputs: Sequence[LinguisticVariable], output: LinguisticVariable,
                 rules: Sequence[Rule], defuzz="paper", resolution=1001):
        if defuzz not in self.DEFUZZIFIERS:
            raise ValueError(f"defuzz must be one of {self.DEFUZZIFIERS}")
        self.inputs = tuple(inputs)
        self.output = output
        self.rules = tuple(rules)
        self.defuzz = defuzz
        self._antecedent_idx = np.array(
            [[var.terms.index(term) for var, term in zip(self.inputs, r.antecedent)] for r in self.rules]
        )
        self._consequent_idx = np.array([output.terms.index(r.consequent) for r in self.rules])
        self.output_centroids = np.array([s.centroid(output.universe) for s in output.sets.values()])
        self._y = np.linspace(output.universe[0], output.universe[1], resolution)
        self._output_mu = np.stack([s(self._y) for s in output.sets.values()])

    def fuzzify(self, X):
        X = np.atleast_2d(np.asarray(X, dtype=float))
        if X.shape[1] != len(self.inputs):
            raise ValueError(f"expected {len(self.inputs)} input columns, got {X.shape[1]}")
        return [var.memberships(X[:, j]) for j, var in enumerate(self.inputs)]

    def firing_strengths(self, X):
        """Rule strengths, shape (n, n_rules)."""
        mus = self.fuzzify(X)
        w = mus[0][:, self._antecedent_idx[:, 0]]
        for j in range(1, len(mus)):
            w = np.minimum(w, mus[j][:, self._antecedent_idx[:, j]])
        return w

    def output_levels(self, w):
        """Clip level of each output set (max strength of the rules that conclude it)."""
        levels = np.zeros((w.shape[0], len(self.output.sets)))
        for k in range(levels.shape[1]):
            mask = self._consequent_idx == k
            if mask.any():
                levels[:, k] = w[:, mask].max(axis=1)
        return levels

    def defuzzify(self, w):
        if self.defuzz == "paper":
            num = w @ self.output_centroids[self._consequent_idx]
            den = w.sum(axis=1)
            return np.divide(num, den, out=np.full(num.shape, np.nan), where=den > 0)

        levels = self.output_levels(w)
        out = np.full(w.shape[0], np.nan)
        chunk = 2048
        for start in range(0, w.shape[0], chunk):
            agg = np.max(np.minimum(levels[start:start + chunk, :, None], self._output_mu[None]), axis=1)
            if self.defuzz == "cog":
                area = agg.sum(axis=1)
                out[start:start + chunk] = np.divide(agg @ self._y, area, out=np.full(area.shape, np.nan),
                                                     where=area > 0)
            else:
                peak = agg.max(axis=1, keepdims=True)
                at_peak = np.isclose(agg, peak) & (peak > 0)
                count = at_peak.sum(axis=1)
                out[start:start + chunk] = np.divide(at_peak @ self._y, count, out=np.full(count.shape, np.nan),
                                                     where=count > 0)
        return out

    def infer(self, X):
        return self.defuzzify(self.firing_strengths(X))

    __call__ = infer

    def explain(self, x):
        """Memberships, fired rules and output for a single input vector."""
        x = np.asarray(x, dtype=float).reshape(1, -1)
        mus = self.fuzzify(x)
        w = self.firing_strengths(x)[0]
        fired = [{"rule": i + 1, "if": r.antecedent, "then": r.consequent, "strength": float(w[i])}
                 for i, r in enumerate(self.rules) if w[i] > 0]
        fired.sort(key=lambda item: -item["strength"])
        return {
            "inputs": {var.name: float(np.clip(x[0, j], *var.universe)) for j, var in enumerate(self.inputs)},
            "memberships": {var.name: dict(zip(var.terms, mus[j][0].tolist())) for j, var in enumerate(self.inputs)},
            "fired_rules": fired,
            "output_levels": dict(zip(self.output.terms, self.output_levels(w[None])[0].tolist())),
            "omega": float(self.defuzzify(w[None])[0]),
        }


def make_input_variables(input_mfs=None, kind="trap"):
    input_mfs = config.PAPER_INPUT_MFS if input_mfs is None else input_mfs
    return [
        LinguisticVariable(name, config.INPUT_UNIVERSE,
                           {t: FuzzySet(t, kind, tuple(float(p) for p in input_mfs[name][t])) for t in config.TERMS})
        for name in config.INPUT_NAMES
    ]


def make_output_variable():
    return LinguisticVariable(config.OUTPUT_NAME, config.OUTPUT_UNIVERSE,
                              {t: FuzzySet(t, "tri", config.PAPER_OUTPUT_MFS[t]) for t in config.OUTPUT_TERMS})


def paper_rules():
    return [Rule((dio, dti, stia), out) for dio, dti, stia, out in config.PAPER_RULES]


def build_paper_fls(defuzz="paper", input_mfs=None, inputs=None):
    """FLSec-RPL's fuzzy system; input_mfs or inputs replace the paper's input sets."""
    if inputs is None:
        inputs = make_input_variables(input_mfs)
    return MamdaniFLS(inputs, make_output_variable(), paper_rules(), defuzz=defuzz)
