"""
project_state.py — sandbox session/project data model + JSON persistence.

Note format is byte-identical to the Ableton MCP note dicts
({pitch, start_time, duration, velocity}, times in beats) so committing a
winning iteration to Ableton requires zero translation.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# repo root on path so harness.ableton_knowledge imports from anywhere
_ROOT = Path(__file__).resolve().parent.parent
import sys
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT / "harness") not in sys.path:
    sys.path.insert(0, str(_ROOT / "harness"))

import ableton_knowledge as K  # noqa: E402

SESSIONS_DIR = _ROOT / "sandbox_sessions"


@dataclass
class SandboxTrack:
    role: str
    name: str
    notes: List[Dict[str, Any]] = field(default_factory=list)
    instrument_spec: str = "fallback:keys"   # see render_worker instrument grammar
    gain_db: float = 0.0
    pan: float = 0.0                          # -1..1


@dataclass
class SandboxConfig:
    max_iterations: int = 5
    pass_threshold: float = 0.85
    autonomy: str = "checkpoint"              # full | checkpoint | collab
    clap_enabled: bool = False
    render_enabled: bool = True
    render_budget_s: float = 300.0
    bars: int = 8
    overrides: Dict[str, Any] = field(default_factory=dict)  # namespaced config (see config.py)


@dataclass
class IterationRecord:
    index: int
    notes: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)  # role -> raw (pre-groove)
    grooved: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)  # role -> post-groove
    groove_params: Dict[str, Any] = field(default_factory=dict)
    scores: Dict[str, Any] = field(default_factory=dict)   # overall/per_role/tiers
    report: Dict[str, Any] = field(default_factory=dict)
    audio: Dict[str, str] = field(default_factory=dict)    # role|master -> wav path
    render_seconds: float = 0.0


@dataclass
class Checkpoint:
    id: str
    type: str                                  # direction | ab_choice | approve_commit
    question: str
    options: List[str] = field(default_factory=list)
    status: str = "pending"                    # pending | answered
    decision: str = ""
    notes: str = ""


class SandboxSession:
    """One sandbox run: project + config + iteration history + checkpoints."""

    def __init__(self, genre: str, parts: List[str], config: SandboxConfig,
                 instruments: str = "fallback", session_id: Optional[str] = None):
        import secrets
        self.id = session_id or f"sbx_{int(time.time()) % 100000:05d}_{secrets.token_hex(2)}"
        prof = K.genre_profile(genre)
        self.genre = prof["_key"]
        self.bpm = prof["bpm"]
        self.key = prof["key"]
        self.config = config
        self.state = "AWAITING_PLAN"           # AWAITING_PLAN -> AWAITING_COMPOSE -> ... -> DONE
        self.plan: Dict[str, Any] = {}         # the model's accepted PLAN JSON
        self.instrument_mode = instruments     # "fallback" or "plugins"
        self.tracks: Dict[str, SandboxTrack] = {
            role: SandboxTrack(
                role=role,
                name=f"{self.genre.replace('_', ' ').title()} {role.title()}",
                instrument_spec=f"fallback:{role}",
            ) for role in parts
        }
        self.iterations: List[IterationRecord] = []
        self.checkpoints: List[Checkpoint] = []
        self.render_seconds_total = 0.0
        self.done_reason = ""

    # --- derived -----------------------------------------------------------
    @property
    def parts(self) -> List[str]:
        return list(self.tracks.keys())

    def best_iteration(self) -> Optional[IterationRecord]:
        scored = [it for it in self.iterations if it.scores.get("overall") is not None]
        return max(scored, key=lambda it: it.scores["overall"]) if scored else None

    def pending_checkpoint(self) -> Optional[Checkpoint]:
        return next((c for c in self.checkpoints if c.status == "pending"), None)

    def add_checkpoint(self, type_: str, question: str, options: List[str]) -> Checkpoint:
        cp = Checkpoint(id=f"cp_{len(self.checkpoints) + 1:02d}", type=type_,
                        question=question, options=options)
        self.checkpoints.append(cp)
        return cp

    # --- persistence ---------------------------------------------------------
    def dir(self) -> Path:
        return SESSIONS_DIR / self.id

    def save(self) -> None:
        d = self.dir()
        d.mkdir(parents=True, exist_ok=True)
        payload = {
            "id": self.id, "genre": self.genre, "bpm": self.bpm, "key": self.key,
            "state": self.state, "plan": self.plan, "instrument_mode": self.instrument_mode,
            "config": asdict(self.config),
            "tracks": {r: asdict(t) for r, t in self.tracks.items()},
            "iterations": [asdict(it) for it in self.iterations],
            "checkpoints": [asdict(c) for c in self.checkpoints],
            "render_seconds_total": self.render_seconds_total,
            "done_reason": self.done_reason,
        }
        tmp = d / "state.json.tmp"
        tmp.write_text(json.dumps(payload, indent=1))
        os.replace(tmp, d / "state.json")

    @classmethod
    def load(cls, session_id: str) -> "SandboxSession":
        data = json.loads((SESSIONS_DIR / session_id / "state.json").read_text())
        cfg = SandboxConfig(**data["config"])
        s = cls(data["genre"], list(data["tracks"].keys()), cfg,
                instruments=data.get("instrument_mode", "fallback"), session_id=data["id"])
        s.bpm, s.key = data["bpm"], data["key"]
        s.state, s.plan = data["state"], data.get("plan", {})
        s.tracks = {r: SandboxTrack(**t) for r, t in data["tracks"].items()}
        s.iterations = [IterationRecord(**it) for it in data["iterations"]]
        s.checkpoints = [Checkpoint(**c) for c in data["checkpoints"]]
        s.render_seconds_total = data.get("render_seconds_total", 0.0)
        s.done_reason = data.get("done_reason", "")
        return s

    @staticmethod
    def list_sessions() -> List[str]:
        if not SESSIONS_DIR.exists():
            return []
        return sorted(p.name for p in SESSIONS_DIR.iterdir() if (p / "state.json").exists())
