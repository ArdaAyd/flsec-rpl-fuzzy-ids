"""Membership-function tuning with differential evolution.

The rule base, the output sets and the defuzzifier stay as in the paper; only the breakpoints of
the nine input sets are searched. Per input there are 8 free numbers: (c, d) of Low, (a, b, c, d)
of Medium and (a, b) of High, so a candidate is a vector of 24 values in [0, 30].
"""

import functools
import json
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.optimize import differential_evolution

from . import config
from .fuzzy import trapmf

HI = config.INPUT_UNIVERSE[1]
GAP = 0.05  # minimum overlap between neighboring sets

_ANTECEDENTS = np.array([[config.TERMS.index(t) for t in rule[:3]] for rule in config.PAPER_RULES])
_CENTROIDS = np.array([{"normal": 1 / 6, "quarantine": 1 / 2, "malicious": 5 / 6}[rule[3]]
                       for rule in config.PAPER_RULES])


def paper_vector():
    v = []
    for name in config.INPUT_NAMES:
        mf = config.PAPER_INPUT_MFS[name]
        v += [mf["L"][2], mf["L"][3], *mf["M"], mf["H"][0], mf["H"][1]]
    return np.array(v, dtype=float)


def decode(x):
    """Maps a 24-vector to trapezoids that keep their linguistic order.

    Constraints: breakpoints are ordered within each set; the cores are ordered Low < Medium < High
    (Low ends before Medium's core ends, High starts after Medium's core starts); neighboring sets
    overlap, so no input value is left without membership. The paper's sets satisfy all of them.
    """
    x = np.clip(np.asarray(x, dtype=float), 0.0, HI)
    mfs = {}
    for k, name in enumerate(config.INPUT_NAMES):
        v = x[8 * k:8 * k + 8]
        lc, ld = np.sort(v[0:2])
        ma, mb, mc, md = np.sort(v[2:6])
        ha, hb = np.sort(v[6:8])
        lc = min(lc, mb)
        ld = min(max(ld, lc), mc)
        ha = max(ha, mb)
        hb = max(hb, mc, ha)
        ma = min(ma, ld - GAP)  # Medium starts before Low ends
        ha = min(ha, md - GAP)  # High starts before Medium ends
        hb = max(hb, ha)
        mfs[name] = {"L": (0.0, 0.0, float(lc), float(ld)),
                     "M": (float(ma), float(mb), float(mc), float(md)),
                     "H": (float(ha), float(hb), HI, HI)}
    return mfs


def omega(X, mfs):
    """Aggressive weight (Eq. 8) for rows of X = [dio_counter, dti, stia]; same as MamdaniFLS."""
    X = np.asarray(X, dtype=float)
    mus = []
    for j, name in enumerate(config.INPUT_NAMES):
        xj = np.clip(X[:, j], *config.INPUT_UNIVERSE)
        mus.append(np.stack([trapmf(xj, *mfs[name][t]) for t in config.TERMS], axis=1))
    w = np.minimum(np.minimum(mus[0][:, _ANTECEDENTS[:, 0]], mus[1][:, _ANTECEDENTS[:, 1]]),
                   mus[2][:, _ANTECEDENTS[:, 2]])
    den = w.sum(axis=1)
    return np.divide(w @ _CENTROIDS, den, out=np.full(len(X), 0.5), where=den > 0)


def confusion(y, pred, w=None):
    w = np.ones(len(y)) if w is None else np.asarray(w, dtype=float)
    y, pred = np.asarray(y, dtype=bool), np.asarray(pred, dtype=bool)
    return w[y & pred].sum(), w[~y & pred].sum(), w[~y & ~pred].sum(), w[y & ~pred].sum()


def window_metrics(y, pred, w=None):
    tp, fp, tn, fn = confusion(y, pred, w)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"recall": recall, "fpr": fp / (fp + tn) if fp + tn else 0.0, "precision": precision,
            "f1": 2 * tp / (2 * tp + fp + fn) if tp else 0.0}


def aggregate(df, resolution=0.05):
    """Merges windows with the same (rounded) inputs and label; returns X, y, weights."""
    key = df.assign(
        dio_counter=df["dio_counter"].clip(upper=HI),
        dti=(df["dti"].clip(upper=HI) / resolution).round() * resolution,
        stia=(df["stia"].clip(upper=HI) / resolution).round() * resolution,
    )
    g = key.groupby(["dio_counter", "dti", "stia", "attacker"], as_index=False).size()
    return g[["dio_counter", "dti", "stia"]].to_numpy(float), g["attacker"].to_numpy(bool), g["size"].to_numpy(float)


def encode(mfs):
    """Inverse of decode for already valid sets (same order as paper_vector)."""
    v = []
    for name in config.INPUT_NAMES:
        s = mfs[name]
        v += [s["L"][2], s["L"][3], *s["M"], s["H"][0], s["H"][1]]
    return np.array(v, dtype=float)


# Objective = window F1 + SEPARATION_WEIGHT * (mean omega of attackers - mean omega of legitimate
# windows) - DISTANCE_WEIGHT * mean |breakpoint shift| / 30. The F1 term dominates; the separation
# term favors confident decisions (lower MD in phase III); the distance term keeps breakpoints that
# do not change the F1 at their expert values.
SEPARATION_WEIGHT = 0.1
DISTANCE_WEIGHT = 0.02
_PAPER = None


def objective_terms(x, X, y, w):
    global _PAPER
    if _PAPER is None:
        _PAPER = paper_vector()
    mfs = decode(x)
    om = omega(X, mfs)
    tp, fp, _, fn = confusion(y, om > config.FUZZY_FILTER_DELTA, w)
    f1 = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
    separation = np.average(om[y], weights=w[y]) - np.average(om[~y], weights=w[~y])
    distance = float(np.mean(np.abs(encode(mfs) - _PAPER))) / HI
    score = f1 + SEPARATION_WEIGHT * separation - DISTANCE_WEIGHT * distance
    return {"score": score, "f1": f1, "separation": separation, "distance": distance}


# Data shared with worker processes (set once by the pool initializer).
_DATA = None


def _set_data(X, y, w):
    global _DATA
    _DATA = (X, y, w)


def negative_score(x):
    return -objective_terms(x, *_DATA)["score"]


def tune(X, y, w, maxiter=150, popsize=15, seed=0, processes=None):
    """Differential evolution over the 24 breakpoints, started with the paper's MFs in the population."""
    history = []

    def record(intermediate_result):
        history.append(objective_terms(intermediate_result.x, X, y, w))

    _set_data(X, y, w)
    with ProcessPoolExecutor(max_workers=processes, initializer=_set_data, initargs=(X, y, w)) as pool:
        result = differential_evolution(
            negative_score, bounds=[(0.0, HI)] * 24, x0=paper_vector(), popsize=popsize, maxiter=maxiter,
            mutation=(0.5, 1.0), recombination=0.7, tol=0.0, polish=False, seed=seed,
            updating="deferred", workers=functools.partial(pool.map, chunksize=16), callback=record)
    return result, history


def save_mfs(mfs, path, **meta):
    with open(path, "w") as f:
        json.dump({"input_mfs": mfs, **meta}, f, indent=2)


def load_mfs(path):
    with open(path) as f:
        data = json.load(f)
    return {name: {t: tuple(v) for t, v in sets.items()} for name, sets in data["input_mfs"].items()}
