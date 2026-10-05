"""
live_profile.py — black-box profile of Ableton Live's audio behaviour (Phase 0).

Plays known test signals through Live and measures what comes out of the master:
pan law, playback neutrality (gain / latency / null), clip-edge fade length and
sample-rate-conversion quality. Pure observation of a licensed copy's output —
no Live code is read. The result is the "Live-compatible" reference profile in
docs/agentic_daw_research.md section 3.

Reuses stem_ablation.render_resample for capture (armed audio track recording
the master "Resampling" bus over one real-time pass) and measure.py for analysis.

RUN ON AN EMPTY SCRATCH SET ONLY. It records the master, so anything else
playing contaminates the measurement, and it creates/deletes tracks and moves
the transport. It refuses to run on a set with more than a template's worth of
tracks unless --force is given. Needs the Remote Script commands
create_arrangement_audio_clip and set_clip_warping (added alongside this file).

Run:  python daw_bench/live_profile.py --out sandbox_sessions/live_profile
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import soundfile as sf

_ROOT = Path(__file__).resolve().parent.parent
for _p in (str(Path(__file__).resolve().parent), str(_ROOT / "harness"), str(_ROOT / "sandbox")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fidelity  # noqa: E402
import measure  # noqa: E402
import signals  # noqa: E402
import stem_ablation as sa  # noqa: E402
from live_client import LiveClient, LiveError  # noqa: E402

SRC_TRACK = "DAWBENCH_SRC"
TEMPO = 120.0                 # 4/4 at 120 BPM: one bar = 2 s, one beat = 0.5 s
MAX_SCRATCH_TRACKS = 4        # Live's default template
MASTER = sa.NodeChain(ref=-1, name="Master", kind="master")


class ProfileError(Exception):
    pass


def _capture_master(client, out_wav: Path, seconds: float) -> Tuple[np.ndarray, int]:
    """Record `seconds` of master output from position 0. Returns (stereo, sr)."""
    bars = int(np.ceil(seconds / 2.0))             # one bar = 2 s at TEMPO
    sa.render_resample(client, MASTER, out_wav, bars=bars, start_bar=1)
    return sf.read(str(out_wav), dtype="float64", always_2d=True)


def _clear_clips(client, track_index: int) -> None:
    count = int(client.send("get_arrangement_clips", {"track_index": track_index}).get("clip_count", 0))
    for _ in range(count):
        client.send("delete_arrangement_clip", {"track_index": track_index, "clip_index": 0})


def _place(client, track_index: int, wav: str, position_beats: float = 0.0) -> None:
    """Replace the source track's content with one unwarped clip of `wav`."""
    _clear_clips(client, track_index)
    try:
        res = client.send("create_arrangement_audio_clip",
                          {"track_index": track_index, "file_path": wav, "position": position_beats})
        client.send("set_clip_warping", {"track_index": track_index,
                                         "clip_index": res.get("clip_index", 0), "warping": False})
    except LiveError as e:
        if "unknown command" in str(e).lower():
            raise ProfileError(
                f"Live's Remote Script is out of date ({e}). Merge "
                "harness/AbletonMCP_Extended/__init__.py into the installed copy in the "
                "Live app bundle (it has diverged — do not overwrite), then restart Live.") from e
        raise


# --- probes -----------------------------------------------------------------
def project_sample_rate(client, work: Path) -> int:
    """Live's API does not expose the project rate; a recording's header does."""
    _, sr = _capture_master(client, work / "sr_probe.wav", 1.0)
    return int(sr)


def probe_pan(client, track_index: int, work: Path, sr: int, n_positions: int = 9,
              freq: float = 1000.0, level_db: float = -12.0) -> Dict[str, Any]:
    wav = signals.write_wav(work / "pan_src.wav",
                            signals.fade(signals.sine(freq, 3.0, sr, level_db), sr), sr)
    _place(client, track_index, wav)
    positions = [round(float(p), 4) for p in np.linspace(-1.0, 1.0, n_positions)]
    left, right = [], []
    try:
        for i, p in enumerate(positions):
            client.send("set_track_pan", {"track_index": track_index, "pan": p})
            cap, cap_sr = _capture_master(client, work / f"pan_{i:02d}.wav", 3.0)
            steady = cap[int(0.25 * cap_sr): int(2.75 * cap_sr)]   # inside the 3 s tone
            l_db, r_db = measure.stereo_tone_gains_db(steady, cap_sr, freq, level_db)
            left.append(l_db)
            right.append(r_db)
    finally:
        client.send("set_track_pan", {"track_index": track_index, "pan": 0.0})
    return {"positions": positions, "left_db": left, "right_db": right,
            "fit": measure.fit_pan_law(positions, left, right)}


