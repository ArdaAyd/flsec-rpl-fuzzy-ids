"""Ablation of FLSec-RPL's components and sensitivity to our modelling choices.

Every variant runs on the same networks, attackers and mobility traces as the full method
(seeds 0-4) and is compared with it pairwise.

Usage: python experiments/baseline/run_ablation.py
"""

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flsec.experiments import grid, paired_comparison, run_grid  # noqa: E402
from flsec.plotting import plot_variants  # noqa: E402

VARIANTS = {
    "FLSec-RPL": {},
    "no STIA": {"use_stia": False},
    "no RDT flag": {"use_rdt": False},
    "no validation": {"validation": False},
    "fixed MD = 3": {"adaptive_md": False, "fixed_md": 3.0},
    "STIA within window": {"stia_mode": "within"},
    "STIA persistent": {"stia_mode": "persistent"},
    "Mamdani COG": {"defuzz": "cog"},
}
METRICS = ["accuracy", "f1", "precision", "recall", "fpr", "ftd_mean", "time_to_block_mean",
           "node_legit_blocked", "attack_dio_processed_per_node"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--processes", type=int, default=None)
    args = parser.parse_args()

    start = time.time()
    methods = {name: ("flsec", opts) for name, opts in VARIANTS.items()}
    runs = run_grid(grid(methods, n_sensors=(16, 32), seeds=range(args.seeds)), args.processes)

    tables, figures = ROOT / "results" / "tables", ROOT / "results" / "figures"
    runs.drop(columns=["detector_options"]).to_csv(tables / "ablation_runs.csv", index=False)
    summary = runs.groupby(["n_sensors", "mobile", "method"])[METRICS].mean().reset_index()
    summary.to_csv(tables / "ablation_summary.csv", index=False)
    comparison = paired_comparison(runs, "FLSec-RPL", METRICS)
    comparison.to_csv(tables / "ablation_vs_full.csv", index=False)
    (tables / "ablation_vs_full.md").write_text(comparison.round(4).to_markdown(index=False) + "\n")

    order = list(VARIANTS)
    for metric in ("f1", "time_to_block_mean", "node_legit_blocked"):
        plot_variants(summary, metric, figures / f"fig_ablation_{metric}.png", order)

    print(summary[["n_sensors", "mobile", "method", "f1", "fpr", "recall", "ftd_mean", "time_to_block_mean",
                   "node_legit_blocked"]].round(3).to_string(index=False))
    print(f"{len(runs)} runs in {time.time() - start:.0f} s")


if __name__ == "__main__":
    main()
