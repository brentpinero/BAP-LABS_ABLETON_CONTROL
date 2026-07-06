"""
track_resolver.py — canonical track-reference resolution across ALL Live track
collections (regular, group, return, master).

This is the reference implementation of the logic that the AbletonMCP Remote Script
inlines as `_resolve_track` / `_track_kind`. The Remote Script keeps its own inline
copy (so it stays self-contained inside Live's interpreter with no extra import on
Live's path), but the LOGIC is defined and unit-tested HERE against a mock song —
so the resolver spec has coverage without needing Ableton running. Keep the two in
sync: any change to the resolution rules should land in both.

Reference convention (LLM/harness address any node by NAME; these are the wire ints/strings):
  - int i in [0, len(tracks))  -> song.tracks[i]        (regular AND group tracks)
  - int -1  /  "master" / "main"  -> song.master_track
  - "return:N" / "r:N" / a return's name  -> song.return_tracks[N]
  - any other string  -> name match across regular/group, then returns, then master
"""

from __future__ import annotations


def resolve_track(song, ref):
    """Resolve a track reference to a Live track across all collections.
    `song` needs `.tracks`, `.return_tracks`, `.master_track`."""
    if isinstance(ref, bool):
        raise TypeError("track reference cannot be a bool")
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
    if low.lstrip("-").isdigit():
        return resolve_track(song, int(s))
    for t in song.tracks:
        if t.name == s:
            return t
    for t in song.return_tracks:
        if t.name == s:
            return t
    if song.master_track.name == s:
        return song.master_track
    raise KeyError("No track named %r" % s)


def track_kind(song, track):
    """Classify a resolved track: 'master' | 'return' | 'group' | 'regular'."""
    if track is song.master_track:
        return "master"
    for rt in song.return_tracks:
        if track is rt:
            return "return"
    if getattr(track, "is_foldable", False):
        return "group"
    return "regular"
