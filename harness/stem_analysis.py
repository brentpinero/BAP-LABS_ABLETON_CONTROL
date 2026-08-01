"""
stem_analysis.py — offline acoustic analysis of ablation stems + rung-to-rung deltas.

Turns each rendered stem .wav into TIME-BASED sound features (the "what does it sound
like" the model trains on) and, per node, computes the causal PLUGIN EFFECT: how the sound
changed when the next effect in the chain was enabled.

Per stem (framewise at ~frame_rate_hz, matching the live perception vocabulary + brightness):
  - band_energy[B]  per-band spectral energy fraction (bands.py v1_7band, == live scheme)
  - rms_db          short-time loudness envelope (dBFS)
  - centroid_hz     spectral centroid (brightness)
  - flux            spectral flux (frame-to-frame movement)
  - width           stereo width side/(mid+side) in [0,1]
plus a `summary` (mean/std/min/max/p10/p90 per feature, per-band means) and whole-stem
`loudness` (LUFS integrated/LRA/true-peak/crest — reuses harness/loudness.py).

Per progressive rung the sidecar also gets `plugin_effect`: the delta vs the previous rung
(the effect of `newly_enabled`) — per-band dB change, loudness/crest/centroid/width deltas.
All written INLINE into the stem sidecars. Reuses bands.py; librosa/soundfile for DSP.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import bands as _bands

ANALYSIS_SCHEMA = "sim.stem-analysis.v1"


def _pct(a, p):
    return float(np.percentile(a, p)) if len(a) else 0.0


def _summary(arr) -> dict:
    a = np.asarray(arr, dtype=float)
    if a.size == 0:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "p10": 0.0, "p90": 0.0}
    return {"mean": float(a.mean()), "std": float(a.std()), "min": float(a.min()),
            "max": float(a.max()), "p10": _pct(a, 10), "p90": _pct(a, 90)}


def analyze_stem(path, scheme: str = None, hop: int = 2048, n_fft: int = 4096,
                 round_series: bool = True) -> dict:
    """Framewise features + summary + loudness for one stem wav."""
    import librosa
    import soundfile as sf

    scheme = scheme or _bands.DEFAULT_SCHEME
    audio, sr = sf.read(path, always_2d=True)          # (N, ch)
    mono = audio.mean(axis=1).astype(np.float32)
    edges = _bands.band_edges(scheme)

    # power STFT → band energies, centroid, flux (all on the same hop grid)
    mag = np.abs(librosa.stft(mono, n_fft=n_fft, hop_length=hop))   # [freq, T]
    powr = mag ** 2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    band_pow = np.array([powr[(freqs >= lo) & (freqs < hi)].sum(axis=0) for lo, hi in edges])  # [B,T]
    total = band_pow.sum(axis=0)
    total[total == 0] = 1.0
    band_frac = (band_pow / total).T                    # [T, B], sums to ~1 per frame
    T = band_frac.shape[0]

    rms = librosa.feature.rms(S=mag, frame_length=n_fft, hop_length=hop)[0][:T]
    rms_db = 20.0 * np.log10(np.maximum(rms, 1e-9))
    centroid = librosa.feature.spectral_centroid(S=mag, sr=sr, n_fft=n_fft, hop_length=hop)[0][:T]
    flux = np.sqrt(np.maximum(np.diff(mag, axis=1), 0.0).__pow__(2).sum(axis=0))  # half-wave rect
    flux = np.concatenate([[0.0], flux])[:T]

    # stereo width per frame: framed RMS of mid/side
    if audio.shape[1] >= 2:
        mid = ((audio[:, 0] + audio[:, 1]) * 0.5).astype(np.float32)
        side = ((audio[:, 0] - audio[:, 1]) * 0.5).astype(np.float32)
        mrms = librosa.feature.rms(y=mid, frame_length=n_fft, hop_length=hop)[0][:T]
        srms = librosa.feature.rms(y=side, frame_length=n_fft, hop_length=hop)[0][:T]
        denom = mrms + srms
        width = np.where(denom > 0, srms / np.maximum(denom, 1e-12), 0.0)
    else:
        width = np.zeros(T)

    r5 = (lambda x: [round(float(v), 5) for v in x]) if round_series else (lambda x: [float(v) for v in x])
    r2 = (lambda x: [round(float(v), 2) for v in x]) if round_series else (lambda x: [float(v) for v in x])
    series = {
        "band_energy": [r5(row) for row in band_frac],  # [T][B]
        "rms_db": r2(rms_db),
        "centroid_hz": [round(float(v), 1) for v in centroid],
        "flux": r5(flux / (flux.max() or 1.0)),          # normalized 0..1
        "width": r5(width),
    }
    summary = {
        "band_energy": [_summary(band_frac[:, b]) for b in range(band_frac.shape[1])],
        "rms_db": _summary(rms_db), "centroid_hz": _summary(centroid),
        "flux": _summary(series["flux"]), "width": _summary(width),
    }
    # dynamics over CONTENT frames only (a stem may be mostly silent in-window, which would
    # otherwise flatten p90-p10 to 0): loudness spread of frames above a floor.
    content = rms_db[rms_db > -60.0]
    dyn = round(float(np.percentile(content, 90) - np.percentile(content, 10)), 2) if content.size > 10 else 0.0
    summary["content_frames"] = int(content.size)
    # FAST loudness only — skip loudness_range / short_term_series (the ~7s sliding-window
    # metrics); derive dynamics cheaply from the framewise rms_db envelope (p90-p10) instead.
    from loudness import (integrated_lufs, momentary_lufs_max, rms_dbfs,
                          sample_peak_dbfs, true_peak_dbtp)
    try:
        sp, rd = sample_peak_dbfs(audio), rms_dbfs(audio)
        loud = {
            "lufs_integrated": round(float(integrated_lufs(audio, sr)), 2),
            "lufs_momentary_max": round(float(momentary_lufs_max(audio, sr)), 2),
            "true_peak_dbtp": round(float(true_peak_dbtp(audio, sr)), 2),
            "sample_peak_dbfs": round(float(sp), 2), "rms_dbfs": round(float(rd), 2),
            "crest_factor_db": round(float(sp - rd), 2),
            "dynamic_range_db": dyn,                    # loudness spread over content frames
        }
    except Exception as e:  # near-silent stem
        loud = {"error": str(e), "dynamic_range_db": dyn}

    return {"schema_version": ANALYSIS_SCHEMA, "scheme": scheme,
            "frame_rate_hz": round(sr / hop, 3), "n_frames": int(T), "hop": hop, "n_fft": n_fft,
            "series": series, "summary": summary, "loudness": loud}


def _band_levels_db(summary: dict) -> list:
    """Per-band absolute level (dB) from a stem summary: mean band fraction weighted by the
    mean linear RMS (== masking.band_abs applied to the time-averaged frame)."""
    lin = 10.0 ** (summary["rms_db"]["mean"] / 20.0)
    out = []
    for b in summary["band_energy"]:
        out.append(20.0 * math.log10(max(b["mean"] * lin, 1e-9)))
    return out


def plugin_effect(cur: dict, prev: dict, newly_enabled: str, vs_label: str) -> dict:
    """Delta between two rungs' analyses = the effect of the newly-enabled plugin."""
    cur_l, prev_l = cur["loudness"], prev["loudness"]
    def dl(k):
        a, b = cur_l.get(k), prev_l.get(k)
        return round(a - b, 2) if isinstance(a, (int, float)) and isinstance(b, (int, float)) else None
    band_db = [round(c - p, 2) for c, p in zip(_band_levels_db(cur["summary"]),
                                               _band_levels_db(prev["summary"]))]
    return {
        "newly_enabled": newly_enabled, "vs_rung": vs_label,
        "band_names": _bands.band_names(cur.get("scheme")),
        "band_db_change": band_db,                        # per-band energy change (dB)
        "loudness_db": dl("lufs_integrated"),
        "true_peak_db": dl("true_peak_dbtp"),
        "crest_db": dl("crest_factor_db"),
        "dynamic_range_change": dl("dynamic_range_db"),
        "centroid_hz_change": round(cur["summary"]["centroid_hz"]["mean"]
                                    - prev["summary"]["centroid_hz"]["mean"], 1),
        "width_change": round(cur["summary"]["width"]["mean"]
                              - prev["summary"]["width"]["mean"], 4),
        "flux_change": round(cur["summary"]["flux"]["mean"] - prev["summary"]["flux"]["mean"], 4),
    }


