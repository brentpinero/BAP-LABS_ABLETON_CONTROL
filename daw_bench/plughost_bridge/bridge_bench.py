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
  chain     the Phase 1 gate: N tracks x a fixed 6-plugin chain (CHAIN) playing an audio clip,
            on a real CoreAudio device (Tracktion's own device path, in the device's audio
            workgroup; output zeroed before the speakers). Dropouts = device xruns (CoreAudio's
            processor-overload notifications) + engine callbacks longer than the period +
            bridge quanta missed, all after warm-up. Bridged = one helper per track's chain.

Build: see README.md. Run:
    python daw_bench/plughost_bridge/bridge_bench.py                   # all parts
    python daw_bench/plughost_bridge/bridge_bench.py --only ramp --max-tracks 32
    python daw_bench/plughost_bridge/bridge_bench.py --only chain --block 128 --tracks 8,32,128,300
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
# PLUGHOST_HELPER overrides the helper (e.g. a patched build for an experiment).
HELPER = Path(os.environ.get("PLUGHOST_HELPER") or ROOT / "build/host_rs/PlughostHelper.app/Contents/MacOS/plughost-helper")
FIXTURE = ROOT / "daw_bench/fixtures/serum2_track66/component_state.bin"
BASE = {"bundle": "/Library/Audio/Plug-Ins/VST3/Serum2.vst3", "class_name": "Serum 2",
        "class_id": "56534558667350736572756D20320000", "helper": str(HELPER),
        "sample_rate": 44100, "tempo": 126}


# The fixed 6-plugin chain of the track-ramp gate: a typical mix chain (channel strip, bus
# compressor, saturation, delay, reverb, limiter), all VST3, all passing the bake-off, all at
# their default settings. (bx_console SSL 4000 E and Lindell 80 Bus, both Plugin Alliance,
# output digital silence on this machine, so neither can stand in for the channel strip.)
VST3 = "/Library/Audio/Plug-Ins/VST3"
CHAIN = [{"bundle": f"{VST3}/SSL 4K E.vst3"},
         {"bundle": f"{VST3}/SSL Native Bus Compressor 2.vst3"},
         {"bundle": f"{VST3}/FabFilter Saturn 2.vst3"},
         {"bundle": f"{VST3}/Kilohearts/kHs Delay.vst3"},
         {"bundle": f"{VST3}/ValhallaRoom.vst3"},
         {"bundle": f"{VST3}/FabFilter Pro-L 2.vst3"}]
# The same six slots with near-free plugins (Kilohearts snapins at defaults, ~0.004 ms per
# 128-sample block for all six vs 0.137 ms for CHAIN): isolates what the host and engine cost per
# plugin and per track, which is what has to scale to 300 tracks.
KHS = f"{VST3}/Kilohearts"
LIGHT_CHAIN = [{"bundle": f"{KHS}/kHs {n}.vst3"} for n in
               ("3-Band EQ", "Compressor", "Distortion", "Delay", "Reverb", "Limiter")]
# In process, Kilohearts snapins go silent (the whole mix, no error) beyond ~96-144 instances
# per process: the light chain runs natively up to 16 tracks only. Bridged, each helper holds 6.
# "none": tracks play the clip with no plugin, Tracktion's own cost per audio track (native only).
CHAINS = {"heavy": CHAIN, "light": LIGHT_CHAIN, "none": []}
DEVICE = {"device": "coreaudio", "device_name": "MacBook Pro Speakers"}


def make_source(path: Path, sr: int, seconds: float, tempo: float) -> Path:
    """A drum-and-bass-like stereo clip: a decaying noise hit and a 55 Hz tone on every beat,
    peaking near -12 dBFS, so every effect in the chain has signal to work on."""
    rng = np.random.default_rng(0)
    n = int(sr * seconds)
    t = np.arange(n) / sr
    beat = 60.0 / tempo
    phase = (t % beat) / beat
    env = np.exp(-phase * 12)
    x = np.stack([0.15 * rng.standard_normal(n) * env + 0.1 * np.sin(2 * np.pi * 55 * t) * env
                  for _ in range(2)], axis=1)
    sf.write(path, x.astype(np.float32), sr, subtype="FLOAT")
    return path


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
            "errors": sum(b.get("errors", 0) for b in bridged),
            # real-device runs only
            "device_xruns": r.get("device_xruns"), "device_xruns_warmup": r.get("device_xruns_warmup"),
            "cpu_load_median": r.get("cpu_load_median"), "cpu_load_max": r.get("cpu_load_max"),
            "odd_block_sizes": r.get("odd_block_sizes"), "workgroup_valid": r.get("workgroup_valid"),
            "build_s": r.get("build_s"), "prespawn_s": r.get("prespawn_s"),
            "playback_start_s": r.get("playback_start_s")}


def dropouts(s: dict) -> int:
    """Every kind of dropout after warm-up: device xruns, late engine callbacks, missed quanta."""
    return (s.get("device_xruns") or 0) + (s.get("overruns") or 0) + (s.get("missed") or 0)


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


