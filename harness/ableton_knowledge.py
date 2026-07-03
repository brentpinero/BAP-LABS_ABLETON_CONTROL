"""
ableton_knowledge.py — the "producer brain" for the Ableton MCP server.

Pure data + generators, NO MCP / socket dependencies (so it is unit-testable on
its own). The MCP server imports this to turn a genre + role into:
  - the RIGHT Ableton 12 instrument (boom bap keys => Electric/Rhodes, not Wavetable)
  - a genre-correct drum/bass/chord/melody/pad pattern in the right key & feel

Design goals:
  - Encode production quality as DATA so the model doesn't have to improvise it.
  - Be EXTENSIBLE: adding a genre = adding one GENRES entry; adding an instrument
    = one INSTRUMENTS entry. Generators read the genre profile, not hard-coded cases.

References: Ableton Live 12 instrument reference; genre BPM/feel conventions.
"""

from typing import Dict, List, Any, Tuple, Optional

# ---------------------------------------------------------------------------
# 1) ABLETON 12 INSTRUMENT CATALOG
#    role  = musical job it does well
#    load  = ordered browser targets to try. "Instruments/<Name>" loads a preset
#            from that device's folder (audible, in-character); a bare device name
#            is the fallback. Drum kits are resolved from the "Drums" folder.
# ---------------------------------------------------------------------------
INSTRUMENTS: Dict[str, Dict[str, Any]] = {
    "Electric":   {"desc": "Rhodes/Wurlitzer electric pianos — warm, vintage keys",
                   "roles": ["keys", "chords", "melody"],
                   "genres": ["boom_bap", "lofi", "rnb", "soul", "jazz", "pop"]},
    "Operator":   {"desc": "FM synth — bells, e-pianos, punchy bass, evolving tones",
                   "roles": ["bass", "lead", "keys", "pluck"],
                   "genres": ["trap", "house", "techno", "pop", "dnb", "boom_bap"]},
    "Analog":     {"desc": "Virtual analog — warm pads, fat leads, deep bass",
                   "roles": ["bass", "pad", "lead"],
                   "genres": ["house", "techno", "pop", "lofi"]},
    "Drift":      {"desc": "Warm analog synth — lush pads, punchy bass, easy to shape",
                   "roles": ["pad", "bass", "lead"],
                   "genres": ["ambient", "lofi", "house", "techno", "dnb"]},
    "Wavetable":  {"desc": "Morphing wavetable synth — modern, digital, wide palette",
                   "roles": ["lead", "pad", "bass", "pluck"],
                   "genres": ["edm", "pop", "trap", "dnb", "techno"]},
    "Collision":  {"desc": "Physical-modeled mallets/bells — marimba, vibes, kalimba",
                   "roles": ["melody", "pluck", "keys"],
                   "genres": ["lofi", "ambient", "pop"]},
    "Tension":    {"desc": "Physical-modeled strings — plucked/bowed",
                   "roles": ["melody", "pluck", "pad"],
                   "genres": ["ambient", "pop", "cinematic"]},
    "Meld":       {"desc": "Bi-timbral textural synth — evolving atmospheres, drones",
                   "roles": ["pad", "lead"],
                   "genres": ["ambient", "cinematic", "techno"]},
}

