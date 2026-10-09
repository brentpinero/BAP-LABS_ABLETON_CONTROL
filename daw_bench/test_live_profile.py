"""
test_live_profile.py — the Live profile driver against a FAKE Live with known
behaviour (a pan law, a record latency, a 4 ms clip-edge fade, a clean or an
aliasing resampler). The probes must recover exactly what the fake was built
with. No Ableton. Run: python daw_bench/test_live_profile.py (or pytest).
"""
from __future__ import annotations

import sys
import tempfile
import time
import types
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import firwin, resample_poly

sys.path.insert(0, str(Path(__file__).parent))

import live_profile as lp  # noqa: E402
import measure  # noqa: E402
import profile  # noqa: E402
import ref_engine  # noqa: E402
from live_client import LiveError  # noqa: E402

# the fake renders instantly: stub sleep on stem_ablation's own `time` reference
# only, leaving the real time module untouched for the rest of the process
lp.sa.time = types.SimpleNamespace(sleep=lambda s: None, time=time.time)


class FakeLive:
    """Renders the source track's clip to a stereo 'master recording' on
    start_playback, applying the modelled engine behaviour."""

    def __init__(self, tmp: Path, sr: int = 48000, pan_law: str = "sin_0_+3",
                 latency: int = 64, fade_ms: float = 4.0, clean_src: bool = True,
                 has_audio_clip_cmd: bool = True, track_count: int = 2):
        self.tmp, self.sr, self.pan_law = tmp, sr, pan_law
        self.latency, self.fade_ms, self.clean_src = latency, fade_ms, clean_src
        self.has_audio_clip_cmd = has_audio_clip_cmd
        self.tracks = [{"name": f"T{i}", "pan": 0.0, "clips": [], "devices": []} for i in range(track_count)]
        self.warp_calls = []
        self.tempo, self.routing, self.takes, self.calls = 97.0, {}, 0, []
        self.master_on = {0: True, 1: False}      # Pro-L style limiter ON, a meter OFF

    def _render(self) -> str:
        src = next((t for t in self.tracks if t["name"] == lp.SRC_TRACK), None)
        seconds = 12.0
        out = np.zeros((int(seconds * self.sr), 2))
        for path, beats in (src["clips"] if src else []):
            audio, file_sr = sf.read(path, dtype="float64")
            if file_sr != self.sr:                       # realtime sample-rate conversion
                down = file_sr // self.sr
                audio = (resample_poly(audio, 1, down, window=firwin(
                    401, 0.47 * self.sr, fs=file_sr, window=("kaiser", 12.0)))
                    if self.clean_src else audio[::down])
            n = int(self.fade_ms * self.sr / 1000.0)     # clip-edge fade
            if n:
                audio = audio.copy()
                audio[:n] *= np.linspace(0.0, 1.0, n)
            if src.get("devices"):                       # a loaded limiter: hard clip at -1 dBFS
                audio = np.clip(audio, -10 ** (-1 / 20), 10 ** (-1 / 20))
            gl, gr = measure.pan_gains(self.pan_law, src["pan"])
            at = int(round(beats * 60.0 / self.tempo * self.sr)) + self.latency
            end = min(len(out), at + len(audio))
            out[at:end, 0] += gl * audio[:end - at]
            out[at:end, 1] += gr * audio[:end - at]
        self.takes += 1
        path = self.tmp / f"take_{self.takes}.wav"
        sf.write(str(path), out.astype("float32"), self.sr, subtype="FLOAT")
        return str(path)

    def send(self, cmd, params=None):
        p = params or {}
        self.calls.append((cmd, p))
        t = self.tracks[p["track_index"]] if isinstance(p.get("track_index"), int) \
            and 0 <= p["track_index"] < len(self.tracks) else None
        if cmd == "get_master_track":
            return {"devices": [{"index": i, "name": f"Dev{i}"} for i in self.master_on]}
        if cmd == "get_device_parameters" and p.get("track_index") == -1:
            return {"parameters": [{"name": "Device On", "value": 1.0 if self.master_on[p["device_index"]] else 0.0}]}
        if cmd == "set_device_enabled" and p.get("track_index") == -1:
            self.master_on[p["device_index"]] = bool(p["enabled"])
            return {}
        if cmd == "get_session_info":
            return {"tempo": self.tempo, "track_count": len(self.tracks), "signature_numerator": 4}
        if cmd == "set_tempo":
            self.tempo = p["tempo"]
        elif cmd == "create_audio_track":
            self.tracks.append({"name": "Audio", "pan": 0.0, "clips": [], "devices": []})
            return {"index": len(self.tracks) - 1}
        elif cmd == "set_track_name":
            t["name"] = p["name"]
        elif cmd == "get_track_info":
            if t is None:
                raise LiveError("no such track")
            return {"name": t["name"], "solo": False,
                    "devices": [{"index": i, "name": d} for i, d in enumerate(t["devices"])]}
        elif cmd == "load_browser_item":
            t["devices"].append(p["item_uri"])
        elif cmd == "delete_device":
            t["devices"].pop(p["device_index"])
        elif cmd in ("set_clip_warping", "set_clip_warp_mode", "set_device_parameter_by_name"):
            self.warp_calls.append((cmd, p))
        elif cmd == "delete_track":
            self.tracks.pop(p["track_index"])
        elif cmd == "set_track_pan":
            t["pan"] = p["pan"]
        elif cmd == "create_arrangement_audio_clip":
            if not self.has_audio_clip_cmd:
                raise LiveError("Unknown command: create_arrangement_audio_clip")
            t["clips"].append((p["file_path"], p["position"]))
            return {"clip_index": len(t["clips"]) - 1}
        elif cmd == "get_arrangement_clips":
            return {"clip_count": len(t["clips"])}
        elif cmd == "delete_arrangement_clip":
            t["clips"].pop(p["clip_index"])
        elif cmd == "set_track_input_routing":
            self.routing[p["track_index"]] = p["source_name"]
            self.tap_channel = p.get("channel")
        elif cmd == "get_track_input_routing":
            return {"input_routing_type": self.routing.get(p["track_index"])}
        elif cmd == "set_track_output_routing":
            t["out"] = p["dest_name"]
        elif cmd == "get_track_output_routing":
            return {"output_routing_type": t.get("out", "Master")}
        elif cmd == "set_song_loop":
            return {"previous": False}
        elif cmd == "start_playback":
            self.last_take = self._render()
        elif cmd == "get_audio_clip_properties":
            return {"file_path": self.last_take}
        return {}


