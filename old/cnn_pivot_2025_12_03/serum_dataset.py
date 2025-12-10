#!/usr/bin/env python3
"""
Serum Audio Dataset for CNN Training
=====================================
PyTorch Dataset that loads mel-spectrograms paired with preset parameters.

This dataset supports:
1. Loading pre-computed mel-spectrograms (.npy files)
2. Extracting relevant parameters from the preset database
3. Normalizing parameters to [0, 1] range for training
4. Optional augmentation for spectrograms

Usage:
    from serum_dataset import SerumAudioDataset, get_dataloaders

    train_loader, val_loader = get_dataloaders(
        mel_spec_dir='data/mel_specs',
        preset_json='data/ultimate_training_dataset/ultimate_serum_dataset_expanded.json',
        batch_size=32
    )
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, random_split

# Import centralized param definitions
from serum_params import CNN_PARAMS, LLM_PARAMS, PARAM_RANGES, normalize_param, denormalize_param


# normalize_param and denormalize_param imported from serum_params


class SerumAudioDataset(Dataset):
    """
    PyTorch Dataset for Serum mel-spectrograms + parameters.

    Each sample contains:
    - mel_spec: [1, 128, T] mel-spectrogram tensor (T varies by audio length)
    - params: [30] tensor of normalized CNN parameters (high-variance params)
    - metadata: dict with preset name, category, note
    """

    def __init__(
        self,
        mel_spec_dir: str,
        preset_json: str,
        param_list: List[str] = None,  # Defaults to CNN_PARAMS
        target_length: int = 128,  # Pad/crop spectrograms to this length
        normalize_specs: bool = True,
        categories: Optional[List[str]] = None,  # Filter by category
    ):
        """
        Args:
            mel_spec_dir: Directory containing mel-spectrogram .npy files
            preset_json: Path to preset database JSON
            param_list: List of parameter names to extract
            target_length: Target time dimension (pad/crop to this)
            normalize_specs: Whether to normalize spectrograms to [-1, 1]
            categories: Optional list of categories to include (e.g., ['bass', 'lead'])
        """
        self.mel_spec_dir = Path(mel_spec_dir)
        self.param_list = param_list if param_list is not None else CNN_PARAMS
        self.target_length = target_length
        self.normalize_specs = normalize_specs

        # Load preset database
        print(f"Loading preset database from {preset_json}...")
        with open(preset_json, 'r') as f:
            self.preset_db = json.load(f)

        # Build name -> preset index mapping
        self.preset_lookup = self._build_preset_lookup()

        # Find all mel-spec files and match to presets
        self.samples = self._find_samples(categories)

        print(f"Found {len(self.samples)} audio samples with matched presets")
        print(f"Parameters per sample: {len(self.param_list)}")

    def _build_preset_lookup(self) -> Dict[str, int]:
        """Build mapping from preset name to database index."""
        lookup = {}
        for i, preset in enumerate(self.preset_db):
            name = preset.get('preset_name', '').strip()
            # Normalize: remove all non-alphanumeric, lowercase
            normalized = re.sub(r'[^a-z0-9]', '', name.lower())
            lookup[normalized] = i
        return lookup

    def _extract_preset_name_from_file(self, filepath: Path) -> str:
        """Extract preset name from mel-spec filename.

        Format: {preset_name}___{note}.npy
        Example: 16_bass_02___________________C3.npy -> 16_bass_02
        """
        # Remove .npy extension
        name = filepath.stem
        # Split on multiple underscores (the separator pattern is ___)
        # The note is the last part after the last occurrence of ___
        parts = name.rsplit('___', 1)
        if len(parts) == 2:
            preset_name = parts[0]
        else:
            preset_name = name
        return preset_name.strip('_').strip()

    def _extract_note_from_file(self, filepath: Path) -> str:
        """Extract MIDI note from filename."""
        name = filepath.stem
        parts = name.rsplit('___', 1)
        if len(parts) == 2:
            # Note like C3, A1, Fs2, etc.
            note = parts[1].strip('_').strip()
            return note
        return 'C3'  # Default

    def _match_preset(self, preset_name: str) -> Optional[int]:
        """Match preset name to database entry."""
        # Same normalization as lookup: remove all non-alphanumeric, lowercase
        normalized = re.sub(r'[^a-z0-9]', '', preset_name.lower())
        return self.preset_lookup.get(normalized)

    def _find_samples(self, categories: Optional[List[str]] = None) -> List[Dict]:
        """Find all mel-spec files and match to presets."""
        samples = []

        # Get category directories
        if categories:
            category_dirs = [self.mel_spec_dir / cat for cat in categories]
        else:
            category_dirs = [d for d in self.mel_spec_dir.iterdir() if d.is_dir()]

        for cat_dir in category_dirs:
            if not cat_dir.exists():
                continue

            category = cat_dir.name

            for npy_file in cat_dir.glob('*.npy'):
                preset_name = self._extract_preset_name_from_file(npy_file)
                note = self._extract_note_from_file(npy_file)

                preset_idx = self._match_preset(preset_name)

                if preset_idx is not None:
                    samples.append({
                        'mel_path': str(npy_file),
                        'preset_idx': preset_idx,
                        'preset_name': preset_name,
                        'category': category,
                        'note': note,
                    })

        return samples

    def _get_params(self, preset_idx: int) -> np.ndarray:
        """Extract and normalize parameters for a preset."""
        preset = self.preset_db[preset_idx]
        params = preset.get('parameters', {})

        param_values = []
        for param_name in self.param_list:
            value = params.get(param_name, 0.0)
            # Handle potential non-numeric values
            if not isinstance(value, (int, float)):
                value = 0.0
            # Normalize
            normalized = normalize_param(float(value), param_name)
            param_values.append(normalized)

        return np.array(param_values, dtype=np.float32)

    def _pad_or_crop(self, mel_spec: np.ndarray) -> np.ndarray:
        """Pad or crop spectrogram to target length (2D: [H, T])."""
        current_len = mel_spec.shape[1]

        if current_len == self.target_length:
            return mel_spec
        elif current_len > self.target_length:
            # Crop from the start (keep attack portion)
            return mel_spec[:, :self.target_length]
        else:
            # Pad with minimum value (silence in dB scale)
            padding = np.full(
                (mel_spec.shape[0], self.target_length - current_len),
                mel_spec.min(),
                dtype=mel_spec.dtype
            )
            return np.concatenate([mel_spec, padding], axis=1)

    def _pad_or_crop_multichannel(self, features: np.ndarray) -> np.ndarray:
        """Pad or crop multi-channel features to target length (3D: [C, H, T])."""
        current_len = features.shape[-1]  # Time is last dimension

        if current_len == self.target_length:
            return features
        elif current_len > self.target_length:
            # Crop from the start (keep attack portion)
            return features[:, :, :self.target_length]
        else:
            # Pad with minimum value per channel (silence in dB scale)
            pad_shape = list(features.shape)
            pad_shape[-1] = self.target_length - current_len
            padding = np.full(pad_shape, features.min(), dtype=features.dtype)
            return np.concatenate([features, padding], axis=-1)

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, Dict]:
        sample = self.samples[idx]

        # Load mel-spectrogram (or multi-channel features)
        features = np.load(sample['mel_path'])

        # Handle both single-channel [128, T] and multi-channel [C, 128, T]
        if features.ndim == 2:
            # Single-channel mel-spec: [128, T] -> [1, 128, T]
            features = features[np.newaxis, :, :]
        # Multi-channel is already [C, 128, T]

        # Pad/crop to target length (works on last dimension)
        features = self._pad_or_crop_multichannel(features)

        # Normalize to [-1, 1] if requested
        if self.normalize_specs:
            # All features are in dB scale, typically -80 to 0
            features = (features + 40) / 40  # Shift and scale to ~[-1, 1]
            features = np.clip(features, -1, 1)

        # Get parameters
        params = self._get_params(sample['preset_idx'])

        # Metadata
        metadata = {
            'preset_name': sample['preset_name'],
            'category': sample['category'],
            'note': sample['note'],
        }

        return (
            torch.from_numpy(features),
            torch.from_numpy(params),
            metadata
        )


def collate_fn(batch):
    """Custom collate function that handles metadata dicts."""
    mel_specs = torch.stack([item[0] for item in batch])
    params = torch.stack([item[1] for item in batch])
    metadata = [item[2] for item in batch]
    return mel_specs, params, metadata


def get_dataloaders(
    mel_spec_dir: str,
    preset_json: str,
    batch_size: int = 32,
    val_split: float = 0.1,
    num_workers: int = 4,
    target_length: int = 128,
    categories: Optional[List[str]] = None,
    seed: int = 42,
) -> Tuple[DataLoader, DataLoader]:
    """
    Create train and validation dataloaders.

    Args:
        mel_spec_dir: Directory containing mel-spectrogram files
        preset_json: Path to preset database JSON
        batch_size: Batch size for training
        val_split: Fraction of data to use for validation
        num_workers: Number of data loading workers
        target_length: Target spectrogram length
        categories: Optional list of categories to include
        seed: Random seed for split

    Returns:
        train_loader, val_loader
    """
    # Create full dataset
    dataset = SerumAudioDataset(
        mel_spec_dir=mel_spec_dir,
        preset_json=preset_json,
        target_length=target_length,
        categories=categories,
    )

    # Split into train/val
    val_size = int(len(dataset) * val_split)
    train_size = len(dataset) - val_size

    generator = torch.Generator().manual_seed(seed)
    train_dataset, val_dataset = random_split(
        dataset, [train_size, val_size], generator=generator
    )

    print(f"Train samples: {train_size}, Validation samples: {val_size}")

    # Create dataloaders
    # Note: pin_memory not supported on MPS, set to False
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        collate_fn=collate_fn,
        pin_memory=False,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        collate_fn=collate_fn,
        pin_memory=False,
    )

    return train_loader, val_loader


# =============================================================================
# QUICK TEST
# =============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Test Serum Audio Dataset")
    parser.add_argument('--mel-dir', type=str,
                        default='data/mel_specs',
                        help='Mel spectrogram directory')
    parser.add_argument('--preset-json', type=str,
                        default='data/ultimate_training_dataset/ultimate_serum_dataset_expanded.json',
                        help='Preset database JSON')
    parser.add_argument('--batch-size', type=int, default=4)
    parser.add_argument('--category', type=str, default=None,
                        help='Filter by category (e.g., bass)')

    args = parser.parse_args()

    categories = [args.category] if args.category else None

    print("=" * 60)
    print("SERUM AUDIO DATASET TEST")
    print("=" * 60)

    # Create dataset
    dataset = SerumAudioDataset(
        mel_spec_dir=args.mel_dir,
        preset_json=args.preset_json,
        categories=categories,
    )

    if len(dataset) == 0:
        print("No samples found! Check paths and file matching.")
    else:
        # Test single sample
        mel_spec, params, meta = dataset[0]
        print(f"\nSample 0:")
        print(f"  Mel-spec shape: {mel_spec.shape}")
        print(f"  Params shape: {params.shape}")
        print(f"  Preset: {meta['preset_name']}")
        print(f"  Category: {meta['category']}")
        print(f"  Note: {meta['note']}")

        # Show parameter values
        print(f"\n  Parameters:")
        for i, (name, val) in enumerate(zip(CNN_PARAMS[:5], params[:5])):
            print(f"    {name}: {val:.3f}")
        print(f"    ... ({len(CNN_PARAMS) - 5} more)")

        # Test dataloader
        print("\n" + "-" * 40)
        print("Testing DataLoader...")

        train_loader, val_loader = get_dataloaders(
            mel_spec_dir=args.mel_dir,
            preset_json=args.preset_json,
            batch_size=args.batch_size,
            categories=categories,
            num_workers=0,  # Use 0 for testing (avoids macOS multiprocessing issues)
        )

        # Get one batch
        mel_batch, param_batch, meta_batch = next(iter(train_loader))
        print(f"\nBatch shapes:")
        print(f"  Mel-specs: {mel_batch.shape}")
        print(f"  Params: {param_batch.shape}")
        print(f"  Batch size: {len(meta_batch)}")

        print("\n✅ Dataset test passed!")
