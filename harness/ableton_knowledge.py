"""
ableton_knowledge.py — the "producer brain" for the Ableton MCP server.

Pure data + light helpers, NO MCP / socket dependencies (unit-testable on its own).

Philosophy: this module does NOT generate MIDI. A capable model composes far better
MIDI than a hard-coded generator, and pre-baked notes just give it something to review
and redo. Instead this is a STYLE REFERENCE + INSTRUMENT PICKER: it tells the model how
a genre actually works (feel, drum placement, harmony, bass/melody approach, structure,
reference artists) and which Ableton 12 instrument fits each role, then the model writes
the notes itself via the MCP note tools.

Extensible: add a genre = one GENRES entry + one STYLE entry; add an instrument = one
INSTRUMENTS entry.
"""

from typing import Dict, List, Any, Tuple, Optional

# ---------------------------------------------------------------------------
# 1) ABLETON 12 INSTRUMENT CATALOG   (role = the job it does well)
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
# 2) LIGHT MUSIC-THEORY REFERENCE (for display in the style guide, not generation)
# ---------------------------------------------------------------------------
_NOTE_PC = {"c": 0, "c#": 1, "db": 1, "d": 2, "d#": 3, "eb": 3, "e": 4, "fb": 4,
            "e#": 5, "f": 5, "f#": 6, "gb": 6, "g": 7, "g#": 8, "ab": 8,
            "a": 9, "a#": 10, "bb": 10, "b": 11, "cb": 11}
_PC_NAME = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

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

# Ableton Drum Rack / General-MIDI note reference (C3 = 60 convention)
DRUM_MAP = {
    "kick": 36, "rimshot": 37, "snare": 38, "clap": 39,
    "closed_hat": 42, "open_hat": 46, "low_tom": 45, "mid_tom": 47,
    "hi_tom": 50, "crash": 49, "ride": 51, "shaker": 70, "tambourine": 54,
}

# roman numerals per heptatonic scale degree
_ROMAN = {
    "minor":  ["i", "ii°", "III", "iv", "v", "VI", "VII"],
    "dorian": ["i", "ii", "III", "IV", "v", "vi°", "VII"],
    "major":  ["I", "ii", "iii", "IV", "V", "vi", "vii°"],
}


def parse_key(key: str) -> Tuple[int, str]:
    """'A minor' -> (9, 'minor'); 'F# dorian' -> (6,'dorian'); default A minor."""
    if not key:
        return 9, "minor"
    parts = str(key).strip().split()
    if not parts or parts[0].lower() not in _NOTE_PC:
        return 9, "minor"  # consistent default: unparseable == empty == A minor
    root = _NOTE_PC[parts[0].lower()]
    scale = "minor"
    if len(parts) > 1:
        s = "_".join(parts[1:]).lower()
        s = {"min": "minor", "maj": "major", "pentatonic": "minor_pentatonic",
             "minor_pent": "minor_pentatonic"}.get(s, s)
        if s in SCALES:
            scale = s
    return root, scale


def scale_note_names(root_pc: int, scale: str) -> List[str]:
    """Note names of one octave of a scale (for the style guide)."""
    ivals = SCALES.get(scale, SCALES["minor"])
    return [_PC_NAME[(root_pc + i) % 12] for i in ivals]


def progression_roman(prof: Dict[str, Any]) -> Dict[str, Any]:
    """Render a genre's suggested progression as roman numerals + chord roots."""
    root_pc, _ = parse_key(prof.get("key", "A minor"))
    scale = prof.get("chord_scale", "minor")
    hept = SCALES.get(scale, SCALES["minor"])
    hept = hept if len(hept) == 7 else SCALES["minor"]
    roman = _ROMAN.get(scale, _ROMAN["minor"])
    prog = prof.get("progression", [0, 3, 4, 3])
    rn = [roman[d % 7] for d in prog]
    roots = [_PC_NAME[(root_pc + hept[d % 7]) % 12] for d in prog]
    return {"roman": " - ".join(rn), "chord_roots": roots, "scale": scale}


