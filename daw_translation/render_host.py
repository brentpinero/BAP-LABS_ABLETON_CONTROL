"""
render_host.py — persistent WARM plugin host for the fast tier.

The fast tier (render_pool → render_worker) spawns ONE subprocess PER job and
loads the plugin fresh every time. Measured on an M4 Max, loading Serum 2 costs
~6 s warm / ~16 s cold — and the sandbox loop re-renders the same roles every
iteration, so that load tax is paid over and over. This module keeps the plugin
LOADED across iterations: the expensive load_plugin() happens once per process
lifetime; subsequent renders reuse the in-memory instrument and cost well under
a second.

Two pieces, mirroring render_node_agent's server/client split:
  • the server (`serve`) is a long-lived SUBPROCESS that imports pedalboard
    (GPLv3) and caches loaded plugins in-process — this is the GPL-isolation
    boundary, exactly like render_worker, so the orchestrator never links GPL.
  • the client (`WarmHostPool`) runs in the loop's process: one persistent host
    per instrument spec (so different instruments still render in PARALLEL, while
    calls that share a plugin serialize on it — a single plugin instance is not
    reentrant). It respawns a host that dies and the caller falls back to a cold
    subprocess render, so a warm-host fault can never break a render.

CORRECTNESS: a cold render starts from the plugin's default state; a reused warm
plugin would otherwise carry over the previous render's state. So the host
snapshots each plugin's default `raw_state` at load and RESTORES it before every
render, then re-applies the job's params — making a warm render byte-identical to
a cold one. Verified in test_render_host.py.

Wire format (TCP on 127.0.0.1, length-framed JSON — audio never crosses the
socket, the host and pool share the filesystem so the wav is written to
job["output"] and the pool just reads that path):
    4-byte big-endian uint32 length  +  UTF-8 JSON body
Request:  {"cmd": "render"|"ping"|"shutdown", "job"?: {...render_pool midi job...}}
Reply:    {"status": "rendered"|"ok"|"error", "output"?: str, "seconds"?: float, "error"?: str}
"""
from __future__ import annotations

import atexit
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

_HOST = "127.0.0.1"
_MAX_FRAME = 16 * 1024 * 1024  # requests/replies are tiny JSON — no wav bytes here


# ── framed socket helpers ────────────────────────────────────────────────────

def _send(sock: socket.socket, obj: Dict[str, Any]) -> None:
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


def _recv(sock: socket.socket) -> Dict[str, Any]:
    (length,) = struct.unpack(">I", _recv_exactly(sock, 4))
    if length > _MAX_FRAME:
        raise ValueError(f"frame too large: {length}")
    return json.loads(_recv_exactly(sock, length).decode("utf-8"))


# ── server side (runs in the warm SUBPROCESS; imports pedalboard) ────────────

def _load_plug_cached(instrument: str, cache: Dict[str, Tuple[Any, Optional[bytes]]]):
    """Load (or reuse) a plugin for an instrument spec, returning (plug, baseline
    raw_state). Only the load — the expensive part — is cached; state is reset
    per render by the caller. Reuses render_worker.load_instrument so the load
    grammar lives in exactly one place."""
    import render_worker  # sibling; the pedalboard import lives here (GPL boundary)

    if instrument in cache:
        return cache[instrument]
    plug = render_worker.load_instrument(instrument)
    try:
        baseline = bytes(plug.raw_state)  # default state, restored before each render
    except Exception:  # noqa: BLE001 — some plugins expose no raw_state
        baseline = None
    cache[instrument] = (plug, baseline)
    return cache[instrument]


def render_job_warm(job: Dict[str, Any],
                    cache: Dict[str, Tuple[Any, Optional[bytes]]]) -> str:
    """Render one render_pool MIDI job using a cached plugin. Falls back to the
    cold render_worker path for fallback synths and raw-state jobs (nothing to
    warm there). Writes job["output"] and returns it."""
    import soundfile as sf
    import render_worker

    notes, bars_from_file = render_worker._load_notes(job["midi"])
    instrument = job.get("instrument", "fallback:keys")
    sr = int(job.get("sr", 44100))
    bpm = float(job.get("bpm", 120.0))
    bars = job.get("bars", bars_from_file)
    tail = float(job.get("tail_seconds", 1.0))
    params = job.get("params")
    chain = job.get("chain", [])

    if instrument.startswith("fallback:") or job.get("raw_state"):
        # numpy proxy synth (no load cost) or exact-state transplant (not warmable)
        audio = render_worker.render_midi(
            notes, bpm, instrument, sr, bars=bars, tail_seconds=tail, params=params)
    else:
        plug, baseline = _load_plug_cached(instrument, cache)
        if baseline is not None:
            try:
                plug.raw_state = baseline  # reset → warm render == cold render
            except Exception:  # noqa: BLE001
                pass
        # shared cold/warm render core → byte-identical to a fresh subprocess render
        audio = render_worker.render_with_plug(
            plug, notes, bpm, sr, bars=bars, tail_seconds=tail, params=params)

    if chain:
        audio = render_worker.render_chain(audio, sr, chain)
    sf.write(job["output"], audio, sr)
    return job["output"]


