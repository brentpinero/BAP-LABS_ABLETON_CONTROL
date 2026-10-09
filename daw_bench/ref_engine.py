"""
ref_engine.py — the audio-quality spec as an executable reference (Phase 0).

A deliberately tiny Python engine that does exactly what docs/agentic_daw_research.md
section 3 asks for, and nothing else: 64-bit float throughout, a selectable pan
law (centre-cut constant power by default, Live's 0/+3 dB law for imports), a
flat high-rejection sample-rate converter, a default-on defeatable clip-edge
fade, and zero latency. It is a profile.py target, so the same probes that
measure Live measure it, and the real engine is later required to null against
it. Run: python daw_bench/ref_engine.py --out sandbox_sessions/ref_profile
"""
from __future__ import annotations

import argparse
import json
import sys
from math import gcd
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import firwin, kaiserord, resample_poly

sys.path.insert(0, str(Path(__file__).resolve().parent))

import measure  # noqa: E402
import profile  # noqa: E402


def convert_rate(audio: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    """Polyphase SRC with a Kaiser FIR flat to 0.45 of the lower rate and 120 dB
    down by its Nyquist (section 3 spec: ripple <= 0.01 dB, aliasing <= -120 dB)."""
    if sr_in == sr_out:
        return audio
    g = gcd(sr_in, sr_out)
    up, down = sr_out // g, sr_in // g
    low = min(sr_in, sr_out)
    nyq_high = sr_in * up / 2.0                           # the filter runs at sr_in * up
    numtaps, beta = kaiserord(120.0, 0.1 * low / nyq_high)  # transition 0.45..0.55 of `low`
    fir = firwin(numtaps | 1, 0.5 * low / nyq_high, window=("kaiser", beta))
    return resample_poly(audio, up, down, window=fir, axis=0)


class RefEngine:
    """profile.py target. `sr` is the project rate."""

    warp_modes = ["bypass"]          # the spec: a stretcher at ratio 1:1 is bypassed

    def __init__(self, sr: int = 48000, pan_law: str = "sin_-3_0",
                 edge_fade_ms: float = 4.0):
        self.sr, self.pan_law, self.edge_fade_ms = sr, pan_law, edge_fade_ms

    def play(self, wav: str, position_beats: float, pan: float, seconds: float,
             warp_mode: str | None = None) -> np.ndarray:
        audio, file_sr = sf.read(wav, dtype="float64", always_2d=True)
        audio = convert_rate(audio, file_sr, self.sr)
        n = int(self.edge_fade_ms * self.sr / 1000.0)
        if n and len(audio) > 2 * n:                      # raised-cosine clip-edge fades
            ramp = (0.5 - 0.5 * np.cos(np.pi * np.arange(n) / n))[:, None]
            audio[:n] *= ramp
            audio[-n:] *= ramp[::-1]
        mono = audio.mean(axis=1)
        gl, gr = measure.pan_gains(self.pan_law, pan)
        out = np.zeros((int(round(seconds * self.sr)), 2))
        at = int(round(position_beats * 60.0 / profile.TEMPO * self.sr))
        end = min(len(out), at + len(mono))
        out[at:end, 0] = gl * mono[:end - at]
        out[at:end, 1] = gr * mono[:end - at]
        return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Profile the Python reference engine.")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent
                                         / "sandbox_sessions" / "ref_profile"))
    ap.add_argument("--sr", type=int, default=48000)
    ap.add_argument("--pan-law", default="sin_-3_0", choices=measure.PAN_LAWS)
    args = ap.parse_args(argv)
    prof = profile.run_probes(RefEngine(args.sr, args.pan_law), Path(args.out), "ref_profile")
    print(json.dumps(prof, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
