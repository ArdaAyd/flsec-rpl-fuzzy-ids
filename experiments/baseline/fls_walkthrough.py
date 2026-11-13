"""Runs typical neighbors through phases I-III and plots the fuzzy system.

Usage: python experiments/baseline/fls_walkthrough.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flsec import config  # noqa: E402
from flsec.features import NeighborList  # noqa: E402
from flsec.fuzzy import build_paper_fls  # noqa: E402
from flsec.plotting import plot_decision_surfaces, plot_membership_functions  # noqa: E402
from flsec.validation import max_detection, quarantine_period  # noqa: E402


def trickle_burst(rng, imin=config.TRICKLE_IMIN_S, horizon=30.0):
    """DIO times of a node whose Trickle timer was reset at t = 0."""
    times, start, interval = [], 0.0, imin
    while True:
        t = start + rng.uniform(interval / 2, interval)
        if t >= horizon:
            return times
        times.append(t)
        start, interval = start + interval, 2 * interval


def cases(rng):
    # (name, previous DIO before the window, DIO times in [0, 30))
    return [
        ("Attacker, ARI = 1 s", -0.5, np.arange(0.5, 30, 1.0)),
        ("Attacker, ARI = 2 s", -1.5, np.arange(0.5, 30, 2.0)),
        ("Attacker, ARI = 8 s", -7.5, np.arange(0.5, 30, 8.0)),
        ("Legitimate, steady state", -50.0, [14.0]),
        ("Legitimate, Trickle reset", -300.0, trickle_burst(rng)),
    ]


def main():
    fls = build_paper_fls()
    rows = []
    for name, previous, times in cases(np.random.default_rng(7)):
        nl = NeighborList()
        nl.record_dio(1, previous)
        nl.close_window()
        for t in times:
            nl.record_dio(1, float(t))
        (obs,) = nl.close_window()
        trace = fls.explain(obs.as_input())
        omega = trace["omega"]
        top = trace["fired_rules"][0]
        suspicious = omega > config.FUZZY_FILTER_DELTA
        rows.append({
            "case": name,
            "DIO_Counter": obs.dio_counter,
            "DTI (s)": round(obs.dti, 2),
            "STIA (s)": round(obs.stia, 2),
            "strongest rule": f"R{top['rule']} {'/'.join(top['if'])} -> {top['then']} ({top['strength']:.2f})",
            "omega": round(omega, 4),
            "decision": "suspicious" if suspicious else "normal",
            "MD": round(max_detection(omega), 2) if suspicious else None,
            "QP (s)": round(quarantine_period(omega), 1) if suspicious else None,
        })

    table = pd.DataFrame(rows)
    tables = ROOT / "results" / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    table.to_csv(tables / "fls_walkthrough.csv", index=False)
    (tables / "fls_walkthrough.md").write_text(table.to_markdown(index=False) + "\n")
    print(table.to_string(index=False))

    figures = ROOT / "results" / "figures"
    plot_membership_functions(fls, figures / "fig_membership_functions.png")
    markers = [(r["DIO_Counter"], r["DTI (s)"], r["case"].split(", ")[1]) for r in rows[:3]]
    plot_decision_surfaces(fls, figures / "fig_decision_surface.png", markers=markers)


if __name__ == "__main__":
    main()