# Drum-kit search hints per genre (matched against the "Drums" browser folder).
# The bare empty "Drum Rack" is always skipped by the loader (it's silent).
KIT_HINTS: Dict[str, Dict[str, List[str]]] = {
    "boom_bap": {"prefer": ["hip hop", "boom", "vinyl", "dusty", "jazz", "funk", "soul", "kit-core", "acoustic"],
                 "avoid":  ["808", "trap", "edm"]},
    "lofi":     {"prefer": ["lo-fi", "lofi", "vinyl", "dusty", "hip hop", "jazz", "soft", "acoustic"],
                 "avoid":  ["808", "edm", "hard"]},
    "trap":     {"prefer": ["808", "trap", "hip hop", "modern"],
                 "avoid":  ["acoustic", "jazz"]},
    "house":    {"prefer": ["house", "909", "core", "dance", "four"],
                 "avoid":  ["acoustic"]},
    "techno":   {"prefer": ["techno", "909", "808", "core", "industrial", "dark"],
                 "avoid":  ["acoustic", "jazz"]},
    "dnb":      {"prefer": ["amen", "break", "dnb", "jungle", "drum", "hard"],
                 "avoid":  ["acoustic"]},
    "rnb":      {"prefer": ["r&b", "rnb", "soul", "hip hop", "smooth", "kit-core"],
                 "avoid":  ["edm", "hard"]},
    "ambient":  {"prefer": ["soft", "brush", "acoustic", "perc", "world"],
                 "avoid":  ["808", "hard", "edm"]},
    "pop":      {"prefer": ["pop", "acoustic", "kit-core", "modern", "clean"],
                 "avoid":  []},
}

# ---------------------------------------------------------------------------
# 2) MUSIC THEORY
# ---------------------------------------------------------------------------
_NOTE_PC = {"c": 0, "c#": 1, "db": 1, "d": 2, "d#": 3, "eb": 3, "e": 4, "fb": 4,
            "e#": 5, "f": 5, "f#": 6, "gb": 6, "g": 7, "g#": 8, "ab": 8,
            "a": 9, "a#": 10, "bb": 10, "b": 11, "cb": 11}

SCALES: Dict[str, List[int]] = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],            # natural minor
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "minor_pentatonic": [0, 3, 5, 7, 10],
    "major_pentatonic": [0, 2, 4, 7, 9],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
}

# diatonic 7th-chord qualities per scale degree (semitone stacks from the degree root)
_SEVENTH = {
    "minor":  [[0, 3, 7, 10], [0, 3, 6, 9], [0, 4, 7, 11], [0, 3, 7, 10],
               [0, 3, 7, 10], [0, 4, 7, 11], [0, 4, 8, 10]],
    "dorian": [[0, 3, 7, 10], [0, 3, 7, 10], [0, 4, 7, 10], [0, 4, 7, 10],
               [0, 3, 7, 10], [0, 3, 6, 9], [0, 4, 7, 11]],
    "major":  [[0, 4, 7, 11], [0, 3, 7, 10], [0, 3, 7, 10], [0, 4, 7, 11],
               [0, 4, 7, 10], [0, 3, 7, 10], [0, 3, 6, 9]],
}


def parse_key(key: str) -> Tuple[int, str]:
    """'A minor' -> (9, 'minor'); 'F# dorian' -> (6,'dorian'); default C minor."""
    if not key:
        return 9, "minor"  # A minor default — friendly for pentatonic melodies
    parts = str(key).strip().split()
    root = _NOTE_PC.get(parts[0].lower(), 0) if parts else 0
    scale = "minor"
    if len(parts) > 1:
        s = "_".join(parts[1:]).lower()
        s = {"min": "minor", "maj": "major", "pentatonic": "minor_pentatonic",
             "minor_pent": "minor_pentatonic"}.get(s, s)
        if s in SCALES:
            scale = s
    return root, scale


def note_name_to_midi(name: str) -> int:
    """'C1' -> 36 (Ableton convention: C3=60)."""
    name = name.strip()
    i = 1 if name[1:2] in ("#", "b") else 0
    pc = _NOTE_PC.get(name[: i + 1].lower(), 0)
    octave = int(name[i + 1:]) if name[i + 1:] else 3
    return pc + (octave + 2) * 12  # C3 = 60 => octave+2


def scale_midi(root_pc: int, scale: str, lo: int = 48, hi: int = 84) -> List[int]:
    """All midi pitches in [lo,hi] belonging to the scale."""
    ivals = SCALES.get(scale, SCALES["minor"])
    out = []
    for m in range(lo, hi + 1):
        if (m - root_pc) % 12 in ivals:
            out.append(m)
    return out


