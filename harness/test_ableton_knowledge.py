"""
test_ableton_knowledge.py — unit tests for the producer brain.

Pure/offline: no Ableton, no socket. Runs standalone (`python harness/test_ableton_knowledge.py`)
or under pytest. Guards the genre intelligence + pattern generators that the workflow
tools depend on (correct instruments per genre, notes in range, timing within bars).
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
    # unknown falls back to boom_bap (never crashes)
    assert K.resolve_genre("polka-core-9000") == "boom_bap"
    assert K.resolve_genre("") == "boom_bap"


# --- instrument selection (the fix: genre-correct, not generic) ------------
def test_boom_bap_uses_rhodes_not_wavetable():
    assert K.instrument_for("keys", "boom bap") == "Electric"      # Rhodes, not Wavetable
    assert K.instrument_for("chords", "boom bap") == "Electric"
    assert K.instrument_for("melody", "boom bap") == "Electric"
    # drums resolve to a kit search, never a bare device
    hint = K.instrument_load_hint("drums", "boom bap")
    assert hint["kind"] == "kit"
    assert "808" in hint["avoid"] and "trap" in hint["avoid"]      # boom bap avoids 808
    assert any(w in hint["prefer"] for w in ("boom", "vinyl", "dusty", "jazz"))


def test_palette_varies_by_genre():
    # different genres must NOT all collapse to the same synth
    keys = {g: K.instrument_for("keys", g) for g in ("boom bap", "trap", "techno", "ambient")}
    assert len(set(keys.values())) >= 2, f"palette too uniform: {keys}"
    assert K.instrument_for("pad", "ambient") == "Meld"           # textural pad for ambient


def test_suggest_instruments_ranks_top_pick_first():
    recs = K.suggest_instruments("keys", "boom bap")
    assert recs and recs[0]["instrument"] == "Electric"
    assert all("instrument" in r and "why" in r for r in recs)


# --- music theory ----------------------------------------------------------
def test_key_parsing_and_chords():
    assert K.parse_key("A minor") == (9, "minor")
    assert K.parse_key("F# dorian") == (6, "dorian")
    assert K.parse_key("") == (9, "minor")                         # sensible default
    # A minor i chord (Am7) -> A C E G in some octave; pitch classes must match
    chord = K.degree_chord(9, "minor", 0, octave=2)
    pcs = sorted({p % 12 for p in chord})
    assert pcs == [0, 4, 7, 9], f"Am7 pitch classes wrong: {pcs}"  # A(9) C(0) E(4) G(7)


def test_scale_midi_in_range_and_scale():
    root, scale = 9, "minor_pentatonic"
    ps = K.scale_midi(root, scale, 60, 79)
    assert ps == sorted(ps) and all(60 <= p <= 79 for p in ps)
    assert all((p - root) % 12 in K.SCALES[scale] for p in ps)


# --- pattern generators ----------------------------------------------------
def test_generators_produce_notes_for_every_role():
    for role in ("drums", "bass", "chords", "melody", "pad"):
        notes = K.generate(role, "boom bap", "A minor", bars=8)
        assert notes, f"{role} produced no notes"
        for n in notes:
            assert set(("pitch", "start_time", "duration", "velocity")) <= set(n)
            assert 0 <= n["pitch"] <= 127
            assert 1 <= n["velocity"] <= 127
            assert n["duration"] > 0


def test_notes_stay_within_the_bar_count():
    bars = 8
    for role in ("drums", "bass", "chords", "melody", "pad"):
        notes = K.generate(role, "boom bap", "A minor", bars=bars)
        if not notes:
            continue
        assert max(n["start_time"] for n in notes) < bars * 4, f"{role} note starts past the section end"


def test_drum_feels_differ_by_genre():
    boom = len(K.drum_pattern("boom bap", 4))
    trap = len(K.drum_pattern("trap", 4))          # fast hats -> denser
    ambient = len(K.drum_pattern("ambient", 4))    # feel 'none' -> no drums
    assert ambient == 0
    assert trap > boom > 0


def test_chords_follow_key_scale():
    # C major chords should be diatonic to C major
    notes = K.chord_pattern("pop", key="C major", bars=4)
    assert notes
    cmaj = set(K.SCALES["major"])
    for n in notes:
        assert (n["pitch"] - 0) % 12 in cmaj or (n["pitch"]) % 12 in {(0 + i) % 12 for i in K.SCALES["major"]}


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        fn()
        print(f"  PASS  {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} tests passed.")


if __name__ == "__main__":
    _run_all()
