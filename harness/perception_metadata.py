"""
perception_metadata.py — continuous device/parameter AUTOMATION stream.

The perception frames capture per-track audio analysis; this captures the moving
signal-chain state: every device parameter's value over the song, so parameter
automation (filter sweeps, etc.) is labeled in the dataset instead of lost to a
static snapshot.

`MetadataRecorder` mirrors TrajectoryRecorder: buffer on the sample clock, flush off
it to `<session>/params.jsonl` + a manifest. It is DELTA-ENCODED — each tick stores
only the params whose value changed since the last tick (a full keyframe on tick 0).
Static params return the exact same float every tick, so the delta cleanly isolates
the automated/moving ones; `automation_state` annotates why each moved.

Each record joins to `frames.jsonl` by the SAME audio-aligned coordinate the frames
use (`bridge.transport_now(now - audio_latency_s)`): `{tick, t_wall, bar, beat,
playing, keyframe, changes:[[track_index, dev_path, param_index, value, auto], ...]}`.

Values arrive from the Remote Script's `get_all_device_parameters` (mode=compact),
which returns `[param_index, value, automation_state]` per device path.
"""

from __future__ import annotations

import json
import time
from collections import deque
from pathlib import Path
from typing import Iterator, Optional

from perception_config import cfg

_ROOT = Path(__file__).resolve().parent.parent


class MetadataRecorder:
    """Delta-encoded parameter-value stream, joined to the perception trajectory."""

    def __init__(self, session_id: Optional[str] = None, override: dict | None = None):
        self.override = override
        self.session_id = session_id or ("sess_%d" % int(time.time()))
        self.dir = _ROOT / cfg("metadata_dir", override) / self.session_id
        self.path = self.dir / "params.jsonl"
        # separate manifest name so it never clobbers the frame trajectory's manifest.json
        # when both streams share one <session> folder (they do, for a clean join).
        self.manifest_path = self.dir / "params_manifest.json"
        self.eps = float(cfg("metadata_change_eps", override))
        self.only_when_playing = bool(cfg("metadata_only_when_playing", override))
        self._buf: deque = deque()
        self._last: dict = {}          # (track_index, dev_path, param_index) -> last value
        self._tick = 0
        self._fh = None

    # -- on the sample clock: cheap, in-memory only --------------------------------
    def on_sample(self, snapshot: dict, transport: dict) -> None:
        """Buffer the params that CHANGED since the last sample (keyframe on tick 0).
        `snapshot` is a compact get_all_device_parameters result; never blocks/raises."""
        try:
            playing = bool(transport.get("playing", False))
            keyframe = (self._tick == 0)
            if self.only_when_playing and not playing and not keyframe:
                self._tick += 1
                return
            changes = []
            for t in snapshot.get("tracks", []):
                ti = t.get("track_index")
                for d in t.get("devices", []):
                    path = d.get("path")
                    for p in d.get("params", []):
                        idx, val = p[0], p[1]
                        auto = p[2] if len(p) > 2 else 0
                        key = (ti, path, idx)
                        prev = self._last.get(key)
                        if keyframe or prev is None or abs(val - prev) > self.eps:
                            changes.append([ti, path, idx, round(val, 6), auto])
                            self._last[key] = val
            if changes:                    # skip ticks where nothing moved (delta stream)
                self._buf.append({
                    "tick": self._tick, "t_wall": transport.get("t_wall"),
                    "bar": transport.get("bar"), "beat": transport.get("beat"),
                    "playing": playing, "keyframe": keyframe, "changes": changes,
                })
            self._tick += 1
        except Exception:  # noqa: BLE001 — a sampler hiccup must never stall the loop
            pass

    # -- off the clock: disk I/O --------------------------------------------------
    def _ensure_open(self) -> None:
        if self._fh is None:
            self.dir.mkdir(parents=True, exist_ok=True)
            if not self.manifest_path.exists():
                from perception_schema import build_metadata_manifest
                self.manifest_path.write_text(
                    json.dumps(build_metadata_manifest(self.session_id, time.time(), self.override),
                               indent=1))
            self._fh = self.path.open("a", encoding="utf-8")

    def flush(self) -> int:
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
        interval = float(cfg("metadata_flush_s", self.override))
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


# -- loaders -------------------------------------------------------------------
def _resolve(path) -> Path:
    p = Path(path)
    return p / "params.jsonl" if p.is_dir() else p


def iter_params(path) -> Iterator[dict]:
    """Yield each delta record (dict) from a session dir or params.jsonl, in order."""
    with _resolve(path).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_params(path) -> dict:
    """Load a whole metadata stream: {"manifest": {...}|None, "records": [...]}."""
    jsonl = _resolve(path)
    manifest = None
    mpath = jsonl.parent / "params_manifest.json"    # named to not clobber frames' manifest.json
    if mpath.exists():
        manifest = json.loads(mpath.read_text())
    return {"manifest": manifest, "records": list(iter_params(jsonl))}


def reconstruct_at(records: list, upto_tick: int) -> dict:
    """Replay delta records up to (and including) upto_tick → {(track,path,idx): value}.
    The held-value view of the chain at that point in the song."""
    state: dict = {}
    for rec in records:
        if rec.get("tick", 0) > upto_tick:
            break
        for ti, path, idx, val, _auto in rec.get("changes", []):
            state[(ti, path, idx)] = val
    return state