def _run(**model):
    with tempfile.TemporaryDirectory() as d:
        live = FakeLive(Path(d), **model)
        profile = lp.run_profile(live, Path(d) / "out")
        return live, profile


def test_profile_recovers_live_like_behaviour():
    live, prof = _run(pan_law="sin_0_+3", latency=64, fade_ms=4.0, clean_src=True)
    assert prof["project_sr"] == 48000
    assert prof["pan"]["fit"]["law"] == "sin_0_+3", prof["pan"]
    assert prof["pan"]["fit"]["max_error_db"] < 0.05
    assert abs(prof["pan"]["left_db"][4]) < 0.05          # centre position: 0 dB
    assert prof["unity"]["latency_samples"] == 64
    assert abs(prof["unity"]["gain_db"]) < 0.01
    assert 3.0 < prof["edge_fade"]["fade_in_ms"] < 4.3, prof["edge_fade"]
    assert prof["src"]["alias_db"] < -80.0, prof["src"]
    assert prof["src"]["passband_ripple_db"] < 0.1, prof["src"]
    # warp (identity in the fake): every Live mode probed, 1:1, transparent
    assert set(prof["warp"]) == set(lp.LiveTarget.warp_modes)
    for mode, r in prof["warp"].items():                      # the fake's 4 ms fades bound both
        assert abs(r["length_error_ms"]) < 3.0 and r["null_depth_db"] > 60.0, (mode, r)
    assert ("set_clip_warp_mode", {"track_index": 2, "clip_index": 0, "warp_mode": 5}) in live.warp_calls
    # limiter (hard clip at -1 dBFS in the fake): ceiling read back, ISP overshoot = 3 dB
    for name, r in prof["limiter"].items():
        assert abs(r["ceiling_dbfs"] + 1.0) < 0.05, (name, r)
        assert 2.8 < r["isp_overshoot_db"] < 3.2, (name, r)
    assert not live.tracks[2]["devices"] if len(live.tracks) > 2 else True   # devices removed


