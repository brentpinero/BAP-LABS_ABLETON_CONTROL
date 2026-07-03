"""
test_ableton_knowledge.py — unit tests for the producer brain.

Pure/offline: no Ableton, no socket. Runs standalone (`python harness/test_ableton_knowledge.py`)
or under pytest. This module is a STYLE REFERENCE + INSTRUMENT PICKER (it does NOT generate
MIDI — the model composes that), so these tests guard genre resolution, genre-appropriate
instrument selection, and the shape/quality of the style guidance the workflow tools return.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ableton_knowledge as K


# --- genre resolution ------------------------------------------------------
def test_genre_resolution_aliases():
    cases = {
        "boom bap": "boom_bap", "boombap": "boom_bap", "90s hip hop": "boom_bap",
        "lofi": "lofi", "lo-fi": "lofi", "chillhop": "lofi",
        "trap": "trap", "deep house": "house", "tech house": "house",
        "drum and bass": "dnb", "drum & bass": "dnb", "jungle": "dnb",
        "neo soul": "rnb", "r&b": "rnb", "ambient": "ambient", "pop": "pop",
    }
    for text, expected in cases.items():
        assert K.resolve_genre(text) == expected, f"{text!r} -> {K.resolve_genre(text)} != {expected}"
    assert K.resolve_genre("polka-core-9000") == "boom_bap"   # unknown falls back, never crashes
    assert K.resolve_genre("") == "boom_bap"


# --- instrument selection (the fix: genre-correct, not generic) ------------
def test_boom_bap_uses_rhodes_not_wavetable():
    assert K.instrument_for("keys", "boom bap") == "Electric"      # Rhodes, not Wavetable
    assert K.instrument_for("chords", "boom bap") == "Electric"
    assert K.instrument_for("melody", "boom bap") == "Electric"
    hint = K.instrument_load_hint("drums", "boom bap")            # drums => kit search, never bare device
    assert hint["kind"] == "kit"
    assert "808" in hint["avoid"] and "trap" in hint["avoid"]
    assert any(w in hint["prefer"] for w in ("boom", "vinyl", "dusty", "jazz"))


def test_palette_varies_by_genre():
    keys = {g: K.instrument_for("keys", g) for g in ("boom bap", "trap", "techno", "ambient")}
    assert len(set(keys.values())) >= 2, f"palette too uniform: {keys}"
    assert K.instrument_for("pad", "ambient") == "Meld"


def test_suggest_instruments_ranks_top_pick_first():
    recs = K.suggest_instruments("keys", "boom bap")
    assert recs and recs[0]["instrument"] == "Electric"
    assert all("instrument" in r and "why" in r for r in recs)


# --- music-theory reference ------------------------------------------------
def test_key_parsing():
    assert K.parse_key("A minor") == (9, "minor")
    assert K.parse_key("F# dorian") == (6, "dorian")
    assert K.parse_key("") == (9, "minor")


def test_scale_note_names_and_progression():
    assert K.scale_note_names(9, "minor_pentatonic") == ["A", "C", "D", "E", "G"]
    prog = K.progression_roman(K.genre_profile("boom bap"))
    assert "roman" in prog and "chord_roots" in prog
    assert prog["chord_roots"] and all(isinstance(x, str) for x in prog["chord_roots"])


def test_drum_map_reference():
    assert K.DRUM_MAP["kick"] == 36 and K.DRUM_MAP["snare"] == 38
    assert K.DRUM_MAP["closed_hat"] == 42 and K.DRUM_MAP["open_hat"] == 46


# --- style guide (what the model composes from) ----------------------------
def test_style_guide_shape_for_every_genre():
    required = {"genre", "bpm", "key", "feel", "drums", "harmony", "bass", "melody",
                "drum_map", "reference_artists", "avoid", "suggested_progression", "how_to_use"}
    for g in K.GENRES:
        sg = K.style_guide(g)
        missing = required - set(sg)
        assert not missing, f"{g} style guide missing {missing}"
        assert sg["reference_artists"], f"{g} has no reference artists"
        assert isinstance(sg["drum_map"], dict) and sg["drum_map"]["kick"] == 36


def test_style_guide_references_are_genre_specific():
    assert any("Premier" in r or "Dilla" in r for r in K.style_guide("boom bap")["reference_artists"])
    assert any("Metro" in r or "808" in r for r in K.style_guide("trap")["reference_artists"])
    assert any("Eno" in r or "Frahm" in r for r in K.style_guide("ambient")["reference_artists"])


def test_style_guide_role_focus():
    sg = K.style_guide("boom bap", role="bass")
    assert sg.get("focus_role") == "bass" and "focus" in sg
    assert sg["focus"] == sg["bass"]


def test_no_midi_generators_remain():
    # this module must NOT expose note generators anymore (the model composes MIDI)
    for gone in ("generate", "drum_pattern", "bass_pattern", "melody_pattern", "GENERATORS"):
        assert not hasattr(K, gone), f"{gone} should have been removed"


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  PASS  {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} tests passed.")


if __name__ == "__main__":
    _run_all()