# ---------------------------------------------------------------------------
# 3) GENRE PROFILES  (tempo/key/palette/structure — extensible)
# ---------------------------------------------------------------------------
GENRES: Dict[str, Dict[str, Any]] = {
    "boom_bap": {
        "aka": ["boom bap", "boombap", "hip hop", "hiphop", "90s hip hop", "east coast"],
        "bpm": 88, "bpm_range": "85-92", "swing": 0.06, "key": "A minor",
        "scale": "minor_pentatonic", "chord_scale": "dorian", "progression": [0, 3, 4, 3],
        "palette": {"drums": "kit", "bass": "Operator", "keys": "Electric",
                    "chords": "Electric", "melody": "Electric", "pad": "Drift"},
        "structure": ["intro:4", "verse:16", "hook:8", "verse:16", "hook:8", "outro:4"],
    },
    "lofi": {
        "aka": ["lo-fi", "lo fi", "chillhop", "study beats"],
        "bpm": 80, "bpm_range": "70-85", "swing": 0.08, "key": "F major",
        "scale": "major_pentatonic", "chord_scale": "major", "progression": [1, 4, 0, 5],
        "palette": {"drums": "kit", "bass": "Operator", "keys": "Electric",
                    "chords": "Electric", "melody": "Collision", "pad": "Drift"},
        "structure": ["intro:4", "loop:16", "loop:16", "outro:4"],
    },
    "trap": {
        "aka": ["trap beat", "drill"],
        "bpm": 140, "bpm_range": "130-150 (half-time feel ~70)", "swing": 0.0, "key": "C minor",
        "scale": "minor", "chord_scale": "minor", "progression": [0, 5, 3, 4],
        "palette": {"drums": "kit", "bass": "Operator", "keys": "Operator",
                    "chords": "Wavetable", "melody": "Wavetable", "pad": "Wavetable"},
        "structure": ["intro:4", "verse:16", "hook:8", "verse:16", "hook:8"],
    },
    "house": {
        "aka": ["deep house", "tech house", "4x4"],
        "bpm": 124, "bpm_range": "120-126", "swing": 0.0, "key": "A minor",
        "scale": "minor", "chord_scale": "minor", "progression": [0, 5, 3, 4],
        "palette": {"drums": "kit", "bass": "Analog", "keys": "Operator",
                    "chords": "Analog", "melody": "Operator", "pad": "Drift"},
        "structure": ["intro:8", "build:8", "drop:16", "break:8", "drop:16", "outro:8"],
    },
    "techno": {
        "aka": ["melodic techno", "peak time"],
        "bpm": 130, "bpm_range": "125-135", "swing": 0.0, "key": "F minor",
        "scale": "minor", "chord_scale": "minor", "progression": [0, 0, 5, 5],
        "palette": {"drums": "kit", "bass": "Analog", "keys": "Meld",
                    "chords": "Meld", "melody": "Wavetable", "pad": "Meld"},
        "structure": ["intro:16", "build:16", "drop:32", "break:16", "drop:32"],
    },
    "dnb": {
        "aka": ["drum and bass", "drum & bass", "jungle", "liquid"],
        "bpm": 174, "bpm_range": "170-176", "swing": 0.0, "key": "D minor",
        "scale": "minor", "chord_scale": "minor", "progression": [0, 3, 4, 3],
        "palette": {"drums": "kit", "bass": "Operator", "keys": "Electric",
                    "chords": "Drift", "melody": "Wavetable", "pad": "Drift"},
        "structure": ["intro:16", "drop:32", "break:16", "drop:32", "outro:16"],
    },
    "rnb": {
        "aka": ["r&b", "rnb", "neo soul", "soul"],
        "bpm": 72, "bpm_range": "60-75", "swing": 0.05, "key": "D minor",
        "scale": "minor_pentatonic", "chord_scale": "dorian", "progression": [0, 3, 1, 4],
        "palette": {"drums": "kit", "bass": "Operator", "keys": "Electric",
                    "chords": "Electric", "melody": "Electric", "pad": "Drift"},
        "structure": ["intro:4", "verse:16", "chorus:8", "verse:16", "chorus:8", "outro:4"],
    },
    "ambient": {
        "aka": ["ambient", "cinematic", "drone", "soundscape"],
        "bpm": 70, "bpm_range": "60-80 or free", "swing": 0.0, "key": "C major",
        "scale": "major_pentatonic", "chord_scale": "major", "progression": [0, 5, 3, 4],
        "palette": {"drums": "kit", "bass": "Drift", "keys": "Tension",
                    "chords": "Meld", "melody": "Tension", "pad": "Meld"},
        "structure": ["intro:16", "swell:32", "peak:16", "fade:16"],
    },
    "pop": {
        "aka": ["pop", "dance pop", "synth pop"],
        "bpm": 118, "bpm_range": "100-125", "swing": 0.0, "key": "C major",
        "scale": "major_pentatonic", "chord_scale": "major", "progression": [0, 4, 5, 3],
        "palette": {"drums": "kit", "bass": "Operator", "keys": "Electric",
                    "chords": "Analog", "melody": "Wavetable", "pad": "Drift"},
        "structure": ["intro:4", "verse:16", "chorus:8", "verse:16", "chorus:8", "bridge:8", "chorus:8"],
    },
}

