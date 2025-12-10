#!/usr/bin/env python3
"""
Multi-Channel Audio Feature Extraction Pipeline for Serum Preset Audio
========================================================================
Extracts 4-channel audio features for CNN training:
  - Channel 0: Mel-spectrogram (frequency content)
  - Channel 1: RMS envelope (amplitude over time) - helps with envelope params
  - Channel 2: Spectral centroid (brightness) - helps with filter/drive
  - Channel 3: Spectral flatness (noise vs tone) - helps with distortion

Usage:
    # Test on a few files
    python mel_spectrogram_pipeline.py --test --max-files 10

    # Run full extraction with parallelization
    python mel_spectrogram_pipeline.py --parallel --workers 8

    # Use multi-channel features (NEW!)
    python mel_spectrogram_pipeline.py --multi-channel --parallel --workers 8

    # Visualize a sample spectrogram
    python mel_spectrogram_pipeline.py --visualize --audio-path path/to/file.wav
"""

import argparse
import json
import multiprocessing as mp
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from functools import partial
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import librosa
import soundfile as sf
from tqdm import tqdm


# =============================================================================
# AUDIO FEATURE CONFIGURATION
# =============================================================================
# These settings are optimized for synthesizer sounds based on audio ML research

MEL_CONFIG = {
    'sr': 44100,          # Sample rate (match our rendered audio)
    'n_mels': 128,        # Number of mel frequency bins (standard for audio ML)
    'n_fft': 2048,        # FFT window size (~46ms at 44.1kHz) - good freq resolution
    'hop_length': 512,    # Step between frames (~11.6ms) - balance time/freq
    'fmin': 20,           # Lowest frequency (human hearing floor)
    'fmax': 16000,        # Highest frequency (most synth content is below this)
    'power': 2.0,         # Power spectrogram (squared magnitude)
    'ref': 1.0,           # Reference for dB conversion
    'top_db': 80.0,       # Dynamic range limit (prevents extreme values)
}

# Multi-channel feature extraction flag (set via --multi-channel)
MULTI_CHANNEL = False


def compute_mel_spectrogram(
    audio: np.ndarray,
    sr: int = MEL_CONFIG['sr'],
    config: Dict = MEL_CONFIG
) -> np.ndarray:
    """
    Compute mel-spectrogram from audio waveform.

    Args:
        audio: Audio waveform (mono, float32/64)
        sr: Sample rate
        config: Mel-spectrogram configuration dict

    Returns:
        mel_spec: Mel-spectrogram in dB scale [n_mels, time_frames]
    """
    mel_spec = librosa.feature.melspectrogram(
        y=audio,
        sr=sr,
        n_mels=config['n_mels'],
        n_fft=config['n_fft'],
        hop_length=config['hop_length'],
        fmin=config['fmin'],
        fmax=config['fmax'],
        power=config['power']
    )

    # Convert to dB scale (log compression - matches human perception)
    mel_spec_db = librosa.power_to_db(
        mel_spec,
        ref=config['ref'],
        top_db=config['top_db']
    )

    return mel_spec_db


def compute_rms_envelope(
    audio: np.ndarray,
    config: Dict = MEL_CONFIG
) -> np.ndarray:
    """
    Compute RMS (root-mean-square) envelope over time.
    This directly captures amplitude contour - critical for envelope params!

    Returns:
        rms: Shape [1, time_frames] - will be broadcast to [n_mels, time_frames]
    """
    rms = librosa.feature.rms(
        y=audio,
        frame_length=config['n_fft'],
        hop_length=config['hop_length']
    )
    # Convert to dB for consistency with mel-spec
    rms_db = librosa.amplitude_to_db(rms, ref=1.0, top_db=config['top_db'])
    return rms_db  # Shape: [1, time_frames]


def compute_spectral_centroid(
    audio: np.ndarray,
    sr: int = MEL_CONFIG['sr'],
    config: Dict = MEL_CONFIG
) -> np.ndarray:
    """
    Compute spectral centroid (brightness) over time.
    This helps with filter cutoff and drive/distortion detection.

    Returns:
        centroid: Shape [1, time_frames] normalized to [0, 1]
    """
    centroid = librosa.feature.spectral_centroid(
        y=audio,
        sr=sr,
        n_fft=config['n_fft'],
        hop_length=config['hop_length']
    )
    # Normalize to 0-1 range (centroid is in Hz, max ~sr/2)
    centroid_normalized = centroid / (sr / 2)
    # Scale to similar range as mel-spec dB values (-80 to 0)
    centroid_scaled = (centroid_normalized * 80) - 80
    return centroid_scaled  # Shape: [1, time_frames]


