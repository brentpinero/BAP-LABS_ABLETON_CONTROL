"""
Tests for content_roles — inferring a mix role from a spectral signature alone,
so projects with generic/unmappable track names still populate real role slots.
Pure Python. Run:  python -m unittest test_content_roles
"""

import unittest

import bands
from content_roles import classify, region_energy


# spectra in v1_7band order: sub low low_mid mid hi_mid presence air
def spec(sub=0, low=0, low_mid=0, mid=0, hi_mid=0, presence=0, air=0):
    v = [sub, low, low_mid, mid, hi_mid, presence, air]
    tot = sum(v) or 1.0
    return [x / tot for x in v]


class TestRegionFold(unittest.TestCase):
    def test_regions_sum_to_one(self):
        r = region_energy(spec(1, 1, 1, 1, 1, 1, 1))
        self.assertAlmostEqual(sum(r.values()), 1.0, places=6)

    def test_sub_low_fold_into_low_region(self):
        r = region_energy(spec(sub=0.5, low=0.5))
        self.assertAlmostEqual(r["low"], 1.0, places=6)
        self.assertAlmostEqual(r["hi"], 0.0, places=6)

    def test_air_folds_into_hi(self):
        r = region_energy(spec(presence=0.5, air=0.5))
        self.assertAlmostEqual(r["hi"], 1.0, places=6)


class TestClassify(unittest.TestCase):
    def test_sub(self):
        self.assertEqual(classify(spec(sub=0.7, low=0.25, low_mid=0.05), rms_db=-6), "sub")

    def test_bass(self):
        # low-heavy body, a little low-mid, negligible air
        self.assertEqual(classify(spec(sub=0.3, low=0.35, low_mid=0.25, mid=0.1), rms_db=-6), "bass")

    def test_drums_broadband(self):
        # kick low + snare mid/hi-mid + hats air => both ends lit
        self.assertEqual(classify(spec(sub=0.2, low=0.15, mid=0.2, hi_mid=0.2, presence=0.15, air=0.1),
                                  rms_db=-6), "drums")

    def test_vox_midrange(self):
        self.assertEqual(classify(spec(low_mid=0.1, mid=0.45, hi_mid=0.35, presence=0.1), rms_db=-6), "vox")

    def test_fx_hf_dominant(self):
        self.assertEqual(classify(spec(hi_mid=0.1, presence=0.4, air=0.5), rms_db=-6), "fx")

    def test_synth_is_catchall_tonal(self):
        # low-mid/mid body with little presence => not vox (mid+hi_mid < 0.5), not bass
        # (spread past 350 Hz): falls through to the tonal catch-all. (vox vs synth is
        # deliberately NOT separable by spectrum alone — that's the name tiebreak's job.)
        self.assertEqual(classify(spec(low_mid=0.45, mid=0.35, hi_mid=0.1, presence=0.1), rms_db=-6), "synth")

    def test_silence_is_other(self):
        self.assertEqual(classify(spec(sub=0.5, low=0.5), rms_db=-90), "other")
        self.assertEqual(classify([], rms_db=-6), "other")

    def test_scheme_agnostic(self):
        # a 3-band scheme still folds by center frequency, no hardcoded band count
        bands.SCHEMES["cr_3band"] = [("lo", 20, 200), ("md", 200, 4000), ("hi", 4000, 20000)]
        try:
            self.assertEqual(classify([0.9, 0.08, 0.02], rms_db=-6, scheme="cr_3band"), "sub")
        finally:
            del bands.SCHEMES["cr_3band"]


if __name__ == "__main__":
    unittest.main()
