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

    def __init__(self, port: int = 9880):
        self.port = port
        self.bar_cache = BarCache()

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

            # Bar changed - save current and start new
            if new_bar != self.current_bar and self.sample_count > 0:
                self.finalize_current_bar()
                self.current_bar = new_bar
                self.current_analysis = BarAnalysis(
                    bar_number=new_bar,
                    timestamp=time.time()
                )
                self.sample_count = 0

            self.messages_received += 1
            self.last_message_time = time.time()

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
        dispatcher.map("/mix/levels", self.handle_levels)
        dispatcher.map("/mix/stereo", self.handle_stereo)
        dispatcher.map("/mix/spectrum", self.handle_spectrum)
        dispatcher.map("/mix/transport", self.handle_transport)
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
