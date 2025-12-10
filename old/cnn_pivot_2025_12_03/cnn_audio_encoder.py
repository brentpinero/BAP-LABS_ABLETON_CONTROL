#!/usr/bin/env python3
"""
CNN Audio Encoder for Serum Parameter Prediction
=================================================
A convolutional neural network that:
1. Takes mel-spectrograms as input
2. Produces 512-dim audio embeddings (for LLM input)
3. Optionally predicts 301 Serum parameters directly (for supervised training)

Architecture based on VGGish/PANNs audio classification networks,
adapted for synthesizer parameter prediction.

Usage:
    # Test model architecture
    python cnn_audio_encoder.py --test

    # Train model
    python cnn_audio_encoder.py --train --epochs 50 --batch-size 32
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Dict, List
import json
from pathlib import Path

# Import centralized param definitions
from serum_params import CNN_PARAMS, NUM_CNN_PARAMS


# =============================================================================
# PARAMETER CONFIGURATION
# =============================================================================
# Using data-driven CNN_PARAMS (30 high-variance parameters)
# See serum_params.py for full list and methodology

NUM_PARAMS = NUM_CNN_PARAMS  # 30 (was 301)


# =============================================================================
# CONVOLUTIONAL BLOCKS
# =============================================================================

class ConvBlock(nn.Module):
    """
    Standard conv block: Conv2d -> BatchNorm -> ReLU -> MaxPool
    """
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        pool_size: int = 2
    ):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels, out_channels,
            kernel_size=kernel_size,
            padding=kernel_size // 2  # Same padding
        )
        self.bn = nn.BatchNorm2d(out_channels)
        self.pool = nn.MaxPool2d(pool_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv(x)
        x = self.bn(x)
        x = F.relu(x)
        x = self.pool(x)
        return x


class ResidualBlock(nn.Module):
    """
    Residual block with skip connection for deeper networks.
    """
    def __init__(self, channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))
        x = x + residual  # Skip connection
        x = F.relu(x)
        return x


# =============================================================================
# MAIN CNN ARCHITECTURE
# =============================================================================

class SerumAudioEncoder(nn.Module):
    """
    CNN encoder for Serum audio analysis.

    Architecture:
    - Input: Multi-channel features [batch, C, 128, 302] where C=1 or C=4
      - 1-channel: mel-spectrogram only
      - 4-channel: mel + RMS envelope + spectral centroid + spectral flatness
    - Conv blocks progressively reduce spatial dimensions
    - Global average pooling produces fixed-size embedding
    - Two output heads: embedding (512-dim) and optional parameters (30-dim)

    Design rationale:
    - VGGish-inspired progressive downsampling
    - Batch normalization for stable training
    - Global pooling handles variable-length audio
    - Separate heads allow embedding-only or param prediction training
    """

    def __init__(
        self,
        n_mels: int = 128,
        embedding_dim: int = 512,
        num_params: int = NUM_PARAMS,
        use_residual: bool = True,
        dropout: float = 0.3,
        in_channels: int = 1  # 1 for mel-only, 4 for multi-channel
    ):
        super().__init__()

        self.n_mels = n_mels
        self.embedding_dim = embedding_dim
        self.num_params = num_params
        self.in_channels = in_channels

        # Convolutional feature extractor
        # Input: [B, C, 128, T] where C = in_channels, T = time frames (~302 for 2.5s audio)
        self.conv_blocks = nn.Sequential(
            # Block 1: in_channels -> 32 channels, 128x302 -> 64x151
            ConvBlock(in_channels, 32, kernel_size=3, pool_size=2),

            # Block 2: 32 -> 64 channels, 64x151 -> 32x75
            ConvBlock(32, 64, kernel_size=3, pool_size=2),

            # Block 3: 64 -> 128 channels, 32x75 -> 16x37
            ConvBlock(64, 128, kernel_size=3, pool_size=2),

            # Block 4: 128 -> 256 channels, 16x37 -> 8x18
            ConvBlock(128, 256, kernel_size=3, pool_size=2),

            # Block 5: 256 -> 512 channels, 8x18 -> 4x9
            ConvBlock(256, 512, kernel_size=3, pool_size=2),
        )

        # Optional residual blocks for more capacity
        self.use_residual = use_residual
        if use_residual:
            self.residual_blocks = nn.Sequential(
                ResidualBlock(512),
                ResidualBlock(512),
            )

        # Global average pooling: [B, 512, H, W] -> [B, 512]
        self.global_pool = nn.AdaptiveAvgPool2d(1)

        # Embedding projection head
        self.embedding_head = nn.Sequential(
            nn.Linear(512, embedding_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(embedding_dim, embedding_dim),
        )

        # Parameter prediction head (optional, for supervised training)
        self.param_head = nn.Sequential(
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, num_params),
            nn.Sigmoid(),  # Parameters are normalized to [0, 1]
        )

    def forward(
        self,
        x: torch.Tensor,
        return_params: bool = True
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass.

        Args:
            x: Audio features tensor [batch, C, n_mels, time] where C = in_channels
               - If C=1: mel-spectrogram only
               - If C=4: mel + RMS + centroid + flatness
            return_params: Whether to also predict parameters

        Returns:
            dict with:
                'embedding': [batch, embedding_dim] audio embedding
                'params': [batch, num_params] predicted parameters (if return_params)
                'features': [batch, 512] raw CNN features (before heads)
        """
        # Handle input shape
        if x.dim() == 3:
            x = x.unsqueeze(1)  # [B, H, W] -> [B, 1, H, W] for single-channel

        # Validate channel count matches model expectation
        if x.shape[1] != self.in_channels:
            raise ValueError(f"Expected {self.in_channels} channels, got {x.shape[1]}")

        # Conv feature extraction
        x = self.conv_blocks(x)

        # Optional residual processing
        if self.use_residual:
            x = self.residual_blocks(x)

        # Global pooling
        x = self.global_pool(x)
        features = x.view(x.size(0), -1)  # [B, 512]

        # Embedding head
        embedding = self.embedding_head(features)

        result = {
            'embedding': embedding,
            'features': features,
        }

        # Optional parameter prediction
        if return_params:
            params = self.param_head(features)
            result['params'] = params

        return result

    def get_embedding(self, x: torch.Tensor) -> torch.Tensor:
        """Convenience method to get just the embedding."""
        return self.forward(x, return_params=False)['embedding']

    def count_parameters(self) -> int:
        """Count total trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# =============================================================================
# LIGHTWEIGHT VARIANT (for fast inference)
# =============================================================================

class SerumAudioEncoderLight(nn.Module):
    """
    Lightweight CNN for fast inference (<10ms target on M4 Max).

    Fewer channels, no residual blocks, smaller embedding.
    """

    def __init__(
        self,
        n_mels: int = 128,
        embedding_dim: int = 256,
        num_params: int = NUM_PARAMS,
        in_channels: int = 1  # 1 for mel-only, 4 for multi-channel
    ):
        super().__init__()

        self.in_channels = in_channels

        self.conv_blocks = nn.Sequential(
            # Fewer channels, same structure
            ConvBlock(in_channels, 16, kernel_size=3, pool_size=2),
            ConvBlock(16, 32, kernel_size=3, pool_size=2),
            ConvBlock(32, 64, kernel_size=3, pool_size=2),
            ConvBlock(64, 128, kernel_size=3, pool_size=2),
            ConvBlock(128, 256, kernel_size=3, pool_size=2),
        )

        self.global_pool = nn.AdaptiveAvgPool2d(1)

        self.embedding_head = nn.Sequential(
            nn.Linear(256, embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, embedding_dim),
        )

        self.param_head = nn.Sequential(
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, num_params),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor, return_params: bool = True) -> Dict[str, torch.Tensor]:
        if x.dim() == 3:
            x = x.unsqueeze(1)

        if x.shape[1] != self.in_channels:
            raise ValueError(f"Expected {self.in_channels} channels, got {x.shape[1]}")

        x = self.conv_blocks(x)
        x = self.global_pool(x)
        features = x.view(x.size(0), -1)

        embedding = self.embedding_head(features)

        result = {'embedding': embedding, 'features': features}
        if return_params:
            result['params'] = self.param_head(features)

        return result

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# =============================================================================
# TESTING / DEMO
# =============================================================================

def test_model():
    """Test model architecture and shapes."""
    import numpy as np

    print("=" * 60)
    print("SERUM AUDIO ENCODER - Architecture Test")
    print("=" * 60)

    # Create models
    model_full = SerumAudioEncoder()
    model_light = SerumAudioEncoderLight()

    print(f"\n--- Full Model ---")
    print(f"Parameters: {model_full.count_parameters():,}")
    print(f"Embedding dim: {model_full.embedding_dim}")
    print(f"Num output params: {model_full.num_params}")

    print(f"\n--- Lightweight Model ---")
    print(f"Parameters: {model_light.count_parameters():,}")

    # Test with sample input (simulating 128 mels x 302 time frames)
    batch_size = 4
    n_mels = 128
    time_frames = 302  # ~2.5s at 44.1kHz with hop_length=512

    x = torch.randn(batch_size, 1, n_mels, time_frames)
    print(f"\n--- Forward Pass Test ---")
    print(f"Input shape: {x.shape}")

    # Test full model
    with torch.no_grad():
        output = model_full(x)
        print(f"\nFull model output:")
        print(f"  embedding: {output['embedding'].shape}")
        print(f"  features: {output['features'].shape}")
        print(f"  params: {output['params'].shape}")
        print(f"  param range: [{output['params'].min():.3f}, {output['params'].max():.3f}]")

        # Test light model
        output_light = model_light(x)
        print(f"\nLight model output:")
        print(f"  embedding: {output_light['embedding'].shape}")
        print(f"  params: {output_light['params'].shape}")

    # Benchmark inference speed
    print(f"\n--- Inference Speed Benchmark ---")
    import time

    # Check for MPS (Apple Silicon)
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print(f"Using: Apple MPS (Metal)")
    else:
        device = torch.device("cpu")
        print(f"Using: CPU")

    model_full = model_full.to(device)
    model_light = model_light.to(device)
    model_full.eval()
    model_light.eval()

    x_device = x.to(device)

    # Warmup
    for _ in range(10):
        with torch.no_grad():
            _ = model_full(x_device, return_params=False)

    # Benchmark full model
    n_runs = 100
    start = time.time()
    for _ in range(n_runs):
        with torch.no_grad():
            _ = model_full(x_device, return_params=False)
    if device.type == "mps":
        torch.mps.synchronize()
    elapsed = (time.time() - start) / n_runs * 1000

    print(f"Full model: {elapsed:.2f}ms per batch (batch_size={batch_size})")
    print(f"Full model: {elapsed/batch_size:.2f}ms per sample")

    # Benchmark light model
    start = time.time()
    for _ in range(n_runs):
        with torch.no_grad():
            _ = model_light(x_device, return_params=False)
    if device.type == "mps":
        torch.mps.synchronize()
    elapsed = (time.time() - start) / n_runs * 1000

    print(f"Light model: {elapsed:.2f}ms per batch (batch_size={batch_size})")
    print(f"Light model: {elapsed/batch_size:.2f}ms per sample")

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Serum Audio Encoder CNN")
    parser.add_argument('--test', action='store_true', help='Run architecture tests')

    args = parser.parse_args()

    if args.test:
        test_model()
    else:
        # Default: show model summary
        model = SerumAudioEncoder()
        print(f"SerumAudioEncoder")
        print(f"  Parameters: {model.count_parameters():,}")
        print(f"  Input: [batch, 1, 128, T] mel-spectrogram")
        print(f"  Output embedding: [batch, {model.embedding_dim}]")
        print(f"  Output params: [batch, {model.num_params}]")
        print(f"\nRun with --test for full architecture validation")
