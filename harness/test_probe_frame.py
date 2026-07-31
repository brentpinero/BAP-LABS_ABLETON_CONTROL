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


# ---- Stage 2: real recorded-data probe (ground truth + LOSO anti-leakage) ----
def _rec_step(beat, rms_by_role, pairs=None, events=None, roles=None):
    """A recorded-trajectory step dict shaped like perception_recorder writes."""
    roles = roles or ["master", "drums", "bass", "sub", "vox", "synth", "fx", "other"]
    role_state = {r: {"bands": [0.0] * 7, "rms_db": rms_by_role.get(r, -120.0), "width": 0.1}
                  for r in roles}
    return {"step": 0, "t_wall": 0.0, "bar": 0, "beat": beat, "playing": True,
            "frame": {"beat": beat, "beats_per_bar": 4, "roles": roles,
                      "role_state": role_state, "masking": {"pairs": pairs or []}},
            "events": events or []}


class TestRealGroundTruth(unittest.TestCase):
    NON_MASTER = ["drums", "bass", "sub", "vox", "synth", "fx", "other"]

    def test_loudest_role_argmax_over_rms(self):
        s = _rec_step(0.0, {"bass": -6.0, "vox": -18.0, "drums": -30.0})
        self.assertEqual(prb._loudest_role(s, self.NON_MASTER), self.NON_MASTER.index("bass"))

    def test_loudest_role_all_silent_is_skip(self):
        self.assertEqual(prb._loudest_role(_rec_step(0.0, {}), self.NON_MASTER), -1)

    def test_mask_intensity_is_peak_pair_score(self):
        self.assertAlmostEqual(
            prb._mask_intensity(_rec_step(0.0, {}, pairs=[{"score": 0.1}, {"score": 0.16}])), 0.16)
        self.assertEqual(prb._mask_intensity(_rec_step(0.0, {}, pairs=[])), 0.0)

    def test_transient_helper_and_beat_quadrant(self):
        self.assertTrue(prb._has_level_jump(_rec_step(0.0, {}, events=[{"type": "level_jump"}])))
        self.assertFalse(prb._has_level_jump(_rec_step(0.0, {}, events=[{"type": "other"}])))
        self.assertEqual(prb._beat_quadrant(_rec_step(2.7, {})), 2)   # floors into beat index
        self.assertEqual(prb._beat_quadrant(_rec_step(3.9, {})), 3)   # clamped to bpb-1


class TestRealProbeMethodology(unittest.TestCase):
    """Guardrails on the science, not the science: degeneracy + LOSO anti-leakage."""

    def _sessions_shared_rule(self, seed=0):
        """3 sessions where dim0 encodes the label the SAME way everywhere → LOSO generalizes."""
        rng = np.random.default_rng(seed)
        out = []
        for i in range(3):
            y = rng.integers(0, 2, 300)
            X = rng.normal(0, 1, (300, 6))
            X[:, 0] = (y * 2 - 1) + rng.normal(0, 0.2, 300)     # shared, session-invariant signal
            out.append({"name": f"s{i}", "X": X,
                        "targets": {"t": y.astype(float)}})
        return out

    def _sessions_session_specific(self, seed=1):
        """Label lives in a DIFFERENT column per session → leaky split inflates, LOSO can't."""
        rng = np.random.default_rng(seed)
        out = []
        for i in range(3):
            y = rng.integers(0, 2, 300)
            X = np.zeros((300, 6))
            X[:, i] = (y * 2 - 1) + rng.normal(0, 0.15, 300)    # only session i's column carries it
            out.append({"name": f"s{i}", "X": X,
                        "targets": {"t": y.astype(float)}})
        return out

    @staticmethod
    def _loso(sessions, target):
        """Build the precomputed pooled/leave-one-out matrices the caller owns, then probe."""
        pooled = np.vstack([s["X"] for s in sessions])
        train_X = [np.vstack([s["X"] for i, s in enumerate(sessions) if i != held])
                   for held in range(len(sessions))]
        return prb.run_probe_loso(sessions, target, pooled, train_X)

    def test_degeneracy_counts_dead_dims(self):
        X = np.random.default_rng(0).normal(0, 1, (500, 6))
        X[:, 2] = 4.2                                            # one constant column
        X[:, 5] = -1.0                                           # another
        rep = prb.degeneracy_report(X)
        self.assertEqual(rep["n_dead_dims"], 2)
        self.assertEqual(rep["n_live_dims"], 4)
        self.assertEqual(rep["n_dims"], 6)

    def test_loso_generalizes_on_shared_rule(self):
        r = self._loso(self._sessions_shared_rule(), "t")
        self.assertEqual(r["n_folds"], 3)                       # one held-out fold per session
        self.assertGreater(r["loso_mean"]["real_acc"], 0.85)   # shared rule → generalizes
        self.assertGreater(r["loso_mean"]["selectivity"], 0.3)

    def test_loso_does_not_leak_across_sessions(self):
        r = self._loso(self._sessions_session_specific(), "t")
        # leaky random split sees each session's own column → nearly perfect
        self.assertGreater(r["leaky_random_split"]["real_acc"], 0.85)
        # honest LOSO can't (held-out session's signal column is dead in the training sessions)
        self.assertLess(r["loso_mean"]["real_acc"], 0.7)
        # the whole point: leakage inflates the number
        self.assertGreater(r["leaky_random_split"]["real_acc"], r["loso_mean"]["real_acc"] + 0.2)


if __name__ == "__main__":
    unittest.main()
