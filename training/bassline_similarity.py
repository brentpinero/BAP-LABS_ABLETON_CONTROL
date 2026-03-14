#!/usr/bin/env python3
"""
Bassline Similarity Scoring for LLM Benchmark

Evaluates generated basslines against reference patterns for:
- DnB: Melodic, sparse, low-register patterns
- Wook/Trap: Dense, mid-range, rhythmic wobble patterns

Key metrics:
1. Note density (notes per beat)
2. Pitch range appropriateness
3. Scale conformity
4. Rhythmic characteristics
"""

import os
import mido
from dataclasses import dataclass
from typing import List, Dict, Optional

# Genre-specific characteristics derived from reference analysis
GENRE_CHARACTERISTICS = {
    "dnb": {
        "notes_per_beat_range": (0.15, 0.5),  # Sparse, melodic
        "pitch_range": (36, 60),               # Low/sub bass register
        "avg_interval_range": (2.0, 8.0),      # Long intervals
        "min_pitch_classes": 3,                # Melodic variety
        "tempo_range": (165, 180),
    },
    "wook": {
        "notes_per_beat_range": (1.0, 5.0),    # Dense, busy
        "pitch_range": (48, 72),                # Mid-range
        "avg_interval_range": (0.1, 1.0),       # Rapid-fire
        "min_pitch_classes": 1,                 # Can be monotonous
        "tempo_range": (130, 160),
    },
}

# Common scales for evaluation (pitch classes 0-11)
SCALES = {
    "C_minor": [0, 2, 3, 5, 7, 8, 10],      # C D Eb F G Ab Bb
    "C_major": [0, 2, 4, 5, 7, 9, 11],      # C D E F G A B
    "F_minor": [5, 7, 8, 10, 0, 1, 3],      # F G Ab Bb C Db Eb
    "chromatic": list(range(12)),           # All notes (fallback)
}


@dataclass
class BassPattern:
    """Represents a bassline pattern"""
    notes: List[Dict]  # List of {pitch, start_time, duration, velocity}

    @property
    def note_count(self) -> int:
        return len(self.notes)

    @property
    def pitches(self) -> List[int]:
        return [n["pitch"] for n in self.notes]

    @property
    def pitch_classes(self) -> set:
        return set(p % 12 for p in self.pitches)

    @property
    def pitch_range(self) -> tuple:
        if not self.pitches:
            return (0, 0)
        return (min(self.pitches), max(self.pitches))

    @property
    def duration_beats(self) -> float:
        if not self.notes:
            return 0
        return max(n["start_time"] for n in self.notes)

    @property
    def notes_per_beat(self) -> float:
        if self.duration_beats <= 0:
            return 0
        return self.note_count / self.duration_beats

    @property
    def avg_interval(self) -> float:
        if len(self.notes) < 2:
            return 0
        times = sorted(n["start_time"] for n in self.notes)
        intervals = [times[i+1] - times[i] for i in range(len(times)-1)]
        return sum(intervals) / len(intervals) if intervals else 0


def load_reference_patterns(genre: str) -> List[BassPattern]:
    """Load reference bassline patterns for a genre"""
    patterns = []

    if genre == "dnb":
        bass_dir = "reference_patterns/dnb/Bass_MIDI"
    elif genre == "wook":
        bass_dir = "reference_patterns/trap/Bass_MIDI_Wook"
    else:
        return patterns

    if not os.path.exists(bass_dir):
        return patterns

    for filename in os.listdir(bass_dir):
        if not filename.endswith('.mid'):
            continue

        filepath = os.path.join(bass_dir, filename)
        try:
            mid = mido.MidiFile(filepath)
            tpb = mid.ticks_per_beat
            notes = []

            for track in mid.tracks:
                current_time = 0
                for msg in track:
                    current_time += msg.time
                    if msg.type == 'note_on' and msg.velocity > 0:
                        notes.append({
                            "pitch": msg.note,
                            "start_time": current_time / tpb,
                            "duration": 0.25,  # Default, would need note_off tracking
                            "velocity": msg.velocity
                        })

            if notes:
                patterns.append(BassPattern(notes=notes))
        except Exception:
            continue

    return patterns


def calculate_density_score(generated: BassPattern, genre: str) -> float:
    """Score based on notes-per-beat matching genre expectations"""
    chars = GENRE_CHARACTERISTICS.get(genre, GENRE_CHARACTERISTICS["dnb"])
    min_npb, max_npb = chars["notes_per_beat_range"]

    npb = generated.notes_per_beat

    if min_npb <= npb <= max_npb:
        return 1.0
    elif npb < min_npb:
        # Too sparse
        return max(0, npb / min_npb)
    else:
        # Too dense
        return max(0, max_npb / npb)


