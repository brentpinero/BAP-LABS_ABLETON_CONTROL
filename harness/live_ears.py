"""
live_ears.py — live-Ableton listening daemon + MCP tool surface.

Daemon half (run: `python run_harness.py ears`): wraps the existing
MixAnalysisBridge (OSC sink for the Mix Analysis Hub M4L device on UDP 9880)
and atomically writes a snapshot JSON every ~500ms. ONE process owns the OSC
port; any number of MCP servers/tools read the snapshot file.

Tool half: register_live_ear_tools(mcp, deps) — get_live_ears_status /
get_mix_analysis / get_bar_history read the snapshot and render musician-prose
summaries. Stale snapshots (daemon down / device off) return fix instructions
instead of silently-old data.

v1 is master-bus only (the M4L device hardcodes /mix/* @ 9880). Per-track =
phase 4b: parameterize the device's OSC prefix and instance it per track.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Dict

_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PATH = _ROOT / "sandbox_sessions" / "live_ears.json"
STALE_S = 3.0
WRITE_INTERVAL_S = 0.5


# --------------------------------------------------------------------------
# Daemon
# --------------------------------------------------------------------------
async def _snapshot_writer(bridge) -> None:
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    while True:
        recent = []
        cur = bridge.current_bar
        if cur is not None:
            for b in range(max(0, cur - 16), cur + 1):
                ba = bridge.bar_cache.get(b)
                if ba is not None:
                    recent.append(ba.to_dict())
        snap = {
            "written_at": time.time(),
            "status": bridge.get_status(),
            "recent_bars": recent[-16:],
            "context_32bar": bridge.build_32bar_context() if recent else {},
            # per-track/group/master live state + group-vs-group masking (v2)
            "per_track": bridge.build_tracks_snapshot(),
        }
        tmp = SNAPSHOT_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(snap))
        os.replace(tmp, SNAPSHOT_PATH)
        await asyncio.sleep(WRITE_INTERVAL_S)


async def main() -> None:
    """Entry point for `python run_harness.py ears`.

    Runs the master-bus snapshot writer (pull path) AND the streaming perception
    FrameEmitter (push path: OSC frames + events + perception_stream.json)
    concurrently over the one bridge that owns OSC 9880.
    """
    from mix_analysis_bridge import MixAnalysisBridge
    from perception_stream import FrameEmitter
    from perception_config import cfg
    from aggregator_bridge import AggregatorBridge

    bridge = MixAnalysisBridge(port=9880)
    transport = await bridge.start()
    emitter = FrameEmitter(bridge)
    # expose for the focus lane (sets current focus) and future in-process consumers
    main.emitter = emitter  # type: ignore[attr-defined]

    # multichannel aggregator translator: /agg/ch/<k> (:9886) -> /track/<id> (:9880),
    # so aggregated nodes feed the SAME bridge as per-track devices. Map is hot-loaded
    # from the provisioning state so re-provisioning takes effect without a restart.
    agg_bridge = AggregatorBridge()
    main.agg_bridge = agg_bridge  # type: ignore[attr-defined]

    print(f"[EARS] snapshotting to {SNAPSHOT_PATH} every {WRITE_INTERVAL_S}s")
    print(f"[EARS] perception push @ {cfg('frame_rate_hz')}Hz -> OSC "
          f"{cfg('push_host')}:{cfg('push_port')} + {emitter.snapshot_path}")
    print(f"[EARS] aggregator bridge on :{agg_bridge.recv_port} -> :9880 (Ctrl-C to stop)")
    try:
        await asyncio.gather(
            _snapshot_writer(bridge),
            emitter.run(),
            emitter.snapshot_writer(),
            agg_bridge.run(),
            _agg_map_watcher(agg_bridge),
        )
    finally:
        transport.close()


async def _agg_map_watcher(agg_bridge) -> None:
    """Hot-reload the aggregator channel->track map when provisioning state changes."""
    state = _ROOT / "sandbox_sessions" / "aggregator_state.json"
    last = None
    while True:
        try:
            mt = state.stat().st_mtime if state.exists() else None
            if mt != last:
                last = mt
                agg_bridge.clear()
                if mt:
                    m = json.loads(state.read_text()).get("map", {})
                    agg_bridge.set_map({int(k): v for k, v in m.items()})
                    print(f"[EARS] aggregator map: {len(agg_bridge.map)} channels", flush=True)
        except Exception:
            pass
        await asyncio.sleep(2.0)


# --------------------------------------------------------------------------
# MCP tools (snapshot readers — no OSC, no port contention)
# --------------------------------------------------------------------------
def _read_snapshot() -> Dict[str, Any]:
    if not SNAPSHOT_PATH.exists():
        return {"error": "live ears daemon not running",
                "fix": "Run `python run_harness.py ears` in a terminal, and load the "
                       "'Mix Analysis Hub' M4L device on Ableton's master track with OSC enabled."}
    snap = json.loads(SNAPSHOT_PATH.read_text())
    age = time.time() - snap.get("written_at", 0)
    if age > STALE_S:
        return {"error": f"live ears snapshot is stale ({age:.0f}s old)",
                "fix": "The ears daemon stopped or the M4L device isn't sending. Restart "
                       "`python run_harness.py ears` and check the device's OSC toggle."}
    return snap


def _describe(bars: list) -> str:
    """Musician-prose summary of recent bar analyses (BarAnalysis.to_dict shape)."""
    if not bars:
        return "No bars cached yet — press play in Ableton so the device streams analysis."
    rms = [(b.get("levels", {}).get("rms_l", -60) + b.get("levels", {}).get("rms_r", -60)) / 2
           for b in bars]
    corr = [b.get("stereo", {}).get("correlation", 1.0) for b in bars]
    width = [b.get("stereo", {}).get("width", 0.0) for b in bars]
    trend = rms[-1] - rms[0] if len(rms) > 1 else 0.0
    parts = [f"Last {len(bars)} bars: level ~{sum(rms) / len(rms):.1f} dB RMS "
             f"({'building' if trend > 1.5 else 'dropping' if trend < -1.5 else 'steady'})."]
    avg_corr = sum(corr) / len(corr)
    if avg_corr < 0.2:
        parts.append(f"Stereo correlation {avg_corr:.2f} — phase risk, check mono compatibility.")
    elif avg_corr < 0.6:
        parts.append(f"Wide image (corr {avg_corr:.2f}).")
    avg_w = sum(width) / len(width)
    parts.append(f"Width {avg_w:.2f} ({'narrow' if avg_w < 0.15 else 'moderate' if avg_w < 0.35 else 'wide'}).")
    return " ".join(parts)


def register_live_ear_tools(mcp, deps: Dict[str, Any]) -> None:
    _ok, _err = deps["ok"], deps["err"]

    @mcp.tool()
    def get_live_ears_status() -> str:
        """Is the live-Ableton listening pipeline up? (ears daemon + Mix Analysis Hub M4L device).
        Reports freshness, bars cached, bpm, playing state. Master bus only in v1."""
        try:
            snap = _read_snapshot()
            if "error" in snap:
                return _ok(snap)
            st = snap["status"]
            return _ok({"fresh": True, "playing": st.get("playing"), "bpm": st.get("bpm"),
                        "current_bar": st.get("current_bar"), "bars_cached": st.get("cached_bars"),
                        "current_levels": st.get("current_levels")})
        except Exception as e:
            return _err("reading live ears status", e)

    @mcp.tool()
    def get_mix_analysis(window_bars: int = 8) -> str:
        """LISTEN to the real Ableton session (master bus): musician-prose summary + per-bar
        numbers (RMS, peak, stereo correlation, width) for the last N bars. Use between actions
        to hear what your changes did. Requires the ears daemon + M4L device (see
        get_live_ears_status)."""
        try:
            snap = _read_snapshot()
            if "error" in snap:
                return _ok(snap)
            bars = snap.get("recent_bars", [])[-max(1, min(window_bars, 16)):]
            return _ok({"summary": _describe(bars),
                        "bars": bars,
                        "transport": {k: snap["status"].get(k) for k in ("playing", "bpm", "current_bar")},
                        "next": "Make your change, let a few bars play, then call get_mix_analysis again."})
        except Exception as e:
            return _err("analyzing live mix", e)

    @mcp.tool()
    def get_masking_report() -> str:
        """LISTEN for frequency clashes across the mix: which GROUPS are masking each
        other and in which bands (kick vs bass, synth vs hi-hats), plus which bands are
        crowded on the master. Group-vs-group + master view. Requires per-track Mix
        Analysis Hub devices + the ears daemon (see get_live_ears_status)."""
        try:
            snap = _read_snapshot()
            if "error" in snap:
                return _ok(snap)
            pt = snap.get("per_track", {})
            masking = pt.get("masking", {})
            return _ok({
                "summary": masking.get("summary", "No per-track spectra yet — load a Mix "
                           "Analysis Hub device on each group + the master, and press play."),
                "clashes": masking.get("pairs", []),
                "master_congestion": masking.get("master_congestion", []),
                "band_scheme": pt.get("band_scheme"),
                "tracks_live": len(pt.get("tracks", {})),
                "next": "Adjust EQ/level on a clashing group, let a few bars play, call again.",
            })
        except Exception as e:
            return _err("reading masking report", e)

    @mcp.tool()
    def get_bar_history(start_bar: int, end_bar: int) -> str:
        """Raw cached per-bar analysis for a bar range (from the 32-bar context window)."""
        try:
            snap = _read_snapshot()
            if "error" in snap:
                return _ok(snap)
            ctx = snap.get("context_32bar", {})
            bars = [b for b in snap.get("recent_bars", [])
                    if start_bar <= b.get("bar", -1) <= end_bar]
            return _ok({"bars": bars, "context": ctx})
        except Exception as e:
            return _err("reading bar history", e)
