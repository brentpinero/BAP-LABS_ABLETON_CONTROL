#!/usr/bin/env python3
"""
Mix Analysis Bridge - OSC Receiver for Mix Analysis Hub M4L Device

Receives real-time audio analysis from Max for Live and builds context for LLM.

OSC Messages received on port 9880:
- /mix/levels rms_l rms_r peak_l peak_r mid_energy side_energy
- /mix/stereo correlation mid_energy side_energy
- /mix/spectrum [10 band magnitudes]
- /mix/transport playing bpm bar beat

Author: BAP Labs
"""

import asyncio
import json
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

import bands as _bands
from masking import Node, compute_masking


@dataclass
class BarAnalysis:
    """Analysis data for a single bar."""
    bar_number: int
    timestamp: float
    spectrum_10band: List[float] = field(default_factory=list)
    rms_l: float = -100.0
    rms_r: float = -100.0
    peak_l: float = -100.0
    peak_r: float = -100.0
    mid_energy: float = 0.0
    side_energy: float = 0.0
    correlation: float = 0.0
    scan_type: str = "realtime"

    def to_dict(self) -> dict:
        return {
            "bar_number": self.bar_number,
            "timestamp": self.timestamp,
            "spectrum_10band": self.spectrum_10band,
            "levels": {
                "rms_l": round(self.rms_l, 2),
                "rms_r": round(self.rms_r, 2),
                "peak_l": round(self.peak_l, 2),
                "peak_r": round(self.peak_r, 2),
            },
            "stereo": {
                "correlation": round(self.correlation, 3),
                "mid_energy": round(self.mid_energy, 4),
                "side_energy": round(self.side_energy, 4),
                "width": self.calculate_width(),
            },
            "scan_type": self.scan_type
        }

    def calculate_width(self) -> float:
        """Calculate stereo width from mid/side energy."""
        total = self.mid_energy + self.side_energy
        if total < 0.0001:
            return 0.0
        return round(self.side_energy / total, 3)


# Roles that participate in the group-vs-group masking view.
_MASK_PARTICIPANTS = ("group", "master")

# Map Live track kinds -> masking node roles.
_ROLE = {"group": "group", "master": "master", "return": "return",
         "audio": "track", "midi": "track"}


@dataclass
class TrackState:
    """Latest per-track/group/master analysis (the live 'ears' for one node).

    Spectrum length is NOT fixed — it carries whatever the active band scheme
    declares, so resolution is swappable (see bands.py). Consumers read the
    length from `bands` and the names from `band_scheme`, never hardcode 7.
    """
    track_id: str
    name: str = ""
    kind: str = ""                       # Live kind: audio | midi | group | master | return
    group_id: str = "-1"
    band_scheme: str = _bands.DEFAULT_SCHEME
    bands: List[float] = field(default_factory=list)   # per-band energy fraction
    rms_l: float = -100.0
    rms_r: float = -100.0
    peak_l: float = -100.0
    peak_r: float = -100.0
    mid_energy: float = 0.0
    side_energy: float = 0.0
    correlation: float = 0.0
    updated_at: float = 0.0

    @property
    def rms_db(self) -> float:
        return (self.rms_l + self.rms_r) / 2.0

    def to_node(self) -> Node:
        return Node(id=self.track_id, name=self.name or self.track_id,
                    role=_ROLE.get(self.kind, "track"), bands=list(self.bands),
                    rms_db=self.rms_db, group_id=self.group_id)

    def to_dict(self) -> dict:
        return {
            "id": self.track_id, "name": self.name, "kind": self.kind,
            "group_id": self.group_id, "band_scheme": self.band_scheme,
            "n_bands": len(self.bands), "bands": [round(b, 6) for b in self.bands],
            "rms_l": round(self.rms_l, 2), "rms_r": round(self.rms_r, 2),
            "peak_l": round(self.peak_l, 2), "peak_r": round(self.peak_r, 2),
            "correlation": round(self.correlation, 3),
            "updated_at": self.updated_at,
        }


