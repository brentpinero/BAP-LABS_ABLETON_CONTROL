"""
calibrate_live.py — Tier 2 live compare: does the Max onepole~ device agree with
the FFT ruler?

Reads the live per-track spectrum the M4L device is emitting (from live_ears.json)
for one track, and compares it to the expected band fractions computed by
calibration_tones.py. Because onepole~ (6 dB/oct) and the FFT ruler (near
brick-wall) have different filter shapes, we DON'T demand equal fractions — we
check the three things that actually prove the live path is trustworthy:

  1. dominant band matches  — the tone lands in the right named band live.
  2. home-band majority     — that band still holds the bulk of the energy.
  3. shape correlation      — the whole 7-band curve tracks the reference (Pearson).

Runbook (Ableton open, `python run_harness.py ears` running, Mix Analysis Hub on
the track, tone WAV playing/looping on a track you rename to match):

  python harness/calibration_tones.py               # once: make WAVs + expected.json
  python harness/calibrate_live.py CalTone sine_1khz # per tone: capture + compare

Omit the tone label to just print the live curve + its best-correlated reference.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import bands

_ROOT = Path(__file__).resolve().parent.parent
_SNAP = _ROOT / "sandbox_sessions" / "live_ears.json"
_EXPECTED = _ROOT / "sandbox_sessions" / "calibration" / "expected.json"

DOMINANT_MIN = 0.40    # onepole leaks more than FFT → looser than Tier 1's 0.80
CORR_MIN = 0.80        # spectral-shape agreement


def _pearson(a, b):
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    return num / (da * db) if da > 0 and db > 0 else 0.0


def _live_bands(track_query: str):
    if not _SNAP.exists():
        sys.exit(f"no live snapshot at {_SNAP} — start `python run_harness.py ears`.")
    snap = json.loads(_SNAP.read_text())
    age = time.time() - snap.get("written_at", 0)
    if age > 3.0:
        sys.exit(f"snapshot is stale ({age:.0f}s) — is the ears daemon running + audio playing?")
    tracks = snap.get("per_track", {}).get("tracks", {})
    q = track_query.lower()
    hits = [(tid, t) for tid, t in tracks.items() if q in str(t.get("name", "")).lower()]
    if not hits:
        names = ", ".join(sorted(str(t.get("name")) for t in tracks.values())) or "(none)"
        sys.exit(f"no track matching {track_query!r}. Live tracks: {names}")
    if len(hits) > 1:
        print(f"[warn] {len(hits)} tracks match {track_query!r}; using first "
              f"({hits[0][1].get('name')}).")
    return hits[0][1]


def main(argv):
    if not _EXPECTED.exists():
        sys.exit("no expected.json — run `python harness/calibration_tones.py` first.")
    if len(argv) < 1:
        sys.exit("usage: python calibrate_live.py <track-name> [tone-label]")
    exp = json.loads(_EXPECTED.read_text())
    names = exp["band_names"]

    track = _live_bands(argv[0])
    live = [float(x) for x in track.get("bands", [])]
    if len(live) != len(names):
        sys.exit(f"live spectrum has {len(live)} bands, expected {len(names)} "
                 f"(scheme mismatch: device={track.get('band_scheme')} vs {exp['scheme']}).")
    live_dom = names[live.index(max(live))]

    def show(label):
        e = exp["tones"][label]
        corr = _pearson(live, e["fractions"])
        home = e["dominant_band"]
        home_frac = live[names.index(home)]
        dom_ok = live_dom == home
        home_ok = home_frac >= DOMINANT_MIN or e["kind"] == "pink"
        corr_ok = corr >= CORR_MIN
        passed = dom_ok and home_ok and corr_ok
        print(f"\n=== {label}  ({'PASS' if passed else 'FAIL'}) ===")
        print(f"  expected dominant : {home}")
        print(f"  live dominant     : {live_dom}   {'ok' if dom_ok else 'MISMATCH'}")
        print(f"  live home fraction: {home_frac:.2f}  (min {DOMINANT_MIN})  "
              f"{'ok' if home_ok else 'LOW'}")
        print(f"  shape correlation : {corr:.3f}   (min {CORR_MIN})  "
              f"{'ok' if corr_ok else 'LOW'}")
        print("  band   " + "  ".join(f"{n:>8s}" for n in names))
        print("  live   " + "  ".join(f"{x:8.3f}" for x in live))
        print("  ref    " + "  ".join(f"{x:8.3f}" for x in e["fractions"]))
        return passed

    if len(argv) >= 2:
        ok = show(argv[1])
        sys.exit(0 if ok else 1)

    # no label → print live curve + best-correlated reference tone
    best = max(exp["tones"], key=lambda k: _pearson(live, exp["tones"][k]["fractions"]))
    print(f"live dominant band: {live_dom}")
    print(f"best-correlated reference tone: {best}")
    show(best)


if __name__ == "__main__":
    main(sys.argv[1:])
