#!/usr/bin/env python3
"""
Structure Detection Pipeline
============================

Detects song structure (intro, verse, chorus, drop, breakdown, etc.)
using librosa's segmentation algorithms.

Key Features:
- Beat and downbeat detection
- Section boundary detection (using Laplacian segmentation)
- Energy envelope analysis for build-up/drop detection
- Label assignment based on energy and spectral features

Usage:
    from structure_detector import StructureDetector

    detector = StructureDetector()
    result = detector.analyze("song.wav")

    # Result contains:
    # - sections: List of (start_time, end_time, label)
    # - beats: Array of beat times
    # - tempo: Estimated BPM
    # - energy_curve: Per-frame energy
"""

import numpy as np
import librosa
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class SectionType(Enum):
    """Common section types in music production."""
    INTRO = "intro"
    VERSE = "verse"
    CHORUS = "chorus"
    PRECHORUS = "prechorus"
    BRIDGE = "bridge"
    DROP = "drop"
    BUILDUP = "buildup"
    BREAKDOWN = "breakdown"
    OUTRO = "outro"
    UNKNOWN = "unknown"


@dataclass
class Section:
    """Represents a detected song section."""
    start_time: float
    end_time: float
    label: SectionType
    energy_level: float  # 0-1 normalized
    spectral_centroid: float  # Hz
    confidence: float  # 0-1

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    def to_dict(self) -> dict:
        return {
            'start_time': round(self.start_time, 3),
            'end_time': round(self.end_time, 3),
            'duration': round(self.duration, 3),
            'label': self.label.value,
            'energy_level': round(self.energy_level, 3),
            'spectral_centroid': round(self.spectral_centroid, 1),
            'confidence': round(self.confidence, 3),
        }


@dataclass
class StructureAnalysis:
    """Complete structure analysis result."""
    sections: List[Section]
    beats: np.ndarray
    downbeats: np.ndarray
    tempo: float
    time_signature: int
    energy_curve: np.ndarray
    total_duration: float

    def to_dict(self) -> dict:
        return {
            'sections': [s.to_dict() for s in self.sections],
            'tempo': round(self.tempo, 1),
            'time_signature': self.time_signature,
            'total_duration': round(self.total_duration, 3),
            'n_sections': len(self.sections),
            'section_labels': [s.label.value for s in self.sections],
        }