ROLES = ["drums", "bass", "chords", "keys", "melody", "lead", "pad"]


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
# 4) STYLE REFERENCE — how each genre actually works, in words. The model reads
#    this and composes its OWN MIDI. Reference artists are baked in as knowledge.
# ---------------------------------------------------------------------------
STYLE: Dict[str, Dict[str, Any]] = {
    "boom_bap": {
        "feel": "Laid-back and dusty. Compose ON-GRID - the engine applies the swing and "
                "behind-the-beat feel for you. Your job is PLACEMENT and note choice.",
        "drums": "Kick (36) ON beat 1 of every bar, plus ONE syncopated kick per bar at the 'and' "
                 "of 2 or of 3 (grid position 1.5 or 2.5). Snare (38) exactly ON beats 2 and 4, velocity "
                 "100+. Closed hats (42) as straight on-grid 8ths, velocity varied 60-95 (engine swings "
                 "them). Open hat (46) once every 2-4 bars as a lift. Quiet ghost snares (vel 20-40) "
                 "between backbeats.",
        "harmony": "Minor or Dorian. Jazzy 7th/9th chords (min7, dom7, min9) voiced on Rhodes in a "
                   "low-mid register. Short 2-4 bar loops. Movement like i-iv or ii-V-i.",
        "bass": "Upright or electric bass locked to the kick. Mostly roots with occasional walking "
                "passing tones. Simple, in the pocket, leaves space.",
        "melody": "Sparse and soulful, minor pentatonic / Dorian. Leave gaps; answer the chords. "
                  "Think a chopped soul-sample line, not a busy solo.",
        "references": ["DJ Premier (Gang Starr)", "Pete Rock", "J Dilla", "Nujabes", "Madlib",
                       "A Tribe Called Quest", "Wu-Tang / RZA"],
        "avoid": "Rigid quantization, trap 808 kicks/hats, over-busy melodies, bright EDM sounds.",
    },
    "lofi": {
        "feel": "Slow, hazy, soft dynamics. Compose ON-GRID - the engine applies the heavy swing "
                "and lazy feel. Focus on sparse placement and warm note choice.",
        "drums": "Kick (36) ON beat 1 and at grid position 2.5 ('and' of 3). Snare/rimshot (38/37) "
                 "exactly ON beats 2 and 4, velocity 70-90. Hats (42) as on-grid 8ths, sparse (skip some), "
                 "velocity 50-80. The engine adds the lazy swing.",
        "harmony": "Warm jazzy 7th/9th and maj7 chords, often Dorian or major. Detuned, mellow. "
                   "ii-V-I and vi-based loops.",
        "bass": "Round, soft bass following roots on the kick. Very simple.",
        "melody": "Gentle, wandering, pentatonic. Mallet/Rhodes lines with lots of space.",
        "references": ["Nujabes", "J Dilla", "idealism", "Tomppabeats", "Jinsang"],
        "avoid": "Loud/hard drums, aggressive synths, dense arrangements.",
    },
    "trap": {
        "feel": "Half-time feel: the beat reads slow (~70) though the grid is ~140. Dark and spacious.",
        "drums": "Booming tuned 808 kick (36) syncopated. Snare or clap (38/39) on beat 3 (half-time "
                 "backbeat). Fast hi-hats (42) as 16ths with bursts of triplet/32nd ROLLS and velocity "
                 "ramps. Occasional open hat (46).",
        "harmony": "Dark minor. Sparse — one held minor chord or a simple i-VI-III-VII loop. Often just "
                   "a bell/pluck riff over the 808.",
        "bass": "The 808 IS the bass: long gliding notes tuned to the key root, sliding between chord "
                "roots. Sits low and loud.",
        "melody": "Dark bell/pluck motif, minor scale, lots of repetition and space.",
        "references": ["Metro Boomin", "Southside (808 Mafia)", "Zaytoven", "Wheezy", "Pierre Bourne"],
        "avoid": "Jazzy chords, acoustic kits, busy basslines competing with the 808.",
    },
    "house": {
        "feel": "Four-on-the-floor, steady and danceable, driving forward.",
        "drums": "Kick (36) on EVERY beat (1,2,3,4). Clap/snare (39/38) on 2 and 4. Open hat (46) on "
                 "the offbeats (the 'ands') for the classic bounce. Closed hats fill 16ths lightly.",
        "harmony": "Minor. Stabby 7th/9th chords on the offbeats, or sustained pads. Simple i-VI-III-VII.",
        "bass": "Offbeat bass — notes on the 'ands', bouncing with the open hats. Rolling and hypnotic.",
        "melody": "Simple hooky riff or plucky arp; repetition is the point.",
        "references": ["Disclosure", "Kerri Chandler", "MK", "Duke Dumont", "Kaytranada (soulful)"],
        "avoid": "Swung hip-hop drums, sparse/half-time feel, over-complex chords.",
    },
    "techno": {
        "feel": "Hypnotic, driving, minimal. Repetition + slow evolution over many bars.",
        "drums": "Relentless four-on-the-floor kick (36). Offbeat open hats (46). Sparse claps/rims; "
                 "percussion loops for groove. Less is more.",
        "harmony": "Dark minor. One or two chords, held or pulsing. Tension from filters/texture, not "
                   "changes.",
        "bass": "Offbeat or rolling 16th sub bass on the root, hypnotic and relentless.",
        "melody": "Minimal dark motif or arpeggio that slowly evolves; often no traditional melody.",
        "references": ["Charlotte de Witte", "Tale of Us", "Adam Beyer", "Boris Brejcha", "Amelie Lens"],
        "avoid": "Busy chord changes, bright/happy tones, swung drums.",
    },
    "dnb": {
        "feel": "Fast (~174) but the bassline reads half-time. Rolling breakbeat energy.",
        "drums": "Breakbeat: kick (36) on beat 1 and around the 'and' of 3; snare (38) on 2 and 4; "
                 "busy syncopated ghost kicks/snares and fast hats. Think a chopped Amen break.",
        "harmony": "Minor. Lush pads (liquid) or minimal/dark (neuro). Simple loops.",
        "bass": "Deep sub or reese bass, long notes on chord roots (half-time), the anchor under the "
                "fast drums.",
        "melody": "Liquid: soulful Rhodes/vocal chops. Neuro: gnarly modulated stabs. Sparse.",
        "references": ["LTJ Bukem (liquid)", "Netsky", "Calibre", "Noisia (neuro)", "Sub Focus"],
        "avoid": "Slow four-on-floor kicks, dense mid-range clutter under the drums.",
    },
    "rnb": {
        "feel": "Slow, smooth, silky, intimate. Compose ON-GRID - the engine adds the deep swing "
                "and behind-the-beat lean. Focus on lush harmony and space.",
        "drums": "Kick (36) ON beat 1 plus one syncopated grid hit per bar (position 1.75 or 2.5). "
                 "Crisp snare/rim (38/37) exactly ON beats 2 and 4. Hats (42) on-grid 8ths, velocity 55-85. "
                 "Ghost snares vel 20-40. Groove over power - the engine supplies the swing.",
        "harmony": "Lush extended chords — min9, maj9, 11ths — on Rhodes, Dorian/minor. Smooth voice "
                   "leading, ii-V movement.",
        "bass": "Smooth electric/sub bass, melodic but supportive, syncopated with the kick.",
        "melody": "Sparse, soulful, vocal-like phrases with space for a topline.",
        "references": ["D'Angelo", "Erykah Badu", "H.E.R.", "SZA", "Steve Lacy", "Brent Faiyaz"],
        "avoid": "Stiff quantization, harsh/bright synths, cluttered arrangements.",
    },
    "ambient": {
        "feel": "Slow or beatless, spacious, evolving. Time feels suspended.",
        "drums": "Often NONE. If used: sparse soft percussion, mallets, or a distant heartbeat pulse.",
        "harmony": "Long sustained pads, open voicings (add9, sus), slow changes. Major or modal, "
                   "consonant and warm.",
        "bass": "Deep sustained drone on the root, or none — let the pad hold the low end.",
        "melody": "Very sparse — a few long bell/string notes, motifs that drift and repeat.",
        "references": ["Brian Eno", "Nils Frahm", "Stars of the Lid", "Tim Hecker", "Jon Hopkins"],
        "avoid": "Rhythmic drums, busy notes, hard transients, fast changes.",
    },
    "pop": {
        "feel": "Bright, catchy, tight. Clear hook and strong groove.",
        "drums": "Four-on-the-floor OR a punchy backbeat (snare on 2 and 4, kick on 1 and 3). Clean, "
                 "consistent hats, a clap layered on the snare.",
        "harmony": "Bright diatonic major chords — classic I-V-vi-IV and friends. Clear, singable.",
        "bass": "Root-driven, locked to the kick, simple and supportive.",
        "melody": "Strong, catchy, singable hook. Repetition + a memorable rhythmic motif.",
        "references": ["Max Martin productions", "Dua Lipa", "The Weeknd", "Doja Cat", "Charli XCX"],
        "avoid": "Muddy low end, wandering non-hooky melodies, overly complex harmony.",
    },
}


