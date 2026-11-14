"""Closed-loop comparison of the paper's and the tuned membership functions on the test seeds.

Both variants run on the same networks, attackers and mobility traces (seeds 0-4), so the
comparison is paired; differences are tested with the Wilcoxon signed-rank test.

Usage: python experiments/proposed/evaluate_tuned.py [--mfs results/tuned_mfs.json] [--tag ""]
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flsec.experiments import grid, run_grid, summarize_runs  # noqa: E402
from flsec.optimize import load_mfs  # noqa: E402
from flsec.plotting import TUNED_COLORS, TUNED_STYLES, plot_metric_grid  # noqa: E402

PAPER, TUNED = "FLSec-RPL", "FLSec-RPL (tuned MFs)"
METRICS = ["accuracy", "f1", "precision", "recall", "fpr", "ftd_mean", "time_to_block_mean",
           "node_legit_blocked", "attack_dio_processed_per_node"]
CELL = ["n_sensors", "mobile", "pan", "ari", "seed"]


def paired_tests(runs):
    rows = []
    wide = runs.pivot_table(index=CELL, columns="method", values=METRICS)
    for (n, mobile), part in wide.groupby(level=["n_sensors", "mobile"]):
        for metric in METRICS:
            a, b = part[(metric, PAPER)], part[(metric, TUNED)]
            ok = a.notna() & b.notna()
            diff = (b - a)[ok]
            p = wilcoxon(b[ok], a[ok]).pvalue if (diff != 0).any() else 1.0
            rows.append({"sensors": n, "network": "mobile" if mobile else "static", "metric": metric,
                         "paper": a[ok].mean(), "tuned": b[ok].mean(), "difference": diff.mean(),
                         "tuned_better_share": float(np.mean(diff > 0)) if metric not in (
                             "fpr", "ftd_mean", "time_to_block_mean", "node_legit_blocked",
                             "attack_dio_processed_per_node") else float(np.mean(diff < 0)),
                         "p_value": p, "pairs": int(ok.sum())})
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mfs", default=str(ROOT / "results" / "tuned_mfs.json"))
    parser.add_argument("--tag", default="")
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--processes", type=int, default=None)
    args = parser.parse_args()

    tuned = load_mfs(args.mfs)
    methods = {PAPER: ("flsec", {}), TUNED: ("flsec", {"input_mfs": tuned})}
    start = time.time()
    runs = run_grid(grid(methods, n_sensors=(16, 32), seeds=range(args.seeds)), args.processes)

    tables, figures = ROOT / "results" / "tables", ROOT / "results" / "figures"
    runs.drop(columns=["detector_options"]).to_csv(tables / f"tuned_runs{args.tag}.csv", index=False)
    summary = summarize_runs(runs)
    summary.to_csv(tables / f"tuned_summary{args.tag}.csv", index=False)
    tests = paired_tests(runs)
    tests.to_csv(tables / f"tuned_vs_paper{args.tag}.csv", index=False)
    (tables / f"tuned_vs_paper{args.tag}.md").write_text(tests.round(4).to_markdown(index=False) + "\n")

    for n in (16, 32):
        cell = summary[summary["n_sensors"] == n]
        for metric in ("accuracy", "f1", "ftd_mean"):
            plot_metric_grid(cell, metric, figures / f"fig_tuned_{metric}_n{n}{args.tag}.png",
                             colors=TUNED_COLORS, styles=TUNED_STYLES)

    print(tests[tests["metric"].isin(["accuracy", "f1", "fpr", "recall", "ftd_mean", "node_legit_blocked"])]
          .round(4).to_string(index=False))
    print(f"{len(runs)} runs in {time.time() - start:.0f} s")


if __name__ == "__main__":
    main()
