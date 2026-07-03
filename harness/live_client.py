"""
live_client.py — minimal client for the AbletonMCP_Extended Remote Script.

Replicates the MCP server's AbletonConnection socket semantics (TCP 9877, raw
JSON framed by parse-completeness) WITHOUT importing the FastMCP server, so CLI
tools (calibration) can drive Live directly. Also a thin automator wrapper.
"""
from __future__ import annotations

import json
import socket
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE / "AbletonMCP_Extended") not in sys.path:
    sys.path.insert(0, str(_HERE / "AbletonMCP_Extended"))


class LiveError(Exception):
    pass


class LiveClient:
    """send(command_type, params) -> result dict, mirroring the Remote Script protocol."""

    def __init__(self, host: str = "localhost", port: int = 9877, timeout: float = 15.0):
        self.host, self.port, self.timeout = host, port, timeout
        self.sock: Optional[socket.socket] = None

    def connect(self) -> "LiveClient":
        if self.sock is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            try:
                s.connect((self.host, self.port))
            except OSError as e:
                raise LiveError(
                    f"Cannot reach Ableton on {self.host}:{self.port} — is Live open "
                    f"with the AbletonMCP_Extended Remote Script loaded? ({e})")
            self.sock = s
        return self

    def close(self) -> None:
        if self.sock:
            try:
                self.sock.close()
            finally:
                self.sock = None

    def send(self, command_type: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        self.connect()
        assert self.sock is not None
        self.sock.sendall(json.dumps({"type": command_type, "params": params or {}}).encode())
        time.sleep(0.1)  # settle for state-mutating commands (matches server behavior)
        chunks: list[bytes] = []
        self.sock.settimeout(self.timeout)
        while True:
            chunk = self.sock.recv(8192)
            if not chunk:
                raise LiveError("connection closed mid-response")
            chunks.append(chunk)
            try:
                resp = json.loads(b"".join(chunks).decode())
                break
            except json.JSONDecodeError:
                continue
        if resp.get("status") == "error":
            raise LiveError(resp.get("message", "unknown Live error"))
        return resp.get("result", {})

    def __enter__(self):
        return self.connect()

    def __exit__(self, *_):
        self.close()


def automator(command_type: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Run a GUI-automation command in-process (macOS Accessibility required)."""
    import automator_bridge  # noqa: WPS433 — Live-free standalone module
    return automator_bridge.handle_automator_command(command_type, params or {})
