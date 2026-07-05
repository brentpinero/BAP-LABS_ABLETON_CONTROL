"""
renderer_live.py — truth-tier renderer: real Ableton on an ISOLATED render node.

Drop-in for `renderer.render_iteration` (same `{"audio": {role→wav, "master"→
wav}, "pool": [...]}` contract) so the sandbox loop is unchanged. Instead of a
headless VST host, it drives a SEPARATE Ableton instance — the render node (VM /
2nd machine / cloud) the user never touches — so stock devices, third-party
plugins, factory content and offline render quality are all EXACTLY Ableton.

Split of responsibilities (see render_node_agent.py):
  • LOM ops (create track, load device, params, notes, select) → LiveClient over
    the node's Remote Script socket — already network-transparent.
  • GUI freeze + wav retrieval → RenderNodeClient → the on-node agent, because
    osascript runs only where the node's GUI lives and the wav is node-local.

v1 renders each role via a temp tagged track (create → load → notes → freeze →
capture → delete), with a per-role content-hash cache so unchanged roles are
copied, not re-frozen. Persistent role tracks are a follow-up optimization.

GUI-FOCUS CAVEAT: Ableton's Freeze targets the GUI-FOCUSED track, which is not
always LOM `selected_track` (learned the hard way). On the isolated node this
must be verified/calibrated as a Phase-1 acceptance step; `select_track` is used
plus an optional click-select hook. Nothing here ever touches the user's set.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from collections import namedtuple
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parent.parent
for _p in (str(_ROOT / "harness"), str(_ROOT / "harness" / "AbletonMCP_Extended"),
           str(_ROOT / "sandbox")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from config import cfg  # noqa: E402
from renderer import sum_stems_to_master  # noqa: E402 — shared master bus


def _device_query_for(instrument_spec: str) -> Optional[str]:
    """Map a sandbox instrument_spec to a browser device name the node can load.
    Returns None for fallback (proxy) roles — those stay on the fast tier."""
    if not instrument_spec or instrument_spec.startswith("fallback:"):
        return None
    kind, _, rest = instrument_spec.partition(":")
    if kind not in ("vst", "au"):
        return None
    plug_path, _, extra = rest.partition("::")
    if extra.startswith("name="):
        return extra[5:]                       # explicit plugin name (e.g. "Serum 2")
    return Path(plug_path).stem                # else the plugin file's basename


def _role_cache_key(notes: List[dict], instrument_spec: str,
                    params: Optional[dict], bpm: float, bars: int, sr: int) -> str:
    payload = json.dumps({"notes": notes, "inst": instrument_spec,
                          "params": params or {}, "bpm": bpm, "bars": bars, "sr": sr},
                         sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _build_src_track(client, tag: str, device_query: str, params: Optional[dict]) -> int:
    """Create a uniquely-tagged temp MIDI track, load the device, apply params.
    Returns the new track index (from the create command's own return, so no
    extra round-trip). Shared by the freeze path and the resample path; each
    appends its own clip flavor (session vs arrangement)."""
    from live_freeze import _load_device  # reuse tested helper

    track_index = int(client.send("create_midi_track", {"index": -1})["index"])
    client.send("set_track_name", {"track_index": track_index, "name": tag})
    _load_device(client, track_index, device_query)
    for name, value in (params or {}).items():
        try:
            client.send("set_device_parameter_by_name",
                        {"track_index": track_index, "device_index": 0,
                         "param_name": name, "value": value})
        except Exception:  # noqa: BLE001 — unknown/readonly params skipped, as headless does
            pass
    return track_index


def _build_role_track(client, role: str, notes: List[dict], bars: int,
                      device_query: str, params: Optional[dict]) -> Tuple[int, str]:
    """Build a source track and give it a SESSION clip of the notes (freeze path).
    Returns (track_index, tag). Does NOT freeze or delete — callers do that."""
    tag = f"SBX_{role}_{int(time.time() * 1000) % 10_000_000}"
    track_index = _build_src_track(client, tag, device_query, params)
    client.send("create_clip", {"track_index": track_index, "clip_index": 0,
                                "length": bars * 4.0})
    client.send("add_notes_to_clip", {"track_index": track_index, "clip_index": 0,
                                      "notes": notes})
    return track_index, tag


def _render_one_role(client, node, role: str, notes: List[dict], bars: int,
                     device_query: str, params: Optional[dict],
                     freeze_dir_on_node: str, out_wav: Path, timeout_s: float,
                     click_select: bool) -> None:
    """Create a temp tagged track on the node, freeze it via the node agent,
    capture the wav, and delete the temp track (per-role, serial path)."""
    from live_freeze import _delete_tagged_track  # reuse tested helper

    track_index, tag = _build_role_track(client, role, notes, bars, device_query, params)
    try:
        client.send("select_track", {"track_index": track_index})
        if click_select:  # GUI-focus the track so Freeze targets it (node-calibrated)
            try:
                node.automator("automator_select_track_by_click", {"track_index": track_index})
            except Exception:  # noqa: BLE001 — optional; LOM select is the fallback
                pass
        node.freeze_capture(freeze_dir_on_node, str(out_wav), timeout_s=timeout_s)
    finally:
        try:
            _delete_tagged_track(client, tag)  # re-finds by unique name; no undo needed
        except Exception:  # noqa: BLE001 — best-effort cleanup
            pass


def render_iteration_live(session, record) -> Dict[str, Any]:
    """Render every role's grooved notes through the isolated Ableton render node.
    Returns the same dict shape as renderer.render_iteration."""
    from live_client import LiveClient  # noqa: E402
    from render_node_agent import RenderNodeClient  # noqa: E402
    from live_freeze import find_freeze_dir  # noqa: E402

    host = cfg(session, "render.node_host")
    port = cfg(session, "render.node_port")
    agent_port = cfg(session, "render.node_agent_port")
    project_dir = cfg(session, "render.node_project_dir")
    if not project_dir:
        raise ValueError(
            "render.node_project_dir is empty — set it (via sandbox_config overrides) to the "
            "SAVED Live project folder ON THE RENDER NODE before using render.backend=ableton.")
    sr = cfg(session, "audio.sr")
    timeout_s = cfg(session, "fidelity.freeze_timeout_s")
    click_select = bool((getattr(session.config, "overrides", None) or {})
                        .get("render.node_click_select", False))
    bars = session.config.bars

    it_dir = session.dir() / "iterations" / f"{record.index:03d}"
    it_dir.mkdir(parents=True, exist_ok=True)
    cache = session.dir() / ".render_cache_live"
    cache.mkdir(parents=True, exist_ok=True)

    render_mode = cfg(session, "render.node_render_mode")
    tail_s = cfg(session, "render.node_record_tail_s")
    node = RenderNodeClient(host, agent_port, timeout=max(60.0, timeout_s + 30.0))
    client = LiveClient(host, port).connect()
    audio: Dict[str, str] = {}
    results: List[Dict[str, Any]] = []
    orig_tempo = None
    try:
        orig_tempo = client.send("get_session_info").get("tempo")
        client.send("set_tempo", {"tempo": session.bpm})

        # Split roles into cache-hits (copied) and pending (need rendering). A role
        # is renderable only if it's a real instrument with notes; fallback/empty
        # roles stay on the fast tier.
        pending: List[Tuple[str, List[dict], str, Path, Path]] = []  # role, notes, dq, out_wav, cache_path
        for role, notes in record.grooved.items():
            trk = session.tracks[role]
            if not notes:
                results.append({"role": role, "status": "skipped", "reason": "empty"})
                continue
            device_query = _device_query_for(trk.instrument_spec)
            if device_query is None:
                results.append({"role": role, "status": "skipped",
                                "reason": "fallback/proxy role — node renders real instruments only"})
                continue
            out_wav = it_dir / f"{role}.wav"
            key = _role_cache_key(notes, trk.instrument_spec, trk.params, session.bpm, bars, sr)
            cached = cache / f"{key}.wav"
            if cached.exists():
                shutil.copy2(cached, out_wav)
                audio[role] = str(out_wav)
                results.append({"role": role, "status": "cached", "output": str(out_wav)})
                continue
            pending.append((role, notes, device_query, out_wav, cached))

        if render_mode == "resample" and pending:
            # LOM-native real-time resampling: no GUI automation, all stems in ONE
            # real-time record pass (Live's API exposes no export/render/freeze).
            _render_pending_via_resample(client, node, session, bars, pending,
                                         it_dir, audio, results, float(tail_s), host)
        else:
            freeze_dir_on_node = str(find_freeze_dir(project_dir))  # freeze path only
            for role, notes, device_query, out_wav, cached in pending:
                trk = session.tracks[role]
                try:
                    _render_one_role(client, node, role, notes, bars,
                                     device_query, trk.params, freeze_dir_on_node,
                                     out_wav, float(timeout_s), click_select)
                    shutil.copy2(out_wav, cached)
                    audio[role] = str(out_wav)
                    results.append({"role": role, "status": "rendered", "output": str(out_wav)})
                except Exception as e:  # noqa: BLE001 — one role's failure never kills the render
                    results.append({"role": role, "status": "error", "error": f"{type(e).__name__}: {e}"})
    finally:
        if orig_tempo is not None:
            try:
                client.send("set_tempo", {"tempo": orig_tempo})
            except Exception:  # noqa: BLE001
                pass
        client.close()

    sum_stems_to_master(session, audio, it_dir, sr)  # writes master.wav into `audio`
    return {"audio": audio, "pool": results}


_Built = namedtuple("_Built", "role src_tag cap_tag cap_idx out_wav cache")


def _retrieve_stem(node, file_path: str, out_wav: Path, host: str) -> None:
    """Copy a node-recorded stem to out_wav. If the host shares the node's
    filesystem (same-Mac / mounted) the file is read directly; otherwise it's
    pulled over the agent. Waits briefly for the file to finish finalizing."""
    if os.path.exists(file_path):
        # local: wait for size to stabilize (Live finalizes on record stop)
        last = -1
        for _ in range(20):
            sz = os.path.getsize(file_path)
            if sz > 1000 and sz == last:
                break
            last = sz
            time.sleep(0.1)
        shutil.copy2(file_path, out_wav)
    else:
        node.fetch_wav(file_path, str(out_wav))  # remote node


def _render_pending_via_resample(client, node, session, bars: int,
                                 pending: List[Tuple[str, List[dict], str, Path, Path]],
                                 it_dir: Path, audio: Dict[str, str],
                                 results: List[Dict[str, Any]], tail_s: float,
                                 host: str) -> None:
    """Capture every pending role in ONE real-time recording pass via LOM
    resampling — no GUI automation, since Live's API exposes no export/render.

    Per role: a source MIDI track (instrument + params + an ARRANGEMENT clip of
    the notes) and an armed audio track whose input is that source, post-FX. Then
    one arrangement-record pass records all stems simultaneously; each recorded
    clip's file_path is fetched back and mapped to its role. All temp tracks are
    deleted in finally. Never touches the user's own set (isolated node only)."""
    from live_freeze import _delete_tagged_track

    length_beats = bars * 4.0
    record_s = length_beats * (60.0 / max(1e-6, float(session.bpm))) + float(tail_s)
    stamp = int(time.time() * 1000) % 10_000_000
    built: List[_Built] = []
    try:
        for i, (role, notes, device_query, out_wav, cached) in enumerate(pending):
            trk = session.tracks[role]
            src_tag = f"SBXSRC_{role}_{stamp}_{i}"
            cap_tag = f"SBXCAP_{role}_{stamp}_{i}"

            # source MIDI track: instrument + params + an ARRANGEMENT clip of the notes
            src_idx = _build_src_track(client, src_tag, device_query, trk.params)
            client.send("create_arrangement_clip",
                        {"track_index": src_idx, "start_time": 0.0, "length": length_beats})
            client.send("add_notes_to_arrangement_clip",
                        {"track_index": src_idx, "clip_index": 0, "notes": notes})

            # capture audio track: input routed from the source (post-FX), armed.
            # The create command returns the new index, so no rescan is needed —
            # no tracks are deleted before retrieval, so the index stays valid.
            cap_idx = int(client.send("create_audio_track", {"index": -1})["index"])
            client.send("set_track_name", {"track_index": cap_idx, "name": cap_tag})
            client.send("set_track_input_routing",
                        {"track_index": cap_idx, "source_name": src_tag, "channel": "Post FX"})
            client.send("set_track_arm", {"track_index": cap_idx, "arm": True})
            built.append(_Built(role, src_tag, cap_tag, cap_idx, out_wav, cached))

        # ONE real-time record pass captures every armed capture track at once
        client.send("set_current_position", {"position": 0.0})
        client.send("set_record_mode", {"mode": 1})
        client.send("start_playback")
        time.sleep(record_s + 1.0)  # +margin for latency + file finalize
        client.send("stop_playback")
        client.send("set_record_mode", {"mode": 0})

        for b in built:
            try:
                props = client.send("get_audio_clip_properties",
                                    {"track_index": b.cap_idx, "clip_index": 0})
                fp = props.get("file_path")
                if not fp:
                    raise RuntimeError("recorded clip has no file_path")
                _retrieve_stem(node, fp, b.out_wav, host)
                shutil.copy2(b.out_wav, b.cache)
                audio[b.role] = str(b.out_wav)
                results.append({"role": b.role, "status": "rendered", "output": str(b.out_wav)})
            except Exception as e:  # noqa: BLE001 — one role failing never kills the pass
                results.append({"role": b.role, "status": "error",
                                "error": f"{type(e).__name__}: {e}"})
    except Exception as e:  # noqa: BLE001 — record-pass failure fails these roles, not the loop
        for b in built:
            if b.role not in audio:
                results.append({"role": b.role, "status": "error",
                                "error": f"resample pass failed: {type(e).__name__}: {e}"})
    finally:
        # delete capture + source temp tracks by unique tag (never a user track)
        for b in built:
            for tag in (b.cap_tag, b.src_tag):
                try:
                    _delete_tagged_track(client, tag)
                except Exception:  # noqa: BLE001 — best-effort cleanup
                    pass
