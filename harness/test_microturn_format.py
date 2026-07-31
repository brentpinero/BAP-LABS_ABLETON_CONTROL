"""
Tests for microturn_format — re-arranging recorded perception steps into ~200ms
interleaved micro-turns (perception masked / action predicted). Pure Python. Run:
    python -m unittest test_microturn_format
"""

import tempfile
import unittest
from pathlib import Path

import perception_frame as pf
from mix_analysis_bridge import TrackState
from perception_frame import Frame
from microturn_format import (load_microturns, save_microturns, stream_text, to_microturns)

TR = {"bpm": 126.0, "bar": 5, "beat": 0.0, "beats_per_bar": 4, "playing": True}


def ts(tid, name, kind="audio", gid="-1"):
    return TrackState(track_id=str(tid), name=name, kind=kind, group_id=str(gid),
                      bands=[0.3, 0.25, 0.15, 0.1, 0.1, 0.05, 0.05],
                      rms_l=-8.0, rms_r=-8.0, mid_energy=0.5, side_energy=0.1)


def rec_step(i, playing=True, events=None):
    tracks = {"1": ts(1, "Drums", "group"), "2": ts(2, "Bass", "group")}
    f = pf.build_frame(tracks, dict(TR, beat=(i * 0.084) % 4, playing=playing)).to_dict()
    return {"step": i, "t_wall": 1000.0 + i * 0.04, "bar": f["bar"], "beat": f["beat"],
            "playing": playing, "frame": f, "events": events or []}


VLEN = len(Frame.from_dict(rec_step(0)["frame"]).to_vector())


class TestGrouping(unittest.TestCase):
    def test_groups_5_frames_per_microturn(self):
        mts = to_microturns([rec_step(i) for i in range(12)])
        self.assertEqual(len(mts), 3)                       # 5 + 5 + 2
        self.assertEqual([m["n_frames"] for m in mts], [5, 5, 2])
        self.assertEqual([m["mt"] for m in mts], [0, 1, 2])

    def test_vectors_are_per_frame_subtokens(self):
        mt = to_microturns([rec_step(i) for i in range(5)])[0]
        self.assertEqual(len(mt["perception"]["vectors"]), 5)   # 5 x 40ms sub-tokens
        self.assertEqual(len(mt["perception"]["vectors"][0]), VLEN)

    def test_preserves_stopped_frames(self):
        steps = [rec_step(0), rec_step(1, playing=False), rec_step(2), rec_step(3, playing=False)]
        mts = to_microturns(steps)
        self.assertEqual(sum(m["n_frames"] for m in mts), 4)

    def test_does_not_group_across_clock_gap(self):
        steps = [rec_step(i) for i in range(6)]
        steps[3]["t_wall"] += 1.0
        for i in range(4, 6):
            steps[i]["t_wall"] += 1.0
        mts = to_microturns(steps)
        self.assertEqual([m["n_frames"] for m in mts], [3, 3])
        self.assertFalse(mts[0]["discontinuity_before"])
        self.assertTrue(mts[1]["discontinuity_before"])

    def test_rejects_time_reversal(self):
        steps = [rec_step(0), rec_step(1)]
        steps[1]["t_wall"] = steps[0]["t_wall"]
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            to_microturns(steps)


class TestSchema(unittest.TestCase):
    def test_perception_masked_actions_predicted(self):
        mt = to_microturns([rec_step(i) for i in range(5)])[0]
        self.assertTrue(mt["loss_mask"]["perception"])          # observed -> masked (no loss)
        self.assertFalse(mt["loss_mask"]["actions"])            # predicted
        self.assertFalse(mt["loss_mask"]["reasoning"])
        self.assertFalse(mt["loss_mask"]["reply"])
        self.assertTrue(mt["loss_mask"]["tool_results"])
        self.assertTrue(mt["loss_mask"]["background"])
        self.assertTrue(mt["loss_mask"]["causal_context"])
        # action-out slots empty, awaiting SFT + action-pairing
        self.assertEqual((mt["reasoning"], mt["actions"], mt["reply"]), (None, [], None))
        self.assertEqual((mt["tool_results"], mt["background"]), ([], []))
        self.assertIn("text", mt["perception"])                 # LLM-readable mix state

    def test_causal_context_is_observed_and_preserved(self):
        steps = [rec_step(i) for i in range(5)]
        steps[0]["frame"]["causal_context"] = {
            "task": "causal_effect", "track_id": "2", "parent_group_id": "1",
            "return_ids": ["return:0"], "master_id": "master",
            "device": {"index": 1, "class": "eq_filter", "bypass": False},
            "intervention": {"kind": "parameter_sweep", "seed": 7},
        }
        mt = to_microturns(steps)[0]
        self.assertEqual(mt["causal_context"]["task"], "causal_effect")
        self.assertTrue(mt["loss_mask"]["causal_context"])

    def test_explicit_timing_metadata(self):
        mt = to_microturns([rec_step(i) for i in range(5)])[0]
        self.assertEqual(mt["schema_version"], "sim.microturn.v1")
        self.assertAlmostEqual(mt["duration_ms"], 200.0, places=3)
        self.assertEqual(mt["source_steps"], [0, 4])

    def test_malformed_frame_fails_loudly(self):
        step = rec_step(0)
        step["frame"] = {"playing": True}
        with self.assertRaisesRegex(ValueError, "malformed frame"):
            to_microturns([step])

    def test_events_aggregated_into_window(self):
        ev = {"type": "clip", "a": "drums", "bar": 5, "beat": 1.0}
        steps = [rec_step(0), rec_step(1, events=[ev]), rec_step(2)]
        mt = to_microturns(steps)[0]
        self.assertEqual([e["type"] for e in mt["perception"]["events"]], ["clip"])

    def test_sync_tags_and_time(self):
        mts = to_microturns([rec_step(i) for i in range(10)], sync_every=1)
        self.assertEqual([m["sync"] for m in mts], ["[T0]", "[T1]"])
        self.assertEqual(mts[0]["mt"], 0)                       # index carries elapsed time


class TestRoundTrip(unittest.TestCase):
    def test_save_load(self):
        mts = to_microturns([rec_step(i) for i in range(7)])
        with tempfile.TemporaryDirectory() as d:
            p = save_microturns(mts, Path(d) / "s.microturns.jsonl")
            back = load_microturns(p)
        self.assertEqual(len(back), len(mts))
        self.assertEqual(back[0]["loss_mask"], mts[0]["loss_mask"])

    def test_stream_text_renders(self):
        txt = stream_text(to_microturns([rec_step(i) for i in range(5)]))
        self.assertIn("PERCEPTION|masked", txt)
        self.assertIn("ACTION|predict", txt)


if __name__ == "__main__":
    unittest.main()
