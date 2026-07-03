"""
loop.py — the deterministic sandbox engine (state machine).

The engine never calls a model. The attached composer (MCP client or MLX driver)
drives it: start() -> [PLAN] -> submit(parts) -> critique -> revise -> ... ->
DONE (pass | plateau | budget), then commit happens outside (sandbox_tools).

Renderer and audio-scorer are injected callables so all loop logic tests run
offline with fakes; when absent, tier weights renormalize to symbolic-only.
"""
from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

import critic
import groove
import midi_metrics
from project_state import (K, IterationRecord, SandboxConfig, SandboxSession)

TIER_WEIGHTS = {"midi": 0.40, "audio": 0.35, "clap": 0.25}
PLATEAU_EPS = 0.02
PLATEAU_AFTER = 3

# Skeleton-first composition order (research: harmony conditions the rest)
ROLE_ORDER = ["chords", "keys", "bass", "drums", "pad", "melody", "lead"]

RendererFn = Callable[[SandboxSession, IterationRecord], Dict[str, Any]]
AudioScorerFn = Callable[[SandboxSession, IterationRecord], Dict[str, Any]]


def _plan_brief(session: SandboxSession) -> Dict[str, Any]:
    sg = K.style_guide(session.genre)
    return {
        "step": "PLAN",
        "instruction": ("Before any notes: return a short PLAN as JSON via "
                        "sandbox_submit(session_id, plan={...}). Keys: key (e.g. 'A minor'), "
                        "progression (roman numerals), motif (one sentence), arrangement "
                        "(one sentence). The critique will hold your notes to this plan."),
        "genre": session.genre, "bpm": session.bpm, "suggested_key": session.key,
        "suggested_progression": sg.get("suggested_progression"),
        "style_feel": sg.get("feel"), "reference_artists": sg.get("reference_artists"),
    }


def _role_brief(session: SandboxSession, role: str) -> Dict[str, Any]:
    sg = K.style_guide(session.genre, role)
    brief = {
        "role": role, "bars": session.config.bars, "bpm": session.bpm,
        "key": session.plan.get("key", session.key),
        "style": {k: sg[k] for k in ("feel", "drums", "harmony", "bass", "melody",
                                     "drum_map", "scale_notes", "avoid") if k in sg},
        "note_schema": {
            "format": "[{pitch:int 0-127, start_time:float beats, duration:float beats, velocity:int 1-127}]",
            "grid": "compose ON-GRID (16ths = multiples of 0.25); the engine applies swing/humanization for you",
            "time": f"bar N starts at beat (N-1)*4; {session.config.bars} bars span 0.0-{session.config.bars * 4}.0",
            "example": [{"pitch": 36, "start_time": 0.0, "duration": 0.5, "velocity": 110}],
        },
    }
    if session.plan:
        brief["your_plan"] = session.plan
    # embed the accepted chord timeline for dependent roles (skeleton-first)
    comp = None
    if session.iterations:
        last = session.iterations[-1]
        comp = last.notes.get("chords") or last.notes.get("keys")
    if comp and role in ("bass", "melody", "lead", "pad"):
        brief["chord_track"] = comp[:64]
        brief["conditioning"] = "Compose AGAINST this chord track — agree with it on strong beats."
    return brief


