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

STAGE 2 (real recorded data) — `python probe_frame.py --real`:
The synthetic probe above proves the encoding CAN carry constructed properties. The real
probe proves it carries decodable signal on ACTUAL recorded sessions and GENERALIZES across
held-out sessions. It loads the 25Hz trajectory recordings, reconstructs the 130-D vector,
and reports (a) NON-DEGENERACY (live vs dead dims, PCA effective rank) and (b) DECODABILITY
under LEAVE-ONE-SESSION-OUT — 25Hz frames are heavily autocorrelated, so a random split
leaks and inflates accuracy; LOSO is the honest number. Targets are ground truth pulled from
the frame DICT (never the vector): beat_quadrant + loudest_role are POSITIVE CONTROLS (their
inputs are in the vector); clash_present tests masking decodability; transient_next (does a
level_jump fire in the NEXT frame) is the forward-looking, non-circular probe closest to
SIM's real job. Same control-shuffle selectivity discipline as Stage 1.
Caveat: recorded sessions are all ~120 BPM with no song id (likely the same test song), so
LOSO measures TEMPORAL, not cross-song, generalization.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

import bands as _bands
import perception_frame as pf
from masking import Node, compute_masking
from mix_analysis_bridge import TrackState
from perception_recorder import frames_of, load_trajectory

_REPO = Path(__file__).resolve().parent.parent
_TRAJ_ROOT = _REPO / "sandbox_sessions" / "trajectories"
_RESULTS_DIR = _REPO / "training" / "eval" / "results"
REAL_SCHEMA_VERSION = "sim.frame-probe-real.v1"

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


def _fit_selectivity(Xtr, ytr, Xte, yte, make_clf, seed=0):
    """Scale, fit a real + a shuffled-control probe on ONE fixed split; report selectivity.

    The shared core of both probe stages: same StandardScaler + label-shuffle-control +
    `selectivity = real - control` discipline. Callers own the split strategy (stratified
    random for synthetic, leave-one-session-out for real) and the estimator (`make_clf`).
    Returns None when the split can't be scored (single-class train or empty test).
    """
    from sklearn.preprocessing import StandardScaler

    if len(np.unique(ytr)) < 2 or yte.size == 0:
        return None
    sc = StandardScaler().fit(Xtr)
    Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

    def _acc(labels_tr):
        clf = make_clf()
        clf.fit(Xtr_s, labels_tr)
        return float(clf.score(Xte_s, yte))

    real = _acc(ytr)
    control = _acc(np.random.default_rng(seed).permutation(ytr))   # same inputs, scrambled labels
    _, counts = np.unique(yte, return_counts=True)
    return {"n_test": int(yte.size), "n_classes": int(len(np.unique(ytr))),
            "majority": float(counts.max()) / yte.size,
            "real_acc": real, "control_acc": control, "selectivity": real - control}


