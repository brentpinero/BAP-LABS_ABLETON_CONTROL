#!/usr/bin/env python3
"""
MixGraph-CLAP Encoder - Phase 1 Implementation
================================================
Multi-track mix representation using CLAP embeddings + computed relationship features.

Architecture (Decision 17):
- Stage 1: Per-track CLAP embeddings (frozen encoder)
- Stage 2: Computed relationship features (masking, stereo, RMS)
- Stage 3: Context embedding (mix-wide average)
- Stage 4: Projection to LLM space

Usage:
    from mix_encoder import MixEncoder

    encoder = MixEncoder()
    result = encoder.encode_mix([track1_audio, track2_audio, ...])

    # Result contains:
    # - track_embeddings: [N, 512] per-track contextualized embeddings
    # - mix_embedding: [512] mix-wide embedding
    # - computed_features: dict of relationship matrices
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import librosa
from typing import List, Dict, Optional, Union, Tuple
from pathlib import Path

# HuggingFace CLAP
try:
    from transformers import ClapModel, ClapProcessor
    CLAP_AVAILABLE = True
except ImportError:
    CLAP_AVAILABLE = False
    print("Warning: transformers not installed. Run: pip install transformers")


# =============================================================================
# RELATIONSHIP FEATURE COMPUTATION
# =============================================================================

def compute_mel_spectrogram(
    audio: np.ndarray,
    sr: int = 48000,
    n_mels: int = 128,
    n_fft: int = 2048,
    hop_length: int = 512,
) -> np.ndarray:
    """Compute mel-spectrogram for relationship analysis."""
    # Handle stereo by averaging to mono for spectral analysis
    if audio.ndim == 2:
        audio = audio.mean(axis=0) if audio.shape[0] == 2 else audio.mean(axis=1)

    mel = librosa.feature.melspectrogram(
        y=audio, sr=sr, n_mels=n_mels, n_fft=n_fft, hop_length=hop_length
    )
    mel_db = librosa.power_to_db(mel, ref=np.max)
    return mel_db


def compute_spectral_overlap(tracks: List[np.ndarray], sr: int = 48000) -> np.ndarray:
    """
    Compute spectral overlap (masking score) between all track pairs.

    Returns: [N, N] matrix where entry [i,j] is overlap score between track i and j.
    Higher values = more frequency masking.
    """
    n_tracks = len(tracks)
    overlap_matrix = np.zeros((n_tracks, n_tracks))

    # Compute mel spectrograms for all tracks
    mels = [compute_mel_spectrogram(t, sr) for t in tracks]

    for i in range(n_tracks):
        for j in range(n_tracks):
            if i == j:
                overlap_matrix[i, j] = 1.0  # Self-overlap is 1
            else:
                # Normalize spectrograms to [0, 1] for comparison
                mel_i = (mels[i] - mels[i].min()) / (mels[i].max() - mels[i].min() + 1e-8)
                mel_j = (mels[j] - mels[j].min()) / (mels[j].max() - mels[j].min() + 1e-8)

                # Truncate to same length
                min_len = min(mel_i.shape[1], mel_j.shape[1])
                mel_i = mel_i[:, :min_len]
                mel_j = mel_j[:, :min_len]

                # Compute cosine similarity across frequency bands, average over time
                # Flatten to [n_mels * time] and compute cosine sim
                flat_i = mel_i.flatten()
                flat_j = mel_j.flatten()

                cos_sim = np.dot(flat_i, flat_j) / (
                    np.linalg.norm(flat_i) * np.linalg.norm(flat_j) + 1e-8
                )
                overlap_matrix[i, j] = cos_sim

    return overlap_matrix


def compute_stereo_correlation(tracks: List[np.ndarray]) -> np.ndarray:
    """
    Compute stereo correlation for each track.

    Returns: [N] array where entry [i] is correlation between L/R channels.
    - 1.0 = mono (L == R)
    - 0.0 = completely uncorrelated (wide stereo)
    - -1.0 = out of phase
    """
    correlations = []

    for track in tracks:
        if track.ndim == 1:
            # Mono track
            correlations.append(1.0)
        elif track.shape[0] == 2:
            # Stereo: [2, samples]
            left, right = track[0], track[1]
            corr = np.corrcoef(left, right)[0, 1]
            correlations.append(corr if not np.isnan(corr) else 1.0)
        elif track.shape[1] == 2:
            # Stereo: [samples, 2]
            left, right = track[:, 0], track[:, 1]
            corr = np.corrcoef(left, right)[0, 1]
            correlations.append(corr if not np.isnan(corr) else 1.0)
        else:
            correlations.append(1.0)

    return np.array(correlations)


def compute_rms_levels(tracks: List[np.ndarray]) -> np.ndarray:
    """
    Compute RMS level in dB for each track.

    Returns: [N] array of RMS levels in dB.
    """
    rms_levels = []

    for track in tracks:
        # Handle stereo by averaging
        if track.ndim == 2:
            track = track.mean(axis=0) if track.shape[0] == 2 else track.mean(axis=1)

        rms = np.sqrt(np.mean(track ** 2) + 1e-10)
        rms_db = 20 * np.log10(rms + 1e-10)
        rms_levels.append(rms_db)

    return np.array(rms_levels)


def compute_rms_ratio_matrix(tracks: List[np.ndarray]) -> np.ndarray:
    """
    Compute pairwise RMS ratio matrix.

    Returns: [N, N] matrix where entry [i,j] is dB difference (track_i - track_j).
    """
    rms_levels = compute_rms_levels(tracks)
    n_tracks = len(tracks)

    ratio_matrix = np.zeros((n_tracks, n_tracks))
    for i in range(n_tracks):
        for j in range(n_tracks):
            ratio_matrix[i, j] = rms_levels[i] - rms_levels[j]

    return ratio_matrix


def compute_spectral_centroid(tracks: List[np.ndarray], sr: int = 48000) -> np.ndarray:
    """
    Compute spectral centroid (brightness) for each track.

    Returns: [N] array of centroid frequencies in Hz.
    """
    centroids = []

    for track in tracks:
        # Handle stereo
        if track.ndim == 2:
            track = track.mean(axis=0) if track.shape[0] == 2 else track.mean(axis=1)

        centroid = librosa.feature.spectral_centroid(y=track, sr=sr)
        centroids.append(float(np.mean(centroid)))

    return np.array(centroids)


# =============================================================================
# PHASE 1 MIX ENCODER
# =============================================================================

class MixEncoder(nn.Module):
    """
    Phase 1 MixGraph-CLAP Encoder.

    Architecture:
    1. Frozen CLAP encoder for per-track embeddings
    2. Computed relationship features (masking, stereo, RMS)
    3. Context embedding (average of all tracks)
    4. Projection layer combining track + context + features
    """

    def __init__(
        self,
        clap_model_name: str = "laion/clap-htsat-unfused",
        embedding_dim: int = 512,
        n_relationship_features: int = 5,  # masking, stereo_corr, rms, centroid, rms_relative
        device: str = None,
    ):
        super().__init__()

        # Auto-detect device
        if device is None:
            if torch.backends.mps.is_available():
                self.device = torch.device("mps")
            elif torch.cuda.is_available():
                self.device = torch.device("cuda")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)

        print(f"MixEncoder using device: {self.device}")

        # Load CLAP model (frozen)
        if CLAP_AVAILABLE:
            print(f"Loading CLAP model: {clap_model_name}")
            self.clap_model = ClapModel.from_pretrained(clap_model_name)
            self.clap_processor = ClapProcessor.from_pretrained(clap_model_name)
            self.clap_model.eval()
            self.clap_model.to(self.device)

            # Freeze CLAP parameters
            for param in self.clap_model.parameters():
                param.requires_grad = False

            # CLAP embedding dimension (typically 512)
            self.clap_dim = self.clap_model.config.projection_dim
            print(f"CLAP embedding dimension: {self.clap_dim}")
        else:
            print("CLAP not available - using random embeddings for testing")
            self.clap_model = None
            self.clap_processor = None
            self.clap_dim = 512

        self.embedding_dim = embedding_dim
        self.n_relationship_features = n_relationship_features

        # Projection layer: [track_emb || context_emb || features] -> embedding_dim
        # Input: clap_dim * 2 (track + context) + n_relationship_features
        projection_input_dim = self.clap_dim * 2 + n_relationship_features

        self.projector = nn.Sequential(
            nn.Linear(projection_input_dim, embedding_dim),
            nn.GELU(),
            nn.LayerNorm(embedding_dim),
            nn.Linear(embedding_dim, embedding_dim),
        ).to(self.device)

        print(f"Projector: {projection_input_dim} -> {embedding_dim}")

    def get_clap_embedding(self, audio: np.ndarray, sr: int = 48000) -> torch.Tensor:
        """Get CLAP embedding for a single audio track."""
        if self.clap_model is None:
            # Return random embedding for testing
            return torch.randn(self.clap_dim, device=self.device)

        # Handle stereo by averaging to mono (CLAP expects mono)
        if audio.ndim == 2:
            audio = audio.mean(axis=0) if audio.shape[0] == 2 else audio.mean(axis=1)

        # CLAP expects 48kHz audio
        if sr != 48000:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=48000)

        # Process audio through CLAP
        inputs = self.clap_processor(
            audio=audio,  # Updated from deprecated 'audios' parameter
            return_tensors="pt",
            sampling_rate=48000,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            audio_embed = self.clap_model.get_audio_features(**inputs)

        return audio_embed.squeeze(0)  # [clap_dim]

    def compute_relationship_features(
        self,
        tracks: List[np.ndarray],
        sr: int = 48000,
    ) -> Dict[str, np.ndarray]:
        """Compute all relationship features for a set of tracks."""
        features = {
            'spectral_overlap': compute_spectral_overlap(tracks, sr),
            'stereo_correlation': compute_stereo_correlation(tracks),
            'rms_levels': compute_rms_levels(tracks),
            'rms_ratios': compute_rms_ratio_matrix(tracks),
            'spectral_centroids': compute_spectral_centroid(tracks, sr),
        }
        return features

    def encode_mix(
        self,
        tracks: List[np.ndarray],
        sr: int = 48000,
        track_names: Optional[List[str]] = None,
    ) -> Dict[str, Union[torch.Tensor, Dict]]:
        """
        Encode a multi-track mix into embeddings.

        Args:
            tracks: List of audio arrays (each can be mono or stereo)
            sr: Sample rate of audio
            track_names: Optional names for each track

        Returns:
            Dictionary containing:
            - track_embeddings: [N, embedding_dim] contextualized per-track embeddings
            - mix_embedding: [embedding_dim] mix-wide embedding
            - clap_embeddings: [N, clap_dim] raw CLAP embeddings
            - computed_features: Dict of relationship matrices
            - track_names: List of track names
        """
        n_tracks = len(tracks)

        if track_names is None:
            track_names = [f"track_{i}" for i in range(n_tracks)]

        # Stage 1: Get CLAP embeddings for each track
        print(f"Encoding {n_tracks} tracks with CLAP...")
        clap_embeddings = []
        for i, track in enumerate(tracks):
            emb = self.get_clap_embedding(track, sr)
            clap_embeddings.append(emb)
        clap_embeddings = torch.stack(clap_embeddings)  # [N, clap_dim]

        # Stage 2: Compute relationship features
        print("Computing relationship features...")
        computed_features = self.compute_relationship_features(tracks, sr)

        # Stage 3: Create context embedding (average of all track embeddings)
        context_embedding = clap_embeddings.mean(dim=0)  # [clap_dim]

        # Stage 4: Project each track embedding with context and features
        print("Projecting to final embeddings...")
        projected_embeddings = []

        for i in range(n_tracks):
            track_emb = clap_embeddings[i]  # [clap_dim]

            # Gather per-track features
            # Average masking with all other tracks
            masking_score = computed_features['spectral_overlap'][i].mean()
            stereo_corr = computed_features['stereo_correlation'][i]
            rms_level = computed_features['rms_levels'][i]
            centroid = computed_features['spectral_centroids'][i]
            # RMS relative to mix average
            rms_relative = rms_level - computed_features['rms_levels'].mean()

            # Normalize features to reasonable ranges
            features_tensor = torch.tensor([
                masking_score,  # [0, 1]
                stereo_corr,  # [-1, 1]
                rms_level / 60 + 1,  # Normalize dB roughly to [0, 1]
                centroid / 10000,  # Normalize Hz to ~[0, 1]
                rms_relative / 20,  # Normalize dB diff to ~[-1, 1]
            ], dtype=torch.float32, device=self.device)

            # Concatenate: [track_emb || context_emb || features]
            combined = torch.cat([track_emb, context_embedding, features_tensor])

            # Project
            projected = self.projector(combined)
            projected_embeddings.append(projected)

        projected_embeddings = torch.stack(projected_embeddings)  # [N, embedding_dim]

        # Final mix embedding (average of projected embeddings)
        mix_embedding = projected_embeddings.mean(dim=0)  # [embedding_dim]

        return {
            'track_embeddings': projected_embeddings,
            'mix_embedding': mix_embedding,
            'clap_embeddings': clap_embeddings,
            'context_embedding': context_embedding,
            'computed_features': computed_features,
            'track_names': track_names,
        }

    def encode_single_track(
        self,
        audio: np.ndarray,
        sr: int = 48000,
        mix_context: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Encode a single track, optionally with mix context.

        Useful for real-time scenarios where tracks are added incrementally.
        """
        # Get CLAP embedding
        clap_emb = self.get_clap_embedding(audio, sr)

        # If no mix context, use self as context
        if mix_context is None:
            context = clap_emb
        else:
            context = mix_context

        # Compute basic features for single track
        stereo_corr = compute_stereo_correlation([audio])[0]
        rms_level = compute_rms_levels([audio])[0]
        centroid = compute_spectral_centroid([audio], sr)[0]

        features = torch.tensor([
            1.0,  # Self-masking placeholder
            stereo_corr,
            rms_level / 60 + 1,
            centroid / 10000,
            0.0,  # No relative RMS without mix context
        ], dtype=torch.float32, device=self.device)

        combined = torch.cat([clap_emb, context, features])
        return self.projector(combined)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def load_audio(path: Union[str, Path], sr: int = 48000) -> Tuple[np.ndarray, int]:
    """Load audio file and return (audio, sample_rate)."""
    audio, loaded_sr = librosa.load(path, sr=sr, mono=False)
    return audio, loaded_sr


