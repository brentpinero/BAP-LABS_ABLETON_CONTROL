"""
renderer.py — sandbox render orchestration (NO pedalboard import here).

Builds one render-pool job per track from the iteration's grooved notes, fans
out to daw_translation/render_pool (subprocess workers, content-hash cache),
then sums stems into master.wav in numpy with per-track gain and constant-power
pan. Only changed roles re-render across iterations thanks to the pool cache.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
import soundfile as sf

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT / "daw_translation") not in sys.path:
    sys.path.insert(0, str(_ROOT / "daw_translation"))

import render_pool  # noqa: E402

from config import cfg  # noqa: E402

SR = 44100
TAIL_SECONDS = 1.0


def render_iteration_dispatch(session, record) -> Dict[str, Any]:
    """Backend-selecting renderer wired into the loop. Reads `render.backend` from
    session config each iteration so the fast tier (pedalboard/dawdreamer) and the
    truth tier (isolated Ableton render node) are switchable per session with no
    code change at the injection seam."""
    backend = cfg(session, "render.backend")
    if backend == "ableton":
        from renderer_live import render_iteration_live  # lazy: pulls in Live client
        return render_iteration_live(session, record)
    if backend == "dawdreamer":
        raise NotImplementedError("render.backend='dawdreamer' lands in Phase 4")
    return render_iteration(session, record)  # pedalboard (default fast tier)


def render_iteration(session, record) -> Dict[str, Any]:
    """Render every role's grooved notes to stems + a summed master.
    Returns {"audio": {role: wav_path, ..., "master": wav_path}, "pool": results}."""
    sr = cfg(session, "audio.sr")
    tail = cfg(session, "audio.tail_seconds")
    it_dir = session.dir() / "iterations" / f"{record.index:03d}"
    it_dir.mkdir(parents=True, exist_ok=True)
    cache = session.dir() / ".render_cache"

    jobs, roles = [], []
    for role, notes in record.grooved.items():
        if not notes:
            continue
        notes_path = it_dir / f"{role}.notes.json"
        notes_path.write_text(json.dumps({"notes": notes, "bars": session.config.bars}))
        jobs.append({
            "midi": str(notes_path), "bpm": session.bpm,
            "instrument": session.tracks[role].instrument_spec,
            "params": session.tracks[role].params or None,
            "output": str(it_dir / f"{role}.wav"), "sr": sr,
            "bars": session.config.bars, "tail_seconds": tail,
        })
        roles.append(role)

    results = render_pool.render_jobs(jobs, cache_dir=cache,
                                      use_warm_host=cfg(session, "render.warm_host"))
    audio: Dict[str, str] = {}
    for role, res in zip(roles, results):
        if res["status"] in ("rendered", "cached"):
            audio[role] = res["output"]

    sum_stems_to_master(session, audio, it_dir, sr)  # writes master.wav into audio
    return {"audio": audio, "pool": results}


def sum_stems_to_master(session, audio: Dict[str, str], it_dir: Path, sr: int) -> None:
    """Sum per-role stem wavs into master.wav (per-track gain + constant-power pan),
    peak-normalized. Mutates `audio` to add the "master" entry. Shared by the
    pedalboard renderer and the Ableton render-node renderer so the master bus
    is computed identically regardless of stem source."""
    stems: Dict[str, np.ndarray] = {}
    for role, path in audio.items():
        if role == "master":
            continue
        data, _ = sf.read(path, dtype="float32", always_2d=True)
        stems[role] = data  # (n, ch)
    if not stems:
        return
    length = max(s.shape[0] for s in stems.values())
    master = np.zeros((length, 2), dtype="float64")
    for role, s in stems.items():
        trk = session.tracks[role]
        gain = 10.0 ** (trk.gain_db / 20.0)
        theta = (float(np.clip(trk.pan, -1, 1)) + 1.0) * np.pi / 4.0  # constant-power
        l_gain, r_gain = np.cos(theta) * gain, np.sin(theta) * gain
        st = np.repeat(s, 2, axis=1) if s.shape[1] == 1 else s[:, :2]
        master[: st.shape[0], 0] += st[:, 0] * l_gain * np.sqrt(2)
        master[: st.shape[0], 1] += st[:, 1] * r_gain * np.sqrt(2)
    norm = cfg(session, "audio.normalize_peak")
    peak = float(np.max(np.abs(master))) or 1.0
    if peak > norm:
        master *= norm / peak
    master_path = it_dir / "master.wav"
    sf.write(master_path, master.astype("float32"), sr)
    audio["master"] = str(master_path)
