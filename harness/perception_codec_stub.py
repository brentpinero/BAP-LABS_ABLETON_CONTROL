"""
perception_codec_stub.py — interface stubs for the lanes deferred to the backbone.

The chosen backbone (MiniCPM-o 4.5) brings its own native vision + audio encoders,
so we do NOT build a vision encoder or audio codec here. These Protocols pin the
integration surface now; the bodies are wired after Phase 0 (standing MiniCPM-o up
on MLX), when its real ingestion clock/token format is known.

  - MixProjector: our fixed-shape mix+focus frame vector -> backbone embedding tokens
    (the trained cross-attention/projector; future FrameEmitter.on_frame call site).
  - ScreenSource: Ableton-window frames -> MiniCPM-o's NATIVE video path (its SigLip2
    owns the encoder — nothing to build here but capture + hand-off).
  - StemSource:  44.1k stems -> MiniCPM-o's NATIVE audio path (its Whisper owns it).
"""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable


@runtime_checkable
class MixProjector(Protocol):
    """Project one perception Frame.to_vector() (length D) into the backbone's
    embedding space (d_model). Trained later against MiniCPM-o; the emitter's
    on_frame callback is the call site."""
    d_model: int

    def encode(self, frame_vec: Sequence[float]): ...            # (D,) -> (d_model,)
    def encode_batch(self, frames: Sequence[Sequence[float]]): ...  # (T,D) -> (T,d_model)


class ZeroProjector:
    """Placeholder projector — asserts vector length, returns zeros. Lets the
    on_frame plumbing be wired before the real adapter exists."""

    def __init__(self, d_model: int = 768, expected_D: int | None = None):
        self.d_model = d_model
        self._D = expected_D

    def encode(self, frame_vec):
        if self._D is not None and len(frame_vec) != self._D:
            raise ValueError(f"frame vector len {len(frame_vec)} != expected {self._D}")
        return [0.0] * self.d_model

    def encode_batch(self, frames):
        return [self.encode(f) for f in frames]


@runtime_checkable
class ScreenSource(Protocol):
    """Ableton-window frames -> MiniCPM-o's native video input. Capture is wired
    post-Phase-0; there is NO encoder here (the backbone's SigLip2 owns it)."""
    fps: float

    def capture(self): ...          # -> image frame (backbone-native format)
    def stream(self): ...           # -> iterator/async of frames


@runtime_checkable
class StemSource(Protocol):
    """44.1k stems -> MiniCPM-o's native audio input. Wired post-Phase-0; there is
    NO codec here (the backbone's Whisper owns it)."""
    sr: int

    def read_block(self, role: str): ...     # -> pcm block for a role
    def stream(self, role: str): ...          # -> iterator/async of pcm blocks


def _not_built(what: str):
    raise NotImplementedError(
        f"{what}: deferred to MiniCPM-o's native path — wire after Phase 0 "
        "(backbone stood up on MLX; ingestion clock/format known).")
