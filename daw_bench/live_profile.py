"""
live_profile.py — black-box profile of Ableton Live's audio behaviour (Phase 0).

Plays known test signals through Live and measures what comes out of the master:
pan law, playback neutrality (gain / latency / null), clip-edge fade length and
sample-rate-conversion quality. Pure observation of a licensed copy's output —
no Live code is read. The result is the "Live-compatible" reference profile in
docs/agentic_daw_research.md section 3.

The probes live in profile.py and are engine-agnostic; this file is the Live
target (one source track, master captured via stem_ablation.render_resample,
which records the "Resampling" bus through an armed audio track) plus the CLI.

RUN ON A SCRATCH SET. It creates/deletes one track and moves the transport.
Capture is silent (source and capture tracks routed to 'Sends Only', source
tapped 'Post Mixer'), so nothing reaches the master or the speakers. It refuses to run on a set with more than a template's worth of
tracks unless --force is given. Needs the Remote Script commands
create_arrangement_audio_clip and set_clip_warping (added alongside this file).

Run:  python daw_bench/live_profile.py --out sandbox_sessions/live_profile
"""
from __future__ import annotations

import argparse
import json
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import soundfile as sf

_ROOT = Path(__file__).resolve().parent.parent
for _p in (str(Path(__file__).resolve().parent), str(_ROOT / "harness"), str(_ROOT / "sandbox")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import profile  # noqa: E402
from profile import ProfileError  # noqa: E402
import stem_ablation as sa  # noqa: E402
from live_client import LiveClient, LiveError  # noqa: E402

SRC_TRACK = "DAWBENCH_SRC"
MAX_SCRATCH_TRACKS = 4        # Live's default template


def _clear_clips(client, track_index: int) -> None:
    count = int(client.send("get_arrangement_clips", {"track_index": track_index}).get("clip_count", 0))
    for _ in range(count):
        client.send("delete_arrangement_clip", {"track_index": track_index, "clip_index": 0})


def _place(client, track_index: int, wav: str, position_beats: float = 0.0) -> None:
    """Replace the source track's content with one unwarped clip of `wav`."""
    _clear_clips(client, track_index)
    try:
        res = client.send("create_arrangement_audio_clip",
                          {"track_index": track_index, "file_path": wav, "position": position_beats})
        client.send("set_clip_warping", {"track_index": track_index,
                                         "clip_index": res.get("clip_index", 0), "warping": False})
    except LiveError as e:
        if "unknown command" in str(e).lower():
            raise ProfileError(
                f"Live's Remote Script is out of date ({e}). Merge "
                "harness/AbletonMCP_Extended/__init__.py into the installed copy in the "
                "Live app bundle (it has diverged — do not overwrite), then restart Live.") from e
        raise


class LiveTarget:
    """profile.py target backed by a running Live: one source track, captured
    silently. The source is tapped 'Post Mixer' (after its fader and pan) and
    both it and the capture track are routed to 'Sends Only', so the test tones
    never reach the master or the speakers, and the master chain is irrelevant."""

    def __init__(self, client, work: Path):
        self.client, self.work, self.takes = client, Path(work), 0
        self.track_index = int(client.send("create_audio_track", {"index": -1})["index"])
        client.send("set_track_name", {"track_index": self.track_index, "name": SRC_TRACK})
        # a template can give new tracks a non-unity fader (measured: -12 dB); 0.85 is 0 dB
        client.send("set_track_volume", {"track_index": self.track_index, "volume": 0.85})
        client.send("set_track_output_routing", {"track_index": self.track_index, "dest_name": "Sends Only"})
        got = client.send("get_track_output_routing", {"track_index": self.track_index}).get("output_routing_type")
        if got != "Sends Only":
            raise ProfileError(f"could not silence the source track: output routing is {got!r}")
        self.node = sa.NodeChain(ref=self.track_index, name=SRC_TRACK, kind="regular")
        # Live's API does not expose the project rate; a recording's header does
        _, sr = self._capture(self.work / "sr_probe.wav", 1.0)
        self.sr = int(sr)

    def _capture(self, out_wav: Path, seconds: float) -> Tuple[np.ndarray, int]:
        bars = int(np.ceil(seconds / 2.0))             # one bar = 2 s at profile.TEMPO
        sa.render_resample(self.client, self.node, out_wav, bars=bars, start_bar=1,
                           channel="Post Mixer", silent=True)
        return sf.read(str(out_wav), dtype="float64", always_2d=True)

    # Live 12 warp modes; the clip is warped at the set tempo (an API-imported
    # clip gets exactly set-tempo beats, measured), so ratio 1:1. LOM values:
    # 5 is the retired REX mode and is rejected, so Complex Pro is 6.
    warp_modes = ["Beats", "Tones", "Texture", "Re-Pitch", "Complex", "Complex Pro"]
    _warp_values = {"Beats": 0, "Tones": 1, "Texture": 2, "Re-Pitch": 3, "Complex": 4, "Complex Pro": 6}

    # Limiters reachable from the browser; params are raw 0..1 values. The probe
    # self-calibrates the ceiling, so only the mode switches matter here.
    limiter_specs = [
        {"name": "Live Limiter mode 0 (Standard)", "uri": "query:AudioFx#Limiter", "params": {"Mode": 0}},
        {"name": "Live Limiter mode 1 (Soft Clip)", "uri": "query:AudioFx#Limiter", "params": {"Mode": 1}},
        {"name": "Live Limiter mode 2 (True Peak)", "uri": "query:AudioFx#Limiter", "params": {"Mode": 2}},
        {"name": "Live Limiter mode 2, lookahead 6 ms", "uri": "query:AudioFx#Limiter", "params": {"Mode": 2, "Lookahead": 2}},
        {"name": "FabFilter Pro-L 2 (defaults)", "uri": "query:Plugins#VST3:FabFilter:Pro-L%202", "params": {}},
    ]

    def play(self, wav: str, position_beats: float, pan: float, seconds: float,
             warp_mode: str | None = None) -> np.ndarray:
        _place(self.client, self.track_index, wav, position_beats)
        if warp_mode is not None:
            self.client.send("set_clip_warping", {"track_index": self.track_index, "clip_index": 0,
                                                  "warping": True})
            self.client.send("set_clip_warp_mode", {"track_index": self.track_index, "clip_index": 0,
                                                    "warp_mode": self._warp_values[warp_mode]})
        self.client.send("set_track_pan", {"track_index": self.track_index, "pan": float(pan)})
        self.takes += 1
        cap, _ = self._capture(self.work / f"take_{self.takes:03d}.wav", seconds)
        return cap

    @contextmanager
    def device(self, spec: dict, track_index: int | None = None):
        """Insert one device on a track (default: the source) for the block's duration."""
        track_index = self.track_index if track_index is None else track_index
        self.client.send("load_browser_item", {"track_index": track_index, "item_uri": spec["uri"]})
        devices = self.client.send("get_track_info", {"track_index": track_index}).get("devices", [])
        index = devices[-1]["index"]
        try:
            for name, value in spec.get("params", {}).items():
                self.client.send("set_device_parameter_by_name",
                                 {"track_index": track_index, "device_index": index,
                                  "param_name": name, "value": value})
            yield index
        finally:
            try:
                self.client.send("delete_device", {"track_index": track_index, "device_index": index})
            except LiveError:
                pass

    # Devices that report latency to Live and pass a quiet signal unchanged
    latency_specs = [
        {"name": "Live Limiter, lookahead setting 2", "uri": "query:AudioFx#Limiter", "params": {"Lookahead": 2}},
        {"name": "FabFilter Pro-L 2 (defaults)", "uri": "query:Plugins#VST3:FabFilter:Pro-L%202", "params": {}},
    ]

    def _ensure_sum_bus(self) -> None:
        """Second source track B plus a fresh return track that sums A and B. The
        return is routed 'Sends Only' too, so the sum never reaches the speakers;
        it is captured Post Mixer like everything else."""
        if getattr(self, "track_b", None) is not None:
            return
        c = self.client
        self.track_b = int(c.send("create_audio_track", {"index": -1})["index"])
        c.send("set_track_name", {"track_index": self.track_b, "name": SRC_TRACK + "_B"})
        c.send("set_track_volume", {"track_index": self.track_b, "volume": 0.85})
        c.send("set_track_output_routing", {"track_index": self.track_b, "dest_name": "Sends Only"})
        ret = c.send("create_return_track")
        self.return_index = int(ret["index"])
        ref = f"return:{self.return_index}"
        c.send("set_track_output_routing", {"track_index": ref, "dest_name": "Sends Only"})
        got = c.send("get_track_output_routing", {"track_index": ref}).get("output_routing_type")
        if got != "Sends Only":
            raise ProfileError(f"could not silence the sum return: output routing is {got!r}")
        for t in (self.track_index, self.track_b):
            c.send("set_send_level", {"track_index": t, "send_index": self.return_index, "level": 1.0})
        self.return_node = sa.NodeChain(ref=ref, name=str(ret.get("name", "")), kind="return")

    def play_sum(self, wav: str, seconds: float, spec: dict | None,
                 mute_a: bool = False, mute_b: bool = False) -> np.ndarray:
        """Sum of tracks A and B (same clip) through the silent return; B carries
        `spec`'s device if given."""
        self._ensure_sum_bus()
        c = self.client
        for t in (self.track_index, self.track_b):
            _place(c, t, wav, 0.0)
            c.send("set_track_pan", {"track_index": t, "pan": 0.0})
        c.send("set_track_mute", {"track_index": self.track_index, "mute": bool(mute_a)})
        c.send("set_track_mute", {"track_index": self.track_b, "mute": bool(mute_b)})
        try:
            self.takes += 1
            out_wav = self.work / f"take_{self.takes:03d}.wav"
            bars = int(np.ceil(seconds / 2.0))
            if spec is None:
                sa.render_resample(c, self.return_node, out_wav, bars=bars, start_bar=1,
                                   channel="Post Mixer", silent=True)
            else:
                with self.device(spec, self.track_b):
                    sa.render_resample(c, self.return_node, out_wav, bars=bars, start_bar=1,
                                       channel="Post Mixer", silent=True)
            cap, _ = sf.read(str(out_wav), dtype="float64", always_2d=True)
            return cap
        finally:
            for t in (self.track_index, self.track_b):
                c.send("set_track_mute", {"track_index": t, "mute": False})

    def close(self) -> None:
        # highest index first so the remaining index stays valid
        owned = [x for x in (self.track_index, getattr(self, "track_b", None)) if x is not None]
        for t in sorted(owned, reverse=True):
            try:
                self.client.send("delete_track", {"track_index": t})
            except LiveError:
                pass
        if getattr(self, "return_index", None) is not None:
            try:
                self.client.send("delete_return_track", {"index": self.return_index})
            except LiveError:
                pass


# --- orchestration -----------------------------------------------------------
def _require_scratch_set(client, track_count: int) -> None:
    """The profile records the master and edits tracks, so refuse anything that
    looks like real work: more tracks than a template, or any arrangement clip."""
    problem = f"{track_count} tracks open" if track_count > MAX_SCRATCH_TRACKS else None
    for i in range(track_count if problem is None else 0):
        try:
            if int(client.send("get_arrangement_clips", {"track_index": i}).get("clip_count", 0)):
                problem = f"track {i} has arrangement clips"
                break
        except LiveError:
            continue
    if problem:
        raise ProfileError(f"{problem} — this looks like a real set. Open an empty scratch "
                           f"set, or pass --force.")


def run_profile(client, out_dir: Path, force: bool = False) -> Dict[str, Any]:
    info = client.send("get_session_info")
    if not force:
        _require_scratch_set(client, int(info.get("track_count", 0)))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    orig_tempo = info.get("tempo")
    target = None
    try:
        client.send("set_tempo", {"tempo": profile.TEMPO})
        target = LiveTarget(client, out_dir)
        return profile.run_probes(target, out_dir, "live_profile")
    finally:
        if target is not None:
            target.close()
        if orig_tempo is not None:
            try:
                client.send("set_tempo", {"tempo": orig_tempo})
            except LiveError:
                pass


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=str(_ROOT / "sandbox_sessions" / "live_profile"))
    ap.add_argument("--force", action="store_true", help="run even if the set has many tracks")
    args = ap.parse_args(argv)
    try:
        with LiveClient(timeout=45) as client:
            profile = run_profile(client, Path(args.out), force=args.force)
    except (ProfileError, LiveError) as e:
        print(f"live profile failed: {e}")
        return 2
    print(json.dumps(profile, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