def compute_spectral_flatness(
    audio: np.ndarray,
    config: Dict = MEL_CONFIG
) -> np.ndarray:
    """
    Compute spectral flatness (noise vs tone) over time.
    Helps detect distortion and noise content.

    Returns:
        flatness: Shape [1, time_frames] in dB scale
    """
    flatness = librosa.feature.spectral_flatness(
        y=audio,
        n_fft=config['n_fft'],
        hop_length=config['hop_length']
    )
    # Convert to dB (flatness is 0-1, where 1 = pure noise)
    # Add small epsilon to avoid log(0)
    flatness_db = 10 * np.log10(flatness + 1e-10)
    # Clip to reasonable range
    flatness_db = np.clip(flatness_db, -80, 0)
    return flatness_db  # Shape: [1, time_frames]


def compute_multi_channel_features(
    audio: np.ndarray,
    sr: int = MEL_CONFIG['sr'],
    config: Dict = MEL_CONFIG
) -> np.ndarray:
    """
    Compute 4-channel audio features stacked together.

    Channels:
        0: Mel-spectrogram [128, T] - frequency content
        1: RMS envelope [128, T] - broadcast from [1, T] - amplitude envelope
        2: Spectral centroid [128, T] - broadcast from [1, T] - brightness
        3: Spectral flatness [128, T] - broadcast from [1, T] - noise vs tone

    Args:
        audio: Mono audio waveform
        sr: Sample rate
        config: Feature extraction config

    Returns:
        features: Shape [4, 128, T] - 4 channels of audio features
    """
    n_mels = config['n_mels']

    # Channel 0: Mel-spectrogram
    mel_spec = compute_mel_spectrogram(audio, sr, config)  # [128, T]

    # Channel 1: RMS envelope (broadcast to 128 rows)
    rms = compute_rms_envelope(audio, config)  # [1, T]
    rms_broadcast = np.repeat(rms, n_mels, axis=0)  # [128, T]

    # Channel 2: Spectral centroid (broadcast to 128 rows)
    centroid = compute_spectral_centroid(audio, sr, config)  # [1, T]
    centroid_broadcast = np.repeat(centroid, n_mels, axis=0)  # [128, T]

    # Channel 3: Spectral flatness (broadcast to 128 rows)
    flatness = compute_spectral_flatness(audio, config)  # [1, T]
    flatness_broadcast = np.repeat(flatness, n_mels, axis=0)  # [128, T]

    # Stack into 4-channel tensor
    features = np.stack([
        mel_spec,
        rms_broadcast,
        centroid_broadcast,
        flatness_broadcast
    ], axis=0)  # [4, 128, T]

    return features.astype(np.float32)


def load_audio_mono(audio_path: str, sr: int = MEL_CONFIG['sr']) -> np.ndarray:
    """
    Load audio file and convert to mono.

    Args:
        audio_path: Path to audio file
        sr: Target sample rate (resamples if different)

    Returns:
        audio: Mono audio waveform as float32
    """
    audio, _ = librosa.load(audio_path, sr=sr, mono=True)
    return audio.astype(np.float32)


