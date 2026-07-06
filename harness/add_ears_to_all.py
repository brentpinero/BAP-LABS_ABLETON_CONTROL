"""
add_ears_to_all.py — load the per-track Mix Analysis Hub device onto every track,
group, and the master of the CURRENT Ableton session, via the (extended) Remote Script.

Requires the AbletonMCP Remote Script edits (user_library category + master target)
to be live — i.e. Ableton restarted after editing the script. Run:

    python add_ears_to_all.py            # dry run: find device + list targets
    python add_ears_to_all.py --load     # actually load onto every track + master
"""

import sys
from collections import deque

from live_client import LiveClient

DEVICE = "mix analysis hub (per-track)"


def find_device_uri(c) -> str | None:
    q = deque([("user_library", 0)])
    seen = 0
    while q and seen < 4000:
        path, d = q.popleft()
        try:
            items = c.send("get_browser_items_at_path", {"path": path}).get("items", [])
        except Exception:
            continue
        for it in items:
            seen += 1
            if DEVICE in (it.get("name") or "").lower() and it.get("is_loadable"):
                return it["uri"]
            if it.get("is_folder") and d < 6:
                q.append((path + "/" + it["name"], d + 1))
    return None


def main():
    do_load = "--load" in sys.argv
    with LiveClient() as c:
        info = c.send("get_session_info")
        n = info.get("track_count", 0)
        uri = find_device_uri(c)
        if not uri:
            print("Device not found under user_library. Is Ableton restarted after the "
                  "Remote Script edit, and does the browser show the .amxd?")
            return 1
        print(f"device uri: {uri}")
        print(f"targets: {n} tracks (incl. groups) + master")
        if not do_load:
            print("dry run — re-run with --load to add the device.")
            return 0

        ok, fail = 0, 0
        for i in list(range(n)) + [-1]:            # -1 == master
            label = "master" if i == -1 else f"track {i}"
            try:
                r = c.send("load_browser_item", {"track_index": i, "item_uri": uri})
                loaded = r.get("loaded")
                print(f"  {label}: {'OK' if loaded else 'skipped'} "
                      f"({r.get('track_name','?')}) devices={len(r.get('devices_after', []))}")
                ok += 1 if loaded else 0
            except Exception as e:
                print(f"  {label}: FAIL {e}")
                fail += 1
        print(f"\nloaded onto {ok} nodes, {fail} failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
