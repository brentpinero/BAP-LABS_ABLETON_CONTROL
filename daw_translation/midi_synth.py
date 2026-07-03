"""
midi_synth.py — deterministic numpy fallback synth for the sandbox render path.

Turns the repo's canonical note dicts ({pitch, start_time, duration, velocity},
times in BEATS — identical to add_notes_to_arrangement_clip) into audio with
role-aware proxy voices. This is NOT sound design: it exists so the sandbox can
always render candidate MIDI for analysis (groove, harmony, register, balance)
even when no VST/AU instrument is available. ~50x realtime, no heavy deps,
importable anywhere (no pedalboard — GPL boundary unaffected).

Deterministic: noise uses per-note seeded RNGs, so identical notes => identical
audio => stable content-hash caching in render_pool.
"""
from __future__ import annotations

import numpy as np

SR_DEFAULT = 44100

# GM-ish drum map (matches harness/ableton_knowledge.DRUM_MAP)
KICK, RIM, SNARE, CLAP = 36, 37, 38, 39
CH, OH, LTOM, MTOM, HTOM = 42, 46, 45, 47, 50
CRASH, RIDE, SHAKER, TAMB = 49, 51, 70, 54

# role -> (waveform, lp_cutoff_hz, attack_s, decay_s, sustain, release_s, detune)
_PITCHED_VOICES = {
    "bass":   ("saw", 500.0, 0.004, 0.08, 0.85, 0.08, 0.0),
    "keys":   ("tri", 1800.0, 0.006, 0.15, 0.70, 0.20, 0.0),
    "chords": ("tri", 1500.0, 0.008, 0.15, 0.70, 0.25, 0.003),
    "melody": ("saw", 2400.0, 0.005, 0.10, 0.75, 0.15, 0.0),
    "lead":   ("saw", 3000.0, 0.004, 0.08, 0.80, 0.12, 0.004),
    "pluck":  ("saw", 2000.0, 0.002, 0.20, 0.00, 0.15, 0.0),
    "pad":    ("saw", 1200.0, 0.250, 0.30, 0.85, 0.60, 0.006),
}
_DEFAULT_VOICE = _PITCHED_VOICES["keys"]


def _midi_hz(pitch: float) -> float:
    return 440.0 * 2.0 ** ((pitch - 69) / 12.0)


try:  # vectorized IIR — scipy ships with librosa; loop fallback keeps deps soft
    from scipy.signal import lfilter as _lfilter
except Exception:  # pragma: no cover
    _lfilter = None


def _one_pole_lp(x: np.ndarray, cutoff_hz: float, sr: int) -> np.ndarray:
    """Simple one-pole lowpass — enough to tame the naive waveforms."""
    a = 1.0 - np.exp(-2.0 * np.pi * cutoff_hz / sr)
    if _lfilter is not None:
        return _lfilter([a], [1.0, -(1.0 - a)], x)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def _adsr(n: int, sr: int, a: float, d: float, s: float, r: float) -> np.ndarray:
    """Linear ADSR envelope, release appended inside n (note length includes release)."""
    na, nd, nr = int(a * sr), int(d * sr), int(r * sr)
    nsus = max(0, n - na - nd - nr)
    env = np.concatenate([
        np.linspace(0.0, 1.0, max(na, 1), endpoint=False),
        np.linspace(1.0, s, max(nd, 1), endpoint=False),
        np.full(nsus, s, dtype="float64"),
        np.linspace(s, 0.0, max(nr, 1)),
    ])
    if len(env) < n:
        env = np.pad(env, (0, n - len(env)))
    return env[:n]


def _osc(wave: str, freq: float, n: int, sr: int, detune: float) -> np.ndarray:
    t = np.arange(n, dtype="float64") / sr
    def one(f: float) -> np.ndarray:
        ph = (f * t) % 1.0
        if wave == "tri":
            return 2.0 * np.abs(2.0 * ph - 1.0) - 1.0
        return 2.0 * ph - 1.0  # naive saw (aliasing acceptable for a proxy voice)
    if detune > 0:
        return 0.5 * (one(freq * (1 + detune)) + one(freq * (1 - detune)))
    return one(freq)


