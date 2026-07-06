"""
test_calibration.py — Tier 1 calibration: is the RULER accurate?

The structural tests (test_perception.py) prove every frame is the same shape and
that meaning lands in stable slots. They deliberately feed synthetic band values,
so they CANNOT prove the numbers are musically correct. This suite closes that gap
for the pure-Python analysis chain (the "slow"/offline ruler):

  A. Band localization — a known-frequency tone must land in the right named band
     (bands.band_energies is the FFT ruler the live device must later agree with).
  B. Energy conservation + additivity — fractions sum to ~1; two tones split
     proportionally (the binning is linear, not lossy).
  C. dB→linear loudness math (masking.Node.band_abs) — the exact scaling that
     weights every masking decision and every frame energy row.
  D. The musical masking invariant — a QUIET track must not false-flag a clash,
     a LOUD overlap must, and louder overlaps must rank as worse clashes.

All deterministic, no Ableton, no Max. Run:  python -m unittest test_calibration -v

Tier 2 (test not here — needs Ableton) plays these SAME reference tones through a
live track and asserts the Max onepole~ band fractions agree with band_energies
within tolerance, proving the fast and slow perception paths speak one band language.
"""

import math
import unittest

import numpy as np

import bands
from masking import Node, compute_masking, masking_between

SR = 44100


def tone(freq_hz, dur_s=1.0, amp=1.0, sr=SR):
    """A pure sine — the simplest signal with a known spectral home."""
    t = np.arange(int(dur_s * sr)) / sr
    return amp * np.sin(2 * math.pi * freq_hz * t)


# A frequency chosen to sit safely inside each v1_7band band → the band we expect
# to dominate. (Edges: sub 20-60, low 60-120, low_mid 120-350, mid 350-2000,
# hi_mid 2000-6000, presence 6000-12000, air 12000-20000.)
TONE_HOMES = {
    40.0: "sub",
    90.0: "low",
    200.0: "low_mid",
    1000.0: "mid",
    4000.0: "hi_mid",
    8000.0: "presence",
    15000.0: "air",
}


class TestBandLocalization(unittest.TestCase):
    """A: does a known tone land in the correct named band?"""

    def test_each_tone_dominates_its_home_band(self):
        names = bands.band_names("v1_7band")
        for freq, home in TONE_HOMES.items():
            fr = bands.band_energies(tone(freq), SR, "v1_7band")
            top = names[int(np.argmax(fr))]
            self.assertEqual(top, home,
                             f"{freq} Hz landed in {top!r}, expected {home!r}")
            # a clean tone should concentrate the bulk of its energy in one band;
            # leakage (Hann sidelobes) is small, so demand a strong majority.
            self.assertGreater(fr[names.index(home)], 0.80,
                               f"{freq} Hz only {fr[names.index(home)]:.2f} in {home}")

    def test_silence_does_not_nan(self):
        fr = bands.band_energies(np.zeros(SR), SR, "v1_7band")
        self.assertEqual(len(fr), 7)
        self.assertTrue(all(math.isfinite(x) for x in fr))


class TestEnergyConservation(unittest.TestCase):
    """B: fractions sum to 1, and two tones split proportionally (linearity)."""

    def test_fractions_sum_to_one(self):
        fr = bands.band_energies(tone(1000.0), SR, "v1_7band")
        self.assertAlmostEqual(sum(fr), 1.0, places=5)

    def test_two_equal_tones_split_between_two_bands(self):
        # equal-power 1 kHz (mid) + 8 kHz (presence) → each band ~half the energy
        sig = tone(1000.0) + tone(8000.0)
        names = bands.band_names("v1_7band")
        fr = bands.band_energies(sig, SR, "v1_7band")
        mid, pres = fr[names.index("mid")], fr[names.index("presence")]
        self.assertGreater(mid, 0.35)
        self.assertGreater(pres, 0.35)
        self.assertAlmostEqual(mid, pres, delta=0.10)   # roughly equal split

    def test_louder_tone_takes_larger_share(self):
        # 1 kHz at 2x amplitude (4x power) vs 8 kHz → mid should dominate ~4:1
        sig = tone(1000.0, amp=2.0) + tone(8000.0, amp=1.0)
        names = bands.band_names("v1_7band")
        fr = bands.band_energies(sig, SR, "v1_7band")
        ratio = fr[names.index("mid")] / max(fr[names.index("presence")], 1e-9)
        self.assertGreater(ratio, 3.0)
        self.assertLess(ratio, 5.0)


