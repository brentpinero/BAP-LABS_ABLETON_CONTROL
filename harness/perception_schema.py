"""
perception_schema.py — the self-documenting DATA DICTIONARY for recorded SIM
trajectories, built PROGRAMMATICALLY from the sources of truth (bands.py,
perception_config.py, perception_frame.py) so it can never drift from the code.

`build_manifest()` produces the `manifest.json` that ships beside each
`frames.jsonl`. Unlike the old id/count-only manifest, it fully explains the data
to a 3rd-party ML researcher who has never seen this codebase:

  - band_table():        the exact Hz edges of every spectral band
  - vector_layout():     the 130-D `to_vector()` map (offset → meaning → encoding)
  - field_dictionary():  every JSONL key, its units, and its range
  - masking_semantics():   how clash `score` / `congestion` are computed (+ caveats)
  - role_taxonomy():     how tracks are mapped to roles (and that `tracks` is raw)
  - event_schema():      event types + the thresholds that fire them
  - focus_enums():       the focus-block vocabularies
  - provenance():        recording knobs + the honest caveats about this corpus

Nothing here hardcodes a band count or role list — all read from config/bands.
"""

from __future__ import annotations

from typing import Any

import inspect

import bands as _bands
import masking as _masking
import perception_frame as _pf
from perception_config import cfg

SCHEMA_VERSION = "sim.frame-trajectory.v2"   # v2 adds per-track `tracks` + full data dictionary


def band_table(scheme_id: str | None = None) -> list[dict]:
    """Every band's index + name + Hz edges, from bands.py (the single source)."""
    scheme_id = scheme_id or _bands.DEFAULT_SCHEME
    names = _bands.band_names(scheme_id)
    edges = _bands.band_edges(scheme_id)
    return [{"index": i, "name": nm, "lo_hz": lo, "hi_hz": hi}
            for i, (nm, (lo, hi)) in enumerate(zip(names, edges))]


def vector_layout(roles: list | None = None, scheme_id: str | None = None) -> dict:
    """The `Frame.to_vector()` layout: ordered segments with offset/length/encoding.

    Mirrors perception_frame.to_vector exactly; asserted to sum to Frame.vector_len.
    """
    roles = roles or cfg("roles")
    scheme_id = scheme_id or cfg("band_scheme")
    R, B = len(roles), _bands.n_bands(scheme_id)
    segs, off = [], 0

    def seg(length, name, encoding):
        nonlocal off
        segs.append({"offset": off, "length": length, "name": name, "encoding": encoding})
        off += length

    seg(6, "musical_time",
        "sin/cos(beat_phase), sin/cos(4-bar hyper_phase), bpm/300 clamped, playing(0|1)")
    seg(R * B, "role_band_energy",
        f"loudness-weighted band_abs per role, L1-normalized across the whole {R}x{B} "
        f"matrix; role-major: value for role i band j at offset {6}+i*{B}+j")
    seg(R, "role_loudness", "clamp((rms_db+60)/60) per role, roles order")
    seg(R, "role_width", "clamp(width) per role, width=side/(mid+side) in [0,1]")
    seg(R * (R - 1) // 2, "masking_upper_triangle",
        "clamp(log1p(pair_score)) over role pairs i<j, row-major upper triangle")
    seg(B, "master_congestion", "clamp(congestion_count/R) per band, bands order")
    seg(R, "focus_selected_role_onehot", "1.0 at the user-selected role, else 0.0")
    seg(B, "focus_focused_band_onehot", "1.0 at the user-focused band, else 0.0")
    seg(1, "focus_device_class", f"index(device_class)/{len(_pf.DEVICE_CLASSES)} scalar")
    seg(1, "focus_last_action", f"index(last_action)/{len(_pf.ACTIONS)} scalar")

    total = _pf.Frame.vector_len(roles, scheme_id)
    assert off == total, f"vector_layout sums to {off}, expected {total}"
    return {"total": total, "roles": list(roles), "scheme": scheme_id,
            "n_roles": R, "n_bands": B, "segments": segs}


