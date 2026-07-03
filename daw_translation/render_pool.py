"""
render_pool.py — Parallel render orchestrator (spike S5, the scale answer).

Fans out render jobs across CPU cores by invoking render_worker.py as separate
SUBPROCESSES. Two reasons it shells out instead of importing the worker:
  1. Licensing: pedalboard is GPLv3 — keeping it behind a process boundary means
     this orchestrator (the product) never links GPL code in-process.
  2. Robustness: a plugin that crashes/hangs takes down one worker process, not
     the whole run.

This is what makes 100s-of-tracks projects tractable: rendering printed FX is the
expensive step, and it's embarrassingly parallel. We add a content-hash cache so
re-translating a project never re-renders unchanged tracks.

No pedalboard import here — intentionally.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

_WORKER = Path(__file__).with_name("render_worker.py")


def default_workers() -> int:
    """Bounded pool: cores - 2, floored at 1 (matches the repo's concurrency habit)."""
    return max(1, (os.cpu_count() or 4) - 2)


DEFAULT_TIMEOUT_S = 120  # a hung plugin kills one job, never the loop


def _job_key(job: dict) -> str:
    """Content hash of (input identity + instrument + chain) — stable cache key.

    MIDI jobs hash the notes file CONTENT (not mtime): the sandbox rewrites
    notes.json every iteration, and only actually-changed roles should re-render.
    """
    h = hashlib.sha256()
    if "midi" in job:
        try:
            h.update(Path(job["midi"]).read_bytes())
        except OSError:
            h.update(str(job["midi"]).encode())
        h.update(f"|{job.get('bpm', 120)}|{job.get('instrument', 'fallback:keys')}"
                 f"|{job.get('bars', '')}|{job.get('tail_seconds', '')}"
                 f"|{job.get('sr', 44100)}".encode())
        h.update(json.dumps(job.get("params") or {}, sort_keys=True).encode())
    else:
        inp = job["input"]
        if inp != "sine" and os.path.exists(inp):
            st = os.stat(inp)
            h.update(f"{inp}:{st.st_size}:{int(st.st_mtime)}".encode())
        else:
            h.update(str(inp).encode())
        h.update(f"|sr={job.get('sr', 44100)}".encode())
    h.update(json.dumps(job.get("chain", []), sort_keys=True).encode())
    return h.hexdigest()[:16]


def _build_cmd(job: dict) -> list[str]:
    cmd = [sys.executable, str(_WORKER), "--out", job["output"],
           "--chain", json.dumps(job.get("chain", []))]
    if "midi" in job:
        cmd += ["--midi", job["midi"], "--bpm", str(job.get("bpm", 120)),
                "--instrument", job.get("instrument", "fallback:keys")]
        if job.get("bars") is not None:
            cmd += ["--bars", str(job["bars"])]
        if job.get("tail_seconds") is not None:
            cmd += ["--tail-seconds", str(job["tail_seconds"])]
        if job.get("params"):
            cmd += ["--params", json.dumps(job["params"])]
    else:
        cmd += ["--in", job["input"]]
    if "sr" in job:
        cmd += ["--sr", str(job["sr"])]
    return cmd


def _run_one(job: dict, cache_dir: Path | None) -> dict:
    out = job["output"]
    key = _job_key(job)

    # Cache hit: output already exists and its sidecar key matches.
    if cache_dir is not None:
        marker = cache_dir / f"{key}.done"
        if marker.exists() and os.path.exists(out):
            return {"output": out, "status": "cached", "key": key, "seconds": 0.0}

    t0 = time.monotonic()
    try:
        proc = subprocess.run(_build_cmd(job), capture_output=True, text=True,
                              timeout=job.get("timeout", DEFAULT_TIMEOUT_S))
    except subprocess.TimeoutExpired:
        return {"output": out, "status": "timeout", "key": key,
                "seconds": round(time.monotonic() - t0, 3)}
    dt = round(time.monotonic() - t0, 3)

    if proc.returncode != 0:
        return {"output": out, "status": "error", "key": key, "seconds": dt,
                "stderr": proc.stderr.strip()[-500:]}

    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / f"{key}.done").write_text("ok")
    return {"output": out, "status": "rendered", "key": key, "seconds": dt}


def render_jobs(jobs: list[dict], max_workers: int | None = None,
                cache_dir: str | os.PathLike | None = None) -> list[dict]:
    """Render many jobs in parallel.

    Audio job: {"input": path|'sine', "chain": [...], "output": path, "sr"?: int}
    MIDI job:  {"midi": notes.json path, "bpm": float, "instrument": spec,
                "chain"?: [...], "output": path, "sr"?: int, "bars"?: float,
                "tail_seconds"?: float, "timeout"?: int}
    Returns one result dict per job (order preserved). Statuses: rendered|cached|error|timeout.
    """
    workers = max_workers or default_workers()
    cdir = Path(cache_dir) if cache_dir else None
    results: list[dict] = [None] * len(jobs)  # type: ignore[list-item]

    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_run_one, job, cdir): i for i, job in enumerate(jobs)}
        for fut in cf.as_completed(futures):
            results[futures[fut]] = fut.result()
    return results


if __name__ == "__main__":
    # Demo: render N sine tones through different gains, in parallel, with caching.
    import tempfile

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    with tempfile.TemporaryDirectory() as d:
        jobs = [
            {"input": "sine", "sr": 44100,
             "chain": [{"builtin": "Gain", "params": {"gain_db": float(i)}}],
             "output": os.path.join(d, f"tone_{i}.wav")}
            for i in range(n)
        ]
        t0 = time.monotonic()
        res = render_jobs(jobs, cache_dir=os.path.join(d, "cache"))
        print(f"{n} jobs on {default_workers()} workers in {time.monotonic()-t0:.2f}s")
        print("  statuses:", {r["status"]: sum(1 for x in res if x["status"] == r["status"]) for r in res})
        t1 = time.monotonic()
        res2 = render_jobs(jobs, cache_dir=os.path.join(d, "cache"))
        print(f"re-run (cached) in {time.monotonic()-t1:.2f}s ->",
              {"cached": sum(1 for r in res2 if r["status"] == "cached")})
