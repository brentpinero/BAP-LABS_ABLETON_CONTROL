#!/usr/bin/env python3
"""
Audio-to-LLM Projector Module
==============================
MLP projection layer that maps CNN audio embeddings into LLM token space.

Architecture inspired by:
- Qwen2-Audio: avg pooling + 2-layer MLP projection
- LLaVA 1.5: MLP vision-language connector
- jonflynng/qwen2-audio-finetune: LoRA configuration patterns

This module bridges our lightweight CNN audio encoder with Qwen3-4B,
enabling the LLM to "understand" audio embeddings as if they were tokens.

Usage:
    from audio_llm_projector import AudioToLLMProjector, MultiTrackProjector

    # Single track
    projector = AudioToLLMProjector(cnn_dim=512, llm_dim=2048)
    llm_tokens = projector(cnn_embedding)  # [batch, 2048]

    # Multi-track (our use case)
    multi_proj = MultiTrackProjector(n_tracks=4, cnn_dim=512, llm_dim=2048)
    llm_tokens = multi_proj(track_embs, master_emb)  # [batch, n_tracks+1, 2048]
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, List, Dict, Tuple
import json
from pathlib import Path


# =============================================================================
# CORE PROJECTOR (Qwen2-Audio style)
# =============================================================================

class AudioToLLMProjector(nn.Module):
    """
    Projects CNN audio embeddings into LLM embedding space.

    Architecture (from Qwen2-Audio):
    - Optional temporal pooling (for streaming chunks)
    - 2-layer MLP with GELU activation
    - Layer normalization for stability

    This is the core building block - maps [batch, cnn_dim] -> [batch, llm_dim]
    """

    def __init__(
        self,
        cnn_dim: int = 512,
        llm_dim: int = 2048,  # Qwen3-4B hidden dim (verify this)
        hidden_dim: Optional[int] = None,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.cnn_dim = cnn_dim
        self.llm_dim = llm_dim
        hidden_dim = hidden_dim or llm_dim  # Default: project directly to llm_dim

        # 2-layer MLP projection (Qwen2-Audio style)
        self.proj = nn.Sequential(
            nn.Linear(cnn_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, llm_dim),
            nn.LayerNorm(llm_dim),
        )

        # Initialize with small weights for stable training
        self._init_weights()

    def _init_weights(self):
        """Initialize projection weights with small values."""
        for module in self.proj.modules():
            if isinstance(module, nn.Linear):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, audio_emb: torch.Tensor) -> torch.Tensor:
        """
        Project audio embedding to LLM space.

        Args:
            audio_emb: [batch, cnn_dim] or [batch, seq_len, cnn_dim]

        Returns:
            [batch, llm_dim] or [batch, seq_len, llm_dim]
        """
        return self.proj(audio_emb)


# =============================================================================
# MULTI-TRACK PROJECTOR (Our Innovation)
# =============================================================================

class MultiTrackProjector(nn.Module):
    """
    Projects multiple audio track embeddings into LLM space.

    Key innovation: Track identifier embeddings allow the LLM to know
    which audio stream each embedding came from (bass, lead, master, etc.)

    Architecture:
    - Shared AudioToLLMProjector for all tracks (parameter efficient)
    - Learnable track embeddings (like positional embeddings)
    - Optional cross-track attention (disabled by default per user feedback)
    """

    # Track type identifiers
    TRACK_TYPES = {
        'bass': 0,
        'lead': 1,
        'pad': 2,
        'drums': 3,
        'fx': 4,
        'vocals': 5,
        'other': 6,
        'master': 7,  # Always last
    }

    def __init__(
        self,
        n_tracks: int = 8,
        cnn_dim: int = 512,
        llm_dim: int = 2048,
        dropout: float = 0.1,
        use_track_attention: bool = False,  # Disabled per user feedback
    ):
        super().__init__()

        self.n_tracks = n_tracks
        self.cnn_dim = cnn_dim
        self.llm_dim = llm_dim

        # Shared projector for all tracks (efficient)
        self.projector = AudioToLLMProjector(
            cnn_dim=cnn_dim,
            llm_dim=llm_dim,
            dropout=dropout,
        )

        # Track identifier embeddings
        # These tell the LLM which track each embedding came from
        self.track_embeddings = nn.Embedding(n_tracks, llm_dim)
        nn.init.normal_(self.track_embeddings.weight, mean=0.0, std=0.02)

        # Track type embeddings (semantic: bass, lead, etc.)
        self.track_type_embeddings = nn.Embedding(len(self.TRACK_TYPES), llm_dim)
        nn.init.normal_(self.track_type_embeddings.weight, mean=0.0, std=0.02)

        # Optional cross-track attention (for learning inter-track relationships)
        self.use_track_attention = use_track_attention
        if use_track_attention:
            self.cross_attention = nn.MultiheadAttention(
                embed_dim=llm_dim,
                num_heads=8,
                dropout=dropout,
                batch_first=True,
            )

    def forward(
        self,
        track_embeddings: torch.Tensor,
        track_types: Optional[torch.Tensor] = None,
        track_ids: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Project multiple track embeddings to LLM space.

        Args:
            track_embeddings: [batch, n_tracks, cnn_dim] - CNN embeddings per track
            track_types: [batch, n_tracks] - optional track type IDs (0=bass, 1=lead, etc.)
            track_ids: [batch, n_tracks] - optional track position IDs (0, 1, 2, ...)

        Returns:
            [batch, n_tracks, llm_dim] - ready to concatenate with text tokens
        """
        batch_size, n_tracks, _ = track_embeddings.shape
        device = track_embeddings.device

        # Project all tracks through shared MLP
        # Reshape: [batch, n_tracks, cnn_dim] -> [batch * n_tracks, cnn_dim]
        flat_emb = track_embeddings.view(-1, self.cnn_dim)
        projected = self.projector(flat_emb)  # [batch * n_tracks, llm_dim]
        projected = projected.view(batch_size, n_tracks, self.llm_dim)

        # Add track position embeddings
        if track_ids is None:
            track_ids = torch.arange(n_tracks, device=device).unsqueeze(0).expand(batch_size, -1)
        pos_emb = self.track_embeddings(track_ids)  # [batch, n_tracks, llm_dim]
        projected = projected + pos_emb

        # Add track type embeddings if provided
        if track_types is not None:
            type_emb = self.track_type_embeddings(track_types)  # [batch, n_tracks, llm_dim]
            projected = projected + type_emb

        # Optional cross-track attention
        if self.use_track_attention:
            attended, _ = self.cross_attention(projected, projected, projected)
            projected = projected + attended  # Residual connection

        return projected

    def get_track_type_id(self, track_name: str) -> int:
        """Get track type ID from name."""
        track_name_lower = track_name.lower()
        for type_name, type_id in self.TRACK_TYPES.items():
            if type_name in track_name_lower:
                return type_id
        return self.TRACK_TYPES['other']