def visualize_relationship_matrix(
    matrix: np.ndarray,
    track_names: List[str],
    title: str = "Track Relationships",
    save_path: Optional[str] = None,
):
    """Visualize a relationship matrix as a heatmap."""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.figure(figsize=(10, 8))
        sns.heatmap(
            matrix,
            xticklabels=track_names,
            yticklabels=track_names,
            annot=True,
            fmt='.2f',
            cmap='RdYlBu_r',
            center=0,
        )
        plt.title(title)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"Saved: {save_path}")
        else:
            plt.show()

        plt.close()
    except ImportError:
        print("matplotlib/seaborn not available for visualization")


# =============================================================================
# QUICK TEST
# =============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Test MixGraph-CLAP Encoder")
    parser.add_argument('--audio-dir', type=str, default='data/renders',
                        help='Directory containing audio files to encode')
    parser.add_argument('--max-tracks', type=int, default=4,
                        help='Maximum number of tracks to encode')
    parser.add_argument('--test-synthetic', action='store_true',
                        help='Use synthetic audio for testing (no files needed)')

    args = parser.parse_args()

    print("=" * 60)
    print("MIXGRAPH-CLAP ENCODER - Phase 1 Test")
    print("=" * 60)

    # Create encoder
    encoder = MixEncoder()

    if args.test_synthetic:
        print("\nGenerating synthetic test audio...")
        sr = 48000
        duration = 2.0

        # Synthetic tracks with different characteristics
        t = np.linspace(0, duration, int(sr * duration))

        # Track 1: Low bass (mono, 60Hz)
        bass = np.sin(2 * np.pi * 60 * t) * 0.8

        # Track 2: Mid synth (stereo, 440Hz + harmonics)
        synth_l = np.sin(2 * np.pi * 440 * t) * 0.3 + np.sin(2 * np.pi * 880 * t) * 0.15
        synth_r = np.sin(2 * np.pi * 440 * t) * 0.3 + np.sin(2 * np.pi * 880 * t) * 0.15
        synth_r = np.roll(synth_r, 100)  # Phase offset for stereo width
        synth = np.stack([synth_l, synth_r])

        # Track 3: High hat (mono, white noise filtered)
        hihat = np.random.randn(len(t)) * 0.2

        # Track 4: Another bass-y element (potential masking)
        sub = np.sin(2 * np.pi * 55 * t) * 0.6

        tracks = [bass, synth, hihat, sub]
        track_names = ['Bass', 'Synth', 'HiHat', 'Sub']

    else:
        print(f"\nLooking for audio files in: {args.audio_dir}")
        audio_dir = Path(args.audio_dir)

        if not audio_dir.exists():
            print(f"Directory not found: {audio_dir}")
            print("Use --test-synthetic to test with synthetic audio")
            exit(1)

        # Find audio files
        audio_files = list(audio_dir.glob('*.wav'))[:args.max_tracks]

        if len(audio_files) == 0:
            print("No .wav files found. Use --test-synthetic to test with synthetic audio")
            exit(1)

        print(f"Found {len(audio_files)} audio files")

        # Load tracks
        tracks = []
        track_names = []
        sr = 48000

        for f in audio_files:
            audio, _ = load_audio(f, sr)
            tracks.append(audio)
            track_names.append(f.stem[:20])  # Truncate long names

    # Encode the mix
    print(f"\nEncoding {len(tracks)} tracks...")
    result = encoder.encode_mix(tracks, sr=48000, track_names=track_names)

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(f"\nTrack embeddings shape: {result['track_embeddings'].shape}")
    print(f"Mix embedding shape: {result['mix_embedding'].shape}")
    print(f"CLAP embeddings shape: {result['clap_embeddings'].shape}")

    print(f"\n--- Computed Features ---")
    print(f"Stereo correlations: {result['computed_features']['stereo_correlation']}")
    print(f"RMS levels (dB): {result['computed_features']['rms_levels']}")
    print(f"Spectral centroids (Hz): {result['computed_features']['spectral_centroids']}")

    print(f"\n--- Spectral Overlap Matrix ---")
    overlap = result['computed_features']['spectral_overlap']
    for i, name in enumerate(track_names):
        row = [f"{overlap[i,j]:.2f}" for j in range(len(track_names))]
        print(f"  {name:15s}: {row}")

    # Visualize if matplotlib available
    try:
        visualize_relationship_matrix(
            overlap,
            track_names,
            title="Spectral Overlap (Masking)",
            save_path="test_renders/spectral_overlap.png" if Path("test_renders").exists() else None,
        )
    except Exception as e:
        print(f"Visualization skipped: {e}")

    print("\n" + "=" * 60)
    print("Phase 1 MixEncoder test complete!")
    print("=" * 60)
