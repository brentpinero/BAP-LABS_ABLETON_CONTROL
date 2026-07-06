"""
swap_ears_to_biquad.py — migrate the per-track Mix Analysis Hub from the old
onepole device to the calibrated biquad device across the whole session.

Both devices emit /track/<id>/spectrum, so they FIGHT if both sit on a track — the
migration must DELETE the onepole instance and LOAD the biquad one, per track.

Three modes, staged for safety on a live 70-track session:
    python swap_ears_to_biquad.py              # DISCOVER (read-only): map exact state + plan
    python swap_ears_to_biquad.py --swap       # EXECUTE: delete onepole + load biquad, resumable
    python swap_ears_to_biquad.py --verify      # VERIFY: every target has biquad, none have onepole

Covers ALL node types uniformly — regular tracks (index), groups (index), master
(-1), and returns ("return:N") — via the Remote Script's unified track resolver.
(Before that fix, groups/master/returns errored on introspect and were hand-swapped.)

Safety:
  * exact device-name match (biquad name CONTAINS the onepole name → substring is unsafe),
  * re-fetches track devices before each delete (indices shift as devices are removed),
  * resumable: skips nodes already on biquad-only,
  * SAVE A BACKUP of the .als before --swap (deleting devices is destructive).
"""

import sys
import time
from collections import deque

from live_client import LiveClient

THROTTLE_S = 1.5       # M4L device LOAD is heavy; give Max time to fully instantiate
OP_TIMEOUT = 60.0      # loading a device (js compile + DSP) can be slow when Live is busy

ONEPOLE = "BAP Labs Mix Analysis Hub (Per-Track)"          # exact device name
BIQUAD = "BAP Labs Mix Analysis Hub (Per-Track Biquad)"    # exact device name


def find_uri(c, needle_exact_lower):
    """Walk the user library browser for a loadable item whose name matches exactly."""
    q = deque([("user_library", 0)])
    seen = 0
    while q and seen < 6000:
        path, d = q.popleft()
        try:
            items = c.send("get_browser_items_at_path", {"path": path}).get("items", [])
        except Exception:
            continue
        for it in items:
            seen += 1
            nm = (it.get("name") or "")
            # strip a trailing ".amxd" for the compare; browser may or may not show it
            base = nm[:-5] if nm.lower().endswith(".amxd") else nm
            if base.lower() == needle_exact_lower and it.get("is_loadable"):
                return it["uri"]
            if it.get("is_folder") and d < 6:
                q.append((path + "/" + nm, d + 1))
    return None


def device_names(c, i):
    """Exact device name list for a track (or master at -1). Returns None on error
    (e.g. a group track the Remote Script can't introspect) with the error string."""
    try:
        ti = c.send("get_track_info", {"track_index": i})
        return [(d.get("name") if isinstance(d, dict) else d) for d in ti.get("devices", [])], ti.get("name", "?"), None
    except Exception as e:
        return None, "?", str(e)


def classify(names):
    has_one = ONEPOLE in names
    has_bi = BIQUAD in names
    return has_one, has_bi


def _label(ref):
    if ref == -1:
        return "master"
    if isinstance(ref, str):
        return ref                       # "return:N"
    return f"track {ref}"


def discover(c):
    """Classify every node. Post-resolver-fix, groups + master (-1) + returns
    ("return:N") introspect like any track — no more 'manual' bucket."""
    n = c.send("get_session_info").get("track_count", 0)
    try:
        nret = int(c.send("get_return_tracks").get("count", 0))
    except Exception:
        nret = 0
    refs = list(range(n)) + [-1] + [f"return:{k}" for k in range(nret)]
    print(f"session: {n} tracks + master + {nret} returns\n")
    plan = {"migrate": [], "done": [], "neither": [], "errors": []}
    for i in refs:
        label = _label(i)
        names, tname, err = device_names(c, i)
        if names is None:
            plan["errors"].append((i, err))
            print(f"  {label:11s} ERROR: {err[:60]}")
            continue
        has_one, has_bi = classify(names)
        if has_one:
            plan["migrate"].append(i)
            extra = " (+biquad already! both present — will de-dup)" if has_bi else ""
            print(f"  {label:11s} [{tname[:28]:28s}] onepole -> migrate{extra}")
        elif has_bi:
            plan["done"].append(i)
        else:
            plan["neither"].append(i)
    print(f"\nPLAN: migrate {len(plan['migrate'])} | already biquad {len(plan['done'])} | "
          f"no-ears {len(plan['neither'])} | errors {len(plan['errors'])}")
    if plan["neither"]:
        print(f"  no-ears (no hub yet, or CalTone scaffolding): {plan['neither']}")
    if plan["errors"]:
        print(f"  errors (unexpected — investigate): {[i for i,_ in plan['errors']]}")
    return plan


