# SIM — Ableton Capabilities Research (Re-aimed for the MiniCPM-o / duplex plan)

**Prepared for:** Studio Interaction Model (SIM) — full-duplex studio collaborator
**Date:** 2026-07-06
**Supersedes framing of:** `EXTENSIONS_SDK_RESEARCH.md` (still accurate about the SDK, but the SDK is now a *minor* player — see §7).

---

## 0. TL;DR — what changed and where the leverage actually is

Given the pivot (MiniCPM-o 4.5 omni backbone brings its own vision + audio encoders; SIM is a **push / duplex / 25 Hz frame-stream** system; Lane 2 mix-perception is built on a **calibrated biquad** M4L bank), the research target moves off "how do we render audio for a CNN" and onto your stated blocker:

> **The Remote Script can't reach devices on group / return / master tracks — exactly the nodes where masking analysis lives.**

Three findings, in priority order:

1. **This blocker is a Remote Script *implementation* bug, not an Ableton platform limit.** I read your `AbletonMCP_Extended/__init__.py`. Every device/mixer handler resolves tracks with the same `song.tracks[index]` pattern plus a `track_index < 0` guard, which *structurally* excludes the master (`song.master_track`, index `-1`) and all return tracks (`song.return_tracks`). Separately, `_get_track_info` unconditionally iterates `clip_slots` and `arrangement_clips`, which **Live itself** refuses on group/return/master — that's the literal source of your `"Main, Group and Return Tracks have no arrangement clips"` error. The LOM fully supports devices on all four track types. **Fix the resolver and the blocker disappears.** (§2–§4)

2. **Live 12.2/12.3 added a cleaner device-deploy path you can use right now:** `Track.insert_device` and `Chain.insert_device` (programmatic insert, assigns the default preset). Combined with the always-available `select-track + browser.load_item` pattern, this replaces your manual hand-swap of the 7 group/master devices — no GUI keystrokes. (§5)

3. **Your M4L saturation is expected and largely self-inflicted by instance count.** Each M4L instance carries its own CPU/RAM cost (no sharing), and M4L is single-core-per-track. But your masking is computed **comparatively on groups + master**, so you almost certainly don't need a biquad device on all 66 leaf tracks. Analyzing at group + master (+ a few key buses) drops you from ~73 instances to ~7–15 and makes the saturation problem mostly evaporate. (§6)

**The Extensions SDK — the subject of the previous report — is a poor fit for SIM's core loop** (right-click-trigger-only, cannot load M4L devices, not real-time). It survives only as an optional offline audit tool. (§7)

---

## 1. Re-framing: what SIM actually needs from Ableton

| SIM need | Nature | Right substrate |
|---|---|---|
| Continuous per-track/group/master **mix features** at 25 Hz | Real-time metering of audio | **M4L** (only real-time option) → OSC 9880 |
| **Read/act on** devices & params across *all* track types incl. group/return/master | Control-plane, event-driven | **Remote Script + LOM** (9877) — *the blocker lives here* |
| **Deploy** the analysis device onto every relevant node | Setup / provisioning | **LOM `insert_device`** or `browser.load_item` |
| Raw stems (Lane 1) & screen (Lane 3b) | Streaming into backbone encoders | MiniCPM-o native paths (deferred) |
| Focus state (Lane 3a) | Symbolic selection readout | LOM `song.view.selected_track` / `selected_parameter` |

Everything that hurts today is in the **control-plane / provisioning** rows — i.e. the LOM/Remote Script, not a missing Ableton feature. That is the good news: no platform capability is blocking you.

---

## 2. Root-cause of the group/return/master blocker (from your code)

Confirmed by direct read of `harness/AbletonMCP_Extended/__init__.py`:

**Cause A — track resolution is `song.tracks`-index-only.** Every handler (`_get_device_parameters` L1424, `_set_device_parameter` L1469, `_set_track_volume` L1520, `_set_track_pan` L1537, `_set_send_level` L1553, `_set_track_mute`, `_set_track_solo`, `_get_track_info` L623, …) opens with:

```python
if track_index < 0 or track_index >= len(self._song.tracks):
    raise IndexError("Track index out of range")
track = self._song.tracks[track_index]
```

