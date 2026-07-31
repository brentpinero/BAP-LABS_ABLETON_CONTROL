"""
live_freeze.py — automated Ableton Freeze rendering (calibration ground truth).

freeze_render() drives the OPEN Live set: creates a temp track, loads the
device, applies state, writes the clip, freezes (Live renders the exact 32-bit
audio with the full chain), copies the freeze wav out, then undoes/cleans up.
ONLY used during explicit user-initiated calibration or opt-in post-commit
verification — never inside the sandbox loop.

Freeze files land in <Project>/Samples/Processed/Freeze/. Live must be open on
a SAVED project (freeze needs a project folder).
"""
from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from live_client import LiveClient, LiveError, automator


class FreezeFailed(Exception):
    pass


def find_freeze_dir(project_dir: str | Path) -> Path:
    return Path(project_dir) / "Samples" / "Processed" / "Freeze"


def _wait_for_new_wav(freeze_dir: Path, before: set, timeout_s: float,
                      poll_s: float = 0.5) -> Path:
    """Poll for a NEW size-stable wav in the freeze folder."""
    deadline = time.monotonic() + timeout_s
    last_size: Dict[Path, int] = {}
    while time.monotonic() < deadline:
        now = set(freeze_dir.glob("*.wav")) if freeze_dir.exists() else set()
        fresh = sorted(now - before, key=lambda p: p.stat().st_mtime)
        for f in fresh:
            size = f.stat().st_size
            if size > 1000 and last_size.get(f) == size:  # stable across two polls
                return f
            last_size[f] = size
        time.sleep(poll_s)
    raise FreezeFailed(
        f"No new freeze wav appeared in {freeze_dir} within {timeout_s}s. Check: "
        f"(1) Live has a SAVED project, (2) Accessibility permission for automation, "
        f"(3) the track isn't receiving routing that blocks Freeze.")


def _load_device(client: LiveClient, track_index: int, device_query: str,
                 max_depth: int = 3) -> None:
    """Find a loadable browser item matching device_query and load it onto the
    track. Bounded BFS through Plug-Ins (vendor folders!) then Instruments."""
    q = device_query.lower()
    from collections import deque
    for root in ("Plug-Ins", "Instruments"):
        queue = deque([(root, 0)])
        while queue:
            path, depth = queue.popleft()
            try:
                items = client.send("get_browser_items_at_path", {"path": path}).get("items", [])
            except LiveError:
                continue
            # exact name match first at this level, then substring
            for match_exact in (True, False):
                for it in items:
                    name = it.get("name", "")
                    ok = (name.lower() == q) if match_exact else (q in name.lower())
                    if ok and it.get("is_loadable"):
                        client.send("load_browser_item",
                                    {"track_index": track_index, "item_uri": it["uri"]})
                        return
            if depth < max_depth:
                for it in items:
                    if it.get("is_folder"):
                        # prioritize folders whose name hints at the query (vendor match)
                        entry = (f"{path}/{it['name']}", depth + 1)
                        if q.split()[0] in it["name"].lower():
                            queue.appendleft(entry)
                        else:
                            queue.append(entry)
    raise FreezeFailed(f"Could not find loadable device matching {device_query!r} in the browser")


def capture_device_state(track_index: int, device_index: int = 0,
                         client: Optional[LiveClient] = None) -> Dict[str, float]:
    """Snapshot a device's named params from Live — the bridge from a user-designed
    patch to a headless-renderable param dict."""
    own = client is None
    c = client or LiveClient().connect()
    try:
        res = c.send("get_device_parameters",
                     {"track_index": track_index, "device_index": device_index})
        return {p["name"]: p["value"] for p in res.get("parameters", [])}
    finally:
        if own:
            c.close()


def find_track_index_by_name(client: LiveClient, name: str) -> Optional[int]:
    """Index of the track whose name == `name` (reverse scan, robust to index
    shifts; skips rows that raise, e.g. group/return), or None."""
    n = int(client.send("get_session_info").get("track_count", 0))
    for i in range(n - 1, -1, -1):
        try:
            ti = client.send("get_track_info", {"track_index": i})
        except LiveError:
            continue  # main/group/return
        if ti.get("name") == name:
            return i
    return None


def _delete_tagged_track(client: LiveClient, tag: str) -> None:
    """Delete the temp track whose name == tag, re-scanning by name (robust to
    index shifts). Only deletes an EXACT tag match — never a user track."""
    idx = find_track_index_by_name(client, tag)
    if idx is not None:
        client.send("delete_track", {"track_index": idx})


def freeze_render(notes: List[Dict[str, Any]], bpm: float, bars: int,
                  device_query: str, project_dir: str | Path,
                  params: Optional[Dict[str, float]] = None,
                  timeout_s: float = 120.0, out_path: Optional[Path] = None) -> Path:
    """Render notes through a device in LIVE via Freeze; return the copied wav path.
    The temp track is undone/removed no matter what (cleanup in finally)."""
    freeze_dir = find_freeze_dir(project_dir)
    client = LiveClient().connect()
    track_index = None
    orig_tempo = None
    try:
        info = client.send("get_session_info")
        orig_tempo = info.get("tempo")  # ALWAYS restored in finally (bug fix:
        client.send("set_tempo", {"tempo": bpm})  # first calibration left 100 BPM behind)
        client.send("create_midi_track", {"index": -1})
        track_index = int(client.send("get_session_info").get("track_count", 1)) - 1
        tag = f"FID_{int(time.time()) % 100000}"
        client.send("set_track_name", {"track_index": track_index, "name": tag})

        _load_device(client, track_index, device_query)
        if params:
            for name, value in params.items():
                try:
                    client.send("set_device_parameter_by_name",
                                {"track_index": track_index, "device_index": 0,
                                 "param_name": name, "value": value})
                except LiveError:
                    pass  # unknown/readonly params skipped, mirroring headless setattr

        client.send("create_clip", {"track_index": track_index, "clip_index": 0,
                                    "length": bars * 4.0})
        client.send("add_notes_to_clip", {"track_index": track_index, "clip_index": 0,
                                          "notes": notes})
        client.send("select_track", {"track_index": track_index})

        before = set(freeze_dir.glob("*.wav")) if freeze_dir.exists() else set()
        res = automator("automator_freeze")
        if not res.get("success", False):
            raise FreezeFailed(f"Freeze menu automation failed: {res}")
        wav = _wait_for_new_wav(freeze_dir, before, timeout_s)

        dest = Path(out_path) if out_path else Path(project_dir) / f"{tag}.wav"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(wav, dest)  # freeze files vanish on unfreeze — copy first
        return dest
    finally:
        if orig_tempo is not None:
            try:
                client.send("set_tempo", {"tempo": orig_tempo})
            except Exception:
                pass
        # delete the temp track by re-finding its unique tag (index may shift);
        # deleting removes it whether frozen or not -> no automator undo needed,
        # so the user's real undo history stays clean.
        if track_index is not None:
            try:
                _delete_tagged_track(client, tag)
            except Exception:
                pass
        client.close()
