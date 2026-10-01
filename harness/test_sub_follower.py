"""
Tests for the Sub Follower: the pure core (fold math, lowest-note mono line,
auto-octave scoring, tap planning) and the two generated device patches.
Pure Python, no Max/Ableton. Run: python -m unittest test_sub_follower
"""

import json
import unittest

import build_sub_follower_device as bsf
import sub_follower_core as sf


def _n(pitch, start, duration):
    return {"pitch": pitch, "start": start, "duration": duration}


class TestFold(unittest.TestCase):
    def test_wraps_any_octave_into_the_window(self):
        self.assertEqual(sf.fold(28, 28), 28)
        self.assertEqual(sf.fold(40, 28), 28)       # E an octave up
        self.assertEqual(sf.fold(16, 28), 28)       # E an octave down
        self.assertEqual(sf.fold(48, 28), 36)
        self.assertEqual(sf.fold(27, 28), 39)       # just under the floor wraps to the top
        for p in range(128):
            f = sf.fold(p, 29)
            self.assertTrue(29 <= f <= 40)
            self.assertEqual((f - p) % 12, 0)       # pitch class is preserved

    def test_names_and_hz_follow_ableton_c3_is_60(self):
        self.assertEqual(sf.note_name(60), "C3")
        self.assertEqual(sf.note_name(28), "E0")
        self.assertEqual(sf.note_name(21), "A-1")
        self.assertAlmostEqual(sf.note_hz(28), 41.2, places=1)
        self.assertAlmostEqual(sf.note_hz(69), 440.0)


class TestMonoLine(unittest.TestCase):
    def test_lowest_sounding_note_wins(self):
        line = sf.mono_line([_n(40, 0, 4), _n(36, 1, 1)])
        self.assertEqual(line, [_n(40, 0, 1), _n(36, 1, 1), _n(40, 2, 2)])

    def test_layered_sources_on_one_pitch_become_one_note(self):
        self.assertEqual(sf.mono_line([_n(36, 0, 2), _n(36, 1, 2)]), [_n(36, 0, 3)])

    def test_gap_splits_and_empty_is_empty(self):
        self.assertEqual(len(sf.mono_line([_n(36, 0, 1), _n(36, 2, 1)])), 2)
        self.assertEqual(sf.mono_line([]), [])


class TestFloorScoring(unittest.TestCase):
    def test_time_outside_the_sweet_spot_costs_by_distance(self):
        line = [_n(40, 0, 4)]                                   # an E
        self.assertEqual(sf.score_floor(line, 28)["cost"], 0)   # folds to E0, in band
        self.assertEqual(sf.score_floor(line, 29)["range_cost"], 2)   # E1, 2 above

    def test_step_turned_into_a_leap_is_penalised(self):
        line = [_n(36, 0, 1), _n(35, 1, 1)]                     # C then B, a semitone down
        self.assertEqual(sf.score_floor(line, 24)["jump_cost"], 1)    # C0 -> B0: leap of 11
        self.assertEqual(sf.score_floor(line, 28)["jump_cost"], 0)    # B0 -> C1: a step

    def test_choose_floor_is_cheapest_and_ties_toward_sweet_spot_floor(self):
        floor, scores = sf.choose_floor([_n(36, 0, 1), _n(35, 1, 1)])
        self.assertEqual(len(scores), sf.FLOOR_MAX - sf.FLOOR_MIN + 1)
        self.assertEqual(min(s["cost"] for s in scores),
                         next(s["cost"] for s in scores if s["floor"] == floor))
        self.assertEqual(floor, 28)
        # E and G in any octave: every floor up to E0 is free, so E0 wins the tie
        self.assertEqual(sf.choose_floor([_n(52, 0, 2), _n(55, 2, 2)])[0], 28)

    def test_choose_floor_moves_the_seam_off_a_riff_that_crosses_it(self):
        # F -> D# -> F: floor F0 would leap a seventh on every move
        floor, scores = sf.choose_floor([_n(41, 0, 1), _n(39, 1, 1), _n(41, 2, 1)])
        self.assertEqual(next(s for s in scores if s["floor"] == 29)["jump_cost"], 1)
        self.assertEqual(next(s for s in scores if s["floor"] == floor)["jump_cost"], 0)

    def test_no_notes_still_returns_a_floor(self):
        self.assertEqual(sf.choose_floor([])[0], sf.BAND_LO)


def _t(index, name, kind="regular", group_id=-1, midi=True):
    return {"index": index, "name": name, "kind": kind, "group_id": group_id,
            "is_midi_track": midi}


class TestFindSources(unittest.TestCase):
    def setUp(self):
        self.tracks = [
            _t(0, "Kick"),
            _t(1, "Sub", "group", midi=False), _t(2, "Sub Serum", group_id=1),
            _t(3, "Bass", "group", midi=False),
            _t(4, "Serum 2", group_id=3), _t(5, "Bass Resample", group_id=3, midi=False),
            _t(6, "Growls", "group", group_id=3, midi=False), _t(7, "Serum 2", group_id=6),
            _t(8, "Lead"),
        ]

    def test_midi_tracks_in_the_group_at_any_depth(self):
        group, sources = sf.find_sources(self.tracks, "bass")
        self.assertEqual(group, 3)
        self.assertEqual(sources, [(4, "Serum 2"), (7, "Serum 2")])   # audio + groups skipped

    def test_excluded_tracks_are_left_out(self):
        self.assertEqual(sf.find_sources(self.tracks, "bass", exclude=(7, None))[1],
                         [(4, "Serum 2")])

    def test_ancestors_innermost_first(self):
        self.assertEqual(sf.ancestors(self.tracks, 7), [6, 3])
        self.assertEqual(sf.ancestors(self.tracks, 0), [])

    def test_missing_group_raises(self):
        with self.assertRaises(ValueError):
            sf.find_sources(self.tracks, "drums")

    def test_find_track_by_index_exact_then_substring(self):
        self.assertEqual(sf.find_track(self.tracks, 2), 2)
        self.assertEqual(sf.find_track(self.tracks, "5"), 5)
        self.assertEqual(sf.find_track(self.tracks, "Sub"), 1)          # exact beats substring
        self.assertEqual(sf.find_track(self.tracks, "sub serum"), 2)
        with self.assertRaises(ValueError):
            sf.find_track(self.tracks, "Pad")


