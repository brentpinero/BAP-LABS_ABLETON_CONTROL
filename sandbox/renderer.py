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

SR = 44100
TAIL_SECONDS = 1.0


def render_iteration(session, record) -> Dict[str, Any]:
    """Render every role's grooved notes to stems + a summed master.
    Returns {"audio": {role: wav_path, ..., "master": wav_path}, "pool": results}."""
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
            "output": str(it_dir / f"{role}.wav"), "sr": SR,
            "bars": session.config.bars, "tail_seconds": TAIL_SECONDS,
        })
        roles.append(role)

    results = render_pool.render_jobs(jobs, cache_dir=cache)
    audio: Dict[str, str] = {}
    stems: Dict[str, np.ndarray] = {}
    for role, res in zip(roles, results):
        if res["status"] in ("rendered", "cached"):
            audio[role] = res["output"]
            data, _ = sf.read(res["output"], dtype="float32", always_2d=True)
            stems[role] = data  # (n, ch)

    if stems:
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
        peak = float(np.max(np.abs(master))) or 1.0
        if peak > 0.98:
            master *= 0.98 / peak
        master_path = it_dir / "master.wav"
        sf.write(master_path, master.astype("float32"), SR)
        audio["master"] = str(master_path)

    return {"audio": audio, "pool": results}
