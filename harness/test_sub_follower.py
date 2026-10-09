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


class TestUnrollAndNormalize(unittest.TestCase):
    def _c(self, **kw):
        base = dict(start=8.0, end=16.0, start_marker=0.0, looping=False, loop_start=0.0,
                    loop_end=4.0, notes=[])
        base.update(kw)
        return sf.unroll_clip(**base)

    def test_plain_clip_offsets_notes_by_clip_start(self):
        out = self._c(notes=[{"pitch": 36, "start_time": 1.0, "duration": 0.5, "velocity": 90},
                             {"pitch": 40, "start_time": 9.0, "duration": 0.5, "velocity": 90}])
        self.assertEqual(out, [{"pitch": 36, "start": 9.0, "duration": 0.5, "velocity": 90}])

    def test_start_marker_shifts_and_muted_notes_are_skipped(self):
        out = self._c(start_marker=2.0,
                      notes=[{"pitch": 36, "start_time": 1.0, "duration": 1.0, "velocity": 90},
                             {"pitch": 38, "start_time": 3.0, "duration": 1.0, "velocity": 90},
                             {"pitch": 40, "start_time": 4.0, "duration": 1.0, "velocity": 90,
                              "mute": True}])
        self.assertEqual([(n["pitch"], n["start"]) for n in out], [(38, 9.0)])

    def test_looped_clip_repeats_until_the_clip_ends(self):
        out = self._c(looping=True, loop_start=0.0, loop_end=4.0,
                      notes=[{"pitch": 36, "start_time": 0.0, "duration": 1.0, "velocity": 90}])
        self.assertEqual([n["start"] for n in out], [8.0, 12.0])

    def test_note_crossing_the_loop_end_is_cut(self):
        out = self._c(looping=True, loop_start=0.0, loop_end=4.0,
                      notes=[{"pitch": 36, "start_time": 3.0, "duration": 3.0, "velocity": 90}])
        self.assertEqual([(n["start"], n["duration"]) for n in out], [(11.0, 1.0), (15.0, 1.0)])

    def test_merge_regions(self):
        self.assertEqual(sf.merge_regions([(4, 12), (0, 8), (20, 24)]), [(0, 12), (20, 24)])

    def test_normalize_is_mono_and_folded_with_auto_floor(self):
        line, floor = sf.normalize([_n(55, 0, 2) | {"velocity": 90}, _n(36, 1, 1) | {"velocity": 90}])
        self.assertEqual(floor, 28)
        self.assertEqual([(n["pitch"], n["start"], n["duration"]) for n in line],
                         [(31, 0, 1), (36, 1, 1)])
        self.assertTrue(all(n["velocity"] == 100 for n in line))


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


def _params(boxes):
    return {b["box"]["saved_attribute_attributes"]["valueof"]["parameter_longname"]: b["box"]
            for b in boxes if b["box"].get("parameter_enable")}


class TestDevicePatches(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bsf.main()
        cls.send = json.loads(bsf.SEND_OUT.read_text())["patcher"]
        cls.fol = json.loads(bsf.FOLLOWER_OUT.read_text())["patcher"]

    @staticmethod
    def _texts(patcher):
        return [b["box"].get("text", "") for b in patcher["boxes"]]

    @staticmethod
    def _feeds(patcher, dst_text):
        ids = {b["box"]["id"]: b["box"].get("text", "") for b in patcher["boxes"]}
        return {ids[ln["patchline"]["source"][0]] for ln in patcher["lines"]
                if ids[ln["patchline"]["destination"][0]] == dst_text}

    def test_no_script_object_in_either_note_path(self):
        for patcher in (self.send, self.fol):
            self.assertFalse(any(t.split(" ")[0] in ("js", "v8", "node.script")
                                 for t in self._texts(patcher)))
            # the embedded script only drives parameters and the status line
            ids = {b["box"]["id"]: b["box"] for b in patcher["boxes"]}
            for ln in patcher["lines"]:
                if ln["patchline"]["source"][0] == "obj-js":
                    dst = ids[ln["patchline"]["destination"][0]]
                    self.assertTrue(dst.get("parameter_enable") or dst["id"] == "obj-setstat")

    def test_send_sends_control_change_not_notes(self):
        texts = self._texts(self.send)
        for obj in ("midiin", "gate 1 1", "ctlout", "plugin~", "plugout~", "live.thisdevice"):
            self.assertIn(obj, texts)
        self.assertNotIn("midiout", texts)
        self.assertEqual(texts.count("table ---sendheld"), 2)       # writer + scan reader

    def test_send_creates_the_follow_track_only_on_first_setup(self):
        code = next(b["box"]["code"] for b in self.send["boxes"]
                    if b["box"]["maxclass"] == "v8.codebox")
        self.assertIn("if (!setupDone) { ensureFollowTrack(); outlet(2, 1); }", code)
        v = _params(self.send["boxes"])["Setup Done"]["saved_attribute_attributes"]["valueof"]
        self.assertEqual(v["parameter_initial"], [0])
        self.assertEqual(v["parameter_invisible"], 1)        # stored, not automatable

    def test_send_parameters(self):
        p = _params(self.send["boxes"])
        self.assertEqual(p["Follow"]["saved_attribute_attributes"]["valueof"]["parameter_initial"], [1])
        v = p["Slot"]["saved_attribute_attributes"]["valueof"]
        self.assertEqual((v["parameter_mmin"], v["parameter_mmax"]), (0.0, float(bsf.MAX_SLOT - 1)))

    def test_follower_turns_cc_into_notes_only(self):
        texts = self._texts(self.fol)
        for obj in ("ctlin", "midiformat", "midiout", "live.thisdevice"):
            self.assertIn(obj, texts)
        self.assertEqual(self._feeds(self.fol, "midiout"), {"midiformat"})
        self.assertEqual(self._feeds(self.fol, "midiparse"), set())    # own notes not forwarded
        v = _params(self.fol["boxes"])["Floor"]["saved_attribute_attributes"]["valueof"]
        self.assertLessEqual(v["parameter_mmin"], sf.FLOOR_MIN)
        self.assertGreaterEqual(v["parameter_mmax"], sf.FLOOR_MAX)
        self.assertEqual(v["parameter_initial"], [sf.BAND_LO])

    def test_embedded_scripts_carry_the_routing_logic(self):
        for patcher, needles in ((self.send, ("midi_inputs 0", "Pre FX", "midi_outputs 0")),
                                 (self.fol, ("current_monitoring_state", "output_routing_channel",
                                             "get_notes_extended", "chooseFloor"))):
            code = next(b["box"]["code"] for b in patcher["boxes"]
                        if b["box"]["maxclass"] == "v8.codebox")
            for needle in needles:
                self.assertIn(needle, code)
            self.assertNotIn("%(", code)                                 # formatting applied

    def test_patchlines_reference_existing_boxes(self):
        for patcher in (self.send, self.fol):
            ids = {b["box"]["id"] for b in patcher["boxes"]}
            for ln in patcher["lines"]:
                self.assertIn(ln["patchline"]["source"][0], ids)
                self.assertIn(ln["patchline"]["destination"][0], ids)


if __name__ == "__main__":
    unittest.main()
