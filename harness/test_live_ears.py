"""
test_live_ears.py — offline tests for the live-Ableton listening pipeline.

Feeds synthetic OSC packets (standing in for the Mix Analysis Hub M4L device)
at a MixAnalysisBridge on a test port, and verifies: bar caching, snapshot
writing, prose summary, and staleness detection. No Ableton needed.
Run: python harness/test_live_ears.py  (or pytest).
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

TEST_PORT = 9891


async def _scenario():
    from mix_analysis_bridge import MixAnalysisBridge
    import live_ears
    from pythonosc.udp_client import SimpleUDPClient

    bridge = MixAnalysisBridge(port=TEST_PORT)
    transport = await bridge.start()
    writer = asyncio.create_task(live_ears._snapshot_writer(bridge))
    client = SimpleUDPClient("127.0.0.1", TEST_PORT)

    for bar in range(1, 6):
        for beat in range(4):
            client.send_message("/mix/levels", [-16.0 + bar, -16.5 + bar, -8.0, -8.2, 0.5, 0.15])
            client.send_message("/mix/stereo", [0.45, 0.5, 0.22])
            client.send_message("/mix/transport", [1, 88.0, bar, beat])
            await asyncio.sleep(0.015)
    await asyncio.sleep(0.8)  # allow a snapshot write

    # fresh snapshot with cached bars
    snap = live_ears._read_snapshot()
    assert "error" not in snap, snap
    assert snap["status"]["cached_bars"] >= 3, snap["status"]
    bars = snap["recent_bars"]
    assert bars and "levels" in bars[-1] and "stereo" in bars[-1]

    # prose mentions level and width
    prose = live_ears._describe(bars)
    assert "dB RMS" in prose and "Width" in prose, prose

    writer.cancel()
    transport.close()

    # staleness detection
    p = live_ears.SNAPSHOT_PATH
    d = json.loads(p.read_text())
    d["written_at"] = time.time() - 60
    p.write_text(json.dumps(d))
    stale = live_ears._read_snapshot()
    assert "error" in stale and "stale" in stale["error"], stale
    os.remove(p)


def test_live_ears_pipeline():
    asyncio.run(_scenario())


def test_missing_snapshot_gives_fix_instructions():
    import live_ears
    if live_ears.SNAPSHOT_PATH.exists():
        os.remove(live_ears.SNAPSHOT_PATH)
    r = live_ears._read_snapshot()
    assert "error" in r and "fix" in r


if __name__ == "__main__":
    test_live_ears_pipeline()
    print("  PASS  test_live_ears_pipeline")
    test_missing_snapshot_gives_fix_instructions()
    print("  PASS  test_missing_snapshot_gives_fix_instructions")
    print("\n2/2 tests passed.")
