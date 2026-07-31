"""Pure planning and validation primitives for the causal plugin-chain dataset.

This module deliberately does not control Ableton.  It creates immutable manifests and
intervention plans that the isolated render node can execute later.  Keeping planning
pure makes source-set preservation, review, and unit testing possible without opening Live.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "sim.causal-plugin.v1"
TASKS = {"causal_effect", "mix_diagnosis", "preference_comparison", "action_selection"}
HIERARCHY_LEVELS = ("track", "group_or_return", "master")

DEVICE_RULES = {
    "eq_filter": ("eq", "filter", "pro-q"),
    "dynamics": ("compress", "limiter", "gate", "pro-l", "pro-mb", "ott", "ducker", "sidechain"),
    "saturation_distortion": ("saturat", "distort", "clip", "overdrive", "roar", "rift", "rectif"),
    "stereo_modulation": ("utility", "autopan", "auto pan", "chorus", "phaser", "flanger", "msed", "lfotool"),
    "time_spatial": ("reverb", "echo", "delay", "valhalla"),
    "meter": ("meter", "span", "analyz", "analys", "spectrum", "oscilloscope"),
    "mix_glue": ("god particle", "glue"),
}
INSTRUMENT_HINTS = ("serum", "simpler", "operator", "wavetable", "instrument", "sampler", "drum rack")

# Per-device-NAME overrides (case-insensitive substring), checked BEFORE the generic
# rules. Value is a LIST of families — a device can belong to several (e.g. an exciter
# that also widens). Teach the map new plugins here as projects introduce them.
DEVICE_NAME_OVERRIDES = {
    "n-power": ["saturation_distortion", "stereo_modulation"],
    "god particle": ["mix_glue"],
    "easy wash out": ["filter_wash"],
    "rectifier": ["saturation_distortion"],
    "lfotool": ["stereo_modulation"],
    "microtuner": ["midi_effect"],
    "bap labs mix analysis": ["meter"],
    "swiss army meter": ["meter"],
    "sidechain_rack_ducker": ["dynamics"],
    "gmaudio ducker": ["dynamics"],
}

# Device CLASS-name → family fallback (Live device class, not display name). Catches
# instruments whose sample-based display name doesn't say "simpler"/"sampler" etc.
DEVICE_CLASS_RULES = {
    "MxDeviceMidiEffect": "midi_effect",
    "InstrumentGroupDevice": "instrument_excluded",
    "DrumGroupDevice": "instrument_excluded",
    "MidiEffectGroupDevice": "midi_effect",
    "AudioEffectGroupDevice": "rack",       # container — its contents classify individually
    "OriginalSimpler": "instrument_excluded",
    "Simpler": "instrument_excluded",
    "MultiSampler": "instrument_excluded",   # Sampler
    "InstrumentImpulse": "instrument_excluded",
    "InstrumentVector": "instrument_excluded",   # Wavetable
    "UltraAnalog": "instrument_excluded",        # Analog
    "Operator": "instrument_excluded",
    "InstrumentMeld": "instrument_excluded",
    "Collision": "instrument_excluded",
    "Tension": "instrument_excluded",
    "Electric": "instrument_excluded",
}

# Families whose devices DON'T change the audio (analysis/MIDI) — the ablation pipeline
# should skip them (wasted rungs) and must never bypass a meter that feeds perception.
NON_AUDIO_FAMILIES = frozenset({"meter", "midi_effect"})

PARAMETER_HINTS = {
    # Names are matched case-insensitively against Live's display names.  Include
    # common stock and VST variants; bounds/automation still come from the live device.
    "eq_filter": ("frequency", "freq", "gain", "q", "cutoff", "resonance", "res", "slope"),
    "dynamics": ("threshold", "thresh", "ratio", "attack", "release", "makeup",
                 "knee", "range", "lookahead", "input", "output", "ceiling",
                 "oversampling", "dry/wet", "wet", "mix"),
    "saturation_distortion": ("drive", "tone", "color", "bias", "shape", "input",
                              "output", "ceiling", "oversampling", "dry/wet", "wet", "mix"),
    "stereo_modulation": ("width", "balance", "pan", "rate", "amount", "depth",
                          "phase", "spread", "dry/wet", "wet", "mix"),
    "time_spatial": ("decay", "time", "predelay", "pre-delay", "feedback", "delay",
                     "density", "diffusion", "size", "damping", "low cut", "high cut",
                     "width", "dry/wet", "wet", "mix"),
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify_families(name: str, class_name: str = "", tag: str = "") -> list[str]:
    """All effect families a device belongs to (a device can be several, e.g. an exciter
    that also widens the stereo image). Precedence: name overrides → instrument hints →
    generic name rules → device-class fallback → ['unknown_effect'].

    `class_name` is Live's device class (e.g. 'PluginDevice', 'AudioEffectGroupDevice',
    'MxDeviceMidiEffect') — used for the meter/MIDI/rack fallbacks that a display name
    alone can't reveal."""
    text = f"{name} {tag}".lower()
    for needle, fams in DEVICE_NAME_OVERRIDES.items():
        if needle in text:
            return list(fams)
    if any(hint in text for hint in INSTRUMENT_HINTS):
        return ["instrument_excluded"]
    hits = [family for family, hints in DEVICE_RULES.items()
            if any(hint in text for hint in hints)]
    if hits:
        return hits
    if class_name in DEVICE_CLASS_RULES:
        return [DEVICE_CLASS_RULES[class_name]]
    return ["unknown_effect"]