def _drum_hit(pitch: int, vel: float, sr: int, rng: np.random.Generator) -> np.ndarray:
    """Synthesize one percussion hit keyed by GM pitch. Returns a short buffer."""
    def decay(n, tau):  # exponential decay envelope
        return np.exp(-np.arange(n) / (tau * sr))
    def noise(n):
        return rng.standard_normal(n)

    if pitch == KICK:
        n = int(0.18 * sr)
        f = np.linspace(95.0, 42.0, n)  # pitch sweep
        body = np.sin(2 * np.pi * np.cumsum(f) / sr) * decay(n, 0.06)
        click = noise(int(0.003 * sr)) * 0.4
        body[: len(click)] += click
        return body * vel
    if pitch in (SNARE, RIM):
        n = int((0.16 if pitch == SNARE else 0.05) * sr)
        tone = np.sin(2 * np.pi * 185.0 * np.arange(n) / sr) * decay(n, 0.03) * 0.5
        snap = _one_pole_lp(noise(n), 6000.0, sr) - _one_pole_lp(noise(n), 800.0, sr)
        return (tone + snap * decay(n, 0.04)) * vel * 0.8
    if pitch == CLAP:
        n = int(0.20 * sr)
        buf = np.zeros(n)
        for k, off in enumerate((0.0, 0.012, 0.025)):  # 3 micro-bursts
            i = int(off * sr)
            m = int(0.05 * sr)
            buf[i:i + m] += noise(m) * decay(m, 0.015) * (0.7 + 0.1 * k)
        return _one_pole_lp(buf, 4000.0, sr) * vel * 0.7
    if pitch in (CH, OH, SHAKER, TAMB):
        dur = {CH: 0.05, OH: 0.30, SHAKER: 0.06, TAMB: 0.15}[pitch]
        n = int(dur * sr)
        hp = noise(n) - _one_pole_lp(noise(n), 3000.0, sr)  # crude highpass
        return hp * decay(n, dur * 0.5) * vel * 0.35
    if pitch in (LTOM, MTOM, HTOM):
        f0 = {LTOM: 90.0, MTOM: 120.0, HTOM: 160.0}[pitch]
        n = int(0.25 * sr)
        f = np.linspace(f0, f0 * 0.6, n)
        return np.sin(2 * np.pi * np.cumsum(f) / sr) * decay(n, 0.09) * vel * 0.8
    if pitch in (CRASH, RIDE):
        dur = 0.9 if pitch == CRASH else 0.5
        n = int(dur * sr)
        hp = noise(n) - _one_pole_lp(noise(n), 2000.0, sr)
        return hp * decay(n, dur * 0.6) * vel * 0.3
    # unknown percussion -> generic mid burst
    n = int(0.08 * sr)
    return _one_pole_lp(noise(n), 2500.0, sr) * decay(n, 0.03) * vel * 0.5


def render_notes(notes: list[dict], bpm: float, role: str = "keys",
                 sr: int = SR_DEFAULT, bars: float | None = None,
                 tail_seconds: float = 1.0) -> np.ndarray:
    """Render note dicts to a mono float32 buffer.

    notes: [{pitch, start_time(beats), duration(beats), velocity}], role picks the
    voice ("drums" => percussion by pitch). bars fixes the musical length (else
    derived from the last note end). Deterministic for identical inputs.
    """
    role = (role or "keys").lower()
    spb = 60.0 / max(1e-3, float(bpm))  # seconds per beat
    if bars is not None:
        musical_end = float(bars) * 4.0 * spb
    else:
        musical_end = max((float(n.get("start_time", 0)) + float(n.get("duration", 0.25)))
                          for n in notes) * spb if notes else 1.0
    total = int((musical_end + tail_seconds) * sr)
    out = np.zeros(total, dtype="float64")

    for i, note in enumerate(notes):
        start = int(float(note.get("start_time", 0.0)) * spb * sr)
        if start >= total:
            continue
        vel = (max(1, min(127, int(note.get("velocity", 100)))) / 127.0) ** 1.5
        pitch = int(note.get("pitch", 60))

        if role == "drums":
            rng = np.random.default_rng(abs(hash((pitch, i, start))) % (2 ** 32))
            buf = _drum_hit(pitch, vel, sr, rng)
        else:
            wave, cutoff, a, d, s, r, det = _PITCHED_VOICES.get(role, _DEFAULT_VOICE)
            n = max(int((float(note.get("duration", 0.25)) * spb + r) * sr), int(0.02 * sr))
            osc = _osc(wave, _midi_hz(pitch), n, sr, det)
            buf = _one_pole_lp(osc, cutoff, sr) * _adsr(n, sr, a, d, s, r) * vel * 0.5

        end = min(start + len(buf), total)
        out[start:end] += buf[: end - start]

    peak = np.max(np.abs(out)) or 1.0
    if peak > 0.9:  # normalize only if hot — keeps relative dynamics otherwise
        out *= 0.9 / peak
    return out.astype("float32")
