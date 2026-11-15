"""Command-line demo of FLSec-RPL for the live presentation.

    python demo.py rules                                     # the 27 rules
    python demo.py mfs                                       # paper vs. tuned membership functions
    python demo.py fis 4 8 0                                 # one window: DIO_Counter, DTI (s), STIA (s)
    python demo.py times 0.5 8.5 16.5 24.5 --previous -7.5   # DIO arrival times in a 30 s window
    python demo.py sim --pan 0.2 --ari 2 --mobile            # one simulation, paper vs. tuned sets
    python demo.py sim --sensors 32 --ari 8 --loss 0.2 --methods paper tuned cosec anomaly
"""

import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from flsec import config  # noqa: E402
from flsec.features import NeighborList  # noqa: E402
from flsec.fuzzy import build_paper_fls  # noqa: E402
from flsec.optimize import load_mfs  # noqa: E402
from flsec.simulator import SimConfig, Simulation  # noqa: E402
from flsec.validation import max_detection, quarantine_period  # noqa: E402

TUNED_MFS = ROOT / "results" / "tuned_mfs.json"
LABELS = {"dio_counter": "DIO_Counter", "dti": "DTI (s)", "stia": "STIA (s)"}
METHODS = {"paper": "FLSec-RPL", "tuned": "FLSec-RPL tuned", "cosec": "CoSec-RPL", "anomaly": "Anomaly IDS"}


def fmt(value, digits=3):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return f"{value:.{digits}f}"


def mf_sets(choice):
    sets = {}
    if choice in ("paper", "both"):
        sets["paper"] = config.PAPER_INPUT_MFS
    if choice in ("tuned", "both"):
        sets["tuned"] = load_mfs(TUNED_MFS)
    return sets


def show_rules(_args):
    print("Rule  DIO_Counter  DTI  STIA  ->  aggressive weight")
    for k, (dio, dti, stia, out) in enumerate(config.PAPER_RULES, 1):
        mark = "  <-" if out == "malicious" else ""
        print(f"R{k:<4} {dio:^11}  {dti:^3}  {stia:^4}  ->  {out}{mark}")
    print("\nOnly R1, R4 and R10 conclude malicious, and all three need a Low STIA.")


def show_mfs(_args):
    sets = mf_sets("both")
    for name in config.INPUT_NAMES:
        print(f"\n{LABELS[name]}")
        for term in config.TERMS:
            row = "".join(f"{label}: " + f"({', '.join(f'{v:.2f}' for v in mfs[name][term])})".ljust(30)
                          for label, mfs in sets.items())
            print(f"  {term}  {row}".rstrip())
    print("\nOutput: normal (0, 0, 0.5), quarantine (0, 0.5, 1), malicious (0.5, 1, 1); centroids 1/6, 1/2, 5/6")


def explain(x, sets):
    clipped = np.clip(np.asarray(x, dtype=float), *config.INPUT_UNIVERSE)
    print(f"inputs: DIO_Counter = {clipped[0]:g}, DTI = {clipped[1]:g} s, STIA = {clipped[2]:g} s"
          " (clipped to [0, 30])")
    for label, mfs in sets.items():
        fls = build_paper_fls(input_mfs=mfs)
        trace = fls.explain(x)
        cog = build_paper_fls(defuzz="cog", input_mfs=mfs).infer([x])[0]
        omega = trace["omega"]
        print(f"\n== {label} membership functions ==")
        print(f"{'':13}{'Low':>8}{'Medium':>8}{'High':>8}")
        for var in fls.inputs:
            mu = trace["memberships"][var.name]
            print(f"{LABELS[var.name]:13}" + "".join(f"{mu[t]:8.3f}" for t in config.TERMS))
        print("fired rules:")
        for r in trace["fired_rules"]:
            print(f"  R{r['rule']:<3} {'/'.join(r['if'])} -> {r['then']:<10} strength {r['strength']:.3f}")
        print(f"omega (Eq. 8)           {omega:.4f}")
        print(f"omega (Mamdani COG)     {cog:.4f}  (reference only)")
        if omega > config.FUZZY_FILTER_DELTA:
            print(f"decision                suspicious (omega > {config.FUZZY_FILTER_DELTA})")
            print(f"phase III               MD = {max_detection(omega):.2f} detections, "
                  f"QP = {quarantine_period(omega):.1f} s (with an RDT flag: MD = 6, QP = 180 s)")
        else:
            print(f"decision                normal (omega <= {config.FUZZY_FILTER_DELTA})")


def run_fis(args):
    explain([args.dio_counter, args.dti, args.stia], mf_sets(args.mfs))


def run_times(args):
    times = sorted(args.times)
    window = config.OBSERVATION_WINDOW_S
    if times[0] < 0 or times[-1] >= window:
        sys.exit(f"DIO times must lie in the observation window [0, {window:g}) s")
    if args.previous is not None and args.previous >= times[0]:
        sys.exit("--previous must be earlier than the first DIO of the window")

    nl = NeighborList()
    if args.previous is not None:
        nl.record_dio(1, args.previous)
        nl.close_window()
    cap, alpha = config.INPUT_UNIVERSE[1], config.SMOOTHING_ALPHA
    last, pti = args.previous, None
    print(f"{'t (s)':>8}{'DTI_t':>9}{'PTI_t':>9}{'(DTI-PTI)^2':>14}")
    for t in times:
        nl.record_dio(1, t)
        dti = cap if last is None else min(t - last, cap)
        pti = dti if pti is None else alpha * dti + (1 - alpha) * pti
        print(f"{t:8.2f}{dti:9.2f}{pti:9.2f}{(dti - pti) ** 2:14.3f}")
        last = t
    (obs,) = nl.close_window()
    print(f"\nDIO_Counter = {obs.dio_counter}, DTI = last interval = {obs.dti:.2f} s, "
          f"STIA = sqrt(sum / {obs.dio_counter}) = {obs.stia:.3f} s\n")
    explain(list(obs.as_input()), mf_sets(args.mfs))


