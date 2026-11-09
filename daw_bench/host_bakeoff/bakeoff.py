"""
bakeoff.py — Phase 1 plugin-hosting bake-off: C++ (JUCE) host vs Rust (plughost) host.

Both hosts run the same probe script on each plugin of plugin_list.json (see README.md):
load -> prepare -> render a -> reset, render b -> edit one parameter, render c -> save state
-> fresh instance with that state -> render d. This harness writes the inputs, runs every
probe in its own process with a timeout, and scores all results with the same code:

  compatible     the probe finished, output is finite, and the restored instance (d) nulls
                 against the edited one (c) — the Phase 1 "load, process, restore state" gate
  determinism    peak residual of a vs b (dBFS)
  overhead       Rust per-block wall time minus C++ in-process per-block wall time (ms)

Plus two single tests:
  serum          the track-66 Serum 2 patch rendered by each host vs the Ableton freeze,
                 per-band level difference in 20-250 Hz (gate: <= 1 dB)
  kill           SIGKILL the Rust host's plugin helper mid-render: the host must survive
                 and report the crash

Build the hosts first (README.md), then:
    python daw_bench/host_bakeoff/bakeoff.py                 # everything
    python daw_bench/host_bakeoff/bakeoff.py --only serum    # one part: compat|serum|kill
    python daw_bench/host_bakeoff/bakeoff.py --limit 5       # first 5 plugins
"""
from __future__ import annotations

import argparse
import functools
import json
import os
import signal
import struct
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "sandbox"))
sys.path.insert(0, str(ROOT / "daw_bench"))
import signals  # noqa: E402  (daw_bench/signals.py: float32 wav writer)

SR = 48000
BLOCK = 512
SECONDS = 4
TIMEOUT_S = 240
RESTORE_PASS_DBFS = -80.0          # c vs d residual that counts as a restored state
FIXTURE = ROOT / "daw_bench" / "fixtures" / "serum2_track66"
SERUM2_VST3 = "/Library/Audio/Plug-Ins/VST3/Serum2.vst3"
SERUM2_CLASS = "56534558667350736572756D20320000"   # Serum 2 processor class (moduleinfo.json)

HOST_RS = ROOT / "build" / "host_rs" / "release" / "host_rs"
HELPER = ROOT / "build" / "host_rs" / "PlughostHelper.app" / "Contents" / "MacOS" / "plughost-helper"
HOST_CPP = ROOT / "build" / "host_cpp" / "host_cpp_artefacts" / "Release" / "host_cpp"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------------------------------------------------------------- inputs

