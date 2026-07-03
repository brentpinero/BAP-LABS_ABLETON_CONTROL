"""
review_ui.py — local approval-workflow web app for the sandbox pipeline.

Run: python run_harness.py review   ->  http://127.0.0.1:8765

Privacy-first: binds 127.0.0.1 only, serves bit-exact wavs from
sandbox_sessions/ (no transcoding — auditioning fidelity is the point), no
external assets. All state flows through the EXISTING persistence: sessions'
state.json, the fidelity registry, the live-ears snapshot. Approvals append to
<session>/approvals.json; checkpoint responses go through the same engine call
the MCP tool uses, so UI and MCP stay consistent.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

import sys
_ROOT = Path(__file__).resolve().parent.parent
for p in (str(_ROOT / "sandbox"), str(_ROOT / "harness")):
    if p not in sys.path:
        sys.path.insert(0, p)

from project_state import SESSIONS_DIR, SandboxSession  # noqa: E402
import fidelity  # noqa: E402
import live_ears  # noqa: E402

STAGES = ["plan", "iteration", "serum_render", "scoring", "ears", "fidelity", "final"]
STATIC_DIR = Path(__file__).parent / "review_ui_static"

app = FastAPI(title="BAP Labs Sandbox Review", docs_url=None, redoc_url=None)

from fastapi.staticfiles import StaticFiles  # noqa: E402
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _session_path(session_id: str) -> Path:
    p = (SESSIONS_DIR / session_id).resolve()
    if not str(p).startswith(str(SESSIONS_DIR.resolve())):
        raise HTTPException(403, "path traversal rejected")
    return p


def _state(session_id: str) -> Dict[str, Any]:
    f = _session_path(session_id) / "state.json"
    if not f.exists():
        raise HTTPException(404, f"no session {session_id}")
    return json.loads(f.read_text())


@app.get("/api/sessions")
def list_sessions():
    out = []
    for sid in SandboxSession.list_sessions():
        try:
            st = _state(sid)
            best = max((it["scores"].get("overall") or 0 for it in st["iterations"]), default=None)
            pending = next((c["id"] for c in st["checkpoints"] if c["status"] == "pending"), None)
            out.append({"id": sid, "genre": st["genre"], "state": st["state"],
                        "bpm": st["bpm"], "key": st["key"],
                        "iterations": len(st["iterations"]), "best_score": best,
                        "done_reason": st.get("done_reason", ""),
                        "pending_checkpoint": pending})
        except Exception:
            continue
    return {"sessions": sorted(out, key=lambda s: s["id"], reverse=True)}


@app.get("/api/sessions/{session_id}")
def session_detail(session_id: str):
    st = _state(session_id)
    ap = _session_path(session_id) / "approvals.json"
    st["approvals"] = json.loads(ap.read_text()) if ap.exists() else []
    return st


@app.get("/api/sessions/{session_id}/audio/{iteration}/{name}")
def session_audio(session_id: str, iteration: str, name: str):
    if "/" in name or ".." in name or ".." in iteration:
        raise HTTPException(403, "rejected")
    base = _session_path(session_id) / "iterations" / iteration / name
    if not base.exists():
        raise HTTPException(404, f"no audio {iteration}/{name}")
    return FileResponse(base, media_type="audio/wav")  # starlette handles Range


class CheckpointBody(BaseModel):
    decision: str
    notes: str = ""


@app.post("/api/sessions/{session_id}/checkpoints/{cp_id}")
def respond_checkpoint(session_id: str, cp_id: str, body: CheckpointBody):
    # same engine path the MCP tool uses — UI and MCP stay consistent
    from loop import SandboxEngine
    eng = SandboxEngine(SandboxSession.load(session_id))
    res = eng.respond_checkpoint(cp_id, body.decision, body.notes)
    if "error" in res:
        raise HTTPException(404, res["error"])
    return res


class ApprovalBody(BaseModel):
    stage: str
    verdict: str            # approved | rejected
    notes: str = ""
    iteration: Optional[int] = None


@app.post("/api/sessions/{session_id}/approvals")
def add_approval(session_id: str, body: ApprovalBody):
    if body.stage not in STAGES:
        raise HTTPException(400, f"stage must be one of {STAGES}")
    if body.verdict not in ("approved", "rejected"):
        raise HTTPException(400, "verdict must be approved|rejected")
    f = _session_path(session_id) / "approvals.json"
    log = json.loads(f.read_text()) if f.exists() else []
    log.append({"stage": body.stage, "verdict": body.verdict, "notes": body.notes,
                "iteration": body.iteration, "at": time.strftime("%Y-%m-%dT%H:%M:%S")})
    f.write_text(json.dumps(log, indent=1))
    return {"ok": True, "count": len(log)}


@app.get("/api/fidelity")
def fidelity_registry():
    return {"registry": fidelity.Registry().data,
            "guide": {"measured-identical": ">=40 dB null — headless render is the Ableton sound",
                      "measured-close": "20-40 dB — minor state/latency differences",
                      "diverged": "<20 dB — state transfer failed or nondeterministic patch",
                      "live_only": "Ableton stock device — cannot render headless",
                      "unmeasured": "not calibrated yet (run_harness.py calibrate)"}}


@app.get("/api/fidelity/{key}/audio/{which}")
def fidelity_audio(key: str, which: str):
    if which not in ("headless", "live"):
        raise HTTPException(400, "which must be headless|live")
    entry = fidelity.Registry().data.get(key)
    if not entry or not entry.get("audio_pair", {}).get(which):
        raise HTTPException(404, "no archived pair")
    p = Path(entry["audio_pair"][which]).resolve()
    if not str(p).startswith(str(fidelity.FIDELITY_AUDIO_DIR.resolve())):
        raise HTTPException(403, "rejected")
    if not p.exists():
        raise HTTPException(404, "file missing")
    return FileResponse(p, media_type="audio/wav")


@app.get("/api/ears")
def ears():
    return live_ears._read_snapshot()


@app.get("/")
def index():
    page = STATIC_DIR / "index.html"
    if page.exists():
        return HTMLResponse(page.read_text())
    return HTMLResponse("<h1>Sandbox Review</h1><p>frontend not built yet — API is live at /api/sessions</p>")


def main() -> None:
    import uvicorn
    print("Sandbox Review UI -> http://127.0.0.1:8765  (Ctrl-C to stop)")
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")


if __name__ == "__main__":
    main()
