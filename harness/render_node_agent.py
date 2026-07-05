"""
render_node_agent.py — on-node bridge for the isolated Ableton render node.

The render node is a SEPARATE Ableton instance (VM / 2nd machine / cloud) that
the model drives but the user never touches. Two things can't cross the network
by themselves:
  1. GUI automation (Freeze / Export) — osascript runs only where the Ableton
     GUI lives, so it must execute ON the node.
  2. The freeze/export wav — it's written to the node's local disk.

This module is BOTH:
  • the server (`serve`) that runs ON the node: a length-framed JSON socket that
    dispatches automator commands to `automator_bridge` and can read back the
    rendered wav bytes. Start it on the node with:  python render_node_agent.py
  • the client (`RenderNodeClient`) that runs on the HOST: the loop calls it to
    trigger a freeze and pull the resulting wav back, machine-agnostically.

LOM operations (create track, load device, add notes) do NOT go through here —
they use `LiveClient(host=<node>)` against the node's Remote Script socket
directly, which is already network-transparent.

Wire format (length-framed, robust for multi-MB wav payloads):
    4-byte big-endian uint32 length  +  UTF-8 JSON body
Request:  {"action": "automator"|"freeze_capture"|"fetch_wav"|"ping", "params": {...}}
Reply:    {"status": "ok"|"error", "result": {...}} | {"status":"error","message":...}
"""
from __future__ import annotations

import base64
import json
import socket
import struct
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE / "AbletonMCP_Extended") not in sys.path:
    sys.path.insert(0, str(_HERE / "AbletonMCP_Extended"))

DEFAULT_AGENT_PORT = 9878
_MAX_PAYLOAD = 256 * 1024 * 1024  # 256 MB ceiling — a wav stem is a few MB


# ── framed socket helpers (shared by server + client) ───────────────────────

def send_framed(sock: socket.socket, obj: Dict[str, Any]) -> None:
    body = json.dumps(obj).encode("utf-8")
    sock.sendall(struct.pack(">I", len(body)) + body)


