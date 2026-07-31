"""
Tests for perception_metadata — the delta-encoded parameter-automation stream.
Pure Python (no daemon/Ableton). Run: python -m unittest test_perception_metadata
"""

import tempfile
import unittest
from pathlib import Path

import perception_metadata as pm


def _snap(lfo, freq):
    """compact get_all_device_parameters shape: params are [idx, value, automation_state]."""
    return {"tracks": [{"track_index": 0, "devices": [
        {"path": "0/0/0", "params": [[0, 1.0, 0], [1, lfo, 1]]},   # LFO automated (nested)
        {"path": "1", "params": [[0, 1.0, 0], [1, freq, 2]]},      # freq overridden
    ]}]}


def _rec(tmp, **over):
    ov = {"metadata_dir": str(tmp)}
    ov.update(over)
    return pm.MetadataRecorder(session_id="s", override=ov)


def _tr(bar, beat, playing=True, t=1.0):
    return {"t_wall": t, "bar": bar, "beat": beat, "playing": playing}


class TestDeltaEncoding(unittest.TestCase):
    def test_keyframe_then_only_changed_params(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp)
            r.on_sample(_snap(0.30, 0.50), _tr(5, 0.0))   # tick0 keyframe (all 4)
            r.on_sample(_snap(0.40, 0.50), _tr(5, 1.0))   # tick1 LFO moved
            r.on_sample(_snap(0.40, 0.50), _tr(5, 2.0))   # tick2 nothing moved -> skipped
            r.on_sample(_snap(0.40, 0.65), _tr(5, 3.0))   # tick3 freq moved
            r.flush(); r.close()
            recs = pm.load_params(Path(tmp) / "s")["records"]
            self.assertEqual(len(recs), 3)                # empty tick2 dropped
            self.assertTrue(recs[0]["keyframe"])
            self.assertEqual(len(recs[0]["changes"]), 4)
            self.assertEqual(recs[1]["changes"], [[0, "0/0/0", 1, 0.4, 1]])
            self.assertEqual(recs[2]["changes"], [[0, "1", 1, 0.65, 2]])

    def test_join_coordinate_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp)
            r.on_sample(_snap(0.30, 0.50), _tr(5, 0.0, t=12.3))
            r.flush(); r.close()
            rec = pm.load_params(Path(tmp) / "s")["records"][0]
            self.assertEqual((rec["t_wall"], rec["bar"], rec["beat"]), (12.3, 5, 0.0))


class TestGatingAndReconstruct(unittest.TestCase):
    def test_only_when_playing_skips_stopped_but_keeps_keyframe(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp, metadata_only_when_playing=True)
            r.on_sample(_snap(0.30, 0.50), _tr(5, 0.0, playing=False))   # tick0 keyframe kept
            r.on_sample(_snap(0.99, 0.50), _tr(5, 1.0, playing=False))   # stopped -> skipped
            r.flush(); r.close()
            recs = pm.load_params(Path(tmp) / "s")["records"]
            self.assertEqual(len(recs), 1)
            self.assertTrue(recs[0]["keyframe"])

    def test_reconstruct_at_holds_last_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp)
            r.on_sample(_snap(0.30, 0.50), _tr(5, 0.0))
            r.on_sample(_snap(0.40, 0.50), _tr(5, 1.0))
            r.on_sample(_snap(0.40, 0.65), _tr(5, 3.0))
            r.flush(); r.close()
            recs = pm.load_params(Path(tmp) / "s")["records"]
            state = pm.reconstruct_at(recs, upto_tick=1)     # after LFO moved, before freq moved
            self.assertEqual(state[(0, "0/0/0", 1)], 0.4)
            self.assertEqual(state[(0, "1", 1)], 0.5)        # freq still original (held)


class TestKeyframeFastInterplay(unittest.TestCase):
    """The 'both' capture: tick0 full keyframe, fast automated-only ticks in between, then
    a periodic full snapshot that catches a NON-automation change the fast ticks miss."""

    def test_full_then_automated_only_then_full_catches_manual_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp)
            # tick0: FULL snapshot (both params present) -> keyframe baselines all
            r.on_sample(_snap(0.30, 0.50), _tr(5, 0.0))
            # tick1: automated-only fast tick -> ONLY the automated LFO param is present+moved
            r.on_sample({"tracks": [{"track_index": 0, "devices": [
                {"path": "0/0/0", "params": [[1, 0.40, 1]]}]}]}, _tr(5, 1.0))
            # tick2: FULL snapshot again -> a NON-automated param (freq idx1 path"1") changed
            #        (a manual tweak the fast ticks would never see) -> caught here
            r.on_sample(_snap(0.40, 0.72), _tr(5, 2.0))
            r.flush(); r.close()
            recs = pm.load_params(Path(tmp) / "s")["records"]
            state = pm.reconstruct_at(recs, upto_tick=2)
            self.assertEqual(state[(0, "0/0/0", 1)], 0.4)     # automated move (from fast tick)
            self.assertEqual(state[(0, "1", 1)], 0.72)        # non-automation move (from full snap)
            # the fast tick emitted only the one automated param
            self.assertEqual(recs[1]["changes"], [[0, "0/0/0", 1, 0.4, 1]])


class TestManifest(unittest.TestCase):
    def test_manifest_written_and_shaped(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp)
            r.on_sample(_snap(0.3, 0.5), _tr(5, 0.0))
            r.flush(); r.close()
            man = pm.load_params(Path(tmp) / "s")["manifest"]
            self.assertEqual(man["schema_version"], "sim.param-stream.v1")
            for k in ("encoding", "join", "line_schema", "automation_state"):
                self.assertIn(k, man)


if __name__ == "__main__":
    unittest.main()