class BarCache:
    """LRU cache for bar analysis data."""

    def __init__(self, max_size: int = 500):
        self.max_size = max_size
        self.cache: Dict[int, BarAnalysis] = {}
        self.access_order: deque = deque()

    def get(self, bar_number: int) -> Optional[BarAnalysis]:
        """Get bar analysis, updating access order."""
        if bar_number in self.cache:
            # Move to end (most recently accessed)
            if bar_number in self.access_order:
                self.access_order.remove(bar_number)
            self.access_order.append(bar_number)
            return self.cache[bar_number]
        return None

    def put(self, bar_number: int, analysis: BarAnalysis):
        """Add or update bar analysis."""
        if bar_number in self.cache:
            self.access_order.remove(bar_number)
        elif len(self.cache) >= self.max_size:
            # Evict oldest
            oldest = self.access_order.popleft()
            del self.cache[oldest]

        self.cache[bar_number] = analysis
        self.access_order.append(bar_number)

    def get_range(self, start_bar: int, end_bar: int) -> List[Optional[BarAnalysis]]:
        """Get a range of bars."""
        return [self.get(b) for b in range(start_bar, end_bar)]


class MixAnalysisBridge:
    """
    Main bridge between M4L Mix Analysis Hub and LLM.

    Receives OSC data, caches bar-by-bar analysis, and builds context windows.
    """

    def __init__(self, port: int = 9880, band_scheme: Optional[str] = None):
        self.port = port
        self.bar_cache = BarCache()
        self.band_scheme = band_scheme or _bands.DEFAULT_SCHEME

        # Per-node live state (track/group/master), keyed by track id. This is the
        # per-track evolution of the master-only bar cache above; both coexist.
        self.tracks: Dict[str, TrackState] = {}

        # Current state
        self.current_bar = 0
        self.current_beat = 0.0
        self.bpm = 120.0
        self.is_playing = False

        # Real-time accumulator for current bar
        self.current_analysis = BarAnalysis(bar_number=0, timestamp=time.time())
        self.sample_count = 0

        # Stats
        self.messages_received = 0
        self.last_message_time = 0.0

    def handle_levels(self, address: str, *args):
        """Handle /mix/levels message."""
        if len(args) >= 6:
            self.current_analysis.rms_l = args[0]
            self.current_analysis.rms_r = args[1]
            self.current_analysis.peak_l = args[2]
            self.current_analysis.peak_r = args[3]
            self.current_analysis.mid_energy = args[4]
            self.current_analysis.side_energy = args[5]
            self.sample_count += 1  # each levels frame = one ~33ms sample of the bar
            self.messages_received += 1
            self.last_message_time = time.time()

    def handle_stereo(self, address: str, *args):
        """Handle /mix/stereo message."""
        if len(args) >= 3:
            self.current_analysis.correlation = args[0]
            self.current_analysis.mid_energy = args[1]
            self.current_analysis.side_energy = args[2]
            self.messages_received += 1
            self.last_message_time = time.time()

    def handle_spectrum(self, address: str, *args):
        """Handle /mix/spectrum message (10 bands)."""
        self.current_analysis.spectrum_10band = list(args[:10])
        self.messages_received += 1
        self.last_message_time = time.time()

    def handle_transport(self, address: str, *args):
        """Handle /mix/transport message."""
        if len(args) >= 4:
            self.is_playing = bool(args[0])
            self.bpm = float(args[1])
            new_bar = int(args[2])
            self.current_beat = float(args[3])

            # Bar changed - save current and start new (don't finalize the
            # startup None-bar; only bars that actually collected samples)
            if new_bar != self.current_bar:
                if self.current_bar is not None and self.sample_count > 0:
                    self.finalize_current_bar()
                self.current_bar = new_bar
                self.current_analysis = BarAnalysis(
                    bar_number=new_bar,
                    timestamp=time.time()
                )
                self.sample_count = 0

            self.messages_received += 1
            self.last_message_time = time.time()

    # ---- per-track handlers -------------------------------------------------
    # OSC contract (emitted by a Mix Analysis Hub device on every track/group/master):
    #   /track/<id>/meta     name kind group_id [band_scheme]
    #   /track/<id>/levels   rms_l rms_r peak_l peak_r mid side
    #   /track/<id>/spectrum b0 b1 ... bN     (N = active scheme's band count)
    #   /track/<id>/stereo   correlation mid side
    # <id> is the Live track id (stable); "master" for the main bus.
    @staticmethod
    def _id_from(address: str) -> str:
        parts = address.split("/")        # ["", "track", "<id>", "<kind>"]
        return parts[2] if len(parts) >= 4 else "?"

    def _track(self, track_id: str) -> TrackState:
        ts = self.tracks.get(track_id)
        if ts is None:
            ts = TrackState(track_id=track_id, band_scheme=self.band_scheme)
            self.tracks[track_id] = ts
        return ts

    def handle_track_meta(self, address: str, *args):
        ts = self._track(self._id_from(address))
        if len(args) >= 1: ts.name = str(args[0])
        if len(args) >= 2: ts.kind = str(args[1])
        if len(args) >= 3: ts.group_id = str(args[2])
        if len(args) >= 4: ts.band_scheme = str(args[3])   # device may declare its scheme
        ts.updated_at = time.time()
        self.messages_received += 1
        self.last_message_time = ts.updated_at

    def handle_track_levels(self, address: str, *args):
        if len(args) >= 6:
            ts = self._track(self._id_from(address))
            ts.rms_l, ts.rms_r, ts.peak_l, ts.peak_r, ts.mid_energy, ts.side_energy = args[:6]
            ts.updated_at = time.time()
            self.messages_received += 1
            self.last_message_time = ts.updated_at

    def handle_track_spectrum(self, address: str, *args):
        # Variable length by design — store whatever the scheme declares.
        ts = self._track(self._id_from(address))
        ts.bands = list(args)
        ts.updated_at = time.time()
        self.messages_received += 1
        self.last_message_time = ts.updated_at

    def handle_track_stereo(self, address: str, *args):
        if len(args) >= 3:
            ts = self._track(self._id_from(address))
            ts.correlation, ts.mid_energy, ts.side_energy = args[:3]
            ts.updated_at = time.time()
            self.messages_received += 1
            self.last_message_time = ts.updated_at

    def compute_track_masking(self, max_age_s: float = 5.0) -> dict:
        """Group-vs-group + master-congestion masking from current per-node spectra.
        Only nodes updated within max_age_s and carrying a spectrum participate."""
        now = time.time()
        nodes = [ts.to_node() for ts in self.tracks.values()
                 if ts.bands and (now - ts.updated_at) <= max_age_s]
        if not nodes:
            return {"scheme": self.band_scheme, "pairs": [], "master_congestion": [],
                    "summary": "No live per-track spectra yet."}
        return compute_masking(nodes, scheme_id=self.band_scheme,
                               participants=_MASK_PARTICIPANTS)

    def build_tracks_snapshot(self, max_age_s: float = 5.0) -> dict:
        """Per-track live state + masking, for the live_ears snapshot file."""
        now = time.time()
        return {
            "band_scheme": self.band_scheme,
            "tracks": {tid: ts.to_dict() for tid, ts in self.tracks.items()
                       if (now - ts.updated_at) <= max_age_s},
            "masking": self.compute_track_masking(max_age_s),
        }

    def handle_default(self, address: str, *args):
        """Handle unknown OSC messages."""
        print(f"[MIX_HUB] Unknown: {address} {args}")

    def finalize_current_bar(self):
        """Save current bar analysis to cache."""
        if self.sample_count > 0:
            self.bar_cache.put(self.current_bar, self.current_analysis)
            print(f"[MIX_HUB] Cached bar {self.current_bar}: "
                  f"RMS={self.current_analysis.rms_l:.1f}/{self.current_analysis.rms_r:.1f}dB "
                  f"Corr={self.current_analysis.correlation:.2f}")

    def build_32bar_context(self, center_bar: Optional[int] = None) -> dict:
        """
        Build 32-bar context window for LLM.

        Args:
            center_bar: Center of context window (default: current bar)

        Returns:
            Context dict ready for LLM consumption
        """
        if center_bar is None:
            center_bar = self.current_bar

        start_bar = max(0, center_bar - 16)
        end_bar = center_bar + 16

        bars_data = []
        for bar_num in range(start_bar, end_bar):
            analysis = self.bar_cache.get(bar_num)
            if analysis:
                bars_data.append(analysis.to_dict())
            else:
                bars_data.append({
                    "bar_number": bar_num,
                    "status": "not_analyzed"
                })

        return {
            "window": {
                "center_bar": center_bar,
                "start_bar": start_bar,
                "end_bar": end_bar,
                "total_bars": end_bar - start_bar
            },
            "transport": {
                "bpm": self.bpm,
                "playing": self.is_playing,
                "current_bar": self.current_bar,
                "current_beat": self.current_beat
            },
            "bars": bars_data,
            "stats": {
                "messages_received": self.messages_received,
                "cached_bars": len(self.bar_cache.cache),
                "last_update": self.last_message_time
            }
        }

    def get_status(self) -> dict:
        """Get current bridge status."""
        return {
            "port": self.port,
            "messages_received": self.messages_received,
            "cached_bars": len(self.bar_cache.cache),
            "tracks_live": len(self.tracks),
            "band_scheme": self.band_scheme,
            "current_bar": self.current_bar,
            "bpm": self.bpm,
            "playing": self.is_playing,
            "last_message": time.time() - self.last_message_time if self.last_message_time else None,
            "current_levels": {
                "rms_l": round(self.current_analysis.rms_l, 1),
                "rms_r": round(self.current_analysis.rms_r, 1),
                "correlation": round(self.current_analysis.correlation, 2)
            }
        }

    async def start(self):
        """Start the OSC server."""
        dispatcher = Dispatcher()
        # master-bus (v1, back-compat)
        dispatcher.map("/mix/levels", self.handle_levels)
        dispatcher.map("/mix/stereo", self.handle_stereo)
        dispatcher.map("/mix/spectrum", self.handle_spectrum)
        dispatcher.map("/mix/transport", self.handle_transport)
        # transport can also arrive globally (not master-scoped)
        dispatcher.map("/transport", self.handle_transport)
        # per-track/group/master (v2)
        dispatcher.map("/track/*/meta", self.handle_track_meta)
        dispatcher.map("/track/*/levels", self.handle_track_levels)
        dispatcher.map("/track/*/spectrum", self.handle_track_spectrum)
        dispatcher.map("/track/*/stereo", self.handle_track_stereo)
        dispatcher.set_default_handler(self.handle_default)

        server = AsyncIOOSCUDPServer(
            ("127.0.0.1", self.port),
            dispatcher,
            asyncio.get_event_loop()
        )
        transport, protocol = await server.create_serve_endpoint()

        print(f"[MIX_HUB] OSC server listening on port {self.port}")
        print(f"[MIX_HUB] Waiting for Mix Analysis Hub M4L device...")

        return transport


async def status_printer(bridge: MixAnalysisBridge):
    """Print status every 5 seconds."""
    while True:
        await asyncio.sleep(5)
        status = bridge.get_status()
        if status["messages_received"] > 0:
            print(f"[STATUS] Msgs: {status['messages_received']} | "
                  f"Bars cached: {status['cached_bars']} | "
                  f"Current: bar {status['current_bar']} @ {status['bpm']:.1f} BPM | "
                  f"RMS: {status['current_levels']['rms_l']:.1f}dB")


async def main():
    """Main entry point."""
    print("=" * 60)
    print("MIX ANALYSIS BRIDGE - Real-Time Audio Analysis Receiver")
    print("=" * 60)
    print()

    bridge = MixAnalysisBridge(port=9880)
    transport = await bridge.start()

    # Start status printer
    asyncio.create_task(status_printer(bridge))

    print()
    print("Commands:")
    print("  - Load 'Mix Analysis Hub.maxpat' in Max/Live")
    print("  - Enable analysis toggle")
    print("  - Play audio to see levels")
    print()
    print("Press Ctrl+C to stop")
    print()

    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[MIX_HUB] Shutting down...")
    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())
