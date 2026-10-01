"""
device_io_routing.py — the canonical source-resolution logic for device audio-input
routing (Live 10+ DeviceIO), mirrored INLINE by the AbletonMCP Remote Script's
_set_device_io (the Remote Script cannot import repo modules from the app
bundle). Pure Python so it is testable without Ableton; if this and the Remote
Script drift, fix the Remote Script to match THIS.

The same handler (and so the same contract) serves set_device_midi_io, which points a
device's midi_inputs / midi_outputs IO at a track; only the DeviceIO list differs.

Resolution contract (identical to _set_track_input_routing):
  * source_index (PREFERRED): song-index of the source track, resolved by
    (name, occurrence) so DUPLICATE track names pick the RIGHT routing option —
    the k-th track named X in session order maps to the k-th 'X' option.
  * source_name: display_name match, exact first then substring — for returns /
    master, which have no song.tracks index (their names are unique).
"""


def pick_option(options, name):
    """Exact display_name match first, then case-insensitive substring."""
    for o in options:
        if str(o.display_name) == name:
            return o
    for o in options:
        if name.lower() in str(o.display_name).lower():
            return o
    return None


def resolve_source(options, tracks, source_index=None, source_name=""):
    """Pick the routing option for a source. Returns (option, ambiguous).
    Raises IndexError on a bad source_index, ValueError when nothing matches."""
    chosen = None
    ambiguous = False
    if source_index is not None:
        si = int(source_index)
        if si < 0 or si >= len(tracks):
            raise IndexError("source_index out of range")
        source_name = str(tracks[si].name)
        occ = sum(1 for t in tracks[:si + 1] if str(t.name) == source_name)
        exact = [o for o in options if str(o.display_name) == source_name]
        if len(exact) >= occ:
            chosen = exact[occ - 1]
        elif exact:
            chosen = exact[0]           # fewer routable than tracks -> best effort
            ambiguous = True
    if chosen is None:
        chosen = pick_option(options, source_name)
    if chosen is None:
        avail = [str(rt.display_name) for rt in options]
        raise ValueError("No routing source '%s'; available: %s" % (source_name, avail))
    return chosen, ambiguous
