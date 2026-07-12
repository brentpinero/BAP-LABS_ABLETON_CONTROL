"""
calibrate_impulse.py — CONTROLLED-IMPULSE latency probe (FRAME-BASED DIAGNOSTIC).

Plays a HARD-ON-GRID click (MIDI notes exactly on integer beats) on a soloed track and
measures how far its onset lands from the beat in the 25 Hz perception frame stream.

STATUS / LIMITATION (measured live): this frame-based version CANNOT resolve the latency
reliably. The master RMS uses `average~ 2048` (~46 ms window), which smears each click
into a ~0.5-beat bump — so there's no sharp onset, and 25 Hz frames + 33 ms snapshots cap
timing at ~40 ms. Live runs scattered +2 / -29 / +56 / +71 ms with ±130 ms within-run
spread. It is kept as a DIAGNOSTIC (and proves the frame pipeline's ~1-frame temporal
floor). The precise measurement uses the source-side sharp-onset tap (`/mix/onset`, a
short-window 200 Hz envelope on the master) — see the onset-stream path.

The click IS placed exactly on the grid (no musical kick-placement confound like the
passive calibrate_latency.py), so the residual is pure pipeline timing — the limit is
resolution, not confound.

The reference clock is the dead-reckoned beat grid (validated to ~0.000 beat error vs
wall-clock), so: a click note on integer beat K plays at K's wall time; it shows up in a
frame whose dead-reckoned beat reads K + latency*bpm/60. Thus

    audio_latency_s  =  current_latency + median(onset_phase) * 60/bpm

Flow (all via the Remote Script; NON-DESTRUCTIVE — creates then deletes a CAL track, and
SOLOS it briefly so the click is isolated on the master for a clean onset):
  1. create MIDI track "CAL_IMPULSE" + load Operator (any instrument; we detect the attack)
  2. write a clip with a short note on every beat, solo, start transport, fire (loops on grid)
  3. the ears daemon (must be recording: PERCEPTION_RECORD_TRAJECTORIES=1) banks frames
  4. detect master-RMS onsets in the fire window, phase vs nearest beat -> latency
  5. cleanup: stop, unsolo, delete the CAL track
  6. --apply writes sandbox_sessions/calibration/perception_latency.json (config auto-loads it)

Run:  python calibrate_impulse.py            # measure + print (dry-run)
      python calibrate_impulse.py --apply    # measure, then write the calibration file
"""

from __future__ import annotations

import glob
import sys
import time
from pathlib import Path

from perception_config import cfg
from perception_recorder import iter_trajectory
from calibrate_latency import residual_latency_s, transient_beats, write_calibration

_ROOT = Path(__file__).resolve().parent.parent
CAL_NAME = "CAL_IMPULSE"


def click_notes(n_beats: int, pitch: int = 72, dur: float = 0.1, vel: int = 110):
    """A short note EXACTLY on each integer beat 0..n_beats-1 (hard on-grid)."""
    return [{"pitch": pitch, "start_time": float(k), "duration": dur, "velocity": vel}
            for k in range(n_beats)]


def _find_instrument(c, prefer=("Operator", "Drift", "Analog", "Wavetable", "Drum Sampler")):
    """A loadable core instrument from the `instruments` browser root (fast-attack synth
    for a clean note-on onset). find_uri only walks user_library, so it can't find these."""
    try:
        items = c.send("get_browser_items_at_path", {"path": "instruments"}).get("items", [])
    except Exception:
        return None, None
    loadable = {it.get("name"): it for it in items if it.get("is_loadable") and it.get("uri")}
    for name in prefer:
        if name in loadable:
            return loadable[name]["uri"], name
    for it in items:                                    # fallback: any loadable instrument
        if it.get("is_loadable") and it.get("uri"):
            return it["uri"], it.get("name")
    return None, None


def latency_from_steps(steps, role: str = "master", current_latency: float = 0.0) -> dict:
    """Pure: onsets + residual + corrected latency from a list of recorded steps. Also
    reports the WITHIN-run phase spread — tight spread + a per-run-varying center is the
    signature of a clip-launch-phase offset (not measurement noise)."""
    import statistics
    from calibrate_latency import phase
    steps = [s for s in steps if s.get("frame", {}).get("playing")]
    bpm = next((s["frame"].get("bpm", 0.0) for s in steps if s.get("frame")), 0.0)
    onsets = transient_beats(steps, role)
    phases = [phase(b) for b in onsets]
    residual = residual_latency_s(onsets, bpm)
    spread_s = (statistics.pstdev(phases) * 60.0 / bpm) if len(phases) > 1 and bpm else 0.0
    return {"bpm": bpm, "frames": len(steps), "onsets": len(onsets), "residual_s": residual,
            "spread_s": spread_s, "new_latency_s": max(0.0, current_latency + residual)}


