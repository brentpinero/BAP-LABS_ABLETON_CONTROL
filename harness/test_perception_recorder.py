"""
Tests for perception_recorder — persisting the live perception stream to a
session-scoped trajectory JSONL and reading it back. Pure Python (no daemon/OSC).
Run: python -m unittest test_perception_recorder
"""

import tempfile
import unittest
from pathlib import Path

import perception_frame as pf
from mix_analysis_bridge import TrackState
from perception_frame import Frame
from perception_stream import Event
from perception_recorder import (TrajectoryRecorder, frames_of, iter_trajectory,
                                 load_trajectory)

TRANSPORT = {"bpm": 128.0, "bar": 4, "beat": 1.0, "beats_per_bar": 4, "playing": True}


def ts(tid, name, kind="audio", gid="-1", b=None, rms=-8.0):
    return TrackState(track_id=str(tid), name=name, kind=kind, group_id=str(gid),
                      bands=(b if b is not None else [0.3, 0.25, 0.15, 0.1, 0.1, 0.05, 0.05]),
                      rms_l=rms, rms_r=rms, mid_energy=0.5, side_energy=0.1)


def make_frame(bar=4, playing=True):
    tracks = {"1": ts(1, "Drums", "group"), "2": ts(2, "Bass", "group")}
    tr = dict(TRANSPORT, bar=bar, playing=playing)
    return pf.build_frame(tracks, tr)


def _rec(tmp, **over):
    ov = {"trajectory_dir": str(tmp)}
    ov.update(over)
    return TrajectoryRecorder(session_id="test", override=ov)


class TestRecordAndLoad(unittest.TestCase):
    def test_records_frames_and_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp)
            for i in range(5):
                r.on_frame(make_frame(bar=4 + i), [])
            self.assertEqual(r.flush(), 5)
            r.close()
            traj = load_trajectory(Path(tmp) / "test")
            self.assertEqual(len(traj["steps"]), 5)
            self.assertEqual([s["step"] for s in traj["steps"]], [0, 1, 2, 3, 4])
            self.assertEqual([s["bar"] for s in traj["steps"]], [4, 5, 6, 7, 8])
            # manifest pins the schema; vector_len matches the frame geometry
            man = traj["manifest"]
            self.assertEqual(man["vector_len"],
                             Frame.vector_len(man["roles"], man["band_scheme"]))
            # frames reconstruct into real Frame objects
            frames = frames_of(traj["steps"])
            self.assertEqual(len(frames), 5)
            self.assertEqual(len(frames[0].to_vector()), man["vector_len"])

    def test_flush_is_incremental_no_dupes(self):
        # regression vs the drain_since() whole-buffer dump: each frame written once
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp)
            r.on_frame(make_frame(), []); r.flush()
            r.on_frame(make_frame(), []); r.flush()
            steps = list(iter_trajectory(Path(tmp) / "test"))
            self.assertEqual([s["step"] for s in steps], [0, 1])

    def test_close_flushes_remainder(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp)
            r.on_frame(make_frame(), [])
            r.close()                                  # no explicit flush() first
            self.assertEqual(len(load_trajectory(Path(tmp) / "test")["steps"]), 1)


class _FakeBridge:
    """Minimal stand-in: the recorder only reads bridge.tracks (id -> TrackState)."""
    def __init__(self, tracks):
        self.tracks = tracks


class TestPerTrackCapture(unittest.TestCase):
    """A1: raw per-track detail is recorded alongside the role aggregates."""

    def test_tracks_recorded_when_bridge_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            tracks = {"1": ts(1, "Drums", "group"), "2": ts(2, "Bass", "group")}
            r = TrajectoryRecorder(session_id="test", override={"trajectory_dir": str(tmp)},
                                   bridge=_FakeBridge(tracks))
            r.on_frame(pf.build_frame(tracks, TRANSPORT), [])
            r.flush(); r.close()
            step = load_trajectory(Path(tmp) / "test")["steps"][0]
            self.assertIn("tracks", step)
            self.assertEqual(set(step["tracks"]), {"1", "2"})
            t = step["tracks"]["1"]
            self.assertEqual(t["name"], "Drums")
            for k in ("bands", "rms_l", "rms_r", "peak_l", "peak_r",
                      "mid_energy", "side_energy", "correlation", "kind", "group_id"):
                self.assertIn(k, t)

    def test_no_tracks_key_without_bridge(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp)                                  # no bridge
            r.on_frame(make_frame(), []); r.flush(); r.close()
            self.assertNotIn("tracks", load_trajectory(Path(tmp) / "test")["steps"][0])

    def test_role_state_carries_peak_and_correlation(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp)
            r.on_frame(make_frame(), []); r.flush(); r.close()
            rs = load_trajectory(Path(tmp) / "test")["steps"][0]["frame"]["role_state"]
            for sub in rs.values():
                self.assertIn("peak_db", sub)
                self.assertIn("correlation", sub)

    def test_manifest_is_v2_data_dictionary(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp)
            r.on_frame(make_frame(), []); r.flush(); r.close()
            man = load_trajectory(Path(tmp) / "test")["manifest"]
            self.assertEqual(man["schema_version"], "sim.frame-trajectory.v2")
            for key in ("bands", "vector_layout", "fields", "masking_semantics",
                        "role_taxonomy", "event_schema", "focus_enums", "provenance"):
                self.assertIn(key, man)


class TestFilteringAndAlignment(unittest.TestCase):
    def test_only_when_playing_skips_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp, trajectory_only_when_playing=True)
            r.on_frame(make_frame(playing=True), [])
            r.on_frame(make_frame(playing=False), [])   # silent, no event -> skipped
            r.on_frame(make_frame(playing=True), [])
            r.flush()
            r.close()
            self.assertEqual(len(load_trajectory(Path(tmp) / "test")["steps"]), 2)

    def test_silent_frame_with_event_is_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp, trajectory_only_when_playing=True)
            ev = Event(t_wall=1.0, bar=4, beat=1.0, type="clip", a="drums", value=-0.1)
            r.on_frame(make_frame(playing=False), [ev])
            r.flush()
            r.close()
            steps = load_trajectory(Path(tmp) / "test")["steps"]
            self.assertEqual(len(steps), 1)
            self.assertEqual(steps[0]["events"][0]["type"], "clip")

    def test_stride_decimates(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _rec(tmp, trajectory_stride=2, trajectory_only_when_playing=False)
            for i in range(6):
                r.on_frame(make_frame(bar=i), [])
            r.flush()
            r.close()
            steps = load_trajectory(Path(tmp) / "test")["steps"]
            self.assertEqual([s["bar"] for s in steps], [0, 2, 4])   # every 2nd frame


if __name__ == "__main__":
    unittest.main()
