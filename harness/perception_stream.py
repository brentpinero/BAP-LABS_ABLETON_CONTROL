"""
perception_stream.py — the push emitter for the streaming perception layer.

Runs inside the `ears` daemon beside MixAnalysisBridge's snapshot writer. On a
fixed frame clock it builds one Frame from the live bridge, detects hysteretic
events, buffers both, and fans out three ways:
  - OSC/UDP push (/perc/frame + /perc/event/<type>) for the future duplex consumer,
  - an in-process on_frame(frame, events) callback (the MiniCPM-o adapter later),
  - a decimated perception_stream.json snapshot (the cross-process bridge to the
    separate text-LLM harness), mirroring live_ears.py.

Events use dual-threshold + dwell / refractory hysteresis so they don't flap.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Callable, Optional

from pythonosc.udp_client import SimpleUDPClient

from perception_config import cfg
from perception_frame import build_frame

_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Event:
    t_wall: float
    bar: int
    beat: float
    type: str                 # mask_on|mask_off|clip|level_jump
    a: Optional[str] = None
    b: Optional[str] = None
    band: Optional[str] = None
    value: float = 0.0
    dir: Optional[str] = None
    seq: int = -1


class EventDetector:
    """Per-signal hysteresis: mask on/off (dual-threshold + dwell), clip (rearm
    margin), level jump (±dB over a window + refractory)."""

    def __init__(self, override: dict | None = None):
        self.T_on = cfg("event.mask_on", override)
        self.T_off = cfg("event.mask_off", override)
        self.min_frames = int(cfg("event.mask_min_frames", override))
        self.clip_db = cfg("event.clip_db", override)
        self.clip_margin = cfg("event.clip_margin_db", override)
        self.jump_db = cfg("event.level_jump_db", override)
        self.jump_win = cfg("event.level_jump_win_s", override)
        self.mask: dict = {}
        self.clip_armed: dict = {}
        self.level_hist: dict = {}
        self.jump_until: dict = {}

    def update(self, frame) -> list:
        evs = []

        def mk(**kw):
            evs.append(Event(t_wall=frame.t_wall, bar=frame.bar, beat=frame.beat, **kw))

        # --- masking pairs ---
        cur = {}
        for p in frame.masking.get("pairs", []):
            cur[tuple(sorted((p["a"], p["b"])))] = (p["score"], p["top_band"])
        for key in set(self.mask) | set(cur):
            score, band = cur.get(key, (0.0, None))
            st = self.mask.setdefault(key, {"on": False, "on_cnt": 0, "off_cnt": 0})
            if not st["on"]:
                st["on_cnt"] = st["on_cnt"] + 1 if score >= self.T_on else 0
                if st["on_cnt"] >= self.min_frames:
                    st.update(on=True, off_cnt=0)
                    mk(type="mask_on", a=key[0], b=key[1], band=band, value=score)
            else:
                st["off_cnt"] = st["off_cnt"] + 1 if score <= self.T_off else 0
                if st["off_cnt"] >= self.min_frames:
                    st.update(on=False, on_cnt=0)
                    mk(type="mask_off", a=key[0], b=key[1], band=band, value=score)

        # --- clip + level jump per role ---
        for a in frame.aggs:
            armed = self.clip_armed.get(a.role, True)
            if armed and a.peak_db >= self.clip_db:
                mk(type="clip", a=a.role, value=a.peak_db)
                self.clip_armed[a.role] = False
            elif not armed and a.peak_db <= self.clip_db - self.clip_margin:
                self.clip_armed[a.role] = True

            hist = self.level_hist.setdefault(a.role, deque())
            hist.append((frame.t_wall, a.node.rms_db))
            while hist and frame.t_wall - hist[0][0] > self.jump_win:
                hist.popleft()
            if len(hist) >= 2 and a.node.rms_db > -119:
                delta = a.node.rms_db - hist[0][1]
                if abs(delta) >= self.jump_db and frame.t_wall >= self.jump_until.get(a.role, 0):
                    mk(type="level_jump", a=a.role, value=delta, dir="up" if delta > 0 else "down")
                    self.jump_until[a.role] = frame.t_wall + self.jump_win
        return evs


class FrameEmitter:
    def __init__(self, bridge, override: dict | None = None,
                 on_frame: Optional[Callable] = None):
        self.bridge = bridge
        self.override = override
        self.on_frame = on_frame
        self.client = SimpleUDPClient(cfg("push_host", override), int(cfg("push_port", override)))
        self.frames = deque(maxlen=int(cfg("buffer_frames", override)))
        self.events = deque(maxlen=int(cfg("buffer_frames", override)))
        self.detector = EventDetector(override)
        self.cursor = 0
        self._focus = {"selected_role": None, "focused_band": None,
                       "device_class": "none", "last_action": "none"}
        self.snapshot_path = _ROOT / cfg("snapshot_path", override)

    def set_focus(self, focus: dict) -> None:
        self._focus = focus

    def _transport(self) -> dict:
        b = self.bridge
        # Align the frame to the audio instant it describes: the audio content lags real
        # time by ~audio_latency_s (M4L window + OSC), so read the dead-reckoned transport
        # at (now - latency) and stamp THAT as the frame's t_wall — one consistent instant.
        at = time.time() - float(cfg("audio_latency_s", self.override))
        if hasattr(b, "transport_now"):
            tr = b.transport_now(at)
        else:
            tr = {"bpm": getattr(b, "bpm", 120.0), "bar": getattr(b, "current_bar", 0) or 0,
                  "beat": getattr(b, "current_beat", 0.0), "beats_per_bar": 4,
                  "playing": getattr(b, "is_playing", False)}
        tr["t_wall"] = at
        return tr

    def tick(self):
        frame = build_frame(self.bridge.tracks, self._transport(), self._focus, self.override)
        evs = self.detector.update(frame)
        self.frames.append(frame)
        for e in evs:
            e.seq = self.cursor
            self.cursor += 1
            self.events.append(e)
        self._push(frame, evs)
        if self.on_frame:
            try:
                self.on_frame(frame, evs)
            except Exception:  # noqa: BLE001 — a bad consumer must not stall the clock
                pass
        return frame, evs

    def _push(self, frame, evs):
        try:
            self.client.send_message("/perc/frame", frame.to_vector())
            for e in evs:
                self.client.send_message(f"/perc/event/{e.type}",
                                         [e.a or "", e.b or "", e.band or "", float(e.value)])
        except Exception:  # noqa: BLE001 — UDP push is best-effort; buffer/file are the record
            pass

    def drain_since(self, seq: int) -> dict:
        return {"frames": [f.to_dict() for f in self.frames],
                "events": [asdict(e) for e in self.events if e.seq >= seq],
                "cursor": self.cursor}

    async def run(self):
        period = 1.0 / max(1.0, float(cfg("frame_rate_hz", self.override)))
        next_t = perf_counter()
        while True:
            self.tick()
            next_t += period
            await asyncio.sleep(max(0.0, next_t - perf_counter()))

    def write_snapshot(self):
        latest = self.frames[-1] if self.frames else None
        snap = {"written_at": time.time(),
                "latest_frame": latest.to_dict() if latest else None,
                "recent_events": [asdict(e) for e in list(self.events)[-int(cfg("max_events", self.override)):]],
                "cursor": self.cursor}
        self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.snapshot_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(snap))
        os.replace(tmp, self.snapshot_path)

    async def snapshot_writer(self):
        interval = float(cfg("snapshot_interval_s", self.override))
        while True:
            self.write_snapshot()
            await asyncio.sleep(interval)
