"""Parallel execution of simulation grids."""

import itertools
import os
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

from . import config as C
from .simulator import SimConfig, run_simulation

METHODS = {
    "FLSec-RPL": ("flsec", {}),
    "CoSec-RPL": ("cosec", {}),
    "Anomaly-Based IDS": ("anomaly", {}),
    # sensitivity variant: the original sigma = 0.5 s never fires for replay intervals >= 1 s
    "CoSec-RPL (sigma = 10 s)": ("cosec", {"sigma": 10.0}),
}


def grid(methods, n_sensors=(16,), mobility=(False, True), pans=C.PAN_LEVELS, aris=C.ARI_LEVELS_S,
         seeds=range(5), **overrides):
    for (name, (kind, opts)), n, mobile, pan, ari, seed in itertools.product(
            methods.items(), n_sensors, mobility, pans, aris, seeds):
        cfg = SimConfig(n_sensors=n, pan=pan, ari=ari, mobile=mobile, detector=kind,
                        detector_options=dict(opts), seed=seed, **overrides)
        yield name, cfg


def _run(item):
    name, cfg = item
    row = run_simulation(cfg)
    row["method"] = name
    return row


def run_grid(items, processes=None):
    items = list(items)
    with ProcessPoolExecutor(max_workers=processes or os.cpu_count()) as pool:
        rows = list(pool.map(_run, items, chunksize=max(1, len(items) // 64)))
    return pd.DataFrame(rows)


def summarize_runs(df, keys=("n_sensors", "mobile", "method", "pan", "ari")):
    """Mean over seeds for every scenario cell."""
    metrics = ["accuracy", "f1", "precision", "recall", "fpr", "ftd_mean", "time_to_block_mean",
               "node_detection_rate", "node_legit_blocked", "attack_dio_processed_per_node",
               "trickle_resets_per_node"]
    return df.groupby(list(keys))[metrics].mean().reset_index()
