"""Tests for the plughost render backend (plughost_render.py + its render_worker/pool wiring).

Unit tests need nothing installed. Integration tests run Serum 2 through host_rs and are
skipped unless the plughost binaries are built (daw_bench/host_bakeoff/README.md) and Serum 2
is installed; the freeze comparison also needs the local-only track-66 fixture.
    python -m pytest daw_translation/test_plughost_render.py -v
"""
from __future__ import annotations

import plistlib
import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "sandbox"))

import plughost_render as pr  # noqa: E402
import render_pool  # noqa: E402
import render_worker  # noqa: E402

SERUM2 = "/Library/Audio/Plug-Ins/VST3/Serum2.vst3"
FIXTURE = HERE.parent / "daw_bench" / "fixtures" / "serum2_track66"


def test_parse_spec_vst_forms():
    assert pr.parse_spec("vst:/x/S.vst3") == {"format": "vst3", "bundle": "/x/S.vst3"}
    assert pr.parse_spec("vst:/x/S.vst3::name=Serum 2")["class_name"] == "Serum 2"
    assert pr.parse_spec("vst:/x/S.vst3::/p/a.vstpreset")["preset"] == "/p/a.vstpreset"
    with pytest.raises(ValueError):
        pr.parse_spec("fallback:keys")


def test_parse_spec_au_reads_codes_from_bundle(tmp_path):
    bundle = tmp_path / "X.component" / "Contents"
    bundle.mkdir(parents=True)
    with open(bundle / "Info.plist", "wb") as f:
        plistlib.dump({"AudioComponents": [{"type": "aumu", "subtype": "Xf2X",
                                            "manufacturer": "XFER"}]}, f)
    spec = pr.parse_spec(f"au:{tmp_path / 'X.component'}")
    assert spec == {"format": "au", "au": ["aumu", "Xf2X", "XFER"]}


def test_note_events_beats_to_samples_with_worker_clamps():
    ev = pr.note_events([{"pitch": 200, "start_time": 1.0, "duration": 0.0, "velocity": 0}],
                        bpm=120, sr=48000)
    assert ev == [{"pitch": 127, "start": 24000, "dur": 960, "vel": 1}]   # 0.5 s; 20 ms minimum


def test_render_length_bars_or_last_note_plus_tail():
    notes = [{"start_time": 2.0, "duration": 2.0}]
    assert pr.render_length(notes, 120, 1000, bars=None, tail=1.0) == 3000    # 2 s + 1 s
    assert pr.render_length(notes, 120, 1000, bars=2, tail=0.5) == 4500       # 4 s + 0.5 s


def test_pool_cache_key_and_cmd_carry_backend(tmp_path):
    notes = tmp_path / "n.json"
    notes.write_text('{"notes": []}')
    job = {"midi": str(notes), "instrument": "vst:/x.vst3", "output": str(tmp_path / "o.wav")}
    assert render_pool._job_key(job) != render_pool._job_key({**job, "backend": "plughost"})
    cmd = render_pool._build_cmd({**job, "backend": "plughost"})
    assert cmd[cmd.index("--backend") + 1] == "plughost"
    assert "--backend" not in render_pool._build_cmd(job)


def test_worker_falls_back_to_pedalboard_when_plughost_missing(monkeypatch, capsys):
    monkeypatch.setattr(pr, "available", lambda: False)
    loaded = []
    monkeypatch.setattr(render_worker, "load_instrument", lambda spec: loaded.append(spec) or "plug")
    monkeypatch.setattr(render_worker, "render_with_plug", lambda plug, *a, **k: np.zeros((10, 2)))
    out = render_worker.render_midi([], 120, "vst:/x.vst3", 44100, backend="plughost")
    assert loaded == ["vst:/x.vst3"] and out.shape == (10, 2)
    assert "rendering with pedalboard" in capsys.readouterr().err


ready = pr.available() and Path(SERUM2).exists()


@pytest.mark.skipif(not (ready and (FIXTURE / "component_state.bin").exists()
                         and (FIXTURE / "live_2026-11-08_126bpm.wav").exists()),
                    reason="plughost not built, Serum 2 missing, or local fixture absent")
def test_track66_patch_matches_live_freeze_within_1db():
    import fidelity
    audio = render_worker.render_midi(
        [{"pitch": 27, "start_time": 0, "duration": 16, "velocity": 100}], 126,
        f"vst:{SERUM2}::name=Serum 2", 44100, tail_seconds=4.38, backend="plughost",
        raw_component_state=(FIXTURE / "component_state.bin").read_bytes())
    assert audio.shape == (529158, 2)
    out = Path(pr.tempfile.mkdtemp()) / "r.wav"
    sf.write(out, audio, 44100)
    bands = fidelity.compare(out, FIXTURE / "live_2026-11-08_126bpm.wav")["band_diff_db"]
    assert max(abs(b) for b in bands[:3]) <= 1.0          # the Phase 1 gate, 20-250 Hz


@pytest.mark.skipif(not ready, reason="plughost not built or Serum 2 missing")
def test_named_params_change_the_render(capsys):
    notes = [{"pitch": 48, "start_time": 0, "duration": 2, "velocity": 100}]
    spec = f"vst:{SERUM2}::name=Serum 2"
    base = pr.render_midi(notes, 120, spec, 44100, tail_seconds=0.5)
    quiet = pr.render_midi(notes, 120, spec, 44100, tail_seconds=0.5, params={"main_vol": 0.1})
    assert "not applied" not in capsys.readouterr().err
    assert base.shape == quiet.shape == (66150, 2)
    assert np.max(np.abs(quiet)) < 0.5 * np.max(np.abs(base))
