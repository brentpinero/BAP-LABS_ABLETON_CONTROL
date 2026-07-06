"""
Smoke tests for the probing harness (methodology guardrails, not the science).
Run: python -m unittest test_probe_frame
"""

import unittest

import numpy as np

import perception_frame as pf
import probe_frame as prb


class TestProbeHarness(unittest.TestCase):
    def test_scenarios_constant_frame_dim(self):
        want = pf.Frame.vector_len(pf.cfg("roles"), pf.cfg("band_scheme"))
        vecs = [v for v, _ in prb.gen_scenarios(20)]
        self.assertTrue(all(len(v) == want for v in vecs))

    def test_labels_present_and_varied(self):
        labs = [lab for _, lab in prb.gen_scenarios(40)]
        for key in ("vocal_buried", "tonal_tilt", "most_congested_band"):
            self.assertTrue(all(key in l for l in labs))
        # vocal_buried should take both values across 40 scenarios
        self.assertEqual(len({l["vocal_buried"] for l in labs}), 2)

    def test_selectivity_high_on_separable_low_on_random(self):
        # a feature that IS the label → high selectivity; pure noise → ~0
        rng = np.random.default_rng(0)
        y = rng.integers(0, 2, 300)
        X_signal = np.column_stack([y + rng.normal(0, 0.1, 300), rng.normal(0, 1, 300)])
        X_noise = rng.normal(0, 1, (300, 4))
        sig = prb.run_probe(X_signal, y, "signal")
        noise = prb.run_probe(X_noise, y, "noise")
        self.assertGreater(sig["real_acc"], 0.9)              # separable → probe learns it
        self.assertGreater(sig["selectivity"], 0.25)          # real >> control
        self.assertLess(abs(noise["selectivity"]), 0.2)       # noise → no selectivity
        self.assertGreater(sig["selectivity"], noise["selectivity"] + 0.2)


if __name__ == "__main__":
    unittest.main()
