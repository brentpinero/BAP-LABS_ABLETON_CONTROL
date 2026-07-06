"""
load_all_ears.py — idempotently load the per-track Mix Analysis Hub onto EVERY
individual track (audio/midi) of the current session. Resumable: skips tracks that
already have the device (so a re-run after a timeout adds no duplicates). Group
tracks are handled separately; invisible (folded-inside) tracks are reported.

Run (backgroundable, logs progress):  python load_all_ears.py
"""

import sys
import time

from live_client import LiveClient

URI = ("query:UserLibrary#Presets:Audio%20Effects:Max%20Audio%20Effect:"
       "BAP%20Labs%20Mix%20Analysis%20Hub%20(Per-Track).amxd")
DEVNAME = "BAP Labs Mix Analysis Hub (Per-Track)"


def log(msg):
    print(msg, flush=True)


def main():
    with LiveClient() as c:
        n = c.send("get_session_info").get("track_count", 0)
        log(f"[load_all_ears] {n} tracks; scanning existing devices…")

        todo, groups, have = [], [], 0
        for i in range(n):
            try:
                ti = c.send("get_track_info", {"track_index": i})
            except Exception as e:
                if "Group" in str(e):
                    groups.append(i)          # group track — handled elsewhere
                continue
            names = [d.get("name") if isinstance(d, dict) else d for d in ti.get("devices", [])]
            if DEVNAME in names:
                have += 1
            else:
                todo.append(i)

        log(f"[load_all_ears] already have: {have} | to load: {len(todo)} | groups(skip): {len(groups)}")

        ok, invisible, other = 0, [], []
        for k, i in enumerate(todo, 1):
            try:
                c.send("load_browser_item", {"track_index": i, "item_uri": URI})
                ok += 1
            except Exception as e:
                (invisible if "invisible" in str(e).lower() else other).append(i)
            if k % 10 == 0 or k == len(todo):
                log(f"[load_all_ears] {k}/{len(todo)} processed ({ok} ok, "
                    f"{len(invisible)} invisible, {len(other)} other)")

        log(f"[load_all_ears] DONE. loaded {ok} | invisible {len(invisible)} | other {len(other)}")
        if invisible:
            log(f"[load_all_ears] invisible (unfold parent groups to reach): {invisible}")
        if other:
            log(f"[load_all_ears] other failures: {other}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
