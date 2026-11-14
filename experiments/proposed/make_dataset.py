"""Builds the observation-window dataset used to tune the membership functions.

FLSec-RPL runs in passive mode (it scores neighbors but never quarantines or blocks them), so the
windows are not biased by the paper's membership functions. Seeds 100-102 form the training split
and 103-104 the validation split; seeds 0-4 stay reserved for the closed-loop test.

Usage: python experiments/proposed/make_dataset.py [--cap 2000]
"""

import argparse
import itertools
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flsec import config as C  # noqa: E402
from flsec.experiments import run_windows  # noqa: E402
from flsec.simulator import SimConfig  # noqa: E402

TRAIN_SEEDS = (100, 101, 102)
VAL_SEEDS = (103, 104)
CELL = ["n_sensors", "mobile", "pan", "ari", "split", "attacker"]


def configs(seeds):
    for n, mobile, pan, ari, seed in itertools.product((16, 32), (False, True), C.PAN_LEVELS, C.ARI_LEVELS_S, seeds):
        yield SimConfig(n_sensors=n, pan=pan, ari=ari, mobile=mobile, seed=seed, detector="flsec",
                        detector_options={"passive": True}, record_windows=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cap", type=int, default=2000,
                        help="max windows per (scenario, split, class) cell; 0 keeps everything")
    parser.add_argument("--processes", type=int, default=None)
    args = parser.parse_args()

    start = time.time()
    df = run_windows(configs(TRAIN_SEEDS + VAL_SEEDS), args.processes)
    df["split"] = df["seed"].map(lambda s: "train" if s in TRAIN_SEEDS else "val")
    total = len(df)
    df["weight"] = 1.0
    if args.cap:
        df["cell_size"] = df.groupby(CELL)["t"].transform("size")
        df = df.sample(frac=1.0, random_state=0)
        df = df[df.groupby(CELL).cumcount() < args.cap].copy()
        kept = df.groupby(CELL)["t"].transform("size")
        df["weight"] = df.pop("cell_size") / kept  # restores the natural class/scenario mix
    df = df.sort_values(["split", "n_sensors", "mobile", "pan", "ari", "seed", "t", "detector", "neighbor"])

    out = ROOT / "data" / "windows.csv.gz"
    df.to_csv(out, index=False, float_format="%.4f", compression="gzip")
    print(f"{total} windows collected, {len(df)} kept -> {out.relative_to(ROOT)} "
          f"({out.stat().st_size / 1e6:.1f} MB) in {time.time() - start:.0f} s")
    print(df.groupby(["split", "mobile", "attacker"]).size().unstack())


if __name__ == "__main__":
    main()
