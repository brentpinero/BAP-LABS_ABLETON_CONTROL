"""
config.py — namespaced, per-session-overridable defaults for the sandbox.

The hardcoded audit (docs + plan) found ~100 fixed constants; this layer
promotes the highest-impact ones to session overrides. Everything here can be
set per session via SandboxConfig.overrides (persisted) — reachable from the
sandbox_config MCP tool and the review UI. Constants NOT promoted are marked
`# CONFIG-CANDIDATE` at their definition sites.

Usage:
    from config import cfg
    cfg(session, "loop.role_floor")        # override if set, else default
"""
from __future__ import annotations

from typing import Any, Dict

DEFAULTS: Dict[str, Any] = {
    # --- engine / verdicts ---
    "loop.tier_weights": {"midi": 0.40, "audio": 0.35, "clap": 0.25},
    "loop.role_floor": 0.60,           # every role must clear this to pass
    "loop.plateau_eps": 0.02,
    "loop.plateau_after": 3,
    "loop.clap_fallback_weight": 0.5,  # CLAP de-weight under proxy synths
    "loop.chord_track_limit": 64,      # notes of chord context in dependent briefs

    # --- critique ---
    "critic.failing_threshold": 0.75,
    "critic.priorities_cap": 3,

    # --- audio pipeline ---
    "audio.sr": 44100,
    "audio.tail_seconds": 1.0,
    "audio.normalize_peak": 0.98,
    "audio.true_peak_max": 0.985,
    "audio.spectral_min_stems": 3,
    "audio.lufs_free_db": 3.0,         # LUFS deviation tolerated before scoring off
    "audio.lufs_span_db": 9.0,
    "audio.crest_band": [6.0, 20.0],

    # --- groove ---
    "groove.swing_tolerance": 0.06,
    "groove.jitter_clip": [-0.02, 0.03],
    "groove.laid_back": {"boom_bap": 0.015, "rnb": 0.020, "lofi": 0.025},

    # --- grid (4/4 remains structural in several modules; documented) ---
    "grid.beats_per_bar": 4,

    # --- CLAP ---
    "clap.model": "laion/clap-htsat-unfused",
    "clap.schedule": "first_and_final",   # first_and_final | every | never

    # --- fidelity / calibration ---
    "fidelity.live_project_dir": "",      # path to the open Live project (calibration)
    "fidelity.freeze_timeout_s": 120,

    # --- render backend (fast tier vs isolated Ableton render node) ---
    # backend: pedalboard (fast, headless — composition only) | dawdreamer (fast,
    # offline+automation-aware) | ableton (TRUTH — an ISOLATED render-node Ableton
    # the user never touches, driven over the socket + node automator daemon).
    "render.backend": "pedalboard",
    "render.node_host": "127.0.0.1",      # render-node address (VM/2nd machine/cloud); localhost = same-Mac stand-in
    "render.node_port": 9877,             # node Remote Script control socket
    "render.node_agent_port": 9878,       # node automator daemon (freeze/export GUI automation runs ON the node)
    "render.node_project_dir": "",        # SAVED Live project folder on the node (freeze wavs land here)
    "render.warm_host": True,             # fast tier keeps the plugin loaded across iterations (kills the per-render load tax)
    # node truth-tier render mode: "resample" = LOM-native real-time resampling
    # (robust, no GUI/Accessibility, all stems in one real-time pass — the verified
    # path, since Live's API exposes NO export/render/freeze); "freeze" = per-role
    # GUI Freeze (faster-than-realtime but serial + Accessibility-dependent).
    "render.node_render_mode": "resample",
    "render.node_record_tail_s": 0.5,     # extra seconds recorded after the musical length
}


# String-enum keys: values outside these sets pass type-checking but silently take
# a wrong branch (e.g. a node_render_mode typo → the fragile freeze path), so they
# get an explicit membership check in validate_overrides.
_ENUMS: Dict[str, set] = {
    "render.backend": {"pedalboard", "dawdreamer", "ableton"},
    "render.node_render_mode": {"resample", "freeze"},
    "clap.schedule": {"first_and_final", "every", "never"},
}


def cfg(session, key: str) -> Any:
    """Session override if present, else the default. Raises on unknown keys."""
    if key not in DEFAULTS:
        raise KeyError(f"unknown config key: {key} (known: {sorted(DEFAULTS)})")
    overrides = getattr(session.config, "overrides", None) or {}
    return overrides.get(key, DEFAULTS[key])


def validate_overrides(overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Reject unknown keys and gross type mismatches; return the cleaned dict."""
    clean = {}
    for k, v in (overrides or {}).items():
        if k not in DEFAULTS:
            raise KeyError(f"unknown config key: {k}")
        d = DEFAULTS[k]
        if d is not None and v is not None and not isinstance(v, type(d)) \
                and not (isinstance(d, float) and isinstance(v, (int, float))):
            raise TypeError(f"{k}: expected {type(d).__name__}, got {type(v).__name__}")
        if k in _ENUMS and v not in _ENUMS[k]:
            raise ValueError(f"{k}: {v!r} not one of {sorted(_ENUMS[k])}")
        clean[k] = v
    return clean
