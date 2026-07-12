"""
Tests for calibrate_impulse pure helpers (note generation + latency-from-steps). The
live orchestration (LiveClient click track) needs Ableton and isn't unit-tested. Run:
    python -m unittest test_calibrate_impulse
"""

import unittest

from calibrate_impulse import click_notes, latency_from_steps
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


if __name__ == "__main__":
    unittest.main()
