"""
tracktion_target.py — Tracktion Engine as a profile.py target (engine candidate).

Each probe becomes one offline render by `tracktion_probe`, a small C++ console
tool (daw_bench/tracktion_probe/) that reads a JSON job — one unwarped audio
clip at a beat position on a panned track, tempo 120 — and renders the master
to a 32-bit float WAV. Same probes as Live and the Python reference engine, so
the three profiles are directly comparable.

Build once:  cmake -S daw_bench/tracktion_probe -B build/tracktion_probe
             -DTRACKTION_ENGINE_DIR=~/Documents/third_party/tracktion_engine
             cmake --build build/tracktion_probe --config Release
Run:         python daw_bench/tracktion_target.py --out sandbox_sessions/tracktion_profile
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))

import profile  # noqa: E402

_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BINARY = _ROOT / "build" / "tracktion_probe" / "tracktion_probe"


def find_binary() -> Path | None:
    for cand in (os.environ.get("TRACKTION_PROBE"), DEFAULT_BINARY,
                 _ROOT / "build" / "tracktion_probe" / "tracktion_probe_artefacts" / "Release" / "tracktion_probe"):
        if cand and Path(cand).exists():
            return Path(cand)
    return None


class TracktionTarget:
    """profile.py target: one render of `tracktion_probe` per play()."""

    def __init__(self, sr: int = 48000, binary: Path | None = None, keep_dir: Path | None = None):
        self.sr = int(sr)
        self.binary = Path(binary) if binary else find_binary()
        if self.binary is None:
            raise FileNotFoundError("tracktion_probe binary not built; see tracktion_target.py docstring")
        self.work = Path(keep_dir) if keep_dir else Path(tempfile.mkdtemp(prefix="tracktion_probe_"))
        self.work.mkdir(parents=True, exist_ok=True)
        self.takes = 0

    def play(self, wav: str, position_beats: float, pan: float, seconds: float) -> np.ndarray:
        self.takes += 1
        out = self.work / f"take_{self.takes:03d}.wav"
        out.unlink(missing_ok=True)                        # Tracktion's writer appends to an existing file
        job = {"sample_rate": self.sr, "tempo": profile.TEMPO, "seconds": float(seconds),
               "output": str(out),
               "clips": [{"file": str(wav), "position_beats": float(position_beats),
                          "pan": float(pan)}]}
        job_path = self.work / f"job_{self.takes:03d}.json"
        job_path.write_text(json.dumps(job))
        run = subprocess.run([str(self.binary), str(job_path)], capture_output=True, text=True,
                             timeout=120)
        if run.returncode != 0 or not out.exists():
            raise RuntimeError(f"tracktion_probe failed ({run.returncode}): {run.stderr.strip()[-800:]}")
        audio, sr = sf.read(str(out), dtype="float64", always_2d=True)
        if sr != self.sr:
            raise RuntimeError(f"tracktion_probe rendered at {sr} Hz, expected {self.sr}")
        return audio


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Profile Tracktion Engine with the Phase 0 probes.")
    ap.add_argument("--out", default=str(_ROOT / "sandbox_sessions" / "tracktion_profile"))
    ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--binary", default=None)
    args = ap.parse_args(argv)
    try:
        target = TracktionTarget(args.sr, args.binary, keep_dir=Path(args.out) / "takes")
    except FileNotFoundError as e:
        print(e)
        return 2
    prof = profile.run_probes(target, Path(args.out), "tracktion_profile")
    print(json.dumps(prof, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