def simulate(method, args):
    if method in ("paper", "tuned"):
        kind = "flsec"
        opts = {"defuzz": args.defuzz, "stia_mode": args.stia_mode, "use_stia": not args.no_stia,
                "use_rdt": not args.no_rdt, "validation": not args.no_validation}
        if args.fixed_md is not None:
            opts.update(adaptive_md=False, fixed_md=args.fixed_md)
        if method == "tuned":
            opts["input_mfs"] = load_mfs(TUNED_MFS)
    elif method == "cosec":
        kind, opts = "cosec", {"sigma": args.cosec_sigma}
    else:
        kind, opts = "anomaly", {}
    cfg = SimConfig(n_sensors=args.sensors, pan=args.pan, ari=args.ari, mobile=args.mobile, detector=kind,
                    detector_options=opts, seed=args.seed, p_loss=args.loss, duration=args.duration)
    sim = Simulation(cfg)
    result = sim.run()
    blocked = {nb for d in sim.legit for nb in sim.detectors[d].ever_blocked}
    result["legit_ids"] = sorted(int(b) for b in blocked if not sim.is_attacker[b])
    result["attacker_ids"] = [int(i) for i in np.nonzero(sim.is_attacker)[0]]
    return result


def run_sim(args):
    if not 0 <= args.pan <= 1 or args.ari <= 0 or args.sensors < 2:
        sys.exit("need 0 <= pan <= 1, ari > 0 and at least 2 sensors")
    start = time.time()
    results = {m: simulate(m, args) for m in args.methods}
    first = next(iter(results.values()))
    attackers = first["attacker_ids"]
    print(f"{args.sensors} sensors, {'mobile' if args.mobile else 'static'}, PAN {args.pan:.0%} "
          f"({len(attackers)} attackers: nodes {', '.join(map(str, attackers)) or '-'}), ARI {args.ari:g} s, "
          f"packet loss {args.loss:.0%}, seed {args.seed}, {args.duration:g} s")

    rows = [
        ("pairs TP/FP/TN/FN", lambda r: f"{r['tp']}/{r['fp']}/{r['tn']}/{r['fn']}"),
        ("accuracy", lambda r: fmt(r["accuracy"])),
        ("F1", lambda r: fmt(r["f1"])),
        ("recall", lambda r: fmt(r["recall"])),
        ("false positive rate", lambda r: fmt(r["fpr"])),
        ("attackers blocked", lambda r: f"{round(r['node_detection_rate'] * len(attackers))}/{len(attackers)}"
                                        if attackers else "-"),
        ("legit nodes blocked", lambda r: str(r["node_legit_blocked"])),
        ("first-time detection (s)", lambda r: fmt(r["ftd_mean"], 1)),
        ("time to block (s)", lambda r: fmt(r["time_to_block_mean"], 1)),
        ("attack DIOs per node", lambda r: fmt(r["attack_dio_processed_per_node"], 1)),
    ]
    print("\n" + f"{'':26}" + "".join(f"{METHODS[m]:>18}" for m in results))
    for label, get in rows:
        print(f"{label:26}" + "".join(f"{get(r):>18}" for r in results.values()))
    for m, r in results.items():
        if r["legit_ids"]:
            print(f"\n{METHODS[m]} blocked legitimate nodes: {', '.join(map(str, r['legit_ids']))}")
    print(f"\n{len(results)} runs in {time.time() - start:.1f} s")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("rules", help="print the rule base").set_defaults(func=show_rules)
    sub.add_parser("mfs", help="print the paper and tuned membership functions").set_defaults(func=show_mfs)

    p = sub.add_parser("fis", help="explain the fuzzy decision for one window")
    p.add_argument("dio_counter", type=float)
    p.add_argument("dti", type=float, help="seconds")
    p.add_argument("stia", type=float, help="seconds")
    p.add_argument("--mfs", choices=["paper", "tuned", "both"], default="both")
    p.set_defaults(func=run_fis)

    p = sub.add_parser("times", help="phase I and II for the DIO arrival times of one neighbor")
    p.add_argument("times", type=float, nargs="+", help="DIO times in the window [0, 30) s")
    p.add_argument("--previous", type=float, default=None,
                   help="time of the neighbor's previous DIO, before the window (e.g. -7.5)")
    p.add_argument("--mfs", choices=["paper", "tuned", "both"], default="both")
    p.set_defaults(func=run_times)

    p = sub.add_parser("sim", help="run one simulation with each method")
    p.add_argument("--sensors", type=int, default=16)
    p.add_argument("--pan", type=float, default=0.2, help="share of attackers, 0-1")
    p.add_argument("--ari", type=float, default=2.0, help="attack replay interval (s)")
    p.add_argument("--mobile", action="store_true")
    p.add_argument("--loss", type=float, default=0.02, help="packet loss probability")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--duration", type=float, default=config.SIM_DURATION_S)
    p.add_argument("--methods", nargs="+", choices=list(METHODS), default=["paper", "tuned"])
    p.add_argument("--cosec-sigma", type=float, default=0.5)
    p.add_argument("--defuzz", choices=["paper", "cog"], default="paper")
    p.add_argument("--stia-mode", choices=["window", "within", "persistent"], default="window")
    p.add_argument("--no-stia", action="store_true")
    p.add_argument("--no-rdt", action="store_true")
    p.add_argument("--no-validation", action="store_true")
    p.add_argument("--fixed-md", type=float, default=None)
    p.set_defaults(func=run_sim)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
