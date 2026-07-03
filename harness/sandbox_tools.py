"""
sandbox_tools.py — MCP surface for the headless sandbox loop.

register_sandbox_tools(mcp, deps) is called from ableton_mcp_server.py; `deps`
carries the server's helpers (_ok/_err/do_add_part) so there are no circular
imports. The sandbox validates COMPOSITION (notes/groove/harmony/balance) with
proxy or VST instruments — final sound design happens in Ableton on commit,
where the real genre instruments are loaded.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

_ROOT = Path(__file__).resolve().parent.parent
for p in (str(_ROOT / "sandbox"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from loop import SandboxEngine  # noqa: E402
from project_state import SandboxSession  # noqa: E402
import renderer as sandbox_renderer  # noqa: E402

try:  # Tier 1/2 ears are optional — engine renormalizes weights without them
    import audio_metrics as sandbox_ears
    _AUDIO_SCORER = sandbox_ears.audio_scorer
except Exception:  # pragma: no cover
    _AUDIO_SCORER = None

_ENGINES: Dict[str, SandboxEngine] = {}


def _engine(session_id: str) -> SandboxEngine:
    if session_id in _ENGINES:
        return _ENGINES[session_id]
    eng = SandboxEngine(SandboxSession.load(session_id),
                        renderer=sandbox_renderer.render_iteration,
                        audio_scorer=_AUDIO_SCORER)
    _ENGINES[session_id] = eng
    return eng


def register_sandbox_tools(mcp, deps: Dict[str, Any]) -> None:
    _ok, _err = deps["ok"], deps["err"]
    do_add_part = deps["do_add_part"]

    @mcp.tool()
    def sandbox_start(genre: str = "boom bap", parts: List[str] = None, bars: int = 8,
                      autonomy: str = "checkpoint", instruments: str = "fallback") -> str:
        """Start a headless COMPOSE-LISTEN-REVISE session: you compose MIDI, the sandbox renders it
        offline, scores it (groove/harmony/genre metrics), and critiques — iterate until it's good,
        THEN commit to Ableton. Nothing touches Ableton until sandbox_commit. Returns the PLAN brief
        (submit a plan first) and any user checkpoint to relay. autonomy: full (auto until commit) |
        checkpoint (direction + A/B + approve; default) | collab (pause every iteration).
        instruments: fallback (fast proxy synths — validates composition, not final sound) | plugins
        (your VST/AU via track instrument_spec). parts default: drums,bass,chords,melody."""
        try:
            eng = SandboxEngine.start(genre, parts, bars=bars, autonomy=autonomy,
                                      instruments=instruments,
                                      renderer=sandbox_renderer.render_iteration,
                                      audio_scorer=_AUDIO_SCORER)
            _ENGINES[eng.s.id] = eng
            out = {"session_id": eng.s.id, "genre": eng.s.genre, "bpm": eng.s.bpm,
                   "key": eng.s.key, "bars": bars, **eng.briefs()}
            gate = eng._gate()
            if gate:
                out.update(gate)
            out["next"] = ("Answer any checkpoint, then sandbox_submit(session_id, plan={key, "
                           "progression, motif, arrangement}). After the plan: compose per role "
                           "briefs (chords first) and sandbox_submit(session_id, parts={role: [notes]}).")
            return _ok(out)
        except Exception as e:
            return _err("starting sandbox", e)

    @mcp.tool()
    def sandbox_submit(session_id: str, parts: Dict[str, List[Dict[str, Any]]] = None,
                       plan: Dict[str, Any] = None, groove_params: Dict[str, Any] = None,
                       comment: str = "") -> str:
        """Submit your PLAN (first) or composed MIDI parts to the sandbox. parts = {role: [notes]}
        — full or partial (only revised roles; the rest carry over). Compose ON-GRID (16ths); the
        engine applies genre swing/humanization (override via groove_params: swing, velocity_jitter,
        accent, push, timing_jitter). Renders headless, scores, and returns a critique with ranked
        priorities + an explicit `next` step. STOP and relay any `checkpoint` to the user."""
        try:
            report = _engine(session_id).submit(parts=parts, plan=plan,
                                                groove_params=groove_params, comment=comment)
            return _ok(report)
        except Exception as e:
            return _err("submitting to sandbox", e)

    @mcp.tool()
    def sandbox_status(session_id: str = "") -> str:
        """List sandbox sessions, or one session's state: iteration scores, best-so-far, budget,
        pending checkpoint."""
        try:
            if not session_id:
                return _ok({"sessions": SandboxSession.list_sessions()})
            s = _engine(session_id).s
            best = s.best_iteration()
            return _ok({
                "session_id": s.id, "state": s.state, "genre": s.genre, "bpm": s.bpm,
                "key": s.key, "parts": s.parts, "plan": s.plan,
                "iterations": [{"index": it.index, "overall": it.scores.get("overall"),
                                "per_role": it.scores.get("per_role")} for it in s.iterations],
                "best_iteration": best.index if best else None,
                "done_reason": s.done_reason,
                "pending_checkpoint": (s.pending_checkpoint().id if s.pending_checkpoint() else None),
                "render_seconds_used": round(s.render_seconds_total, 1),
            })
        except Exception as e:
            return _err("reading sandbox status", e)

    @mcp.tool()
    def sandbox_listen(session_id: str, iteration: int = -1, track: str = "master") -> str:
        """Get one iteration's rendered audio path (for the USER to audition) + its scores and
        critique. track: master or a role name. iteration -1 = latest, -2 = previous, or an index."""
        try:
            s = _engine(session_id).s
            if not s.iterations:
                return _ok({"error": "no iterations yet"})
            it = s.iterations[iteration] if iteration < 0 else \
                next((x for x in s.iterations if x.index == iteration), s.iterations[-1])
            return _ok({
                "iteration": it.index,
                "wav": it.audio.get(track) or it.audio,
                "scores": {"overall": it.scores.get("overall"),
                           "per_role": it.scores.get("per_role")},
                "critique": it.report.get("critique", {}),
                "note": "Play the wav for the user — proxy instruments validate the COMPOSITION, "
                        "not the final Ableton sound.",
            })
        except Exception as e:
            return _err("listening to sandbox iteration", e)

    @mcp.tool()
    def sandbox_ab(session_id: str, iteration_a: int = -1, iteration_b: int = -2) -> str:
        """Compare two iterations side by side (scores, per-role deltas, both wav paths) — use at
        plateau checkpoints so the user can pick a direction."""
        try:
            s = _engine(session_id).s
            if len(s.iterations) < 2:
                return _ok({"error": "need at least 2 iterations to A/B"})
            def pick(i):
                return s.iterations[i] if i < 0 else \
                    next((x for x in s.iterations if x.index == i), s.iterations[-1])
            a, b = pick(iteration_a), pick(iteration_b)
            return _ok({
                "a": {"iteration": a.index, "overall": a.scores.get("overall"),
                      "per_role": a.scores.get("per_role"), "wav": a.audio.get("master")},
                "b": {"iteration": b.index, "overall": b.scores.get("overall"),
                      "per_role": b.scores.get("per_role"), "wav": b.audio.get("master")},
                "delta": {r: round(a.scores.get("per_role", {}).get(r, 0) -
                                   b.scores.get("per_role", {}).get(r, 0), 3)
                          for r in s.parts},
                "next": "Play both wavs for the user and ask which direction to take.",
            })
        except Exception as e:
            return _err("comparing iterations", e)

    @mcp.tool()
    def sandbox_checkpoint_respond(session_id: str, checkpoint_id: str,
                                   decision: str, notes: str = "") -> str:
        """Record the USER's answer to a sandbox checkpoint (direction/A-B/approve). Pass their
        creative direction in `notes` — it becomes part of the session plan."""
        try:
            return _ok(_engine(session_id).respond_checkpoint(checkpoint_id, decision, notes))
        except Exception as e:
            return _err("responding to checkpoint", e)

    @mcp.tool()
    def sandbox_commit(session_id: str, iteration: int = 0, start_bar: int = 0) -> str:
        """Place a finished sandbox iteration into Ableton: per role, creates a track, loads the
        REAL genre-appropriate instrument, writes the (grooved) notes into the arrangement.
        iteration 0 = the best-scoring one. REFUSES while an approve checkpoint is pending — ask
        the user first. Follow with balance_mix() and get_playability_report()."""
        try:
            eng = _engine(session_id)
            s = eng.s
            cp = s.pending_checkpoint()
            if cp is not None:
                return _ok({"refused": "checkpoint pending", "checkpoint": {
                    "id": cp.id, "type": cp.type, "question": cp.question,
                    "options": cp.options,
                    "instruction": "Ask the USER, then sandbox_checkpoint_respond(...) before committing."}})
            it = s.best_iteration() if iteration == 0 else \
                next((x for x in s.iterations if x.index == iteration), None)
            if it is None:
                return _ok({"error": f"no iteration {iteration}"})
            placed = []
            for role in s.parts:
                notes = it.grooved.get(role) or it.notes.get(role) or []
                if not notes:
                    continue
                res = do_add_part(role, s.genre, s.config.bars, start_bar, None, notes,
                                  set_bpm=(role == s.parts[0]))
                placed.append(res)
            return _ok({"committed_iteration": it.index, "score": it.scores.get("overall"),
                        "placed": placed,
                        "next": "Call balance_mix() then get_playability_report(); "
                                "then start_playback to hear it in Ableton."})
        except Exception as e:
            return _err("committing sandbox iteration", e)

    @mcp.tool()
    def sandbox_config(session_id: str, max_iterations: int = None, pass_threshold: float = None,
                       autonomy: str = None, render_enabled: bool = None) -> str:
        """Adjust a running session's budget/threshold/autonomy ('full'|'checkpoint'|'collab')."""
        try:
            s = _engine(session_id).s
            for name, val in (("max_iterations", max_iterations),
                              ("pass_threshold", pass_threshold),
                              ("autonomy", autonomy), ("render_enabled", render_enabled)):
                if val is not None:
                    setattr(s.config, name, val)
            s.save()
            from dataclasses import asdict
            return _ok({"config": asdict(s.config)})
        except Exception as e:
            return _err("configuring sandbox", e)
