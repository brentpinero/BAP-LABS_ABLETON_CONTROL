"""
sub_follower_core.py — the pure logic behind the Sub Follower: one Serum sub track
that plays a mono, octave-folded line derived from every MIDI track in the bass group.

The LIVE note path (gate -> lowest-note priority -> octave fold) runs inside the M4L
devices as plain Max objects (build_sub_follower_device.py); nothing here touches
notes in real time. This module is the offline side, used by sub_follower_provision.py:

  * AUTO OCTAVE — score every candidate fold floor against the bass notes and pick
    the one that keeps the sub in its sweet spot with the fewest octave jumps.
    mono_line() mirrors the device's lowest-note rule so the score reflects what the
    sub will actually play.
  * TAP PLANNING — which sources need a new tap device on the hub track.

Pure Python, no Ableton: tests in test_sub_follower.py.
"""

# Sub sweet spot in MIDI numbers (Ableton names 60 "C3", so 28 = E0 = 41.2 Hz and
# 38 = D1 = 73.4 Hz). Mixing guidance puts sub fundamentals around 40-60 Hz and warns
# below ~40 Hz; these are tunable defaults, not hard rules.
BAND_LO = 28
BAND_HI = 38
FLOOR_MIN = 24          # candidate fold floors: C0 (32.7 Hz) ..
FLOOR_MAX = 31          # .. G0 (49.0 Hz)
W_RANGE = 1.0           # weight: time spent outside the sweet spot
W_JUMP = 0.5            # weight: melodic steps the fold turns into octave leaps
EPS = 1e-6

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def fold(pitch, floor):
    """Fold any pitch into the one-octave window [floor, floor + 11]."""
    return floor + (pitch - floor) % 12


def note_hz(pitch):
    return 440.0 * 2 ** ((pitch - 69) / 12.0)


def note_name(pitch):
    """Ableton's naming: MIDI 60 is C3."""
    return "%s%d" % (NOTE_NAMES[pitch % 12], pitch // 12 - 2)


def mono_line(notes):
    """Reduce overlapping notes from all sources to the mono line the device plays:
    at every moment the LOWEST sounding pitch wins.
    notes: [{"pitch", "start", "duration"}] in absolute beats. Returns the same shape,
    adjacent same-pitch segments merged."""
    notes = [n for n in notes if n["duration"] > EPS]
    times = sorted({t for n in notes for t in (n["start"], n["start"] + n["duration"])})
    line = []
    for t0, t1 in zip(times, times[1:]):
        if t1 - t0 <= EPS:
            continue
        held = [n["pitch"] for n in notes
                if n["start"] <= t0 + EPS and n["start"] + n["duration"] >= t1 - EPS]
        if not held:
            continue                                  # silence between notes
        low = min(held)
        last = line[-1] if line else None
        if last and last["pitch"] == low and abs(last["start"] + last["duration"] - t0) <= EPS:
            last["duration"] = t1 - last["start"]
        else:
            line.append({"pitch": low, "start": t0, "duration": t1 - t0})
    return line


def score_floor(line, floor):
    """Cost of one fold floor for a mono line. Lower is better.
      range_cost: duration-weighted semitones outside [BAND_LO, BAND_HI], per beat.
      jump_cost:  share of note-to-note moves the fold seam turns from a step into a
                  leap (more than a tritone)."""
    total = outside = 0.0
    moves = jumps = 0
    prev = None
    for seg in line:
        p = fold(seg["pitch"], floor)
        total += seg["duration"]
        outside += max(BAND_LO - p, p - BAND_HI, 0) * seg["duration"]
        if prev is not None and p != prev:
            moves += 1
            jumps += abs(p - prev) > 6
        prev = p
    range_cost = outside / total if total > 0 else 0.0
    jump_cost = jumps / moves if moves else 0.0
    return {"floor": floor, "range_cost": range_cost, "jump_cost": jump_cost,
            "cost": W_RANGE * range_cost + W_JUMP * jump_cost}


def choose_floor(notes):
    """Best fold floor for the given source notes; ties go to the floor nearest the
    bottom of the sweet spot. Returns (floor, scores) with a score per candidate."""
    line = mono_line(notes)
    scores = [score_floor(line, f) for f in range(FLOOR_MIN, FLOOR_MAX + 1)]
    best = min(scores, key=lambda s: (round(s["cost"], 6), abs(s["floor"] - BAND_LO)))
    return best["floor"], scores


def find_sources(tracks, group_needle="bass", exclude=()):
    """The MIDI tracks the sub should follow: every regular MIDI track inside the bass
    group, at any nesting depth.
      tracks: get_track_info dicts (index, name, kind, group_id, is_midi_track)
      group_needle: case-insensitive substring of the group track's name
      exclude: track indices to leave out (the sub track, the hub track)
    Returns (group_index, [(track_index, name)]) in session order."""
    groups = [t for t in tracks
              if t.get("kind") == "group" and group_needle.lower() in t["name"].lower()]
    if not groups:
        raise ValueError("no group track with %r in its name" % group_needle)
    group = groups[0]["index"]
    sources = [(t["index"], t["name"]) for t in tracks
               if t.get("kind") == "regular" and t.get("is_midi_track")
               and t["index"] not in exclude and group in ancestors(tracks, t["index"])]
    return group, sources


def ancestors(tracks, index):
    """Indices of the group tracks containing track `index`, innermost first."""
    parent = {t["index"]: int(t.get("group_id", -1)) for t in tracks}
    chain = []
    while parent.get(index, -1) != -1 and parent[index] not in chain:
        index = parent[index]
        chain.append(index)
    return chain


def find_track(tracks, ref):
    """Index of the track named `ref` (exact, then case-insensitive substring), or
    `ref` itself when it is already an index. Raises ValueError when nothing matches."""
    if isinstance(ref, int) or str(ref).lstrip("-").isdigit():
        return int(ref)
    for exact in (True, False):
        for t in tracks:
            name = t["name"]
            if name == ref if exact else str(ref).lower() in name.lower():
                return t["index"]
    raise ValueError("no track named %r" % ref)


def plan_taps(existing, wanted):
    """Match the taps already on the hub track to the sources that should be followed.
    Matching is by (name, occurrence), the same contract as the routing resolver, so
    duplicate track names stay distinct and a tap's Follow automation keeps its source.
      existing: source name of each tap, in device order
      wanted:   [(track_index, name)] sources in session order
    Returns (keep, add, stale):
      keep  = [(tap_position, track_index, name)] taps to (re)route
      add   = [(track_index, name)] sources needing a new tap
      stale = [tap_position] taps whose source is gone (left in place: removing a
              tap would drop its automation; teardown removes them)."""
    free = {}
    for pos, name in enumerate(existing):
        free.setdefault(name, []).append(pos)
    keep, add = [], []
    for idx, name in wanted:
        if free.get(name):
            keep.append((free[name].pop(0), idx, name))
        else:
            add.append((idx, name))
    stale = sorted(pos for positions in free.values() for pos in positions)
    return keep, add, stale
