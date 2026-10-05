"""
test_measure.py — offline tests for the Phase 0 measurement harness.

Each test builds a synthetic 'DAW behaviour' with a known answer (a pan law, a
good and a bad resampler, a 4 ms fade, a clipped sine) and checks the instrument
recovers it. No Live, no plugins. Run: python daw_bench/test_measure.py (or pytest).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.signal import firwin, resample_poly

sys.path.insert(0, str(Path(__file__).parent))

import measure  # noqa: E402
import signals  # noqa: E402

SR = 48000


# --- meter gate: +-0.1 dBTP / +-0.1 LU on signals with known answers ----------
def test_true_peak_reads_intersample_peak():
    # fs/4 sine at 45 deg: samples peak at -6.02 dBFS, waveform peaks 3.01 dB higher
    x = signals.fade(signals.isp_stress(2.0, SR, sample_peak_db=-6.02), SR)
    assert abs(measure.loudness.sample_peak_dbfs(x) - (-6.02)) < 0.01
    assert abs(measure.true_peak_dbtp(x, SR) - (-3.01)) < 0.1


def test_16x_meter_beats_4x_default():
    # 0.4*fs tone: the 4x default under-reads by ~0.4 dB, 16x stays inside the gate
    x = signals.fade(signals.sine(0.4 * SR, 1.0, SR, level_db=-3.0), SR)
    err_16 = abs(measure.true_peak_dbtp(x, SR) - (-3.0))
    err_4 = abs(measure.loudness.true_peak_dbtp(x, SR, oversample=4) - (-3.0))
    assert err_16 < 0.1, err_16
    assert err_4 > 0.3, err_4


def test_integrated_loudness_of_reference_tone():
    # EBU Tech 3341 case 1 shape: stereo 1 kHz sine at -23 dBFS reads -23 LUFS
    tone = signals.sine(1000.0, 20.0, SR, level_db=-23.0)
    lufs = measure.loudness.integrated_lufs(np.column_stack([tone, tone]), SR)
    assert abs(lufs - (-23.0)) < 0.1, lufs


# --- level, distortion, residual ---------------------------------------------
def test_tone_level_and_thd_of_clean_and_clipped_sine():
    x = signals.sine(997.0, 1.0, SR, level_db=-12.0)
    assert abs(measure.tone_level_db(x, SR, 997.0) - (-12.0)) < 0.001
    assert measure.thd_n_db(x, SR, 997.0) < -200.0           # numerically clean
    clipped = np.clip(x, -0.2, 0.2)                           # hard clip -> harmonics
    assert -30.0 < measure.thd_n_db(clipped, SR, 997.0) < -10.0


def test_residual_resolves_below_float32_precision():
    x = signals.noise(1.0, SR, level_db=-20.0, seed=1)
    assert measure.residual_dbfs(x, x) == measure.FLOOR_DB
    # float32 round trip leaves a residual a 120 dB-capped null test cannot see
    r = measure.residual_dbfs(x, x.astype(np.float32).astype(np.float64))
    assert -190.0 < r < -140.0, r


def test_latency_recovers_known_delay():
    x = signals.noise(2.0, SR, seed=2)
    late = np.concatenate([np.zeros(2048), x])
    assert measure.latency_samples(x, late, SR) == 2048


# --- pan law --------------------------------------------------------------------
def _pan_measurements(law: str, positions):
    tone = signals.sine(1000.0, 0.5, SR, level_db=-3.0)
    left_db, right_db = [], []
    for p in positions:
        gl, gr = measure.pan_gains(law, p)
        l_db, r_db = measure.stereo_tone_gains_db(
            np.column_stack([tone * gl, tone * gr]), SR, 1000.0, source_level_db=-3.0)
        left_db.append(l_db)
        right_db.append(r_db)
    return left_db, right_db


def test_fit_pan_law_identifies_each_law():
    positions = list(np.linspace(-1.0, 1.0, 21))
    for law in measure.PAN_LAWS:
        left_db, right_db = _pan_measurements(law, positions)
        fit = measure.fit_pan_law(positions, left_db, right_db)
        assert fit["law"] == law, (law, fit)
        assert fit["max_error_db"] <= 0.01, (law, fit)


def test_pan_law_reference_points():
    # Live's documented law: 0 dB at centre, +3 dB hard-panned
    c = measure.pan_gains("sin_0_+3", 0.0)
    assert abs(20 * np.log10(c[0])) < 1e-9
    assert abs(20 * np.log10(measure.pan_gains("sin_0_+3", 1.0)[1]) - 3.0103) < 1e-3
    # centre-cut constant power: -3 dB centre, 0 dB hard-panned
    assert abs(20 * np.log10(measure.pan_gains("sin_-3_0", 0.0)[0]) + 3.0103) < 1e-3


# --- sample-rate conversion -------------------------------------------------------
SWEEP = dict(f_start=20.0, f_end=48000.0, seconds=8.0, level_db=-6.0)


def test_src_sweep_separates_good_from_bad_converter():
    sr_in, sr_out = 96000, 48000
    sweep = signals.linear_sweep(SWEEP["f_start"], SWEEP["f_end"], SWEEP["seconds"],
                                 sr_in, SWEEP["level_db"])
    # steep anti-alias filter: flat to 20 kHz, down >100 dB by 26 kHz
    good = resample_poly(sweep, 1, 2, window=firwin(401, 23000.0, fs=sr_in,
                                                    window=("kaiser", 12.0)))
    bad = sweep[::2]                                              # no filter: aliases
    g = measure.analyse_src_sweep(good, sr_out, **SWEEP)
    b = measure.analyse_src_sweep(bad, sr_out, **SWEEP)
    assert g["passband_ripple_db"] < 0.5, g
    assert g["alias_db"] < -60.0, g
    assert b["alias_db"] > -3.0, b                                # folded back at full level


# --- clip-edge fade -----------------------------------------------------------------
def test_edge_fade_length():
    # leading silence: the edge sits mid-capture, as it does in a real recording
    tone = np.concatenate([np.zeros(SR // 4), signals.sine(5000.0, 0.5, SR, level_db=-6.0)])
    assert measure.edge_fade_ms(tone, SR, 5000.0) < 0.5                    # hard edge
    faded = tone.copy()
    n = int(0.004 * SR)                                            # 4 ms linear fade-in
    faded[SR // 4: SR // 4 + n] *= np.linspace(0.0, 1.0, n)
    assert 3.0 < measure.edge_fade_ms(faded, SR, 5000.0) < 4.3, measure.edge_fade_ms(faded, SR, 5000.0)


# --- limiter -------------------------------------------------------------------------
def test_limiter_overshoot_catches_sample_peak_limiter():
    # a limiter that only clamps SAMPLES to -1 dBFS lets the true peak through
    x = signals.fade(signals.isp_stress(1.0, SR, sample_peak_db=-1.0), SR)
    assert measure.limiter_overshoot_db(x, SR, ceiling_db=-1.0) > 2.9
    assert measure.limiter_overshoot_db(x * 10 ** (-3.02 / 20), SR, ceiling_db=-1.0) <= 0.1


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
