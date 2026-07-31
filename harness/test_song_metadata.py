"""
Tests for song_metadata — the static per-track/plugin dump. Pure, fake client.
Run: python -m unittest test_song_metadata
"""

import unittest

import song_metadata as sm


class FakeClient:
    """Returns a canned get_all_device_parameters(full) payload with a rack."""
    def send(self, cmd, params=None):
        if cmd == "get_session_info":
            return {"tempo": 126.0}
        if cmd == "get_all_device_parameters":
            return {"mode": "full", "track_count": 3, "tracks": [
                {"track_index": 0, "track_name": "Lead", "kind": "regular",
                 "is_audio_track": False, "is_midi_track": True, "devices": [
                    {"path": "0", "name": "Instrument Rack", "class_name": "InstrumentGroupDevice",
                     "params": [{"index": 0, "name": "Device On", "value": 1.0, "min": 0, "max": 1,
                                 "automation_state": 0}]},
                    {"path": "0/0/0", "name": "Serum 2", "class_name": "PluginDevice",
                     "params": [{"index": 0, "name": "Device On", "value": 1.0, "min": 0, "max": 1,
                                 "automation_state": 0},
                                {"index": 1, "name": "LFO 1 Rate", "value": 0.3, "min": 0, "max": 1,
                                 "automation_state": 1}]},
                    {"path": "1", "name": "EQ Eight", "class_name": "Eq8",
                     "params": [{"index": 0, "name": "Device On", "value": 0.0, "min": 0, "max": 1,
                                 "automation_state": 0},
                                {"index": 1, "name": "1 Frequency A", "value": 0.5, "min": 0, "max": 1,
                                 "automation_state": 2}]}]},
                {"track_index": "return:0", "track_name": "A-Reverb", "kind": "return",
                 "is_audio_track": False, "is_midi_track": False, "devices": [
                    {"path": "0", "name": "Reverb", "class_name": "Reverb",
                     "params": [{"index": 0, "name": "Device On", "value": 1.0, "min": 0, "max": 1,
                                 "automation_state": 0}]}]},
                {"track_index": -1, "track_name": "Main", "kind": "master",
                 "is_audio_track": False, "is_midi_track": False, "devices": [
                    {"path": "0", "name": "Rift", "class_name": "PluginDevice",
                     "params": [{"index": 0, "name": "Device On", "value": 1.0, "min": 0, "max": 1,
                                 "automation_state": 0}]}]}]}
        return {}


class TestSongMetadata(unittest.TestCase):
    def setUp(self):
        self.meta = sm.build_song_metadata(FakeClient(), project_file=None)

    def test_rack_recursion_nested_path(self):
        lead = self.meta["tracks"][0]
        self.assertEqual([d["path"] for d in lead["devices"]], ["0", "0/0/0", "1"])  # Serum nested

    def test_track_type_midi_return_master(self):
        types = {t["name"]: t["track_type"] for t in self.meta["tracks"]}
        self.assertEqual(types["Lead"], "midi")
        self.assertEqual(types["A-Reverb"], "return")
        self.assertEqual(types["Main"], "master")

    def test_vst_and_classification(self):
        serum = self.meta["tracks"][0]["devices"][1]
        self.assertEqual(serum["classification"], "instrument")      # from causal_dataset
        self.assertTrue(serum["is_vst"] and serum["vst_partial"])
        self.assertEqual(serum["automated_params"], ["LFO 1 Rate"])   # automation_state=1
        rift = self.meta["tracks"][2]["devices"][0]
        self.assertEqual(rift["classification"], "saturation_distortion")
        self.assertTrue(rift["vst_partial"])

    def test_enabled_from_device_on_and_family_hint(self):
        eq = self.meta["tracks"][0]["devices"][2]
        self.assertFalse(eq["enabled"])                              # Device On == 0.0
        self.assertEqual(eq["classification"], "eq_filter")
        self.assertIn("1 Frequency A", eq["family_relevant_params"])

    def test_summary_counts(self):
        s = sm._summary(self.meta)
        self.assertIn("2 VST", s)                                    # Serum + Rift
        self.assertIn("2 automated params", s)                      # LFO Rate + EQ Freq

    def test_signal_order_and_chain_position(self):
        devs = self.meta["tracks"][0]["devices"]                     # Rack, Serum(0/0/0), EQ(1)
        self.assertEqual([d["signal_order"] for d in devs], [0, 1, 2])
        serum = devs[1]
        self.assertEqual(serum["depth"], 1)                          # one rack level deep
        self.assertEqual(serum["chain_position"], 0)                 # first device in the chain
        self.assertEqual(serum["parent_path"], "0/0")
        self.assertEqual(devs[2]["depth"], 0)                        # EQ is top-level
        self.assertEqual(devs[0]["depth"], 0)


class TestClassification(unittest.TestCase):
    def test_multi_family_and_new_families(self):
        import causal_dataset as cd
        self.assertEqual(cd.classify_families("N-POWER", "AudioEffectGroupDevice"),
                         ["saturation_distortion", "stereo_modulation"])   # combo device
        self.assertEqual(cd.classify_families("The God Particle", "PluginDevice"), ["mix_glue"])
        self.assertEqual(cd.classify_families("Easy Wash Out", "AudioEffectGroupDevice"),
                         ["filter_wash"])
        self.assertEqual(cd.classify_families("Rectifier SEND", "AudioEffectGroupDevice"),
                         ["saturation_distortion"])
        self.assertEqual(cd.classify_families("SPAN", "AuPluginDevice"), ["meter"])
        self.assertEqual(cd.classify_families("Microtuner", "MxDeviceMidiEffect"), ["midi_effect"])
        # class-name fallback when the display name says nothing
        self.assertEqual(cd.classify_families("", "AudioEffectGroupDevice"), ["rack"])
        # backward-compatible single-label wrapper
        self.assertEqual(cd.classify_device("N-POWER"), "saturation_distortion")

    def test_changes_audio_flag_excludes_meters(self):
        # a meter device should be flagged as not changing audio (ablation skips it)
        dev = sm.annotate_device({"path": "0", "name": "SPAN", "class_name": "AuPluginDevice",
                                  "params": []}, 0)
        self.assertFalse(dev["changes_audio"])
        self.assertIn("meter", dev["families"])


if __name__ == "__main__":
    unittest.main()
