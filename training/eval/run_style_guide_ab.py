#!/usr/bin/env python3
"""
run_style_guide_ab.py — A/B eval: does K.style_guide() improve Haiku's compositions?

Arm A (guided):   Haiku composes 8 bars for (genre, role) WITH the style guide injected.
Arm B (unguided): identical prompt minus the guide.
Both arms get the same engine-side groove pass (mirrors production), then are scored
by the sandbox tier-0 scorer (midi_metrics). Reports per-genre/role win rates, paired
deltas + bootstrap CI, which metric families move, and per-arm parse-failure rate
(the small-model readiness signal).

Dual purpose: validates the style guide AND the scorer — if guided doesn't beat
unguided, either the guide doesn't help or the metrics don't measure quality.

Usage:
    python training/eval/run_style_guide_ab.py --dry-run          # offline pipeline check
    python training/eval/run_style_guide_ab.py --genres "boom bap,house" --seeds 1
    python training/eval/run_style_guide_ab.py                     # full 9x4x3 matrix

Requires ANTHROPIC_API_KEY (or an `ant auth login` profile on newer SDKs).
Results land in training/eval/results/style_guide_ab_<ts>.json.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import random
import re
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
for p in (str(_ROOT / "harness"), str(_ROOT / "sandbox"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import ableton_knowledge as K  # noqa: E402
import groove  # noqa: E402
import midi_metrics  # noqa: E402

MODEL = "claude-haiku-4-5"
ROLES = ["drums", "bass", "chords", "melody"]
RESULTS_DIR = Path(__file__).parent / "results"

BASE_SYSTEM = (
    "You are a MIDI composer for Ableton Live. You output ONLY a JSON array of note "
    "objects — no prose, no markdown fences. Each note: {\"pitch\": int 0-127, "
    "\"start_time\": float beats, \"duration\": float beats, \"velocity\": int 1-127}. "
    "Compose ON-GRID (start times at multiples of 0.25); humanization is applied for you."
)


def _prompt(genre: str, role: str, seed: int, guided: bool):
    prof = K.genre_profile(genre)
    system = BASE_SYSTEM
    if guided:
        sg = K.style_guide(genre, role)
        system += "\n\nSTYLE GUIDE (follow it precisely):\n" + json.dumps(sg, indent=1)
    user = (f"Compose 8 bars of the {role.upper()} part for a "
            f"{prof['_key'].replace('_', ' ')} beat in {prof['key']} at {prof['bpm']} BPM. "
            f"8 bars of 4/4 span beats 0.0 to 32.0. "
            f"Drum map if drums: kick=36 snare=38 closed_hat=42 open_hat=46 clap=39 rim=37. "
            f"Variation seed: {seed}. Output the JSON array only.")
    return system, user


def _parse_notes(text: str):
    """Tolerant JSON extraction: bare array, fenced block, or {'notes': [...]}."""
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.DOTALL)
    if m:
        t = m.group(1).strip()
    start = t.find("[")
    if start == -1:
        obj_start = t.find("{")
        if obj_start == -1:
            return None
        t = t[obj_start:]
        try:
            data = json.loads(t[: t.rfind("}") + 1])
            t = json.dumps(data.get("notes", []))
            start = 0
        except Exception:
            return None
    try:
        notes = json.loads(t[start: t.rfind("]") + 1])
    except Exception:
        return None
    if not isinstance(notes, list) or not notes:
        return None
    clean = []
    for n in notes:
        if not isinstance(n, dict) or "pitch" not in n:
            return None
        clean.append({"pitch": int(n["pitch"]),
                      "start_time": float(n.get("start_time", 0)),
                      "duration": float(n.get("duration", 0.25)),
                      "velocity": int(n.get("velocity", 100))})
    return clean


class _P:  # minimal project stand-in for the scorer
    def __init__(self, genre):
        prof = K.genre_profile(genre)
        self.genre, self.key, self.plan = prof["_key"], prof["key"], {}


def _score(notes, genre: str, role: str) -> dict:
    grooved = groove.apply_groove(notes, genre, role, seed=0)  # same pass both arms
    return midi_metrics.score_role(role, grooved, _P(genre), bars=8)


def _canned(genre: str, role: str, good: bool):
    """Dry-run compositions: 'good' loosely follows conventions, 'bad' is a flat wall."""
    notes = []
    if not good:
        return [{"pitch": 60, "start_time": i * 0.25, "duration": 0.25, "velocity": 100}
                for i in range(32)]
    root, _ = K.parse_key(K.genre_profile(genre)["key"])
    for bar in range(8):
        b = bar * 4
        if role == "drums":
            notes += [{"pitch": 36, "start_time": b, "duration": 0.5, "velocity": 116},
                      {"pitch": 38, "start_time": b + 1, "duration": 0.5, "velocity": 110},
                      {"pitch": 38, "start_time": b + 3, "duration": 0.5, "velocity": 108}]
            notes += [{"pitch": 42, "start_time": b + i * 0.5, "duration": 0.25,
                       "velocity": 88 if i % 2 == 0 else 62} for i in range(8)]
        elif role == "bass":
            notes += [{"pitch": 36 + root, "start_time": b, "duration": 1.0, "velocity": 104}]
        elif role == "chords":
            notes += [{"pitch": 48 + root + i, "start_time": b, "duration": 3.5, "velocity": 82}
                      for i in (0, 3, 7, 10)]
        else:
            notes += [{"pitch": 60 + root + p, "start_time": b + i, "duration": 0.9,
                       "velocity": 95} for i, p in enumerate((0, 3, 5, 7))]
    return notes


def run_pair(client, genre: str, role: str, seed: int, dry_run: bool) -> dict:
    out = {"genre": K.resolve_genre(genre), "role": role, "seed": seed}
    for arm, guided in (("guided", True), ("unguided", False)):
        if dry_run:
            notes = _canned(genre, role, good=guided)  # guided plays the "better" canned part
        else:
            system, user = _prompt(genre, role, seed, guided)
            try:
                resp = client.messages.create(
                    model=MODEL, max_tokens=4000, system=system,
                    messages=[{"role": "user", "content": user}])
                text = next((b.text for b in resp.content if b.type == "text"), "")
                notes = _parse_notes(text)
            except Exception as e:
                out[arm] = {"error": f"{type(e).__name__}: {str(e)[:120]}"}
                continue
        if notes is None:
            out[arm] = {"parse_failure": True, "score": 0.0}
            continue
        detail = _score(notes, genre, role)
        out[arm] = {"score": detail["score"], "notes": len(notes),
                    "metrics": {m["name"]: m["score"] for m in detail["metrics"]}}
    return out


def _bootstrap_ci(deltas, n=2000, seed=7):
    if not deltas:
        return (0.0, 0.0)
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(deltas, k=len(deltas))) / len(deltas) for _ in range(n))
    return (round(means[int(0.025 * n)], 4), round(means[int(0.975 * n)], 4))


def summarize(pairs):
    scored = [p for p in pairs if "score" in p.get("guided", {}) and "score" in p.get("unguided", {})]
    deltas = [p["guided"]["score"] - p["unguided"]["score"] for p in scored]
    wins = sum(1 for d in deltas if d > 0.005)
    losses = sum(1 for d in deltas if d < -0.005)
    parse_fail = {arm: sum(1 for p in pairs if p.get(arm, {}).get("parse_failure"))
                  for arm in ("guided", "unguided")}
    errors = {arm: sum(1 for p in pairs if "error" in p.get(arm, {}))
              for arm in ("guided", "unguided")}

    # which metric families move (mean guided-minus-unguided per metric name)
    fam: dict = {}
    for p in scored:
        for name, g in p["guided"]["metrics"].items():
            u = p["unguided"]["metrics"].get(name)
            if u is not None:
                fam.setdefault(name, []).append(g - u)
    fam_delta = {k: round(sum(v) / len(v), 4) for k, v in sorted(fam.items())}

    by_role: dict = {}
    for p, d in zip(scored, deltas):
        by_role.setdefault(p["role"], []).append(d)

    return {
        "model": MODEL, "pairs_run": len(pairs), "pairs_scored": len(scored),
        "win_rate": round(wins / len(scored), 3) if scored else None,
        "wins": wins, "losses": losses, "ties": len(scored) - wins - losses,
        "mean_delta": round(sum(deltas) / len(deltas), 4) if deltas else None,
        "delta_ci95": _bootstrap_ci(deltas),
        "delta_by_role": {r: round(sum(v) / len(v), 4) for r, v in sorted(by_role.items())},
        "metric_family_delta": fam_delta,
        "parse_failures": parse_fail, "api_errors": errors,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--genres", default=",".join(K.GENRES))
    ap.add_argument("--roles", default=",".join(ROLES))
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true",
                    help="no API calls; canned compositions exercise the pipeline")
    args = ap.parse_args()

    genres = [g.strip() for g in args.genres.split(",") if g.strip()]
    roles = [r.strip() for r in args.roles.split(",") if r.strip()]
    jobs = [(g, r, s) for g in genres for r in roles for s in range(args.seeds)]
    print(f"style_guide A/B on {MODEL}: {len(genres)} genres x {len(roles)} roles x "
          f"{args.seeds} seeds = {len(jobs)} pairs ({2 * len(jobs)} calls)"
          f"{' [DRY RUN]' if args.dry_run else ''}")

    client = None
    if not args.dry_run:
        import anthropic
        client = anthropic.Anthropic()

    t0 = time.monotonic()
    with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_pair, client, g, r, s, args.dry_run) for g, r, s in jobs]
        pairs = [f.result() for f in futures]
    dt = time.monotonic() - t0

    summary = summarize(pairs)
    summary["wall_seconds"] = round(dt, 1)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"style_guide_ab_{int(time.time())}.json"
    out_path.write_text(json.dumps({"summary": summary, "pairs": pairs}, indent=1))

    print(json.dumps(summary, indent=2))
    print(f"\nfull results -> {out_path}")


if __name__ == "__main__":
    main()
