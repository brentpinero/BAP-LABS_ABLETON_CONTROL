"""Smoke tests for the review UI API (TestClient, no server, no Ableton)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "sandbox"))

from fastapi.testclient import TestClient  # noqa: E402

import review_ui  # noqa: E402
from loop import SandboxEngine  # noqa: E402

client = TestClient(review_ui.app)


def _mk_session():
    eng = SandboxEngine.start("boom bap", ["drums"], bars=2, autonomy="checkpoint")
    return eng.s.id


def test_sessions_list_and_detail():
    sid = _mk_session()
    r = client.get("/api/sessions")
    assert r.status_code == 200
    assert any(s["id"] == sid for s in r.json()["sessions"])
    d = client.get(f"/api/sessions/{sid}")
    assert d.status_code == 200 and d.json()["genre"] == "boom_bap"


def test_traversal_rejected():
    r = client.get("/api/sessions/../../etc/audio/001/x.wav")
    assert r.status_code in (403, 404)
    r2 = client.get("/api/sessions/nope_123")
    assert r2.status_code == 404


def test_checkpoint_roundtrip_mutates_state():
    sid = _mk_session()
    cp = client.get(f"/api/sessions/{sid}").json()["checkpoints"][0]["id"]
    r = client.post(f"/api/sessions/{sid}/checkpoints/{cp}",
                    json={"decision": "proceed as planned", "notes": "dusty"})
    assert r.status_code == 200
    st = client.get(f"/api/sessions/{sid}").json()
    assert st["checkpoints"][0]["status"] == "answered"


def test_approvals_append_and_validate():
    sid = _mk_session()
    ok = client.post(f"/api/sessions/{sid}/approvals",
                     json={"stage": "scoring", "verdict": "approved", "iteration": 1})
    assert ok.status_code == 200
    bad = client.post(f"/api/sessions/{sid}/approvals",
                      json={"stage": "nonsense", "verdict": "approved"})
    assert bad.status_code == 400
    st = client.get(f"/api/sessions/{sid}").json()
    assert st["approvals"][0]["stage"] == "scoring"


def test_fidelity_and_ears_endpoints():
    assert "registry" in client.get("/api/fidelity").json()
    e = client.get("/api/ears").json()  # daemon down -> structured error w/ fix
    assert "error" in e or "status" in e


def _cleanup():
    import shutil
    from project_state import SESSIONS_DIR
    for p in SESSIONS_DIR.glob("sbx_*"):
        shutil.rmtree(p, ignore_errors=True)


if __name__ == "__main__":
    try:
        for name in sorted(k for k in dir() if k.startswith("test_")):
            globals()[name]()
            print(f"  PASS  {name}")
        print("\n5/5 tests passed.")
    finally:
        _cleanup()