def degree_chord(root_pc: int, scale: str, degree: int, octave: int = 4) -> List[int]:
    """Diatonic 7th chord on a scale degree (0-indexed). Falls back to minor table."""
    ivals = SCALES.get(scale, SCALES["minor"])
    heptatonic = ivals if len(ivals) == 7 else SCALES["minor"]
    table = _SEVENTH.get(scale, _SEVENTH["minor"])
    d = degree % 7
    chord_root = root_pc + (octave + 2) * 12 + heptatonic[d]
    stack = table[d]
    return [chord_root + s for s in stack]


# ---------------------------------------------------------------------------
# 3) GENRE PROFILES  (extensible: add an entry to support a new genre)
#    feel drives the pattern generators; palette maps role -> instrument.
# ---------------------------------------------------------------------------
GENRES: Dict[str, Dict[str, Any]] = {
    "boom_bap": {
        "aka": ["boom bap", "boombap", "hip hop", "hiphop", "90s hip hop", "east coast"],
        "bpm": 88, "swing": 0.06, "key": "A minor", "scale": "minor_pentatonic",
        "chord_scale": "dorian", "feel": "boom_bap", "bass_feel": "root_hits",
        "progression": [0, 3, 4, 3],   # i - iv - v - iv (jazzy dorian)
        "palette": {"drums": "kit", "bass": "Operator", "keys": "Electric",
                    "chords": "Electric", "melody": "Electric", "pad": "Drift"},
        "structure": ["intro:4", "verse:16", "hook:8", "verse:16", "hook:8", "outro:4"],
        "tips": "Dusty swung drums, Rhodes keys, upright/electric bass on the kick, minor/dorian.",
    },
    "lofi": {
        "aka": ["lo-fi", "lo fi", "chillhop", "study beats"],
        "bpm": 80, "swing": 0.08, "key": "F major", "scale": "major_pentatonic",
        "chord_scale": "major", "feel": "boom_bap", "bass_feel": "root_hits",
        "progression": [1, 4, 0, 5],   # ii - V - I - vi-ish, jazzy/warm
        "palette": {"drums": "kit", "bass": "Operator", "keys": "Electric",
                    "chords": "Electric", "melody": "Collision", "pad": "Drift"},
        "structure": ["intro:4", "loop:16", "loop:16", "outro:4"],
        "tips": "Slow swung drums, warm Rhodes 7th chords, soft mallet melody, mellow.",
    },
    "trap": {
        "aka": ["trap beat", "drill"],
        "bpm": 140, "swing": 0.0, "key": "C minor", "scale": "minor",
        "chord_scale": "minor", "feel": "trap", "bass_feel": "eight_oh_eight",
        "progression": [0, 5, 3, 4],
        "palette": {"drums": "kit", "bass": "Operator", "keys": "Operator",
                    "chords": "Wavetable", "melody": "Wavetable", "pad": "Wavetable"},
        "structure": ["intro:4", "verse:16", "hook:8", "verse:16", "hook:8"],
        "tips": "Booming 808 glides, fast hat rolls, dark minor bells/plucks. Half-time feel.",
    },
    "house": {
        "aka": ["deep house", "tech house", "4x4"],
        "bpm": 124, "swing": 0.0, "key": "A minor", "scale": "minor",
        "chord_scale": "minor", "feel": "four_on_floor", "bass_feel": "offbeat",
        "progression": [0, 5, 3, 4],
        "palette": {"drums": "kit", "bass": "Analog", "keys": "Operator",
                    "chords": "Analog", "melody": "Operator", "pad": "Drift"},
        "structure": ["intro:8", "build:8", "drop:16", "break:8", "drop:16", "outro:8"],
        "tips": "Four-on-the-floor kick, offbeat bass & open hats, stabby chords.",
    },
    "techno": {
        "aka": ["melodic techno", "peak time"],
        "bpm": 130, "swing": 0.0, "key": "F minor", "scale": "minor",
        "chord_scale": "minor", "feel": "four_on_floor", "bass_feel": "offbeat",
        "progression": [0, 0, 5, 5],
        "palette": {"drums": "kit", "bass": "Analog", "keys": "Meld",
                    "chords": "Meld", "melody": "Wavetable", "pad": "Meld"},
        "structure": ["intro:16", "build:16", "drop:32", "break:16", "drop:32"],
        "tips": "Driving kick, hypnotic offbeat bass, dark evolving pads.",
    },
    "dnb": {
        "aka": ["drum and bass", "drum & bass", "jungle", "liquid"],
        "bpm": 174, "swing": 0.0, "key": "D minor", "scale": "minor",
        "chord_scale": "minor", "feel": "dnb", "bass_feel": "root_hits",
        "progression": [0, 3, 4, 3],
        "palette": {"drums": "kit", "bass": "Operator", "keys": "Electric",
                    "chords": "Drift", "melody": "Wavetable", "pad": "Drift"},
        "structure": ["intro:16", "drop:32", "break:16", "drop:32", "outro:16"],
        "tips": "Fast breakbeat, sub-heavy bass, lush pads (liquid) or gnarly (neuro).",
    },
    "rnb": {
        "aka": ["r&b", "rnb", "neo soul", "soul"],
        "bpm": 72, "swing": 0.05, "key": "D minor", "scale": "minor_pentatonic",
        "chord_scale": "dorian", "feel": "boom_bap", "bass_feel": "root_hits",
        "progression": [0, 3, 1, 4],
        "palette": {"drums": "kit", "bass": "Operator", "keys": "Electric",
                    "chords": "Electric", "melody": "Electric", "pad": "Drift"},
        "structure": ["intro:4", "verse:16", "chorus:8", "verse:16", "chorus:8", "outro:4"],
        "tips": "Laid-back swung drums, lush Rhodes 7ths, smooth bass, sparse melody.",
    },
    "ambient": {
        "aka": ["ambient", "cinematic", "drone", "soundscape"],
        "bpm": 70, "swing": 0.0, "key": "C major", "scale": "major_pentatonic",
        "chord_scale": "major", "feel": "none", "bass_feel": "sustained",
        "progression": [0, 5, 3, 4],
        "palette": {"drums": "kit", "bass": "Drift", "keys": "Tension",
                    "chords": "Meld", "melody": "Tension", "pad": "Meld"},
        "structure": ["intro:16", "swell:32", "peak:16", "fade:16"],
        "tips": "Often no drums. Long evolving pads, sparse bell/string motifs.",
    },
    "pop": {
        "aka": ["pop", "dance pop", "synth pop"],
        "bpm": 118, "swing": 0.0, "key": "C major", "scale": "major_pentatonic",
        "chord_scale": "major", "feel": "four_on_floor", "bass_feel": "root_hits",
        "progression": [0, 4, 5, 3],   # I - V - vi - IV
        "palette": {"drums": "kit", "bass": "Operator", "keys": "Electric",
                    "chords": "Analog", "melody": "Wavetable", "pad": "Drift"},
        "structure": ["intro:4", "verse:16", "chorus:8", "verse:16", "chorus:8", "bridge:8", "chorus:8"],
        "tips": "Punchy four-on-floor, bright chords, catchy synth/vocal-style melody.",
    },
}

