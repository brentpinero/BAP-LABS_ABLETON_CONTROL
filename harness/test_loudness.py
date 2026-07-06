"""
Tests for loudness.py — invariants + a couple of absolute BS.1770 anchor points.
Pure Python (numpy/scipy/pyloudnorm), no Ableton. Run: python -m unittest test_loudness -v
"""

import math
import unittest

import numpy as np

import loudness

SR = 44100


def sine(freq, dur_s, amp, sr=SR):
    t = np.arange(int(dur_s * sr)) / sr
    return amp * np.sin(2 * math.pi * freq * t)


class TestInvariants(unittest.TestCase):
    def test_true_peak_ge_sample_peak(self):
        # inter-sample peaks can only be >= sample peaks
        x = sine(997, 4.0, 0.9)                    # 997 Hz: non-integer period → inter-sample overs
        self.assertGreaterEqual(loudness.true_peak_dbtp(x, SR) + 1e-6,
                                loudness.sample_peak_dbfs(x))

    def test_crest_factor_of_sine_is_3db(self):
        # a pure sine has peak/RMS = sqrt(2) = 3.01 dB
        x = sine(1000, 4.0, 0.5)
        self.assertAlmostEqual(loudness.sample_peak_dbfs(x) - loudness.rms_dbfs(x), 3.01, delta=0.1)

    def test_louder_is_higher_lufs(self):
        quiet = loudness.integrated_lufs(sine(1000, 4.0, 0.05), SR)
        loud = loudness.integrated_lufs(sine(1000, 4.0, 0.5), SR)
        self.assertGreater(loud, quiet)
        self.assertAlmostEqual(loud - quiet, 20.0, delta=1.0)   # 10x amplitude ≈ +20 LU

    def test_plr_equals_truepeak_minus_lufs(self):
        x = sine(1000, 4.0, 0.3)
        r = loudness.analyze(x, SR)
        self.assertAlmostEqual(r["plr_db"], r["true_peak_dbtp"] - r["lufs_integrated"], delta=0.05)

    def test_over_ceiling_flag(self):
        hot = loudness.analyze(sine(1000, 4.0, 1.0), SR)     # full-scale → over -1 dBTP
        self.assertTrue(hot["over_minus1_dbtp"])
        quiet = loudness.analyze(sine(1000, 4.0, 0.1), SR)   # -20 dBFS → well under
        self.assertFalse(quiet["over_minus1_dbtp"])

    def test_silence(self):
        z = np.zeros(SR * 4)
        r = loudness.analyze(z, SR)
        self.assertEqual(r["lufs_integrated"], loudness.SILENCE_DB)
        self.assertEqual(r["sample_peak_dbfs"], loudness.SILENCE_DB)


class TestAbsoluteAnchor(unittest.TestCase):
    def test_minus20_sine_integrated_lufs(self):
        # -20 dBFS-peak 1 kHz sine, dual-mono: sine RMS is -3 dB, but BS.1770 sums
        # L+R (+3 dB), so they cancel → integrated ≈ -20 LUFS (K-weight ~0 @1kHz).
        # (This anchor confirms pyloudnorm applies proper channel-weighted BS.1770.)
        x = sine(1000, 5.0, 0.1)
        lufs = loudness.integrated_lufs(x, SR)
        self.assertAlmostEqual(lufs, -20.0, delta=1.0)

    def test_stereo_and_mono_agree(self):
        mono = sine(1000, 4.0, 0.3)
        stereo = np.column_stack([mono, mono])
        self.assertAlmostEqual(loudness.integrated_lufs(mono, SR),
                               loudness.integrated_lufs(stereo, SR), delta=0.2)

    def test_lra_small_for_steady_tone(self):
        # a constant-level tone has ~no loudness range
        self.assertLess(loudness.loudness_range(sine(1000, 6.0, 0.3), SR), 1.0)


if __name__ == "__main__":
    unittest.main()