def _node_key(wav_name: str) -> str:
    return wav_name.split("__", 1)[0]


def analyze_session(session_dir, scheme=None, hop=2048, n_fft=4096, log=print) -> dict:
    """Two passes over a stem-ablation session: (1) analyze each wav → inject `audio_analysis`
    into its sidecar; (2) per node, compute `plugin_effect` deltas into progressive rungs."""
    session_dir = Path(session_dir)
    sidecars = {}                                        # wav_name -> (json_path, sidecar dict)
    analyses = {}                                        # wav_name -> analysis dict
    wavs = sorted(session_dir.glob("*.wav"))
    for i, wav in enumerate(wavs):
        jf = wav.with_suffix(".json")
        if not jf.exists():
            continue
        sc = json.loads(jf.read_text())
        try:
            an = analyze_stem(wav, scheme=scheme, hop=hop, n_fft=n_fft)
        except Exception as e:                           # a bad/short stem must not stop the run
            log(f"  analyze FAILED {wav.name}: {e}")
            continue
        sc["audio_analysis"] = an
        analyses[wav.name] = an
        sidecars[wav.name] = (jf, sc)
        if (i + 1) % 25 == 0:
            log(f"  analyzed {i + 1}/{len(wavs)}")

    # Pass 2: per node, delta each progressive rung against the previous chain state.
    nodes = {}
    for wav_name, (jf, sc) in sidecars.items():
        nodes.setdefault(_node_key(wav_name), []).append(wav_name)
    deltas = 0
    for node, names in nodes.items():
        by_through = {}                                  # enabled_through -> wav_name (for progressive)
        all_off = None
        for wn in names:
            rung = sidecars[wn][1].get("rung", {})
            if rung.get("kind") == "progressive":
                by_through[rung.get("enabled_through")] = wn
            elif rung.get("kind") == "all_off":
                all_off = wn
        for through, wn in by_through.items():
            prev_wn = by_through.get(through - 1) if through and through - 1 in by_through else all_off
            if not prev_wn or wn not in analyses or prev_wn not in analyses:
                continue
            sc = sidecars[wn][1]
            eff = plugin_effect(analyses[wn], analyses[prev_wn],
                                sc["rung"].get("newly_enabled"),
                                sidecars[prev_wn][1]["rung"].get("label"))
            sc["plugin_effect"] = eff
            deltas += 1

    for jf, sc in sidecars.values():                     # write everything back once
        jf.write_text(json.dumps(sc, indent=1))
    return {"analyzed": len(analyses), "sidecars": len(sidecars), "plugin_effects": deltas}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Analyze ablation stems into features + plugin-effect deltas.")
    ap.add_argument("session_dir", help="ablation session dir with stem .wav + .json sidecars")
    ap.add_argument("--hop", type=int, default=2048, help="STFT hop (default 2048 ~= 23Hz @48k)")
    ap.add_argument("--n-fft", type=int, default=4096)
    args = ap.parse_args(argv)
    import time
    t0 = time.time()
    res = analyze_session(args.session_dir, hop=args.hop, n_fft=args.n_fft)
    print(f"[ANALYZE] {res['analyzed']} stems analyzed | {res['plugin_effects']} plugin-effect deltas "
          f"| {res['sidecars']} sidecars updated in {(time.time()-t0)/60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