class SandboxEngine:
    """Wraps a SandboxSession with the iterate/verdict/checkpoint logic."""

    def __init__(self, session: SandboxSession,
                 renderer: Optional[RendererFn] = None,
                 audio_scorer: Optional[AudioScorerFn] = None):
        self.s = session
        self.renderer = renderer
        self.audio_scorer = audio_scorer

    # --- lifecycle ---------------------------------------------------------
    @classmethod
    def start(cls, genre: str, parts: Optional[List[str]] = None, bars: int = 8,
              autonomy: str = "checkpoint", instruments: str = "fallback",
              renderer: Optional[RendererFn] = None,
              audio_scorer: Optional[AudioScorerFn] = None,
              **cfg_overrides) -> "SandboxEngine":
        parts = parts or ["drums", "bass", "chords", "melody"]
        parts = sorted(parts, key=lambda r: ROLE_ORDER.index(r) if r in ROLE_ORDER else 99)
        config = SandboxConfig(autonomy=autonomy, bars=bars, **cfg_overrides)
        session = SandboxSession(genre, parts, config, instruments=instruments)
        eng = cls(session, renderer, audio_scorer)
        if autonomy in ("checkpoint", "collab"):
            session.add_checkpoint(
                "direction",
                f"Starting a {session.genre.replace('_', ' ')} sandbox ({bars} bars, "
                f"{session.bpm} BPM, {session.key}, parts: {', '.join(parts)}). "
                f"Any creative direction before composing? (mood, reference, key, energy)",
                ["proceed as planned", "give direction"])
        session.save()
        return eng

    def briefs(self) -> Dict[str, Any]:
        """What the composer needs right now (plan brief or role briefs)."""
        if self.s.state == "AWAITING_PLAN":
            return {"plan_brief": _plan_brief(self.s),
                    "then": "Role briefs follow after the plan is accepted."}
        return {"role_briefs": {r: _role_brief(self.s, r) for r in self.s.parts},
                "order": [r for r in self.s.parts]}

    # --- checkpoints ---------------------------------------------------------
    def respond_checkpoint(self, checkpoint_id: str, decision: str, notes: str = "") -> Dict[str, Any]:
        cp = next((c for c in self.s.checkpoints if c.id == checkpoint_id), None)
        if cp is None:
            return {"error": f"no checkpoint {checkpoint_id}"}
        cp.status, cp.decision, cp.notes = "answered", decision, notes
        if cp.type == "direction" and notes:
            self.s.plan.setdefault("user_direction", notes)
        self.s.save()
        return {"ok": True, "state": self.s.state}

    def _gate(self) -> Optional[Dict[str, Any]]:
        cp = self.s.pending_checkpoint()
        if cp:
            return {"checkpoint": {
                "id": cp.id, "type": cp.type, "question": cp.question, "options": cp.options,
                "instruction": ("STOP. Ask the USER this question verbatim, then call "
                                f"sandbox_checkpoint_respond(session_id='{self.s.id}', "
                                f"checkpoint_id='{cp.id}', decision=..., notes=...).")}}
        return None

    # --- the loop ------------------------------------------------------------
    def submit(self, parts: Optional[Dict[str, List[Dict]]] = None,
               plan: Optional[Dict[str, Any]] = None,
               groove_params: Optional[Dict[str, Any]] = None,
               comment: str = "") -> Dict[str, Any]:
        gate = self._gate()
        if gate:
            return gate
        if self.s.state == "DONE":
            best = self.s.best_iteration()
            return {"done": self.s.done_reason,
                    "best_iteration": best.index if best else None,
                    "next": "Session finished — sandbox_commit or sandbox_start a new one."}

        if plan:
            self.s.plan.update(plan)
            if str(plan.get("key", "")).strip():
                self.s.key = plan["key"]
            self.s.state = "AWAITING_COMPOSE"
            self.s.save()
            return {"plan_accepted": self.s.plan, **self.briefs(),
                    "next": "Compose per the role briefs (skeleton order: chords first), "
                            f"then sandbox_submit(session_id='{self.s.id}', parts={{role: [notes]}})."}

        if self.s.state == "AWAITING_PLAN":
            # allow plan-less fast path for full-autonomy big models
            self.s.state = "AWAITING_COMPOSE"

        if not parts:
            return {"error": "submit parts={role: [notes]} (or plan={...} first)",
                    **self.briefs()}

        # merge partial submits over the previous iteration's notes
        prev_notes = dict(self.s.iterations[-1].notes) if self.s.iterations else {}
        merged = {**prev_notes, **{r: n for r, n in parts.items() if r in self.s.tracks}}
        unknown = [r for r in parts if r not in self.s.tracks]

        rec = IterationRecord(index=len(self.s.iterations) + 1, notes=merged,
                              groove_params=groove_params or {})
        # groove pass (score/performance separation)
        rec.grooved = {r: groove.apply_groove(n, self.s.genre, r, groove_params, seed=rec.index)
                       for r, n in merged.items()}

        # render (optional/injected) + audio tier
        tiers: Dict[str, float] = {}
        if self.renderer and self.s.config.render_enabled:
            t0 = time.monotonic()
            render_out = self.renderer(self.s, rec) or {}
            rec.render_seconds = round(time.monotonic() - t0, 2)
            self.s.render_seconds_total += rec.render_seconds
            rec.audio = render_out.get("audio", {})
        if self.audio_scorer and rec.audio:
            audio_scores = self.audio_scorer(self.s, rec) or {}
            if "audio" in audio_scores:
                tiers["audio"] = audio_scores["audio"]
            if "clap" in audio_scores:
                tiers["clap"] = audio_scores["clap"]

        # tier 0: symbolic
        per_role_detail = {
            r: midi_metrics.score_role(r, rec.grooved.get(r, []), self.s,
                                       self.s.config.bars, context=rec.grooved)
            for r in merged
        }
        global_detail = midi_metrics.score_global(rec.grooved, self.s, self.s.config.bars)
        role_scores = [d["score"] for d in per_role_detail.values()] + [global_detail["score"]]
        tiers["midi"] = round(sum(role_scores) / len(role_scores), 4)

        # weighted overall (renormalize over present tiers; clap halved on fallback synth)
        weights = {}
        for tier, w in TIER_WEIGHTS.items():
            if tier in tiers:
                weights[tier] = w * (0.5 if tier == "clap" and self.s.instrument_mode == "fallback" else 1.0)
        wsum = sum(weights.values())
        overall = round(sum(tiers[t] * w for t, w in weights.items()) / wsum, 4)

        prev_best = self.s.best_iteration()
        prev_best_score = prev_best.scores["overall"] if prev_best else None
        rec.scores = {"overall": overall, "tiers": tiers,
                      "per_role_detail": per_role_detail, "global_detail": global_detail,
                      "per_role": {r: d["score"] for r, d in per_role_detail.items()}}
        self.s.iterations.append(rec)

        verdict = self._verdict(overall)
        report = critic.build_report(self.s, rec, verdict, prev_best_score)
        if unknown:
            report["warning"] = f"ignored unknown roles: {unknown}"
        rec.report = {k: report[k] for k in ("verdict", "scores", "critique")}

        # checkpoints by autonomy
        if verdict in ("pass", "plateau", "budget"):
            self.s.state = "DONE"
            self.s.done_reason = verdict
            self.s.add_checkpoint(
                "approve_commit",
                f"Sandbox finished ({verdict}) — best is iteration "
                f"#{self.s.best_iteration().index} at {self.s.best_iteration().scores['overall']:.2f}. "
                f"Audition the wavs, then approve committing to Ableton?",
                ["commit best", "commit a different iteration", "discard"])
            report["checkpoint"] = self._gate()["checkpoint"]
        elif self.s.config.autonomy == "collab":
            self.s.state = "AWAITING_REVISION"
            cp = self.s.add_checkpoint(
                "ab_choice",
                f"Iteration {rec.index} scored {overall:.2f}. Direction for the next pass?",
                ["follow the critique", "give direction", "stop and use best"])
            report["checkpoint"] = self._gate()["checkpoint"]
        else:
            self.s.state = "AWAITING_REVISION"

        self.s.save()
        return report

    def _verdict(self, overall: float) -> str:
        if overall >= self.s.config.pass_threshold:
            return "pass"
        n = len(self.s.iterations)
        if n >= self.s.config.max_iterations:
            return "budget"
        if self.s.render_seconds_total > self.s.config.render_budget_s:
            return "budget"
        if n >= PLATEAU_AFTER:
            scores = [it.scores["overall"] for it in self.s.iterations]
            best_now = max(scores)
            best_before = max(scores[:-2]) if len(scores) > 2 else 0.0
            if best_now - best_before < PLATEAU_EPS:
                return "plateau"
        return "revise"
