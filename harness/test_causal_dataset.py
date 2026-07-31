"""Tests for causal_dataset; no Ableton instance is required."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from causal_dataset import (build_example, build_project_manifest, build_routing_graph,
                            classify_device, eligible_parameters, exceeds_aa_variance, make_review_queue,
                            mark_reconciled, parameter_coverage, parameter_sweep, plan_interventions)


TRACKS = [
    {"id": "1", "name": "Music", "type": "group", "group_id": -1,
     "output_routing": "Master", "mixer": {"sends": []}, "devices": [], "clips": []},
    {"id": "2", "name": "Bass", "type": "audio", "group_id": 1,
     "output_routing": "Group", "mixer": {"sends": [0.3]}, "devices": [], "clips": []},
]


class TestClassificationAndPlanning(unittest.TestCase):
    def test_effect_families_and_instrument_exclusion(self):
        self.assertEqual(classify_device("FabFilter Pro-Q 3"), "eq_filter")
        self.assertEqual(classify_device("Glue Compressor"), "dynamics")
        self.assertEqual(classify_device("Serum 2"), "instrument_excluded")

    def test_parameter_sweep_is_bounded_and_deterministic(self):
        self.assertEqual(parameter_sweep(0.5, 0.0, 1.0), [0.45, 0.5, 0.55, 0.7])
        with self.assertRaises(ValueError):
            parameter_sweep(2.0, 0.0, 1.0)

    def test_plan_has_aa_baseline_bypass_prefix_and_ofat(self):
        device = {"index": 2, "name": "Glue Compressor", "parameters": [
            {"name": "Threshold", "value": 0.5, "min": 0.0, "max": 1.0},
            {"name": "Release", "value": 0.5, "min": 0.0, "max": 1.0, "automated": True},
        ]}
        plan = plan_interventions(device, seed=9)
        self.assertEqual([p["kind"] for p in plan[:4]],
                         ["aa_repeat", "baseline", "bypass", "chain_prefix"])
        sweeps = [p for p in plan if p["kind"] == "parameter_sweep"]
        self.assertEqual({p["parameter"] for p in sweeps}, {"Threshold"})
        self.assertTrue(all(p["seed"] == 9 for p in plan))

    def test_instruments_produce_no_effect_interventions(self):
        self.assertEqual(plan_interventions({"index": 0, "name": "Serum 2"}, seed=1), [])

    def test_every_effect_family_tracks_its_relevant_live_parameter_names(self):
        cases = {
            "eq_filter": ["1 Frequency A", "1 Gain A", "1 Q A", "Filter Freq", "Resonance", "Slope"],
            "dynamics": ["Threshold", "Ratio", "Attack", "Release", "Makeup", "Knee",
                         "Lookahead", "Input Gain", "Output Level", "Ceiling", "Oversampling", "Dry/Wet"],
            "saturation_distortion": ["Drive", "Tone", "Color", "Bias", "Shape", "Input",
                                      "Output", "Ceiling", "Oversampling", "Dry/Wet"],
            "stereo_modulation": ["Width", "Balance", "Pan", "Rate", "Amount", "Depth",
                                  "Phase", "Spread", "Dry/Wet"],
            "time_spatial": ["Decay Time", "PreDelay", "Feedback", "Delay Time", "Density",
                             "Diffusion", "Size", "Damping", "Low Cut", "High Cut", "Width", "Dry/Wet"],
        }
        for family, names in cases.items():
            params = [{"name": name, "value": 0.5, "min": 0.0, "max": 1.0} for name in names]
            selected = {p["name"] for p in eligible_parameters(family, params)}
            self.assertEqual(selected, set(names), family)

    def test_parameter_inventory_excludes_automated_readonly_and_unrelated_controls(self):
        params = [
            {"name": "Threshold", "value": 0.5, "min": 0.0, "max": 1.0, "automated": True},
            {"name": "Ratio", "value": 0.5, "min": 0.0, "max": 1.0, "readonly": True},
            {"name": "Device On", "value": 1.0, "min": 0.0, "max": 1.0},
            {"name": "Attack", "value": 0.5, "min": 0.0, "max": 1.0},
        ]
        self.assertEqual([p["name"] for p in eligible_parameters("dynamics", params)], ["Attack"])
        coverage = parameter_coverage("dynamics", params)
        self.assertEqual(coverage["total"], len(params))
        self.assertEqual([p["name"] for p in coverage["selected"]], ["Attack"])
        self.assertEqual({p["reason"] for p in coverage["excluded"]},
                         {"readonly", "automated_requires_explicit_override",
                          "not_relevant_to_device_family"})
        self.assertTrue(coverage["accounted"])

    def test_missing_bounds_are_reported_not_silently_dropped(self):
        coverage = parameter_coverage("eq_filter", [{"name": "Frequency", "value": 0.5}])
        self.assertEqual(coverage["selected"], [])
        self.assertEqual(coverage["excluded"][0]["reason"], "missing_value_or_bounds")


class TestManifestAndHierarchy(unittest.TestCase):
    def test_hierarchy_and_send_edges(self):
        graph = build_routing_graph(TRACKS)
        self.assertIn({"source": "2", "target": "1", "kind": "audio_output"}, graph["edges"])
        self.assertIn({"source": "2", "target": "return:0", "kind": "send", "amount": 0.3},
                      graph["edges"])

    def test_manifest_hashes_source_and_fails_closed_until_reconciled(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "source.als"
            scratch = Path(d) / "scratch.als"
            source.write_bytes(b"source")
            scratch.write_bytes(b"scratch")
            ir = {"tracks": TRACKS, "tempo": 126, "live_version": {"creator": "Live"},
                  "coverage": {}, "master": {}}
            manifest = build_project_manifest(ir, source, scratch)
        self.assertNotEqual(manifest["source"]["sha256"], manifest["scratch"]["sha256"])
        self.assertFalse(manifest["reconciliation"]["live_complete"])
        ready = mark_reconciled(manifest, live_complete=True, plugin_availability_complete=True)
        self.assertTrue(ready["reconciliation"]["ready"])
        failed = mark_reconciled(manifest, live_complete=True, plugin_availability_complete=True,
                                 errors=["missing plugin"])
        self.assertFalse(failed["reconciliation"]["ready"])


class TestExamplesAndReview(unittest.TestCase):
    def _observations(self, master_lufs):
        return {"track": {"lufs": -12.0}, "group_or_return": {"lufs": -11.0},
                "master": {"lufs": master_lufs, "stereo": {"correlation": 0.8}}}

    def test_aa_threshold_and_three_level_example(self):
        baseline = self._observations(-9.0)
        candidate = self._observations(-8.0)
        example = build_example(
            manifest_id="m1", task="causal_effect", section={"id": "drop"},
            target={"track_id": "2", "parent_group_id": "1", "return_ids": ["return:0"],
                    "master_id": "master", "device_index": 0},
            intervention={"kind": "bypass", "seed": 3}, observations=candidate,
            baseline_observations=baseline, aa_delta={"master": {"lufs": 0.01}},
            provenance={"source_hash": "abc", "render_id": "r1"})
        self.assertEqual(example["deltas"]["master"]["lufs"], 1.0)
        self.assertTrue(example["quality"]["retained"])
        self.assertFalse(example["labels"]["authored_anchor"])

    def test_rejects_wrong_hierarchy_and_noise_only(self):
        self.assertFalse(exceeds_aa_variance({"lufs": 0.01}, {"lufs": 0.01}))
        with self.assertRaisesRegex(ValueError, "observations"):
            build_example(manifest_id="m", task="causal_effect", section={}, target={},
                          intervention={}, observations={"track": {}}, baseline_observations={},
                          aa_delta={}, provenance={})

    def test_review_queue_is_reproducible_and_level_matched(self):
        base = self._observations(-9.0)
        examples = [build_example(
            manifest_id="m", task="preference_comparison", section={"id": str(i)}, target={},
            intervention={"kind": "bypass", "seed": i}, observations=self._observations(-8.0),
            baseline_observations=base, aa_delta={"lufs": 0.001}, provenance={}) for i in range(3)]
        first = make_review_queue(examples, seed=4)
        self.assertEqual(first, make_review_queue(examples, seed=4))
        self.assertTrue(all(row["level_match"] for row in first))


if __name__ == "__main__":
    unittest.main()
