#!/usr/bin/env python3
"""
CNN Training Script for Serum Audio Encoder
=============================================
Trains the CNN to predict synthesizer parameters from mel-spectrograms.

Usage:
    # Quick test run (1 epoch, small batch)
    python train_cnn.py --test

    # Full training
    python train_cnn.py --epochs 50 --batch-size 32

    # Resume from checkpoint
    python train_cnn.py --resume checkpoints/best_model.pt
"""

import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm

# Local imports
from serum_dataset import SerumAudioDataset, get_dataloaders, collate_fn
from cnn_audio_encoder import SerumAudioEncoder, SerumAudioEncoderLight
from serum_params import CNN_PARAMS, NUM_CNN_PARAMS


# =============================================================================
# TRAINING CONFIGURATION
# =============================================================================

DEFAULT_CONFIG = {
    # Data
    'mel_spec_dir': 'data/mel_specs',
    'preset_json': 'data/ultimate_training_dataset/ultimate_serum_dataset_expanded.json',
    'target_length': 128,

    # Model
    'model_type': 'full',  # 'full' or 'light'
    'embedding_dim': 512,
    'dropout': 0.3,
    'in_channels': 1,  # 1 for mel-only, 4 for multi-channel features

    # Training
    'batch_size': 32,
    'epochs': 50,
    'learning_rate': 1e-4,
    'weight_decay': 1e-5,
    'val_split': 0.1,

    # Optimization
    'scheduler': 'cosine',  # 'cosine' or 'plateau'
    'warmup_epochs': 5,
    'min_lr': 1e-6,

    # Checkpointing
    'checkpoint_dir': 'checkpoints',
    'save_every': 5,  # Save every N epochs

    # Hardware
    'num_workers': 4,
}


# =============================================================================
# TRAINING FUNCTIONS
# =============================================================================

def get_device() -> torch.device:
    """Get the best available device (MPS for M4 Max, else CPU)."""
    if torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")


def create_model(config: Dict, device: torch.device) -> nn.Module:
    """Create and initialize the model."""
    in_channels = config.get('in_channels', 1)

    if config['model_type'] == 'light':
        model = SerumAudioEncoderLight(
            n_mels=128,
            embedding_dim=config['embedding_dim'] // 2,
            num_params=NUM_CNN_PARAMS,
            in_channels=in_channels,
        )
    else:
        model = SerumAudioEncoder(
            n_mels=128,
            embedding_dim=config['embedding_dim'],
            num_params=NUM_CNN_PARAMS,
            dropout=config['dropout'],
            in_channels=in_channels,
        )

    return model.to(device)


def train_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
    epoch: int,
) -> Dict[str, float]:
    """Train for one epoch."""
    model.train()
    total_loss = 0.0
    num_batches = 0

    pbar = tqdm(train_loader, desc=f"Epoch {epoch} [Train]", leave=False)

    for mel_specs, params, metadata in pbar:
        # Move to device
        mel_specs = mel_specs.to(device)
        params = params.to(device)

        # Forward pass
        optimizer.zero_grad()
        outputs = model(mel_specs, return_params=True)
        pred_params = outputs['params']

        # Compute loss
        loss = criterion(pred_params, params)

        # Backward pass
        loss.backward()
        optimizer.step()

        # Track metrics
        total_loss += loss.item()
        num_batches += 1

        pbar.set_postfix({'loss': f'{loss.item():.4f}'})

    avg_loss = total_loss / num_batches
    return {'train_loss': avg_loss}


@torch.no_grad()
def validate(
    model: nn.Module,
    val_loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    epoch: int,
) -> Dict[str, float]:
    """Validate the model."""
    model.eval()
    total_loss = 0.0
    total_mae = 0.0
    num_batches = 0

    pbar = tqdm(val_loader, desc=f"Epoch {epoch} [Val]", leave=False)

    for mel_specs, params, metadata in pbar:
        mel_specs = mel_specs.to(device)
        params = params.to(device)

        outputs = model(mel_specs, return_params=True)
        pred_params = outputs['params']

        loss = criterion(pred_params, params)
        mae = torch.abs(pred_params - params).mean()

        total_loss += loss.item()
        total_mae += mae.item()
        num_batches += 1

    avg_loss = total_loss / num_batches
    avg_mae = total_mae / num_batches

    return {
        'val_loss': avg_loss,
        'val_mae': avg_mae,
    }


