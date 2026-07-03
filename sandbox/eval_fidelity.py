"""
eval_fidelity.py — the calibration CLI: measure headless-vs-Ableton parity per plugin.

Run EXPLICITLY when you're not working in Live (it drives your open set):
    python run_harness.py calibrate --plugin Serum --project-dir "<open project folder>"
    python run_harness.py calibrate --batch plugins.json --project-dir ...

For each plugin: renders a deterministic test pattern headless (pedalboard) AND
in Live (automated Freeze), aligns + null-tests, prints the verdict, stores it
in the fidelity registry, and archives both wavs for A/B audition in the
review UI. Stock Ableton devices can be registered as live_only via --stock.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
for p in (str(_ROOT / "sandbox"), str(_ROOT / "harness"), str(_ROOT / "daw_translation")):
    if p not in sys.path:
        sys.path.insert(0, p)

import fidelity  # noqa: E402

BPM = 100.0
BARS = 4


def test_pattern() -> list[dict]:
    """Deterministic 4-bar pattern: pitch range sweep, chord, velocity ramp, release tail."""
    notes = []
    # bar 1: chromatic-ish range sweep
    for i, pitch in enumerate((36, 48, 60, 72, 84, 96)):
        notes.append({"pitch": pitch, "start_time": i * 0.5, "duration": 0.4,
                      "velocity": 100})
    # bar 2: velocity ramp on one pitch
    for i in range(8):
        notes.append({"pitch": 60, "start_time": 4 + i * 0.5, "duration": 0.4,
                      "velocity": 20 + i * 14})
    # bar 3: polyphony (chord) + sustained release into bar 4
    for p in (48, 55, 60, 64):
        notes.append({"pitch": p, "start_time": 8.0, "duration": 3.0, "velocity": 96})
    notes.append({"pitch": 52, "start_time": 12.0, "duration": 2.0, "velocity": 110})
    return notes


def render_headless(plugin_path: str, out: Path, params: dict | None,
                    notes: list[dict], sr: int = 44100) -> None:
    notes_path = out.with_suffix(".notes.json")
    notes_path.write_text(json.dumps({"notes": notes, "bars": BARS}))
    kind = "au" if plugin_path.endswith(".component") else "vst"
    cmd = [sys.executable, str(_ROOT / "daw_translation" / "render_worker.py"),
           "--midi", str(notes_path), "--bpm", str(BPM),
           "--instrument", f"{kind}:{plugin_path}", "--out", str(out), "--sr", str(sr)]
    if params:
        params_path = out.with_suffix(".params.json")
        params_path.write_text(json.dumps(params))
        cmd += ["--params", str(params_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise RuntimeError(f"headless render failed: {proc.stderr[-400:]}")


def calibrate_plugin(plugin: str, plugin_path: str, project_dir: str,
                     params: dict | None = None, preset: str = "") -> dict:
    from live_freeze import freeze_render  # imported late: needs Live only here
    archive = fidelity.FIDELITY_AUDIO_DIR / fidelity.Registry.key(plugin, preset, params)
    archive.mkdir(parents=True, exist_ok=True)
    notes = test_pattern()

    print(f"[calibrate] {plugin}: headless render...")
    headless_wav = archive / "headless.wav"
    render_headless(plugin_path, headless_wav, params, notes)

    print(f"[calibrate] {plugin}: Live freeze render (driving your open set)...")
    live_wav = freeze_render(notes, BPM, BARS, plugin, project_dir,
                             params=params, out_path=archive / "live.wav")

    print(f"[calibrate] {plugin}: comparing...")
    results = fidelity.compare(headless_wav, live_wav)
    reg = fidelity.Registry()
    key = reg.record(plugin, plugin_path, Path(plugin_path).suffix.lstrip("."),
                     results, preset=preset, params=params,
                     audio_pair={"headless": str(headless_wav), "live": str(live_wav)})
    print(f"\n=== {plugin} ===")
    print(f"  null depth : {results['null_depth_db']} dB  ({results['label']})")
    print(f"  latency    : {results['latency_samples']} samples")
    print(f"  gain delta : {results['gain_delta_db']} dB | LUFS delta: {results['lufs_delta']}")
    print(f"  bands (dB) : {results['band_diff_db']}")
    print(f"  registry   : {key} | A/B pair archived -> {archive}")
    print("  guide: >=40 dB near-identical | 20-40 minor state/PDC diff | <20 state transfer diverged")
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Headless-vs-Ableton fidelity calibration")
    ap.add_argument("--plugin", help="plugin display name to search in Live's browser (e.g. Serum)")
    ap.add_argument("--plugin-path", help="headless plugin path (default: /Library/Audio/Plug-Ins/VST3/<plugin>.vst3)")
    ap.add_argument("--params", help="JSON file of named param values (captured from Live)")
    ap.add_argument("--preset", default="", help="preset label for the registry key")
    ap.add_argument("--project-dir", required=False,
                    help="the OPEN Live project folder (where Samples/Processed/Freeze lives)")
    ap.add_argument("--batch", help="JSON file: [{plugin, plugin_path, params?, preset?}]")
    ap.add_argument("--stock", help="register a stock Ableton device as live_only (no render)")
    args = ap.parse_args(argv)

    if args.stock:
        key = fidelity.Registry().record_live_only(args.stock)
        print(f"registered stock device as live_only: {key}")
        return 0

    if not args.project_dir:
        ap.error("--project-dir is required for calibration (the open Live project folder)")

    print("=" * 74)
    print(" CALIBRATION will drive your OPEN Ableton Live set (temp tracks, freeze,")
    print(" undo). Don't work in Live until it finishes.")
    print("=" * 74)

    jobs = []
    if args.batch:
        jobs = json.loads(Path(args.batch).read_text())
    elif args.plugin:
        jobs = [{"plugin": args.plugin, "plugin_path": args.plugin_path or
                 f"/Library/Audio/Plug-Ins/VST3/{args.plugin}.vst3",
                 "params": json.loads(Path(args.params).read_text()) if args.params else None,
                 "preset": args.preset}]
    else:
        ap.error("give --plugin or --batch (or --stock)")

    failures = 0
    for job in jobs:
        try:
            calibrate_plugin(job["plugin"], job["plugin_path"], args.project_dir,
                             params=job.get("params"), preset=job.get("preset", ""))
        except Exception as e:  # noqa: BLE001 — keep sweeping the batch
            failures += 1
            print(f"[calibrate] {job['plugin']} FAILED: {e}")
    print(f"\ndone: {len(jobs) - failures}/{len(jobs)} calibrated")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
