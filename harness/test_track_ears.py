"""
Tests for the per-track live-ears backbone: bands contract, masking math, and the
bridge's per-track OSC routing / snapshot. Pure-Python (no Max, no Ableton).

Run:  python -m unittest test_track_ears -v
"""

import unittest

import bands
from masking import Node, compute_masking, masking_between
from mix_analysis_bridge import MixAnalysisBridge


class TestBandsContract(unittest.TestCase):
    def test_default_scheme_is_7(self):
        self.assertEqual(bands.n_bands(), 7)
        self.assertEqual(bands.band_names()[0], "sub")
        self.assertEqual(bands.band_names()[-1], "air")

    def test_resolution_is_swappable(self):
        # Register a coarser scheme at runtime; accessors adapt with no other change.
        bands.SCHEMES["test_3band"] = [("lo", 20, 250), ("mid", 250, 4000), ("hi", 4000, 20000)]
        self.assertEqual(bands.n_bands("test_3band"), 3)
        self.assertTrue(bands.validate([0.3, 0.4, 0.3], "test_3band"))
        self.assertFalse(bands.validate([0.3, 0.4], "test_3band"))
        del bands.SCHEMES["test_3band"]

    def test_band_energies_sum_to_one(self):
        import numpy as np
        sr = 48000
        t = np.linspace(0, 1, sr, endpoint=False)
        sig = np.sin(2 * np.pi * 80 * t).astype("float32")   # 80 Hz -> 'low' band
        e = bands.band_energies(sig, sr)
        self.assertEqual(len(e), 7)
        self.assertAlmostEqual(sum(e), 1.0, places=5)
        self.assertEqual(max(range(len(e)), key=lambda i: e[i]), 1)  # 'low' dominates


class TestMasking(unittest.TestCase):
    def _bands(self, **kv):
        v = [0.0] * 7
        for name, val in kv.items():
            v[bands.band_names().index(name)] = val
        return v

    def test_kick_vs_bass_clash_in_low(self):
        kick = Node("1", "Kick", "group", self._bands(sub=0.6, low=0.3), rms_db=-6)
        bass = Node("2", "Bass", "group", self._bands(sub=0.5, low=0.4), rms_db=-6)
        hats = Node("3", "Hats", "group", self._bands(presence=0.5, air=0.4), rms_db=-12)
        m = compute_masking([kick, bass, hats])
        # worst clash should be kick vs bass, and in a low band
        self.assertTrue(m["pairs"])
        worst = m["pairs"][0]
        self.assertEqual({worst["a"], worst["b"]}, {"Kick", "Bass"})
        self.assertIn(worst["top_band"], ("sub", "low"))

    def test_quiet_track_does_not_false_clash(self):
        loud = Node("1", "Bass", "group", self._bands(low=0.8), rms_db=-6)
        quiet = Node("2", "Pad", "group", self._bands(low=0.8), rms_db=-60)
        m = masking_between(loud, quiet)
        self.assertEqual(m["score"], 0.0)   # pad too quiet to mask

    def test_master_congestion(self):
        a = Node("1", "A", "group", self._bands(mid=0.7), rms_db=-6)
        b = Node("2", "B", "group", self._bands(mid=0.7), rms_db=-6)
        c = Node("3", "C", "group", self._bands(mid=0.7), rms_db=-6)
        m = compute_masking([a, b, c])
        mid = next(x for x in m["master_congestion"] if x["band"] == "mid")
        self.assertEqual(mid["congestion"], 3)


class TestBridgeRouting(unittest.TestCase):
    def test_per_track_osc_populates_state_and_masking(self):
        br = MixAnalysisBridge()
        # two groups clashing in the low end + a bright group
        br.handle_track_meta("/track/10/meta", "Drums", "group", "-1")
        br.handle_track_levels("/track/10/levels", -6.0, -6.0, -3.0, -3.0, 0.5, 0.1)
        br.handle_track_spectrum("/track/10/spectrum", 0.6, 0.3, 0.05, 0.03, 0.01, 0.005, 0.005)

        br.handle_track_meta("/track/20/meta", "Bass", "group", "-1")
        br.handle_track_levels("/track/20/levels", -6.0, -6.0, -3.0, -3.0, 0.5, 0.1)
        br.handle_track_spectrum("/track/20/spectrum", 0.5, 0.4, 0.05, 0.03, 0.01, 0.005, 0.005)

        self.assertEqual(len(br.tracks), 2)
        self.assertEqual(br.tracks["10"].name, "Drums")
        self.assertEqual(len(br.tracks["10"].bands), 7)

        snap = br.build_tracks_snapshot()
        self.assertEqual(snap["band_scheme"], "v1_7band")
        self.assertIn("10", snap["tracks"])
        self.assertTrue(snap["masking"]["pairs"])
        self.assertEqual({snap["masking"]["pairs"][0]["a"], snap["masking"]["pairs"][0]["b"]},
                         {"Drums", "Bass"})

    def test_variable_band_length_is_accepted(self):
        # A device declaring a different resolution just stores that many bands.
        br = MixAnalysisBridge()
        br.handle_track_spectrum("/track/5/spectrum", *([0.1] * 10))
        self.assertEqual(len(br.tracks["5"].bands), 10)

    def test_master_bus_backcompat(self):
        br = MixAnalysisBridge()
        br.handle_levels("/mix/levels", -8.0, -8.0, -4.0, -4.0, 0.4, 0.1)
        self.assertAlmostEqual(br.current_analysis.rms_l, -8.0)

    def test_osc_wildcard_routing(self):
        """Guards the real wire path: /track/<id>/* must route through python-osc's
        Dispatcher wildcard matching, not just direct handler calls."""
        from pythonosc.dispatcher import Dispatcher
        br = MixAnalysisBridge()
        d = Dispatcher()
        d.map("/track/*/meta", br.handle_track_meta)
        d.map("/track/*/spectrum", br.handle_track_spectrum)

        def dispatch(addr, *args):
            for h in list(d.handlers_for_address(addr)):
                h.callback(addr, *args)

        dispatch("/track/42/meta", "Bass", "group", "-1")
        dispatch("/track/42/spectrum", *([0.1] * 7))
        self.assertIn("42", br.tracks)
        self.assertEqual(br.tracks["42"].name, "Bass")
        self.assertEqual(len(br.tracks["42"].bands), 7)


if __name__ == "__main__":
    unittest.main()