def style_guide(genre: str, role: str = "") -> Dict[str, Any]:
    """Return rich, composable STYLE guidance for a genre (optionally focused on one role).
    The model uses this to write its OWN MIDI — this returns knowledge, not notes."""
    prof = genre_profile(genre)
    gkey = prof["_key"]
    st = STYLE.get(gkey, STYLE["boom_bap"])
    root_pc, _ = parse_key(prof.get("key", "A minor"))
    guide: Dict[str, Any] = {
        "genre": gkey.replace("_", " "),
        "bpm": prof["bpm"], "bpm_range": prof.get("bpm_range"),
        "key": prof["key"], "swing": prof.get("swing"),
        "feel": st["feel"],
        "scale_notes": scale_note_names(root_pc, prof.get("scale", "minor")),
        "suggested_progression": progression_roman(prof),
        "drum_map": DRUM_MAP,
        "drums": st["drums"], "harmony": st["harmony"], "bass": st["bass"], "melody": st["melody"],
        "arrangement": prof.get("structure"),
        "instrument_palette": prof.get("palette"),
        "reference_artists": st["references"],
        "avoid": st["avoid"],
        "how_to_use": ("Compose the MIDI yourself following this guidance and write it with "
                       "add_notes_to_arrangement_clip. Times are in BEATS (1 bar of 4/4 = 4 beats). "
                       "Humanize velocity/timing where the feel calls for it."),
    }
    if role:
        r = role.lower()
        focus = {"drums": st["drums"], "bass": st["bass"], "pad": st["harmony"],
                 "chords": st["harmony"], "keys": st["harmony"],
                 "melody": st["melody"], "lead": st["melody"]}.get(r)
        if focus:
            guide["focus_role"] = role
            guide["focus"] = focus
    return guide


# ---------------------------------------------------------------------------
# 5) INSTRUMENT SELECTION
# ---------------------------------------------------------------------------
def instrument_for(role: str, genre: str) -> str:
    """Return the instrument NAME (or 'kit') the palette wants for this role+genre."""
    prof = genre_profile(genre)
    role = (role or "").lower()
    palette = prof.get("palette", {})
    if role in palette:
        return palette[role]
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