def field_dictionary() -> dict:
    """Per-key description/units/range for every level of a recorded JSONL step."""
    return {
        "step_record": {
            "step": "monotonic index of this recorded frame (int, gaps if stride>1)",
            "t_wall": "audio-aligned instant, epoch seconds (float); shifted by audio_latency_s",
            "bar": "integer bar index at this frame",
            "beat": "float beats into the bar",
            "playing": "transport playing (bool)",
            "frame": "the fixed-shape role-aggregate Frame (see `frame`)",
            "events": "discrete events that fired on this frame (see `event`)",
            "tracks": "RAW per-track state, keyed by Live track id (see `track`) — "
                      "present only when recorded with a bridge; the un-abstracted truth",
        },
        "frame": {
            "t_wall": "epoch seconds (audio instant)", "bpm": "beats/minute",
            "bar": "int bar", "beat": "float beat", "beats_per_bar": "time-sig numerator",
            "playing": "bool", "scheme": "band-scheme id (see band_table)",
            "roles": "fixed role order (master always index 0)",
            "role_state": "per-role aggregate (see `role_state`)",
            "masking": "clash pairs + master congestion (see masking_semantics)",
            "focus": "user focus block (see focus_enums)",
            "unmapped": "track names that fell through to the 'other' role",
            "text": "terse human/LLM-readable render of this frame",
        },
        "role_state": {
            "bands": "per-band energy FRACTION, sums to ~1 across bands (unitless)",
            "rms_db": "role summed level, dB, floor -120",
            "width": "stereo width side/(mid+side) in [0,1]",
            "peak_db": "loudest member peak, dB, floor -120",
            "correlation": "loudness-weighted mean L/R correlation of members, [-1,1]",
        },
        "track": {
            "id": "Live track id (string)", "name": "track name",
            "kind": "audio | midi | group | master | return",
            "group_id": "parent group's track id, or '-1' if top-level",
            "band_scheme": "band-scheme id for this track's spectrum",
            "n_bands": "length of `bands`",
            "bands": "per-band energy FRACTION, sums to ~1 (unitless)",
            "rms_l": "left RMS, dB", "rms_r": "right RMS, dB",
            "peak_l": "left peak, dB", "peak_r": "right peak, dB",
            "mid_energy": "mid-channel linear energy (unitless, for width)",
            "side_energy": "side-channel linear energy (unitless, for width)",
            "correlation": "L/R correlation, [-1,1]",
            "updated_at": "epoch seconds this track last reported",
        },
        "event": {
            "type": "mask_on | mask_off | clip | level_jump",
            "t_wall": "epoch seconds", "bar": "int bar", "beat": "float beat",
            "a": "primary role (clash side A / clipping or jumping role)",
            "b": "secondary role (clash side B), else null",
            "band": "band name for mask events, else null",
            "value": "score (mask), peak dB (clip), or delta dB (level_jump)",
            "dir": "'up'|'down' for level_jump, else null",
            "seq": "monotonic event sequence number",
        },
    }


def masking_semantics() -> dict:
    """How the masking `score` and `congestion` numbers are computed — and the caveat."""
    # read the congestion thresholds straight from compute_masking's signature so this
    # dictionary can't drift from the code; fall back to the known defaults if renamed.
    try:
        params = inspect.signature(_masking.compute_masking).parameters
        cfrac = float(params["congestion_frac"].default)
        adb = float(params["audible_db"].default)
    except Exception:
        cfrac, adb = 0.10, -50.0
    return {
        "band_abs": "per band = band_fraction * 10^(rms_db/20) (loudness-weighted energy)",
        "pair_score": "sum over bands of min(band_abs_A, band_abs_B) — both loud in a band = clash",
        "pair_score_scale": "UNBOUNDED energy sum, NOT [0,1]; ~0.17 max on real material. "
                            "The 130-D vector applies log1p+clamp; downstream absolute clash "
                            "thresholds are unreliable — prefer a data-relative split.",
        "master_congestion": f"per band, count of groups whose band_fraction >= {cfrac} AND "
                             f"whose rms_db > {adb} dB (audible). Higher = more crowded band.",
        "top_band": "the band contributing the most to a pair's score",
    }


def role_taxonomy(override: dict | None = None) -> dict:
    """The role vocabulary + how tracks map to roles. `role_state` is an AGGREGATE;
    the per-frame `tracks` map is the raw per-track truth for analysis."""
    return {
        "roles": list(cfg("roles", override)),
        "return_role": cfg("return_role", override),
        "role_map": [{"role": r, "name_substrings": list(needles)}
                     for r, needles in cfg("role_map", override)],
        "mapping_rule": "master/return by kind; else walk up to the top-level group and "
                        "match its name against role_map (first match wins, sub before bass); "
                        "if the name is uninformative, fall back to the track's SPECTRAL "
                        "signature (content_roles.classify). 'other' is the catch-all.",
        "note": "role_state collapses every track of a role into ONE aggregate submix — it is "
                "for the model's track labeling, not fine analysis. Use `tracks` for raw detail.",
    }


