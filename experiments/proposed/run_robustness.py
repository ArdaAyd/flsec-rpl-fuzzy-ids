"""Robustness of the paper's and the tuned membership functions to packet loss.

Usage: python experiments/proposed/run_robustness.py [--mfs results/tuned_mfs.json]
"""

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flsec.experiments import grid, run_grid  # noqa: E402
from flsec.optimize import load_mfs  # noqa: E402
from flsec.plotting import plot_loss_curves  # noqa: E402

LOSSES = (0.0, 0.1, 0.2, 0.3)
METRICS = ["accuracy", "f1", "precision", "recall", "fpr", "ftd_mean", "time_to_block_mean", "node_legit_blocked"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mfs", default=str(ROOT / "results" / "tuned_mfs.json"))
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--processes", type=int, default=None)
    args = parser.parse_args()

    methods = {"FLSec-RPL": ("flsec", {}), "FLSec-RPL (tuned MFs)": ("flsec", {"input_mfs": load_mfs(args.mfs)})}
    items = [item for loss in LOSSES
             for item in grid(methods, n_sensors=(16, 32), pans=(0.1, 0.3, 0.5), aris=(1.0, 4.0, 8.0),
                              seeds=range(args.seeds), p_loss=loss)]
    start = time.time()
    runs = run_grid(items, args.processes)

    tables, figures = ROOT / "results" / "tables", ROOT / "results" / "figures"
    runs.drop(columns=["detector_options"]).to_csv(tables / "robustness_runs.csv", index=False)
    summary = runs.groupby(["n_sensors", "mobile", "method", "p_loss"])[METRICS].mean().reset_index()
    summary.to_csv(tables / "robustness_summary.csv", index=False)
    (tables / "robustness_summary.md").write_text(summary.round(4).to_markdown(index=False) + "\n")
    for metric in ("f1", "ftd_mean"):
        plot_loss_curves(summary, metric, figures / f"fig_robustness_{metric}.png")

    print(summary[["n_sensors", "mobile", "method", "p_loss", "f1", "fpr", "recall", "ftd_mean"]]
          .round(3).to_string(index=False))
    print(f"{len(runs)} runs in {time.time() - start:.0f} s")


if __name__ == "__main__":
    main()