- **Master** is `self._song.master_track`. It is *not* in `song.tracks`, and the `-1` convention you pass is rejected by `track_index < 0`. → unreachable.
- **Return tracks** are `self._song.return_tracks[j]`. Also *not* in `song.tracks`. → unreachable by these handlers (you have read-only `_get_return_tracks` at L1597, but the device/mixer *write* path never uses it).
- **Group tracks** *are* in `song.tracks` (they're foldable tracks, `is_foldable == True`), so device ops on groups actually work through the param handlers — but discovery via `_get_track_info` breaks (Cause B), so the agent can't *find* the group's devices.

**Cause B — `_get_track_info` reads clip collections that don't exist on non-regular tracks.** Lines 632–661 iterate `track.clip_slots[:8]` and `track.arrangement_clips[:20]` unconditionally. Master and return tracks have **no** clip slots and **no** arrangement clips; group tracks have no arrangement clips. Live raises `RuntimeError: Main, Group and Return Tracks have no arrangement clips` on access — your exact reported error. The `hasattr(track, 'arrangement_clips')` check at L652 passes (the attribute exists) but *iterating* it throws.

**Verdict:** implementation gap. The LOM's `Track` class explicitly models audio / MIDI / **return** / **master** tracks, and group membership is exposed via `group_track` / `is_foldable`. Devices and `mixer_device` are available on all track types. Your own code already touches `self._song.master_track.mixer_device.volume` (L571) and enumerates `self._song.return_tracks` (L1601) — the collections are right there; the write path just never wired them in.

---

## 3. The fix — a unified track resolver

Introduce one resolver and route **every** handler through it. Extend the string-based track references you already support (e.g. `"track_index": "MIDI"`) to a typed scheme that spans all four collections.

```python
def _resolve_track(self, ref):
    """Resolve a track reference to a Live track across ALL collections.
    Accepts: int index into song.tracks; -1 for master; or strings:
      'master'/'main', 'return:0' or a return's name, a group/track name.
    """
    song = self._song
    # Integer index (regular + group tracks live here; -1 == master)
    if isinstance(ref, int):
        if ref == -1:
            return song.master_track
        if 0 <= ref < len(song.tracks):
            return song.tracks[ref]
        raise IndexError("Track index out of range")

    s = str(ref).strip()
    low = s.lower()
    if low in ("master", "main", "-1"):
        return song.master_track
    if low.startswith("return:") or low.startswith("r:"):
        j = int(s.split(":", 1)[1])
        if 0 <= j < len(song.return_tracks):
            return song.return_tracks[j]
        raise IndexError("Return track index out of range")
    # Name match across regular/group, then returns, then master
    for t in song.tracks:
        if t.name == s:
            return t
    for t in song.return_tracks:
        if t.name == s:
            return t
    if song.master_track.name == s:
        return song.master_track
    raise KeyError("No track named %r" % s)


def _track_kind(self, track):
    song = self._song
    if track is song.master_track:
        return "master"
    if track in song.return_tracks:
        return "return"
    if getattr(track, "is_foldable", False):
        return "group"
    return "regular"
```

Then make `_get_track_info` clip-safe (only regular tracks have playable clips):

```python
kind = self._track_kind(track)
clip_slots, arrangement_clips = [], []
if kind == "regular":
    for i, slot in enumerate(track.clip_slots[:8]):
        ...  # existing logic
    try:
        for i, clip in enumerate(track.arrangement_clips[:20]):
            ...  # existing logic
    except RuntimeError:
        pass  # belt-and-suspenders: Live guards these on non-regular tracks
```

Because `devices`, `mixer_device.volume/panning/sends`, `mute`, `solo` are uniform across all track kinds, **once resolution and clip-guarding are fixed, list / add / delete / enable / parameter operations on group / return / master "just work."** Note: `arm` and clip firing are *not* valid on master/return — gate those by `kind`.

> **Per your project rules:** this is a behavioral change to the Remote Script surface, so it warrants tests. A Tier-1-style unit test (mock `song` with `.tracks`, `.return_tracks`, `.master_track`, a foldable group) can assert the resolver returns the right object for `-1`, `"master"`, `"return:0"`, a group name, and that `_get_track_info` no longer throws on non-regular tracks. Happy to write both the resolver refactor and the tests on request.

---

## 4. Canonical LOM addressing cheat-sheet (verified)

| Track type | Where it lives | Devices | Clip slots | Arr. clips | `arm` |
|---|---|---|---|---|---|
| Regular audio/MIDI | `song.tracks[i]` | ✅ `.devices` | ✅ | ✅ | ✅ |
| **Group** | `song.tracks[i]` where `is_foldable` | ✅ `.devices` | ✅ (scene launch) | ❌ (raises) | ❌ |
| **Return** | `song.return_tracks[j]` | ✅ `.devices` | ❌ | ❌ | ❌ |
| **Master/Main** | `song.master_track` | ✅ `.devices` | ❌ | ❌ | ❌ |

Group membership of a regular track: `track.group_track` (returns the group Track, or id 0 / `None` if ungrouped). Fold state via `is_foldable` + `fold_state`. `mixer_device` (volume, panning, sends, and on master `cue_volume`/`crossfader`) is present on every kind.

---

## 5. Deploying the analysis device onto group/master (no more hand-swaps)

Two programmatic paths, both avoiding GUI keystrokes:

**Path A — `Track.insert_device` (new in Live 12.2/12.3).** The M4L/LOM API now exposes `Track.insert_device` and `Chain.insert_device`, which insert a device and assign its default preset. This is the cleanest option **if** it accepts a Max Audio Effect / browser device (not only Live-native devices) and works on master/return targets. Both are unconfirmed in the public notes → **verify empirically** (5-minute test: resolve `song.master_track`, call `insert_device`, confirm your `.amxd` lands). If it only takes native devices, use Path B.

**Path B — select + `browser.load_item` (always works, loads M4L).** The canonical control-surface pattern:

```python
song.view.selected_track = target_track          # master/return/group all selectable
item = <browser item for "BAP Labs Mix Analysis Hub (Per-Track Biquad)">
app.browser.load_item(item)                       # loads onto the selected track
```

`load_item` loads into the **currently selected track**, with insertion-position control (0 = end, 1 = left of selected device, 2 = right). Master, return, and group tracks can all be set as `selected_track`, so this deploys your `.amxd` to exactly the 7 group/master nodes programmatically — replacing the manual swap. To locate the browser item, walk `app.browser.user_library` / the Audio Effects tree once and cache the item reference for your device name.

Either path, wrapped in your existing migration script (`swap_ears_to_biquad.py`), turns the group/master deployment into an automated pass like the 66 leaf tracks.

---

## 6. The M4L saturation problem — cause and mitigations (verified)

**Why it happens (confirmed):** each M4L device instance has its own CPU/RAM cost — instances do **not** share processing; M4L runs single-core-per-track and is not multiprocessor-capable, so a bank of analysis devices with `live.remote~`/FFT/biquad chains compounds linearly and eventually saturates Max's headroom (your "cumulative Max saturation, solved by a Live restart"). This is inherent to M4L, not a bug you can patch away — you manage it by **reducing instance count and per-instance cost.**

**Mitigations, highest-leverage first:**

1. **Match instance count to the analysis you actually consume.** Lane 2 masking is comparative on **groups + master** (kick-vs-bass, synth-vs-hats), and your FrameEmitter canonicalizes to **8 roles** regardless of track count. That strongly implies you don't need a biquad instance on all 66 leaf tracks — analyze at the **role/group + master** level (≈7–15 instances). This alone likely removes the saturation ceiling. If you still want per-source detail for a few critical elements, add leaf instances selectively, not universally.
2. **Route to shared analysis nodes.** Return/bus tracks let many sources share one effect instance — send role-grouped audio to a small set of analysis returns instead of instancing per leaf track.
3. **Trim per-instance cost.** One biquad bandpass per band × N bands per instance is the dominant load; consider a lighter shared-topology (e.g., a single multi-output analysis object) or decimate the internal analysis rate where the 25 Hz frame clock doesn't need more.
4. **Use Live 12's per-track Performance Impact indicators** to find the heaviest nodes, and freeze/disable non-analysis devices during analysis passes.
5. **Keep the staged-load + restart** only as a fallback; with (1) it should rarely trigger.

**Strategic note:** M4L remains the *only* real-time metering substrate (the LOM exposes no live signal levels, and the Extensions SDK is explicitly non-real-time). So keep M4L for the live Lane-2 stream — just run far fewer, leaner instances. Longer term, once MiniCPM-o's **Lane 1 (raw audio)** path is live, some of what the biquad bank infers symbolically may be better handled by feeding stems to the backbone's native audio encoder — worth revisiting the per-track-M4L substrate at that point rather than scaling it up now.

---

## 7. Where the Extensions SDK still fits under SIM (small, optional)

The previous report's SDK analysis is still technically correct, but the pivot demotes it:

- **Cannot stream** — right-click-trigger-only, no headless/event/launch invocation. Wrong shape for a 25 Hz duplex loop.
- **Cannot deploy your analysis device** — `insertDevice` is Live-native-only; it will not load a Max Audio Effect. So it can't help provision the biquad bank.
- **Not real-time** — no live metering; can't feed Lane 2.

What it *can* still do, if ever useful:
- **Offline audit/repair tool** (a right-click "verify Mix Analysis Hub is present + enabled on every group/return/master"): the SDK cleanly exposes `song.returnTracks`, `song.mainTrack`, `track.groupTrack`, `track.devices`, and `DeviceParameter.get/setValue` across all track types — a tidy consistency-checker the user runs by hand.
- **Lane 1 / dataset capture:** `renderPreFxAudio` (audio tracks) is a clean stem-render primitive that pairs with Live 12.3's new **stem separation** and **bounce-groups / Paste Bounced Audio** for building your `.als` raw→mastered training corpus. Nice-to-have, not on the critical path.

Recommendation: **don't invest in the SDK for SIM's core.** Park it as an optional utility.

---

## 8. Arrangement vs Session (your open question)

For SIM, arrangement editing is not on the perception critical path, so this is minor. State of play: session clip ops are solid on regular tracks; arrangement-clip *reading* works on regular tracks (and is the code that throws on group/return/master — fixed by §3's guard); arrangement clip *creation/editing* via the Remote Script is limited (you use the GUI-automation `automator_bridge.py` for split/consolidate/etc.). The Extensions SDK can write arrangement MIDI/audio clips natively but only via right-click. None of this blocks SIM; revisit only if the agent needs to *compose to the arrangement* later.

---

## 9. Ranked next steps

1. **P0 — Ship the unified `_resolve_track` + clip-access guard** (§3). Unblocks device introspection/control on group/return/master, which is where masking lives. Add Tier-1 tests. *This is the whole blocker.*
2. **P1 — Automate M4L deploy to the 7 group/master nodes** via `Track.insert_device` (verify) or `select + browser.load_item` (§5). Retire the hand-swap.
3. **P1 — Cut analysis-device count to group + master (+ key buses)** (§6.1). Kills saturation; aligns with your 8-role canonicalization.
4. **P2 — Expose the new nodes through the MCP tool surface** (get/set device params, enable, mixer) using resolver-based addressing, so the agent can act on groups/master, not just read them.
5. **P3 (optional) — SDK right-click audit tool + `renderPreFxAudio` for Lane 1 / `.als` dataset** (§7).

---

## 10. Questions to validate empirically (fast)

- Does `Track.insert_device` accept a **Max Audio Effect** (your `.amxd`) and work on **master/return** targets? (If not → Path B.)
- After the resolver fix, do `get_device_parameters` / `set_device_parameter` behave correctly on `song.master_track` and `song.return_tracks[j]` (they should — same `mixer_device`/`devices` API)?
- At group+master-only instancing, does Max saturation stop recurring across a full session load?
- Does `song.view.selected_track = song.master_track` reliably select the master for `load_item` on your Live build?

---

## 11. Sources

**Local (authoritative for the diagnosis):** `harness/AbletonMCP_Extended/__init__.py` (`_get_track_info` L623, device/mixer handlers L1424–1594, return/master helpers L1597–1624); project brief provided by author (SIM strategy summary, 2026-07-06).

**Public (LOM / API / performance — verified):**
- [LOM — The Live Object Model (Cycling '74 / Max 8 docs)](https://docs.cycling74.com/legacy/max8/vignettes/live_object_model)
- [Controlling Live using Max for Live — Ableton](https://help.ableton.com/hc/en-us/articles/5402681764242-Controlling-Live-using-Max-for-Live)
- [Live 12 Release Notes — Ableton](https://www.ableton.com/en/release-notes/live-12/) (Track.insert_device / Chain.insert_device; LOM additions)
- [Ableton Live 12.3 is here — Ableton blog](https://www.ableton.com/en/blog/live-12-3-is-here/) (stem separation, bounce groups, LOM plug-in-window control)
- [Optimizing CPU-Intensive Devices — Ableton](https://help.ableton.com/hc/en-us/articles/12911009486108-Optimizing-CPU-Intensive-Devices)
- [M4L is a CPU hog? — Cycling '74 forum](https://cycling74.com/forums/m4l-is-a-cpu-hog) (per-instance cost, single-core behavior)
- [AbletonOSC: A unified control API for Ableton Live (NIME 2023)](https://nime.org/proceedings/2023/nime2023_60.pdf)
- [Working with the Browser — Live 12 Manual](https://www.ableton.com/en/live-manual/12/working-with-the-browser/) (browser load / insertion position)
