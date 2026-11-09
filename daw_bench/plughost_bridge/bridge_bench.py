"""
bridge_bench.py — Phase 1 spike: Tracktion Engine hosting plugins out of process via plughost.

Runs bridge_probe (C++, Tracktion + a "Plughost" JUCE plugin format over plughost_bridge's
C ABI) and scores it against the same edit with the plugin in process (the control):

  null      offline render through the bridge vs in process (gate: bit-identical, so delay
            compensation absorbs the bridge's latency exactly)
  ramp      realtime at 128-sample blocks, paced to wall-clock time, for N = 1, 2, 4, ... tracks
            of Serum 2: callback time, overruns (callback longer than its period), and the
            bridge's missed/late quanta, for bridged and in-process
  kill      SIGKILL every bridged helper mid-playback: the engine must keep calling back, and
            the control thread must recover each chain from its snapshot

Build: see README.md. Run:
    python daw_bench/plughost_bridge/bridge_bench.py                   # all parts
    python daw_bench/plughost_bridge/bridge_bench.py --only ramp --max-tracks 32
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PROBE = ROOT / "build/bridge_probe/bridge_probe_artefacts/Release/bridge_probe"
HELPER = ROOT / "build/host_rs/PlughostHelper.app/Contents/MacOS/plughost-helper"
FIXTURE = ROOT / "daw_bench/fixtures/serum2_track66/component_state.bin"
BASE = {"bundle": "/Library/Audio/Plug-Ins/VST3/Serum2.vst3", "class_name": "Serum 2",
        "class_id": "56534558667350736572756D20320000", "helper": str(HELPER),
        "sample_rate": 44100, "tempo": 126}


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def peak_dbfs(x: np.ndarray) -> float:
    return float(20 * np.log10(np.max(np.abs(x)) + 1e-30))


mem_gb_peak: dict = {}


def _rss_gb(pid: int) -> float:
    """Resident memory of a process and its children (GB)."""
    pids = [str(pid)] + subprocess.run(["pgrep", "-P", str(pid)], capture_output=True, text=True).stdout.split()
    out = subprocess.run(["ps", "-o", "rss=", "-p", ",".join(pids)], capture_output=True, text=True).stdout
    return sum(int(x) for x in out.split()) / 1024 / 1024


def run_probe(job: dict, out: Path, name: str, timeout: float = 600, during=None) -> dict:
    """Runs one bridge_probe job; `during(proc)` runs on a thread while it plays (kill test).
    Peak memory of the probe plus its helpers lands in mem_gb_peak[name]."""
    job = {**BASE, **job, "output": str(out / f"{name}.wav")}
    if FIXTURE.exists():
        job["component_state"] = str(FIXTURE)
    jpath = out / f"{name}.json"
    jpath.write_text(json.dumps(job))
    p = subprocess.Popen([str(PROBE), str(jpath)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if during:
        threading.Thread(target=during, args=(p,), daemon=True).start()

    def sample_memory():
        while p.poll() is None:
            try:
                mem_gb_peak[name] = max(mem_gb_peak.get(name, 0.0), _rss_gb(p.pid))
            except ValueError:
                pass
            time.sleep(1.0)
    threading.Thread(target=sample_memory, daemon=True).start()
    try:
        stdout, stderr = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        return {"ok": False, "error": f"timeout after {timeout} s"}
    report = next((json.loads(line) for line in stdout.splitlines() if line.startswith("{")), None)
    if report is None:
        return {"ok": False, "error": f"exit {p.returncode}: {stderr[-400:]}"}
    report["exit"] = p.returncode
    (out / f"{name}.report.json").write_text(json.dumps(report, indent=1))
    return report


def null(out: Path) -> dict:
    res = {}
    for kind in ("native", "bridge"):
        log(f"null: offline render, {kind}")
        res[kind] = run_probe({"mode": "offline", "plugin": kind, "block": 512, "seconds": 8, "tracks": 1},
                              out, f"offline_{kind}")
    a, _ = sf.read(out / "offline_native.wav")
    b, _ = sf.read(out / "offline_bridge.wav")
    n = min(len(a), len(b))
    res["residual_dbfs"] = round(peak_dbfs(a[:n] - b[:n]), 1)
    res["latency"] = (res["bridge"].get("bridged") or [{}])[0].get("latency")
    log(f"null: bridge vs in process residual {res['residual_dbfs']} dBFS "
        f"(bridge latency {res['latency']} samples, compensated by Tracktion)")
    return res


def summarize_rt(r: dict) -> dict:
    bridged = r.get("bridged") or []
    st = [b.get("status", {}) for b in bridged]
    return {"ok": r.get("ok"), "error": r.get("error"), "callbacks": r.get("callbacks"),
            "overruns": r.get("overruns"), "overruns_warmup": r.get("overruns_warmup"),
            "cb_ms_median": r.get("cb_ms_median"),
            "cb_ms_p99": r.get("cb_ms_p99"), "cb_ms_max": r.get("cb_ms_max"), "period_ms": r.get("period_ms"),
            # bridge misses after the 1 s warm-up (startup is reported apart, as for overruns)
            "missed": sum(b.get("missed_after_warmup", 0) for b in bridged),
            "late": sum(b.get("late_after_warmup", 0) for b in bridged),
            "missed_total": sum(s.get("missed", 0) for s in st),
            "fallbacks": sum(b.get("fallbacks", 0) for b in bridged),
            "size_mismatches": sum(b.get("size_mismatches", 0) for b in bridged),
            "errors": sum(b.get("errors", 0) for b in bridged)}


DROPOUT_STOP = 0.001   # stop a ramp above 0.1% dropouts (raw counts are always reported)


def ramp(out: Path, max_tracks: int, seconds: float, kinds=("native", "bridge_lq1", "bridge_lq2"),
         stop: bool = True) -> dict:
    """Doubles the track count until dropouts (engine overruns + bridge missed quanta) exceed
    DROPOUT_STOP of callbacks. Bridged runs at 1 and 2 quanta of endpoint latency."""
    res = {}
    variants = {"native": ("native", 1), "bridge_lq1": ("bridge", 1), "bridge_lq2": ("bridge", 2)}
    for label in kinds:
        kind, lq = variants[label]
        res[label] = {}
        n = 1
        while n <= max_tracks:
            log(f"ramp: {label}, {n} track(s), {seconds} s at 128 samples")
            s = summarize_rt(run_probe({"mode": "realtime", "plugin": kind, "block": 128, "latency_quanta": lq,
                                        "seconds": seconds, "tracks": n}, out, f"rt_{label}_{n}"))
            s["mem_gb"] = mem_gb_peak.get(f"rt_{label}_{n}")
            res[label][n] = s
            if not s["ok"]:
                log(f"ramp: {label} {n}: FAILED {s['error']}")
                break
            drops = s["overruns"] + s["missed"]
            s["dropout_rate"] = drops / max(s["callbacks"], 1)
            log(f"ramp: {label} {n}: after 1 s warm-up: overruns {s['overruns']}, missed {s['missed']}, "
                f"late {s['late']} (warm-up: overruns {s['overruns_warmup']}, bridge missed total "
                f"{s['missed_total']}) "
                f"of {s['callbacks']} callbacks; callback median {s['cb_ms_median']:.3f} p99 "
                f"{s['cb_ms_p99']:.3f} max {s['cb_ms_max']:.3f} ms (period {s['period_ms']:.2f}); "
                f"errors {s['errors']}")
            if stop and s["dropout_rate"] > DROPOUT_STOP:
                break
            n *= 2
    return res


def kill(out: Path, tracks: int, seconds: float) -> dict:
    """SIGKILLs every plughost helper (children of bridge_probe) a third of the way in."""
    killed = []
    marker = out / "rt_kill.playing"
    marker.unlink(missing_ok=True)

    def killer(proc):
        # Wait until the probe reports playback running (startup can take several seconds),
        # then a third of the run, so the kill lands mid-playback with endpoints in use.
        while not marker.exists() and proc.poll() is None:
            time.sleep(0.05)
        time.sleep(seconds / 3)
        kids = subprocess.run(["pgrep", "-P", str(proc.pid)], capture_output=True, text=True).stdout.split()
        for pid in kids:
            try:
                os.kill(int(pid), signal.SIGKILL)
                killed.append(int(pid))
            except ProcessLookupError:
                pass
        log(f"kill: SIGKILL {len(killed)} helper(s)")

    log(f"kill: realtime, {tracks} bridged track(s), {seconds} s")
    r = run_probe({"mode": "realtime", "plugin": "bridge", "block": 128, "seconds": seconds, "tracks": tracks,
                   "playing_marker": str(marker)}, out, "rt_kill", during=killer)
    s = summarize_rt(r)
    s["killed"] = len(killed)
    s["recoveries_ms"] = [b.get("recoveries_ms") for b in r.get("bridged") or []]
    s["engine_kept_running"] = bool(r.get("ok")) and r.get("callbacks") is not None
    rec = out / "rt_kill.wav"
    if rec.exists():   # audio after recovery: the last second should not be silent
        x, sr = sf.read(rec)
        s["last_second_peak_dbfs"] = round(peak_dbfs(x[-sr:]), 1)
    log(f"kill: engine kept running {s['engine_kept_running']}, recoveries {s['recoveries_ms']}, "
        f"last second peak {s.get('last_second_peak_dbfs')} dBFS")
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "sandbox_sessions/bridge_bench" / time.strftime("%Y%m%d_%H%M%S")))
    ap.add_argument("--only", choices=["null", "ramp", "kill"])
    ap.add_argument("--max-tracks", type=int, default=64)
    ap.add_argument("--seconds", type=float, default=8.0)
    ap.add_argument("--kinds", default="native,bridge_lq1,bridge_lq2", help="ramp variants, comma-separated")
    ap.add_argument("--no-stop", action="store_true", help="ramp to --max-tracks even with dropouts")
    args = ap.parse_args()
    for b in (PROBE, HELPER):
        if not b.exists():
            print(f"missing {b}: build first (README.md)")
            return 2
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    log(f"output -> {out}")
    report = {}
    if args.only in (None, "null"):
        report["null"] = null(out)
    if args.only in (None, "ramp"):
        report["ramp"] = ramp(out, args.max_tracks, args.seconds, args.kinds.split(","), not args.no_stop)
    if args.only in (None, "kill"):
        report["kill"] = kill(out, 4, max(args.seconds, 9.0))
    (out / "report.json").write_text(json.dumps(report, indent=1))
    log("done: " + str(out / "report.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
