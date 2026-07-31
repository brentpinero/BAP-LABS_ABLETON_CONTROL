"""
Tests for perception_schema — the self-documenting manifest / data dictionary.
Guards that the dictionary stays in sync with the code it describes (no drift).
Run: python -m unittest test_perception_schema
"""

import inspect
import json
import unittest

import bands as _bands
import masking as _masking
import perception_frame as pf
import perception_schema as ps
from mix_analysis_bridge import TrackState
from perception_config import cfg


class TestVectorLayout(unittest.TestCase):
    def test_layout_total_matches_frame_geometry(self):
        roles, scheme = cfg("roles"), cfg("band_scheme")
        lay = ps.vector_layout(roles, scheme)
        self.assertEqual(lay["total"], pf.Frame.vector_len(roles, scheme))
        self.assertEqual(sum(s["length"] for s in lay["segments"]), lay["total"])

    def test_segments_are_contiguous(self):
        lay = ps.vector_layout()
        off = 0
        for s in lay["segments"]:
            self.assertEqual(s["offset"], off)          # no gaps/overlaps
            off += s["length"]
        self.assertEqual(off, lay["total"])


class TestBandTable(unittest.TestCase):
    def test_band_table_matches_bands_module(self):
        scheme = cfg("band_scheme")
        table = ps.band_table(scheme)
        self.assertEqual([b["name"] for b in table], _bands.band_names(scheme))
        for b, (lo, hi) in zip(table, _bands.band_edges(scheme)):
            self.assertEqual((b["lo_hz"], b["hi_hz"]), (lo, hi))


class TestDataDictionaryCoverage(unittest.TestCase):
    def test_every_track_dict_key_is_documented(self):
        actual = set(TrackState(track_id="1", bands=[0.0] * 7).to_dict())
        self.assertTrue(actual <= set(ps.field_dictionary()["track"]),
                        f"undocumented track keys: {actual - set(ps.field_dictionary()['track'])}")

    def test_every_role_state_key_is_documented(self):
        tracks = {"1": TrackState(track_id="1", name="Bass", kind="group",
                                  bands=[0.3, 0.25, 0.15, 0.1, 0.1, 0.05, 0.05],
                                  rms_l=-8.0, rms_r=-8.0)}
        rs = pf.build_frame(tracks, {"bpm": 120, "bar": 1, "beat": 0,
                                     "beats_per_bar": 4, "playing": True}).to_dict()["role_state"]
        documented = set(ps.field_dictionary()["role_state"])
        for sub in rs.values():
            self.assertTrue(set(sub) <= documented, f"undocumented: {set(sub) - documented}")

    def test_focus_enums_match_perception_frame(self):
        fe = ps.focus_enums()
        self.assertEqual(fe["device_classes"], list(pf.DEVICE_CLASSES))
        self.assertEqual(fe["actions"], list(pf.ACTIONS))

    def test_event_types_documented(self):
        self.assertEqual(set(ps.event_schema()["types"]),
                         {"mask_on", "mask_off", "clip", "level_jump"})


class TestMaskingSemantics(unittest.TestCase):
    def test_congestion_thresholds_track_the_code(self):
        params = inspect.signature(_masking.compute_masking).parameters
        cfrac = params["congestion_frac"].default
        note = ps.masking_semantics()["master_congestion"]
        self.assertIn(str(cfrac), note)                 # dictionary reflects the real default


class TestBuildManifest(unittest.TestCase):
    def test_manifest_shape_and_serializable(self):
        m = ps.build_manifest("sess_x", 123.0)
        self.assertEqual(m["schema_version"], "sim.frame-trajectory.v2")
        self.assertEqual(m["session_id"], "sess_x")
        self.assertEqual(m["vector_len"], pf.Frame.vector_len(m["roles"], m["band_scheme"]))
        self.assertEqual(m["role_taxonomy"]["roles"], list(cfg("roles")))
        json.dumps(m)                                    # must be JSON-serializable


if __name__ == "__main__":
    unittest.main()
