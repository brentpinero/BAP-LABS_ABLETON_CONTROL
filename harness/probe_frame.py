"""
probe_frame.py — does the perception frame actually ENCODE the mix properties that
matter? (Stage 1 of the eval plan: probing classifiers with control tasks + selectivity.)

Method (Hewitt & Liang 2019): generate synthetic multi-track mixes with KNOWN ground
truth, extract the real `perception_frame.to_vector()`, then train a deliberately simple
linear probe (logistic regression) to decode each property. For every probe we ALSO train
the same probe on a CONTROL task (labels shuffled) and report:

    selectivity = real_task_accuracy - control_task_accuracy

High real acc with LOW control acc => the FRAME encodes the property linearly (good).
High real acc with HIGH control acc => the probe is just powerful (the frame gets no credit).

This is the cheapest high-signal test of "is the frame deep enough" — it needs NO backbone
training and NO Ableton. Run:  python probe_frame.py   (or import gen_scenarios/run_probe).

Ground-truth labels are either APPLIED by construction (tonal tilt, vocal buried) or derived
from the offline DSP gold (masking.compute_masking) — the latter are plumbing sanity checks
(the info is partly in the vector already); the former are the emergent, load-bearing probes.
"""

from __future__ import annotations

import numpy as np

import bands as _bands
import perception_frame as pf
from masking import Node, compute_masking
from mix_analysis_bridge import TrackState

# characteristic 7-band shapes (sub, low, low_mid, mid, hi_mid, presence, air) per role
_ROLE_SHAPES = {
    "Drums":  [0.15, 0.15, 0.10, 0.20, 0.15, 0.15, 0.10],
    "Bass":   [0.10, 0.35, 0.30, 0.20, 0.05, 0.00, 0.00],
    "Sub":    [0.60, 0.30, 0.10, 0.00, 0.00, 0.00, 0.00],
    "Vox":    [0.00, 0.00, 0.10, 0.40, 0.25, 0.20, 0.05],
    "Synth":  [0.00, 0.05, 0.15, 0.35, 0.25, 0.15, 0.05],
    "FX":     [0.00, 0.00, 0.05, 0.20, 0.25, 0.30, 0.20],
}
_HI = [4, 5, 6]   # hi_mid, presence, air indices (for tonal tilt)
_TRANSPORT = {"bpm": 126.0, "bar": 8, "beat": 1.0, "beats_per_bar": 4, "playing": True}


def _ts(rng, name, bands_, rms_db, width):
    b = np.clip(np.array(bands_) * rng.uniform(0.8, 1.2, len(bands_)), 0, None)
    b = (b / b.sum()).tolist() if b.sum() > 0 else b.tolist()
    return TrackState(track_id=name, name=name, kind="group", group_id="-1",
                      bands=b, rms_l=rms_db, rms_r=rms_db,
                      mid_energy=1.0 - width, side_energy=width)


def gen_scenarios(n, seed_base=0):
    """Yield (vector, labels) for n synthetic mixes with known ground truth."""
    names = _bands.band_names(pf.cfg("band_scheme"))
    for k in range(n):
        rng = np.random.default_rng(seed_base + k)
        # base per-role loudness + width
        tracks = {}
        rms = {r: rng.uniform(-20, -6) for r in _ROLE_SHAPES}
        # --- perturbation 1: vocal buried (binary) ---
        buried = int(rng.random() < 0.5)
        if buried:
            rms["Vox"] = rng.uniform(-26, -18)          # push vox down
            rms["Synth"] = rng.uniform(-8, -4)          # loud synth overlapping vox mid/pres
        # --- perturbation 2: tonal tilt (0 dark / 1 neutral / 2 bright) ---
        tilt = int(rng.integers(0, 3))
        tilt_factor = {0: 0.4, 1: 1.0, 2: 2.2}[tilt]
        for r, shape in _ROLE_SHAPES.items():
            b = list(shape)
            for i in _HI:
                b[i] *= tilt_factor
            tracks[r] = _ts(rng, r, b, rms[r], rng.uniform(0.05, 0.5))
        vec = pf.build_frame(tracks, _TRANSPORT).to_vector()

        # --- derived gold from offline masking (plumbing sanity) ---
        nodes = [tracks[r].to_node() for r in tracks]
        m = compute_masking(nodes, pf.cfg("band_scheme"), participants=("group",))
        cong = m.get("master_congestion", [])
        most_congested = int(np.argmax([c["congestion"] for c in cong])) if cong else 0

        yield np.array(vec, dtype=np.float64), {
            "vocal_buried": buried,
            "tonal_tilt": tilt,
            "most_congested_band": most_congested,
        }


def run_probe(X, y, name, seed=0):
    """Train a linear probe + a control probe (shuffled labels); report selectivity."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    y = np.asarray(y)
    if len(np.unique(y)) < 2:
        return None
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    sc = StandardScaler().fit(Xtr)
    Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)

    def _acc(labels_tr):
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(Xtr, labels_tr)
        return clf.score(Xte, yte)

    real = _acc(ytr)
    rng = np.random.default_rng(seed)
    control = _acc(rng.permutation(ytr))               # same inputs, scrambled labels
    majority = float(np.bincount(yte).max()) / len(yte)
    return {"task": name, "classes": int(len(np.unique(y))), "majority": majority,
            "real_acc": real, "control_acc": control, "selectivity": real - control}


def main(n=800):
    data = list(gen_scenarios(n))
    X = np.vstack([v for v, _ in data])
    print(f"probed {n} synthetic mixes; frame dim = {X.shape[1]}\n")
    print(f"{'task':22s} {'classes':>7} {'majority':>9} {'real':>6} {'control':>8} {'selectivity':>12}")
    for key in ("vocal_buried", "tonal_tilt", "most_congested_band"):
        y = [lab[key] for _, lab in data]
        r = run_probe(X, np.array(y), key)
        if r:
            flag = "GOOD" if r["selectivity"] > 0.15 and r["real_acc"] > r["majority"] + 0.1 else "weak"
            print(f"{r['task']:22s} {r['classes']:>7} {r['majority']:>9.2f} "
                  f"{r['real_acc']:>6.2f} {r['control_acc']:>8.2f} {r['selectivity']:>12.2f}  {flag}")
    print("\nselectivity = real - control; GOOD = frame encodes it linearly above the "
          "control baseline (info is in the frame, not just the probe).")


if __name__ == "__main__":
    main()
