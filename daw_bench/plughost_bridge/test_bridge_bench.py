"""Tests for the Tracktion <-> plughost bridge spike.

Unit tests need nothing built. Integration tests run bridge_probe (Tracktion + the Plughost
format) on Serum 2 and are skipped unless bridge_probe and the plughost helper are built and
Serum 2 is installed.
    python -m pytest daw_bench/plughost_bridge/test_bridge_bench.py -v
"""
import re
import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

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


def test_dropouts_sum_every_kind_and_tolerate_missing_device_fields():
    assert bb.dropouts({"device_xruns": 2, "overruns": 1, "missed": 3}) == 6
    assert bb.dropouts({"device_xruns": None, "overruns": 0, "missed": 0}) == 0   # paced runs


def test_summarize_carries_device_fields():
    s = bb.summarize_rt({"ok": True, "device_xruns": 4, "device_xruns_warmup": 2, "cpu_load_median": 0.3,
                         "workgroup_valid": True, "bridged": []})
    assert (s["device_xruns"], s["device_xruns_warmup"], s["workgroup_valid"]) == (4, 2, True)


def test_source_clip_has_signal_for_the_chain(tmp_path):
    x, sr = sf.read(bb.make_source(tmp_path / "src.wav", 44100, 2.0, 126))
    assert sr == 44100 and x.shape == (88200, 2)
    peak = 20 * np.log10(np.abs(x).max())
    assert -12 < peak < -1                      # loud enough to drive every effect, never clipping


def test_chain_is_six_installed_vst3s():
    assert len(bb.CHAIN) == 6
    assert all(c["bundle"].endswith(".vst3") for c in bb.CHAIN)


ready = (bb.PROBE.exists() and bb.HELPER.exists() and Path(bb.BASE["bundle"]).exists())
chain_ready = bb.PROBE.exists() and bb.HELPER.exists() and all(Path(c["bundle"]).exists() for c in bb.CHAIN)


@pytest.mark.skipif(not chain_ready, reason="bridge_probe / helper not built, or a CHAIN plugin missing")
@pytest.mark.parametrize("kind", ["native", "bridge"])
def test_chain_on_coreaudio_carries_audio_without_dropouts(tmp_path, kind):
    """One track x the 6-plugin chain on the real CoreAudio device (output zeroed): the clip must
    come through every plugin (a silent plugin would make the ramp measure nothing)."""
    src = bb.make_source(tmp_path / "src.wav", bb.BASE["sample_rate"], 6, bb.BASE["tempo"])
    r = bb.run_probe({"mode": "realtime", "plugin": kind, "block": 128, "seconds": 4, "tracks": 1,
                      "chain": bb.CHAIN, "audio_file": str(src), "prespawn_parallel": 1, "warmup_s": 2.0,
                      **bb.DEVICE}, tmp_path, "chain")
    s = bb.summarize_rt(r)
    assert s["ok"] and s["workgroup_valid"] and s["errors"] == 0
    assert bb.dropouts(s) == 0
    x, _ = sf.read(tmp_path / "chain.wav")
    assert bb.peak_dbfs(x) > -40


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