def main():
    mode = "--swap" if "--swap" in sys.argv else "--verify" if "--verify" in sys.argv else "--discover"
    with LiveClient(timeout=OP_TIMEOUT) as c:
        one_uri = find_uri(c, ONEPOLE.lower())
        bi_uri = find_uri(c, BIQUAD.lower())
        print(f"onepole uri: {one_uri}")
        print(f"biquad  uri: {bi_uri}\n")
        if not bi_uri:
            print("Biquad device not found in browser — is it in the User Library?")
            return 1

        plan = discover(c)

        if mode == "--discover":
            print("\nread-only. Re-run with --swap to execute (SAVE A BACKUP FIRST).")
            return 0

        if mode == "--verify":
            bad = []
            for i in plan["migrate"]:            # any still-onepole leaf track = not migrated
                names, tname, err = device_names(c, i)
                if names is None:
                    continue
                has_one, has_bi = classify(names)
                if has_one or not has_bi:
                    bad.append((i, tname))
            if bad:
                print(f"\nNOT fully migrated ({len(bad)} leaf tracks still wrong): {bad}")
            else:
                print(f"\nAll {len(plan['done'])} nodes (tracks + groups + master + returns) "
                      f"are biquad-only.")
                if plan["errors"]:
                    print(f"  unexpected errors to check: {[i for i,_ in plan['errors']]}")
            return 0

        # --- --swap: every node not yet biquad-only. Post-resolver-fix this covers
        #   regular tracks, groups, master (-1), and returns ("return:N") uniformly.
        #   migrate = still has onepole; neither = orphaned (onepole gone, biquad
        #   load failed). delete step is a no-op when onepole is already gone.
        #   Sort by str() so mixed int/str refs (-1, 3, "return:0") order safely.
        targets = sorted(set(plan["migrate"]) | set(plan["neither"]), key=str)
        print(f"\n[swap] migrating {len(targets)} nodes "
              f"({len(plan['migrate'])} onepole + {len(plan['neither'])} orphaned) "
              f"— tracks + groups + master + returns.")
        ok, fail = 0, []
        for k, i in enumerate(targets, 1):
            try:
                names, tname, err = device_names(c, i)
                if names is None:
                    fail.append((i, "introspect")); continue
                has_one, has_bi = classify(names)
                if has_bi and not has_one:
                    ok += 1; continue                # already migrated (resumable)
                # delete EVERY exact-onepole instance (fresh index each time; guards dupes)
                guard = 0
                while names is not None and ONEPOLE in names and guard < 5:
                    idx = names.index(ONEPOLE)
                    c.send("delete_device", {"track_index": i, "device_index": idx})
                    time.sleep(THROTTLE_S)
                    names, tname, err = device_names(c, i)
                    guard += 1
                # load biquad if not already present
                if names is not None and BIQUAD not in names:
                    r = c.send("load_browser_item", {"track_index": i, "item_uri": bi_uri})
                    after = r.get("devices_after", [])
                    time.sleep(THROTTLE_S)
                else:
                    after = names or []
                if BIQUAD in after and ONEPOLE not in after:
                    ok += 1
                else:
                    fail.append((i, f"after={after}"))
            except Exception as e:
                # transient timeout / busy → record and move on; a re-run resumes it
                fail.append((i, str(e)[:40]))
            if k % 10 == 0 or k == len(targets):
                print(f"  [swap] {k}/{len(targets)} ({ok} ok, {len(fail)} fail)", flush=True)
        print(f"\n[swap] DONE. migrated {ok}/{len(targets)} nodes. failures: {fail}")
        if plan["errors"]:
            print(f"[swap] {len(plan['errors'])} nodes errored on introspect "
                  f"(investigate): {[i for i,_ in plan['errors']]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