# Drum map (Ableton Drum Rack / GM)
KICK, SNARE, CH, OH, RIM, CLAP, RIDE = 36, 38, 42, 46, 37, 39, 51
BEATS_PER_BAR = 4


def resolve_genre(name: str) -> str:
    """Map a free-text genre to a GENRES key. Defaults to boom_bap."""
    if not name:
        return "boom_bap"
    q = str(name).strip().lower()
    if q in GENRES:
        return q
    for key, prof in GENRES.items():
        if q == key or q in prof.get("aka", []):
            return key
        if any(a in q or q in a for a in prof.get("aka", [])):
            return key
    return "boom_bap"


def genre_profile(name: str) -> Dict[str, Any]:
    prof = dict(GENRES[resolve_genre(name)])
    prof["_key"] = resolve_genre(name)
    return prof


# ---------------------------------------------------------------------------
# 4) PATTERN GENERATORS  (return list of note dicts for the MCP note tools)
#    note = {pitch, start_time (beats), duration (beats), velocity}
# ---------------------------------------------------------------------------
def _n(pitch, start, dur, vel):
    return {"pitch": int(pitch), "start_time": round(float(start), 4),
            "duration": round(float(dur), 4), "velocity": int(max(1, min(127, vel)))}


def drum_pattern(genre: str, bars: int = 8) -> List[Dict[str, Any]]:
    prof = genre_profile(genre)
    feel = prof.get("feel", "boom_bap")
    swing = prof.get("swing", 0.0)
    notes: List[Dict[str, Any]] = []

    for bar in range(bars):
        b = bar * BEATS_PER_BAR
        if feel == "boom_bap":
            for t in (0.0, 2.5):
                notes.append(_n(KICK, b + t, 0.5, 118))
            for t in (1.0, 3.0):
                notes.append(_n(SNARE, b + t, 0.5, 112))
            for i, t in enumerate([0, .5, 1, 1.5, 2, 2.5, 3, 3.5]):
                sw = swing if (i % 2 == 1) else 0.0
                notes.append(_n(CH, b + t + sw, 0.25, 92 if t == int(t) else 64))
            if bar % 4 == 3:
                notes.append(_n(OH, b + 3.5, 0.5, 100))
        elif feel == "four_on_floor":
            for t in (0, 1, 2, 3):
                notes.append(_n(KICK, b + t, 0.5, 116))
            for t in (1, 3):
                notes.append(_n(CLAP, b + t, 0.25, 104))
            for t in (0.5, 1.5, 2.5, 3.5):
                notes.append(_n(OH, b + t, 0.25, 80))
        elif feel == "trap":
            for t in (0.0, 0.75, 2.0):     # syncopated kick
                notes.append(_n(KICK, b + t, 0.5, 118))
            notes.append(_n(SNARE, b + 2.0, 0.5, 110))  # half-time snare on 3
            # rolling hats: 16ths with occasional 32nd rolls
            step = 0.25
            t = 0.0
            while t < 4.0:
                roll = (bar % 2 == 1 and 3.0 <= t < 3.5)
                if roll:
                    for k in range(4):
                        notes.append(_n(CH, b + t + k * 0.125, 0.1, 70))
                else:
                    notes.append(_n(CH, b + t, 0.2, 88 if t == int(t) else 60))
                t += step
        elif feel == "dnb":
            notes.append(_n(KICK, b + 0.0, 0.4, 118))
            notes.append(_n(KICK, b + 2.5, 0.4, 110))
            for t in (1.0, 3.0):
                notes.append(_n(SNARE, b + t, 0.4, 114))
            for t in [x * 0.5 for x in range(8)]:
                notes.append(_n(CH, b + t, 0.2, 84 if t == int(t) else 58))
        elif feel == "none":
            continue  # ambient: no drums
        else:
            for t in (0.0, 2.0):
                notes.append(_n(KICK, b + t, 0.5, 112))
            for t in (1.0, 3.0):
                notes.append(_n(SNARE, b + t, 0.5, 108))
    return notes


