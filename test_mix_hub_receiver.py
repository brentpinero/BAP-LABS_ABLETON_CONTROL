#!/usr/bin/env python3
"""
Test receiver for Mix Analysis Hub - Logs all OSC messages to file for debugging.

Run this, then load Mix Analysis Hub.maxpat in Ableton on Master track.
Play some audio and this will log everything.

Usage:
    python test_mix_hub_receiver.py
"""

import asyncio
import time
from datetime import datetime
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

# Log file
LOG_FILE = "/Users/brentpinero/Documents/serum_llm_2/mix_hub_test.log"

# Stats
stats = {
    "levels_count": 0,
    "stereo_count": 0,
    "transport_count": 0,
    "start_time": time.time(),
    "last_bar": -1,
    "bars_seen": set()
}


def log(msg: str):
    """Log to both console and file."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def handle_levels(address: str, *args):
    """Handle /mix/levels message."""
    stats["levels_count"] += 1
    if stats["levels_count"] <= 5 or stats["levels_count"] % 30 == 0:
        log(f"LEVELS: rms_l={args[0]:.1f} rms_r={args[1]:.1f} peak_l={args[2]:.1f} peak_r={args[3]:.1f} mid={args[4]:.4f} side={args[5]:.4f}")


def handle_stereo(address: str, *args):
    """Handle /mix/stereo message."""
    stats["stereo_count"] += 1
    if stats["stereo_count"] <= 5 or stats["stereo_count"] % 30 == 0:
        log(f"STEREO: corr={args[0]:.3f} mid={args[1]:.4f} side={args[2]:.4f}")


def handle_transport(address: str, *args):
    """Handle /mix/transport message."""
    stats["transport_count"] += 1

    if len(args) >= 5:
        playing = bool(args[0])
        bpm = args[1]
        bar = int(args[2])
        beat = args[3]
        length = int(args[4])

        # Log every bar change
        if bar != stats["last_bar"]:
            stats["bars_seen"].add(bar)
            stats["last_bar"] = bar
            log(f">>> BAR CHANGE: bar={bar} beat={beat:.2f} | {'PLAYING' if playing else 'STOPPED'} @ {bpm:.1f} BPM | song_length={length} bars")

        # Also log first few transport messages
        if stats["transport_count"] <= 3:
            log(f"TRANSPORT: playing={playing} bpm={bpm} bar={bar} beat={beat:.2f} length={length}")


def handle_unknown(address: str, *args):
    """Handle unknown messages."""
    log(f"UNKNOWN: {address} -> {args}")


async def print_summary():
    """Print summary every 10 seconds."""
    while True:
        await asyncio.sleep(10)
        elapsed = time.time() - stats["start_time"]
        total = stats["levels_count"] + stats["stereo_count"] + stats["transport_count"]

        log(f"=== SUMMARY ({elapsed:.0f}s) === msgs={total} | levels={stats['levels_count']} stereo={stats['stereo_count']} transport={stats['transport_count']} | bars_seen={len(stats['bars_seen'])}")


async def main():
    # Clear log file
    with open(LOG_FILE, "w") as f:
        f.write(f"=== MIX HUB TEST LOG - {datetime.now().isoformat()} ===\n")
        f.write(f"Listening on port 9880 for OSC from Mix Analysis Hub\n\n")

    log("Starting Mix Hub Test Receiver on port 9880...")
    log("Load 'Mix Analysis Hub.maxpat' in Ableton on Master track")
    log("Enable the toggle and play audio")
    log("")

    dispatcher = Dispatcher()
    dispatcher.map("/mix/levels", handle_levels)
    dispatcher.map("/mix/stereo", handle_stereo)
    dispatcher.map("/mix/transport", handle_transport)
    dispatcher.set_default_handler(handle_unknown)

    server = AsyncIOOSCUDPServer(
        ("127.0.0.1", 9880),
        dispatcher,
        asyncio.get_event_loop()
    )
    transport, protocol = await server.create_serve_endpoint()

    log("OSC Server started! Waiting for data...")
    log("")

    # Start summary printer
    asyncio.create_task(print_summary())

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        log("\nShutting down...")
        log(f"FINAL: {stats['levels_count']} levels, {stats['stereo_count']} stereo, {stats['transport_count']} transport")
        log(f"Bars seen: {sorted(stats['bars_seen'])}")
    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())