def probe_unity(client, track_index: int, work: Path, sr: int) -> Dict[str, Any]:
    """Unwarped clip at the project rate, pan centre, faders untouched: is
    playback a pure delay? Reports gain, latency and how deeply it nulls."""
    src = signals.fade(signals.noise(3.0, sr, level_db=-20.0, seed=7), sr)
    _place(client, track_index, signals.write_wav(work / "unity_src.wav", src, sr))
    cap, cap_sr = _capture_master(client, work / "unity.wav", 3.0)
    out = cap[:, 0]
    lag = measure.latency_samples(src, out, cap_sr, max_lag_s=1.0)
    aligned = out[lag:] if lag >= 0 else np.concatenate([np.zeros(-lag), out])
    gain_db, matched = fidelity.gain_match(src, aligned[:len(src)])
    return {"latency_samples": int(lag), "gain_db": round(gain_db, 4),
            "residual_dbfs": round(measure.residual_dbfs(src, matched), 2),
            "source_rms_dbfs": -20.0}


def probe_edge_fade(client, track_index: int, work: Path, sr: int) -> Dict[str, Any]:
    """Hard-edged tone placed mid-capture: how long is the fade Live adds? (Depends
    on the user's 'Create Fades on Clip Edges' preference, which the API can't read.)"""
    wav = signals.write_wav(work / "fade_src.wav", signals.sine(5000.0, 1.0, sr, -6.0), sr)
    _place(client, track_index, wav, position_beats=2.0)            # starts at 1.0 s
    cap, cap_sr = _capture_master(client, work / "fade.wav", 3.0)
    start = int(0.5 * cap_sr)
    return {"fade_in_ms": round(measure.edge_fade_ms(cap[start: int(1.9 * cap_sr), 0], cap_sr, 5000.0), 3)}


def probe_src(client, track_index: int, work: Path, sr: int) -> Dict[str, Any]:
    """Sweep stored at twice the project rate, so Live must downsample it in real
    time: passband flatness and how much above-Nyquist content folds back."""
    file_sr = 2 * sr
    sweep = dict(f_start=20.0, f_end=float(sr), seconds=8.0, level_db=-6.0)
    src = signals.linear_sweep(sweep["f_start"], sweep["f_end"], sweep["seconds"],
                               file_sr, sweep["level_db"])
    _place(client, track_index, signals.write_wav(work / "src_sweep.wav", src, file_sr))
    cap, cap_sr = _capture_master(client, work / "src.wav", 9.0)
    out = cap[:, 0]
    # align on the part of the sweep that survives conversion (below 0.45 * sr)
    ref = signals.linear_sweep(sweep["f_start"], sweep["f_end"], sweep["seconds"],
                               cap_sr, sweep["level_db"])
    ref[int(0.45 * sweep["seconds"] * cap_sr):] = 0.0
    lag = measure.latency_samples(ref, out, cap_sr, max_lag_s=1.0)
    result = measure.analyse_src_sweep(out[max(lag, 0):], cap_sr, **sweep)
    result.update({"file_sr": file_sr, "project_sr": cap_sr})
    return result


# --- orchestration -----------------------------------------------------------
def _require_scratch_set(client, track_count: int) -> None:
    """The profile records the master and edits tracks, so refuse anything that
    looks like real work: more tracks than a template, or any arrangement clip."""
    problem = f"{track_count} tracks open" if track_count > MAX_SCRATCH_TRACKS else None
    for i in range(track_count if problem is None else 0):
        try:
            if int(client.send("get_arrangement_clips", {"track_index": i}).get("clip_count", 0)):
                problem = f"track {i} has arrangement clips"
                break
        except LiveError:
            continue
    if problem:
        raise ProfileError(f"{problem} — this looks like a real set. Open an empty scratch "
                           f"set, or pass --force.")


def run_profile(client, out_dir: Path, force: bool = False) -> Dict[str, Any]:
    info = client.send("get_session_info")
    if not force:
        _require_scratch_set(client, int(info.get("track_count", 0)))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    orig_tempo = info.get("tempo")
    track_index = None
    profile: Dict[str, Any] = {}
    try:
        client.send("set_tempo", {"tempo": TEMPO})
        track_index = int(client.send("create_audio_track", {"index": -1})["index"])
        client.send("set_track_name", {"track_index": track_index, "name": SRC_TRACK})
        sr = project_sample_rate(client, out_dir)
        profile["project_sr"] = sr
        for name, probe in (("pan", probe_pan), ("unity", probe_unity),
                            ("edge_fade", probe_edge_fade), ("src", probe_src)):
            try:
                profile[name] = probe(client, track_index, out_dir, sr)
            except ProfileError:
                raise
            except Exception as e:  # noqa: BLE001 — one probe failing never loses the others
                profile[name] = {"error": f"{type(e).__name__}: {e}"}
    finally:
        if track_index is not None:
            try:
                client.send("delete_track", {"track_index": track_index})
            except LiveError:
                pass
        if orig_tempo is not None:
            try:
                client.send("set_tempo", {"tempo": orig_tempo})
            except LiveError:
                pass
    (out_dir / "live_profile.json").write_text(json.dumps(profile, indent=1))
    return profile


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=str(_ROOT / "sandbox_sessions" / "live_profile"))
    ap.add_argument("--force", action="store_true", help="run even if the set has many tracks")
    args = ap.parse_args(argv)
    try:
        with LiveClient(timeout=45) as client:
            profile = run_profile(client, Path(args.out), force=args.force)
    except (ProfileError, LiveError) as e:
        print(f"live profile failed: {e}")
        return 2
    print(json.dumps(profile, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
