#!/usr/bin/env python3
"""
MIDI Analyzer for Dataset Generation
=====================================
Extracts musical features from MIDI files for composition training data.

Features Extracted:
1. Note-level: pitch, velocity, duration, start_time
2. Pattern-level: chord detection, scale inference, rhythm analysis
3. File-level: BPM, key, density, instrument type (from filename)

Output format matches the write_midi tool schema for consistency.

Usage:
    # Analyze all MIDI from inventory
    python analyze_midi.py --from-inventory data/sample_pack_inventory.json

    # Analyze specific directory
    python analyze_midi.py --path /path/to/midi/files

    # Analyze single file
    python analyze_midi.py --file song.mid
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from collections import Counter, defaultdict
import mido
from mido import MidiFile, MidiTrack


# =============================================================================
# MUSIC THEORY CONSTANTS
# =============================================================================

# Note names
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Scale patterns (intervals from root)
SCALE_PATTERNS = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'pentatonic_major': [0, 2, 4, 7, 9],
    'pentatonic_minor': [0, 3, 5, 7, 10],
    'blues': [0, 3, 5, 6, 7, 10],
}

# Common chord types (intervals from root)
CHORD_TYPES = {
    'major': [0, 4, 7],
    'minor': [0, 3, 7],
    'dim': [0, 3, 6],
    'aug': [0, 4, 8],
    'sus2': [0, 2, 7],
    'sus4': [0, 5, 7],
    'maj7': [0, 4, 7, 11],
    'min7': [0, 3, 7, 10],
    'dom7': [0, 4, 7, 10],
    '7sus4': [0, 5, 7, 10],
}

# Instrument categories by filename keywords (ordered by priority - check first matches first)
# Note: Using word boundary matching to avoid false positives like "flow" matching "low"
INSTRUMENT_KEYWORDS = {
    'drums': ['drum', 'kick', 'snare', 'hihat', 'hi-hat', 'perc', 'clap', 'cymbal'],
    'chords': ['chord', 'chords', 'pad', 'keys', 'piano', 'organ', 'stab'],
    'bass': ['bass', '808', ' sub '],  # Note: " sub " with spaces to avoid "sub" in words
    'lead': ['lead', 'melody'],
    'arp': ['arp', 'arpegg'],
    'strings': ['string', 'strings', 'violin', 'cello'],
    'fx': ['fx', 'riser', 'sweep', 'impact', 'buildup'],
}

# GM Drum map (for channel 10 / track 10 or drum tracks)
GM_DRUM_MAP = {
    35: 'acoustic_bass_drum', 36: 'bass_drum', 37: 'side_stick', 38: 'snare',
    39: 'clap', 40: 'electric_snare', 41: 'low_floor_tom', 42: 'closed_hihat',
    43: 'high_floor_tom', 44: 'pedal_hihat', 45: 'low_tom', 46: 'open_hihat',
    47: 'low_mid_tom', 48: 'hi_mid_tom', 49: 'crash', 50: 'high_tom',
    51: 'ride', 52: 'chinese_cymbal', 53: 'ride_bell', 54: 'tambourine',
    55: 'splash', 56: 'cowbell', 57: 'crash_2', 58: 'vibraslap',
    59: 'ride_2', 60: 'hi_bongo', 61: 'low_bongo', 62: 'mute_hi_conga',
    63: 'open_hi_conga', 64: 'low_conga', 65: 'high_timbale', 66: 'low_timbale',
    67: 'high_agogo', 68: 'low_agogo', 69: 'cabasa', 70: 'maracas',
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class MidiNote:
    """Single MIDI note in tool-compatible format."""
    pitch: int          # 0-127
    start: float        # beats from start
    duration: float     # beats
    velocity: int       # 0-127

    # Derived properties (not in tool schema, but useful)
    note_name: str = ""
    octave: int = 0

    def __post_init__(self):
        self.note_name = NOTE_NAMES[self.pitch % 12]
        self.octave = (self.pitch // 12) - 1


@dataclass
class ChordEvent:
    """Detected chord at a specific time."""
    start: float        # beats
    duration: float     # beats
    root: str           # note name (C, C#, etc.)
    type: str           # major, minor, etc.
    notes: List[int]    # MIDI pitches


@dataclass
class RhythmPattern:
    """Analyzed rhythm pattern."""
    hits_per_bar: int
    on_beat_ratio: float    # % of notes on beats
    offbeat_ratio: float    # % of notes on offbeats
    syncopation: float      # 0-1, higher = more syncopated
    note_density: float     # notes per beat
    common_durations: List[float]  # most common note lengths in beats


@dataclass
class MidiAnalysis:
    """Complete analysis of a MIDI file."""
    # File info
    filepath: str
    filename: str

    # Extracted from filename
    bpm_from_filename: Optional[int] = None
    key_from_filename: Optional[str] = None
    instrument_type: str = "unknown"

    # MIDI metadata
    ticks_per_beat: int = 480
    detected_bpm: Optional[float] = None
    duration_beats: float = 0.0
    duration_seconds: float = 0.0

    # Note statistics
    total_notes: int = 0
    unique_pitches: int = 0
    pitch_range: Tuple[int, int] = (0, 0)
    avg_velocity: float = 0.0
    velocity_range: Tuple[int, int] = (0, 0)

    # Musical analysis
    detected_key: Optional[str] = None
    detected_scale: Optional[str] = None
    key_confidence: float = 0.0

    # Pattern analysis
    is_drum_pattern: bool = False
    chord_progression: List[Dict] = field(default_factory=list)
    rhythm_analysis: Optional[Dict] = None

    # Notes in tool-compatible format
    notes: List[Dict] = field(default_factory=list)

    # Drum-specific (if drum pattern)
    drum_elements: List[str] = field(default_factory=list)
    drum_pattern_type: str = ""  # 4/4, breakbeat, etc.


# =============================================================================
# MIDI PARSING
# =============================================================================

def parse_midi_file(filepath: str) -> Tuple[List[MidiNote], int, Optional[float]]:
    """
    Parse MIDI file and extract all notes.

    Returns:
        notes: List of MidiNote objects
        ticks_per_beat: MIDI resolution
        tempo_bpm: Detected BPM if tempo event found
    """
    try:
        midi = MidiFile(filepath)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return [], 480, None

    ticks_per_beat = midi.ticks_per_beat
    tempo_bpm = None

    # Extract tempo from tempo events
    for track in midi.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo_bpm = mido.tempo2bpm(msg.tempo)
                break
        if tempo_bpm:
            break

    # Parse all note events
    notes = []

    for track in midi.tracks:
        current_time = 0  # in ticks
        active_notes = {}  # pitch -> (start_tick, velocity)

        for msg in track:
            current_time += msg.time

            if msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = (current_time, msg.velocity)

            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    start_tick, velocity = active_notes.pop(msg.note)
                    duration_ticks = current_time - start_tick

                    # Convert to beats
                    start_beats = start_tick / ticks_per_beat
                    duration_beats = duration_ticks / ticks_per_beat

                    notes.append(MidiNote(
                        pitch=msg.note,
                        start=round(start_beats, 4),
                        duration=round(duration_beats, 4),
                        velocity=velocity,
                    ))

    # Sort by start time
    notes.sort(key=lambda n: (n.start, n.pitch))

    return notes, ticks_per_beat, tempo_bpm


# =============================================================================
# MUSICAL ANALYSIS
# =============================================================================

def detect_key_and_scale(notes: List[MidiNote]) -> Tuple[Optional[str], Optional[str], float]:
    """
    Detect the most likely key and scale from notes.

    Uses pitch class histogram matching against scale templates.

    Returns:
        key: Root note name (e.g., "C", "F#")
        scale: Scale type (e.g., "major", "minor")
        confidence: 0-1 score
    """
    if not notes:
        return None, None, 0.0

    # Build pitch class histogram (weighted by duration)
    pitch_classes = defaultdict(float)
    for note in notes:
        pc = note.pitch % 12
        pitch_classes[pc] += note.duration

    # Normalize
    total = sum(pitch_classes.values())
    if total == 0:
        return None, None, 0.0

    pitch_histogram = {pc: count / total for pc, count in pitch_classes.items()}

    best_key = None
    best_scale = None
    best_score = 0.0

    # Try each root note and scale combination
    for root in range(12):
        for scale_name, intervals in SCALE_PATTERNS.items():
            # Get pitch classes in this scale
            scale_pcs = set((root + i) % 12 for i in intervals)

            # Score: sum of histogram weights for notes in scale
            score = sum(pitch_histogram.get(pc, 0) for pc in scale_pcs)

            # Penalize notes outside scale
            outside_weight = sum(
                pitch_histogram.get(pc, 0)
                for pc in range(12)
                if pc not in scale_pcs
            )
            score -= outside_weight * 0.5

            if score > best_score:
                best_score = score
                best_key = NOTE_NAMES[root]
                best_scale = scale_name

    # Convert score to confidence (0-1)
    confidence = min(best_score, 1.0)

    return best_key, best_scale, confidence


def detect_chords(notes: List[MidiNote], window_beats: float = 0.25) -> List[ChordEvent]:
    """
    Detect chords by finding simultaneous notes.

    Args:
        notes: List of MIDI notes
        window_beats: Time window for grouping notes into chords

    Returns:
        List of detected chords
    """
    if not notes:
        return []

    chords = []

    # Group notes by start time (within window)
    time_groups = defaultdict(list)
    for note in notes:
        # Round to window
        group_time = round(note.start / window_beats) * window_beats
        time_groups[group_time].append(note)

    for start_time, group_notes in sorted(time_groups.items()):
        if len(group_notes) < 3:
            continue  # Need at least 3 notes for a chord

        # Get unique pitch classes
        pitches = sorted(set(n.pitch for n in group_notes))
        pitch_classes = sorted(set(p % 12 for p in pitches))

        if len(pitch_classes) < 3:
            continue

        # Try to identify chord type
        best_chord = None
        best_match = 0

        for root_pc in pitch_classes:
            for chord_name, intervals in CHORD_TYPES.items():
                chord_pcs = set((root_pc + i) % 12 for i in intervals)
                match = len(chord_pcs & set(pitch_classes)) / len(chord_pcs)

                if match > best_match:
                    best_match = match
                    best_chord = (NOTE_NAMES[root_pc], chord_name, pitches)

        if best_chord and best_match >= 0.75:
            # Calculate chord duration (min duration of notes)
            duration = min(n.duration for n in group_notes)

            chords.append(ChordEvent(
                start=start_time,
                duration=duration,
                root=best_chord[0],
                type=best_chord[1],
                notes=best_chord[2],
            ))

    return chords


def analyze_rhythm(notes: List[MidiNote], time_sig_beats: int = 4) -> RhythmPattern:
    """
    Analyze rhythm patterns from notes.

    Args:
        notes: List of MIDI notes
        time_sig_beats: Beats per bar (default 4/4)

    Returns:
        RhythmPattern with statistics
    """
    if not notes:
        return RhythmPattern(
            hits_per_bar=0, on_beat_ratio=0, offbeat_ratio=0,
            syncopation=0, note_density=0, common_durations=[],
        )

    # Count notes on beats vs offbeats
    on_beat = 0
    offbeat = 0
    syncopated = 0

    durations = []

    for note in notes:
        durations.append(note.duration)

        # Position within beat
        beat_pos = note.start % 1.0

        if beat_pos < 0.05 or beat_pos > 0.95:  # On the beat
            on_beat += 1
        elif 0.45 < beat_pos < 0.55:  # On the & (8th note offbeat)
            offbeat += 1
        else:  # Syncopated
            syncopated += 1

    total = len(notes)

    # Find common durations
    duration_counts = Counter(round(d, 2) for d in durations)
    common_durations = [d for d, _ in duration_counts.most_common(5)]

    # Calculate total duration
    if notes:
        total_beats = max(n.start + n.duration for n in notes)
        total_bars = total_beats / time_sig_beats
        hits_per_bar = int(total / max(total_bars, 1))
        note_density = total / max(total_beats, 1)
    else:
        hits_per_bar = 0
        note_density = 0

    return RhythmPattern(
        hits_per_bar=hits_per_bar,
        on_beat_ratio=round(on_beat / total, 3) if total else 0,
        offbeat_ratio=round(offbeat / total, 3) if total else 0,
        syncopation=round(syncopated / total, 3) if total else 0,
        note_density=round(note_density, 3),
        common_durations=common_durations,
    )


def detect_drum_elements(notes: List[MidiNote], filename: str = "") -> Tuple[bool, List[str], str]:
    """
    Detect if MIDI is a drum pattern and identify elements.

    Returns:
        is_drum: True if this appears to be drums
        elements: List of drum element names
        pattern_type: Style description (e.g., "4/4 kick-snare")
    """
    if not notes:
        return False, [], ""

    # First check filename for melodic indicators (override pitch-based detection)
    filename_lower = filename.lower()
    melodic_keywords = ['chord', 'lead', 'bass', 'melody', 'pad', 'arp', 'keys', 'piano',
                        'strings', 'synth', 'organ', 'brass', 'choir', 'woodwind', 'buildup']
    if any(kw in filename_lower for kw in melodic_keywords):
        return False, [], ""

    # Check filename for drum indicators
    drum_keywords = ['drum', 'kick', 'snare', 'hat', 'perc', 'hihat', 'clap', 'tom']
    filename_says_drums = any(kw in filename_lower for kw in drum_keywords)

    # Check if notes are in typical drum range (35-81 GM drums)
    pitches = [n.pitch for n in notes]
    avg_pitch = sum(pitches) / len(pitches)

    # Drums typically centered around 36-60
    # Melodic content typically higher
    is_drum = filename_says_drums or ((35 <= avg_pitch <= 55) and (max(pitches) - min(pitches) < 20))

    if not is_drum:
        # Check for typical drum pitch clustering (very specific pitches, no scales)
        pitch_set = set(pitches)
        # Drums usually use specific pitches, not scales - be more conservative
        if len(pitch_set) < 10 and all(35 <= p <= 70 for p in pitch_set):
            is_drum = True

    if not is_drum:
        return False, [], ""

    # Identify drum elements
    elements = set()
    for note in notes:
        if note.pitch in GM_DRUM_MAP:
            elements.add(GM_DRUM_MAP[note.pitch])
        elif 35 <= note.pitch <= 40:
            elements.add('kick')
        elif 37 <= note.pitch <= 40:
            elements.add('snare')
        elif 42 <= note.pitch <= 46:
            elements.add('hihat')
        elif 49 <= note.pitch <= 57:
            elements.add('cymbal')

    # Determine pattern type
    has_kick = any('kick' in e or 'bass_drum' in e for e in elements)
    has_snare = any('snare' in e for e in elements)
    has_hat = any('hat' in e for e in elements)

    if has_kick and has_snare and has_hat:
        pattern_type = "full_kit"
    elif has_kick and has_snare:
        pattern_type = "kick_snare"
    elif has_hat:
        pattern_type = "hats_only"
    elif has_kick:
        pattern_type = "kick_only"
    else:
        pattern_type = "percussion"

    return True, list(elements), pattern_type


# =============================================================================
# FILENAME PARSING
# =============================================================================

def extract_from_filename(filename: str) -> Tuple[Optional[int], Optional[str], str]:
    """
    Extract BPM, key, and instrument type from filename.

    Common patterns:
    - TSP_S2PE_126_bass_brassy_Gmin.mid
    - 120_Cmaj_bass_loop.mid
    - drum_pattern_house_128bpm.mid
    """
    name = filename.lower()

    # BPM extraction
    bpm = None
    bpm_patterns = [
        r'(\d{2,3})_?bpm',
        r'_(\d{2,3})_',
        r'^(\d{2,3})_',
    ]
    for pattern in bpm_patterns:
        match = re.search(pattern, name)
        if match:
            potential_bpm = int(match.group(1))
            if 60 <= potential_bpm <= 200:
                bpm = potential_bpm
                break

    # Key extraction
    key = None
    key_patterns = [
        r'([a-g][#b]?)(maj|min|major|minor)',
        r'_([a-g][#b]?)(?:maj|min)?_',
    ]
    for pattern in key_patterns:
        match = re.search(pattern, name)
        if match:
            key = match.group(1).upper()
            if len(match.groups()) > 1 and match.group(2):
                modifier = match.group(2)
                if 'min' in modifier:
                    key += 'm'
                else:
                    key += 'maj'
            break

    # Instrument type
    instrument = "unknown"
    for inst_type, keywords in INSTRUMENT_KEYWORDS.items():
        if any(kw in name for kw in keywords):
            instrument = inst_type
            break

    return bpm, key, instrument


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def analyze_midi(filepath: str) -> MidiAnalysis:
    """
    Complete analysis of a MIDI file.

    Returns MidiAnalysis with all extracted features.
    """
    path = Path(filepath)
    filename = path.name

    # Extract from filename
    bpm_fn, key_fn, instrument = extract_from_filename(filename)

    # Parse MIDI
    notes, ticks_per_beat, detected_bpm = parse_midi_file(filepath)

    if not notes:
        return MidiAnalysis(
            filepath=filepath,
            filename=filename,
            bpm_from_filename=bpm_fn,
            key_from_filename=key_fn,
            instrument_type=instrument,
            ticks_per_beat=ticks_per_beat,
        )

    # Basic statistics
    pitches = [n.pitch for n in notes]
    velocities = [n.velocity for n in notes]

    total_notes = len(notes)
    unique_pitches = len(set(pitches))
    pitch_range = (min(pitches), max(pitches))
    avg_velocity = sum(velocities) / total_notes
    velocity_range = (min(velocities), max(velocities))

    # Duration
    duration_beats = max(n.start + n.duration for n in notes)
    if bpm_fn or detected_bpm:
        bpm_for_calc = bpm_fn or detected_bpm
        duration_seconds = duration_beats * 60 / bpm_for_calc
    else:
        duration_seconds = 0

    # Musical analysis
    detected_key, detected_scale, key_confidence = detect_key_and_scale(notes)

    # Drum detection
    is_drum, drum_elements, drum_pattern_type = detect_drum_elements(notes, filename)

    # Chord detection (only if not drums)
    chord_progression = []
    if not is_drum:
        chords = detect_chords(notes)
        chord_progression = [
            {"start": c.start, "root": c.root, "type": c.type}
            for c in chords
        ]

    # Rhythm analysis
    rhythm = analyze_rhythm(notes)

    # Convert notes to tool-compatible format
    notes_dict = [
        {"pitch": n.pitch, "start": n.start, "duration": n.duration, "velocity": n.velocity}
        for n in notes
    ]

    return MidiAnalysis(
        filepath=filepath,
        filename=filename,
        bpm_from_filename=bpm_fn,
        key_from_filename=key_fn,
        instrument_type=instrument if not is_drum else "drums",
        ticks_per_beat=ticks_per_beat,
        detected_bpm=detected_bpm,
        duration_beats=round(duration_beats, 2),
        duration_seconds=round(duration_seconds, 2),
        total_notes=total_notes,
        unique_pitches=unique_pitches,
        pitch_range=pitch_range,
        avg_velocity=round(avg_velocity, 1),
        velocity_range=velocity_range,
        detected_key=detected_key,
        detected_scale=detected_scale,
        key_confidence=round(key_confidence, 3),
        is_drum_pattern=is_drum,
        chord_progression=chord_progression,
        rhythm_analysis=asdict(rhythm),
        notes=notes_dict,
        drum_elements=drum_elements,
        drum_pattern_type=drum_pattern_type,
    )


# =============================================================================
# BATCH PROCESSING
# =============================================================================

def analyze_from_inventory(inventory_path: str) -> List[MidiAnalysis]:
    """Load MIDI paths from inventory JSON and analyze all."""
    with open(inventory_path, 'r') as f:
        inventory = json.load(f)

    # Collect all MIDI paths from packs
    midi_paths = set()

    for pack in inventory.get('packs', []):
        midi_paths.update(pack.get('midi_files', []))

    print(f"Found {len(midi_paths)} MIDI files in inventory")

    results = []
    for i, path in enumerate(sorted(midi_paths)):
        if (i + 1) % 50 == 0:
            print(f"  Analyzed {i + 1}/{len(midi_paths)}...")

        if os.path.exists(path):
            analysis = analyze_midi(path)
            results.append(analysis)

    return results


def analyze_directory(dir_path: str, recursive: bool = True) -> List[MidiAnalysis]:
    """Analyze all MIDI files in a directory."""
    path = Path(dir_path)

    if recursive:
        midi_files = list(path.rglob('*.mid')) + list(path.rglob('*.midi'))
    else:
        midi_files = list(path.glob('*.mid')) + list(path.glob('*.midi'))

    print(f"Found {len(midi_files)} MIDI files")

    results = []
    for i, midi_path in enumerate(midi_files):
        if (i + 1) % 50 == 0:
            print(f"  Analyzed {i + 1}/{len(midi_files)}...")

        analysis = analyze_midi(str(midi_path))
        results.append(analysis)

    return results


# =============================================================================
# REPORTING
# =============================================================================

def print_summary(results: List[MidiAnalysis]):
    """Print analysis summary."""
    if not results:
        print("No MIDI files analyzed.")
        return

    print(f"\n{'='*60}")
    print("MIDI ANALYSIS SUMMARY")
    print(f"{'='*60}")

    print(f"\nTotal files: {len(results)}")

    # Instrument breakdown
    instrument_counts = Counter(r.instrument_type for r in results)
    print(f"\nInstrument types:")
    for inst, count in instrument_counts.most_common():
        print(f"  {inst}: {count}")

    # Drum patterns
    drum_patterns = [r for r in results if r.is_drum_pattern]
    print(f"\nDrum patterns: {len(drum_patterns)}")

    # Key distribution
    keys = [r.detected_key for r in results if r.detected_key and not r.is_drum_pattern]
    if keys:
        key_counts = Counter(keys)
        print(f"\nTop detected keys:")
        for key, count in key_counts.most_common(5):
            print(f"  {key}: {count}")

    # BPM distribution
    bpms = [r.bpm_from_filename or r.detected_bpm for r in results if r.bpm_from_filename or r.detected_bpm]
    if bpms:
        avg_bpm = sum(bpms) / len(bpms)
        print(f"\nBPM: avg={avg_bpm:.0f}, range={min(bpms)}-{max(bpms)}")

    # Note statistics
    total_notes = sum(r.total_notes for r in results)
    avg_notes = total_notes / len(results)
    print(f"\nNotes: total={total_notes:,}, avg per file={avg_notes:.0f}")


def save_results(results: List[MidiAnalysis], output_path: str):
    """Save analysis results to JSON."""
    data = {
        "analysis_count": len(results),
        "files": [asdict(r) for r in results],
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\nResults saved to: {output_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Analyze MIDI files for dataset generation")

    parser.add_argument('--from-inventory', type=str,
                        help='Load MIDI paths from inventory JSON')
    parser.add_argument('--path', type=str,
                        help='Directory to scan for MIDI files')
    parser.add_argument('--file', type=str,
                        help='Single MIDI file to analyze')
    parser.add_argument('--output', type=str, default='data/midi_analysis.json',
                        help='Output JSON path')
    parser.add_argument('--no-recursive', action='store_true',
                        help='Don\'t recurse into subdirectories')

    args = parser.parse_args()

    results = []

    if args.file:
        # Single file
        print(f"Analyzing: {args.file}")
        analysis = analyze_midi(args.file)
        results = [analysis]

        # Print detailed output for single file
        print(f"\n{'-'*40}")
        print(f"File: {analysis.filename}")
        print(f"Instrument: {analysis.instrument_type}")
        print(f"BPM: {analysis.bpm_from_filename or analysis.detected_bpm or 'unknown'}")
        print(f"Key: {analysis.detected_key} {analysis.detected_scale or ''} (confidence: {analysis.key_confidence})")
        print(f"Duration: {analysis.duration_beats} beats")
        print(f"Notes: {analysis.total_notes}")
        print(f"Is drum pattern: {analysis.is_drum_pattern}")
        if analysis.is_drum_pattern:
            print(f"Drum elements: {', '.join(analysis.drum_elements)}")
        if analysis.chord_progression:
            chord_names = [c["root"] + c["type"] for c in analysis.chord_progression[:8]]
            print(f"Chords: {chord_names}")

    elif args.from_inventory:
        # From inventory JSON
        results = analyze_from_inventory(args.from_inventory)

    elif args.path:
        # Directory scan
        results = analyze_directory(args.path, recursive=not args.no_recursive)

    else:
        # Default: try local inventory
        default_inventory = 'data/sample_pack_inventory.json'
        if os.path.exists(default_inventory):
            print(f"Using default inventory: {default_inventory}")
            results = analyze_from_inventory(default_inventory)
        else:
            print("Usage: python analyze_midi.py --from-inventory data/sample_pack_inventory.json")
            print("   or: python analyze_midi.py --path /path/to/midi/files")
            print("   or: python analyze_midi.py --file song.mid")
            return

    if results:
        print_summary(results)
        save_results(results, args.output)


if __name__ == '__main__':
    main()
