"""
microturn_format.py — re-arrange the recorded perception stream into the ~200ms
INTERLEAVED MICRO-TURN format used by full-duplex interaction models (Thinking Machines
Lab "Interaction Models"; corroborated by Moshi, SyncLLM, Qwen-Omni). See
.claude/MICRO_TURN_DATASET_SPEC.md for the rationale + citations.

Key facts the format encodes (verified against primary sources):
  * A micro-turn = one fixed ~200ms step. The daemon records perception FRAMES at 25Hz
    (40ms). We group DEFAULT 5 frames = 200ms per micro-turn to match Thinking
    Machines Lab's published interaction format. This is a DATASET POLICY, not a claim
    that five SIM frames are a native MiniCPM-o token.
  * ONE interleaved stream, not discrete request/response turns: per micro-turn,
    perception-in (OBSERVED, loss-MASKED) then action-out (PREDICTED). dMel masks the
    input modality by task direction; we mask perception, predict actions/reply/reasoning.
  * Heavy planning and tool work can run asynchronously and return later (TML). The
    schema therefore keeps tool-call, tool-result, and background-result lanes separate.
  * Elapsed time is explicit: wall-time bounds, duration, source steps, discontinuity
    markers, and a periodic sync tag. We never group across a recording gap.

This converter fills the PERCEPTION (masked) half from a recorded trajectory; the
action-out slots (reasoning / actions / reply) are left empty for the collaborator-SFT
and action-pairing steps to populate. `to_vector()` frames are the per-40ms sub-tokens.

Load a recorded session and convert:
    from perception_recorder import load_trajectory
    from microturn_format import to_microturns, save_microturns
    steps = load_trajectory("sandbox_sessions/trajectories/sess_...")["steps"]
    mts = to_microturns(steps)
    save_microturns(mts, "out/session.microturns.jsonl")
"""

from __future__ import annotations

import json
from pathlib import Path

from perception_frame import Frame

CHUNK_FRAMES = 5                       # 5 x 40ms = 200ms micro-turn (matches TML / SyncLLM band)
FRAME_PERIOD_S = 0.04                  # recorder default: 25 Hz
MAX_CONTIGUOUS_GAP_S = 0.08            # tolerate one late tick; split larger gaps


def _round(xs, n=4):
    return [round(float(x), n) for x in xs]


def _contiguous_chunks(steps, chunk_frames, max_gap_s):
    """Yield fixed-size chunks without hiding clock gaps or time reversal."""
    chunk = []
    previous_t = None
    discontinuity = False
    for step in steps:
        t = float(step["t_wall"])
        if previous_t is not None:
            delta = t - previous_t
            if delta <= 0:
                raise ValueError("trajectory t_wall values must be strictly increasing")
            if delta > max_gap_s:
                if chunk:
                    yield chunk, discontinuity
                chunk = []
                discontinuity = True
        chunk.append(step)
        previous_t = t
        if len(chunk) == chunk_frames:
            yield chunk, discontinuity
            chunk = []
            discontinuity = False
    if chunk:
        yield chunk, discontinuity


def to_microturns(steps, chunk_frames: int = CHUNK_FRAMES, sync_every: int = 1,
                  max_gap_s: float = MAX_CONTIGUOUS_GAP_S, strict: bool = True) -> list:
    """Group recorded perception steps into ~200ms interleaved micro-turns.

    Each micro-turn carries the OBSERVED perception (frame vectors + terse text + events)
    as a loss-MASKED input, plus empty PREDICTED slots (reasoning/actions/reply) for the
    SFT + action-pairing passes to fill. `sync_every` controls the periodic sync tag.

    Stopped/silent states are retained because silence and elapsed time are part of an
    interaction model's context. Recording gaps split windows instead of being compressed.
    With strict=True (default), malformed frames fail loudly rather than silently reducing
    the number of perception sub-tokens in a training example.
    """
    if chunk_frames < 1:
        raise ValueError("chunk_frames must be >= 1")
    fs = list(steps)
    mts = []
    for chunk, discontinuity in _contiguous_chunks(fs, chunk_frames, max_gap_s):
        head = chunk[0]["frame"]
        mt_idx = len(mts)
        vectors, events, invalid_frames = [], [], 0
        for s in chunk:
            f = s["frame"]
            try:
                vectors.append(_round(Frame.from_dict(f).to_vector()))
            except Exception as exc:
                invalid_frames += 1
                if strict:
                    raise ValueError("malformed frame at source step %r" % s.get("step")) from exc
            events.extend(s.get("events", []))
        t_start = float(chunk[0]["t_wall"])
        t_end = float(chunk[-1]["t_wall"]) + FRAME_PERIOD_S
        mts.append({
            "schema_version": "sim.microturn.v1",
            "mt": mt_idx,                              # micro-turn index == elapsed-time sense
            "t_start": t_start,
            "t_end": t_end,
            "duration_ms": round((t_end - t_start) * 1000.0, 3),
            "source_steps": [chunk[0].get("step"), chunk[-1].get("step")],
            "discontinuity_before": discontinuity,
            "bar": head.get("bar"), "beat": round(head.get("beat", 0.0), 3),
            "bpm": head.get("bpm"),
            "playing": bool(head.get("playing")),
            "sync": ("[T%d]" % mt_idx) if (mt_idx % max(1, sync_every) == 0) else None,
            "n_frames": len(chunk),
            "invalid_frames": invalid_frames,
            "perception": {                            # MASKED — observed, no loss
                "vectors": vectors,                    # the per-40ms sub-tokens
                "text": head.get("text", ""),          # LLM-readable terse mix state
                "events": events,
            },
            # Optional causal-dataset context is event-driven and observed.  It carries
            # project/hierarchy/device/intervention state without polluting the 25 Hz DSP
            # vector or teaching the model to predict its own evidence.
            "causal_context": head.get("causal_context"),
            "reasoning": None,                         # PREDICTED — optional compact rationale
            "actions": [],                             # PREDICTED — DAW tool calls launched here
            "tool_results": [],                        # OBSERVED — async results arriving here
            "background": [],                          # OBSERVED — async planner updates arriving here
            "reply": None,                             # PREDICTED — spoken/text reply
            # loss_mask: True = observed/masked (no loss); False = predicted
            "loss_mask": {"perception": True, "causal_context": True,
                          "reasoning": False, "actions": False,
                          "tool_results": True, "background": True, "reply": False},
        })
    return mts


def stream_text(microturns, topk_vec: int = 0) -> str:
    """Human-readable render of the interleaved stream (for inspection / a tokenizer
    sanity check): masked PERCEPTION then predicted ACTION per micro-turn, with sync tags."""
    lines = []
    for mt in microturns:
        tag = (mt["sync"] + " ") if mt.get("sync") else ""
        p = mt["perception"]
        ev = (" events=" + ",".join(e.get("type", "?") for e in p["events"])) if p["events"] else ""
        lines.append(f"{tag}bar{mt['bar']}:{mt['beat']:.2f}  ⟨PERCEPTION|masked⟩ {p['text']}{ev}")
        act = mt["actions"] or "∅"
        rsn = mt["reasoning"] or "∅"
        rep = mt["reply"] or "∅"
        lines.append(f"          ⟨ACTION|predict⟩ think={rsn} actions={act} reply={rep}")
    return "\n".join(lines)


def save_microturns(microturns, path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        for mt in microturns:
            fh.write(json.dumps(mt) + "\n")
    return p


def load_microturns(path) -> list:
    with Path(path).open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]