def test_profile_tells_engines_apart():
    _, prof = _run(pan_law="sin_-3_0", latency=0, fade_ms=0.0, clean_src=False)
    assert prof["pan"]["fit"]["law"] == "sin_-3_0"
    assert abs(prof["pan"]["left_db"][4] + 3.01) < 0.05    # centre cut by 3 dB
    assert prof["unity"]["latency_samples"] == 0
    assert prof["unity"]["residual_dbfs"] < -140.0         # pure passthrough nulls
    assert prof["edge_fade"]["fade_in_ms"] < 0.5
    assert prof["src"]["alias_db"] > -6.0                  # unfiltered decimation aliases
                                                           # (full level, less the 3 dB centre cut)


def test_cleans_up_and_restores_tempo():
    live, _ = _run()
    assert [t["name"] for t in live.tracks] == ["T0", "T1"]   # source + capture tracks gone
    assert live.tempo == 97.0
    assert live.master_on == {0: True, 1: False}              # master chain untouched
    assert not any(c == "set_device_enabled" for c, _ in live.calls)


def test_capture_is_silent():
    live, _ = _run()
    routed = [(p["track_index"], p["dest_name"]) for c, p in live.calls if c == "set_track_output_routing"]
    assert routed and all(d == "Sends Only" for _, d in routed)      # source and every capture track
    assert len({t for t, _ in routed}) >= 2
    assert live.tap_channel == "Post Mixer"                          # pan and fader included


def test_refuses_a_real_looking_set():
    with tempfile.TemporaryDirectory() as d:
        live = FakeLive(Path(d), track_count=12)
        try:
            lp.run_profile(live, Path(d) / "out")
            raise AssertionError("should have refused")
        except profile.ProfileError as e:
            assert "scratch set" in str(e)
        assert len(live.tracks) == 12 and live.tempo == 97.0   # untouched


def test_refuses_a_small_set_that_has_clips():
    with tempfile.TemporaryDirectory() as d:
        live = FakeLive(Path(d))
        live.tracks[0]["clips"].append(("song.wav", 0.0))
        try:
            lp.run_profile(live, Path(d) / "out")
            raise AssertionError("should have refused")
        except profile.ProfileError as e:
            assert "arrangement clips" in str(e)
        assert len(live.tracks) == 2 and live.tracks[0]["clips"]   # untouched


def test_stale_remote_script_gives_actionable_error():
    with tempfile.TemporaryDirectory() as d:
        live = FakeLive(Path(d), has_audio_clip_cmd=False)
        try:
            lp.run_profile(live, Path(d) / "out")
            raise AssertionError("should have failed")
        except profile.ProfileError as e:
            assert "Remote Script" in str(e)
        assert [t["name"] for t in live.tracks] == ["T0", "T1"]  # still cleaned up


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")


# --- the executable spec must pass its own spec --------------------------------
def test_reference_engine_meets_section_3_spec():
    with tempfile.TemporaryDirectory() as d:
        prof = profile.run_probes(ref_engine.RefEngine(48000), Path(d), "ref")
    assert prof["pan"]["fit"]["law"] == "sin_-3_0", prof["pan"]["fit"]
    assert prof["pan"]["fit"]["max_error_db"] < 0.01
    assert prof["unity"]["latency_samples"] == 0
    assert prof["unity"]["residual_dbfs"] < -100.0           # only the 4 ms edge fades differ
    assert 3.0 < prof["edge_fade"]["fade_in_ms"] < 4.3, prof["edge_fade"]  # raised-cosine 4 ms reads ~3.3
    assert prof["src"]["passband_ripple_db"] < 0.01, prof["src"]
    assert prof["src"]["alias_db"] < -120.0, prof["src"]


def test_reference_engine_live_compatible_mode():
    with tempfile.TemporaryDirectory() as d:
        prof = profile.run_probes(ref_engine.RefEngine(44100, pan_law="sin_0_+3", edge_fade_ms=0.0),
                                  Path(d), "ref")
    assert prof["project_sr"] == 44100
    assert prof["pan"]["fit"]["law"] == "sin_0_+3"
    assert prof["edge_fade"]["fade_in_ms"] < 0.5
    assert prof["unity"]["residual_dbfs"] < -140.0           # fades off: pure passthrough
    assert prof["warp"]["bypass"]["residual_dbfs"] < -140.0  # spec: stretcher bypassed at 1:1
    assert prof["limiter"] == {"skipped": "target cannot insert limiters"}
