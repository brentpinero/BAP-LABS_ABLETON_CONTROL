"""
stem_ablation.py — automated per-node plugin-ablation stem renderer.

For each node (track / group / return / master) this walks the device chain and
renders a LADDER of stems:

  rung 0  baseline_all_on   — every device enabled (the real mix stem; also an
                              A/A repeatability check vs the final progressive rung)
  rung 1  all_off           — every device bypassed (the dry source/instrument alone)
  rung 2  through_0_<dev0>  — only device 0 enabled
  rung 3  through_1_<dev1>  — devices 0..1 enabled
  ...
  rung N+1 through_{N-1}    — devices 0..N-1 enabled  (== baseline)

Diffing consecutive progressive rungs isolates EACH plugin's audible contribution.
Ladder length is N+2 for a chain of N devices.

Two render paths, chosen per run with `--mode`:
  resample  — GUI-free, universal (track/group/return/master). A capture audio track
              is routed from the node's Post-FX tap (or the master "Resampling" bus)
              and records one real-time pass. Reuses the command set proven in
              sandbox/renderer_live.py.
  freeze    — Ableton's offline Freeze (ground-truth render quality) for a regular
              track: select → Freeze → copy the wav → Unfreeze (so the next rung can
              re-toggle devices). Cannot render the master bus.

Device bypass is set_device_enabled (the "Device On" param). The node's ORIGINAL
enabled states are captured up front and ALWAYS restored in a finally — the user's
set is left exactly as found.

The Ableton-driving pieces go through a small `client.send(cmd, params)` seam
(LiveClient) + the in-process `automator(...)`; the ladder/enumeration/sidecar/
restore logic is pure and unit-tested with a fake client (see test_stem_ablation.py).
Live validation (esp. the group/master resample routing + freeze/unfreeze) needs
Ableton open — see the plan's B3 spike.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from causal_dataset import SCHEMA_VERSION, sha256_file
from live_client import LiveClient, LiveError, automator
from live_freeze import _wait_for_new_wav, find_freeze_dir

_ROOT = Path(__file__).resolve().parent.parent


class RenderError(Exception):
    pass


# ---------------------------------------------------------------------------
# Pure model + ladder (no Ableton) — the unit-tested core
# ---------------------------------------------------------------------------
@dataclass
class NodeChain:
    """One renderable node and its device chain."""
    ref: Any                     # track_index int, -1 (master), or "return:N"
    name: str
    kind: str                    # regular | group | return | master
    devices: list = field(default_factory=list)   # [{index, name, class_name}]


def _slug(text: str) -> str:
    """Filesystem-safe token from an arbitrary name."""
    return re.sub(r"[^0-9A-Za-z]+", "-", str(text)).strip("-") or "x"


def node_slug(node: NodeChain) -> str:
    """Stable per-node filename prefix, e.g. master_-1_Master, track_3_Lead."""
    kind = node.kind or "track"
    ref = str(node.ref).replace(":", "-")
    return f"{kind}_{ref}_{_slug(node.name)}"


def ablation_ladder(device_names: list) -> list[dict]:
    """The rung plan for a chain of N devices (pure). See module docstring.

    N == 0 -> a single 'no_devices' rung (the node's dry stem still renders).
    Otherwise N+2 rungs: baseline_all_on, all_off, then through_0..through_{N-1}.
    """
    n = len(device_names)
    if n == 0:
        return [{"index": 0, "kind": "no_devices", "enabled_through": -1,
                 "enabled_mask": [], "label": "no_devices", "newly_enabled": None}]
    rungs = [
        {"kind": "baseline", "enabled_through": n - 1, "enabled_mask": [True] * n,
         "label": "baseline_all_on", "newly_enabled": None},
        {"kind": "all_off", "enabled_through": -1, "enabled_mask": [False] * n,
         "label": "all_off", "newly_enabled": None},
    ]
    for k in range(n):
        rungs.append({
            "kind": "progressive", "enabled_through": k,
            "enabled_mask": [i <= k for i in range(n)],
            "label": f"through_{k}_{_slug(device_names[k])}",
            "newly_enabled": device_names[k],
        })
    for i, r in enumerate(rungs):
        r["index"] = i
    return rungs


def node_from_info(ref: Any, info: dict) -> NodeChain:
    """Build a NodeChain from a get_track_info result (device index defaults to
    positional slot for surfaces that omit it, e.g. return tracks)."""
    devices = [{"index": d.get("index", i), "name": d.get("name", ""),
                "class_name": d.get("class_name", "")}
               for i, d in enumerate(info.get("devices", []))]
    return NodeChain(ref=ref, name=info.get("name", str(ref)),
                     kind=info.get("kind", "regular"), devices=devices)


def sidecar(node: NodeChain, rung: dict, mode: str, wav_name: str,
            ok: bool, error: Optional[str]) -> dict:
    """Per-rung metadata written next to each stem wav."""
    return {
        "schema_version": SCHEMA_VERSION,
        "node": {"ref": node.ref, "name": node.name, "kind": node.kind},
        "rung": {k: rung[k] for k in ("index", "kind", "enabled_through", "label",
                                      "newly_enabled")},
        "devices": [dict(d, enabled=bool(en))
                    for d, en in zip(node.devices, rung["enabled_mask"])],
        "render_mode": mode,
        "wav": wav_name,
        "rendered": ok,
        "error": error,
    }


# ---------------------------------------------------------------------------
# Ableton I/O (through the client.send seam)
# ---------------------------------------------------------------------------
def enumerate_nodes(client, max_returns: int = 24) -> list[NodeChain]:
    """All addressable nodes: regular/group tracks, return tracks, and the master."""
    nodes: list[NodeChain] = []
    n = int(client.send("get_session_info").get("track_count", 0))
    for i in range(n):
        try:
            nodes.append(node_from_info(i, client.send("get_track_info", {"track_index": i})))
        except LiveError:
            continue                                  # unresolvable row — skip
    for j in range(max_returns):                      # returns via the resolver ref
        try:
            nodes.append(node_from_info(f"return:{j}",
                                        client.send("get_track_info", {"track_index": f"return:{j}"})))
        except LiveError:
            break                                     # no more return tracks
    try:
        nodes.append(node_from_info(-1, client.send("get_track_info", {"track_index": -1})))
    except LiveError:
        pass
    return nodes


def read_enabled_mask(client, node: NodeChain) -> list[bool]:
    """Current on/off state per device (for restore). Devices without a 'Device On'
    param — or that fail to read — are treated as always-on (True)."""
    mask = []
    for d in node.devices:
        enabled = True                                # no 'Device On' / unreadable → always-on
        try:
            params = client.send("get_device_parameters",
                                 {"track_index": node.ref, "device_index": d["index"]}).get("parameters", [])
            on = next((p for p in params if p.get("name") == "Device On"), None)
            enabled = bool(on["value"]) if on else True
        except LiveError:
            pass
        mask.append(enabled)
    return mask


def apply_enabled_mask(client, node: NodeChain, mask: list) -> list[str]:
    """Set each device on/off to `mask`. Returns per-device outcome: ok|no_on_off|error."""
    out = []
    for d, want in zip(node.devices, mask):
        status = "ok"
        try:
            client.send("set_device_enabled",
                        {"track_index": node.ref, "device_index": d["index"], "enabled": bool(want)})
        except LiveError as e:
            status = "no_on_off" if "on/off" in str(e).lower() else "error"
        out.append(status)
    return out


CAPTURE_PREFIX = "ABLCAP_"


def _sweep_capture_tracks(client, prefix: str = CAPTURE_PREFIX) -> int:
    """DISARM then delete every leftover capture track (highest index first so earlier
    indices don't shift mid-sweep). Returns how many were removed.

    Critical: LOM arm is NOT exclusive (unlike the GUI, arming one track does not disarm
    others), so a stray armed capture track from a prior rung WILL keep recording
    alongside the new one — literally recording over. Disarm before delete so nothing
    armed can linger even if a delete is refused."""
    n = int(client.send("get_session_info").get("track_count", 0))
    removed = 0
    for i in range(n - 1, -1, -1):
        try:
            ti = client.send("get_track_info", {"track_index": i})
        except LiveError:
            continue
        if str(ti.get("name", "")).startswith(prefix):
            try:
                client.send("set_track_arm", {"track_index": i, "arm": False})
            except LiveError:
                pass
            try:
                client.send("delete_track", {"track_index": i})
                removed += 1
            except LiveError:
                pass
    return removed


def _soloed_tracks(client) -> list[int]:
    """Indices of every soloed regular/group track. A solo mutes everything else, so it
    silently starves the master (and any node fed by muted sources) during capture — the
    #1 cause of empty stems. Detect it up front."""
    n = int(client.send("get_session_info").get("track_count", 0))
    out = []
    for i in range(n):
        try:
            if client.send("get_track_info", {"track_index": i}).get("solo"):
                out.append(i)
        except LiveError:
            continue
    return out


def _set_solos(client, indices, state: bool) -> None:
    for i in indices:
        try:
            client.send("set_track_solo", {"track_index": i, "solo": bool(state)})
        except LiveError:
            pass


def _record_seconds(bars: int, bpm: float, bpb: int = 4) -> float:
    return bars * bpb * 60.0 / max(bpm, 1.0)


def _copy_stem(file_path: str, out_wav: Path) -> None:
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    if not Path(file_path).exists():
        raise RenderError(f"recorded stem not found on disk: {file_path}")
    shutil.copy2(file_path, out_wav)


def render_resample(client, node: NodeChain, out_wav: Path, bars: int = 8,
                    start_bar: int = 1, settle_s: float = 0.4) -> None:
    """Capture the node's post-FX output (or the master 'Resampling' bus) via a
    temporary armed audio track over one real-time record pass. GUI-free; universal.

    Records `bars` bars starting at `start_bar` (1-indexed, Ableton's bar numbering) —
    set this past any silent intro so the stem captures actual musical content.

    NOTE (B3 spike): the group/return Post-FX and master Resampling routing here is
    live-unvalidated — confirm on a real set before trusting group/master stems.
    """
    info = client.send("get_session_info")
    bpm = float(info.get("tempo", 120.0))
    bpb = int(info.get("signature_numerator", 4) or 4)
    start_pos = max(0, start_bar - 1) * bpb                 # beats; bar 1 == position 0
    _sweep_capture_tracks(client)                           # clean slate: no armed leftover can co-record
    tag = "%s%d" % (CAPTURE_PREFIX, int(time.time()) % 100000)
    cap = int(client.send("create_audio_track", {"index": -1})["index"])
    loop_prev = True
    try:
        client.send("set_track_name", {"track_index": cap, "name": tag})
        # master output is captured via the "Resampling" input (post master chain) — it has
        # NO sub-channel, so don't pass one. Track/group tap the node's Post-FX by name.
        if node.kind == "master":
            want_src, req = "Resampling", {"track_index": cap, "source_name": "Resampling"}
        else:
            want_src, req = node.name, {"track_index": cap, "source_name": node.name,
                                        "channel": "Post FX"}
        client.send("set_track_input_routing", req)
        # VERIFY the routing actually took — a silent mismatch would record the WRONG source
        # (e.g. the capture defaulting to Ext. In or a stale track). Fail loudly instead.
        got = client.send("get_track_input_routing", {"track_index": cap}).get("input_routing_type")
        if got != want_src:
            raise RenderError(f"input routing for {node.kind} '{node.name}' did not take: "
                              f"wanted {want_src!r}, got {got!r} (source not available?)")
        client.send("set_track_arm", {"track_index": cap, "arm": True})
        # Master capture taps "Resampling" (= master out); monitoring In would loop it
        # straight back into the master → feedback. Off (2) still records the armed input.
        # Track/group Post-FX taps a specific track, so In (0) is safe and audible.
        client.send("set_track_monitor",
                    {"track_index": cap, "state": 2 if node.kind == "master" else 0})
        loop_prev = bool(client.send("set_song_loop", {"loop": False}).get("previous", True))
        client.send("set_current_position", {"position": float(start_pos)})
        client.send("set_record_mode", {"mode": 1})
        client.send("start_playback")
        time.sleep(_record_seconds(bars, bpm, bpb) + settle_s)
        client.send("stop_playback")
        client.send("set_record_mode", {"mode": 0})
        props = client.send("get_audio_clip_properties", {"track_index": cap, "clip_index": 0})
        fp = props.get("file_path")
        if not fp:
            raise RenderError("captured clip has no file_path")
        _copy_stem(fp, out_wav)
    finally:
        # Idempotent transport reset — also covers an INTERRUPT during the record sleep
        # (the try-path stop/reset above never runs then), so we never leave the set
        # playing or armed-recording.
        for cmd, params in (("stop_playback", {}), ("set_record_mode", {"mode": 0}),
                            ("set_track_arm", {"track_index": cap, "arm": False})):
            try:
                client.send(cmd, params)
            except LiveError:
                pass
        if loop_prev:
            try:
                client.send("set_song_loop", {"loop": True})
            except LiveError:
                pass
        try:
            _sweep_capture_tracks(client)              # disarm+delete this cap AND any straggler
        except LiveError:
            pass


def render_freeze(client, node: NodeChain, out_wav: Path, project_dir: str | Path,
                  timeout_s: float = 120.0) -> None:
    """Offline Freeze render of a regular/group track's current (ablated) chain, then
    Unfreeze so the next rung can re-toggle devices. Master/return cannot be frozen."""
    if not isinstance(node.ref, int) or node.ref < 0:
        raise RenderError(f"freeze cannot render {node.kind} node {node.ref!r}; use --mode resample")
    freeze_dir = find_freeze_dir(project_dir)
    before = set(freeze_dir.glob("*.wav")) if freeze_dir.exists() else set()
    client.send("select_track", {"track_index": node.ref})
    if not automator("automator_freeze").get("success", False):
        raise RenderError("Freeze menu automation failed (Accessibility permission? saved project?)")
    try:
        wav = _wait_for_new_wav(freeze_dir, before, timeout_s)
        out_wav.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(wav, out_wav)                     # freeze wavs vanish on unfreeze — copy first
    finally:
        client.send("select_track", {"track_index": node.ref})
        automator("automator_unfreeze")                # leave the track editable for the next rung


def render_node(client, node: NodeChain, mode: str, out_wav: Path, *,
                project_dir: str | Path | None = None, bars: int = 8,
                start_bar: int = 1) -> None:
    if mode == "freeze":
        if project_dir is None:
            raise RenderError("--mode freeze needs --project-dir (the Live project folder)")
        render_freeze(client, node, out_wav, project_dir)
    else:
        render_resample(client, node, out_wav, bars=bars, start_bar=start_bar)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def run_ablation(client, nodes: list, mode: str, out_dir: str | Path, *,
                 project_dir: str | Path | None = None, bars: int = 8, start_bar: int = 1,
                 project_file: str | Path | None = None,
                 render_fn: Optional[Callable[[NodeChain, dict, Path], None]] = None,
                 started_at: Optional[float] = None) -> dict:
    """Run the ablation ladder for every node, writing stems + sidecars + a manifest.

    ORIGINAL device-enabled states are captured per node and restored in a finally,
    so the user's set is left exactly as found even if a render raises.

    `render_fn(node, rung, out_wav)` is injectable (tests pass a fake that writes a
    dummy wav); by default it dispatches to render_node with `mode`.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    live = render_fn is None                            # live capture vs an injected test fn
    if render_fn is None:
        def render_fn(node, rung, out_wav):
            render_node(client, node, mode, out_wav, project_dir=project_dir, bars=bars,
                        start_bar=start_bar)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "session_dir": str(out_dir),
        "started_at": started_at if started_at is not None else time.time(),
        "render_mode": mode,
        "bars": bars,
        "start_bar": start_bar,
        "project_dir": str(project_dir) if project_dir else None,
        "project_file": {"path": str(project_file), "sha256": sha256_file(project_file)}
        if project_file else None,
        "ladder": "per node, N+2 rungs: baseline_all_on, all_off, through_0..through_{N-1}",
        "nodes": [{"ref": n.ref, "name": n.name, "kind": n.kind,
                   "devices": n.devices, "n_rungs": len(ablation_ladder([d["name"] for d in n.devices]))}
                  for n in nodes],
    }
    manifest["cleared_solos"] = []
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=1))

    # A soloed track mutes every other track, so the master (and any node fed by muted
    # sources) records silence. Clear solos for the whole run; restore in the finally so
    # the user's set is left exactly as found. render_fn=None means live capture; a test's
    # injected render_fn has no client to query, so only guard the live path.
    solos = _soloed_tracks(client) if live else []
    if solos:
        print(f"[{time.strftime('%H:%M:%S')}] clearing {len(solos)} soloed track(s) for capture "
              f"(restored after): {solos}", flush=True)
        manifest["cleared_solos"] = solos
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=1))
        _set_solos(client, solos, False)
    try:
        for node in nodes:
            original = read_enabled_mask(client, node)     # capture BEFORE toggling
            try:
                device_names = [d["name"] for d in node.devices]
                ladder = ablation_ladder(device_names)
                for rung in ladder:
                    apply_enabled_mask(client, node, rung["enabled_mask"])
                    wav_name = f"{node_slug(node)}__rung{rung['index']:02d}_{rung['label']}.wav"
                    out_wav = out_dir / wav_name
                    ok, err = True, None
                    print(f"[{time.strftime('%H:%M:%S')}] {node_slug(node)} "
                          f"rung {rung['index'] + 1}/{len(ladder)} {rung['label']} ...", flush=True)
                    try:
                        render_fn(node, rung, out_wav)
                    except Exception as e:                 # a bad rung must not abort the node
                        ok, err = False, str(e)
                    if not ok:
                        print(f"    -> FAILED: {err}", flush=True)
                    (out_dir / (wav_name[:-4] + ".json")).write_text(
                        json.dumps(sidecar(node, rung, mode, wav_name, ok, err), indent=1))
            finally:
                apply_enabled_mask(client, node, original)  # ALWAYS restore the user's chain
    finally:
        _set_solos(client, solos, True)                     # restore the user's solo(s)
    return manifest


# ---------------------------------------------------------------------------
# Node selection + CLI
# ---------------------------------------------------------------------------
def filter_nodes(nodes: list, selectors: Optional[list]) -> list:
    """Keep nodes matching any selector (exact ref like 'master'/'3'/'return:0', or a
    case-insensitive name substring). None/empty -> all nodes."""
    if not selectors:
        return nodes
    sel = [s.lower() for s in selectors]
    out = []
    for n in nodes:
        ref = str(n.ref).lower()
        alias = "master" if n.ref == -1 else ref
        if any(s == ref or s == alias or s in n.name.lower() for s in sel):
            out.append(n)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Automated per-node plugin-ablation stem renderer.")
    ap.add_argument("--mode", choices=["freeze", "resample"], default="resample",
                    help="freeze = offline ground truth (regular/group tracks); "
                         "resample = GUI-free, universal (default)")
    ap.add_argument("--nodes", nargs="*", default=None,
                    help="node names or refs to render (default: all). e.g. master 'Lead' return:0")
    ap.add_argument("--session", default=None, help="session id (default: abl_<epoch>)")
    ap.add_argument("--project-dir", default=None, help="Live project folder (required for --mode freeze)")
    ap.add_argument("--project-file", default=None, help="path to the .als for provenance hashing")
    ap.add_argument("--bars", type=int, default=8, help="resample capture length in bars (default 8)")
    ap.add_argument("--start-bar", type=int, default=1,
                    help="bar to start the resample capture at (1-indexed; set past a silent intro)")
    ap.add_argument("--out", default=None, help="output dir (default sandbox_sessions/ablation/<session>)")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=9877)
    args = ap.parse_args(argv)

    client = LiveClient(host=args.host, port=args.port).connect()
    try:
        nodes = filter_nodes(enumerate_nodes(client), args.nodes)
        if not nodes:
            print("[ABLATION] no matching nodes — nothing to render.")
            return 1
        session = args.session or ("abl_%d" % int(time.time()))
        out_dir = Path(args.out) if args.out else _ROOT / "sandbox_sessions" / "ablation" / session
        print(f"[ABLATION] {len(nodes)} node(s), mode={args.mode} -> {out_dir}")
        for n in nodes:
            print(f"  - {n.kind} {n.ref} '{n.name}' ({len(n.devices)} devices, "
                  f"{len(ablation_ladder([d['name'] for d in n.devices]))} rungs)")
        run_ablation(client, nodes, args.mode, out_dir, project_dir=args.project_dir,
                     bars=args.bars, start_bar=args.start_bar, project_file=args.project_file)
        print(f"[ABLATION] done -> {out_dir}/manifest.json")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