# =============================================================================
# STREAMING PROJECTOR (For real-time inference)
# =============================================================================

class StreamingAudioProjector(nn.Module):
    """
    Streaming-capable projector for real-time audio processing.

    Maintains a buffer of recent audio embeddings and produces
    temporally-smoothed projections suitable for continuous inference.
    """

    def __init__(
        self,
        cnn_dim: int = 512,
        llm_dim: int = 2048,
        buffer_size: int = 10,  # Number of chunks to buffer (~1s at 100ms chunks)
        temporal_pooling: str = 'mean',  # 'mean', 'max', or 'attention'
    ):
        super().__init__()

        self.buffer_size = buffer_size
        self.temporal_pooling = temporal_pooling

        # Core projector
        self.projector = AudioToLLMProjector(cnn_dim, llm_dim)

        # Temporal attention for weighted pooling
        if temporal_pooling == 'attention':
            self.temporal_attn = nn.Sequential(
                nn.Linear(llm_dim, llm_dim // 4),
                nn.Tanh(),
                nn.Linear(llm_dim // 4, 1),
            )

        # Buffer state (not saved with model)
        self.register_buffer('embedding_buffer', torch.zeros(buffer_size, llm_dim))
        self.register_buffer('buffer_idx', torch.tensor(0))
        self.register_buffer('buffer_count', torch.tensor(0))

    def reset_buffer(self):
        """Clear the embedding buffer."""
        self.embedding_buffer.zero_()
        self.buffer_idx.zero_()
        self.buffer_count.zero_()

    def process_chunk(self, audio_emb: torch.Tensor) -> torch.Tensor:
        """
        Process a single audio chunk and return smoothed embedding.

        Args:
            audio_emb: [cnn_dim] or [1, cnn_dim] - single chunk embedding

        Returns:
            [llm_dim] - temporally smoothed projection
        """
        if audio_emb.dim() == 2:
            audio_emb = audio_emb.squeeze(0)

        # Project current chunk
        projected = self.projector(audio_emb.unsqueeze(0)).squeeze(0)  # [llm_dim]

        # Add to circular buffer
        idx = self.buffer_idx.item()
        self.embedding_buffer[idx] = projected
        self.buffer_idx = (self.buffer_idx + 1) % self.buffer_size
        self.buffer_count = torch.min(self.buffer_count + 1, torch.tensor(self.buffer_size))

        # Compute temporally pooled embedding
        count = self.buffer_count.item()
        if count == 0:
            return projected

        valid_buffer = self.embedding_buffer[:count]

        if self.temporal_pooling == 'mean':
            return valid_buffer.mean(dim=0)
        elif self.temporal_pooling == 'max':
            return valid_buffer.max(dim=0)[0]
        elif self.temporal_pooling == 'attention':
            # Attention-weighted pooling
            attn_weights = self.temporal_attn(valid_buffer)  # [count, 1]
            attn_weights = F.softmax(attn_weights, dim=0)
            return (valid_buffer * attn_weights).sum(dim=0)
        else:
            return projected


# =============================================================================
# COMPLETE AUDIO-LLM BRIDGE
# =============================================================================

class AudioLLMBridge(nn.Module):
    """
    Complete bridge between CNN audio encoder and LLM.

    This is the top-level module that:
    1. Takes raw audio or CNN embeddings
    2. Projects to LLM space
    3. Formats for LLM input (with special tokens)

    Designed to work with Qwen3-4B but adaptable to other LLMs.
    """

    # Special token IDs (will be set during initialization)
    AUDIO_START_TOKEN = "<|audio_start|>"
    AUDIO_END_TOKEN = "<|audio_end|>"
    TRACK_SEP_TOKEN = "<|track_sep|>"

    def __init__(
        self,
        cnn_encoder: Optional[nn.Module] = None,
        cnn_dim: int = 512,
        llm_dim: int = 2048,
        n_tracks: int = 8,
        use_cnn: bool = True,
    ):
        super().__init__()

        self.use_cnn = use_cnn and (cnn_encoder is not None)

        # Optional CNN encoder (can be None if using pre-computed embeddings)
        if self.use_cnn:
            self.cnn_encoder = cnn_encoder
            # Freeze CNN by default during LLM fine-tuning
            for param in self.cnn_encoder.parameters():
                param.requires_grad = False

        # Multi-track projector
        self.projector = MultiTrackProjector(
            n_tracks=n_tracks,
            cnn_dim=cnn_dim,
            llm_dim=llm_dim,
        )

    def encode_audio(self, mel_specs: torch.Tensor) -> torch.Tensor:
        """
        Encode mel-spectrograms to embeddings using CNN.

        Args:
            mel_specs: [batch, n_tracks, 1, n_mels, time]

        Returns:
            [batch, n_tracks, cnn_dim]
        """
        if not self.use_cnn:
            raise ValueError("CNN encoder not available. Pass pre-computed embeddings.")

        batch_size, n_tracks = mel_specs.shape[:2]

        # Process each track through CNN
        embeddings = []
        for t in range(n_tracks):
            track_mel = mel_specs[:, t]  # [batch, 1, n_mels, time]
            output = self.cnn_encoder(track_mel, return_params=False)
            embeddings.append(output['embedding'])  # [batch, cnn_dim]

        return torch.stack(embeddings, dim=1)  # [batch, n_tracks, cnn_dim]

    def forward(
        self,
        audio_embeddings: torch.Tensor,
        track_types: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Project audio embeddings to LLM token space.

        Args:
            audio_embeddings: [batch, n_tracks, cnn_dim]
            track_types: [batch, n_tracks] - optional track type IDs

        Returns:
            [batch, n_tracks, llm_dim] - ready to prepend to text tokens
        """
        return self.projector(audio_embeddings, track_types=track_types)

    def get_audio_token_count(self, n_tracks: int) -> int:
        """Get number of tokens the audio will occupy in the LLM context."""
        # Each track becomes one token in current implementation
        # Could be expanded to multiple tokens per track for more detail
        return n_tracks

    def save_pretrained(self, save_dir: str):
        """Save projector weights and config."""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        # Save weights
        torch.save(self.state_dict(), save_path / "audio_llm_bridge.pt")

        # Save config
        config = {
            'cnn_dim': self.projector.cnn_dim,
            'llm_dim': self.projector.llm_dim,
            'n_tracks': self.projector.n_tracks,
            'use_cnn': self.use_cnn,
        }
        with open(save_path / "config.json", 'w') as f:
            json.dump(config, f, indent=2)

        print(f"Saved AudioLLMBridge to {save_path}")

    @classmethod
    def from_pretrained(cls, load_dir: str, cnn_encoder: Optional[nn.Module] = None):
        """Load projector from saved weights."""
        load_path = Path(load_dir)

        # Load config
        with open(load_path / "config.json", 'r') as f:
            config = json.load(f)

        # Create model
        model = cls(
            cnn_encoder=cnn_encoder,
            cnn_dim=config['cnn_dim'],
            llm_dim=config['llm_dim'],
            n_tracks=config['n_tracks'],
            use_cnn=config['use_cnn'] and (cnn_encoder is not None),
        )

        # Load weights
        state_dict = torch.load(load_path / "audio_llm_bridge.pt", map_location='cpu')
        model.load_state_dict(state_dict)

        print(f"Loaded AudioLLMBridge from {load_path}")
        return model


# =============================================================================
# TESTING
# =============================================================================

def test_projector():
    """Test projector architectures."""
    print("=" * 60)
    print("AUDIO-LLM PROJECTOR TEST")
    print("=" * 60)

    batch_size = 4
    n_tracks = 4
    cnn_dim = 512
    llm_dim = 2048  # Qwen3-4B hidden dim

    # Test single projector
    print("\n--- Single Track Projector ---")
    proj = AudioToLLMProjector(cnn_dim=cnn_dim, llm_dim=llm_dim)
    single_emb = torch.randn(batch_size, cnn_dim)
    output = proj(single_emb)
    print(f"Input: {single_emb.shape}")
    print(f"Output: {output.shape}")
    print(f"Parameters: {sum(p.numel() for p in proj.parameters()):,}")

    # Test multi-track projector
    print("\n--- Multi-Track Projector ---")
    multi_proj = MultiTrackProjector(n_tracks=n_tracks, cnn_dim=cnn_dim, llm_dim=llm_dim)
    track_embs = torch.randn(batch_size, n_tracks, cnn_dim)
    track_types = torch.tensor([[0, 1, 2, 7]] * batch_size)  # bass, lead, pad, master
    output = multi_proj(track_embs, track_types=track_types)
    print(f"Input: {track_embs.shape}")
    print(f"Output: {output.shape}")
    print(f"Parameters: {sum(p.numel() for p in multi_proj.parameters()):,}")

    # Test streaming projector
    print("\n--- Streaming Projector ---")
    stream_proj = StreamingAudioProjector(cnn_dim=cnn_dim, llm_dim=llm_dim, buffer_size=5)

    # Simulate streaming chunks
    for i in range(8):
        chunk = torch.randn(cnn_dim)
        output = stream_proj.process_chunk(chunk)
        print(f"  Chunk {i+1}: output shape = {output.shape}, buffer count = {stream_proj.buffer_count.item()}")

    # Test full bridge
    print("\n--- Full Audio-LLM Bridge ---")
    bridge = AudioLLMBridge(cnn_encoder=None, cnn_dim=cnn_dim, llm_dim=llm_dim, n_tracks=n_tracks)
    track_embs = torch.randn(batch_size, n_tracks, cnn_dim)
    output = bridge(track_embs)
    print(f"Input: {track_embs.shape}")
    print(f"Output: {output.shape}")
    print(f"Total parameters: {sum(p.numel() for p in bridge.parameters()):,}")

    # Save and load test
    print("\n--- Save/Load Test ---")
    bridge.save_pretrained("/tmp/audio_llm_bridge_test")
    loaded = AudioLLMBridge.from_pretrained("/tmp/audio_llm_bridge_test")
    test_output = loaded(track_embs)
    print(f"Reload successful: output shape = {test_output.shape}")

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == '__main__':
    test_projector()
