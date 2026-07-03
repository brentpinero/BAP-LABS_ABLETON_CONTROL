"""
midi_metrics.py — Tier-0 symbolic scoring (milliseconds, no audio).

Metric names follow the MusPy / music-generation-evaluation literature where we
overlap it: pitch_class_entropy, scale_consistency (pitch-in-scale rate),
groove_consistency (mean Hamming similarity of neighboring measures on a 16-step
onset grid), empty_beat_rate, polyphony. Each metric returns
{name, value, score (0-1), target, explain} so the critic can speak musician.
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Any, Dict, List, Optional

from project_state import K

BEATS_PER_BAR = 4
GRID = 4  # 16th-note resolution steps per beat


def _m(name: str, value: float, score: float, target: str, explain: str) -> Dict[str, Any]:
    return {"name": name, "value": round(float(value), 4),
            "score": round(float(max(0.0, min(1.0, score))), 4),
            "target": target, "explain": explain}


def _onset_grid(notes: List[Dict], bars: int) -> List[List[int]]:
    """Per-bar binary onset vectors at 16th resolution (for groove_consistency)."""
    grids = [[0] * (BEATS_PER_BAR * GRID) for _ in range(max(1, bars))]
    for n in notes:
        t = float(n.get("start_time", 0.0))
        bar = int(t // BEATS_PER_BAR)
        if bar < len(grids):
            step = int(round((t % BEATS_PER_BAR) * GRID)) % (BEATS_PER_BAR * GRID)
            grids[bar][step] = 1
    return grids


def _band_score(value: float, lo: float, hi: float, soft: float) -> float:
    """1.0 inside [lo,hi], linear falloff over `soft` outside."""
    if lo <= value <= hi:
        return 1.0
    d = (lo - value) if value < lo else (value - hi)
    return max(0.0, 1.0 - d / max(soft, 1e-9))


# --- MusPy-aligned primitives ----------------------------------------------
def pitch_class_entropy(notes: List[Dict]) -> float:
    pcs = Counter(int(n["pitch"]) % 12 for n in notes)
    total = sum(pcs.values())
    if not total:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in pcs.values())


def scale_consistency(notes: List[Dict], key: str) -> float:
    root, scale = K.parse_key(key)
    ivals = set(K.SCALES.get(scale, K.SCALES["minor"]))
    # accept both natural-minor and dorian colors for minor keys (genre practice)
    if "minor" in scale:
        ivals |= set(K.SCALES["dorian"])
    if not notes:
        return 1.0
    ok = sum(1 for n in notes if (int(n["pitch"]) - root) % 12 in ivals)
    return ok / len(notes)


def groove_consistency(notes: List[Dict], bars: int) -> float:
    grids = _onset_grid(notes, bars)
    if len(grids) < 2:
        return 1.0
    sims = []
    for a, b in zip(grids, grids[1:]):
        same = sum(1 for x, y in zip(a, b) if x == y)
        sims.append(same / len(a))
    return sum(sims) / len(sims)


def empty_beat_rate(notes: List[Dict], bars: int) -> float:
    beats = [0] * max(1, bars * BEATS_PER_BAR)
    for n in notes:
        b = int(float(n.get("start_time", 0.0)))
        if b < len(beats):
            beats[b] = 1
    return 1.0 - sum(beats) / len(beats)


def polyphony(notes: List[Dict]) -> float:
    """Mean simultaneous notes among sounding moments (MusPy-style)."""
    if not notes:
        return 0.0
    events = []
    for n in notes:
        t0 = float(n.get("start_time", 0.0))
        events.append((t0, 1))
        events.append((t0 + float(n.get("duration", 0.25)), -1))
    events.sort()
    active, weighted, span, last_t = 0, 0.0, 0.0, events[0][0]
    for t, d in events:
        if active > 0:
            weighted += active * (t - last_t)
            span += (t - last_t)
        active += d
        last_t = t
    return weighted / span if span > 0 else 0.0


# --- per-role scoring --------------------------------------------------------
def _drum_metrics(notes, project, bars) -> List[Dict]:
    prof = K.genre_profile(project.genre)
    kicks = [n for n in notes if int(n["pitch"]) == 36]
    snares = [n for n in notes if int(n["pitch"]) in (37, 38, 39)]
    hats = [n for n in notes if int(n["pitch"]) in (42, 46)]
    out = []

    kd = sum(1 for k in kicks if (float(k["start_time"]) % BEATS_PER_BAR) < 0.3) / max(1, bars)
    out.append(_m("kick_downbeat", kd, min(1.0, kd), "kick on beat 1 of most bars",
                  "Anchor the groove: a kick on (or very near) beat 1 each bar."))

    strong = {1.0, 3.0} if prof.get("bpm", 120) < 160 else {1.0, 3.0}
    hits = sum(1 for s in snares if any(abs((float(s["start_time"]) % 4.0) - b) < 0.3 for b in strong))
    # loud snares only (ghosts don't count as the backbeat)
    loud = sum(1 for s in snares if int(s.get("velocity", 100)) >= 80 and
               any(abs((float(s["start_time"]) % 4.0) - b) < 0.3 for b in strong))
    bb = loud / max(1, bars * 2)
    out.append(_m("backbeat", bb, min(1.0, bb), "strong snare/clap on 2 and 4",
                  "The backbeat carries the style — snare beats 2 & 4, velocity 100+."))

    vels = [int(n.get("velocity", 100)) for n in notes]
    vstd = (sum((v - sum(vels) / len(vels)) ** 2 for v in vels) / len(vels)) ** 0.5 if vels else 0
    out.append(_m("velocity_variance", vstd, _band_score(vstd, 8, 30, 8),
                  "σ between 8 and 30", "Vary velocities — flat velocity reads as machine-gun."))

    gc = groove_consistency(notes, bars)
    out.append(_m("groove_consistency", gc, _band_score(gc, 0.80, 0.97, 0.15),
                  "0.80–0.97 (repetitive but not frozen)",
                  "Bars should feel related with small variations — not identical, not chaos."))

    per_bar = len(notes) / max(1, bars)
    lo, hi = (10, 26) if prof["_key"] in ("trap", "dnb") else (6, 20)
    out.append(_m("density", per_bar, _band_score(per_bar, lo, hi, 8),
                  f"{lo}-{hi} hits/bar for {project.genre}",
                  "Hit density should sit in the genre's pocket."))

    if hats:
        swing_target = prof.get("swing", 0.0)
        off = [h for h in hats if abs((float(h["start_time"]) % 1.0) - 0.5) < 0.25]
        if off and swing_target > 0:
            mean_delay = sum((float(h["start_time"]) % 1.0) - 0.5 for h in off) / len(off)
            sw = _band_score(mean_delay, swing_target * 0.3, swing_target * 0.9, swing_target)
            out.append(_m("swing", mean_delay, sw, f"offbeat hats delayed ~{swing_target:.2f} beats",
                          "Swung offbeats give the genre its lean."))
    return out


def _bass_metrics(notes, project, bars, drum_notes=None) -> List[Dict]:
    out = []
    sc = scale_consistency(notes, project.key)
    out.append(_m("scale_consistency", sc, sc, f"in {project.key}",
                  "Bass must live in the key — out-notes read as mistakes down low."))
    if notes:
        pitches = sorted(int(n["pitch"]) for n in notes)
        med = pitches[len(pitches) // 2]
        lo, hi = (24, 48) if project.genre == "trap" else (28, 52)
        out.append(_m("register", med, _band_score(med, lo, hi, 8),
                      f"median pitch {lo}-{hi} (E1-E3)", "Keep the bass in bass register."))
        poly = polyphony(notes)
        out.append(_m("monophony", poly, _band_score(poly, 0.0, 1.15, 0.6),
                      "≈1 note at a time", "Basslines are monophonic — overlaps mud the low end."))
        ebr = empty_beat_rate(notes, bars)
        out.append(_m("empty_beat_rate", ebr, _band_score(ebr, 0.1, 0.6, 0.25),
                      "0.1-0.6 (leave space)", "A bassline needs rests to breathe."))
        if drum_notes:
            kicks = [float(n["start_time"]) for n in drum_notes if int(n["pitch"]) == 36]
            if kicks:
                locked = sum(1 for n in notes
                             if any(abs(float(n["start_time"]) - kt) < 0.15 for kt in kicks))
                lock = locked / len(notes)
                # house/techno bass intentionally sits OFF the kick
                prof_key = K.genre_profile(project.genre)["_key"]
                if prof_key in ("house", "techno"):
                    out.append(_m("kick_relation", lock, _band_score(lock, 0.0, 0.35, 0.3),
                                  "offbeat vs the four-on-floor kick",
                                  "House/techno bass bounces BETWEEN kicks, not on them."))
                else:
                    out.append(_m("kick_relation", lock, _band_score(lock, 0.4, 1.0, 0.3),
                                  "≥40% of bass onsets locked to the kick",
                                  "Lock the bass to the kick for pocket."))
    return out


def _chords_metrics(notes, project, bars) -> List[Dict]:
    out = []
    sc = scale_consistency(notes, project.key)
    out.append(_m("scale_consistency", sc, sc, f"in {project.key}", "Stay diatonic (color tones OK)."))
    # cluster near-simultaneous notes into chords (tolerates rolled voicings)
    stacks: List[List[int]] = []
    last_t = None
    for n in sorted(notes, key=lambda x: float(x["start_time"])):
        t = float(n["start_time"])
        if last_t is not None and t - last_t <= 0.2:
            stacks[-1].append(int(n["pitch"]))
        else:
            stacks.append([int(n["pitch"])])
        last_t = t
    poly_stacks = [s for s in stacks if len(s) >= 3]
    vc = (sum(len(s) for s in poly_stacks) / len(poly_stacks)) if poly_stacks else 0.0
    out.append(_m("voice_count", vc, _band_score(vc, 3, 5, 2), "3-5 voices",
                  "Chords want 3-5 voices — fewer is thin, more gets muddy."))
    if poly_stacks:
        lows = [min(s) for s in poly_stacks]
        low_ok = sum(1 for p in lows if p >= 48) / len(lows)  # C2 floor for comp voicings
        out.append(_m("voicing_floor", low_ok, low_ok, "voicings above C2 (48)",
                      "Low chord voicings mask the bass — keep the comp above C2."))
        changes = len({tuple(sorted(p % 12 for p in s)) for s in poly_stacks})
        per4 = changes / max(1, bars / 4)
        out.append(_m("harmonic_motion", per4, _band_score(per4, 2, 6, 3),
                      "2-6 distinct chords per 4 bars", "Some movement, not a chord-per-16th."))
        sevenths = sum(1 for s in poly_stacks
                       if any((p - min(s)) % 12 in (10, 11) for p in s)) / len(poly_stacks)
        prof_key = K.genre_profile(project.genre)["_key"]
        if prof_key in ("boom_bap", "lofi", "rnb", "jazz"):
            out.append(_m("seventh_color", sevenths, sevenths, "7th/9th voicings",
                          "This style wants jazzy 7ths/9ths, not plain triads."))
    return out


def _melody_metrics(notes, project, bars, chord_notes=None) -> List[Dict]:
    out = []
    sc = scale_consistency(notes, project.key)
    out.append(_m("scale_consistency", sc, sc, f"in {project.key}", "Melody must sit in the key."))
    pce = pitch_class_entropy(notes)
    out.append(_m("pitch_class_entropy", pce, _band_score(pce, 1.5, 3.0, 0.8),
                  "1.5-3.0 bits", "Too low = monotone, too high = no tonal center."))
    if len(notes) >= 2:
        seq = sorted(notes, key=lambda x: float(x["start_time"]))
        steps = [abs(int(b["pitch"]) - int(a["pitch"])) for a, b in zip(seq, seq[1:])]
        stepwise = sum(1 for s in steps if 1 <= s <= 2) / len(steps)
        out.append(_m("stepwise_motion", stepwise, _band_score(stepwise, 0.35, 0.8, 0.25),
                      "35-80% steps", "Mostly stepwise with occasional leaps sings best."))
        rng = max(int(n["pitch"]) for n in notes) - min(int(n["pitch"]) for n in notes)
        out.append(_m("range", rng, _band_score(rng, 5, 19, 7), "within ~1.5 octaves",
                      "Keep the line in a singable range."))
        ebr = empty_beat_rate(notes, bars)
        out.append(_m("empty_beat_rate", ebr, _band_score(ebr, 0.15, 0.7, 0.2),
                      "0.15-0.7 (space!)", "Melodies need rests — don't fill every beat."))
        # motif repetition: 4-gram interval self-similarity
        if len(steps) >= 8:
            grams = [tuple(steps[i:i + 4]) for i in range(len(steps) - 3)]
            top = Counter(grams).most_common(1)[0][1] / len(grams)
            out.append(_m("motif_repetition", top, _band_score(top, 0.12, 0.6, 0.15),
                          "a motif that returns (12-60%)",
                          "Repeat and vary a motif — pure wander or pure loop both fail."))
    if chord_notes and notes:
        clashes = 0
        strong = [n for n in notes if (float(n["start_time"]) % 2.0) < 1e-3]
        for n in strong:
            t = float(n["start_time"])
            sounding = [c for c in chord_notes
                        if float(c["start_time"]) <= t < float(c["start_time"]) + float(c.get("duration", 1))]
            if sounding and all(abs((int(n["pitch"]) - int(c["pitch"])) % 12) in (1, 6, 11)
                                for c in sounding):
                clashes += 1
        rate = 1.0 - clashes / max(1, len(strong))
        out.append(_m("chord_agreement", rate, rate, "no semitone/tritone clash on strong beats",
                      "Strong-beat notes should agree with the chord under them."))
    return out


def score_role(role: str, notes: List[Dict], project, bars: int,
               context: Optional[Dict[str, List[Dict]]] = None) -> Dict[str, Any]:
    """Score one role. context may carry other roles' notes for cross-checks."""
    context = context or {}
    role_l = role.lower()
    if not notes:
        return {"score": 0.0, "metrics": [_m("presence", 0, 0, "notes exist",
                                             f"No notes submitted for {role}.")]}
    if role_l == "drums":
        metrics = _drum_metrics(notes, project, bars)
    elif role_l == "bass":
        metrics = _bass_metrics(notes, project, bars, drum_notes=context.get("drums"))
    elif role_l in ("chords", "keys", "pad"):
        metrics = _chords_metrics(notes, project, bars)
    else:  # melody / lead
        metrics = _melody_metrics(notes, project, bars, chord_notes=context.get("chords") or context.get("keys"))
    score = sum(m["score"] for m in metrics) / len(metrics)
    return {"score": round(score, 4), "metrics": metrics}


def score_global(parts: Dict[str, List[Dict]], project, bars: int) -> Dict[str, Any]:
    """Cross-part checks: register separation + plan adherence."""
    metrics = []
    bass = parts.get("bass", [])
    comp = parts.get("chords") or parts.get("keys") or []
    if bass and comp:
        top_bass = max(int(n["pitch"]) for n in bass)
        low_comp = min(int(n["pitch"]) for n in comp)
        sep = low_comp - top_bass
        metrics.append(_m("register_separation", sep, _band_score(sep, 3, 127, 6),
                          "comp voicings ≥3 semitones above the bass top",
                          "Give the bass its own register — overlap = mud."))
    if getattr(project, "plan", None):
        want_key = str(project.plan.get("key", "")).lower().replace(" ", "")
        have_key = project.key.lower().replace(" ", "")
        if want_key and want_key != have_key:
            metrics.append(_m("plan_adherence", 0.0, 0.0, f"plan said {project.plan.get('key')}",
                              "Notes drifted from the accepted PLAN's key."))
    if not metrics:
        metrics.append(_m("global", 1.0, 1.0, "-", "No cross-part issues detected."))
    score = sum(m["score"] for m in metrics) / len(metrics)
    return {"score": round(score, 4), "metrics": metrics}