def process_single_audio(
    audio_path: str,
    output_dir: str,
    config: Dict = MEL_CONFIG,
    save_npy: bool = True,
    multi_channel: bool = False
) -> Dict:
    """
    Process a single audio file: load, compute features, save.

    Args:
        audio_path: Path to input .wav file
        output_dir: Directory to save .npy feature files
        config: Feature extraction configuration
        save_npy: Whether to save the features to disk
        multi_channel: If True, compute 4-channel features; else just mel-spec

    Returns:
        result: Dict with processing results
    """
    try:
        audio_path = Path(audio_path)

        # Load audio as mono
        audio = load_audio_mono(str(audio_path), sr=config['sr'])

        # Compute features
        if multi_channel:
            features = compute_multi_channel_features(audio, sr=config['sr'], config=config)
        else:
            features = compute_mel_spectrogram(audio, sr=config['sr'], config=config)

        # Determine output path (mirror input directory structure)
        rel_path = audio_path.relative_to(Path(output_dir).parent / "rendered_audio")
        out_path = Path(output_dir) / rel_path.with_suffix('.npy')

        if save_npy:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(out_path, features.astype(np.float32))

        return {
            'audio_path': str(audio_path),
            'output_path': str(out_path),
            'shape': features.shape,
            'success': True,
            'error': None
        }

    except Exception as e:
        return {
            'audio_path': str(audio_path),
            'output_path': None,
            'shape': None,
            'success': False,
            'error': str(e)
        }


def process_single_audio_worker(audio_path: str, output_dir: str, multi_channel: bool = False) -> Dict:
    """Worker function for multiprocessing."""
    return process_single_audio(audio_path, output_dir, MEL_CONFIG, save_npy=True, multi_channel=multi_channel)