def calculate_pitch_range_score(generated: BassPattern, genre: str) -> float:
    """Score based on pitch range matching genre expectations"""
    chars = GENRE_CHARACTERISTICS.get(genre, GENRE_CHARACTERISTICS["dnb"])
    expected_low, expected_high = chars["pitch_range"]

    if not generated.pitches:
        return 0.0

    actual_low, actual_high = generated.pitch_range

    # Check if range overlaps with expected
    overlap_low = max(actual_low, expected_low)
    overlap_high = min(actual_high, expected_high)

    if overlap_low > overlap_high:
        # No overlap - penalize based on distance
        distance = min(abs(actual_low - expected_high), abs(actual_high - expected_low))
        return max(0, 1.0 - distance / 24)  # 2 octaves tolerance

    # Calculate overlap ratio
    actual_span = actual_high - actual_low + 1
    overlap_span = overlap_high - overlap_low + 1

    return overlap_span / actual_span if actual_span > 0 else 0


def calculate_scale_conformity(generated: BassPattern, key: str = "C_minor") -> float:
    """Score based on how many notes fit the expected scale"""
    if not generated.pitch_classes:
        return 0.0

    scale = set(SCALES.get(key, SCALES["chromatic"]))
    matching = generated.pitch_classes & scale

    return len(matching) / len(generated.pitch_classes)


def calculate_rhythmic_score(generated: BassPattern, genre: str) -> float:
    """Score based on rhythmic characteristics matching genre"""
    chars = GENRE_CHARACTERISTICS.get(genre, GENRE_CHARACTERISTICS["dnb"])
    min_int, max_int = chars["avg_interval_range"]

    avg_int = generated.avg_interval

    if avg_int == 0:
        return 0.0

    if min_int <= avg_int <= max_int:
        return 1.0
    elif avg_int < min_int:
        return max(0, avg_int / min_int)
    else:
        return max(0, max_int / avg_int)


def calculate_melodic_variety(generated: BassPattern, genre: str) -> float:
    """Score based on pitch class variety"""
    chars = GENRE_CHARACTERISTICS.get(genre, GENRE_CHARACTERISTICS["dnb"])
    min_classes = chars["min_pitch_classes"]

    actual_classes = len(generated.pitch_classes)

    if actual_classes >= min_classes:
        # For wook, less variety is fine; for dnb, more is better
        if genre == "wook":
            return 1.0
        else:
            return min(1.0, actual_classes / 6)  # Up to 6 classes is ideal for melodic
    else:
        return actual_classes / min_classes


def evaluate_generated_bassline(notes: List[Dict], genre: str, key: str = "C_minor") -> Dict:
    """
    Main entry point: evaluate a generated bassline against genre expectations.

    Args:
        notes: List of note dicts with pitch, start_time, duration, velocity
        genre: "dnb" or "wook"
        key: Key signature (default C_minor)

    Returns:
        Dict with scores and details
    """
    if not notes:
        return {
            "total_score": 0.0,
            "error": "No notes provided",
            "details": {}
        }

    generated = BassPattern(notes=notes)

    # Calculate individual scores
    density_score = calculate_density_score(generated, genre)
    pitch_range_score = calculate_pitch_range_score(generated, genre)
    scale_score = calculate_scale_conformity(generated, key)
    rhythmic_score = calculate_rhythmic_score(generated, genre)
    variety_score = calculate_melodic_variety(generated, genre)

    # Weighted average (adjust weights based on importance)
    weights = {
        "density": 0.25,
        "pitch_range": 0.20,
        "scale": 0.20,
        "rhythm": 0.20,
        "variety": 0.15,
    }

    total_score = (
        density_score * weights["density"] +
        pitch_range_score * weights["pitch_range"] +
        scale_score * weights["scale"] +
        rhythmic_score * weights["rhythm"] +
        variety_score * weights["variety"]
    )

    return {
        "total_score": round(total_score, 3),
        "genre": genre,
        "key": key,
        "details": {
            "density_score": round(density_score, 3),
            "pitch_range_score": round(pitch_range_score, 3),
            "scale_conformity_score": round(scale_score, 3),
            "rhythmic_score": round(rhythmic_score, 3),
            "variety_score": round(variety_score, 3),
        },
        "pattern_stats": {
            "note_count": generated.note_count,
            "notes_per_beat": round(generated.notes_per_beat, 3),
            "pitch_range": generated.pitch_range,
            "pitch_classes": list(generated.pitch_classes),
            "avg_interval": round(generated.avg_interval, 3),
        }
    }


if __name__ == "__main__":
    # Test with reference patterns
    for genre in ["dnb", "wook"]:
        print(f"\n{'='*60}")
        print(f"Testing {genre.upper()} reference patterns")
        print("="*60)

        patterns = load_reference_patterns(genre)
        if not patterns:
            print(f"No patterns found for {genre}")
            continue

        scores = []
        for i, pattern in enumerate(patterns[:5]):
            result = evaluate_generated_bassline(pattern.notes, genre)
            scores.append(result["total_score"])
            print(f"\nPattern {i+1}: Score = {result['total_score']:.3f}")
            print(f"  Stats: {result['pattern_stats']['note_count']} notes, "
                  f"{result['pattern_stats']['notes_per_beat']:.2f} npb")

        if scores:
            print(f"\nAverage score: {sum(scores)/len(scores):.3f}")
