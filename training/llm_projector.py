#!/usr/bin/env python3
"""
LLM Projector - Bridge MixGraph-CLAP embeddings to Qwen3-4B
============================================================

Projects audio embeddings from MixGraph-CLAP (512d) into Qwen3-4B's input space (2560d).

Architecture follows LLaVA-style approach:
1. Audio embeddings from MixGraph-CLAP encoder
2. Trainable projection layer (MLP or Linear)
3. Special audio tokens injected into LLM context

Usage:
    from llm_projector import AudioProjector, MixAudioLLM

    projector = AudioProjector(in_dim=512, out_dim=2560)
    llm = MixAudioLLM(projector, "Qwen/Qwen3-4B")

    # Encode mix and generate response
    response = llm.generate_with_audio(audio_embeddings, "Why is the bass muddy?")
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Optional, Tuple, Union
import numpy as np


# =============================================================================
# PROJECTION LAYERS
# =============================================================================

class LinearProjector(nn.Module):
    """
    Simple linear projection from audio embedding space to LLM space.
    Fast and efficient, good baseline.
    """
    def __init__(self, in_dim: int = 512, out_dim: int = 2560):
        super().__init__()
        self.proj = nn.Linear(in_dim, out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.proj(x)


class MLPProjector(nn.Module):
    """
    Two-layer MLP projection with GELU activation.
    Better capacity for learning complex mappings (LLaVA default).
    """
    def __init__(self, in_dim: int = 512, out_dim: int = 2560, hidden_dim: int = 1024):
        super().__init__()
        self.proj = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, out_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.proj(x)


class QFormerProjector(nn.Module):
    """
    Q-Former style projection with learnable queries.
    More expressive but requires more training data.

    Inspired by BLIP-2: Uses learnable query tokens that attend to audio embeddings,
    then projects the queries to LLM space.
    """
    def __init__(
        self,
        in_dim: int = 512,
        out_dim: int = 2560,
        n_queries: int = 8,
        n_heads: int = 8,
        n_layers: int = 2,
    ):
        super().__init__()

        self.n_queries = n_queries

        # Learnable query tokens
        self.queries = nn.Parameter(torch.randn(n_queries, in_dim))

        # Cross-attention layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=in_dim,
            nhead=n_heads,
            dim_feedforward=in_dim * 4,
            activation='gelu',
            batch_first=True,
        )
        self.cross_attn = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)

        # Project to LLM dimension
        self.proj = nn.Linear(in_dim, out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Audio embeddings [batch, n_tracks, in_dim] or [n_tracks, in_dim]

        Returns:
            LLM-ready embeddings [batch, n_queries, out_dim]
        """
        # Handle unbatched input
        if x.dim() == 2:
            x = x.unsqueeze(0)

        batch_size = x.shape[0]

        # Expand queries for batch
        queries = self.queries.unsqueeze(0).expand(batch_size, -1, -1)

        # Concatenate queries with audio embeddings for self-attention
        # (Simplified cross-attention via self-attention mask could be added)
        combined = torch.cat([queries, x], dim=1)  # [batch, n_queries + n_tracks, in_dim]

        # Self-attention
        attended = self.cross_attn(combined)

        # Take only query outputs
        query_outputs = attended[:, :self.n_queries, :]  # [batch, n_queries, in_dim]

        # Project to LLM dimension
        return self.proj(query_outputs)


