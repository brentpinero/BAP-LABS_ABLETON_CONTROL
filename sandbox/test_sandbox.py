"""
test_sandbox.py — offline tests for the sandbox engine (no Ableton, no audio).

Covers: golden good-vs-bad pattern ranking per role, groove determinism,
loop verdicts (pass/plateau/budget), best-iteration selection, partial-submit
merge, checkpoint gating. Run: python sandbox/test_sandbox.py  (or pytest).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import groove  # noqa: E402
import midi_metrics  # noqa: E402
from loop import SandboxEngine  # noqa: E402
from project_state import SESSIONS_DIR, SandboxConfig, SandboxSession  # noqa: E402

BARS = 4


def _good_drums():
    notes = []
    for bar in range(BARS):
        b = bar * 4
        notes += [{"pitch": 36, "start_time": b + 0.0, "duration": 0.5, "velocity": 115},
                  {"pitch": 36, "start_time": b + 2.5, "duration": 0.5, "velocity": 105},
                  {"pitch": 38, "start_time": b + 1.0, "duration": 0.5, "velocity": 112},
                  {"pitch": 38, "start_time": b + 3.0, "duration": 0.5, "velocity": 108}]
        notes += [{"pitch": 42, "start_time": b + t / 2, "duration": 0.25,
                   "velocity": 90 if t % 2 == 0 else 62} for t in range(8)]
    return notes


def _bad_drums():  # no backbeat, flat velocity, wall of same-pitch hits
    return [{"pitch": 42, "start_time": i * 0.25, "duration": 0.1, "velocity": 100}
            for i in range(BARS * 16)]


def _good_bass():
    notes = []
    for bar in range(BARS):
        b = bar * 4
        root = [45, 41, 43, 41][bar % 4]  # A F G F — in A minor
        notes += [{"pitch": root, "start_time": b + 0.0, "duration": 1.0, "velocity": 105},
                  {"pitch": root, "start_time": b + 2.5, "duration": 0.75, "velocity": 95}]
    return notes


def _bad_bass():  # out of key, high register, overlapping wall
    return [{"pitch": 70 + (i % 3), "start_time": i * 0.5, "duration": 2.0, "velocity": 100}
            for i in range(BARS * 8)]


def _good_chords():  # Am7 / Dm7 comp above C2
    notes = []
    for bar in range(BARS):
        b = bar * 4
        chord = [57, 60, 64, 67] if bar % 2 == 0 else [50, 53, 57, 60]
        for p in chord:
            notes.append({"pitch": p, "start_time": b + 0.0, "duration": 3.5, "velocity": 84})
    return notes


def _good_melody():
    seq = [69, 72, 74, 76, 74, 72, 69, 67]  # A C D E ... pentatonic
    notes = []
    for bar in range(0, BARS, 2):
        b = bar * 4
        for i, p in enumerate(seq):
            notes.append({"pitch": p, "start_time": b + i * 0.5, "duration": 0.45, "velocity": 95})
    return notes


class _P:  # minimal project stand-in for direct metric tests
    genre, key, plan = "boom_bap", "A minor", {}


# --- metrics: golden ranking ------------------------------------------------
def test_good_beats_bad_per_role():
    for role, good, bad in [
        ("drums", _good_drums(), _bad_drums()),
        ("bass", _good_bass(), _bad_bass()),
    ]:
        g = midi_metrics.score_role(role, good, _P, BARS)["score"]
        b = midi_metrics.score_role(role, bad, _P, BARS)["score"]
        assert g > b + 0.15, f"{role}: good {g} should clearly beat bad {b}"


def test_muspy_primitives():
    assert midi_metrics.scale_consistency(_good_bass(), "A minor") == 1.0
    assert midi_metrics.scale_consistency(
        [{"pitch": 61, "start_time": 0, "duration": 1, "velocity": 90}], "A minor") == 0.0
    assert midi_metrics.groove_consistency(_good_drums(), BARS) > 0.9
    assert 0.0 <= midi_metrics.empty_beat_rate(_good_bass(), BARS) <= 1.0
    assert midi_metrics.polyphony(_good_chords()) >= 3.0


def test_register_separation_global():
    parts = {"bass": _good_bass(), "chords": _good_chords()}
    g = midi_metrics.score_global(parts, _P, BARS)
    assert g["score"] > 0.9
    muddy = {"bass": _good_bass(),
             "chords": [{**n, "pitch": n["pitch"] - 24} for n in _good_chords()]}
    assert midi_metrics.score_global(muddy, _P, BARS)["score"] < g["score"]


# --- groove ------------------------------------------------------------------
def test_groove_deterministic_and_bounded():
    a = groove.apply_groove(_good_drums(), "boom bap", "drums", seed=1)
    b = groove.apply_groove(_good_drums(), "boom bap", "drums", seed=1)
    assert a == b, "groove must be deterministic for identical inputs"
    for orig, g in zip(sorted(_good_drums(), key=lambda x: (x["start_time"], x["pitch"])), a):
        assert abs(g["start_time"] - orig["start_time"]) < 0.12
        assert 1 <= g["velocity"] <= 127
    vels = [n["velocity"] for n in a]
    assert len(set(vels)) > 3, "groove should vary velocities"


# --- loop engine --------------------------------------------------------------
def _fresh_engine(**cfg):
    eng = SandboxEngine.start("boom bap", ["drums", "bass", "chords", "melody"],
                              bars=BARS, autonomy=cfg.pop("autonomy", "full"), **cfg)
    return eng


def _full_parts():
    return {"drums": _good_drums(), "bass": _good_bass(),
            "chords": _good_chords(), "melody": _good_melody()}


def test_checkpoint_gates_submit():
    eng = SandboxEngine.start("boom bap", ["drums"], bars=BARS, autonomy="checkpoint")
    r = eng.submit(parts={"drums": _good_drums()})
    assert "checkpoint" in r and r["checkpoint"]["type"] == "direction"
    cp = r["checkpoint"]["id"]
    eng.respond_checkpoint(cp, "proceed as planned")
    r2 = eng.submit(parts={"drums": _good_drums()})
    assert "checkpoint" not in r2 or r2.get("verdict"), "submit should proceed after answer"


def test_plan_then_briefs_embed_chords():
    eng = _fresh_engine()
    assert "plan_brief" in eng.briefs()
    r = eng.submit(plan={"key": "A minor", "progression": "i-iv-v-iv",
                         "motif": "call and answer", "arrangement": "4-bar loop"})
    assert "plan_accepted" in r
    eng.submit(parts=_full_parts())
    briefs = eng.briefs()["role_briefs"]
    assert "chord_track" in briefs["melody"], "melody brief must embed the chord timeline"


def test_pass_verdict_and_done():
    eng = _fresh_engine(pass_threshold=0.5)
    r = eng.submit(parts=_full_parts())
    assert r["verdict"] == "pass", r["scores"]
    assert eng.s.state == "DONE"
    assert "checkpoint" in r and r["checkpoint"]["type"] == "approve_commit"


def test_budget_verdict():
    eng = _fresh_engine(pass_threshold=0.999, max_iterations=2)
    eng.submit(parts=_full_parts())
    r = eng.submit(parts=_full_parts())
    assert r["verdict"] == "budget"


def test_plateau_and_best_iteration_wins():
    eng = _fresh_engine(pass_threshold=0.999, max_iterations=10)
    eng.submit(parts=_full_parts())                       # decent
    eng.submit(parts={**_full_parts(), "bass": _bad_bass()})   # worse
    r = eng.submit(parts={**_full_parts(), "bass": _bad_bass()})
    assert r["verdict"] in ("plateau", "budget")
    best = eng.s.best_iteration()
    assert best.index == 1, "argmax iteration must win, not the last one"


def test_partial_submit_merges():
    eng = _fresh_engine(pass_threshold=0.999, max_iterations=10)
    eng.submit(parts=_full_parts())
    r = eng.submit(parts={"bass": _good_bass()})  # only bass resubmitted
    assert set(eng.s.iterations[-1].notes) == {"drums", "bass", "chords", "melody"}
    assert r["scores"]["per_role"].get("drums", 0) > 0, "unrevised roles must persist"


def test_persistence_roundtrip():
    eng = _fresh_engine(pass_threshold=0.5)
    eng.submit(parts=_full_parts())
    loaded = SandboxSession.load(eng.s.id)
    assert loaded.state == "DONE" and loaded.best_iteration().index == 1


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    try:
        for fn in fns:
            fn()
            print(f"  PASS  {fn.__name__}")
        print(f"\n{len(fns)}/{len(fns)} tests passed.")
    finally:
        # clean test sessions
        if SESSIONS_DIR.exists():
            for p in SESSIONS_DIR.iterdir():
                if p.name.startswith("sbx_"):
                    shutil.rmtree(p, ignore_errors=True)


if __name__ == "__main__":
    _run_all()