class StructureDetector:
    """
    Detects song structure using librosa segmentation.

    Algorithm:
    1. Compute features (chroma, MFCC, onset strength)
    2. Build recurrence matrix
    3. Detect segment boundaries using Laplacian segmentation
    4. Label sections based on energy and spectral features
    """

    def __init__(
        self,
        n_segments: int = 8,  # Target number of sections
        hop_length: int = 512,
        n_mels: int = 128,
        n_mfcc: int = 20,
    ):
        self.n_segments = n_segments
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.n_mfcc = n_mfcc

    def load_audio(self, path: Union[str, Path], sr: int = 22050) -> Tuple[np.ndarray, int]:
        """Load audio file."""
        y, sr = librosa.load(path, sr=sr, mono=True)
        return y, sr

    def detect_beats(self, y: np.ndarray, sr: int) -> Tuple[np.ndarray, float, np.ndarray]:
        """
        Detect beats and estimate tempo.

        Returns:
            beats: Array of beat times
            tempo: Estimated BPM
            downbeats: Array of downbeat times (first beat of each bar)
        """
        # Get onset envelope
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)

        # Estimate tempo and beat positions
        tempo, beat_frames = librosa.beat.beat_track(
            onset_envelope=onset_env,
            sr=sr,
            hop_length=self.hop_length,
        )

        # Convert frames to times
        beats = librosa.frames_to_time(beat_frames, sr=sr, hop_length=self.hop_length)

        # Estimate downbeats (assume 4/4 time, every 4th beat)
        # This is a simplification - real downbeat detection is more complex
        if len(beats) >= 4:
            downbeats = beats[::4]
        else:
            downbeats = beats[:1] if len(beats) > 0 else np.array([])

        # Handle tempo array (librosa 0.11+ returns array)
        if hasattr(tempo, '__len__'):
            tempo = tempo[0] if len(tempo) > 0 else 120.0

        return beats, float(tempo), downbeats

    def compute_features(self, y: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """Compute audio features for segmentation."""
        # Chromagram
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)

        # MFCCs (exclude first coefficient)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc, hop_length=self.hop_length)

        # RMS energy
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]

        # Spectral centroid
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)[0]

        # Spectral contrast
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=self.hop_length)

        return {
            'chroma': chroma,
            'mfcc': mfcc,
            'rms': rms,
            'centroid': centroid,
            'contrast': contrast,
        }

    def detect_boundaries(
        self,
        features: Dict[str, np.ndarray],
        sr: int,
    ) -> np.ndarray:
        """
        Detect section boundaries using Laplacian segmentation.

        This uses the recurrence matrix approach from librosa.
        """
        # Stack features for segmentation (use chroma and MFCC)
        # Normalize each feature
        chroma_norm = librosa.util.normalize(features['chroma'], axis=1)
        mfcc_norm = librosa.util.normalize(features['mfcc'], axis=1)

        # Combine features
        combined = np.vstack([chroma_norm, mfcc_norm])

        # Build recurrence matrix
        R = librosa.segment.recurrence_matrix(
            combined,
            width=3,
            mode='affinity',
            sym=True,
        )

        # Detect boundaries using checkerboard kernel
        bound_frames = librosa.segment.agglomerative(
            combined,
            self.n_segments,
        )

        # Add start and end
        bound_frames = np.unique(np.concatenate([[0], bound_frames, [combined.shape[1]]]))

        # Convert to times
        bound_times = librosa.frames_to_time(
            bound_frames,
            sr=sr,
            hop_length=self.hop_length,
        )

        return bound_times

    def label_sections(
        self,
        bound_times: np.ndarray,
        features: Dict[str, np.ndarray],
        sr: int,
        total_duration: float,
    ) -> List[Section]:
        """
        Label sections based on energy and spectral features.

        Labeling heuristics:
        - Low energy at start/end → intro/outro
        - High energy → chorus/drop
        - Rising energy → buildup
        - Falling energy → breakdown
        - Mid energy → verse/bridge
        """
        sections = []
        n_sections = len(bound_times) - 1

        # Get per-segment statistics
        for i in range(n_sections):
            start_time = bound_times[i]
            end_time = bound_times[i + 1]

            # Get frames for this segment
            start_frame = librosa.time_to_frames(start_time, sr=sr, hop_length=self.hop_length)
            end_frame = librosa.time_to_frames(end_time, sr=sr, hop_length=self.hop_length)
            end_frame = min(end_frame, len(features['rms']))

            if start_frame >= end_frame:
                continue

            # Compute segment statistics
            seg_rms = features['rms'][start_frame:end_frame]
            seg_centroid = features['centroid'][start_frame:end_frame]

            energy_level = float(np.mean(seg_rms))
            spectral_centroid = float(np.mean(seg_centroid))

            # Normalize energy to 0-1
            global_max_rms = np.max(features['rms'])
            energy_normalized = energy_level / (global_max_rms + 1e-10)

            # Check energy trend (rising/falling)
            if len(seg_rms) > 4:
                first_quarter = np.mean(seg_rms[:len(seg_rms)//4])
                last_quarter = np.mean(seg_rms[-len(seg_rms)//4:])
                energy_trend = last_quarter - first_quarter
            else:
                energy_trend = 0

            # Label assignment
            label = self._assign_label(
                i, n_sections, energy_normalized, energy_trend,
                spectral_centroid, start_time, total_duration
            )

            # Confidence based on how clear the section characteristics are
            confidence = self._compute_confidence(
                energy_normalized, energy_trend, label
            )

            sections.append(Section(
                start_time=start_time,
                end_time=end_time,
                label=label,
                energy_level=energy_normalized,
                spectral_centroid=spectral_centroid,
                confidence=confidence,
            ))

        return sections

    def _assign_label(
        self,
        section_idx: int,
        n_sections: int,
        energy: float,
        energy_trend: float,
        centroid: float,
        start_time: float,
        total_duration: float,
    ) -> SectionType:
        """Assign section label based on heuristics."""
        position_ratio = start_time / total_duration

        # First section is likely intro
        if section_idx == 0 and energy < 0.5:
            return SectionType.INTRO

        # Last section is likely outro
        if section_idx == n_sections - 1 and energy < 0.6:
            return SectionType.OUTRO

        # Rising energy = buildup
        if energy_trend > 0.1:
            return SectionType.BUILDUP

        # High energy section = drop/chorus
        if energy > 0.7:
            # Electronic music tends to have "drops", other genres "chorus"
            if centroid > 3000:  # Brighter = more likely electronic drop
                return SectionType.DROP
            else:
                return SectionType.CHORUS

        # Sudden energy decrease = breakdown
        if energy_trend < -0.1 and energy < 0.5:
            return SectionType.BREAKDOWN

        # Medium energy in first half = verse
        if position_ratio < 0.5 and energy < 0.6:
            return SectionType.VERSE

        # Medium energy in second half = bridge
        if position_ratio >= 0.5 and energy < 0.6:
            return SectionType.BRIDGE

        return SectionType.UNKNOWN

    def _compute_confidence(
        self,
        energy: float,
        energy_trend: float,
        label: SectionType,
    ) -> float:
        """Compute confidence score for the label assignment."""
        # Higher confidence for extreme values (clearly low or high energy)
        if label in [SectionType.DROP, SectionType.CHORUS]:
            return min(1.0, energy * 1.2)
        elif label in [SectionType.INTRO, SectionType.OUTRO]:
            return min(1.0, (1 - energy) * 1.2)
        elif label == SectionType.BUILDUP:
            return min(1.0, abs(energy_trend) * 5)
        elif label == SectionType.BREAKDOWN:
            return min(1.0, abs(energy_trend) * 5)
        else:
            return 0.5  # Default medium confidence

    def analyze(
        self,
        audio_path: Union[str, Path, None] = None,
        y: np.ndarray = None,
        sr: int = 22050,
    ) -> StructureAnalysis:
        """
        Analyze song structure.

        Args:
            audio_path: Path to audio file
            y: Audio array (alternative to audio_path)
            sr: Sample rate

        Returns:
            StructureAnalysis with sections, beats, tempo, etc.
        """
        # Load audio if path provided
        if audio_path is not None:
            y, sr = self.load_audio(audio_path, sr)
        elif y is None:
            raise ValueError("Must provide either audio_path or y")

        total_duration = len(y) / sr

        # Detect beats and tempo
        beats, tempo, downbeats = self.detect_beats(y, sr)

        # Compute features
        features = self.compute_features(y, sr)

        # Detect boundaries
        bound_times = self.detect_boundaries(features, sr)

        # Label sections
        sections = self.label_sections(bound_times, features, sr, total_duration)

        # Estimate time signature (simple: 4/4 assumed)
        time_signature = 4

        return StructureAnalysis(
            sections=sections,
            beats=beats,
            downbeats=downbeats,
            tempo=tempo,
            time_signature=time_signature,
            energy_curve=features['rms'],
            total_duration=total_duration,
        )

    def visualize(
        self,
        analysis: StructureAnalysis,
        save_path: Optional[str] = None,
    ):
        """Visualize structure analysis."""
        try:
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(2, 1, figsize=(14, 6), sharex=True)

            # Plot energy curve
            ax1 = axes[0]
            times = np.linspace(0, analysis.total_duration, len(analysis.energy_curve))
            ax1.plot(times, analysis.energy_curve, color='blue', alpha=0.7)
            ax1.set_ylabel('Energy (RMS)')
            ax1.set_title(f'Song Structure Analysis (Tempo: {analysis.tempo:.1f} BPM)')

            # Add section boundaries
            for section in analysis.sections:
                ax1.axvline(section.start_time, color='red', linestyle='--', alpha=0.5)

            # Plot section labels
            ax2 = axes[1]
            colors = {
                SectionType.INTRO: '#90EE90',
                SectionType.VERSE: '#87CEEB',
                SectionType.PRECHORUS: '#DDA0DD',
                SectionType.CHORUS: '#FFD700',
                SectionType.DROP: '#FF6347',
                SectionType.BUILDUP: '#FFA500',
                SectionType.BREAKDOWN: '#E0E0E0',
                SectionType.BRIDGE: '#98FB98',
                SectionType.OUTRO: '#D3D3D3',
                SectionType.UNKNOWN: '#FFFFFF',
            }

            for section in analysis.sections:
                color = colors.get(section.label, '#FFFFFF')
                ax2.axvspan(section.start_time, section.end_time, alpha=0.5, color=color)
                ax2.text(
                    (section.start_time + section.end_time) / 2,
                    0.5,
                    section.label.value,
                    ha='center', va='center',
                    fontsize=9, fontweight='bold',
                )

            ax2.set_xlim(0, analysis.total_duration)
            ax2.set_ylim(0, 1)
            ax2.set_xlabel('Time (seconds)')
            ax2.set_ylabel('Sections')

            plt.tight_layout()

            if save_path:
                plt.savefig(save_path)
                print(f"Saved: {save_path}")
            else:
                plt.show()

            plt.close()

        except ImportError:
            print("matplotlib not available for visualization")


# =============================================================================
# TESTING
# =============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Detect song structure")
    parser.add_argument('audio_path', nargs='?', default=None,
                        help='Path to audio file')
    parser.add_argument('--synthetic', action='store_true',
                        help='Use synthetic test audio')
    parser.add_argument('--n-segments', type=int, default=8,
                        help='Target number of segments')
    parser.add_argument('--visualize', action='store_true',
                        help='Show visualization')

    args = parser.parse_args()

    print("=" * 60)
    print("STRUCTURE DETECTOR - Testing")
    print("=" * 60)

    detector = StructureDetector(n_segments=args.n_segments)

    if args.synthetic or args.audio_path is None:
        print("\nGenerating synthetic test audio...")
        sr = 22050
        duration = 60.0  # 1 minute

        t = np.linspace(0, duration, int(sr * duration))

        # Create synthetic song with structure:
        # Intro (0-8s): Low energy
        # Verse (8-20s): Medium energy
        # Buildup (20-28s): Rising energy
        # Drop (28-44s): High energy
        # Breakdown (44-52s): Low energy
        # Outro (52-60s): Fading

        y = np.zeros_like(t)

        # Add energy envelope
        envelope = np.ones_like(t)
        envelope[:int(8*sr)] = np.linspace(0.2, 0.4, int(8*sr))  # Intro
        envelope[int(8*sr):int(20*sr)] = 0.5  # Verse
        envelope[int(20*sr):int(28*sr)] = np.linspace(0.5, 1.0, int(8*sr))  # Buildup
        envelope[int(28*sr):int(44*sr)] = 1.0  # Drop
        envelope[int(44*sr):int(52*sr)] = np.linspace(1.0, 0.3, int(8*sr))  # Breakdown
        envelope[int(52*sr):] = np.linspace(0.3, 0.1, len(envelope[int(52*sr):]))  # Outro

        # Base frequency (varies by section)
        freq_base = 120
        y += envelope * np.sin(2 * np.pi * freq_base * t)

        # Add harmonics for higher energy sections
        y += (envelope > 0.6).astype(float) * 0.3 * np.sin(2 * np.pi * freq_base * 2 * t)
        y += (envelope > 0.8).astype(float) * 0.2 * np.sin(2 * np.pi * freq_base * 4 * t)

        # Add some noise for texture
        y += envelope * 0.1 * np.random.randn(len(t))

        # Normalize
        y = y / np.max(np.abs(y)) * 0.8

        print(f"Generated {duration}s synthetic audio with expected structure:")
        print("  0-8s: Intro (low energy)")
        print("  8-20s: Verse (medium energy)")
        print("  20-28s: Buildup (rising energy)")
        print("  28-44s: Drop (high energy)")
        print("  44-52s: Breakdown (falling energy)")
        print("  52-60s: Outro (fading)")

    else:
        print(f"\nLoading: {args.audio_path}")
        y, sr = detector.load_audio(args.audio_path)
        duration = len(y) / sr
        print(f"Duration: {duration:.1f}s, Sample rate: {sr}Hz")

    # Analyze
    print("\nAnalyzing structure...")
    analysis = detector.analyze(y=y, sr=sr)

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(f"\nTempo: {analysis.tempo:.1f} BPM")
    print(f"Time Signature: {analysis.time_signature}/4")
    print(f"Total Duration: {analysis.total_duration:.1f}s")
    print(f"Detected Beats: {len(analysis.beats)}")
    print(f"Detected Sections: {len(analysis.sections)}")

    print("\n--- Sections ---")
    for i, section in enumerate(analysis.sections):
        print(f"  [{i+1}] {section.start_time:6.1f}s - {section.end_time:6.1f}s: "
              f"{section.label.value:12s} (energy: {section.energy_level:.2f}, "
              f"conf: {section.confidence:.2f})")

    # Visualize if requested
    if args.visualize:
        detector.visualize(analysis, save_path="test_renders/structure_analysis.png")

    print("\n" + "=" * 60)
    print("Structure detection test complete!")
    print("=" * 60)
