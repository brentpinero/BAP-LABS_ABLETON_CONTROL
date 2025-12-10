#!/usr/bin/env python3
"""
Mel-Spectrogram Extraction Pipeline for Serum Preset Audio
============================================================
Extracts mel-spectrograms from rendered audio files for CNN training.

Usage:
    # Test on a few files
    python mel_spectrogram_pipeline.py --test --max-files 10

    # Run full extraction with parallelization
    python mel_spectrogram_pipeline.py --parallel --workers 8

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
# MEL-SPECTROGRAM CONFIGURATION
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
    # Compute mel spectrogram
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


def load_audio_mono(audio_path: str, sr: int = MEL_CONFIG['sr']) -> np.ndarray:
    """
    Load audio file and convert to mono.

    Args:
        audio_path: Path to audio file
        sr: Target sample rate (resamples if different)

    Returns:
        audio: Mono audio waveform as float32
    """
    # Load with librosa (handles resampling automatically)
    audio, _ = librosa.load(audio_path, sr=sr, mono=True)
    return audio.astype(np.float32)


def process_single_audio(
    audio_path: str,
    output_dir: str,
    config: Dict = MEL_CONFIG,
    save_npy: bool = True
) -> Dict:
    """
    Process a single audio file: load, compute mel-spec, save.

    Args:
        audio_path: Path to input .wav file
        output_dir: Directory to save .npy mel-spec files
        config: Mel-spectrogram configuration
        save_npy: Whether to save the mel-spec to disk

    Returns:
        result: Dict with processing results
    """
    try:
        audio_path = Path(audio_path)

        # Load audio as mono
        audio = load_audio_mono(str(audio_path), sr=config['sr'])

        # Compute mel-spectrogram
        mel_spec = compute_mel_spectrogram(audio, sr=config['sr'], config=config)

        # Determine output path (mirror input directory structure)
        # e.g., data/rendered_audio/bass/preset_C3.wav -> data/mel_specs/bass/preset_C3.npy
        rel_path = audio_path.relative_to(Path(output_dir).parent / "rendered_audio")
        out_path = Path(output_dir) / rel_path.with_suffix('.npy')

        if save_npy:
            # Create output directory if needed
            out_path.parent.mkdir(parents=True, exist_ok=True)

            # Save as compressed numpy array (much smaller than raw)
            np.save(out_path, mel_spec.astype(np.float32))

        return {
            'audio_path': str(audio_path),
            'output_path': str(out_path),
            'shape': mel_spec.shape,
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


def process_single_audio_worker(audio_path: str, output_dir: str) -> Dict:
    """Worker function for multiprocessing (needs to be picklable)."""
    return process_single_audio(audio_path, output_dir, MEL_CONFIG, save_npy=True)


def extract_all_mel_specs(
    audio_dir: str,
    output_dir: str,
    max_files: Optional[int] = None,
    num_workers: int = 1,
    resume: bool = False
) -> Dict:
    """
    Extract mel-spectrograms from all audio files.

    Args:
        audio_dir: Directory containing rendered audio files
        output_dir: Directory to save mel-spectrogram .npy files
        max_files: Optional limit on number of files to process
        num_workers: Number of parallel workers (1 = sequential)
        resume: Skip files that already have mel-specs extracted

    Returns:
        stats: Processing statistics
    """
    # Find all .wav files
    audio_dir = Path(audio_dir)
    output_dir_path = Path(output_dir)
    wav_files = list(audio_dir.rglob("*.wav"))

    total_found = len(wav_files)

    # Filter out already-processed files if resuming
    if resume:
        files_to_process = []
        for wav_file in wav_files:
            # Compute expected output path
            rel_path = wav_file.relative_to(audio_dir)
            expected_npy = output_dir_path / rel_path.with_suffix('.npy')
            if not expected_npy.exists():
                files_to_process.append(wav_file)

        skipped = total_found - len(files_to_process)
        wav_files = files_to_process
        print(f"Resume mode: Skipping {skipped:,} already-processed files")

    if max_files:
        wav_files = wav_files[:max_files]

    print(f"Found {len(wav_files)} audio files to process (of {total_found:,} total)")
    print(f"Output directory: {output_dir}")
    print(f"Workers: {num_workers}")
    print(f"Mel-spec config: {MEL_CONFIG['n_mels']} mels, {MEL_CONFIG['n_fft']} FFT, {MEL_CONFIG['hop_length']} hop")
    print()

    results = []

    if num_workers > 1:
        # Parallel processing
        ctx = mp.get_context('spawn')  # macOS compatibility
        worker_fn = partial(process_single_audio_worker, output_dir=output_dir)

        with ctx.Pool(num_workers) as pool:
            results = list(tqdm(
                pool.imap(worker_fn, [str(f) for f in wav_files]),
                total=len(wav_files),
                desc="Extracting mel-specs"
            ))
    else:
        # Sequential processing
        for wav_file in tqdm(wav_files, desc="Extracting mel-specs"):
            result = process_single_audio(str(wav_file), output_dir)
            results.append(result)

    # Compute statistics
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    # Get shape distribution
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
        'errors': [{'file': r['audio_path'], 'error': r['error']} for r in failed[:20]]  # First 20 errors
    }

    # Save stats
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / 'extraction_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\n=== Extraction Complete ===")
    print(f"Successful: {stats['successful']:,} / {stats['total_files']:,} ({stats['success_rate']:.1f}%)")
    print(f"Failed: {stats['failed']}")
    print(f"Shape distribution: {shape_counts}")
    print(f"Stats saved to: {output_dir / 'extraction_stats.json'}")

    return stats


def visualize_mel_spectrogram(audio_path: str, save_path: Optional[str] = None):
    """
    Visualize a mel-spectrogram for debugging/inspection.

    Args:
        audio_path: Path to audio file
        save_path: Optional path to save the visualization
    """
    import matplotlib.pyplot as plt

    # Load and process
    audio = load_audio_mono(audio_path)
    mel_spec = compute_mel_spectrogram(audio)

    # Create figure
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # Plot waveform
    times = np.arange(len(audio)) / MEL_CONFIG['sr']
    axes[0].plot(times, audio, linewidth=0.5)
    axes[0].set_xlabel('Time (s)')
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title(f'Waveform: {Path(audio_path).name}')
    axes[0].set_xlim(0, times[-1])

    # Plot mel-spectrogram
    img = librosa.display.specshow(
        mel_spec,
        x_axis='time',
        y_axis='mel',
        sr=MEL_CONFIG['sr'],
        hop_length=MEL_CONFIG['hop_length'],
        fmin=MEL_CONFIG['fmin'],
        fmax=MEL_CONFIG['fmax'],
        ax=axes[1]
    )
    axes[1].set_title(f'Mel-Spectrogram: {mel_spec.shape[0]} mels x {mel_spec.shape[1]} frames')
    fig.colorbar(img, ax=axes[1], format='%+2.0f dB')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved visualization to: {save_path}")
    else:
        plt.show()

    plt.close()

    return mel_spec


def extract_from_inventory(
    inventory_path: str,
    output_dir: str,
    max_files: Optional[int] = None,
    num_workers: int = 1,
    resume: bool = False
) -> Dict:
    """
    Extract mel-spectrograms from audio files listed in an inventory JSON.

    This is useful for processing external sample pack audio that doesn't
    live in a single directory structure.

    Args:
        inventory_path: Path to inventory JSON (from scan_sample_packs.py)
        output_dir: Directory to save mel-spectrogram files
        max_files: Optional limit on number of files to process
        num_workers: Number of parallel workers (1 = sequential)
        resume: Skip files that already have mel-specs extracted

    Returns:
        stats: Processing statistics
    """
    with open(inventory_path, 'r') as f:
        inventory = json.load(f)

    # Collect all audio paths from packs
    audio_files = []
    audio_extensions = {'.wav', '.aif', '.aiff', '.mp3', '.flac'}

    for pack in inventory.get('packs', []):
        for audio_path in pack.get('audio_files', []):
            ext = Path(audio_path).suffix.lower()
            if ext in audio_extensions:
                audio_files.append(audio_path)

    total_found = len(audio_files)
    print(f"Found {total_found:,} audio files in inventory")

    # Filter out already-processed files if resuming
    output_dir_path = Path(output_dir)
    if resume:
        files_to_process = []
        for audio_path in audio_files:
            # Create a safe output filename from the full path
            safe_name = Path(audio_path).name
            expected_npy = output_dir_path / f"{safe_name}.npy"
            if not expected_npy.exists():
                files_to_process.append(audio_path)

        skipped = total_found - len(files_to_process)
        audio_files = files_to_process
        print(f"Resume mode: Skipping {skipped:,} already-processed files")

    if max_files:
        audio_files = audio_files[:max_files]

    print(f"Processing {len(audio_files):,} audio files")
    print(f"Output directory: {output_dir}")
    print(f"Workers: {num_workers}")
    print(f"Mel-spec config: {MEL_CONFIG['n_mels']} mels, {MEL_CONFIG['n_fft']} FFT, {MEL_CONFIG['hop_length']} hop")
    print()

    # Create output directory
    output_dir_path.mkdir(parents=True, exist_ok=True)

    results = []

    if num_workers > 1:
        # Parallel processing with custom output naming
        ctx = mp.get_context('spawn')

        # Create (audio_path, output_path) pairs
        work_items = []
        for audio_path in audio_files:
            safe_name = Path(audio_path).name
            output_path = str(output_dir_path / f"{safe_name}.npy")
            work_items.append((audio_path, output_path))

        worker_fn = process_audio_to_path

        with ctx.Pool(num_workers) as pool:
            results = list(tqdm(
                pool.imap(worker_fn, work_items),
                total=len(work_items),
                desc="Extracting mel-specs"
            ))
    else:
        # Sequential processing
        for audio_path in tqdm(audio_files, desc="Extracting mel-specs"):
            safe_name = Path(audio_path).name
            output_path = str(output_dir_path / f"{safe_name}.npy")
            result = process_audio_to_path((audio_path, output_path))
            results.append(result)

    # Compute statistics
    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]

    stats = {
        'total_files': len(audio_files),
        'successful': len(successful),
        'failed': len(failed),
        'success_rate': len(successful) / len(audio_files) * 100 if audio_files else 0,
        'mel_config': MEL_CONFIG,
        'errors': [{'file': r.get('audio_path'), 'error': r.get('error')} for r in failed[:20]]
    }

    # Save stats
    with open(output_dir_path / 'extraction_stats_external.json', 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\n=== Extraction Complete ===")
    print(f"Successful: {stats['successful']:,} / {stats['total_files']:,} ({stats['success_rate']:.1f}%)")
    print(f"Failed: {stats['failed']}")
    print(f"Stats saved to: {output_dir_path / 'extraction_stats_external.json'}")

    return stats


def process_audio_to_path(args: Tuple[str, str]) -> Dict:
    """Process a single audio file and save to specific output path."""
    audio_path, output_path = args

    try:
        # Load audio
        audio = load_audio_mono(audio_path)

        # Compute mel-spectrogram
        mel_spec = compute_mel_spectrogram(audio)

        # Save
        np.save(output_path, mel_spec.astype(np.float32))

        return {
            'success': True,
            'audio_path': audio_path,
            'output_path': output_path,
            'shape': mel_spec.shape
        }
    except Exception as e:
        return {
            'success': False,
            'audio_path': audio_path,
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(
        description="Extract mel-spectrograms from rendered Serum audio files"
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
        help='Load audio paths from inventory JSON (e.g., external_drive_inventory.json)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='/Users/brentpinero/Documents/serum_llm_2/data/mel_specs',
        help='Directory to save mel-spectrogram files'
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
        help='Visualize a mel-spectrogram'
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
        help='Skip files that already have mel-specs extracted'
    )

    args = parser.parse_args()

    if args.visualize:
        # Visualization mode
        if args.audio_path:
            audio_path = args.audio_path
        else:
            # Find a sample file
            wav_files = list(Path(args.audio_dir).rglob("*.wav"))
            if not wav_files:
                print("No audio files found!")
                return
            audio_path = str(wav_files[0])

        print(f"Visualizing: {audio_path}")
        mel_spec = visualize_mel_spectrogram(audio_path)
        print(f"Mel-spectrogram shape: {mel_spec.shape}")
        return

    # Set defaults
    if args.test:
        args.max_files = 10
        args.parallel = False

    num_workers = 1
    if args.parallel:
        num_workers = args.workers or max(1, mp.cpu_count() - 2)

    # Run extraction - either from inventory or directory
    if args.from_inventory:
        # Process files from inventory JSON (external sample packs)
        stats = extract_from_inventory(
            inventory_path=args.from_inventory,
            output_dir=args.output_dir,
            max_files=args.max_files,
            num_workers=num_workers,
            resume=args.resume
        )
    else:
        # Process files from directory (Serum renders)
        stats = extract_all_mel_specs(
            audio_dir=args.audio_dir,
            output_dir=args.output_dir,
            max_files=args.max_files,
            num_workers=num_workers,
            resume=args.resume
        )

    return stats


if __name__ == '__main__':
    main()
