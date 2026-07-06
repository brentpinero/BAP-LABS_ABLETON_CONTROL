"""
calibration_tones.py — Tier 2 reference-tone generator + expected band fractions.

Tier 1 (test_calibration.py) proved the FFT ruler (bands.band_energies) is accurate.
Tier 2 proves the LIVE Max onepole~ device agrees with that ruler. This module
makes the reference signals + the expected answer:

  1. Renders known tones (sine at a known dBFS + a pink-noise burst) to WAVs.
  2. Computes each tone's band_energies (the FFT ruler) → the EXPECTED fractions.
  3. Writes both WAVs and expected.json into sandbox_sessions/calibration/.

Runbook (needs Ableton):
  python harness/calibration_tones.py            # generate WAVs + expected.json
  → drop a WAV on an audio track (rename it "CalTone"), solo + loop it, play.
  → python harness/calibrate_live.py CalTone     # capture live frame, compare.

onepole~ is a gentle 6 dB/oct filter and the FFT ruler is near-brick-wall, so the
two won't match to the decimal. The live compare therefore checks agreement in the
ways that matter: same dominant band, home-band majority, and spectral-shape
correlation — not an exact fraction match.
"""

from __future__ import annotations

import json
import math
import wave
from pathlib import Path

import numpy as np

import bands

SR = 44100
_OUT = Path(__file__).resolve().parent.parent / "sandbox_sessions" / "calibration"

# (label, kind, arg, dBFS) — arg is Hz for sines; ignored for pink.
TONES = [
    ("sine_40hz",    "sine", 40.0,    -12.0),
    ("sine_90hz",    "sine", 90.0,    -12.0),
    ("sine_1khz",    "sine", 1000.0,  -12.0),
    ("sine_4khz",    "sine", 4000.0,  -12.0),
    ("sine_8khz",    "sine", 8000.0,  -12.0),
    ("pink_fullband","pink", 0.0,     -18.0),
]


def _sine(freq, dur_s, dbfs):
    amp = 10.0 ** (dbfs / 20.0)
    t = np.arange(int(dur_s * SR)) / SR
    return amp * np.sin(2 * math.pi * freq * t)


def _pink(dur_s, dbfs):
    # Voss-ish pink via FFT 1/f shaping — a broadband reference across all bands.
    n = int(dur_s * SR)
    white = np.random.default_rng(0).standard_normal(n)   # fixed seed → reproducible
    spec = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    freqs[0] = freqs[1]
    spec = spec / np.sqrt(freqs)
    sig = np.fft.irfft(spec, n=n)
    sig = sig / (np.max(np.abs(sig)) or 1.0) * (10.0 ** (dbfs / 20.0))
    return sig


def _write_wav(path, sig):
    pcm = np.clip(sig, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def generate(scheme_id: str = "v1_7band", dur_s: float = 2.0) -> dict:
    _OUT.mkdir(parents=True, exist_ok=True)
    expected = {"scheme": scheme_id, "sr": SR, "band_names": bands.band_names(scheme_id),
                "tones": {}}
    for label, kind, arg, dbfs in TONES:
        sig = _sine(arg, dur_s, dbfs) if kind == "sine" else _pink(dur_s, dbfs)
        wav = _OUT / f"{label}.wav"
        _write_wav(wav, sig)
        fr = bands.band_energies(sig, SR, scheme_id)
        names = bands.band_names(scheme_id)
        expected["tones"][label] = {
            "kind": kind, "arg_hz": arg, "dbfs": dbfs,
            "wav": str(wav.name),
            "fractions": [round(x, 6) for x in fr],
            "dominant_band": names[int(np.argmax(fr))],
        }
    (_OUT / "expected.json").write_text(json.dumps(expected, indent=2))
    return expected


if __name__ == "__main__":
    exp = generate()
    print(f"wrote {len(exp['tones'])} tones + expected.json to {_OUT}")
    for label, t in exp["tones"].items():
        print(f"  {label:16s} dominant={t['dominant_band']:9s} "
              f"peak={max(t['fractions']):.2f}")
