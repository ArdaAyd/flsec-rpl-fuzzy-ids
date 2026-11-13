"""Reproduces the detection experiments of the paper (accuracy, F1 and FTD vs. PAN and ARI).

Usage: python experiments/baseline/run_reproduction.py [--sensors 16 32] [--seeds 5]
"""

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flsec.experiments import METHODS, grid, run_grid, summarize_runs  # noqa: E402
from flsec.plotting import plot_metric_grid  # noqa: E402

METRICS = (("accuracy", "accuracy", 100), ("f1", "f1", 100), ("ftd_s", "ftd_mean", 1))


def compare_with_paper(summary, paper):
    rows = []
    for (n, mobile, method), cell in summary.groupby(["n_sensors", "mobile", "method"]):
        row = {"sensors": n, "network": "mobile" if mobile else "static", "method": method}
        for metric, column, scale in METRICS:
            values = cell[column].dropna() * scale
            ours = f"{values.min():.0f}-{values.max():.0f}" if len(values) else "no detection"
            ref = paper[(paper.n_sensors == n) & (paper.mobile == mobile) & (paper.method == method)
                        & (paper.metric == metric)]
            row[f"{metric} (ours)"] = ours
            row[f"{metric} (paper)"] = f"{ref['min'].iloc[0]}-{ref['max'].iloc[0]}" if len(ref) else ""
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sensors", type=int, nargs="+", default=[16, 32])
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--processes", type=int, default=None)
    args = parser.parse_args()

    start = time.time()
    runs = run_grid(grid(METHODS, n_sensors=args.sensors, seeds=range(args.seeds)), args.processes)
    tables, figures = ROOT / "results" / "tables", ROOT / "results" / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    runs.to_csv(tables / "reproduction_runs.csv", index=False)
    summary = summarize_runs(runs)
    summary.to_csv(tables / "reproduction_summary.csv", index=False)

    paper = pd.read_csv(ROOT / "data" / "paper_reported_ranges.csv")
    comparison = compare_with_paper(summary, paper)
    comparison.to_csv(tables / "reproduction_vs_paper.csv", index=False)
    (tables / "reproduction_vs_paper.md").write_text(comparison.to_markdown(index=False) + "\n")

    for n in args.sensors:
        cell = summary[summary["n_sensors"] == n]
        for metric in ("accuracy", "f1", "ftd_mean"):
            plot_metric_grid(cell, metric, figures / f"fig_repro_{metric}_n{n}.png")

    print(comparison.to_string(index=False))
    print(f"{len(runs)} runs in {time.time() - start:.0f} s")


if __name__ == "__main__":
    main()