class TestPlanTaps(unittest.TestCase):
    def test_first_run_adds_every_source(self):
        self.assertEqual(sf.plan_taps([], [(3, "Reese"), (4, "Growl")]),
                         ([], [(3, "Reese"), (4, "Growl")], []))

    def test_existing_taps_keep_their_source_and_new_ones_are_added(self):
        keep, add, stale = sf.plan_taps(["Reese", "Growl"],
                                        [(5, "Growl"), (3, "Reese"), (6, "Wub")])
        self.assertEqual(keep, [(1, 5, "Growl"), (0, 3, "Reese")])
        self.assertEqual(add, [(6, "Wub")])
        self.assertEqual(stale, [])

    def test_duplicate_names_match_by_occurrence(self):
        keep, add, stale = sf.plan_taps(["Serum 2", "Serum 2"],
                                        [(7, "Serum 2"), (9, "Serum 2"), (11, "Serum 2")])
        self.assertEqual(keep, [(0, 7, "Serum 2"), (1, 9, "Serum 2")])
        self.assertEqual(add, [(11, "Serum 2")])

    def test_vanished_source_leaves_a_stale_tap(self):
        self.assertEqual(sf.plan_taps(["Reese", "Old"], [(3, "Reese")]),
                         ([(0, 3, "Reese")], [], [1]))


def _boxes(path):
    return json.loads(path.read_text())["patcher"]["boxes"]


def _params(boxes):
    return {b["box"]["saved_attribute_attributes"]["valueof"]["parameter_longname"]: b["box"]
            for b in boxes if b["box"].get("parameter_enable")}


class TestDevicePatches(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bsf.main()
        cls.tap = _boxes(bsf.TAP_OUT)
        cls.fol = _boxes(bsf.FOLLOWER_OUT)

    def _texts(self, boxes):
        return [b["box"].get("text", "") for b in boxes]

    def test_no_script_objects_in_either_note_path(self):
        for boxes in (self.tap, self.fol):
            self.assertFalse(any(t.split(" ")[0] in ("js", "v8", "node.script", "jsui")
                                 for t in self._texts(boxes)))

    def test_tap_is_a_gated_audio_effect_with_its_own_held_table(self):
        texts = self._texts(self.tap)
        for obj in ("midiin", "gate 1 1", "midiformat", "midiout", "plugin~", "plugout~"):
            self.assertIn(obj, texts)
        self.assertEqual(texts.count("table ---tapheld"), 2)     # writer + scan reader
        self.assertNotIn("table ---sfheld", texts)               # never shares the sub's

    def test_tap_slot_parameter_spans_every_midi_note(self):
        v = _params(self.tap)["Slot"]["saved_attribute_attributes"]["valueof"]
        self.assertEqual((v["parameter_mmin"], v["parameter_mmax"]), (0.0, 127.0))

    def test_tap_follow_switch_is_automatable_and_on_by_default(self):
        v = _params(self.tap)["Follow"]["saved_attribute_attributes"]["valueof"]
        self.assertEqual(v["parameter_initial"], [1])
        self.assertEqual(v["parameter_initial_enable"], 1)
        self.assertNotIn("parameter_invisible", v)       # visible = automatable

    def test_follower_floor_parameter_covers_the_candidate_floors(self):
        v = _params(self.fol)["Floor"]["saved_attribute_attributes"]["valueof"]
        self.assertLessEqual(v["parameter_mmin"], sf.FLOOR_MIN)
        self.assertGreaterEqual(v["parameter_mmax"], sf.FLOOR_MAX)
        self.assertEqual(v["parameter_initial"], [sf.BAND_LO])

    def test_neither_device_passes_midi_straight_through(self):
        # slot notes must never reach the synth; real notes must never skip the gate
        for path in (bsf.TAP_OUT, bsf.FOLLOWER_OUT):
            patcher = json.loads(path.read_text())["patcher"]
            ids = {b["box"]["id"]: b["box"].get("text", "") for b in patcher["boxes"]}
            feeds_out = {ids[ln["patchline"]["source"][0]] for ln in patcher["lines"]
                         if ids[ln["patchline"]["destination"][0]] == "midiout"}
            self.assertEqual(feeds_out, {"midiformat"})

    def test_patchlines_reference_existing_boxes(self):
        for path in (bsf.TAP_OUT, bsf.FOLLOWER_OUT):
            patcher = json.loads(path.read_text())["patcher"]
            ids = {b["box"]["id"] for b in patcher["boxes"]}
            for ln in patcher["lines"]:
                self.assertIn(ln["patchline"]["source"][0], ids)
                self.assertIn(ln["patchline"]["destination"][0], ids)


if __name__ == "__main__":
    unittest.main()
