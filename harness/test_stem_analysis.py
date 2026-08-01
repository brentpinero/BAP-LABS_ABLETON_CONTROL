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

    def test_louder_tone_has_higher_rms(self):
        with tempfile.TemporaryDirectory() as tmp:
            loud, quiet = Path(tmp) / "l.wav", Path(tmp) / "q.wav"
            _write_wav(loud, amp=0.8); _write_wav(quiet, amp=0.1)
            al = sa.analyze_stem(loud); aq = sa.analyze_stem(quiet)
            self.assertGreater(al["summary"]["rms_db"]["mean"], aq["summary"]["rms_db"]["mean"])


class TestPluginEffect(unittest.TestCase):
    def _an(self, rms, band0, centroid, lufs, crest):
        return {"scheme": "v1_7band",
                "summary": {"rms_db": {"mean": rms},
                            "band_energy": [{"mean": band0}] + [{"mean": (1 - band0) / 6}] * 6,
                            "centroid_hz": {"mean": centroid}, "width": {"mean": 0.1},
                            "flux": {"mean": 0.2}},
                "loudness": {"lufs_integrated": lufs, "crest_factor_db": crest,
                             "true_peak_dbtp": -1.0, "dynamic_range_db": 5.0}}

    def test_effect_captures_deltas(self):
        prev = self._an(rms=-20, band0=0.2, centroid=1000, lufs=-18, crest=10)
        cur = self._an(rms=-14, band0=0.5, centroid=1400, lufs=-12, crest=6)   # louder, brighter, more sub
        eff = sa.plugin_effect(cur, prev, "Saturator", "through_0_EQ")
        self.assertEqual(eff["newly_enabled"], "Saturator")
        self.assertEqual(eff["loudness_db"], -12 - (-18))                      # +6 dB louder
        self.assertEqual(eff["centroid_hz_change"], 400.0)                     # brighter
        self.assertEqual(eff["crest_db"], 6 - 10)                              # -4 (more compressed)
        self.assertEqual(len(eff["band_db_change"]), 7)
        self.assertGreater(eff["band_db_change"][0], 0)                        # sub band grew


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