def make_stimulus(path: Path) -> None:
    """Stereo effect input: pink-ish noise with 250 ms on/off bursts so dynamics plugins act."""
    rng = np.random.default_rng(7)
    n = SR * SECONDS
    white = rng.standard_normal((n, 2))
    spec = np.fft.rfft(white, axis=0)
    f = np.fft.rfftfreq(n, 1 / SR)
    spec /= np.sqrt(np.maximum(f, 20.0))[:, None]             # 1/f power
    x = np.fft.irfft(spec, n=n, axis=0)
    x *= 0.25 / np.max(np.abs(x))
    gate = (np.arange(n) // (SR // 4)) % 2 == 0
    x[~gate] *= 0.1                                           # -20 dB between bursts
    signals.write_wav(path, x, SR)


def chord_notes() -> list[dict]:
    """Instrument input: C3/E3/G3 for 1.5 s, then C2 for 1.5 s."""
    s = SR * 3 // 2
    return [{"pitch": p, "start": 0, "dur": s, "vel": 100} for p in (48, 52, 55)] + \
           [{"pitch": 36, "start": s + SR // 4, "dur": s, "vel": 100}]


def vstpreset(class_id: str, component: bytes, controller: bytes | None) -> bytes:
    """A VST3 .vstpreset: 48-byte header, 'Comp'/'Cont' chunks, then the chunk list."""
    chunks = [(b"Comp", component)] + ([(b"Cont", controller)] if controller else [])
    body, entries, offset = b"", [], 48
    for cid, data in chunks:
        entries.append((cid, offset, len(data)))
        body += data
        offset += len(data)
    header = b"VST3" + struct.pack("<i", 1) + class_id.encode("ascii") + struct.pack("<q", offset)
    listing = b"List" + struct.pack("<i", len(entries)) + b"".join(
        cid + struct.pack("<qq", off, size) for cid, off, size in entries)
    return header + body + listing


# ---------------------------------------------------------------- running hosts

def run_host(host: str, job: dict, job_dir: Path, timeout: float = TIMEOUT_S) -> dict:
    """Runs one probe process; a crash, hang or garbled output becomes a failed result."""
    job_dir.mkdir(parents=True, exist_ok=True)
    job = {**job, "out_dir": str(job_dir)}
    jpath = job_dir / "job.json"
    jpath.write_text(json.dumps(job))
    cmd = [str(HOST_RS), str(jpath), str(HELPER)] if host == "rust" else [str(HOST_CPP), str(jpath)]
    t = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        rc, out = p.returncode, p.stdout
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"timeout after {timeout:.0f} s", "wall_s": timeout}
    res = {}
    rpath = job_dir / "result.json"
    if rpath.exists():
        try:
            res = json.loads(rpath.read_text())
        except json.JSONDecodeError:
            pass
    if not res:
        res = {"ok": False, "error": f"no result (exit {rc}, signal {-rc if rc < 0 else 0})",
               "stdout_tail": out[-300:]}
    res["exit"] = rc
    res["wall_s"] = round(time.time() - t, 2)
    return res


def band_diff(x: np.ndarray, y: np.ndarray) -> list[float]:
    """Per-band level difference (dB) in fidelity.py's 8 log bands, on the mono sum."""
    import fidelity
    return fidelity.band_rms_diff(_mono(x), _mono(y), SR)


def _mono(z: np.ndarray) -> np.ndarray:
    return z.mean(axis=1) if z.ndim == 2 else z


def band_max_db(x: np.ndarray, y: np.ndarray) -> float:
    """Largest per-band level difference between two renders (dB)."""
    return max(abs(v) for v in band_diff(x, y))


def low_band_max(band_diff_db: list[float]) -> float:
    """Largest absolute difference in the three bands under 250 Hz (the Serum gate)."""
    return max(abs(x) for x in band_diff_db[:3])


def peak_dbfs(x: np.ndarray) -> float:
    return float(20 * np.log10(np.max(np.abs(x)) + 1e-30))


def score(res: dict, job_dir: Path) -> dict:
    """Same scoring for both hosts, from the wavs each probe wrote."""
    s = {"loaded": "load_ms" in res, "finished": bool(res.get("ok"))}
    wav = {k: job_dir / f"{k}.wav" for k in "abcd"}
    if not all(p.exists() for p in wav.values()):
        s["compatible"] = False
        return s
    a, b, c, d = (sf.read(wav[k], dtype="float64")[0] for k in "abcd")
    s["finite"] = bool(all(np.isfinite(x).all() for x in (a, b, c, d)))
    s["out_peak_dbfs"] = round(peak_dbfs(a), 1)
    s["silent"] = s["out_peak_dbfs"] < -120
    s["determinism_dbfs"] = round(peak_dbfs(a - b), 1)
    s["restore_dbfs"] = round(peak_dbfs(c - d), 1)          # restored vs edited
    s["edit_effect_dbfs"] = round(peak_dbfs(c - a), 1)      # how far the edit moved the audio
    s["restored_vs_unedited_dbfs"] = round(peak_dbfs(d - a), 1)
    s["deterministic"] = s["determinism_dbfs"] <= RESTORE_PASS_DBFS
    s["restore_inconclusive"] = False
    if s["deterministic"]:
        # A deterministic plugin must null after a restore.
        s["restored"] = s["restore_dbfs"] <= RESTORE_PASS_DBFS
    else:
        # Random phase, modelled noise, free-running LFOs: no sample-level null is possible, and
        # a fresh instance has its own seed. Judge the 8-band spectrum instead: the restored
        # render must sit within the plugin's own repeat variation of the edited one.
        floor = max(band_max_db(a, b), 0.25)     # how much two identical-settings renders differ
        s["band_repeat_db"], s["band_edit_db"], s["band_restore_db"] = (
            round(floor, 2), round(band_max_db(c, a), 2), round(band_max_db(d, c), 2))
        if s["band_edit_db"] <= 2 * floor:        # the edit is not visible: cannot tell
            s["restore_inconclusive"] = True
            s["restored"] = True
        else:
            s["restored"] = s["band_restore_db"] <= 2 * floor
    s["compatible"] = s["finished"] and s["finite"] and s["restored"]
    # band comparisons yield numpy bools, which json cannot write
    return {k: (bool(v) if isinstance(v, np.bool_) else v) for k, v in s.items()}


# ---------------------------------------------------------------- tests

def job_for(entry: dict, stimulus: Path) -> dict:
    job = {"sr": SR, "block": BLOCK, "frames": SR * SECONDS, "format": entry["format"],
           "input_wav": str(stimulus), "notes": chord_notes()}
    if entry["format"] == "au":
        job["au"] = entry["au"]
    else:
        job["bundle"] = entry["bundle"]
        job["class_index"] = entry.get("class_index", 0)
    return job


def compat(out: Path, limit: int | None) -> list[dict]:
    plugins = json.loads((HERE / "plugin_list.json").read_text())["plugins"][:limit]
    stimulus = out / "stimulus.wav"
    make_stimulus(stimulus)
    rows = []
    for i, entry in enumerate(plugins, 1):
        row = {"plugin": entry["name"], "format": entry["format"]}
        for host in ("cpp", "rust"):
            d = out / "compat" / f"{i:02d}_{entry['format']}_{host}"
            log(f"compat {i}/{len(plugins)} {entry['name']} ({entry['format']}) {host}: start")
            res = run_host(host, job_for(entry, stimulus), d)
            sc = score(res, d)
            row[host] = {**{k: res.get(k) for k in ("ok", "error", "stage", "load_ms", "restore_ms",
                            "block_ms_median", "block_ms_p95", "latency", "n_params", "kind",
                            "edited_param", "exit", "wall_s")}, **sc}
            log(f"compat {i}/{len(plugins)} {entry['name']} {host}: "
                f"{'PASS' if sc['compatible'] else 'FAIL'} "
                f"{res.get('error', '') or ''}"[:200])
        cpp, rs = row["cpp"], row["rust"]
        if cpp.get("block_ms_median") is not None and rs.get("block_ms_median") is not None:
            row["overhead_ms"] = round(rs["block_ms_median"] - cpp["block_ms_median"], 4)
        rows.append(row)
        (out / "compat.json").write_text(json.dumps(rows, indent=1))
    return rows


def serum(out: Path) -> dict:
    """Track-66 patch through each host vs the Ableton freeze (and the old pedalboard render)."""
    import fidelity
    notes = json.loads((FIXTURE / "notes.json").read_text())
    comp = (FIXTURE / "component_state.bin").read_bytes()
    cont_path = FIXTURE / "controller_state.bin"
    preset = out / "serum2_track66.vstpreset"
    preset.write_bytes(vstpreset(SERUM2_CLASS, comp, cont_path.read_bytes() if cont_path.exists() else None))
    frames = int(notes["window_seconds"] * SR)
    job = {"sr": SR, "block": BLOCK, "frames": frames, "format": "vst3", "bundle": SERUM2_VST3,
           "preset": str(preset),
           "notes": [{"pitch": n["pitch"], "start": round(n["start_s"] * SR),
                      "dur": round(n["dur_s"] * SR), "vel": n["velocity"]} for n in notes["notes"]]}
    live = FIXTURE / "live.wav"
    result = {}
    # Offline vs realtime process mode: Serum has "Use Ultra on Render", which only an offline
    # host can trigger — the leading suspect for the low-end gap (sandbox-fidelity notes).
    for mode in ("offline", "realtime"):
        for host in ("cpp", "rust"):
            d = out / "serum" / f"{host}_{mode}"
            log(f"serum {host} {mode}: start")
            res = run_host(host, {**job, "realtime": mode == "realtime"}, d)
            entry = {"ok": res.get("ok"), "error": res.get("error"), "load_ms": res.get("load_ms")}
            if (d / "a.wav").exists():
                cmpr = fidelity.compare(d / "a.wav", live)
                entry.update({k: cmpr.get(k) for k in ("null_depth_db", "band_diff_db", "lufs_delta",
                                                        "latency_samples", "label")})
                entry["low_band_max_abs_db"] = low_band_max(cmpr["band_diff_db"])
            result[f"{host}_{mode}"] = entry
            log(f"serum {host} {mode}: {entry.get('band_diff_db')} err={entry.get('error')}")
        a = [out / "serum" / f"{h}_{mode}" / "a.wav" for h in ("cpp", "rust")]
        if all(p.exists() for p in a):
            x, y = (sf.read(p, dtype="float64")[0] for p in a)
            result[f"cpp_vs_rust_{mode}_dbfs"] = round(peak_dbfs(x - y), 1)
    old = FIXTURE / "pedalboard_headless.wav"     # the July render through pedalboard (VST3)
    if old.exists():
        cmpr = fidelity.compare(old, live)
        result["pedalboard_baseline"] = {"band_diff_db": cmpr["band_diff_db"],
                                         "low_band_max_abs_db": low_band_max(cmpr["band_diff_db"])}
    (out / "serum.json").write_text(json.dumps(result, indent=1))
    return result


def kill(out: Path) -> dict:
    """SIGKILL the plugin helper mid-render. The Rust host must survive, recover the chain from
    its snapshot in a new helper, and finish the render (the C++ host has no helper to kill:
    the plugin runs in its process, so a plugin crash ends the host)."""
    d = out / "kill"
    d.mkdir(parents=True, exist_ok=True)
    # Long enough that the render (~0.05 ms per 512-sample block for Serum) outlasts the kill.
    # stop_after: the host returns once render a (and any recovery) is done; no b/c/d renders.
    job = {"sr": SR, "block": BLOCK, "frames": SR * 300, "format": "vst3", "bundle": SERUM2_VST3,
           "notes": chord_notes(), "stop_after": "a", "out_dir": str(d)}
    jpath = d / "job.json"
    jpath.write_text(json.dumps(job))
    log("kill: starting a 300 s Serum render")
    p = subprocess.Popen([str(HOST_RS), str(jpath), str(HELPER)], stdout=subprocess.PIPE, text=True)
    helper_pid, seen = None, None
    for _ in range(100):                       # find the helper (a child of host_rs) ...
        time.sleep(0.05)
        kids = subprocess.run(["pgrep", "-P", str(p.pid)], capture_output=True, text=True).stdout.split()
        if kids:
            seen = seen or time.time()
            helper_pid = int(kids[-1])         # newest child: the chain helper, after the scan helper
        if seen and time.time() - seen > 0.6:  # ... let it load and start rendering
            break
    result = {"helper_pid": helper_pid}
    if helper_pid:
        os.kill(helper_pid, signal.SIGKILL)
        log(f"kill: SIGKILL helper {helper_pid}")
    p.communicate(timeout=300)
    res = json.loads((d / "result.json").read_text()) if (d / "result.json").exists() else {}
    result.update({"host_exit": p.returncode, "host_survived": p.returncode >= 0 and bool(res),
                   "crash_error": res.get("crash_error"), "recovered": bool(res.get("recovered")),
                   "recover_ms": res.get("recover_ms"), "finished": bool(res.get("ok")),
                   "error": res.get("error")})
    log(f"kill: host exit {p.returncode}, recovered={result['recovered']} "
        f"in {result['recover_ms']} ms, finished={result['finished']}, crash={result['crash_error']!r}")
    (d / "a.wav").unlink(missing_ok=True)      # a 300 s wav is not worth keeping
    (out / "kill.json").write_text(json.dumps(result, indent=1))
    return result


@functools.lru_cache(maxsize=None)
def native_arm64(bundle: str) -> bool:
    """False when a VST3 bundle has no arm64 slice: no native host (Live included) can load it,
    so it is a plugin-side failure, not a hosting one."""
    exe_dir = Path(bundle) / "Contents" / "MacOS"
    exes = list(exe_dir.iterdir()) if exe_dir.exists() else []
    if not exes:
        return True
    archs = subprocess.run(["lipo", "-archs", str(exes[0])], capture_output=True, text=True).stdout
    return "arm64" in archs


def exclusion(entry: dict) -> str | None:
    """Why a plugin is left out of the gate rate, or None. Recorded facts (an "excluded" field in
    plugin_list.json, e.g. unlicensed on this machine) first, then a VST3 with no arm64 slice."""
    if entry.get("excluded"):
        return entry["excluded"]
    if entry["format"] == "vst3" and not native_arm64(entry["bundle"]):
        return "no arm64 slice"
    return None


def row_key(r: dict) -> str:
    return f"{r['plugin']} ({r['format']})"


def summarize(rows: list[dict]) -> dict:
    """Gate rate per host over hostable plugins (see exclusion()). Failures that look the same
    in both hosts are listed as plugin-side, but still count."""
    entries = {(p["name"], p["format"]): p for p in
               json.loads((HERE / "plugin_list.json").read_text())["plugins"]}
    excluded = {}
    for r in rows:
        reason = exclusion(entries[(r["plugin"], r["format"])])
        if reason:
            excluded[row_key(r)] = reason
    scored = [r for r in rows if row_key(r) not in excluded]
    both_fail = [row_key(r) for r in scored
                 if not r["cpp"].get("compatible") and not r["rust"].get("compatible")]
    summary = {"excluded": excluded, "fail_in_both_hosts": both_fail}
    for host in ("cpp", "rust"):
        ok = [r for r in scored if r[host].get("compatible")]
        summary[host] = {"compatible": len(ok), "of": len(scored),
                         "rate": round(len(ok) / max(len(scored), 1), 3),
                         "restore_inconclusive": [row_key(r) for r in scored
                                                  if r[host].get("restore_inconclusive")],
                         "failures": {row_key(r): r[host].get("error") or
                                      f"restore {r[host].get('restore_dbfs')} dBFS"
                                      for r in scored if not r[host].get("compatible")}}
    over = [r["overhead_ms"] for r in rows if "overhead_ms" in r]
    if over:
        summary["overhead_ms_median"] = float(np.median(over))
        summary["overhead_ms_p90"] = float(np.percentile(over, 90))
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "sandbox_sessions" / "host_bakeoff" / time.strftime("%Y%m%d_%H%M%S")))
    ap.add_argument("--only", choices=["compat", "serum", "kill"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--summarize", metavar="RUN_DIR", help="re-score an existing run's compat.json")
    args = ap.parse_args()
    if args.summarize:                      # re-score from the saved wavs with the current rules
        run = Path(args.summarize)
        rows = json.loads((run / "compat.json").read_text())
        for i, row in enumerate(rows, 1):
            for host in ("cpp", "rust"):
                d = run / "compat" / f"{i:02d}_{row['format']}_{host}"
                res = json.loads((d / "result.json").read_text()) if (d / "result.json").exists() else {}
                row[host].update(score({**res, "ok": row[host].get("ok")}, d))
        (run / "compat_rescored.json").write_text(json.dumps(rows, indent=1))
        print(json.dumps(summarize(rows), indent=1))
        return 0
    for b in (HOST_RS, HELPER, HOST_CPP):
        if not b.exists():
            print(f"missing {b}: build the hosts first (README.md)")
            return 2
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    log(f"output -> {out}")
    report = {}
    if args.only in (None, "compat"):
        rows = compat(out, args.limit)
        report["compat"] = summarize(rows)
    if args.only in (None, "serum"):
        report["serum"] = serum(out)
    if args.only in (None, "kill"):
        report["kill"] = kill(out)
    (out / "report.json").write_text(json.dumps(report, indent=1))
    log("report:\n" + json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
