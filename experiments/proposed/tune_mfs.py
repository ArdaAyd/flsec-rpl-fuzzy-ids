"""Tunes the input membership functions on the training windows.

Writes the tuned sets, the convergence history, window-level metrics (paper vs. tuned) on the
train and validation splits and a comparison figure.

Usage: python experiments/proposed/tune_mfs.py [--subset all|static|mobile] [--maxiter 150]
"""

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flsec import config  # noqa: E402
from flsec.optimize import aggregate, decode, objective_terms, omega, save_mfs, tune, window_metrics  # noqa: E402
from flsec.plotting import plot_mf_comparison  # noqa: E402

INPUTS = ["dio_counter", "dti", "stia"]


def evaluate(df, mfs_by_name):
    rows = []
    for split in ("train", "val"):
        for network in ("static", "mobile", "all"):
            part = df[df["split"] == split]
            if network != "all":
                part = part[part["mobile"] == (network == "mobile")]
            X, y = part[INPUTS].to_numpy(float), part["attacker"].to_numpy(bool)
            for name, mfs in mfs_by_name.items():
                om = omega(X, mfs)
                pred = om > config.FUZZY_FILTER_DELTA
                m = window_metrics(y, pred)
                m["f1_natural"] = window_metrics(y, pred, part["weight"])["f1"]
                m["omega_attacker"], m["omega_legit"] = om[y].mean(), om[~y].mean()
                rows.append({"split": split, "network": network, "mfs": name, **m})
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subset", choices=["all", "static", "mobile"], default="all")
    parser.add_argument("--maxiter", type=int, default=150)
    parser.add_argument("--popsize", type=int, default=15)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--processes", type=int, default=None)
    args = parser.parse_args()
    tag = "" if args.subset == "all" else f"_{args.subset}"

    df = pd.read_csv(ROOT / "data" / "windows.csv.gz")
    train = df[df["split"] == "train"]
    if args.subset != "all":
        train = train[train["mobile"] == (args.subset == "mobile")]
    X, y, w = aggregate(train)

    start = time.time()
    result, history = tune(X, y, w, maxiter=args.maxiter, popsize=args.popsize, seed=args.seed,
                           processes=args.processes)
    tuned = decode(result.x)
    elapsed = time.time() - start

    results, tables = ROOT / "results", ROOT / "results" / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    terms = objective_terms(result.x, X, y, w)
    save_mfs(tuned, results / f"tuned_mfs{tag}.json", subset=args.subset, train_objective=terms,
             generations=len(history), maxiter=args.maxiter, popsize=args.popsize, seed=args.seed,
             vector=[round(float(v), 4) for v in result.x])
    hist = pd.DataFrame(history)
    hist.insert(0, "generation", range(1, len(hist) + 1))
    hist.to_csv(tables / f"tuning_history{tag}.csv", index=False)

    metrics = evaluate(df, {"paper": config.PAPER_INPUT_MFS, "tuned": tuned})
    metrics.to_csv(tables / f"window_metrics{tag}.csv", index=False)
    (tables / f"window_metrics{tag}.md").write_text(metrics.round(4).to_markdown(index=False) + "\n")
    plot_mf_comparison(config.PAPER_INPUT_MFS, tuned, results / "figures" / f"fig_tuned_mfs{tag}.png")

    print(f"{len(X)} unique training windows, {len(history)} generations, {elapsed:.0f} s")
    for name, sets in tuned.items():
        print(name, {t: tuple(round(v, 2) for v in p) for t, p in sets.items()})
    print(metrics.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