def _prog_roots(prof: Dict[str, Any], bars: int) -> List[Tuple[int, int]]:
    """Return [(bar, chord_root_pc_relative_degree)] one chord per bar following progression."""
    root_pc, _ = parse_key(prof.get("key", "A minor"))
    scale = prof.get("chord_scale", "minor")
    heptatonic = SCALES.get(scale, SCALES["minor"])
    heptatonic = heptatonic if len(heptatonic) == 7 else SCALES["minor"]
    prog = prof.get("progression", [0, 3, 4, 3])
    out = []
    for bar in range(bars):
        deg = prog[bar % len(prog)]
        out.append((bar, deg))
    return out


def chord_pattern(genre: str, key: Optional[str] = None, bars: int = 8) -> List[Dict[str, Any]]:
    prof = genre_profile(genre)
    if key:
        prof["key"] = key
    root_pc, _ = parse_key(prof.get("key", "A minor"))
    scale = prof.get("chord_scale", "minor")
    feel = prof.get("feel", "boom_bap")
    notes = []
    for bar, deg in _prog_roots(prof, bars):
        b = bar * BEATS_PER_BAR
        chord = degree_chord(root_pc, scale, deg, octave=2)  # warm low-mid comp register
        if feel == "four_on_floor":     # offbeat stabs
            for t in (0.5, 1.5, 2.5, 3.5):
                for p in chord:
                    notes.append(_n(p, b + t, 0.25, 82))
        elif feel == "trap":            # sparse held on beat 1
            for p in chord:
                notes.append(_n(p, b, 4.0, 74))
        else:                            # boom_bap / rnb / lofi: held 7th on the "and" of 1
            for p in chord:
                notes.append(_n(p, b, 3.5, 84))
    return notes