def classify_device(name: str, tag: str = "") -> str:
    """Primary (first) family for a device — backward-compatible single-label classifier.
    New code wanting the full multi-family list should call classify_families()."""
    return classify_families(name, tag=tag)[0]


def build_routing_graph(tracks: Iterable[dict]) -> dict:
    """Return stable node metadata and parent edges from the static ALS proto-IR."""
    rows = list(tracks)
    ids = {str(t.get("id")) for t in rows}
    nodes, edges = [], []
    for track in rows:
        tid = str(track.get("id"))
        group_id = track.get("group_id")
        parent = str(group_id) if group_id is not None and str(group_id) in ids else "master"
        nodes.append({"id": tid, "name": track.get("name"), "type": track.get("type"),
                      "output_routing": track.get("output_routing")})
        edges.append({"source": tid, "target": parent, "kind": "audio_output"})
        for return_index, amount in enumerate((track.get("mixer") or {}).get("sends") or []):
            if isinstance(amount, (int, float)) and amount > 0:
                edges.append({"source": tid, "target": f"return:{return_index}",
                              "kind": "send", "amount": amount})
    nodes.append({"id": "master", "name": "Master", "type": "master", "output_routing": None})
    return {"nodes": nodes, "edges": edges}


def build_project_manifest(ir: dict, source_path: str | Path, scratch_path: str | Path | None = None,
                           sections: list[dict] | None = None, sample_rate: int = 44100,
                           render_settings: dict | None = None) -> dict:
    """Create the immutable reconciliation manifest; missing scratch state fails closed."""
    source = Path(source_path).expanduser().resolve()
    scratch = Path(scratch_path).expanduser().resolve() if scratch_path else None
    tracks = ir.get("tracks") or []
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "source": {"path": str(source), "sha256": sha256_file(source)},
        "scratch": {"path": str(scratch), "sha256": sha256_file(scratch)} if scratch else None,
        "live_version": ir.get("live_version"),
        "tempo": ir.get("tempo"),
        "sample_rate": sample_rate,
        "sections": sections or [],
        "render_settings": render_settings or {},
        "routing_graph": build_routing_graph(tracks),
        "tracks": tracks,
        "master": ir.get("master"),
        "coverage": ir.get("coverage") or {},
        "reconciliation": {"static_complete": False, "live_complete": False,
                           "plugin_availability_complete": False, "errors": []},
    }
    manifest["manifest_id"] = hashlib.sha256(canonical_json(manifest).encode()).hexdigest()[:20]
    return manifest


def mark_reconciled(manifest: dict, *, live_complete: bool, plugin_availability_complete: bool,
                    errors: list[str] | None = None) -> dict:
    out = json.loads(json.dumps(manifest))
    rec = out["reconciliation"]
    rec.update({"static_complete": True, "live_complete": bool(live_complete),
                "plugin_availability_complete": bool(plugin_availability_complete),
                "errors": list(errors or [])})
    rec["ready"] = all((rec["static_complete"], rec["live_complete"],
                        rec["plugin_availability_complete"])) and not rec["errors"]
    return out


def parameter_sweep(center: float, minimum: float, maximum: float) -> list[float]:
    """Four deterministic points: two close neighbors, center, and one strong value."""
    if not all(math.isfinite(float(x)) for x in (center, minimum, maximum)) or minimum >= maximum:
        raise ValueError("parameter bounds must be finite and minimum < maximum")
    if not minimum <= center <= maximum:
        raise ValueError("parameter center must be within bounds")
    span = maximum - minimum
    values = (center - 0.05 * span, center, center + 0.05 * span, center + 0.20 * span)
    return sorted({round(min(max(v, minimum), maximum), 8) for v in values})


def eligible_parameters(device_class: str, parameters: Iterable[dict]) -> list[dict]:
    hints = PARAMETER_HINTS.get(device_class, ())
    return [p for p in parameters if any(h in str(p.get("name", "")).lower() for h in hints)
            and not p.get("readonly", False) and not p.get("automated", False)]


