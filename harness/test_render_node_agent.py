"""
test_render_node_agent.py — offline tests for the on-node render agent.

No macOS/osascript, no Ableton, no network server — the automator is injected as
a fake, and framing is exercised over an in-process socketpair.
Run: python harness/test_render_node_agent.py  (or pytest).
"""
from __future__ import annotations

import base64
import socket
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import render_node_agent as rna  # noqa: E402


def test_framing_roundtrip():
    a, b = socket.socketpair()
    try:
        payload = {"action": "ping", "params": {"x": [1, 2, 3], "s": "hïgh"}}
        rna.send_framed(a, payload)
        assert rna.recv_framed(b) == payload
    finally:
        a.close()
        b.close()


def test_ping():
    assert rna.handle_request({"action": "ping"})["result"]["pong"] is True


def test_automator_dispatch_uses_injected_fn():
    calls = []

    def fake(cmd, params):
        calls.append((cmd, params))
        return {"success": True, "cmd": cmd}

    resp = rna.handle_request(
        {"action": "automator", "params": {"command_type": "automator_freeze", "params": {"a": 1}}},
        automator_fn=fake)
    assert resp["status"] == "ok"
    assert resp["result"]["cmd"] == "automator_freeze"
    assert calls == [("automator_freeze", {"a": 1})]


def test_fetch_wav_returns_bytes():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "stem.wav"
        p.write_bytes(b"RIFFxxxxWAVE-data")
        resp = rna.handle_request({"action": "fetch_wav", "params": {"path": str(p)}})
        assert resp["status"] == "ok"
        assert base64.b64decode(resp["result"]["wav_b64"]) == b"RIFFxxxxWAVE-data"
        assert resp["result"]["name"] == "stem.wav"


def test_freeze_capture_waits_for_new_wav():
    with tempfile.TemporaryDirectory() as d:
        freeze_dir = Path(d)

        # the "automator" writes the freeze wav as a side effect, like Live does
        def fake_freeze(cmd, params):
            (freeze_dir / "Freeze Test-1.wav").write_bytes(b"\x00" * 4096)
            return {"success": True}

        resp = rna.handle_request(
            {"action": "freeze_capture",
             "params": {"freeze_dir": str(freeze_dir), "timeout_s": 5.0}},
            automator_fn=fake_freeze)
        assert resp["status"] == "ok", resp
        assert len(base64.b64decode(resp["result"]["wav_b64"])) == 4096
        assert resp["result"]["name"] == "Freeze Test-1.wav"


def test_freeze_capture_reports_failure():
    with tempfile.TemporaryDirectory() as d:
        resp = rna.handle_request(
            {"action": "freeze_capture", "params": {"freeze_dir": d, "timeout_s": 2.0}},
            automator_fn=lambda *a: {"success": False, "why": "no accessibility"})
        assert resp["status"] == "error"
        assert "freeze automation failed" in resp["message"]


def test_fetch_wav_client_writes_to_host(monkeypatch=None):
    """RenderNodeClient.fetch_wav pulls a node-local wav back to a host path
    (used to retrieve resampling-recorded stems from a remote node)."""
    with tempfile.TemporaryDirectory() as d:
        node_wav = Path(d) / "recorded.wav"
        node_wav.write_bytes(b"RIFFyyyyWAVE-stem")
        host_out = Path(d) / "host" / "lead.wav"

        client = rna.RenderNodeClient("127.0.0.1", 0)
        # exercise the base64 write path directly via handle_request (no socket)
        resp = rna.handle_request({"action": "fetch_wav", "params": {"path": str(node_wav)}})
        host_out.parent.mkdir(parents=True, exist_ok=True)
        host_out.write_bytes(base64.b64decode(resp["result"]["wav_b64"]))
        assert host_out.read_bytes() == b"RIFFyyyyWAVE-stem"
        assert hasattr(client, "fetch_wav")


def test_unknown_action():
    assert rna.handle_request({"action": "bogus"})["status"] == "error"


def test_client_server_end_to_end():
    """Spin the real server on an ephemeral port, drive it with RenderNodeClient,
    but keep the automator fake (patched onto the module) so no GUI is touched."""
    orig = rna._local_automator
    rna._local_automator = lambda cmd, params: {"success": True, "echo": cmd}
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    port = srv.getsockname()[1]
    srv.listen(1)

    def serve_once():
        conn, _ = srv.accept()
        try:
            rna.send_framed(conn, rna.handle_request(rna.recv_framed(conn)))
        finally:
            conn.close()

    t = threading.Thread(target=serve_once, daemon=True)
    t.start()
    try:
        client = rna.RenderNodeClient("127.0.0.1", port, timeout=5.0)
        assert client.automator("automator_freeze")["echo"] == "automator_freeze"
    finally:
        rna._local_automator = orig
        srv.close()
        t.join(timeout=2)


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  PASS  {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} tests passed.")


if __name__ == "__main__":
    _run_all()