def chain_ramp(out: Path, block: int, tracks: list[int], seconds: float, kinds=("native", "bridge_lq1"),
               stop: bool = True, repeats: int = 3, chain: str = "heavy", probe_timeout: float = 900) -> dict:
    """The track-ramp gate on the real device: N tracks x CHAIN at `block` samples.

    The machine is shared (a DAW, browsers, other jobs), so each track count runs every variant
    `repeats` times, interleaved (native, bridge, native, bridge, ...) so they see the same
    conditions. best = the fewest dropouts of any repeat (what the engine can do); median = what
    this machine typically gave. A variant leaves the ramp once even its best repeat drops out."""
    sr = BASE["sample_rate"]
    source = make_source(out / f"source_{sr}.wav", sr, seconds + 2, BASE["tempo"])
    variants = {"native": ("native", 1), "bridge_lq1": ("bridge", 1), "bridge_lq2": ("bridge", 2)}
    res = {label: {} for label in kinds}
    active = list(kinds)
    for n in tracks:
        runs = {label: [] for label in active}
        for rep in range(repeats):
            for label in active:
                kind, lq = variants[label]
                name = f"chain_{chain}_{label}_b{block}_{n}_r{rep}"
                log(f"chain: {chain} {label}, {n} track(s) x {len(CHAINS[chain])} plugins, run {rep + 1}/{repeats}, {seconds} s at "
                    f"{block} samples on {DEVICE['device_name']} (load avg {os.getloadavg()[0]:.1f})")
                r = run_probe({"mode": "realtime", "plugin": kind, "block": block, "latency_quanta": lq,
                               "seconds": seconds, "tracks": n, "chain": CHAINS[chain], "audio_file": str(source),
                               "prespawn_parallel": 8, "warmup_s": 2.0, **DEVICE}, out, name, timeout=probe_timeout)
                s = summarize_rt(r)
                s["mem_gb"] = mem_gb_peak.get(name)
                s["load_avg"] = os.getloadavg()[0]
                runs[label].append(s)
                if not s["ok"]:
                    log(f"chain: {label} {n}: FAILED {s['error']}")
                    continue
                s["dropouts"] = dropouts(s)
                rec = out / f"{name}.wav"
                if rec.exists():   # the chain must carry the clip: a silent run measures nothing
                    x, _ = sf.read(rec)
                    s["out_peak_dbfs"] = round(peak_dbfs(x), 1)
                    if s["out_peak_dbfs"] < -60:   # counts as a failed run, not a pass
                        s["silent"] = True
                        log(f"chain: {label} {n}: OUTPUT SILENT ({s['out_peak_dbfs']} dBFS)")
                log(f"chain: {label} {n}: dropouts {s['dropouts']} (device xruns {s['device_xruns']}, late callbacks "
                    f"{s['overruns']}, missed quanta {s['missed']}) of {s['callbacks']} callbacks; callback median "
                    f"{s['cb_ms_median']:.3f} p99 {s['cb_ms_p99']:.3f} max {s['cb_ms_max']:.3f} ms (period "
                    f"{s['period_ms']:.2f}); load {s['cpu_load_median']:.2f}; warm-up xruns {s['device_xruns_warmup']}; "
                    f"workgroup {s['workgroup_valid']}; build {s['build_s']:.1f} s; mem {s['mem_gb'] or 0:.1f} GB; "
                    f"out peak {s.get('out_peak_dbfs')} dBFS")
        for label, rs in runs.items():
            drops = sorted(s["dropouts"] for s in rs if s.get("ok") and "dropouts" in s and not s.get("silent"))
            res[label][n] = {"runs": rs, "best": drops[0] if drops else None,
                             "median": drops[len(drops) // 2] if drops else None}
            log(f"chain: {label} {n} tracks: dropouts best {res[label][n]['best']}, median {res[label][n]['median']} "
                f"over {len(drops)} run(s)")
        (out / "report_partial.json").write_text(json.dumps(res, indent=1))
        if stop:
            active = [label for label in active if res[label][n]["best"] == 0]
            if not active:
                break
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "sandbox_sessions/bridge_bench" / time.strftime("%Y%m%d_%H%M%S")))
    ap.add_argument("--only", choices=["null", "ramp", "kill", "chain"])
    ap.add_argument("--block", type=int, default=128, help="chain: device block size")
    ap.add_argument("--tracks", default="1,8,32,64,128,256,300", help="chain: track counts, comma-separated")
    ap.add_argument("--repeats", type=int, default=3, help="chain: interleaved runs per variant and track count")
    ap.add_argument("--probe-timeout", type=float, default=900, help="chain: seconds before a run counts as hung")
    ap.add_argument("--chain", choices=list(CHAINS), default="heavy", help="chain: which 6-plugin chain")
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
    if args.only == "chain":
        kinds = args.kinds.split(",") if args.kinds != "native,bridge_lq1,bridge_lq2" else ["native", "bridge_lq1"]
        report["chain"] = chain_ramp(out, args.block, [int(x) for x in args.tracks.split(",")], args.seconds,
                                     kinds, not args.no_stop, args.repeats, args.chain, args.probe_timeout)
    (out / "report.json").write_text(json.dumps(report, indent=1))
    log("done: " + str(out / "report.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
