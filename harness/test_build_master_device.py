"""
Tests for the specialized master device (build_master_device) + the end goal it
serves: feeding the bridge the /mix/* contract this device emits must REVIVE the bar
cache (the bug where the per-track biquad Hub on the master starved it). Pure Python,
no Max/Ableton. Run: python -m unittest test_build_master_device
"""

import json
import unittest

import bands
import build_master_device as bmd
from mix_analysis_bridge import MixAnalysisBridge


def _patch_texts():
    bmd.main()                                   # regenerate from the base hub
    d = json.loads(bmd.OUT.read_text())          # must round-trip as valid JSON
    return [b["box"].get("text", "") for b in d["patcher"]["boxes"]]


class TestMasterDevicePatch(unittest.TestCase):
    def setUp(self):
        self.texts = _patch_texts()

    def test_emits_mix_audio_contract(self):
        # the /mix/* audio messages the bar cache consumes (levels/stereo -> finalize +
        # samples; spectrum for the master's bar spectrum)
        for addr in ("prepend /mix/levels", "prepend /mix/stereo", "prepend /mix/spectrum"):
            self.assertIn(addr, self.texts, f"missing {addr}")

    def test_transport_cluster_stripped(self):
        # transport is LOM-sourced in the daemon now; the device must NOT emit /mix/transport
        # and must not carry the plugsync~/live.observer objects that threw the console error
        self.assertNotIn("prepend /mix/transport", self.texts)
        self.assertNotIn("plugsync~", self.texts)
        self.assertFalse(any("live.observer" in t for t in self.texts))
        self.assertFalse(any(t.startswith("live.path") for t in self.texts))

    def test_no_js_on_master(self):
        # the master carries NO js: track_ears.js's new LiveAPI("this_device ...") throws
        # "a project without a name..." on the master bus every meta-metro tick. The master
        # perception node is synthesized in the daemon (MixAnalysisBridge) instead.
        self.assertFalse(any(t.startswith("js ") for t in self.texts))
        self.assertNotIn("prepend spectrum", self.texts)   # no /track/* dual-emit tags

    def test_calibrated_biquad_bank_present(self):
        n = bands.n_bands()
        biquads = [t for t in self.texts if t.startswith("biquad~ ")]
        self.assertEqual(len(biquads), n, f"expected {n} bandpass filters")
        # coefficients are real numbers (calibration baked in), not placeholders
        coeffs = biquads[0].split()[1:]
        self.assertEqual(len(coeffs), 5)                 # ff0 ff1 ff2 fb1 fb2
        self.assertTrue(any(float(c) != 0.0 for c in coeffs))


class TestBridgeBarCacheRevival(unittest.TestCase):
    """The whole point: given the /mix/* stream this device emits, the bridge caches
    bars again. Drives the handlers directly (no socket) exactly as OSC would."""

    def test_mix_stream_caches_a_bar(self):
        b = MixAnalysisBridge(port=0)
        # enter bar 5 (no samples yet -> nothing to finalize)
        b.handle_transport("/mix/transport", 1, 120.0, 5, 0.0)
        self.assertEqual(len(b.bar_cache.cache), 0)
        # a few /mix/levels + /mix/stereo frames arrive during the bar
        for _ in range(4):
            b.handle_levels("/mix/levels", -12.0, -12.5, -6.0, -6.2, 0.5, 0.1)
            b.handle_stereo("/mix/stereo", 0.42, 0.5, 0.1)
        # bar flips to 6 -> bar 5 finalizes into the cache
        b.handle_transport("/mix/transport", 1, 120.0, 6, 0.0)
        self.assertEqual(len(b.bar_cache.cache), 1)
        self.assertIn(5, b.bar_cache.cache)
        cached = b.bar_cache.cache[5]
        self.assertAlmostEqual(cached.rms_l, -12.0, places=5)   # real level, not the -100 default
        self.assertAlmostEqual(cached.correlation, 0.42, places=5)

    def test_mix_stream_synthesizes_master_node(self):
        # with no js on the device, the bridge must build the master perception node from
        # /mix/* so the frame/masking still see the master (role by kind, normalized bands)
        b = MixAnalysisBridge(port=0)
        b.handle_levels("/mix/levels", -8.0, -8.0, -3.0, -3.0, 0.5, 0.1)
        b.handle_spectrum("/mix/spectrum", 0.1, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0)
        b.handle_stereo("/mix/stereo", 0.3, 0.5, 0.1)
        m = b.tracks.get("master")
        self.assertIsNotNone(m)
        self.assertEqual(m.kind, "master")
        self.assertAlmostEqual(m.rms_db, -8.0, places=5)
        self.assertAlmostEqual(sum(m.bands), 1.0, places=5)   # raw RMS -> normalized fractions
        self.assertAlmostEqual(m.correlation, 0.3, places=5)

    def test_transport_without_levels_caches_nothing(self):
        # reproduces the reported bug: transport advances but no /mix/levels -> no cache
        b = MixAnalysisBridge(port=0)
        b.handle_transport("/mix/transport", 1, 120.0, 5, 0.0)
        b.handle_transport("/mix/transport", 1, 120.0, 6, 0.0)
        b.handle_transport("/mix/transport", 1, 120.0, 7, 0.0)
        self.assertEqual(len(b.bar_cache.cache), 0)


class TestLomTransport(unittest.TestCase):
    """The daemon sources transport from the LOM (Remote Script) because the per-device
    plugsync~/live.observer is unreliable on fresh M4L loads. set_transport drives the
    bar cache; once lom_transport is set, the device's stale /mix/transport is ignored."""

    def test_set_transport_drives_bar_cache(self):
        b = MixAnalysisBridge(port=0)
        b.set_transport(1, 126.0, 40, 0.0)               # enter bar 40 (LOM says playing)
        for _ in range(3):
            b.handle_levels("/mix/levels", -9.0, -9.0, -3.0, -3.0, 0.5, 0.1)
        b.set_transport(1, 126.0, 41, 0.0)               # bar flip -> bar 40 finalizes
        self.assertIn(40, b.bar_cache.cache)
        self.assertAlmostEqual(b.bpm, 126.0, places=5)   # tempo tracks the LOM, not 120 default

    def test_lom_gate_ignores_device_transport(self):
        # once the LOM poller owns transport, the device's frozen /mix/transport is a no-op
        b = MixAnalysisBridge(port=0)
        b.lom_transport = True
        b.bpm = 126.0                                    # sentinel: LOM-sourced value
        b.handle_transport("/mix/transport", 0, 120.0, 16, 0.0)   # device's stale values
        self.assertEqual(b.bpm, 126.0)                   # device's 120 did NOT overwrite it
        self.assertEqual(b.current_bar, 0)               # device never moved the bar
        # the LOM poller still drives it through the gate
        b.set_transport(1, 126.0, 44, 2.0)
        self.assertEqual(b.current_bar, 44)


if __name__ == "__main__":
    unittest.main()
