"""
Tests for calibrate_impulse pure helpers (note generation + latency-from-steps). The
live orchestration (LiveClient click track) needs Ableton and isn't unit-tested. Run:
    python -m unittest test_calibrate_impulse
"""

import unittest

from calibrate_impulse import (click_notes, detect_env_onsets, interp_beats,
                               latency_from_onsets, latency_from_steps)
from test_calibrate_latency import synth_steps


class TestClickNotes(unittest.TestCase):
    def test_notes_land_on_integer_beats(self):
        notes = click_notes(8)
        self.assertEqual(len(notes), 8)
        self.assertEqual([n["start_time"] for n in notes], [float(k) for k in range(8)])
        self.assertTrue(all(n["duration"] < 0.5 for n in notes))     # short = sharp onset


class TestLatencyFromSteps(unittest.TestCase):
    def test_recovers_on_grid_latency(self):
        # a hard-on-grid click delayed 0.06 beat by the pipeline @120 BPM -> 30 ms
        steps = synth_steps(n_beats=24, bpm=120.0, offset_beats=0.06)
        r = latency_from_steps(steps, current_latency=0.0)
        self.assertGreaterEqual(r["onsets"], 16)
        self.assertAlmostEqual(r["new_latency_s"], 0.030, delta=0.012)

    def test_adds_to_current_latency(self):
        # residual ~0 (on grid) with a nonzero current latency -> unchanged
        steps = synth_steps(n_beats=24, bpm=120.0, offset_beats=0.0)
        r = latency_from_steps(steps, current_latency=0.040)
        self.assertAlmostEqual(r["residual_s"], 0.0, delta=0.006)
        self.assertAlmostEqual(r["new_latency_s"], 0.040, delta=0.006)

    def test_skips_stopped_frames(self):
        r = latency_from_steps(synth_steps(n_beats=8, playing=False))
        self.assertEqual(r["onsets"], 0)


class TestOnsetStream(unittest.TestCase):
    def _env(self, onset_ts, fps=200, dur=2.0):
        # a 200 Hz envelope: ~0 between hits, a sharp spike at each onset time
        n = int(dur * fps)
        s = []
        for i in range(n):
            t = i / fps
            v = 1.0 if any(0 <= t - ot < 0.01 for ot in onset_ts) else 0.02
            s.append((t, v))
        return s

    def test_detect_env_onsets_subsample(self):
        got = detect_env_onsets(self._env([0.10, 0.60, 1.10]))
        self.assertEqual(len(got), 3)
        for want, g in zip([0.10, 0.60, 1.10], got):
            self.assertAlmostEqual(g, want, delta=0.006)      # ~5 ms resolution

    def test_interp_beats_linear(self):
        anchors = [(0.0, 0.0), (10.0, 20.0)]                  # 2 beats/s (120 BPM)
        self.assertAlmostEqual(interp_beats(anchors, 0.5), 1.0, places=6)
        self.assertAlmostEqual(interp_beats(anchors, 5.0), 10.0, places=6)

    def test_latency_from_onsets_recovers(self):
        # onsets 0.05 beat past each integer beat @120 BPM -> 25 ms latency
        anchors = [(0.0, 0.0), (10.0, 20.0)]                  # beat = 2 * t_wall
        onset_ts = [(k + 0.05) / 2.0 for k in range(1, 12)]   # wall time of beat k+0.05
        r = latency_from_onsets(onset_ts, anchors, bpm=120.0)
        self.assertEqual(r["usable"], 11)
        self.assertAlmostEqual(r["latency_s"], 0.025, delta=0.004)
        self.assertLess(r["spread_s"], 0.005)


if __name__ == "__main__":
    unittest.main()
