"""
Tests for track_resolver — the canonical resolution logic mirrored by the
AbletonMCP Remote Script's inline _resolve_track/_track_kind. Pure Python, mock
`song`, no Ableton. Run:  python -m unittest test_track_resolver -v

Covers the bug this fixes: group / return / master tracks were unreachable because
the old inline guard rejected any track_index < 0 and only indexed song.tracks.
"""

import unittest

from track_resolver import resolve_track, track_kind


class _Track:
    def __init__(self, name, is_foldable=False):
        self.name = name
        self.is_foldable = is_foldable


class _Song:
    """Mock Live song: regular + group tracks in .tracks, returns separate, one master."""
    def __init__(self):
        self.kick = _Track("Kick")
        self.drums_group = _Track("Drums", is_foldable=True)   # a group track
        self.bass = _Track("Bass")
        self.tracks = [self.kick, self.drums_group, self.bass]
        self.rev = _Track("A-Reverb")
        self.delay = _Track("B-Delay")
        self.return_tracks = [self.rev, self.delay]
        self.master_track = _Track("Master")


class TestResolveTrack(unittest.TestCase):
    def setUp(self):
        self.song = _Song()

    def test_int_index_regular_and_group(self):
        self.assertIs(resolve_track(self.song, 0), self.song.kick)
        self.assertIs(resolve_track(self.song, 1), self.song.drums_group)  # group via song.tracks

    def test_minus_one_is_master(self):
        self.assertIs(resolve_track(self.song, -1), self.song.master_track)

    def test_master_by_name(self):
        for ref in ("master", "Master", "main", "MAIN", "-1"):
            self.assertIs(resolve_track(self.song, ref), self.song.master_track, ref)

    def test_return_by_convention_and_name(self):
        self.assertIs(resolve_track(self.song, "return:0"), self.song.rev)
        self.assertIs(resolve_track(self.song, "r:1"), self.song.delay)
        self.assertIs(resolve_track(self.song, "A-Reverb"), self.song.rev)

    def test_name_match_regular_and_group(self):
        self.assertIs(resolve_track(self.song, "Kick"), self.song.kick)
        self.assertIs(resolve_track(self.song, "Drums"), self.song.drums_group)

    def test_numeric_string_passthrough(self):
        self.assertIs(resolve_track(self.song, "2"), self.song.bass)
        self.assertIs(resolve_track(self.song, "-1"), self.song.master_track)

    def test_out_of_range(self):
        with self.assertRaises(IndexError):
            resolve_track(self.song, 99)
        with self.assertRaises(IndexError):
            resolve_track(self.song, "return:9")

    def test_unknown_name(self):
        with self.assertRaises(KeyError):
            resolve_track(self.song, "Nonexistent Track")

    def test_bool_rejected(self):
        with self.assertRaises(TypeError):
            resolve_track(self.song, True)


class TestTrackKind(unittest.TestCase):
    def setUp(self):
        self.song = _Song()

    def test_kinds(self):
        self.assertEqual(track_kind(self.song, self.song.master_track), "master")
        self.assertEqual(track_kind(self.song, self.song.rev), "return")
        self.assertEqual(track_kind(self.song, self.song.drums_group), "group")
        self.assertEqual(track_kind(self.song, self.song.kick), "regular")

    def test_kind_of_resolved_refs(self):
        # end-to-end: resolve then classify, the pattern _get_track_info uses
        s = self.song
        self.assertEqual(track_kind(s, resolve_track(s, -1)), "master")
        self.assertEqual(track_kind(s, resolve_track(s, "return:0")), "return")
        self.assertEqual(track_kind(s, resolve_track(s, "Drums")), "group")
        self.assertEqual(track_kind(s, resolve_track(s, 0)), "regular")


if __name__ == "__main__":
    unittest.main()