def _recv_exactly(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(min(65536, n - len(buf)))
        if not chunk:
            raise ConnectionError("connection closed mid-frame")
        buf.extend(chunk)
    return bytes(buf)


def recv_framed(sock: socket.socket) -> Dict[str, Any]:
    (length,) = struct.unpack(">I", _recv_exactly(sock, 4))
    if length > _MAX_PAYLOAD:
        raise ValueError(f"frame too large: {length} bytes")
    return json.loads(_recv_exactly(sock, length).decode("utf-8"))


# ── request handling (pure; unit-testable without a socket) ──────────────────

def handle_request(req: Dict[str, Any], automator_fn=None) -> Dict[str, Any]:
    """Dispatch one agent request. `automator_fn(command_type, params) -> dict`
    is injectable so tests don't need macOS/osascript. Returns a reply dict."""
    action = req.get("action")
    params = req.get("params") or {}
    try:
        if action == "ping":
            return {"status": "ok", "result": {"pong": True}}

        if action == "automator":
            fn = automator_fn or _local_automator
            res = fn(params["command_type"], params.get("params") or {})
            return {"status": "ok", "result": res}

        if action == "fetch_wav":
            data = Path(params["path"]).read_bytes()
            return {"status": "ok", "result": {"name": Path(params["path"]).name,
                                               "wav_b64": base64.b64encode(data).decode("ascii")}}

        if action == "freeze_capture":
            # freeze the GUI-focused track, wait for the NEW stable wav in the
            # node's freeze folder, and return its bytes — all node-local.
            fn = automator_fn or _local_automator
            freeze_dir = Path(params["freeze_dir"])
            timeout_s = float(params.get("timeout_s", 120.0))
            before = set(freeze_dir.glob("*.wav")) if freeze_dir.exists() else set()
            res = fn(params.get("command_type", "automator_freeze"), {})
            if not res.get("success", False):
                return {"status": "error", "message": f"freeze automation failed: {res}"}
            wav = _wait_for_new_wav(freeze_dir, before, timeout_s)
            data = wav.read_bytes()
            return {"status": "ok", "result": {"name": wav.name,
                                               "wav_b64": base64.b64encode(data).decode("ascii")}}

        return {"status": "error", "message": f"unknown action: {action}"}
    except Exception as e:  # noqa: BLE001 — report, don't crash the daemon
        return {"status": "error", "message": f"{type(e).__name__}: {e}"}


def _local_automator(command_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    import automator_bridge  # node-only (macOS Accessibility); imported lazily
    return automator_bridge.handle_automator_command(command_type, params or {})


def _wait_for_new_wav(freeze_dir: Path, before: set, timeout_s: float,
                      poll_s: float = 0.5) -> Path:
    """Poll for a NEW, size-stable wav (mirrors live_freeze._wait_for_new_wav)."""
    deadline = time.monotonic() + timeout_s
    last_size: Dict[Path, int] = {}
    while time.monotonic() < deadline:
        now = set(freeze_dir.glob("*.wav")) if freeze_dir.exists() else set()
        for f in sorted(now - before, key=lambda p: p.stat().st_mtime):
            size = f.stat().st_size
            if size > 1000 and last_size.get(f) == size:  # stable across two polls
                return f
            last_size[f] = size
        time.sleep(poll_s)
    raise TimeoutError(
        f"No new freeze wav in {freeze_dir} within {timeout_s}s — check the node's "
        f"Live has a SAVED project and Accessibility permission for automation.")


# ── server (runs ON the node) ────────────────────────────────────────────────

def serve(host: str = "0.0.0.0", port: int = DEFAULT_AGENT_PORT) -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(4)
    print(f"render_node_agent listening on {host}:{port} — "
          f"drives THIS node's Ableton GUI (freeze/export) on request")
    while True:
        conn, addr = srv.accept()
        try:
            req = recv_framed(conn)
            send_framed(conn, handle_request(req))
        except Exception as e:  # noqa: BLE001 — one bad request never kills the daemon
            try:
                send_framed(conn, {"status": "error", "message": f"{type(e).__name__}: {e}"})
            except Exception:
                pass
        finally:
            conn.close()


# ── client (runs on the HOST, inside the loop) ───────────────────────────────

class RenderNodeClient:
    """Host-side client for the node agent. Machine-agnostic freeze/export."""

    def __init__(self, host: str = "127.0.0.1", port: int = DEFAULT_AGENT_PORT,
                 timeout: float = 180.0):
        self.host, self.port, self.timeout = host, port, timeout

    def _call(self, action: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        try:
            s.connect((self.host, self.port))
            send_framed(s, {"action": action, "params": params or {}})
            resp = recv_framed(s)
        finally:
            s.close()
        if resp.get("status") == "error":
            raise RuntimeError(f"render node agent: {resp.get('message')}")
        return resp.get("result", {})

    def ping(self) -> bool:
        return bool(self._call("ping").get("pong"))

    def automator(self, command_type: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return self._call("automator", {"command_type": command_type, "params": params or {}})

    def freeze_capture(self, freeze_dir: str, out_path: str,
                       command_type: str = "automator_freeze",
                       timeout_s: float = 120.0) -> Path:
        """Freeze the node's GUI-focused track and write the returned wav to out_path."""
        res = self._call("freeze_capture", {"freeze_dir": freeze_dir,
                                            "command_type": command_type, "timeout_s": timeout_s})
        dest = Path(out_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(base64.b64decode(res["wav_b64"]))
        return dest

    def fetch_wav(self, path_on_node: str, out_path: str) -> Path:
        """Pull a node-local wav (e.g. a resampling-recorded stem) back to the host
        and write it to out_path. Used when host and node don't share a filesystem."""
        res = self._call("fetch_wav", {"path": path_on_node})
        dest = Path(out_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(base64.b64decode(res["wav_b64"]))
        return dest


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Ableton render-node on-node agent")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=DEFAULT_AGENT_PORT)
    a = ap.parse_args()
    serve(a.host, a.port)