def run_probe(X, y, name, seed=0):
    """Synthetic-scenario probe: a stratified random split scored by _fit_selectivity."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split

    y = np.asarray(y)
    if len(np.unique(y)) < 2:
        return None
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    m = _fit_selectivity(Xtr, ytr, Xte, yte, lambda: LogisticRegression(max_iter=2000, C=1.0), seed)
    if m is None:
        return None
    return {"task": name, "classes": m["n_classes"], "majority": m["majority"],
            "real_acc": m["real_acc"], "control_acc": m["control_acc"],
            "selectivity": m["selectivity"]}


# ===========================================================================
# STAGE 2 — probe the REAL recorded trajectory data (leave-one-session-out)
# ===========================================================================
# ground-truth targets — derived from the recorded frame DICT, never the vector
def _beat_quadrant(step):
    """Which beat of the bar (0..beats_per_bar-1). Positive control (time block encodes it)."""
    f = step["frame"]
    return int(min(f.get("beat", 0.0), (f.get("beats_per_bar") or 4) - 1))


def _loudest_role(step, non_master):
    """Index (into non_master) of the loudest role by RMS; -1 if all silent (skip row)."""
    rs = step["frame"].get("role_state", {})
    best_i, best_db = -1, -119.0
    for i, r in enumerate(non_master):
        db = rs.get(r, {}).get("rms_db", -120.0)
        if db > best_db:
            best_i, best_db = i, db
    return best_i


def _mask_intensity(step):
    """Frame's peak masking-pair score. On real material an absolute clash threshold (~0.5)
    is never crossed (scores top out ~0.17 — see the masking-scale caveat in run_real), so
    the relative_masking_high target is a DATA-RELATIVE above-median split of this quantity:
    a balanced test of decoding relative masking, not absolute clash detection."""
    pairs = step["frame"].get("masking", {}).get("pairs", [])
    return max((float(p.get("score", 0.0)) for p in pairs), default=0.0)


def _has_level_jump(step):
    return any(e.get("type") == "level_jump" for e in step.get("events", []))


def load_recorded(session_dirs):
    """Reconstruct 130-D vectors + aligned ground-truth targets per recorded session.

    Returns (sessions, mask_median) where each session is {name, X (N x D), _mask_intensity,
    targets {name: array, nan=skip}}. Fails loud on an empty session so a broken recording
    can't silently shrink the set.
    """
    sessions = []
    for d in session_dirs:
        steps = load_trajectory(d)["steps"]
        if not steps:
            raise ValueError(f"session {d} has no recorded steps")
        non_master = [r for r in steps[0]["frame"]["roles"] if r != "master"]
        X = np.array([f.to_vector() for f in frames_of(steps)], dtype=np.float64)

        quad = np.array([_beat_quadrant(s) for s in steps], dtype=np.float64)
        loud = np.array([_loudest_role(s, non_master) for s in steps], dtype=np.float64)
        loud[loud < 0] = np.nan                                      # drop all-silent rows
        intensity = np.array([_mask_intensity(s) for s in steps], dtype=np.float64)
        tnext = np.array([_has_level_jump(steps[i + 1]) if i + 1 < len(steps) else np.nan
                          for i in range(len(steps))], dtype=np.float64)  # next-frame transient
        sessions.append({"name": Path(d).name, "X": X, "_mask_intensity": intensity,
                         "targets": {"beat_quadrant": quad, "loudest_role": loud,
                                     "transient_next": tnext}})
    # relative_masking_high: DATA-RELATIVE above-median split (absolute clash is never crossed).
    thr = float(np.median(np.concatenate([s["_mask_intensity"] for s in sessions])))
    for s in sessions:
        s["targets"]["relative_masking_high"] = (s["_mask_intensity"] >= thr).astype(np.float64)
    return sessions, thr


def degeneracy_report(X):
    """Per-dim variance + PCA effective rank over the pooled real frames."""
    std = X.std(axis=0)
    dead = int((std < 1e-6).sum())
    Xc = X - X.mean(axis=0)
    sv = np.linalg.svd(Xc, compute_uv=False)
    var = sv ** 2
    total = float(var.sum())
    cum = np.cumsum(var / total) if total > 0 else np.zeros_like(var)
    pr = float((total ** 2) / float(np.square(var).sum())) if total > 0 else 0.0
    return {"n_frames": int(X.shape[0]), "n_dims": int(X.shape[1]),
            "n_dead_dims": dead, "n_live_dims": int(X.shape[1] - dead),
            "std_min": float(std.min()), "std_mean": float(std.mean()), "std_max": float(std.max()),
            "pca_components_for_95pct": int(np.searchsorted(cum, 0.95) + 1),
            "pca_components_for_99pct": int(np.searchsorted(cum, 0.99) + 1),
            "participation_ratio": round(pr, 2)}


def _clean(X, y):
    """Drop rows whose target is NaN (skip markers)."""
    m = ~np.isnan(y)
    return X[m], y[m].astype(int)


# RidgeClassifier — a CLOSED-FORM linear decoder (one linear solve, no iterative convergence).
# On 10^5 frames a multinomial lbfgs LogisticRegression grinds to max_iter and costs minutes
# per fit; Ridge is sub-second and is the more honest test of "is the info LINEARLY decodable"
# (the synthetic Stage-1 probe keeps LogisticRegression, whose scenarios are small).
def _ridge():
    from sklearn.linear_model import RidgeClassifier
    return RidgeClassifier(alpha=1.0)


def run_probe_loso(sessions, target, pooled_X, train_X_by_held, seed=0):
    """Leave-one-session-out probe + a leaky random-split contrast for one target.

    `pooled_X` (all frames) and `train_X_by_held[h]` (all frames except session h) are
    target-independent and precomputed once by the caller, so the big vector matrices are
    not re-stacked per target. Only the per-target labels (y) and the fits vary here.
    """
    folds = []
    for held in range(len(sessions)):
        Xte, yte = _clean(sessions[held]["X"], sessions[held]["targets"][target])
        if Xte.shape[0] == 0:
            continue
        ytr = np.concatenate([s["targets"][target] for i, s in enumerate(sessions) if i != held])
        Xtr, ytr = _clean(train_X_by_held[held], ytr)
        r = _fit_selectivity(Xtr, ytr, Xte, yte, _ridge, seed)
        if r is not None:
            r["held_out"] = sessions[held]["name"]
            folds.append(r)

    # leaky random split (autocorrelation-inflated upper bound, clearly labeled)
    yall = np.concatenate([s["targets"][target] for s in sessions])
    Xall, yall = _clean(pooled_X, yall)
    leaky = None
    if Xall.shape[0] > 10 and len(np.unique(yall)) >= 2:
        perm = np.random.default_rng(seed).permutation(Xall.shape[0])
        cut = int(0.8 * Xall.shape[0])
        tr, te = perm[:cut], perm[cut:]
        leaky = _fit_selectivity(Xall[tr], yall[tr], Xall[te], yall[te], _ridge, seed)

    mean = {}
    if folds:
        for k in ("majority", "real_acc", "control_acc", "selectivity"):
            mean[k] = round(float(np.mean([f[k] for f in folds])), 4)
    return {"target": target, "n_folds": len(folds), "loso_mean": mean,
            "loso_folds": folds, "leaky_random_split": leaky}


REAL_TARGETS = ("beat_quadrant", "loudest_role", "relative_masking_high", "transient_next")
_CONTROL_TARGETS = {"beat_quadrant", "loudest_role"}   # positive controls (inputs in the vector)


def run_real(session_dirs):
    """Full real-data probe: non-degeneracy + LOSO decodability over all targets."""
    sessions, thr = load_recorded(session_dirs)
    pooled = np.vstack([s["X"] for s in sessions])
    train_X_by_held = [np.vstack([s["X"] for i, s in enumerate(sessions) if i != held])
                       for held in range(len(sessions))]
    max_mask = float(np.concatenate([s["_mask_intensity"] for s in sessions]).max())
    return {
        "schema_version": REAL_SCHEMA_VERSION,
        "sessions": [{"name": s["name"], "n_frames": int(s["X"].shape[0])} for s in sessions],
        "vector_len": int(pooled.shape[1]),
        "degeneracy": degeneracy_report(pooled),
        "mask_median_threshold": round(thr, 4),
        "max_masking_score": round(max_mask, 3),
        "targets": {t: run_probe_loso(sessions, t, pooled, train_X_by_held) for t in REAL_TARGETS},
        "notes": {
            "anti_leakage": "loso_mean is the honest metric; leaky_random_split is an "
                            "autocorrelation-inflated upper bound (25Hz frames are correlated).",
            "controls": "beat_quadrant + loudest_role are positive controls (their inputs "
                        "are in the vector). transient_next is the forward-looking probe.",
            "relative_masking_high": f"absolute masking is near-zero on this material (max pair "
                                     f"score {max_mask:.2f}), so an absolute clash target is "
                                     f"degenerate; this is a DATA-RELATIVE above-median split "
                                     f"(thr={thr:.4f}) — a plumbing check on relative masking, "
                                     f"NOT absolute clash detection. UPSTREAM: the masking score "
                                     f"in masking.py is an unbounded energy sum; a bounded [0,1] "
                                     f"intensity would let this be an absolute target.",
            "same_song_caveat": "all sessions ~120 BPM, no song id -> likely same song; "
                                "LOSO measures temporal, not cross-song, generalization.",
        },
    }


def _fmt_real(res):
    d = res["degeneracy"]
    lines = ["=" * 72,
             "FRAME PROBE (REAL recorded data) — is the 130-D vector learnable?",
             "=" * 72,
             "sessions: " + ", ".join(f"{s['name']}({s['n_frames']})" for s in res["sessions"]),
             f"NON-DEGENERACY: {d['n_live_dims']}/{d['n_dims']} dims live ({d['n_dead_dims']} dead)"
             f" | PCA {d['pca_components_for_95pct']} comps=95% var, {d['pca_components_for_99pct']}"
             f"=99% | participation-ratio {d['participation_ratio']}",
             "-" * 72,
             f"{'target':22s} {'ctrl?':>5} {'base':>6} {'realLOSO':>9} {'shuf':>6} "
             f"{'select':>7} {'leaky':>6}  flag"]
    for t in REAL_TARGETS:
        m = res["targets"][t]["loso_mean"]
        if not m:
            lines.append(f"{t:22s}  (no valid fold — degenerate target)")
            continue
        lk = res["targets"][t]["leaky_random_split"]
        leaky = f"{lk['real_acc']:.2f}" if lk else "  --"
        is_ctrl = "yes" if t in _CONTROL_TARGETS else "no"
        good = m["selectivity"] > 0.05 and m["real_acc"] > m["majority"] + 0.03
        flag = "GOOD" if good else ("control" if t in _CONTROL_TARGETS else "weak")
        lines.append(f"{t:22s} {is_ctrl:>5} {m['majority']:>6.2f} {m['real_acc']:>9.2f} "
                     f"{m['control_acc']:>6.2f} {m['selectivity']:>7.2f} {leaky:>6}  {flag}")
    lines += ["-" * 72,
              "LOSO = leave-one-session-out (honest); leaky = random split (autocorr upper "
              "bound). select = realLOSO - shuffled-label control.", "=" * 72]
    return "\n".join(lines)


def _discover_sessions():
    return sorted(p for p in _TRAJ_ROOT.glob("sess_*") if (p / "frames.jsonl").exists())


def main_real(session_dirs=None, out_path=None):
    session_dirs = session_dirs or _discover_sessions()
    if len(session_dirs) < 2:
        raise SystemExit(f"need >=2 sessions for leave-one-session-out; found {len(session_dirs)}")
    print(f"[probe] loading {len(session_dirs)} session(s), reconstructing 130-D vectors...")
    res = run_real(session_dirs)
    print(_fmt_real(res))
    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = Path(out_path) if out_path else (_RESULTS_DIR / f"frame_probe_real_{int(time.time())}.json")
    out.write_text(json.dumps(res, indent=2))
    print(f"[probe] wrote {out}")
    return res


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
    ap = argparse.ArgumentParser(description="Probe whether the 130-D perception vector is learnable.")
    ap.add_argument("--real", action="store_true",
                    help="probe the REAL recorded trajectory data (leave-one-session-out) "
                         "instead of synthetic scenarios")
    ap.add_argument("--sessions", nargs="*", type=Path, default=None,
                    help="session dirs for --real (default: all under sandbox_sessions/trajectories/)")
    ap.add_argument("-n", type=int, default=800, help="synthetic scenarios (default probe)")
    args = ap.parse_args()
    if args.real:
        main_real(session_dirs=args.sessions)
    else:
        main(n=args.n)
