"""Metrics of a simulation run.

Pair level: every (legitimate detector, node) pair that was within radio range at some point after
detection started; predicted positive if the detector blocked the node at least once. The pair set
depends only on the topology, so it is the same for every detector.
FTD: time from the attack start until an attacker is first marked suspicious by any detector.
"""

import math

import numpy as np


def classification_metrics(tp, fp, tn, fn):
    total = tp + fp + tn + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "accuracy": (tp + tn) / total if total else math.nan,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fp / (fp + tn) if fp + tn else 0.0,
    }


def summarize(sim):
    cfg = sim.cfg
    attackers = [i for i in range(sim.n) if sim.is_attacker[i]]
    tp = fp = tn = fn = 0
    pairs_heard = 0
    for d in sim.legit:
        blocked_by_d = sim.detectors[d].ever_blocked
        pairs_heard += len(sim.heard_after[d])
        for nb in np.nonzero(sim.contact[d])[0]:
            hit = int(nb) in blocked_by_d
            if sim.is_attacker[nb]:
                tp += hit
                fn += not hit
            else:
                fp += hit
                tn += not hit
    out = {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "pairs_heard": pairs_heard,
           **classification_metrics(tp, fp, tn, fn)}

    first_suspicion, first_block = {}, {}
    for d in sim.legit:
        det = sim.detectors[d]
        for nb, t in det.ever_blocked.items():
            first_block[nb] = min(first_block.get(nb, math.inf), t)
        for nb, t in det.first_suspected.items():
            first_suspicion[nb] = min(first_suspicion.get(nb, math.inf), t)

    out["node_detection_rate"] = (sum(a in first_block for a in attackers) / len(attackers)
                                  if attackers else math.nan)
    out["node_legit_blocked"] = sum(i in first_block for i in sim.legit)
    ftd = [first_suspicion[a] - cfg.attack_start for a in attackers if a in first_suspicion]
    ttb = [first_block[a] - cfg.attack_start for a in attackers if a in first_block]
    out["ftd_mean"] = float(np.mean(ftd)) if ftd else math.nan
    out["time_to_block_mean"] = float(np.mean(ttb)) if ttb else math.nan

    sensors = [i for i in sim.legit if i != 0]
    st = sim.stat
    out["joined_at_end"] = float(np.mean(sim.joined[sensors])) if sensors else math.nan
    out["trickle_resets_per_node"] = float(np.mean(st["trickle_resets"][sensors])) if sensors else 0.0
    out["attack_dio_processed_per_node"] = float(np.mean(st["attack_dio_processed"][sim.legit]))
    out["dio_suppressed"] = int(st["dio_suppressed"][sim.legit].sum())
    out["rdt_tx"] = int(st["rdt_tx"].sum())
    out["parents_on_attackers"] = sum(1 for i in sensors if sim.parent[i] is not None
                                      and sim.is_attacker[sim.parent[i]])
    return out
