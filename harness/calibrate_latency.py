"""
calibrate_latency.py — measure the audio->frame pipeline latency and write it to the
perception calibration file, so the emitter aligns each frame's transport to the audio
instant the frame actually carries (perception_config.audio_latency_s).

METHOD (self-referential — uses the dead-reckoned beat grid as the reference clock):
record a BEAT-LOCKED loop (a kick on the beat) with the trajectory recorder, then measure
how far the low-band (kick) energy ONSETS land from the nearest integer beat. That residual
phase IS the pipeline latency: if the frame clock runs L seconds ahead of the audio, a kick
whose audio is on beat 0 shows up in a frame that reads beat = L * bpm/60. So

    audio_latency_s  +=  median(onset_phase_beats) * 60 / bpm

(the current latency is already folded into the recorded beats, so this converges — re-run
after --apply and the residual should be ~0).

Run (after recording a few bars of a beat-locked loop; the ears daemon records when
PERCEPTION_RECORD_TRAJECTORIES=1):
    python calibrate_latency.py                 # analyze the newest recorded session
    python calibrate_latency.py <session_dir>   # a specific one
    python calibrate_latency.py <dir> --apply   # also write the calibration file
"""

from __future__ import annotations

import glob
import json
import statistics
import sys
from pathlib import Path

from perception_config import cfg
from perception_recorder import load_trajectory

_ROOT = Path(__file__).resolve().parent.parent
CALIB = _ROOT / "sandbox_sessions" / "calibration" / "perception_latency.json"
LOW_ROLES = ("drums", "master")                # where a kick's low-band energy shows up


def phase(abs_beat: float) -> float:
    """Signed distance to the nearest integer beat, in [-0.5, 0.5)."""
    return abs_beat - round(abs_beat)


def energy_series(steps, roles=LOW_ROLES):
    """(t_wall, absolute_beat, low_band_linear_energy) per playing step."""
    out = []
    for s in steps:
        f = s.get("frame", {})
        if not f.get("playing", s.get("playing", False)):
            continue
        rs = f.get("role_state", {})
        e = 0.0
        for r in roles:
            st = rs.get(r)
            if not st:
                continue
            bands = st.get("bands") or []
            low = (bands[0] if len(bands) > 0 else 0.0) + (bands[1] if len(bands) > 1 else 0.0)
            rms = st.get("rms_db", -120.0)
            lin = 10.0 ** (rms / 20.0) if rms > -119.0 else 0.0
            e += lin * low
        abs_beat = f.get("bar", 0) * f.get("beats_per_bar", 4) + f.get("beat", 0.0)
        out.append((s.get("t_wall", 0.0), abs_beat, e))
    return out


def detect_onsets(series, k: float = 1.8, refractory_beats: float = 0.3):
    """Absolute-beat positions of low-band energy rising edges (kick hits). A rising edge
    = energy crosses above k * median(nonzero energy); refractory suppresses double-triggers."""
    if len(series) < 2:
        return []
    nz = [e for _, _, e in series if e > 0]
    if not nz:
        return []
    thr = k * statistics.median(nz)
    onsets, last = [], -1e9
    for i in range(1, len(series)):
        _, b, e = series[i]
        if e >= thr > series[i - 1][2] and (b - last) >= refractory_beats:
            onsets.append(b)
            last = b
    return onsets


def residual_latency_s(onset_beats, bpm: float) -> float:
    """Median onset phase (beats from the nearest beat) converted to seconds."""
    if not onset_beats or bpm <= 0:
        return 0.0
    return statistics.median(phase(b) for b in onset_beats) * 60.0 / bpm


def calibrate(session, roles=LOW_ROLES, current_latency=None) -> dict:
    """Analyze a recorded session -> the corrected audio_latency_s (and diagnostics)."""
    traj = load_trajectory(session)
    steps = traj["steps"]
    bpm = next((s["frame"].get("bpm", 0.0) for s in steps if s.get("frame")), 0.0)
    series = energy_series(steps, roles)
    onsets = detect_onsets(series)
    cur = float(cfg("audio_latency_s")) if current_latency is None else float(current_latency)
    residual = residual_latency_s(onsets, bpm)
    new_latency = max(0.0, cur + residual)
    return {
        "session": str(session), "bpm": bpm, "steps": len(steps),
        "playing_steps": len(series), "onsets": len(onsets),
        "current_latency_s": round(cur, 4), "residual_s": round(residual, 4),
        "new_latency_s": round(new_latency, 4),
    }


def write_calibration(new_latency_s: float) -> Path:
    CALIB.parent.mkdir(parents=True, exist_ok=True)
    CALIB.write_text(json.dumps({"audio_latency_s": round(float(new_latency_s), 4)}, indent=1))
    return CALIB


def _newest_session():
    dirs = sorted(glob.glob(str(_ROOT / "sandbox_sessions" / "trajectories" / "sess_*")))
    return dirs[-1] if dirs else None


def main(argv) -> int:
    apply = "--apply" in argv
    args = [a for a in argv if not a.startswith("--")]
    session = args[0] if args else _newest_session()
    if not session or not Path(session).exists():
        print("no recorded session found. Record a beat-locked loop first: "
              "PERCEPTION_RECORD_TRAJECTORIES=1 python run_harness.py ears")
        return 2
    r = calibrate(session)
    print(f"session {Path(r['session']).name}: {r['playing_steps']} playing frames, "
          f"{r['onsets']} kick onsets @ {r['bpm']:.1f} BPM")
    if r["onsets"] < 4:
        print("  too few onsets to trust — play a clearer 4-on-floor / kick loop and re-record.")
    print(f"  current latency {r['current_latency_s']*1000:.0f} ms  +  residual "
          f"{r['residual_s']*1000:+.0f} ms  ->  {r['new_latency_s']*1000:.0f} ms")
    if apply:
        p = write_calibration(r["new_latency_s"])
        print(f"  wrote {p} (restart the ears daemon to pick it up; re-run to verify ~0 residual)")
    else:
        print("  dry-run. Re-run with --apply to write the calibration file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