def event_schema(override: dict | None = None) -> dict:
    """Event types + the (hysteretic) thresholds that fire them, from config."""
    return {
        "types": ["mask_on", "mask_off", "clip", "level_jump"],
        "thresholds": {
            "mask_on": cfg("event.mask_on", override),
            "mask_off": cfg("event.mask_off", override),
            "mask_min_frames": int(cfg("event.mask_min_frames", override)),
            "clip_db": cfg("event.clip_db", override),
            "clip_margin_db": cfg("event.clip_margin_db", override),
            "level_jump_db": cfg("event.level_jump_db", override),
            "level_jump_win_s": cfg("event.level_jump_win_s", override),
        },
        "note": "mask on/off use dual-threshold + dwell (mask_min_frames); clip re-arms only "
                "after dropping clip_margin_db below clip_db; level_jump needs +/- level_jump_db "
                "over level_jump_win_s with a refractory window.",
    }


def focus_enums() -> dict:
    """The focus-block vocabularies (empty when no user interaction is recorded)."""
    return {
        "fields": ["selected_role", "focused_band", "device_class", "last_action"],
        "device_classes": list(_pf.DEVICE_CLASSES),
        "actions": list(_pf.ACTIONS),
        "note": "focus is null/'none' unless the focus lane is live and the user is interacting.",
    }


def provenance(override: dict | None = None) -> dict:
    """Recording knobs + the honest caveats about interpreting this corpus."""
    return {
        "frame_rate_hz": cfg("frame_rate_hz", override),
        "stride": max(1, int(cfg("trajectory_stride", override))),
        "only_when_playing": bool(cfg("trajectory_only_when_playing", override)),
        "audio_latency_s": cfg("audio_latency_s", override),
        "caveats": [
            "only_when_playing=True skips silent/stopped frames (event-bearing frames kept).",
            "Frames at 25 Hz are heavily autocorrelated — split by SESSION, not randomly, to "
            "avoid leakage when probing/training.",
            "t_wall is shifted back by audio_latency_s so the frame aligns to the audio instant.",
            "A single test song (~120 BPM) makes cross-session generalization TEMPORAL, not "
            "cross-song; add diverse material before claiming musical generality.",
        ],
    }


METADATA_SCHEMA_VERSION = "sim.param-stream.v1"


def build_metadata_manifest(session_id: str, started_at: float,
                            override: dict | None = None) -> dict:
    """Data dictionary for the continuous parameter-automation stream (params.jsonl),
    written beside frames.jsonl in the same <session> folder."""
    return {
        "schema_version": METADATA_SCHEMA_VERSION,
        "session_id": session_id,
        "started_at": started_at,
        "sample_hz": cfg("metadata_sample_hz", override),
        "change_eps": cfg("metadata_change_eps", override),
        "only_when_playing": bool(cfg("metadata_only_when_playing", override)),
        "encoding": "delta — each record stores only params that changed since the previous "
                    "record; a full keyframe (keyframe=true) is written on tick 0. Hold the "
                    "last value between records.",
        "join": "records join frames.jsonl by t_wall/bar/beat (stamped from the SAME "
                "transport_now(now - audio_latency_s) the frames use).",
        "line_schema": "{tick, t_wall, bar, beat, playing, keyframe, "
                       "changes:[[track_index, dev_path, param_index, value, automation_state], ...]}",
        "dev_path": "device position in the track chain; nested rack devices as "
                    "'<devIdx>/<chainIdx>/<devIdx>...'. Join names/bounds via song_metadata.json.",
        "automation_state": {"0": "none", "1": "playing (automation active)", "2": "overridden"},
        "companion": "static chain + param names/bounds/classification live in song_metadata.py output.",
    }


def build_manifest(session_id: str, started_at: float, override: dict | None = None) -> dict:
    """The full data-dictionary manifest written beside frames.jsonl."""
    roles = cfg("roles", override)
    scheme = cfg("band_scheme", override)
    return {
        "schema_version": SCHEMA_VERSION,
        "session_id": session_id,
        "started_at": started_at,
        "frame_rate_hz": cfg("frame_rate_hz", override),
        "band_scheme": scheme,
        "roles": list(roles),
        "vector_len": _pf.Frame.vector_len(roles, scheme),
        "stride": max(1, int(cfg("trajectory_stride", override))),
        "only_when_playing": bool(cfg("trajectory_only_when_playing", override)),
        "audio_latency_s": cfg("audio_latency_s", override),
        "line_schema": "one JSON object per line: "
                       "{step, t_wall, bar, beat, playing, frame, events, tracks}",
        "bands": band_table(scheme),
        "vector_layout": vector_layout(roles, scheme),
        "fields": field_dictionary(),
        "masking_semantics": masking_semantics(),
        "role_taxonomy": role_taxonomy(override),
        "event_schema": event_schema(override),
        "focus_enums": focus_enums(),
        "provenance": provenance(override),
    }
