"""
perception_recorder.py — persist the live perception stream to a session-scoped
trajectory JSONL, so the SIM can be trained on REAL sessions.

The FrameEmitter (perception_stream.py) already builds one (frame, events) per tick
and calls its `on_frame` hook — the reserved MiniCPM-o seat, currently unused. This
recorder plugs into that hook:

  on_frame(frame, events)   -> buffers a compact record IN MEMORY (fast, runs on the
                               25 Hz frame clock; never touches disk or blocks the clock)
  flush_loop()              -> async; every `trajectory_flush_s` appends buffered records
                               to <session>/frames.jsonl (I/O decoupled from the clock)

One manifest.json per session pins the schema (roles, band scheme, vector length,
frame rate) so a loader can validate/reconstruct frames.

Each JSONL line is ONE trajectory step:
  {"step": int, "t_wall": float, "bar": int, "beat": float, "playing": bool,
   "frame": <Frame.to_dict()>, "events": [<Event asdict>, ...]}

This is the OBSERVATION half of a SIM trajectory. Action/outcome pairing (wrapping
MCP tool calls with the frame before/after) layers on top later — `step` + `t_wall`
are the join keys. Read back with load_trajectory() / iter_trajectory().
"""

from __future__ import annotations

import json
import time
from collections import deque
from dataclasses import asdict
from pathlib import Path
from typing import Iterator, Optional

from perception_config import cfg
from perception_frame import Frame

_ROOT = Path(__file__).resolve().parent.parent


class TrajectoryRecorder:
    """Buffers perception frames on the clock, flushes them to a session JSONL off it."""

    def __init__(self, session_id: Optional[str] = None, override: dict | None = None):
        self.override = override
        self.session_id = session_id or ("sess_%d" % int(time.time()))
        self.dir = _ROOT / cfg("trajectory_dir", override) / self.session_id
        self.path = self.dir / "frames.jsonl"
        self.manifest_path = self.dir / "manifest.json"
        self.stride = max(1, int(cfg("trajectory_stride", override)))
        self.only_when_playing = bool(cfg("trajectory_only_when_playing", override))
        self._buf: deque = deque()               # pending records (dicts), drained by flush
        self._step = 0                           # monotonic step index (recorded frames)
        self._seen = 0                            # total frames offered (for stride)
        self._fh = None                          # append file handle (opened on first flush)

    # -- on the frame clock: cheap, in-memory only --------------------------------
    def on_frame(self, frame, events) -> None:
        """Called once per tick by FrameEmitter. Serialize + buffer; never block/raise."""
        try:
            self._seen += 1
            if self.only_when_playing and not getattr(frame, "playing", False) and not events:
                return                            # skip silent/stopped frames (low value)
            if (self._seen - 1) % self.stride:
                return                            # decimation (stride > 1)
            self._buf.append({
                "step": self._step,
                "t_wall": frame.t_wall,
                "bar": frame.bar,
                "beat": frame.beat,
                "playing": bool(getattr(frame, "playing", False)),
                "frame": frame.to_dict(),
                "events": [asdict(e) for e in events],
            })
            self._step += 1
        except Exception:  # noqa: BLE001 — a recorder hiccup must never stall the clock
            pass

    # -- off the clock: disk I/O --------------------------------------------------
    def _ensure_open(self) -> None:
        if self._fh is None:
            self.dir.mkdir(parents=True, exist_ok=True)
            if not self.manifest_path.exists():
                self.manifest_path.write_text(json.dumps(self._manifest(), indent=1))
            self._fh = self.path.open("a", encoding="utf-8")

    def _manifest(self) -> dict:
        roles, scheme = cfg("roles", self.override), cfg("band_scheme", self.override)
        return {
            "session_id": self.session_id,
            "started_at": time.time(),
            "frame_rate_hz": cfg("frame_rate_hz", self.override),
            "band_scheme": scheme,
            "roles": roles,
            "vector_len": Frame.vector_len(roles, scheme),
            "stride": self.stride,
            "only_when_playing": self.only_when_playing,
            "schema": "step,t_wall,bar,beat,playing,frame(Frame.to_dict),events(Event)",
        }

    def flush(self) -> int:
        """Drain the in-memory buffer to the JSONL (append). Returns rows written."""
        if not self._buf:
            return 0
        self._ensure_open()
        n = 0
        while self._buf:
            self._fh.write(json.dumps(self._buf.popleft()) + "\n")
            n += 1
        self._fh.flush()
        return n

    async def flush_loop(self) -> None:
        import asyncio
        interval = float(cfg("trajectory_flush_s", self.override))
        try:
            while True:
                await asyncio.sleep(interval)
                self.flush()
        finally:
            self.close()

    def close(self) -> None:
        try:
            self.flush()
        finally:
            if self._fh is not None:
                self._fh.close()
                self._fh = None


# -- loader --------------------------------------------------------------------
def _resolve(path) -> Path:
    """Accept a session dir OR a frames.jsonl path; return the jsonl path."""
    p = Path(path)
    return p / "frames.jsonl" if p.is_dir() else p


def iter_trajectory(path) -> Iterator[dict]:
    """Yield each recorded step (dict) from a session dir or frames.jsonl, in order."""
    with _resolve(path).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_trajectory(path) -> dict:
    """Load a whole session: {"manifest": {...}|None, "steps": [step dicts]}."""
    jsonl = _resolve(path)
    manifest = None
    mpath = jsonl.parent / "manifest.json"
    if mpath.exists():
        manifest = json.loads(mpath.read_text())
    return {"manifest": manifest, "steps": list(iter_trajectory(jsonl))}


def frames_of(steps) -> list:
    """Reconstruct Frame objects from recorded steps (for probing / vectorization)."""
    return [Frame.from_dict(s["frame"]) for s in steps]