def serve(port_file: str) -> None:
    """Run the warm host: bind an ephemeral localhost port, announce it by writing
    <port_file>, then serve render requests over one persistent connection until
    the pool disconnects or sends shutdown. Plugins stay loaded for the lifetime."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((_HOST, 0))
    srv.listen(1)
    port = srv.getsockname()[1]
    # announce atomically: write temp then rename, so the pool never reads a
    # half-written port.
    tmp = Path(f"{port_file}.tmp")
    tmp.write_text(str(port))
    os.replace(tmp, port_file)

    cache: Dict[str, Tuple[Any, Optional[bytes]]] = {}
    conn, _ = srv.accept()
    srv.close()
    try:
        while True:
            try:
                req = _recv(conn)
            except (ConnectionError, ValueError):
                break  # pool went away — exit so the process doesn't leak
            cmd = req.get("cmd")
            if cmd == "ping":
                _send(conn, {"status": "ok"})
            elif cmd == "shutdown":
                _send(conn, {"status": "ok"})
                break
            elif cmd == "render":
                t0 = time.monotonic()
                try:
                    out = render_job_warm(req["job"], cache)
                    _send(conn, {"status": "rendered", "output": out,
                                 "seconds": round(time.monotonic() - t0, 3)})
                except Exception as e:  # noqa: BLE001 — report; keep the host alive
                    _send(conn, {"status": "error", "error": f"{type(e).__name__}: {e}",
                                 "seconds": round(time.monotonic() - t0, 3)})
            else:
                _send(conn, {"status": "error", "error": f"unknown cmd: {cmd}"})
    finally:
        conn.close()


# ── client side (runs in the loop's process) ────────────────────────────────

class _Host:
    """One warm subprocess + its persistent connection, guarded by a lock (a
    single plugin instance is not reentrant, so calls to the same host serialize)."""

    def __init__(self, ready_timeout: float = 30.0):
        self.lock = threading.Lock()
        self._proc: Optional[subprocess.Popen] = None
        self._sock: Optional[socket.socket] = None
        self._portdir: Optional[Path] = None
        self._ready_timeout = ready_timeout

    def _alive(self) -> bool:
        return (self._sock is not None and self._proc is not None
                and self._proc.poll() is None)

    def _spawn(self) -> None:
        import tempfile
        self._portdir = Path(tempfile.mkdtemp(prefix="warmhost_"))
        port_file = self._portdir / "port"
        self._proc = subprocess.Popen(
            [sys.executable, str(_HERE / "render_host.py"), "--serve", "--port-file", str(port_file)])
        deadline = time.monotonic() + self._ready_timeout
        while time.monotonic() < deadline:
            if self._proc.poll() is not None:
                raise RuntimeError(f"warm host exited during startup (rc={self._proc.returncode})")
            if port_file.exists():
                port = int(port_file.read_text())
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(max(60.0, self._ready_timeout))
                s.connect((_HOST, port))
                self._sock = s
                return
            time.sleep(0.05)
        raise TimeoutError("warm host never announced its port")

    def _ensure(self) -> None:
        if self._alive():
            return
        self._teardown()
        self._spawn()

    def render(self, job: Dict[str, Any], timeout: float) -> Dict[str, Any]:
        """Render one job on this host. Raises on host/socket failure so the pool
        can fall back to a cold subprocess and respawn the host next time."""
        with self.lock:
            self._ensure()
            assert self._sock is not None
            self._sock.settimeout(timeout)
            try:
                _send(self._sock, {"cmd": "render", "job": job})
                return _recv(self._sock)
            except (OSError, ConnectionError, ValueError) as e:
                self._teardown()  # poisoned — next call respawns
                raise RuntimeError(f"warm host render failed: {type(e).__name__}: {e}")

    def _teardown(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except Exception:  # noqa: BLE001
                pass
            self._sock = None
        if self._proc is not None:
            try:
                if self._proc.poll() is None:
                    self._proc.terminate()
                    try:
                        self._proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        self._proc.kill()
            except Exception:  # noqa: BLE001
                pass
            self._proc = None
        if self._portdir is not None:
            shutil.rmtree(self._portdir, ignore_errors=True)  # don't leak the port-file dir
            self._portdir = None

    def close(self) -> None:
        with self.lock:
            if self._alive():
                try:
                    self._sock.settimeout(5.0)
                    _send(self._sock, {"cmd": "shutdown"})
                    _recv(self._sock)
                except Exception:  # noqa: BLE001
                    pass
            self._teardown()


class WarmHostPool:
    """Keeps one warm host per instrument spec, alive across render_jobs() calls
    (so plugins stay loaded across loop iterations). Thread-safe; distinct specs
    render in parallel, same spec serializes on its shared plugin."""

    def __init__(self, ready_timeout: float = 30.0):
        self._hosts: Dict[str, _Host] = {}
        self._guard = threading.Lock()
        self._ready_timeout = ready_timeout
        atexit.register(self.shutdown)

    def _host_for(self, instrument: str) -> _Host:
        with self._guard:
            h = self._hosts.get(instrument)
            if h is None:
                h = _Host(ready_timeout=self._ready_timeout)
                self._hosts[instrument] = h
            return h

    def render(self, job: Dict[str, Any], timeout: float) -> Dict[str, Any]:
        instrument = job.get("instrument", "fallback:keys")
        return self._host_for(instrument).render(job, timeout)

    def shutdown(self) -> None:
        with self._guard:
            hosts = list(self._hosts.values())
            self._hosts.clear()
        for h in hosts:
            h.close()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Warm plugin host (fast-tier render server)")
    ap.add_argument("--serve", action="store_true", help="run the warm host server (subprocess mode)")
    ap.add_argument("--port-file", help="path to write the chosen localhost port to")
    args = ap.parse_args()
    if args.serve:
        if not args.port_file:
            ap.error("--serve requires --port-file")
        serve(args.port_file)
    else:
        ap.error("nothing to do (use --serve, or import WarmHostPool)")
