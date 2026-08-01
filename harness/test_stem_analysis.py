"""Tests for stem_analysis — offline stem features + rung-delta plugin effects.
Uses tiny synthetic wavs. Run: python -m unittest test_stem_analysis"""

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

import stem_analysis as sa


def _write_wav(path, freq=440.0, amp=0.5, sr=48000, dur=2.0):
    import soundfile as sf
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    tone = amp * np.sin(2 * np.pi * freq * t)
    sf.write(str(path), np.stack([tone, tone], axis=1), sr)   # stereo


class TestSummaryAndLevels(unittest.TestCase):
    def test_summary_stats(self):
        s = sa._summary([0.0, 1.0, 2.0, 3.0, 4.0])
        self.assertEqual(s["min"], 0.0)
        self.assertEqual(s["max"], 4.0)
        self.assertEqual(s["mean"], 2.0)

    def test_band_levels_db_weights_by_rms(self):
        summ = {"rms_db": {"mean": -6.0}, "band_energy": [{"mean": 0.5}, {"mean": 0.25}]}
        lv = sa._band_levels_db(summ)
        # louder overall + bigger fraction => higher band level; both finite
        self.assertGreater(lv[0], lv[1])


class TestAnalyzeStem(unittest.TestCase):
    def test_features_shape_and_bands_sum(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = Path(tmp) / "tone.wav"
            _write_wav(w, freq=440.0)
            an = sa.analyze_stem(w, hop=2048, n_fft=4096)
            self.assertEqual(an["schema_version"], sa.ANALYSIS_SCHEMA)
            self.assertGreater(an["n_frames"], 5)
            self.assertEqual(len(an["series"]["band_energy"][0]), 7)   # v1_7band
            # a 440Hz tone concentrates energy in the 'mid' band (350-2000) -> fraction ~1
            mids = [row[3] for row in an["series"]["band_energy"] if sum(row) > 0]
            self.assertGreater(np.mean(mids), 0.8)
            self.assertIn("lufs_integrated", an["loudness"])
            # mel view: [T][64] on the same grid, peak mel band tracks the 440Hz tone
            self.assertEqual(an["mel_bands"], 64)
            self.assertEqual(len(an["series"]["mel_db"]), an["n_frames"])
            self.assertEqual(len(an["series"]["mel_db"][0]), 64)
            self.assertEqual(len(an["summary"]["mel_db_mean"]), 64)
            peak_band = int(np.argmax(an["summary"]["mel_db_mean"]))
            self.assertLess(peak_band, 20)   # 440Hz lives in the low mel bands, not the top

    def test_louder_tone_has_higher_rms(self):
        with tempfile.TemporaryDirectory() as tmp:
            loud, quiet = Path(tmp) / "l.wav", Path(tmp) / "q.wav"
            _write_wav(loud, amp=0.8); _write_wav(quiet, amp=0.1)
            al = sa.analyze_stem(loud); aq = sa.analyze_stem(quiet)
            self.assertGreater(al["summary"]["rms_db"]["mean"], aq["summary"]["rms_db"]["mean"])


class TestBarGrid(unittest.TestCase):
    def test_header_gets_bar_grid_with_bpm(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = Path(tmp) / "tone.wav"
            _write_wav(w)
            an = sa.analyze_stem(w, bpm=126.0, start_bar=4)
            self.assertEqual(an["bpm"], 126.0)
            self.assertEqual(an["start_bar"], 4)
            # 4 beats * 60/126 s/beat * 23.4375 frames/s
            self.assertAlmostEqual(an["frames_per_bar"], (4 * 60 / 126) * (48000 / 2048), places=2)
            self.assertNotIn("bpm", sa.analyze_stem(w))   # no bpm -> no grid

    def test_per_bar_effect_localizes_change(self):
        # prev: quiet throughout; cur: loud in the 2nd bar only -> the delta must land in bar 5
        fpb = 10.0
        T = 30
        mk = lambda rms: {"frames_per_bar": fpb, "start_bar": 4,
                          "series": {"rms_db": rms,
                                     "mel_db": [[-60.0] * 64] * T,
                                     "band_energy": [[1 / 7.0] * 7] * T}}
        prev = mk([-40.0] * T)
        cur = mk([-40.0] * 10 + [-20.0] * 10 + [-40.0] * 10)
        bars = sa.per_bar_effect(cur, prev)
        self.assertEqual(len(bars), 3)
        self.assertEqual([b["bar"] for b in bars], [4, 5, 6])
        self.assertEqual(bars[0]["rms_db_change"], 0.0)
        self.assertEqual(bars[1]["rms_db_change"], 20.0)   # the loud bar
        self.assertEqual(bars[2]["rms_db_change"], 0.0)
        self.assertTrue(all(b["content"] for b in bars))
        self.assertEqual(len(bars[1]["band_db_change"]), 7)
        self.assertEqual(len(bars[1]["mel_db_change"]), 64)

    def test_per_bar_none_without_grid(self):
        no_grid = {"series": {"rms_db": [0.0]}}
        self.assertIsNone(sa.per_bar_effect(no_grid, no_grid))


class TestPluginEffect(unittest.TestCase):
    def _an(self, rms, band0, centroid, lufs, crest, mel=-40.0):
        return {"scheme": "v1_7band",
                "summary": {"rms_db": {"mean": rms},
                            "band_energy": [{"mean": band0}] + [{"mean": (1 - band0) / 6}] * 6,
                            "mel_db_mean": [mel] * 64,
                            "centroid_hz": {"mean": centroid}, "width": {"mean": 0.1},
                            "flux": {"mean": 0.2}},
                "loudness": {"lufs_integrated": lufs, "crest_factor_db": crest,
                             "true_peak_dbtp": -1.0, "dynamic_range_db": 5.0}}

    def test_effect_captures_deltas(self):
        prev = self._an(rms=-20, band0=0.2, centroid=1000, lufs=-18, crest=10, mel=-40.0)
        cur = self._an(rms=-14, band0=0.5, centroid=1400, lufs=-12, crest=6, mel=-34.0)   # louder, brighter, more sub
        eff = sa.plugin_effect(cur, prev, "Saturator", "through_0_EQ")
        self.assertEqual(eff["newly_enabled"], "Saturator")
        self.assertEqual(eff["loudness_db"], -12 - (-18))                      # +6 dB louder
        self.assertEqual(eff["centroid_hz_change"], 400.0)                     # brighter
        self.assertEqual(eff["crest_db"], 6 - 10)                              # -4 (more compressed)
        self.assertEqual(len(eff["band_db_change"]), 7)
        self.assertGreater(eff["band_db_change"][0], 0)                        # sub band grew
        self.assertEqual(len(eff["mel_db_change"]), 64)
        self.assertEqual(eff["mel_db_change"][0], 6.0)                         # -34 - (-40)

    def test_effect_tolerates_missing_mel(self):
        # v1-era summaries (no mel_db_mean) must not crash the delta
        prev = self._an(rms=-20, band0=0.2, centroid=1000, lufs=-18, crest=10)
        cur = self._an(rms=-14, band0=0.5, centroid=1400, lufs=-12, crest=6)
        del prev["summary"]["mel_db_mean"]
        eff = sa.plugin_effect(cur, prev, "EQ", "all_off")
        self.assertIsNone(eff["mel_db_change"])


class TestAnalyzeSession(unittest.TestCase):
    def test_injects_analysis_and_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            # two rungs of one node: all_off (quiet) then through_0 (louder)
            for name, amp, rung in [("n__rung01_all_off", 0.1, {"index": 1, "kind": "all_off",
                                                                "label": "all_off", "newly_enabled": None,
                                                                "enabled_through": -1}),
                                    ("n__rung02_through_0_EQ", 0.6, {"index": 2, "kind": "progressive",
                                                                     "label": "through_0_EQ",
                                                                     "newly_enabled": "EQ",
                                                                     "enabled_through": 0})]:
                _write_wav(Path(tmp) / f"{name}.wav", amp=amp)
                (Path(tmp) / f"{name}.json").write_text(json.dumps(
                    {"node": {"name": "n"}, "rung": rung, "devices": []}))
            res = sa.analyze_session(tmp, log=lambda *a: None)
            self.assertEqual(res["analyzed"], 2)
            self.assertEqual(res["plugin_effects"], 1)
            prog = json.loads((Path(tmp) / "n__rung02_through_0_EQ.json").read_text())
            self.assertIn("audio_analysis", prog)
            self.assertIn("plugin_effect", prog)
            self.assertEqual(prog["plugin_effect"]["newly_enabled"], "EQ")
            self.assertGreater(prog["plugin_effect"]["loudness_db"], 0)        # through_0 louder than all_off


if __name__ == "__main__":
    unittest.main()
