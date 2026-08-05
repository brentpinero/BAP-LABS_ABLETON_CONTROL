"""
Tests for device_io_routing — the canonical DeviceIO source-resolution logic
mirrored inline by the Remote Script's _set_device_audio_input. Pure Python,
mock options/tracks, no Ableton. Run: python -m unittest test_device_io_routing

Covers the case this substrate exists for: 70+ track bass-music projects with
MANY duplicate track names (e.g. 26x 'Serum 2'), where a bare name match would
pull the WRONG track's audio into an analysis pair.
"""

import unittest

from device_io_routing import pick_option, resolve_source


class _Opt:
    def __init__(self, display_name):
        self.display_name = display_name


class _Track:
    def __init__(self, name):
        self.name = name


class TestPickOption(unittest.TestCase):
    def setUp(self):
        self.opts = [_Opt("Kick"), _Opt("Kick Layer"), _Opt("A-Reverb")]

    def test_exact_beats_substring(self):
        self.assertIs(pick_option(self.opts, "Kick"), self.opts[0])

    def test_substring_fallback_case_insensitive(self):
        self.assertIs(pick_option(self.opts, "reverb"), self.opts[2])

    def test_no_match(self):
        self.assertIsNone(pick_option(self.opts, "Snare"))


class TestResolveSource(unittest.TestCase):
    def setUp(self):
        # session order: Serum 2, Kick, Serum 2, Serum 2 — the duplicate-name trap
        self.tracks = [_Track("Serum 2"), _Track("Kick"),
                       _Track("Serum 2"), _Track("Serum 2")]
        self.opts = [_Opt("Serum 2"), _Opt("Kick"), _Opt("Serum 2"), _Opt("Serum 2")]

    def test_duplicates_resolved_by_occurrence(self):
        # track index 2 is the SECOND 'Serum 2' -> second 'Serum 2' option
        opt, amb = resolve_source(self.opts, self.tracks, source_index=2)
        self.assertIs(opt, self.opts[2])
        self.assertFalse(amb)
        # and index 3 is the third
        opt, _ = resolve_source(self.opts, self.tracks, source_index=3)
        self.assertIs(opt, self.opts[3])

    def test_fewer_options_than_tracks_is_ambiguous_best_effort(self):
        opts = [_Opt("Serum 2"), _Opt("Kick")]      # only one 'Serum 2' routable
        opt, amb = resolve_source(opts, self.tracks, source_index=3)
        self.assertIs(opt, opts[0])
        self.assertTrue(amb)

    def test_by_name_for_returns(self):
        opts = self.opts + [_Opt("A-Reverb")]
        opt, amb = resolve_source(opts, self.tracks, source_name="A-Reverb")
        self.assertIs(opt, opts[-1])
        self.assertFalse(amb)

    def test_bad_index_raises(self):
        with self.assertRaises(IndexError):
            resolve_source(self.opts, self.tracks, source_index=99)

    def test_no_match_raises_with_available(self):
        with self.assertRaises(ValueError) as cm:
            resolve_source(self.opts, self.tracks, source_name="Nonexistent")
        self.assertIn("available", str(cm.exception))


class TestMirrorsRemoteScript(unittest.TestCase):
    """The Remote Script mirrors this logic inline (it can't import repo modules).
    Guard the mirror: the inline implementation must contain the same load-bearing
    steps — occurrence counting and exact-list indexing."""

    def test_remote_script_contains_mirrored_logic(self):
        import io as _io
        from pathlib import Path
        src = (Path(__file__).parent / "AbletonMCP_Extended" / "__init__.py").read_text()
        self.assertIn("_set_device_audio_input", src)
        # the occurrence-resolution idiom, verbatim in both implementations
        self.assertIn("occ = sum(1 for t in self._song.tracks[:si + 1]", src)
        self.assertIn("chosen = exact[occ - 1]", src)
        self.assertIn("_get_device_audio_inputs", src)
        self.assertIn("available_routing_types", src)


if __name__ == "__main__":
    unittest.main()
