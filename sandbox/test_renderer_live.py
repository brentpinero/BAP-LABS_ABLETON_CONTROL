"""
test_renderer_live.py — offline tests for the Ableton-render-node renderer.

No Ableton, no network: LiveClient / RenderNodeClient / live_freeze helpers are
monkeypatched with fakes so we exercise the orchestration, the {"audio": ...}
contract, per-role caching, and fallback-role skipping.
Run: python sandbox/test_renderer_live.py  (or pytest).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import soundfile as sf

_ROOT = Path(__file__).resolve().parent.parent
for _p in (str(_ROOT / "sandbox"), str(_ROOT / "harness"),
           str(_ROOT / "harness" / "AbletonMCP_Extended")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import renderer_live  # noqa: E402
import renderer as sandbox_renderer  # noqa: E402


# ── fakes ────────────────────────────────────────────────────────────────────

class _FakeTrack:
    def __init__(self, instrument_spec, params=None, gain_db=0.0, pan=0.0):
        self.instrument_spec = instrument_spec
        self.params = params
        self.gain_db = gain_db
        self.pan = pan


class _FakeSession:
    def __init__(self, tmp: Path, tracks, overrides, bpm=100.0, bars=4):
        self._dir = tmp
        self.tracks = tracks
        self.bpm = bpm
        self.config = SimpleNamespace(overrides=overrides, bars=bars)

    def dir(self):
        return self._dir


class _FakeLiveClient:
    def __init__(self, *a, **k):
        self._tracks = 2

    def connect(self):
        return self

    def send(self, cmd, params=None):
        if cmd == "get_session_info":
            return {"tempo": 120.0, "track_count": self._tracks}
        if cmd in ("create_midi_track", "create_audio_track"):
            self._tracks += 1
            return {"index": self._tracks - 1}  # create commands return the new index
        return {}

    def close(self):
        pass


class _FakeNode:
    """freeze_capture writes a real 1s stereo wav so sum_stems_to_master can read it."""
    def __init__(self, *a, **k):
        self.calls = 0

    def freeze_capture(self, freeze_dir, out_path, timeout_s=120.0, **k):
        self.calls += 1
        n = int(0.2 * 48000)
        sig = (0.1 * np.random.default_rng(self.calls).standard_normal((n, 2))).astype("float32")
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        sf.write(out_path, sig, 48000)
        return Path(out_path)

    def automator(self, *a, **k):
        return {"success": True}


def _patch(monkey_targets):
    """Monkeypatch the lazily-imported symbols; return a restore() callable."""
    import live_client, render_node_agent, live_freeze
    saved = {}
    for mod, name, val in monkey_targets:
        saved[(mod, name)] = getattr(mod, name, None)
        setattr(mod, name, val)

    def restore():
        for (mod, name), val in saved.items():
            setattr(mod, name, val)
    return restore, (live_client, render_node_agent, live_freeze)


# ── pure-helper tests ────────────────────────────────────────────────────────

def test_device_query_mapping():
    f = renderer_live._device_query_for
    assert f("vst:/Library/Audio/Plug-Ins/VST3/Serum2.vst3::name=Serum 2") == "Serum 2"
    assert f("vst:/x/Massive X.vst3") == "Massive X"
    assert f("au:/x/Zebra2.component") == "Zebra2"
    assert f("fallback:bass") is None
    assert f("") is None


def test_role_cache_key_stability_and_sensitivity():
    k = renderer_live._role_cache_key
    base = k([{"pitch": 60}], "vst:x::name=Serum 2", {"A": 1.0}, 100, 4, 48000)
    assert base == k([{"pitch": 60}], "vst:x::name=Serum 2", {"A": 1.0}, 100, 4, 48000)
    assert base != k([{"pitch": 61}], "vst:x::name=Serum 2", {"A": 1.0}, 100, 4, 48000)
    assert base != k([{"pitch": 60}], "vst:x::name=Serum 2", {"A": 2.0}, 100, 4, 48000)
    assert base != k([{"pitch": 60}], "vst:x::name=Serum 2", {"A": 1.0}, 100, 4, 44100)


def test_sum_stems_to_master_regression():
    with tempfile.TemporaryDirectory() as d:
        it_dir = Path(d)
        for role in ("a", "b"):
            sf.write(it_dir / f"{role}.wav",
                     (0.2 * np.ones((1000, 2))).astype("float32"), 48000)
        session = _FakeSession(it_dir, {"a": _FakeTrack("vst:x"), "b": _FakeTrack("vst:x")}, {})
        audio = {"a": str(it_dir / "a.wav"), "b": str(it_dir / "b.wav")}
        sandbox_renderer.sum_stems_to_master(session, audio, it_dir, 48000)
        assert "master" in audio
        m, _ = sf.read(audio["master"])
        assert m.shape[0] == 1000 and abs(np.max(np.abs(m))) <= 0.985 + 1e-6


def test_dispatch_routes_by_backend():
    calls = {}
    orig = sandbox_renderer.render_iteration
    sandbox_renderer.render_iteration = lambda s, r: calls.setdefault("pedalboard", True) or {"audio": {}}
    try:
        session = _FakeSession(Path("/tmp"), {}, {"render.backend": "pedalboard"})
        sandbox_renderer.render_iteration_dispatch(session, SimpleNamespace(index=0, grooved={}))
        assert calls.get("pedalboard")
        # unimplemented backend surfaces clearly rather than silently mis-rendering
        session2 = _FakeSession(Path("/tmp"), {}, {"render.backend": "dawdreamer"})
        try:
            sandbox_renderer.render_iteration_dispatch(session2, SimpleNamespace(index=0, grooved={}))
            assert False, "expected NotImplementedError"
        except NotImplementedError:
            pass
    finally:
        sandbox_renderer.render_iteration = orig


def test_render_iteration_live_contract_and_skips():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        tracks = {
            "lead": _FakeTrack("vst:/x/Serum2.vst3::name=Serum 2", {"MacroKnob 1": 0.5}),
            "drums": _FakeTrack("fallback:drums"),   # should be SKIPPED on the node
            "empty": _FakeTrack("vst:/x/Serum2.vst3::name=Serum 2"),
        }
        session = _FakeSession(tmp, tracks, {"render.node_project_dir": str(tmp / "proj"),
                                             "render.node_render_mode": "freeze"})
        record = SimpleNamespace(index=1, grooved={
            "lead": [{"pitch": 60, "start_time": 0.0, "duration": 1.0, "velocity": 100}],
            "drums": [{"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 100}],
            "empty": [],
        })
        node = _FakeNode()
        restore, (live_client, render_node_agent, live_freeze) = _patch([
            (__import__("live_client"), "LiveClient", _FakeLiveClient),
            (__import__("render_node_agent"), "RenderNodeClient", lambda *a, **k: node),
            (__import__("live_freeze"), "find_freeze_dir", lambda p: Path(p) / "Samples/Processed/Freeze"),
            (__import__("live_freeze"), "_load_device", lambda *a, **k: None),
            (__import__("live_freeze"), "_delete_tagged_track", lambda *a, **k: None),
        ])
        try:
            out = renderer_live.render_iteration_live(session, record)
        finally:
            restore()

        audio, pool = out["audio"], {r["role"]: r for r in out["pool"]}
        assert "lead" in audio and "master" in audio          # real VST role rendered + master summed
        assert pool["lead"]["status"] == "rendered"
        assert pool["drums"]["status"] == "skipped"           # fallback role not sent to node
        assert pool["empty"]["status"] == "skipped"           # empty notes skipped
        assert node.calls == 1                                # only the one real role froze

        # second render of identical inputs hits the per-role cache (no new freeze)
        record2 = SimpleNamespace(index=2, grooved=dict(record.grooved))
        restore2, _ = _patch([
            (__import__("live_client"), "LiveClient", _FakeLiveClient),
            (__import__("render_node_agent"), "RenderNodeClient", lambda *a, **k: node),
            (__import__("live_freeze"), "find_freeze_dir", lambda p: Path(p) / "Samples/Processed/Freeze"),
            (__import__("live_freeze"), "_load_device", lambda *a, **k: None),
            (__import__("live_freeze"), "_delete_tagged_track", lambda *a, **k: None),
        ])
        try:
            out2 = renderer_live.render_iteration_live(session, record2)
        finally:
            restore2()
        assert {r["role"]: r["status"] for r in out2["pool"]}["lead"] == "cached"
        assert node.calls == 1                                # cache hit → no second freeze


class _FakeLiveClientResample:
    """Simulates the LOM commands the resampling path uses: track create/name,
    input routing, arm, record mode, transport, and get_audio_clip_properties
    returning a real recorded wav so the renderer can retrieve it."""
    def __init__(self, *a, **k):
        self.names: list = []
        self._tmp = Path(tempfile.mkdtemp(prefix="resample_"))
        self.record_calls = 0
        self.armed: list = []
        self.routed: dict = {}

    def connect(self):
        return self

    def send(self, cmd, params=None):
        params = params or {}
        if cmd == "get_session_info":
            return {"tempo": 120.0, "track_count": len(self.names)}
        if cmd in ("create_midi_track", "create_audio_track"):
            self.names.append("")
            return {"index": len(self.names) - 1}
        if cmd == "set_track_name":
            self.names[params["track_index"]] = params["name"]
            return {}
        if cmd == "get_track_info":
            i = params["track_index"]
            if 0 <= i < len(self.names):
                return {"name": self.names[i]}
            raise RuntimeError("no such track")
        if cmd == "set_track_arm" and params.get("arm"):
            self.armed.append(self.names[params["track_index"]])
        if cmd == "set_track_input_routing":
            self.routed[self.names[params["track_index"]]] = params.get("source_name")
        if cmd == "set_record_mode" and params.get("mode") == 1:
            self.record_calls += 1
        if cmd == "get_audio_clip_properties":
            name = self.names[params["track_index"]]
            fp = self._tmp / f"{name}.wav"
            n = int(0.2 * 48000)
            sf.write(fp, (0.1 * np.random.default_rng(len(name)).standard_normal((n, 2))
                         ).astype("float32"), 48000)
            return {"file_path": str(fp), "length": 4.0}
        return {}

    def close(self):
        pass


def test_render_iteration_live_resample_one_pass():
    """render.node_render_mode='resample' captures all real roles in ONE real-time
    record pass over the LOM (no GUI), maps each recorded stem to its role, and
    yields the same {audio, pool} contract."""
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        tracks = {
            "lead": _FakeTrack("vst:/x/Serum2.vst3::name=Serum 2", {"MacroKnob 1": 0.5}),
            "sub": _FakeTrack("vst:/x/Serum2.vst3::name=Serum 2"),
            "drums": _FakeTrack("fallback:drums"),   # skipped (fast tier)
        }
        # bpm/bars kept tiny so the real-time record sleep stays short in the test
        session = _FakeSession(tmp, tracks, {
            "render.node_project_dir": str(tmp / "proj"),
            "render.node_render_mode": "resample",
            "render.node_record_tail_s": 0.0,
        }, bpm=240.0, bars=1)
        record = SimpleNamespace(index=1, grooved={
            "lead": [{"pitch": 60, "start_time": 0.0, "duration": 1.0, "velocity": 100}],
            "sub": [{"pitch": 36, "start_time": 0.0, "duration": 2.0, "velocity": 100}],
            "drums": [{"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 100}],
        })
        client_holder = {}

        def _mk_client(*a, **k):
            c = _FakeLiveClientResample()
            client_holder["c"] = c
            return c

        node = SimpleNamespace(fetch_wav=lambda *a, **k: None)
        restore, _ = _patch([
            (__import__("live_client"), "LiveClient", _mk_client),
            (__import__("render_node_agent"), "RenderNodeClient", lambda *a, **k: node),
            (__import__("live_freeze"), "find_freeze_dir", lambda p: Path(p) / "Samples/Processed/Freeze"),
            (__import__("live_freeze"), "_load_device", lambda *a, **k: None),
            (__import__("live_freeze"), "_delete_tagged_track", lambda *a, **k: None),
        ])
        try:
            out = renderer_live.render_iteration_live(session, record)
        finally:
            restore()

        audio, pool = out["audio"], {r["role"]: r for r in out["pool"]}
        assert client_holder["c"].record_calls == 1       # ONE record pass for BOTH real roles
        assert len(client_holder["c"].armed) == 2         # both capture tracks armed
        assert pool["lead"]["status"] == "rendered"
        assert pool["sub"]["status"] == "rendered"
        assert pool["drums"]["status"] == "skipped"
        assert "lead" in audio and "sub" in audio and "master" in audio


def test_render_live_requires_node_project_dir():
    session = _FakeSession(Path("/tmp"), {}, {"render.node_project_dir": ""})
    try:
        renderer_live.render_iteration_live(session, SimpleNamespace(index=0, grooved={}))
        assert False, "expected ValueError for empty node_project_dir"
    except ValueError as e:
        assert "node_project_dir" in str(e)


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  PASS  {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} tests passed.")


if __name__ == "__main__":
    _run_all()
