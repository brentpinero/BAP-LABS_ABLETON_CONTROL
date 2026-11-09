"""
test_fidelity.py — offline tests for the fidelity measurement core.

Synthetic 'plugins' = known transformations of a generated signal, so every
metric has a ground-truth expectation. No Live, no pedalboard, no network.
Run: python sandbox/test_fidelity.py  (or pytest).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))

import fidelity  # noqa: E402

SR = 44100


def _signal(seconds: float = 3.0, seed: int = 3) -> np.ndarray:
    """Noise burst + sine mix — broadband enough for alignment + band math."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    sig = (0.3 * np.sin(2 * np.pi * 220 * t)
           + 0.2 * np.sin(2 * np.pi * 1330 * t)
           + 0.15 * rng.standard_normal(n))
    env = np.minimum(1.0, t * 20)  # fast fade-in so alignment has an onset
    return (sig * env).astype("float64")


def _wav(path: Path, audio: np.ndarray, sr: int = SR) -> str:
    sf.write(path, audio.astype("float32"), sr)
    return str(path)


def test_exact_copy_with_known_delay():
    a = _signal()
    delayed = np.concatenate([np.zeros(173), a])  # b arrives 173 samples LATE
    with tempfile.TemporaryDirectory() as d:
        res = fidelity.compare(_wav(Path(d) / "a.wav", a),
                               _wav(Path(d) / "b.wav", delayed))
    assert res["latency_samples"] == 173, res
    assert res["null_depth_db"] > 60, res  # float32 wav roundtrip caps exactness
    assert res["label"] == "measured-identical"
    assert abs(res["gain_delta_db"]) < 0.1


def test_align_with_lag_window_longer_than_signal():
    a = _signal(seconds=0.25)
    delayed = np.concatenate([np.zeros(173), a])
    lag, _ = fidelity.align(a, delayed, SR, max_lag_s=2.0)  # window > signal length
    assert lag == 173, lag


def test_known_filter_and_gain():
    from scipy.signal import lfilter
    a = _signal()
    b = lfilter([0.7, 0.3], [1.0], a) * 2.0  # mild FIR + 6.02 dB gain
    with tempfile.TemporaryDirectory() as d:
        res = fidelity.compare(_wav(Path(d) / "a.wav", a),
                               _wav(Path(d) / "b.wav", b))
    assert abs(res["gain_delta_db"] + 6.02) < 1.0, res  # b louder -> match REDUCES it
    assert 3 < res["null_depth_db"] < 40, res           # close but audibly filtered
    # mild FIR on a sine-dominated signal is spectrally close — smart label applies
    assert res["label"] in ("measured-close", "spectral-match")


def test_unrelated_signals_null_near_zero():
    # different seed AND different spectral content (else the smart label
    # correctly calls two same-recipe noises a spectral-match)
    a = _signal(seed=1)
    rng = np.random.default_rng(99)
    n = len(a)
    t = np.arange(n) / SR
    b = (0.5 * np.sin(2 * np.pi * 90 * t) + 0.1 * rng.standard_normal(n)) * 0.9
    with tempfile.TemporaryDirectory() as d:
        res = fidelity.compare(_wav(Path(d) / "a.wav", a),
                               _wav(Path(d) / "b.wav", b))
    assert res["null_depth_db"] < 6, res
    assert res["label"] == "diverged"


def test_spectral_match_label_for_phase_randomized():
    # same spectrum, decorrelated phase (the Serum-unison situation)
    rng1, rng2 = np.random.default_rng(1), np.random.default_rng(2)
    n = SR * 3
    a = rng1.standard_normal(n) * 0.2
    b = rng2.standard_normal(n) * 0.2  # identical spectrum, uncorrelated waveform
    with tempfile.TemporaryDirectory() as d:
        res = fidelity.compare(_wav(Path(d) / "a.wav", a),
                               _wav(Path(d) / "b.wav", b))
    assert res["null_depth_db"] < 10, res
    assert res["label"] == "spectral-match", res


def test_sr_mismatch_resample_path():
    a = _signal()
    with tempfile.TemporaryDirectory() as d:
        pa = _wav(Path(d) / "a.wav", a, SR)
        import librosa
        b48 = librosa.resample(a, orig_sr=SR, target_sr=48000)
        pb = _wav(Path(d) / "b.wav", b48, 48000)
        res = fidelity.compare(pa, pb)
    assert res["resampled"] is True
    # resampling full-band noise is audibly close but NOT exact (~15-25 dB null) —
    # exactly why the resampled flag exists and caps identity claims
    assert res["null_depth_db"] > 12, res
    assert res["label"] in ("measured-close", "spectral-match")


def test_band_diff_reports_filter_shape():
    a = _signal()
    # crude lowpass: kill highs -> high bands should show positive a-vs-b dB
    from scipy.signal import butter, lfilter
    ba, bb = butter(4, 1000 / (SR / 2), btype="low")
    b = lfilter(ba, bb, a)
    with tempfile.TemporaryDirectory() as d:
        res = fidelity.compare(_wav(Path(d) / "a.wav", a),
                               _wav(Path(d) / "b.wav", b))
    band_diff = res["band_diff_db"]
    assert band_diff[-1] > band_diff[1] + 6, band_diff  # a has far more top end


def test_registry_roundtrip_and_labels():
    with tempfile.TemporaryDirectory() as d:
        reg = fidelity.Registry(Path(d) / "reg.json")
        k = reg.record("Serum", "/path/Serum.vst3", "vst3",
                       {"null_depth_db": 47.0, "label": "measured-identical"},
                       preset="BS - Clean FM",
                       audio_pair={"headless": "h.wav", "live": "l.wav"})
        reg.record_live_only("Electric")
        reg2 = fidelity.Registry(Path(d) / "reg.json")
        assert reg2.data[k]["label"] == "measured-identical"
        assert reg2.best_label("Serum") == "measured-identical"
        assert reg2.best_label("Electric") == "live_only"
        assert reg2.best_label("NeverMeasured") == "unmeasured"


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  PASS  {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} tests passed.")


if __name__ == "__main__":
    _run_all()