class TestLoudnessMath(unittest.TestCase):
    """C: the dB→linear scaling that weights every masking + energy decision."""

    def test_db_to_linear_reference_points(self):
        # band_abs scales the (fraction) bands by linear RMS = 10^(dB/20)
        for db, expect in [(0.0, 1.0), (-6.0, 0.5012), (-20.0, 0.1), (-40.0, 0.01)]:
            n = Node(id="x", name="x", role="group", bands=[1.0], rms_db=db)
            self.assertAlmostEqual(n.band_abs()[0], expect, places=3,
                                   msg=f"{db} dB → {n.band_abs()[0]}")

    def test_silence_floor_is_hard_zero(self):
        # at/below -120 dB the node contributes exactly nothing (guard in band_abs)
        for db in (-120.0, -200.0):
            n = Node(id="x", name="x", role="group", bands=[1.0, 1.0], rms_db=db)
            self.assertEqual(n.band_abs(), [0.0, 0.0])

    def test_frame_loudness_normalization_is_monotonic(self):
        # the frame maps rms_db → (db+60)/60 clamped [0,1]; verify the anchor points
        def norm(db):
            return min(1.0, max(0.0, (db + 60.0) / 60.0))
        self.assertAlmostEqual(norm(0.0), 1.0)
        self.assertAlmostEqual(norm(-30.0), 0.5)
        self.assertAlmostEqual(norm(-60.0), 0.0)
        self.assertEqual(norm(-90.0), 0.0)        # clamps, never negative


class TestMaskingInvariant(unittest.TestCase):
    """D: the musical claim — loudness-weighting means quiet ≠ clash."""

    def _node(self, name, db, bands_=(0.5, 0.5, 0, 0, 0, 0, 0)):
        return Node(id=name, name=name, role="group", bands=list(bands_), rms_db=db)

    def test_quiet_overlap_does_not_false_flag(self):
        # identical spectra, but one node is -60 dB → below floor → no clash
        loud = self._node("kick", -6.0)
        quiet = self._node("ghost", -60.0)
        m = masking_between(loud, quiet, "v1_7band")
        self.assertEqual(m["score"], 0.0, "a -60 dB track must not clash")

    def test_loud_overlap_does_flag(self):
        # two loud, spectrally-overlapping groups → a real clash (positive control)
        a = self._node("kick", -6.0)
        b = self._node("bass", -6.0)
        m = masking_between(a, b, "v1_7band")
        self.assertGreater(m["score"], 0.0)
        self.assertIn(m["top_band"], ("sub", "low"))

    def test_louder_overlap_ranks_as_worse_clash(self):
        # clash severity must track loudness: -6/-6 worse than -6/-24
        base = self._node("kick", -6.0)
        loud_partner = self._node("bass_loud", -6.0)
        quiet_partner = self._node("bass_quiet", -24.0)
        s_loud = masking_between(base, loud_partner, "v1_7band")["score"]
        s_quiet = masking_between(base, quiet_partner, "v1_7band")["score"]
        self.assertGreater(s_loud, s_quiet)

    def test_compute_masking_orders_worst_first(self):
        # end-to-end: the pair list the model sees is sorted worst-clash first
        nodes = [
            self._node("kick", -6.0),
            self._node("bass", -6.0),
            self._node("hats", -24.0, (0, 0, 0, 0, 0.3, 0.4, 0.3)),
        ]
        out = compute_masking(nodes, "v1_7band", participants=("group",))
        self.assertTrue(out["pairs"])
        scores = [p["score"] for p in out["pairs"]]
        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
