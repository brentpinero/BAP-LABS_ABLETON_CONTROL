"""
test_tracktion_target.py — the Tracktion Engine target through the Phase 0 probes.

Needs the built `tracktion_probe` binary (see tracktion_target.py); skips when it
is absent, like the repo's other hardware-gated tests. The assertions are the
engine-agnostic sanity floor, not the spec gates: a candidate may legitimately
differ from the reference engine (that difference IS the measurement), but it
must play the clip at the right level, time and rate.
Run: python daw_bench/test_tracktion_target.py (or pytest).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import profile  # noqa: E402
import tracktion_target as tt  # noqa: E402


def test_tracktion_probe_plays_the_probes():
    if tt.find_binary() is None:
        print("SKIP: tracktion_probe not built")
        return
    with tempfile.TemporaryDirectory() as d:
        prof = profile.run_probes(tt.TracktionTarget(48000, keep_dir=Path(d) / "takes"), Path(d), "tt")
    for key in profile.PROBES:
        assert "error" not in prof[key], (key, prof[key])
    assert prof["project_sr"] == 48000
    assert prof["pan"]["fit"]["law"] in profile.measure.PAN_LAWS
    assert abs(prof["unity"]["gain_db"]) < 6.5                 # unity apart from the pan law
    assert abs(prof["unity"]["latency_samples"]) < 4800        # within 100 ms of the grid
    assert prof["src"]["passband_ripple_db"] < 6.0             # the sweep actually played


if __name__ == "__main__":
    test_tracktion_probe_plays_the_probes()
    print("ok  test_tracktion_probe_plays_the_probes")