class AudioProjector(nn.Module):
    """
    Main audio projector with configurable architecture.
    """
    def __init__(
        self,
        in_dim: int = 512,
        out_dim: int = 2560,
        projector_type: str = "mlp",  # "linear", "mlp", "qformer"
        hidden_dim: int = 1024,
        n_queries: int = 8,
    ):
        super().__init__()

        self.projector_type = projector_type

        if projector_type == "linear":
            self.projector = LinearProjector(in_dim, out_dim)
        elif projector_type == "mlp":
            self.projector = MLPProjector(in_dim, out_dim, hidden_dim)
        elif projector_type == "qformer":
            self.projector = QFormerProjector(in_dim, out_dim, n_queries)
        else:
            raise ValueError(f"Unknown projector type: {projector_type}")

        # Track dimensions
        self.in_dim = in_dim
        self.out_dim = out_dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.projector(x)

    @property
    def n_params(self) -> int:
        """Count trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# =============================================================================
# AUDIO TOKEN INJECTION
# =============================================================================

class AudioTokenizer:
    """
    Handles special token management for audio embeddings in LLM context.

    Special tokens:
    - <audio> / </audio>: Wraps audio embeddings
    - <track_N>: Individual track markers
    - <mix>: Mix-level embedding marker
    """

    AUDIO_START = "<audio>"
    AUDIO_END = "</audio>"
    TRACK_PREFIX = "<track_"
    MIX_TOKEN = "<mix>"

    def __init__(self, tokenizer=None):
        self.tokenizer = tokenizer
        self.special_tokens = [
            self.AUDIO_START,
            self.AUDIO_END,
            self.MIX_TOKEN,
        ]
        # Add track tokens (support up to 16 tracks)
        for i in range(16):
            self.special_tokens.append(f"<track_{i}>")

    def add_special_tokens(self, tokenizer):
        """Add special tokens to tokenizer."""
        tokenizer.add_special_tokens({
            'additional_special_tokens': self.special_tokens
        })
        return tokenizer

    def format_audio_context(
        self,
        track_names: List[str],
        include_mix: bool = True,
    ) -> str:
        """
        Format text context describing the audio embeddings.

        Returns template like:
        "<audio><track_0> (Kick) <track_1> (Bass) <mix></audio>"
        """
        parts = [self.AUDIO_START]

        for i, name in enumerate(track_names):
            parts.append(f"<track_{i}> ({name})")

        if include_mix:
            parts.append(self.MIX_TOKEN)

        parts.append(self.AUDIO_END)

        return " ".join(parts)


# =============================================================================
# AUDIO-LLM INTEGRATION (Placeholder for full implementation)
# =============================================================================

class MixAudioLLM(nn.Module):
    """
    Full audio-LLM integration combining:
    1. MixGraph-CLAP encoder
    2. Audio projector
    3. Qwen3-4B LLM

    This is a placeholder for the full implementation.
    Full implementation would require:
    - Loading Qwen3-4B with MLX
    - Modifying forward pass to inject audio embeddings
    - Managing special tokens
    """

    def __init__(
        self,
        projector: AudioProjector,
        llm_path: str = "Qwen/Qwen3-4B",
        device: str = None,
    ):
        super().__init__()

        self.projector = projector
        self.llm_path = llm_path
        self.audio_tokenizer = AudioTokenizer()

        # Device setup
        if device is None:
            if torch.backends.mps.is_available():
                self.device = torch.device("mps")
            elif torch.cuda.is_available():
                self.device = torch.device("cuda")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)

        self.projector.to(self.device)

        # LLM would be loaded here in full implementation
        self.llm = None
        self.tokenizer = None

    def prepare_audio_embeddings(
        self,
        track_embeddings: torch.Tensor,
        mix_embedding: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Project audio embeddings to LLM space.

        Args:
            track_embeddings: [N, 512] per-track embeddings from MixGraph-CLAP
            mix_embedding: Optional [512] mix-level embedding

        Returns:
            Projected embeddings ready for LLM input [N+1, 2560]
        """
        # Project track embeddings
        projected_tracks = self.projector(track_embeddings.to(self.device))

        # If mix embedding provided, project and append
        if mix_embedding is not None:
            projected_mix = self.projector(mix_embedding.unsqueeze(0).to(self.device))
            projected = torch.cat([projected_tracks, projected_mix], dim=0)
        else:
            projected = projected_tracks

        return projected

    def generate_with_audio(
        self,
        track_embeddings: torch.Tensor,
        question: str,
        track_names: List[str],
        mix_embedding: Optional[torch.Tensor] = None,
        max_new_tokens: int = 256,
    ) -> str:
        """
        Generate a response given audio context and a question.

        This is a placeholder - actual generation requires full LLM integration.
        """
        # Project audio embeddings
        audio_embeds = self.prepare_audio_embeddings(track_embeddings, mix_embedding)

        # Format prompt with audio context
        audio_context = self.audio_tokenizer.format_audio_context(track_names)
        prompt = f"{audio_context}\n\nUser: {question}\nAssistant:"

        # Placeholder response
        # In full implementation, this would:
        # 1. Tokenize the prompt
        # 2. Insert audio embeddings at special token positions
        # 3. Run LLM forward pass
        # 4. Decode output tokens

        return f"[PLACEHOLDER] Would analyze {len(track_names)} tracks and respond to: {question}"


# =============================================================================
# TESTING
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("LLM PROJECTOR - Testing")
    print("=" * 60)

    # Test different projector types
    projector_configs = [
        ("linear", {}),
        ("mlp", {"hidden_dim": 1024}),
        ("qformer", {"n_queries": 8}),
    ]

    # Simulate MixGraph-CLAP output
    batch_size = 1
    n_tracks = 4
    clap_dim = 512
    qwen_dim = 2560

    fake_track_embeddings = torch.randn(n_tracks, clap_dim)
    fake_mix_embedding = torch.randn(clap_dim)

    print(f"\nInput: {n_tracks} tracks x {clap_dim}d = {fake_track_embeddings.shape}")
    print(f"Target output: {n_tracks} tracks x {qwen_dim}d\n")

    for proj_type, kwargs in projector_configs:
        print(f"--- {proj_type.upper()} Projector ---")

        projector = AudioProjector(
            in_dim=clap_dim,
            out_dim=qwen_dim,
            projector_type=proj_type,
            **kwargs
        )

        # Forward pass
        with torch.no_grad():
            output = projector(fake_track_embeddings)

        print(f"  Output shape: {output.shape}")
        print(f"  Parameters: {projector.n_params:,}")
        print()

    # Test full MixAudioLLM pipeline (placeholder)
    print("--- MixAudioLLM Integration ---")

    projector = AudioProjector(in_dim=clap_dim, out_dim=qwen_dim, projector_type="mlp")
    llm = MixAudioLLM(projector)

    track_names = ["Kick", "Bass", "Synth", "HiHat"]
    question = "Why is the bass masking the kick?"

    response = llm.generate_with_audio(
        fake_track_embeddings,
        question,
        track_names,
        mix_embedding=fake_mix_embedding,
    )

    print(f"  Question: {question}")
    print(f"  Response: {response}")

    print("\n" + "=" * 60)
    print("LLM Projector test complete!")
    print("=" * 60)