def parameter_coverage(device_class: str, parameters: Iterable[dict]) -> dict:
    """Account for every live parameter as selected or explicitly excluded.

    This report is stored with the manifest so a renamed/new plugin parameter cannot
    silently disappear from intervention planning.
    """
    hints = PARAMETER_HINTS.get(device_class, ())
    selected, excluded = [], []
    for parameter in parameters:
        name = str(parameter.get("name", ""))
        if parameter.get("readonly", False):
            excluded.append({"name": name, "reason": "readonly"})
        elif parameter.get("automated", False):
            excluded.append({"name": name, "reason": "automated_requires_explicit_override"})
        elif not any(h in name.lower() for h in hints):
            excluded.append({"name": name, "reason": "not_relevant_to_device_family"})
        elif any(parameter.get(k) is None for k in ("value", "min", "max")):
            excluded.append({"name": name, "reason": "missing_value_or_bounds"})
        else:
            selected.append(parameter)
    return {"device_class": device_class, "total": len(selected) + len(excluded),
            "selected": selected, "excluded": excluded, "accounted": True}


def plan_interventions(device: dict, *, seed: int, include_prefixes: bool = True) -> list[dict]:
    """Plan A/A, baseline, bypass, prefix, and safe OFAT sweeps for one effect."""
    device_class = classify_device(device.get("name", ""), device.get("tag", ""))
    if device_class == "instrument_excluded":
        return []
    common = {"seed": int(seed), "device_index": int(device["index"]),
              "device_name": device.get("name"), "device_class": device_class}
    plans = [dict(common, kind="aa_repeat"), dict(common, kind="baseline"),
             dict(common, kind="bypass", enabled=False)]
    if include_prefixes and int(device["index"]) > 0:
        plans.append(dict(common, kind="chain_prefix", enabled_through=int(device["index"]) - 1))
    coverage = parameter_coverage(device_class, device.get("parameters") or [])
    for parameter in coverage["selected"]:
        for value in parameter_sweep(float(parameter["value"]), float(parameter["min"]),
                                     float(parameter["max"])):
            if value != float(parameter["value"]):
                plans.append(dict(common, kind="parameter_sweep", parameter=parameter["name"], value=value,
                                  automation_policy="reject_if_automated"))
    for plan in plans:
        plan["parameter_coverage"] = coverage
    return plans


def metric_deltas(baseline: dict, candidate: dict) -> dict:
    """Subtract nested numeric metric maps while preserving their hierarchy."""
    out = {}
    for key in sorted(set(baseline) & set(candidate)):
        a, b = baseline[key], candidate[key]
        if isinstance(a, dict) and isinstance(b, dict):
            nested = metric_deltas(a, b)
            if nested:
                out[key] = nested
        elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
            out[key] = round(float(b) - float(a), 8)
    return out


def exceeds_aa_variance(delta: dict, aa_delta: dict, multiplier: float = 2.0,
                        floor: float = 1e-8) -> bool:
    """Retain an example when any numeric delta clears repeated-render noise."""
    def leaves(value: Any) -> list[float]:
        if isinstance(value, dict):
            return [x for v in value.values() for x in leaves(v)]
        return [abs(float(value))] if isinstance(value, (int, float)) else []
    signal, noise = leaves(delta), leaves(aa_delta)
    return bool(signal) and max(signal) > max([floor] + noise) * multiplier


def build_example(*, manifest_id: str, task: str, section: dict, target: dict,
                  intervention: dict, observations: dict, baseline_observations: dict,
                  aa_delta: dict, provenance: dict, preference: str = "uncertain") -> dict:
    if task not in TASKS:
        raise ValueError(f"unknown task: {task}")
    if set(observations) != set(HIERARCHY_LEVELS):
        raise ValueError(f"observations must contain exactly {HIERARCHY_LEVELS}")
    if preference not in {"baseline", "candidate", "tie", "uncertain"}:
        raise ValueError("invalid preference label")
    deltas = {level: metric_deltas(baseline_observations[level], observations[level])
              for level in HIERARCHY_LEVELS}
    retained = exceeds_aa_variance(deltas, aa_delta)
    return {
        "schema_version": SCHEMA_VERSION, "manifest_id": manifest_id, "task": task,
        "section": section, "target": target, "intervention": intervention,
        "observations": observations, "deltas": deltas,
        "labels": {"causal_effect": deltas, "audibility": {k: bool(v) for k, v in deltas.items()},
                   "engineering_constraints": {}, "authored_anchor": intervention.get("kind") == "baseline",
                   "preference": preference, "confidence": "pending"},
        "quality": {"retained": retained, "aa_delta": aa_delta}, "provenance": provenance,
    }


def make_review_queue(examples: Iterable[dict], limit: int = 32, seed: int = 0) -> list[dict]:
    """Randomize retained, unresolved comparisons with durable presentation order."""
    rows = [e for e in examples if e.get("quality", {}).get("retained")
            and e.get("labels", {}).get("preference") == "uncertain"]
    rng = random.Random(seed)
    rng.shuffle(rows)
    return [{"example_id": hashlib.sha256(canonical_json(e).encode()).hexdigest()[:20],
             "presentation_order": rng.choice(("baseline_first", "candidate_first")),
             "level_match": True, "reviewer": None, "decision": None}
            for e in rows[:limit]]
