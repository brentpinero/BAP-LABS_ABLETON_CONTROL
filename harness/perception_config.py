"""
perception_config.py — config for the streaming perception layer.

One flat DEFAULTS dict + cfg() accessor (mirrors sandbox/config.py's style), with
env-var overrides so the `ears` daemon can be tuned without code edits
(PERCEPTION_FRAME_RATE_HZ, PERCEPTION_PUSH_PORT, ...). Resolution/band scheme is
data-driven via bands.py — nothing here hardcodes a band count.
"""

from __future__ import annotations

import os
from typing import Any

import bands as _bands

DEFAULTS: dict[str, Any] = {
    # frame clock — configurable; the duplex backbone (MiniCPM-o) decimates to its
    # own token rate later, so never bake a rate into consumers.
    "frame_rate_hz": 25,
    "band_scheme": _bands.DEFAULT_SCHEME,

    # fixed role taxonomy (constant frame dimensionality). master is always index 0;
    # "other" is the catch-all so no node is ever dropped and shape stays constant.
    "roles": ["master", "drums", "bass", "sub", "vox", "synth", "fx", "other"],
    "return_role": "fx",                       # return tracks default here
    # priority-ordered name→role substrings (first match wins; sub before bass).
    "role_map": [
        ("sub",   ["sub", "808", "sub bass"]),
        ("drums", ["drum", "kick", "snare", "hat", "clap", "perc", "tom", "cymbal", "ride", "fill", "beat"]),
        ("bass",  ["bass", "reese", "wobble"]),
        ("vox",   ["vox", "vocal", "voc ", "adlib", "acapella", "lead vox", "harmon"]),
        ("synth", ["synth", "pad", "lead", "pluck", "arp", "key", "piano", "chord", "melod", "stab", "saw"]),
        ("fx",    ["fx", "reverb", "delay", "riser", "impact", "noise", "sweep", "texture", "ambience", "foley"]),
    ],

    # transport (push)
    "push_host": "127.0.0.1",
    "push_port": 9884,                         # avoids 9880 (OSC recv) + 9878 collision
    "buffer_frames": 512,
    "snapshot_path": "sandbox_sessions/perception_stream.json",
    "snapshot_interval_s": 0.25,
    "stale_s": 3.0,
    "node_max_age_s": 5.0,                     # a track must have updated within this to count

    # text-LLM bridge
    "inject_live_block": True,
    "text_topk": 3,
    "max_events": 8,

    # event thresholds (hysteretic)
    "event.mask_on": 0.15,
    "event.mask_off": 0.08,
    "event.mask_min_frames": 3,
    "event.clip_db": -0.3,
    "event.clip_margin_db": 3.0,
    "event.level_jump_db": 6.0,
    "event.level_jump_win_s": 0.5,

    "focus_listeners": True,

    # adaptive provisioning (Phase 3): which nodes get instrumented + fed to masking.
    "aggregator_channels": 32,                 # input pairs per aggregator device (64ch)
    # coverage is capacity-driven, NOT name-gated: the aggregator is cheap (~1-2% CPU
    # per device), so instrument every node up to this hard cap, spread across as many
    # aggregator devices as needed (ceil(max_instrument / (aggregator_channels-1))).
    # select_nodes only has to RANK when a project exceeds this; below it, everything
    # is covered regardless of naming/grouping.
    "max_instrument": 120,                     # hard cap on total instrumented nodes
    "select_capacity": 120,                    # ranking budget (== max_instrument)
    "select_energy_db": -40.0,                 # a leaf track above this counts as "loud"
    "agg_osc_port": 9886,                       # aggregator per-channel spectrum OSC
    "agg_gate_db": -70.0,                        # below this a channel is silence; its
                                                # normalized spectrum is noise -> zero it

    # transport source: the daemon polls the Remote Script (LOM) for authoritative
    # is_playing/tempo/song-position and drives the bar cache, instead of trusting the
    # per-device plugsync~/live.observer (which fails to bind on fresh M4L loads).
    "transport_poll_hz": 10.0,                  # LOM transport poll rate (bar-accurate)
}


def _coerce(default: Any, raw: str) -> Any:
    if isinstance(default, bool):
        return raw.strip().lower() in ("1", "true", "yes", "on")
    if isinstance(default, int):
        return int(raw)
    if isinstance(default, float):
        return float(raw)
    return raw


def cfg(key: str, override: dict | None = None) -> Any:
    """Resolve a config value: explicit override > env var > DEFAULTS."""
    if override and key in override:
        return override[key]
    env = os.environ.get("PERCEPTION_" + key.upper().replace(".", "_"))
    if env is not None and key in DEFAULTS:
        return _coerce(DEFAULTS[key], env)
    return DEFAULTS[key]
