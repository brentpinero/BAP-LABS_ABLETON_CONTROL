#!/usr/bin/env python3
"""
Beat Similarity Scoring for MIDI Pattern Evaluation

Compares generated MIDI patterns against reference patterns to provide
objective ground truth for LLM benchmark evaluation.

Based on analysis of reference patterns:
- boom_bap: pitches 36, 40, 42 with ~10% swing
- trap: pitches 36, 38, 42, 46 - straight OR triplet timing
- house: pitches 36, 38, 42 with four-on-floor kick
- dnb: pitches 36, 38/39, 42, 46 - clap (39) common

Metrics:
- Onset Similarity (40%): How close are note timings to reference?
- Velocity Contour (20%): Do dynamics match the genre feel?
- Pattern Completeness (20%): Are essential elements present?
- Groove Feel (20%): Does timing match genre (swing vs triplet vs straight)?
"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
import math
import mido


@dataclass
class Note:
    """Single MIDI note"""
    pitch: int
    start_time: float  # In beats
    duration: float
    velocity: int

    def normalized_pitch(self) -> int:
        """Map equivalent drums to same value for comparison flexibility"""
        # Map rimshot (40) to snare (38)
        if self.pitch == 40:
            return 38
        # Map clap (39) to snare (38) for DnB compatibility
        if self.pitch == 39:
            return 38
        return self.pitch


@dataclass
class DrumPattern:
    """A drum pattern with notes"""
    name: str
    genre: str
    tempo: float = 120.0
    length_beats: float = 4.0
    notes: List[Note] = field(default_factory=list)

    def get_onsets_by_pitch(self, normalize: bool = True) -> Dict[int, List[float]]:
        """Get onset times grouped by pitch"""
        onsets = {}
        for note in self.notes:
            pitch = note.normalized_pitch() if normalize else note.pitch
            if pitch not in onsets:
                onsets[pitch] = []
            onsets[pitch].append(note.start_time)
        return onsets

    def get_velocity_by_pitch(self, normalize: bool = True) -> Dict[int, List[int]]:
        """Get velocities grouped by pitch"""
        velocities = {}
        for note in self.notes:
            pitch = note.normalized_pitch() if normalize else note.pitch
            if pitch not in velocities:
                velocities[pitch] = []
            velocities[pitch].append(note.velocity)
        return velocities

    def get_unique_pitches(self, normalize: bool = True) -> Set[int]:
        """Get set of unique pitches"""
        if normalize:
            return set(n.normalized_pitch() for n in self.notes)
        return set(n.pitch for n in self.notes)


# GM drum mapping
DRUM_NAMES = {
    36: "kick",
    38: "snare",
    39: "clap",
    40: "rimshot",
    42: "closed_hat",
    46: "open_hat",
    49: "crash",
}

# Genre characteristics from reference pattern analysis
GENRE_CHARACTERISTICS = {
    "boom_bap": {
        "required_pitches": {36, 38},  # kick + snare (38 or 40 accepted)
        "optional_pitches": {42, 46},
        "timing_type": "swing",  # Off-grid swing timing
        "expected_swing": 0.10,  # ~10% notes off grid
        "tempo_range": (85, 100),
    },
    "trap": {
        "required_pitches": {36, 38},
        "optional_pitches": {42, 46},
        "timing_type": "flexible",  # Straight OR triplet
        "valid_intervals": [0.25, 0.333, 0.5, 0.667],  # 16th, triplet 8th, 8th, triplet quarter
        "tempo_range": (130, 170),
        "hat_heavy": True,  # High hihat density
    },
    "house": {
        "required_pitches": {36},  # Four-on-floor kick essential
        "optional_pitches": {38, 39, 42, 46},
        "timing_type": "straight",
        "four_on_floor": True,  # Kick on every beat
        "tempo_range": (120, 130),
    },
    "dnb": {
        "required_pitches": {36, 38},  # 38 includes 39 (clap) via normalization
        "optional_pitches": {42, 46},
        "timing_type": "straight",
        "tempo_range": (160, 180),
    },
}


def load_midi_pattern(filepath: str, genre: str = None) -> Optional[DrumPattern]:
    """Load a MIDI file as DrumPattern."""
    if not os.path.exists(filepath):
        return None

    try:
        mid = mido.MidiFile(filepath)
        ticks_per_beat = mid.ticks_per_beat

        # Get tempo
        tempo_us = 500000
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempo_us = msg.tempo
                    break

        bpm = 60_000_000 / tempo_us

        # Extract notes
        notes = []
        for track in mid.tracks:
            current_time = 0
            active_notes = {}

            for msg in track:
                current_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes[msg.note] = (current_time, msg.velocity)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes:
                        start_tick, velocity = active_notes.pop(msg.note)
                        notes.append(Note(
                            pitch=msg.note,
                            start_time=start_tick / ticks_per_beat,
                            duration=max((current_time - start_tick) / ticks_per_beat, 0.1),
                            velocity=velocity
                        ))

        # Determine length
        if notes:
            max_end = max(n.start_time + n.duration for n in notes)
            length = max(4.0, math.ceil(max_end / 4) * 4)
        else:
            length = 4.0

        # Infer genre from path
        if genre is None:
            for g in GENRE_CHARACTERISTICS.keys():
                if g in filepath.lower():
                    genre = g
                    break
            else:
                genre = "unknown"

        return DrumPattern(
            name=os.path.splitext(os.path.basename(filepath))[0],
            genre=genre,
            tempo=bpm,
            length_beats=length,
            notes=notes
        )

    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def pattern_from_notes(notes: List[Dict], genre: str = "unknown", name: str = "generated") -> DrumPattern:
    """Create DrumPattern from note dicts (from MCP/Ableton)."""
    pattern_notes = [
        Note(
            pitch=n.get("pitch", 60),
            start_time=n.get("start_time", 0.0),
            duration=n.get("duration", 0.5),
            velocity=n.get("velocity", 100)
        )
        for n in notes
    ]

    length = 4.0
    if pattern_notes:
        max_end = max(n.start_time + n.duration for n in pattern_notes)
        length = max(4.0, math.ceil(max_end / 4) * 4)

    return DrumPattern(name=name, genre=genre, length_beats=length, notes=pattern_notes)


def calculate_onset_similarity(generated: DrumPattern, reference: DrumPattern) -> float:
    """
    Calculate onset similarity (normalized to pattern length).
    Returns 0.0-1.0 (higher = more similar)
    """
    if not generated.notes or not reference.notes:
        return 0.0

    gen_onsets = generated.get_onsets_by_pitch(normalize=True)
    ref_onsets = reference.get_onsets_by_pitch(normalize=True)

    gen_length = generated.length_beats or 4.0
    ref_length = reference.length_beats or 4.0

    total_distance = 0.0
    matched_notes = 0

    for pitch, gen_times in gen_onsets.items():
        if pitch not in ref_onsets:
            total_distance += len(gen_times) * 0.5
            matched_notes += len(gen_times)
            continue

        ref_times = ref_onsets[pitch]

        for gen_t in gen_times:
            # Normalize to pattern position (0-1)
            gen_pos = (gen_t % gen_length) / gen_length
            ref_positions = [(rt % ref_length) / ref_length for rt in ref_times]

            # Find nearest (with wrap-around)
            min_dist = min(
                min(abs(gen_pos - rp), 1.0 - abs(gen_pos - rp))
                for rp in ref_positions
            )
            total_distance += min(min_dist, 0.5)
            matched_notes += 1

    if matched_notes == 0:
        return 0.0

    avg_distance = total_distance / matched_notes
    return max(0.0, 1.0 - avg_distance * 2)


def calculate_velocity_similarity(generated: DrumPattern, reference: DrumPattern) -> float:
    """Compare velocity contours."""
    gen_vel = generated.get_velocity_by_pitch(normalize=True)
    ref_vel = reference.get_velocity_by_pitch(normalize=True)

    if not gen_vel:
        return 0.0

    similarities = []
    for pitch in gen_vel:
        if pitch in ref_vel:
            gen_avg = sum(gen_vel[pitch]) / len(gen_vel[pitch])
            ref_avg = sum(ref_vel[pitch]) / len(ref_vel[pitch])
            diff = abs(gen_avg - ref_avg) / 127.0
            similarities.append(1.0 - diff)
        else:
            similarities.append(0.5)

    return sum(similarities) / len(similarities)


def calculate_pattern_completeness(generated: DrumPattern, reference: DrumPattern) -> float:
    """Check if generated has reference elements."""
    gen_pitches = generated.get_unique_pitches(normalize=True)
    ref_pitches = reference.get_unique_pitches(normalize=True)

    if not ref_pitches:
        return 1.0 if not gen_pitches else 0.5

    present = gen_pitches & ref_pitches
    return len(present) / len(ref_pitches)


def calculate_groove_feel(generated: DrumPattern, reference: DrumPattern) -> float:
    """
    Compare timing characteristics (swing vs triplet vs straight).
    """
    def analyze_timing(pattern: DrumPattern) -> Dict:
        """Analyze timing characteristics of a pattern."""
        if not pattern.notes:
            return {"swing": 0.0, "triplet": 0.0, "straight": 0.0}

        # Get hihat timing intervals
        hats = sorted([n.start_time for n in pattern.notes if n.pitch == 42])

        if len(hats) < 2:
            return {"swing": 0.0, "triplet": 0.0, "straight": 1.0}

        intervals = [hats[i+1] - hats[i] for i in range(len(hats)-1)]

        # Count interval types
        straight_count = sum(1 for i in intervals if abs(i - 0.25) < 0.03 or abs(i - 0.5) < 0.03)
        triplet_count = sum(1 for i in intervals if abs(i - 0.333) < 0.03 or abs(i - 0.667) < 0.03)

        # Check for swing (off-grid notes)
        swing_count = 0
        for n in pattern.notes:
            t = n.start_time
            on_grid = (abs(t % 0.25) < 0.03 or abs(t % 0.25) > 0.22 or
                      abs(t % 0.333) < 0.03 or abs(t % 0.333) > 0.30)
            if not on_grid:
                swing_count += 1

        total = len(pattern.notes)
        return {
            "swing": swing_count / total if total else 0.0,
            "triplet": triplet_count / len(intervals) if intervals else 0.0,
            "straight": straight_count / len(intervals) if intervals else 0.0,
        }

    gen_timing = analyze_timing(generated)
    ref_timing = analyze_timing(reference)

    # Compare timing profiles
    diff = (
        abs(gen_timing["swing"] - ref_timing["swing"]) +
        abs(gen_timing["triplet"] - ref_timing["triplet"]) +
        abs(gen_timing["straight"] - ref_timing["straight"])
    ) / 3

    return max(0.0, 1.0 - diff * 2)


def calculate_similarity(generated: DrumPattern, reference: DrumPattern) -> Dict:
    """Calculate overall similarity with component breakdown."""
    onset = calculate_onset_similarity(generated, reference)
    velocity = calculate_velocity_similarity(generated, reference)
    completeness = calculate_pattern_completeness(generated, reference)
    groove = calculate_groove_feel(generated, reference)

    weights = {"onset": 0.40, "velocity": 0.20, "completeness": 0.20, "groove": 0.20}

    total = (
        onset * weights["onset"] +
        velocity * weights["velocity"] +
        completeness * weights["completeness"] +
        groove * weights["groove"]
    )

    return {
        "total_score": round(total, 3),
        "onset_similarity": round(onset, 3),
        "velocity_similarity": round(velocity, 3),
        "pattern_completeness": round(completeness, 3),
        "groove_feel": round(groove, 3),
        "weights": weights,
    }


def load_reference_patterns(genre: str, base_path: str = "reference_patterns") -> List[DrumPattern]:
    """Load all reference patterns for a genre."""
    patterns = []
    genre_path = os.path.join(base_path, genre)

    if not os.path.exists(genre_path):
        return patterns

    for root, dirs, files in os.walk(genre_path):
        for f in files:
            if f.endswith('.mid') or f.endswith('.midi'):
                pattern = load_midi_pattern(os.path.join(root, f), genre=genre)
                if pattern:
                    patterns.append(pattern)

    return patterns


def find_best_match(generated: DrumPattern, references: List[DrumPattern]) -> Dict:
    """Find best matching reference and return scores."""
    if not references:
        return {"error": "No references", "total_score": 0.0}

    best_score = -1.0
    best_match = None
    best_details = None
    all_scores = []

    for ref in references:
        details = calculate_similarity(generated, ref)
        all_scores.append({"reference": ref.name, "score": details["total_score"]})

        if details["total_score"] > best_score:
            best_score = details["total_score"]
            best_match = ref
            best_details = details

    return {
        "best_match": best_match.name if best_match else None,
        "total_score": best_score,
        "details": best_details,
        "reference_count": len(references),
        "top_matches": sorted(all_scores, key=lambda x: -x["score"])[:3],
    }


def evaluate_generated_pattern(notes: List[Dict], genre: str, base_path: str = "reference_patterns") -> Dict:
    """
    Main entry point: evaluate generated pattern against references.

    Args:
        notes: List of note dicts from MCP (pitch, start_time, duration, velocity)
        genre: Target genre (boom_bap, trap, house, dnb)
        base_path: Path to reference patterns

    Returns:
        Evaluation results with scores and details
    """
    generated = pattern_from_notes(notes, genre=genre)
    references = load_reference_patterns(genre, base_path)

    if not references:
        return {"error": f"No references for '{genre}'", "total_score": 0.0}

    result = find_best_match(generated, references)

    # Add generated pattern info
    result["generated"] = {
        "note_count": len(generated.notes),
        "pitches": list(generated.get_unique_pitches()),
        "length_beats": generated.length_beats,
    }

    # Check genre requirements
    if genre in GENRE_CHARACTERISTICS:
        chars = GENRE_CHARACTERISTICS[genre]
        gen_pitches = generated.get_unique_pitches(normalize=True)
        required = chars["required_pitches"]
        result["genre_requirements"] = {
            "has_required": required.issubset(gen_pitches),
            "required": list(required),
            "present": list(gen_pitches & required),
            "missing": list(required - gen_pitches),
        }

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Beat Similarity Scoring")
    parser.add_argument("--genre", default="boom_bap")
    parser.add_argument("--list", action="store_true", help="List reference patterns")
    parser.add_argument("--analyze", help="Analyze a MIDI file")
    args = parser.parse_args()

    if args.list:
        print("Reference patterns by genre:\n")
        for genre in GENRE_CHARACTERISTICS.keys():
            patterns = load_reference_patterns(genre)
            print(f"{genre} ({len(patterns)} patterns):")
            for p in patterns:
                pitches = sorted(p.get_unique_pitches(normalize=False))
                print(f"  - {p.name}: {len(p.notes)} notes, pitches {pitches}")
            print()

    elif args.analyze:
        pattern = load_midi_pattern(args.analyze)
        if pattern:
            print(f"Pattern: {pattern.name}")
            print(f"Notes: {len(pattern.notes)}")
            print(f"Pitches: {sorted(pattern.get_unique_pitches(normalize=False))}")

            refs = load_reference_patterns(args.genre)
            if refs:
                result = find_best_match(pattern, refs)
                print(f"\nBest match: {result['best_match']} (score: {result['total_score']:.3f})")
                print(f"Details: {result['details']}")
    else:
        print(f"Beat Similarity Scoring - {args.genre}")
        refs = load_reference_patterns(args.genre)
        print(f"Loaded {len(refs)} reference patterns for {args.genre}")
