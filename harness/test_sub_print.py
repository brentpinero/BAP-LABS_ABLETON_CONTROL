"""
Tests for the Sub Print device patch (build_sub_print_device). Pure Python, no Max/Ableton.
Run: python -m unittest test_sub_print
"""

import json
import unittest

import build_sub_print_device as bsp
import sub_follower_core as sf


class TestSubPrintPatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bsp.main()
        cls.patcher = json.loads(bsp.OUT.read_text())["patcher"]
        cls.boxes = {b["box"]["id"]: b["box"] for b in cls.patcher["boxes"]}
        cls.texts = [b.get("text", "") for b in cls.boxes.values()]

    def _params(self):
        return {b["saved_attribute_attributes"]["valueof"]["parameter_longname"]: b
                for b in self.boxes.values() if b.get("parameter_enable")}

    def test_the_subs_own_midi_passes_straight_through(self):
        ids = {ln["patchline"]["source"][0]: ln["patchline"]["destination"][0]
               for ln in self.patcher["lines"]}
        self.assertEqual(ids["obj-midiin"], "obj-midiout")

    def test_print_is_a_mappable_visible_button(self):
        v = self._params()["Print"]["saved_attribute_attributes"]["valueof"]
        self.assertNotIn("parameter_invisible", v)
        self.assertEqual(self.boxes["obj-print"]["maxclass"], "live.text")
        self.assertEqual(self.boxes["obj-print"]["mode"], 0)

    def test_fold_is_on_by_default_and_floor_covers_candidates(self):
        p = self._params()
        self.assertEqual(p["Mono + fold"]["saved_attribute_attributes"]["valueof"]["parameter_initial"], [1])
        v = p["Floor"]["saved_attribute_attributes"]["valueof"]
        self.assertEqual(v["parameter_initial"], [sf.BAND_LO])
        self.assertLessEqual(v["parameter_mmin"], sf.FLOOR_MIN)

    def test_script_reads_bass_group_and_rewrites_only_its_own_clips(self):
        code = next(b["code"] for b in self.boxes.values() if b["maxclass"] == "v8.codebox")
        for needle in ("get_all_notes_extended", "create_midi_clip", "add_new_notes", "delete_clip",
                       'CLIP_NAME = "%s"' % bsp.CLIP_NAME, "/bass/i", "function print()"):
            self.assertIn(needle, code)
        self.assertNotIn("%(", code)
        # only clips named CLIP_NAME are deleted
        self.assertIn('String(cl.get("name")) === CLIP_NAME) old.push(cl.id)', code)

    def test_script_only_drives_the_status_line(self):
        for ln in self.patcher["lines"]:
            if ln["patchline"]["source"][0] == "obj-js":
                self.assertEqual(ln["patchline"]["destination"][0], "obj-setstat")

    def test_patchlines_reference_existing_boxes(self):
        for ln in self.patcher["lines"]:
            self.assertIn(ln["patchline"]["source"][0], self.boxes)
            self.assertIn(ln["patchline"]["destination"][0], self.boxes)


if __name__ == "__main__":
    unittest.main()
