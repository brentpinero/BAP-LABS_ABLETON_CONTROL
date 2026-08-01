"""Tests for enrich_sidecars — merging Remote Script device detail into stem sidecars.
Run: python -m unittest test_enrich_sidecars"""

import json
import tempfile
import unittest
from pathlib import Path

import enrich_sidecars as es


SONG_META = {"tracks": [{
    "name": "26-Serum 2", "kind": "regular", "track_type": "midi", "group_id": 22,
    "devices": [
        {"path": "0", "name": "Serum 2", "class_name": "PluginDevice", "classification": "instrument",
         "families": ["instrument"], "is_vst": True, "vst_partial": True, "enabled": True,
         "automated_params": [], "params": [{"name": "LFO 1 Rate", "value": 0.3, "min": 0, "max": 1,
                                             "automation_state": 0}]},
        {"path": "1", "name": "EQ Eight", "class_name": "Eq8", "classification": "eq_filter",
         "families": ["eq_filter"], "is_vst": False, "vst_partial": False, "enabled": True,
         "automated_params": ["1 Frequency A"], "params": [{"name": "1 Frequency A", "value": 0.5}],
         "family_relevant_params": ["1 Frequency A"]},
        {"path": "5", "name": "SideChain_Rack_Ducker", "class_name": "AudioEffectGroupDevice",
         "classification": "rack", "families": ["dynamics"], "is_vst": False, "vst_partial": False,
         "enabled": True, "params": []},
        {"path": "5/0/0", "name": "GMaudio Ducker 1.5", "class_name": "MxDeviceAudioEffect",
         "classification": "dynamics", "enabled": True, "params": [{"name": "Amount", "value": 0.8}]},
    ]}]}

SIDECAR = {
    "schema_version": "sim.causal-plugin.v1",
    "node": {"ref": 25, "name": "26-Serum 2", "kind": "regular"},
    "rung": {"index": 3, "label": "through_1_EQ-Eight"},
    "devices": [
        {"index": 0, "name": "Serum 2", "class_name": "PluginDevice", "enabled": True, "ablatable": False},
        {"index": 1, "name": "EQ Eight", "class_name": "Eq8", "enabled": True, "ablatable": True},
        {"index": 5, "name": "SideChain_Rack_Ducker", "class_name": "AudioEffectGroupDevice",
         "enabled": False, "ablatable": True},
    ],
    "render_mode": "resample", "wav": "x.wav", "rendered": True, "error": None,
}


class TestEnrichSidecar(unittest.TestCase):
    def setUp(self):
        self.tm = es.build_name_index(SONG_META)["26-Serum 2"]
        self.out = es.enrich_sidecar(SIDECAR, self.tm)

    def test_node_gets_type_and_group(self):
        self.assertEqual(self.out["node"]["track_type"], "midi")
        self.assertEqual(self.out["node"]["group_id"], 22)
        self.assertEqual(self.out["schema_version"], es.ENRICH_SCHEMA)

    def test_devices_get_params_and_classification(self):
        eq = self.out["devices"][1]
        self.assertEqual(eq["classification"], "eq_filter")
        self.assertEqual(eq["families"], ["eq_filter"])
        self.assertEqual(eq["params"], [{"name": "1 Frequency A", "value": 0.5}])
        self.assertEqual(eq["automated_params"], ["1 Frequency A"])

    def test_per_rung_flags_preserved(self):
        # the ablation state (enabled/ablatable) must NOT be overwritten by the metadata
        self.assertFalse(self.out["devices"][2]["enabled"])   # rack was OFF this rung
        self.assertTrue(self.out["devices"][2]["ablatable"])
        self.assertTrue(self.out["devices"][0]["enabled"])
        self.assertFalse(self.out["devices"][0]["ablatable"])

    def test_rack_children_attached(self):
        rack = self.out["devices"][2]
        self.assertIn("rack_devices", rack)
        self.assertEqual(rack["rack_devices"][0]["name"], "GMaudio Ducker 1.5")
        self.assertEqual(rack["rack_devices"][0]["params"], [{"name": "Amount", "value": 0.8}])

    def test_unmatched_track_is_noop_flagged(self):
        out = es.enrich_sidecar(SIDECAR, None)
        self.assertFalse(out["enrichment"]["matched"])
        self.assertEqual(out["devices"][1].get("params"), None)  # untouched


class TestEnrichSession(unittest.TestCase):
    def test_writes_back_and_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "s1.json").write_text(json.dumps(SIDECAR))
            miss = json.loads(json.dumps(SIDECAR)); miss["node"]["name"] = "Ghost Track"
            (Path(tmp) / "s2.json").write_text(json.dumps(miss))
            (Path(tmp) / "manifest.json").write_text(json.dumps({"x": 1}))   # must be skipped
            res = es.enrich_session(tmp, SONG_META)
            self.assertEqual(res["enriched"], 2)
            self.assertEqual(res["matched"], 1)
            self.assertEqual(res["unmatched"], ["Ghost Track"])
            got = json.loads((Path(tmp) / "s1.json").read_text())
            self.assertEqual(got["devices"][1]["classification"], "eq_filter")


if __name__ == "__main__":
    unittest.main()
