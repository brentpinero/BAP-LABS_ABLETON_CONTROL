"""
Tests for calibrate_latency — measuring the audio->frame pipeline latency from a
recorded beat-locked trajectory. Pure Python (synthetic trajectory). Run:
    python -m unittest test_calibrate_latency
"""

import json
import tempfile
import unittest
from pathlib import Path

from calibrate_latency import (calibrate, detect_onsets, energy_series, phase,
                               residual_latency_s)


def synth_steps(n_beats=8, bpm=120.0, offset_beats=0.0, sig=4, fps=25, playing=True):
    """A synthetic 4-on-floor: a low-band kick spike at each integer beat + `offset_beats`
    (simulating the frame clock running `offset` ahead of the audio)."""
    fpb = fps * 60.0 / bpm                       # frames per beat
    total = int(n_beats * fpb)
    kick_frames = {int(round((k + offset_beats) * fpb)) for k in range(n_beats)}
    steps = []
    for i in range(total):
        abs_beat = i / fpb
        kick = i in kick_frames
        rms = -6.0 if kick else -32.0
        low = 0.85 if kick else 0.15
        bar = int(abs_beat // sig)
        steps.append({"step": i, "t_wall": i / fps, "playing": playing, "frame": {
            "playing": playing, "bpm": bpm, "bar": bar, "beat": abs_beat - bar * sig,
            "beats_per_bar": sig,
            "role_state": {"drums": {"bands": [low, low * 0.4, 0.0, 0.0, 0.0, 0.0, 0.0],
                                     "rms_db": rms, "width": 0.0}}}})
    return steps


class TestPhaseMath(unittest.TestCase):
    def test_phase_signed_distance_to_nearest_beat(self):
        self.assertAlmostEqual(phase(4.0), 0.0)
        self.assertAlmostEqual(phase(4.05), 0.05, places=6)
        self.assertAlmostEqual(phase(3.95), -0.05, places=6)

    def test_residual_zero_when_on_grid(self):
        self.assertAlmostEqual(residual_latency_s([0.0, 1.0, 2.0, 3.0], 120.0), 0.0)

    def test_residual_converts_beats_to_seconds(self):
        # +0.05 beat median @ 120 BPM -> 0.05 * 60/120 = 0.025 s
        self.assertAlmostEqual(residual_latency_s([0.05, 1.05, 2.05], 120.0), 0.025, places=4)


class TestOnsetDetection(unittest.TestCase):
    def test_finds_one_onset_per_beat(self):
        onsets = detect_onsets(energy_series(synth_steps(n_beats=8, offset_beats=0.0)))
        self.assertGreaterEqual(len(onsets), 6)           # ~8, allow edge losses
        for b in onsets:                                  # each lands near an integer beat
            self.assertLess(abs(phase(b)), 0.15)

    def test_energy_series_skips_stopped_frames(self):
        series = energy_series(synth_steps(n_beats=4, playing=False))
        self.assertEqual(series, [])


class TestCalibrateEndToEnd(unittest.TestCase):
    def _write(self, steps):
        d = tempfile.mkdtemp()
        sess = Path(d) / "sess_test"
        sess.mkdir()
        with (sess / "frames.jsonl").open("w") as fh:
            for s in steps:
                fh.write(json.dumps(s) + "\n")
        return sess

    def test_recovers_injected_latency(self):
        # frames whose kick lands 0.05 beat late (clock 0.05 beat ahead of audio) @120 BPM
        sess = self._write(synth_steps(n_beats=16, bpm=120.0, offset_beats=0.05))
        r = calibrate(sess, current_latency=0.0)
        self.assertGreaterEqual(r["onsets"], 10)
        self.assertAlmostEqual(r["new_latency_s"], 0.025, delta=0.012)   # ~25 ms recovered

    def test_converges_when_already_calibrated(self):
        # on-grid onsets -> residual ~0, latency unchanged
        sess = self._write(synth_steps(n_beats=16, bpm=120.0, offset_beats=0.0))
        r = calibrate(sess, current_latency=0.030)
        self.assertAlmostEqual(r["residual_s"], 0.0, delta=0.006)
        self.assertAlmostEqual(r["new_latency_s"], 0.030, delta=0.006)


if __name__ == "__main__":
    unittest.main()