def bass_pattern(genre: str, key: Optional[str] = None, bars: int = 8) -> List[Dict[str, Any]]:
    prof = genre_profile(genre)
    if key:
        prof["key"] = key
    root_pc, _ = parse_key(prof.get("key", "A minor"))
    scale = prof.get("chord_scale", "minor")
    heptatonic = SCALES.get(scale, SCALES["minor"])
    heptatonic = heptatonic if len(heptatonic) == 7 else SCALES["minor"]
    bass_feel = prof.get("bass_feel", "root_hits")
    notes = []
    for bar, deg in _prog_roots(prof, bars):
        b = bar * BEATS_PER_BAR
        root = root_pc + (1 + 2) * 12 + heptatonic[deg % 7]  # octave 1 (C1=36 area)
        if bass_feel == "root_hits":        # follow the kick: 1 and the "and" of 3
            notes.append(_n(root, b + 0.0, 1.0, 108))
            notes.append(_n(root, b + 2.5, 0.75, 96))
        elif bass_feel == "offbeat":        # house/techno offbeat 8ths
            for t in (0.5, 1.5, 2.5, 3.5):
                notes.append(_n(root, b + t, 0.4, 100))
        elif bass_feel == "eight_oh_eight":  # long 808 glide per bar
            notes.append(_n(root, b + 0.0, 3.5, 112))
        elif bass_feel == "sustained":       # ambient drone
            notes.append(_n(root, b + 0.0, 4.0, 80))
        else:
            notes.append(_n(root, b + 0.0, 1.0, 100))
    return notes


def melody_pattern(genre: str, key: Optional[str] = None, bars: int = 8) -> List[Dict[str, Any]]:
    prof = genre_profile(genre)
    if key:
        prof["key"] = key
    root_pc, scale_name = parse_key(prof.get("key", "A minor"))
    scale = prof.get("scale", "minor_pentatonic")
    pitches = scale_midi(root_pc, scale, lo=60, hi=79)  # C4..G5 range
    if not pitches:
        pitches = scale_midi(root_pc, "minor_pentatonic", 60, 79)
    # deterministic, musical-ish contour (no RNG so results are reproducible)
    contour = [0, 2, 1, 3, 2, 4, 3, 1, 4, 5, 3, 2, 1, 0, 2, 1]
    rhythm = [1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, 2.0]  # beats within a 2-bar phrase-ish
    notes = []
    phrase_len = 4  # bars per phrase
    for bar in range(bars):
        b = bar * BEATS_PER_BAR
        # play on phrase-leading bars, rest on others for space
        if bar % 2 == 1 and prof.get("feel") in ("boom_bap", "trap"):
            continue
        t = 0.0
        ri = bar
        while t < 4.0:
            idx = contour[(bar * 3 + int(t * 2)) % len(contour)]
            pitch = pitches[idx % len(pitches)]
            dur = rhythm[(ri) % len(rhythm)]
            dur = min(dur, 4.0 - t)
            vel = 96 if t == int(t) else 84
            notes.append(_n(pitch, b + t, max(0.25, dur * 0.9), vel))
            t += dur
            ri += 1
    return notes