def _window_steps(session, t0: float, t1: float):
    return [s for s in iter_trajectory(session) if t0 <= s.get("t_wall", 0.0) <= t1]


def _newest_session():
    d = sorted(glob.glob(str(_ROOT / "sandbox_sessions" / "trajectories" / "sess_*")))
    return d[-1] if d else None


def run(record_s: float = 16.0, n_beats: int = 8, apply: bool = False) -> int:
    from live_client import LiveClient

    session = _newest_session()
    if not session:
        print("No recording session. Start the ears daemon with recording on first:\n"
              "  PERCEPTION_RECORD_TRAJECTORIES=1 python run_harness.py ears")
        return 2

    idx = None
    try:
        with LiveClient(timeout=45) as c:
            c.send("create_midi_track", {"index": -1}); time.sleep(0.4)
            idx = int(c.send("get_session_info").get("track_count", 0)) - 1
            c.send("set_track_name", {"track_index": idx, "name": CAL_NAME})
            uri, iname = _find_instrument(c)
            if not uri:
                print("Couldn't find a core instrument in the browser.")
                return 3
            c.send("load_browser_item", {"track_index": idx, "item_uri": uri}); time.sleep(1.0)
            print(f"loaded {iname} on CAL_IMPULSE")
            c.send("create_clip", {"track_index": idx, "clip_index": 0, "length": float(n_beats)})
            time.sleep(0.3)
            c.send("add_notes_to_clip", {"track_index": idx, "clip_index": 0,
                                         "notes": click_notes(n_beats)})
            c.send("set_track_solo", {"track_index": idx, "solo": True})   # isolate the click
            c.send("start_playback")
            fire_t = time.time()
            c.send("fire_clip", {"track_index": idx, "clip_index": 0})
            print(f"CAL_IMPULSE firing (soloed) on track {idx} — recording {record_s:.0f}s "
                  f"of on-grid clicks...")
            time.sleep(record_s)
            c.send("stop_clip", {"track_index": idx, "clip_index": 0})
            c.send("set_track_solo", {"track_index": idx, "solo": False})
    finally:
        # always restore: unsolo (belt-and-suspenders) + delete the CAL track
        try:
            with LiveClient(timeout=20) as c:
                if idx is not None:
                    c.send("set_track_solo", {"track_index": idx, "solo": False})
                    c.send("delete_track", {"track_index": idx})
                    print(f"cleaned up: deleted CAL_IMPULSE (track {idx}), solo restored")
        except Exception as e:
            print(f"  cleanup warning ({e}); remove the CAL_IMPULSE track manually if it remains")

    time.sleep(float(cfg("trajectory_flush_s")) + 0.5)      # let the recorder flush the window
    steps = _window_steps(session, fire_t + 2.5, fire_t + record_s)   # skip launch-quantize settle
    # debug dump: the raw master signal so we can SEE the click structure / onset quality
    import json as _json
    dbg = [{"t": round(s["t_wall"] - fire_t, 3), "beat": round(s["frame"]["bar"] * 4 + s["frame"]["beat"], 3),
            "rms": round(s["frame"]["role_state"].get("master", {}).get("rms_db", -120), 1)}
           for s in steps if s["frame"].get("playing")]
    (_ROOT / "sandbox_sessions" / "calibration").mkdir(parents=True, exist_ok=True)
    (_ROOT / "sandbox_sessions" / "calibration" / "impulse_debug.json").write_text(_json.dumps(dbg))
    cur = float(cfg("audio_latency_s"))
    r = latency_from_steps(steps, current_latency=cur)
    print(f"  {r['frames']} frames, {r['onsets']} on-grid click onsets @ {r['bpm']:.1f} BPM")
    if r["onsets"] < 8:
        print("  too few clean onsets — is the daemon recording, and is the click audible? "
              "Re-run; ensure PERCEPTION_RECORD_TRAJECTORIES=1.")
        return 4
    print(f"  measured pipeline latency: current {cur*1000:.0f} ms + residual "
          f"{r['residual_s']*1000:+.0f} ms  ->  {r['new_latency_s']*1000:.0f} ms "
          f"(within-run spread ±{r['spread_s']*1000:.0f} ms)")
    if apply:
        p = write_calibration(r["new_latency_s"])
        print(f"  wrote {p} — restart the ears daemon to apply, then re-run to confirm ~0 residual.")
    else:
        print("  dry-run. Re-run with --apply to write the calibration file.")
    return 0


def main(argv) -> int:
    return run(apply="--apply" in argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
