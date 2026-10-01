"""
Tests for the Sub Follower gate probe: the MIDI IO Probe patch (build_midi_probe_device)
and the pure verdict logic of probe_device_midi_io. Pure Python, no Max/Ableton.
Run: python -m unittest test_midi_probe
"""

import json
import struct
import unittest

import build_midi_probe_device as bmp
import probe_device_midi_io as probe


def _osc(addr, *ints):
    """Encode an OSC packet with int args, the way udpsend emits a note list."""
    def pad(b):
        return b + b"\x00" * (4 - len(b) % 4)
    return (pad(addr.encode()) + pad(("," + "i" * len(ints)).encode())
            + b"".join(struct.pack(">i", v) for v in ints))


class TestProbePatch(unittest.TestCase):
    def setUp(self):
        bmp.main()
        self.patcher = json.loads(bmp.OUT.read_text())["patcher"]
        self.texts = [b["box"].get("text", "") for b in self.patcher["boxes"]]

    def test_declares_n_midi_inputs_and_one_output(self):
        self.assertEqual(self.texts.count("midiin"), bmp.N_INPUTS)
        self.assertEqual(self.texts.count("midiout"), 1)

    def test_each_input_has_its_own_osc_address(self):
        for k in range(1, bmp.N_INPUTS + 1):
            self.assertIn("prepend /midiprobe/in/%d" % k, self.texts)
        self.assertIn("udpsend 127.0.0.1 %d" % probe.OSC_PORT, self.texts)

    def test_is_a_valid_audio_effect_passthrough(self):
        self.assertIn("plugin~", self.texts)
        self.assertIn("plugout~", self.texts)

    def test_no_js_in_the_note_path(self):
        self.assertFalse(any(t.startswith(("js ", "v8 ")) for t in self.texts))

    def test_patchlines_reference_existing_boxes(self):
        ids = {b["box"]["id"] for b in self.patcher["boxes"]}
        for ln in self.patcher["lines"]:
            self.assertIn(ln["patchline"]["source"][0], ids)
            self.assertIn(ln["patchline"]["destination"][0], ids)


class TestProbeLogic(unittest.TestCase):
    def test_parse_osc_int_note_list(self):
        self.assertEqual(probe.parse_osc(_osc("/midiprobe/in/2", 36, 100)),
                         ("/midiprobe/in/2", [36, 100]))

    def test_summarize_ignores_note_offs_and_other_addresses(self):
        msgs = [("/midiprobe/in/1", [36, 100]), ("/midiprobe/in/1", [36, 0]),
                ("/midiprobe/in/2", [43, 90]), ("/agg/ch/1", [1, 1])]
        self.assertEqual(probe.summarize_hits(msgs), {1: {36}, 2: {43}})

    def test_independent_inputs_each_hear_only_their_source(self):
        routed = {1: {36, 38}, 2: {43}}
        self.assertEqual(probe.independent_inputs(routed, {1: {36}, 2: {43}}), 2)

    def test_shared_port_counts_as_one(self):
        # every [midiin] hears the same source: one port, not two
        routed = {1: {36, 43}, 2: {43}}
        self.assertEqual(probe.independent_inputs(routed, {1: {43}, 2: {43}}), 1)

    def test_foreign_notes_are_not_independent(self):
        self.assertEqual(probe.independent_inputs({1: {36}}, {1: {50}}), 0)

    def test_verdict_picks_device_shape(self):
        self.assertTrue(probe.verdict(4, 3).startswith("SINGLE HUB"))
        self.assertTrue(probe.verdict(1, 1).startswith("TAP STACK"))
        self.assertTrue(probe.verdict(4, 1).startswith("TAP STACK"))
        self.assertTrue(probe.verdict(0, 0).startswith("RELAY TRACKS"))
        self.assertTrue(probe.verdict(1, 0).startswith("RELAY TRACKS"))


if __name__ == "__main__":
    unittest.main()