def pad_pattern(genre: str, key: Optional[str] = None, bars: int = 8) -> List[Dict[str, Any]]:
    """Sustained chords, one per bar (long)."""
    prof = genre_profile(genre)
    if key:
        prof["key"] = key
    root_pc, _ = parse_key(prof.get("key", "A minor"))
    scale = prof.get("chord_scale", "minor")
    notes = []
    for bar, deg in _prog_roots(prof, bars):
        b = bar * BEATS_PER_BAR
        chord = degree_chord(root_pc, scale, deg, octave=3)  # airier register above the comp
        for p in chord:
            notes.append(_n(p, b, 4.0, 70))
    return notes


GENERATORS = {
    "drums": lambda g, k, bars: drum_pattern(g, bars),
    "bass": bass_pattern,
    "chords": chord_pattern,
    "keys": chord_pattern,   # "keys" = comping chords by default
    "melody": melody_pattern,
    "lead": melody_pattern,
    "pad": pad_pattern,
}
ROLES = list(GENERATORS.keys())


def generate(role: str, genre: str, key: Optional[str] = None, bars: int = 8) -> List[Dict[str, Any]]:
    role = (role or "").lower()
    gen = GENERATORS.get(role)
    if gen is None:
        return []
    if role == "drums":
        return drum_pattern(genre, bars)
    return gen(genre, key, bars)


def instrument_for(role: str, genre: str) -> str:
    """Return the instrument NAME (or 'kit') the palette wants for this role+genre."""
    prof = genre_profile(genre)
    role = (role or "").lower()
    palette = prof.get("palette", {})
    if role in palette:
        return palette[role]
    # fall back by role affinity across the catalog
    for name, info in INSTRUMENTS.items():
        if role in info.get("roles", []) and prof["_key"] in info.get("genres", []):
            return name
    return "Operator"


def instrument_load_hint(role: str, genre: str) -> Dict[str, Any]:
    """What the loader needs: either a drum-kit search, or an Instruments device/preset."""
    prof = genre_profile(genre)
    name = instrument_for(role, genre)
    if role.lower() == "drums" or name == "kit":
        hints = KIT_HINTS.get(prof["_key"], {"prefer": [], "avoid": []})
        return {"kind": "kit", "prefer": hints["prefer"], "avoid": hints["avoid"]}
    return {"kind": "instrument", "device": name,
            "desc": INSTRUMENTS.get(name, {}).get("desc", "")}


def suggest_instruments(role: str, genre: str, n: int = 4) -> List[Dict[str, str]]:
    """Curated, ranked instrument suggestions for a role+genre (for the MCP tool)."""
    prof = genre_profile(genre)
    gkey = prof["_key"]
    role = (role or "").lower()
    scored = []
    top = instrument_for(role, genre)
    for name, info in INSTRUMENTS.items():
        if not info.get("roles"):
            continue
        score = 0
        if role in info.get("roles", []):
            score += 2
        if gkey in info.get("genres", []):
            score += 2
        if name == top:
            score += 5
        if score:
            scored.append((score, name, info["desc"]))
    scored.sort(reverse=True)
    return [{"instrument": n, "why": d} for _, n, d in scored[:n]]
