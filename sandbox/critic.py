"""
critic.py — deterministic metrics → musician-readable critique.

Research-backed principle (ComposerX/Libretto): ranked, actionable, prose
feedback beats raw numbers. Every report ends with an explicit `next`
instruction so any model — including small ones — knows exactly what to do.
"""
from __future__ import annotations

from typing import Any, Dict, List


def _failing(metrics: List[Dict[str, Any]], threshold: float = 0.75) -> List[Dict[str, Any]]:
    return sorted((m for m in metrics if m["score"] < threshold), key=lambda m: m["score"])


def _line(role: str, m: Dict[str, Any]) -> str:
    return f"{role}: {m['explain']} (measured {m['value']}, want {m['target']})"


def build_report(session, record, verdict: str, prev_best: float | None) -> Dict[str, Any]:
    per_role = {r: v["score"] for r, v in record.scores.get("per_role_detail", {}).items()}
    overall = record.scores.get("overall", 0.0)

    # ranked priorities: worst failing metrics across roles, capped at 3
    ranked: List[tuple] = []
    for role, detail in record.scores.get("per_role_detail", {}).items():
        for m in _failing(detail["metrics"]):
            ranked.append((m["score"], role, m))
    for m in _failing(record.scores.get("global_detail", {}).get("metrics", [])):
        ranked.append((m["score"], "global", m))
    ranked.sort(key=lambda x: x[0])
    priorities = [_line(role, m) for _, role, m in ranked[:3]]

    weakest = sorted(per_role, key=per_role.get)[:2] if per_role else []
    if verdict == "pass":
        summary = f"This one works — overall {overall:.2f}. Ship it or keep polishing."
    elif priorities:
        summary = (f"Overall {overall:.2f}. Strongest: "
                   f"{max(per_role, key=per_role.get) if per_role else '-'}; "
                   f"fix {', '.join(weakest)} first.")
    else:
        summary = f"Overall {overall:.2f}. No individual metric failing — refine taste-level details."

    per_role_notes = {
        role: [_line("", m).lstrip(": ") for m in _failing(detail["metrics"])[:3]]
        for role, detail in record.scores.get("per_role_detail", {}).items()
        if _failing(detail["metrics"])
    }

    delta = None if prev_best is None else round(overall - prev_best, 4)

    if verdict == "pass":
        nxt = (f"Verdict PASS. Present the result to the user; on approval call "
               f"sandbox_commit(session_id='{session.id}').")
    elif verdict in ("plateau", "budget"):
        best = session.best_iteration()
        nxt = (f"Loop ended ({verdict}). Best iteration is #{best.index if best else '?'} "
               f"(score {best.scores.get('overall') if best else '?'}). Use sandbox_ab to compare "
               f"candidates or sandbox_commit to place the best one.")
    else:
        revise = sorted(per_role_notes) or session.parts
        nxt = (f"Revise ONLY {', '.join(revise[:2])} per the priorities, then call "
               f"sandbox_submit(session_id='{session.id}', parts={{...only revised roles...}}). "
               f"{record.scores.get('iterations_left', '')}")

    return {
        "session_id": session.id,
        "iteration": record.index,
        "verdict": verdict,
        "scores": {
            "overall": overall,
            "per_role": per_role,
            "tiers": record.scores.get("tiers", {}),
            "delta_vs_prev_best": delta,
        },
        "critique": {
            "summary": summary,
            "priorities": priorities,
            "per_role": per_role_notes,
        },
        "audio": record.audio,
        "budget": {
            "iterations_used": record.index,
            "iterations_max": session.config.max_iterations,
            "render_seconds_used": round(session.render_seconds_total, 1),
        },
        "next": nxt,
    }
