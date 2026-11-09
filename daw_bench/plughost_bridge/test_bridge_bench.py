"""Tests for the Tracktion <-> plughost bridge spike.

Unit tests need nothing built. Integration tests run bridge_probe (Tracktion + the Plughost
format) on Serum 2 and are skipped unless bridge_probe and the plughost helper are built and
Serum 2 is installed.
    python -m pytest daw_bench/plughost_bridge/test_bridge_bench.py -v
"""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge_bench as bb  # noqa: E402


def test_summarize_counts_bridge_misses_after_warmup_only():
    report = {"ok": True, "callbacks": 1000, "overruns": 2, "overruns_warmup": 5,
              "cb_ms_median": 0.1, "cb_ms_p99": 0.2, "cb_ms_max": 3.0, "period_ms": 2.9,
              "bridged": [{"status": {"missed": 9, "late": 4}, "missed_after_warmup": 1,
                           "late_after_warmup": 0, "fallbacks": 3, "size_mismatches": 0, "errors": 0},
                          {"status": {"missed": 7, "late": 1}, "missed_after_warmup": 0,
                           "late_after_warmup": 1, "fallbacks": 2, "size_mismatches": 0, "errors": 0}]}
    s = bb.summarize_rt(report)
    assert (s["overruns"], s["overruns_warmup"]) == (2, 5)
    assert (s["missed"], s["late"], s["missed_total"]) == (1, 1, 16)
    assert s["fallbacks"] == 5


def test_header_declares_every_exported_function():
    here = Path(__file__).resolve().parent
    exported = set(re.findall(r'pub extern "C" fn (ph_\w+)', (here / "src/lib.rs").read_text()))
    declared = set(re.findall(r"\b(ph_\w+)\s*\(", (here / "plughost_bridge.h").read_text()))
    assert exported and exported == declared


ready = (bb.PROBE.exists() and bb.HELPER.exists() and Path(bb.BASE["bundle"]).exists())


@pytest.mark.skipif(not ready, reason="bridge_probe / plughost helper not built, or Serum 2 missing")
def test_offline_render_through_bridge_is_bit_identical(tmp_path):
    res = bb.null(tmp_path)
    assert res["native"]["ok"] and res["bridge"]["ok"]
    assert res["residual_dbfs"] < -120          # delay compensation absorbs the bridge exactly


@pytest.mark.skipif(not ready, reason="bridge_probe / plughost helper not built, or Serum 2 missing")
def test_realtime_bridge_one_track_no_dropouts_after_warmup(tmp_path):
    s = bb.summarize_rt(bb.run_probe({"mode": "realtime", "plugin": "bridge", "block": 128,
                                      "latency_quanta": 2, "seconds": 4, "tracks": 1}, tmp_path, "rt"))
    assert s["ok"] and s["errors"] == 0 and s["size_mismatches"] == 0
    assert s["overruns"] == 0 and s["missed"] == 0