def extract_all_mel_specs(
    audio_dir: str,
    output_dir: str,
    max_files: Optional[int] = None,
    num_workers: int = 1,
    resume: bool = False,
    multi_channel: bool = False
) -> Dict:
    """
    Extract audio features from all audio files.

    Args:
        audio_dir: Directory containing rendered audio files
        output_dir: Directory to save feature .npy files
        max_files: Optional limit on number of files to process
        num_workers: Number of parallel workers (1 = sequential)
        resume: Skip files that already have features extracted
        multi_channel: If True, extract 4-channel features

    Returns:
        stats: Processing statistics
    """
    audio_dir = Path(audio_dir)
    output_dir_path = Path(output_dir)
    wav_files = list(audio_dir.rglob("*.wav"))

    total_found = len(wav_files)

    # Filter out already-processed files if resuming
    if resume:
        files_to_process = []
        for wav_file in wav_files:
            rel_path = wav_file.relative_to(audio_dir)
            expected_npy = output_dir_path / rel_path.with_suffix('.npy')
            if not expected_npy.exists():
                files_to_process.append(wav_file)

        skipped = total_found - len(files_to_process)
        wav_files = files_to_process
        print(f"Resume mode: Skipping {skipped:,} already-processed files")

    if max_files:
        wav_files = wav_files[:max_files]

    feature_type = "4-channel (mel+rms+centroid+flatness)" if multi_channel else "mel-spectrogram only"
    print(f"Found {len(wav_files)} audio files to process (of {total_found:,} total)")
    print(f"Feature type: {feature_type}")
    print(f"Output directory: {output_dir}")
    print(f"Workers: {num_workers}")
    print(f"Config: {MEL_CONFIG['n_mels']} mels, {MEL_CONFIG['n_fft']} FFT, {MEL_CONFIG['hop_length']} hop")
    print()

    results = []

    if num_workers > 1:
        ctx = mp.get_context('spawn')
        worker_fn = partial(process_single_audio_worker, output_dir=output_dir, multi_channel=multi_channel)

        with ctx.Pool(num_workers) as pool:
            results = list(tqdm(
                pool.imap(worker_fn, [str(f) for f in wav_files]),
                total=len(wav_files),
                desc="Extracting features"
            ))
    else:
        for wav_file in tqdm(wav_files, desc="Extracting features"):
            result = process_single_audio(str(wav_file), output_dir, multi_channel=multi_channel)
            results.append(result)

    # Compute statistics
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    shapes = [r['shape'] for r in successful if r['shape']]
    if shapes:
        unique_shapes = list(set(shapes))
        shape_counts = {str(s): shapes.count(s) for s in unique_shapes}
    else:
        shape_counts = {}

    stats = {
        'total_files': len(wav_files),
        'successful': len(successful),
        'failed': len(failed),
        'success_rate': len(successful) / len(wav_files) * 100 if wav_files else 0,
        'shape_distribution': shape_counts,
        'mel_config': MEL_CONFIG,
        'multi_channel': multi_channel,
        'errors': [{'file': r['audio_path'], 'error': r['error']} for r in failed[:20]]
    }

    output_dir_path.mkdir(parents=True, exist_ok=True)
    with open(output_dir_path / 'extraction_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\n=== Extraction Complete ===")
    print(f"Successful: {stats['successful']:,} / {stats['total_files']:,} ({stats['success_rate']:.1f}%)")
    print(f"Failed: {stats['failed']}")
    print(f"Shape distribution: {shape_counts}")
    print(f"Stats saved to: {output_dir_path / 'extraction_stats.json'}")

    return stats


def process_audio_to_path(args: Tuple[str, str, bool]) -> Dict:
    """Process a single audio file and save to specific output path."""
    audio_path, output_path, multi_channel = args

    try:
        audio = load_audio_mono(audio_path)

        if multi_channel:
            features = compute_multi_channel_features(audio)
        else:
            features = compute_mel_spectrogram(audio)

        np.save(output_path, features.astype(np.float32))

        return {
            'success': True,
            'audio_path': audio_path,
            'output_path': output_path,
            'shape': features.shape
        }
    except Exception as e:
        return {
            'success': False,
            'audio_path': audio_path,
            'error': str(e)
        }


def extract_from_inventory(
    inventory_path: str,
    output_dir: str,
    max_files: Optional[int] = None,
    num_workers: int = 1,
    resume: bool = False,
    multi_channel: bool = False
) -> Dict:
    """
    Extract audio features from files listed in an inventory JSON.
    """
    with open(inventory_path, 'r') as f:
        inventory = json.load(f)

    audio_files = []
    audio_extensions = {'.wav', '.aif', '.aiff', '.mp3', '.flac'}

    for pack in inventory.get('packs', []):
        for audio_path in pack.get('audio_files', []):
            ext = Path(audio_path).suffix.lower()
            if ext in audio_extensions:
                audio_files.append(audio_path)

    total_found = len(audio_files)
    print(f"Found {total_found:,} audio files in inventory")

    output_dir_path = Path(output_dir)
    if resume:
        files_to_process = []
        for audio_path in audio_files:
            safe_name = Path(audio_path).name
            expected_npy = output_dir_path / f"{safe_name}.npy"
            if not expected_npy.exists():
                files_to_process.append(audio_path)

        skipped = total_found - len(files_to_process)
        audio_files = files_to_process
        print(f"Resume mode: Skipping {skipped:,} already-processed files")

    if max_files:
        audio_files = audio_files[:max_files]

    feature_type = "4-channel (mel+rms+centroid+flatness)" if multi_channel else "mel-spectrogram only"
    print(f"Processing {len(audio_files):,} audio files")
    print(f"Feature type: {feature_type}")
    print(f"Output directory: {output_dir}")
    print(f"Workers: {num_workers}")
    print()

    output_dir_path.mkdir(parents=True, exist_ok=True)

    results = []

    if num_workers > 1:
        ctx = mp.get_context('spawn')

        work_items = []
        for audio_path in audio_files:
            safe_name = Path(audio_path).name
            output_path = str(output_dir_path / f"{safe_name}.npy")
            work_items.append((audio_path, output_path, multi_channel))

        with ctx.Pool(num_workers) as pool:
            results = list(tqdm(
                pool.imap(process_audio_to_path, work_items),
                total=len(work_items),
                desc="Extracting features"
            ))
    else:
        for audio_path in tqdm(audio_files, desc="Extracting features"):
            safe_name = Path(audio_path).name
            output_path = str(output_dir_path / f"{safe_name}.npy")
            result = process_audio_to_path((audio_path, output_path, multi_channel))
            results.append(result)

    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]

    stats = {
        'total_files': len(audio_files),
        'successful': len(successful),
        'failed': len(failed),
        'success_rate': len(successful) / len(audio_files) * 100 if audio_files else 0,
        'mel_config': MEL_CONFIG,
        'multi_channel': multi_channel,
        'errors': [{'file': r.get('audio_path'), 'error': r.get('error')} for r in failed[:20]]
    }

    with open(output_dir_path / 'extraction_stats_external.json', 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\n=== Extraction Complete ===")
    print(f"Successful: {stats['successful']:,} / {stats['total_files']:,} ({stats['success_rate']:.1f}%)")
    print(f"Failed: {stats['failed']}")
    print(f"Stats saved to: {output_dir_path / 'extraction_stats_external.json'}")

    return stats


def visualize_multi_channel_features(audio_path: str, save_path: Optional[str] = None):
    """
    Visualize all 4 channels of audio features.
    """
    import matplotlib.pyplot as plt

    audio = load_audio_mono(audio_path)
    features = compute_multi_channel_features(audio)

    fig, axes = plt.subplots(5, 1, figsize=(14, 12))

    # Plot waveform
    times = np.arange(len(audio)) / MEL_CONFIG['sr']
    axes[0].plot(times, audio, linewidth=0.5)
    axes[0].set_xlabel('Time (s)')
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title(f'Waveform: {Path(audio_path).name}')
    axes[0].set_xlim(0, times[-1])

    channel_names = ['Mel-Spectrogram', 'RMS Envelope', 'Spectral Centroid', 'Spectral Flatness']

    for i, name in enumerate(channel_names):
        img = librosa.display.specshow(
            features[i],
            x_axis='time',
            y_axis='mel' if i == 0 else 'linear',
            sr=MEL_CONFIG['sr'],
            hop_length=MEL_CONFIG['hop_length'],
            fmin=MEL_CONFIG['fmin'] if i == 0 else None,
            fmax=MEL_CONFIG['fmax'] if i == 0 else None,
            ax=axes[i + 1]
        )
        axes[i + 1].set_title(f'Channel {i}: {name}')
        fig.colorbar(img, ax=axes[i + 1], format='%+2.0f dB')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved visualization to: {save_path}")
    else:
        plt.show()

    plt.close()

    return features


def main():
    parser = argparse.ArgumentParser(
        description="Extract audio features from rendered Serum audio files"
    )
    parser.add_argument(
        '--audio-dir',
        type=str,
        default='/Users/brentpinero/Documents/serum_llm_2/data/rendered_audio',
        help='Directory containing rendered audio files'
    )
    parser.add_argument(
        '--from-inventory',
        type=str,
        default=None,
        help='Load audio paths from inventory JSON'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='/Users/brentpinero/Documents/serum_llm_2/data/mel_specs',
        help='Directory to save feature files'
    )
    parser.add_argument(
        '--multi-channel',
        action='store_true',
        help='Extract 4-channel features (mel + rms + centroid + flatness)'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Use multiprocessing for extraction'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Number of parallel workers (default: cpu_count - 2)'
    )
    parser.add_argument(
        '--max-files',
        type=int,
        default=None,
        help='Limit number of files to process (for testing)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run a quick test on 10 files'
    )
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Visualize features for a sample file'
    )
    parser.add_argument(
        '--audio-path',
        type=str,
        default=None,
        help='Specific audio file to visualize'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Skip files that already have features extracted'
    )

    args = parser.parse_args()

    if args.visualize:
        if args.audio_path:
            audio_path = args.audio_path
        else:
            wav_files = list(Path(args.audio_dir).rglob("*.wav"))
            if not wav_files:
                print("No audio files found!")
                return
            audio_path = str(wav_files[0])

        print(f"Visualizing: {audio_path}")
        if args.multi_channel:
            features = visualize_multi_channel_features(audio_path)
            print(f"Multi-channel features shape: {features.shape}")
        else:
            audio = load_audio_mono(audio_path)
            mel_spec = compute_mel_spectrogram(audio)
            print(f"Mel-spectrogram shape: {mel_spec.shape}")
        return

    if args.test:
        args.max_files = 10
        args.parallel = False

    num_workers = 1
    if args.parallel:
        num_workers = args.workers or max(1, mp.cpu_count() - 2)

    if args.from_inventory:
        stats = extract_from_inventory(
            inventory_path=args.from_inventory,
            output_dir=args.output_dir,
            max_files=args.max_files,
            num_workers=num_workers,
            resume=args.resume,
            multi_channel=args.multi_channel
        )
    else:
        stats = extract_all_mel_specs(
            audio_dir=args.audio_dir,
            output_dir=args.output_dir,
            max_files=args.max_files,
            num_workers=num_workers,
            resume=args.resume,
            multi_channel=args.multi_channel
        )

    return stats


if __name__ == '__main__':
    main()