def save_checkpoint(
    model: nn.Module,
    optimizer: optim.Optimizer,
    epoch: int,
    metrics: Dict,
    config: Dict,
    filepath: str,
):
    """Save a training checkpoint."""
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'metrics': metrics,
        'config': config,
        'param_names': CNN_PARAMS,
    }
    torch.save(checkpoint, filepath)
    print(f"  Saved checkpoint: {filepath}")


def load_checkpoint(
    filepath: str,
    model: nn.Module,
    optimizer: Optional[optim.Optimizer] = None,
) -> Tuple[int, Dict]:
    """Load a training checkpoint."""
    checkpoint = torch.load(filepath, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])

    if optimizer is not None:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    return checkpoint['epoch'], checkpoint.get('metrics', {})


# =============================================================================
# MAIN TRAINING LOOP
# =============================================================================

def train(config: Dict, resume_path: Optional[str] = None):
    """Main training function."""

    print("=" * 60)
    print("SERUM CNN AUDIO ENCODER - Training")
    print("=" * 60)

    # Setup
    device = get_device()
    print(f"\nDevice: {device}")

    # Create checkpoint directory
    checkpoint_dir = Path(config['checkpoint_dir'])
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Create dataloaders
    print(f"\nLoading data...")
    train_loader, val_loader = get_dataloaders(
        mel_spec_dir=config['mel_spec_dir'],
        preset_json=config['preset_json'],
        batch_size=config['batch_size'],
        val_split=config['val_split'],
        num_workers=config['num_workers'],
        target_length=config['target_length'],
    )

    print(f"Train batches: {len(train_loader)}")
    print(f"Val batches: {len(val_loader)}")

    # Create model
    print(f"\nCreating model ({config['model_type']})...")
    model = create_model(config, device)
    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Output params: {NUM_CNN_PARAMS}")

    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.AdamW(
        model.parameters(),
        lr=config['learning_rate'],
        weight_decay=config['weight_decay'],
    )

    # Learning rate scheduler
    if config['scheduler'] == 'cosine':
        scheduler = optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=config['epochs'] - config['warmup_epochs'],
            eta_min=config['min_lr'],
        )
    else:
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=0.5,
            patience=5,
        )

    # Resume from checkpoint
    start_epoch = 1
    best_val_loss = float('inf')

    if resume_path:
        print(f"\nResuming from: {resume_path}")
        start_epoch, metrics = load_checkpoint(resume_path, model, optimizer)
        start_epoch += 1
        best_val_loss = metrics.get('val_loss', float('inf'))
        print(f"Resuming from epoch {start_epoch}, best val_loss: {best_val_loss:.4f}")

    # Training history
    history = {
        'train_loss': [],
        'val_loss': [],
        'val_mae': [],
        'lr': [],
    }

    # Save config
    config_path = checkpoint_dir / 'config.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n{'='*60}")
    print("Starting training...")
    print(f"{'='*60}\n")

    start_time = time.time()

    for epoch in range(start_epoch, config['epochs'] + 1):
        epoch_start = time.time()

        # Train
        train_metrics = train_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )

        # Validate
        val_metrics = validate(
            model, val_loader, criterion, device, epoch
        )

        # Get current LR
        current_lr = optimizer.param_groups[0]['lr']

        # Update scheduler
        if config['scheduler'] == 'plateau':
            scheduler.step(val_metrics['val_loss'])
        elif epoch > config['warmup_epochs']:
            scheduler.step()

        # Update history
        history['train_loss'].append(train_metrics['train_loss'])
        history['val_loss'].append(val_metrics['val_loss'])
        history['val_mae'].append(val_metrics['val_mae'])
        history['lr'].append(current_lr)

        # Print epoch summary
        epoch_time = time.time() - epoch_start
        print(f"Epoch {epoch:3d}/{config['epochs']} | "
              f"Train Loss: {train_metrics['train_loss']:.4f} | "
              f"Val Loss: {val_metrics['val_loss']:.4f} | "
              f"Val MAE: {val_metrics['val_mae']:.4f} | "
              f"LR: {current_lr:.2e} | "
              f"Time: {epoch_time:.1f}s")

        # Save best model
        if val_metrics['val_loss'] < best_val_loss:
            best_val_loss = val_metrics['val_loss']
            save_checkpoint(
                model, optimizer, epoch,
                {**train_metrics, **val_metrics},
                config,
                checkpoint_dir / 'best_model.pt',
            )

        # Save periodic checkpoint
        if epoch % config['save_every'] == 0:
            save_checkpoint(
                model, optimizer, epoch,
                {**train_metrics, **val_metrics},
                config,
                checkpoint_dir / f'checkpoint_epoch_{epoch}.pt',
            )

    # Training complete
    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Training complete!")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Best val loss: {best_val_loss:.4f}")
    print(f"{'='*60}")

    # Save final model
    save_checkpoint(
        model, optimizer, config['epochs'],
        {'train_loss': history['train_loss'][-1], 'val_loss': history['val_loss'][-1]},
        config,
        checkpoint_dir / 'final_model.pt',
    )

    # Save training history
    history_path = checkpoint_dir / 'training_history.json'
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"Saved training history: {history_path}")

    return model, history


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Train Serum Audio Encoder CNN")

    # Training args
    parser.add_argument('--epochs', type=int, default=DEFAULT_CONFIG['epochs'],
                        help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=DEFAULT_CONFIG['batch_size'],
                        help='Batch size')
    parser.add_argument('--lr', type=float, default=DEFAULT_CONFIG['learning_rate'],
                        help='Learning rate')

    # Model args
    parser.add_argument('--model', type=str, default='full',
                        choices=['full', 'light'],
                        help='Model type (full or light)')

    # Data args
    parser.add_argument('--mel-dir', type=str, default=DEFAULT_CONFIG['mel_spec_dir'],
                        help='Mel spectrogram directory')
    parser.add_argument('--preset-json', type=str, default=DEFAULT_CONFIG['preset_json'],
                        help='Preset database JSON path')

    # Checkpoint args
    parser.add_argument('--resume', type=str, default=None,
                        help='Path to checkpoint to resume from')
    parser.add_argument('--checkpoint-dir', type=str, default=DEFAULT_CONFIG['checkpoint_dir'],
                        help='Directory to save checkpoints')

    # Test mode
    parser.add_argument('--test', action='store_true',
                        help='Quick test run (1 epoch, small batch)')

    # Multi-channel features
    parser.add_argument('--multi-channel', action='store_true',
                        help='Use 4-channel features (mel + rms + centroid + flatness)')

    args = parser.parse_args()

    # Build config
    config = DEFAULT_CONFIG.copy()
    config['epochs'] = args.epochs
    config['batch_size'] = args.batch_size
    config['learning_rate'] = args.lr
    config['model_type'] = args.model
    config['mel_spec_dir'] = args.mel_dir
    config['preset_json'] = args.preset_json
    config['checkpoint_dir'] = args.checkpoint_dir
    config['in_channels'] = 4 if args.multi_channel else 1

    # Test mode overrides
    if args.test:
        config['epochs'] = 1
        config['batch_size'] = 8
        config['num_workers'] = 0  # Easier debugging
        print("TEST MODE: 1 epoch, batch_size=8")

    # Multi-channel info
    if args.multi_channel:
        print("MULTI-CHANNEL MODE: 4 channels (mel + rms + centroid + flatness)")

    # Run training
    train(config, resume_path=args.resume)


if __name__ == '__main__':
    main()
