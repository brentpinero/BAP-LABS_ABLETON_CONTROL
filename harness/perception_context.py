"""
perception_context.py — text-LLM bridge for the streaming perception layer.

The perception FrameEmitter runs in the `ears` process and writes
perception_stream.json every ~0.25s. This module (imported by the separate LLM
harness process) reads that snapshot and renders a compact `LIVE MIX (now)` block
to inject into the model's prompt each turn — so the model always sees the current
mix state + recent events WITHOUT calling a tool (push-emulation on a turn-based
harness). Stale/missing stream → empty string, so a dead daemon never breaks a turn.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from perception_config import cfg

_ROOT = Path(__file__).resolve().parent.parent


def read_perception_snapshot() -> dict | None:
    path = _ROOT / cfg("snapshot_path")
    try:
        snap = json.loads(path.read_text())
    except Exception:
        return None
    if time.time() - snap.get("written_at", 0) > float(cfg("stale_s")):
        return None
    return snap


def build_live_mix_block(max_events: int | None = None) -> str:
    """The `LIVE MIX (now)` context block, or '' if the stream is down."""
    snap = read_perception_snapshot()
    if not snap or not snap.get("latest_frame"):
        return ""
    lf = snap["latest_frame"]
    lines = [lf.get("text", "").rstrip()]

    n = int(cfg("max_events") if max_events is None else max_events)
    evs = snap.get("recent_events", [])[-n:]
    if evs:
        parts = []
        for e in evs:
            t = e.get("type", "")
            if t in ("mask_on", "mask_off"):
                parts.append(f"{t} {e.get('a')}~{e.get('b')}@{e.get('band')}")
            elif t == "level_jump":
                parts.append(f"{e.get('a')} {e.get('dir')} {e.get('value'):+.0f}dB")
            elif t == "clip":
                parts.append(f"clip {e.get('a')}")
        if parts:
            lines.append("RECENT: " + " · ".join(parts))
    return "\n".join(lines)
