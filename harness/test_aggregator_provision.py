"""
Tests for aggregator_provision — plan (multi-device allocation + index-based
routing) and the v2 DEVICE-PULL apply (set_device_audio_input instead of capture
tracks, stale-IO clearing, device-pull state). Pure Python (fake LiveClient). Run:
    python -m unittest test_aggregator_provision
"""

import json
import tempfile
import unittest
from pathlib import Path

from perception_config import cfg


class FakeClient:
    """Minimal stand-in for LiveClient: N leaf tracks + master + no returns."""
    def __init__(self, n, names=None):
        self.n = n
        self.names = names or ["Audio %d" % i for i in range(n)]

    def send(self, cmd, params=None):
        if cmd == "get_session_info":
            return {"track_count": self.n}
        if cmd == "get_track_info":
            i = params["track_index"]
            if i == -1:
                return {"name": "Master", "kind": "master"}
            return {"name": self.names[i], "kind": "audio"}
        if cmd == "get_return_tracks":
            return {"return_tracks": []}
        return {}


class TestPlanAllocation(unittest.TestCase):
    def setUp(self):
        import aggregator_provision as ap
        self.ap = ap
        self.n_pairs = int(cfg("aggregator_channels"))
        self.usable = self.n_pairs - 1

    def test_full_coverage_under_cap(self):
        # 100 generic tracks, all instrumented, spread across ceil(100/usable) devices
        items, sel, n_dev = self.ap.plan(FakeClient(100))
        self.assertEqual(len(items), 100)                      # nothing dropped
        self.assertEqual(n_dev, -(-100 // self.usable))        # ceil
        # every capture routes by song index (dup-name safe), never by name here
        self.assertTrue(all(it["source_index"] == it["ref"] for it in items))

    def test_global_channels_unique_across_devices(self):
        items, _sel, n_dev = self.ap.plan(FakeClient(100))
        self.assertGreater(n_dev, 1)                           # forces cross-device
        gch = [it["osc_channel"] for it in items]
        self.assertEqual(len(gch), len(set(gch)))              # no OSC collision
        # global channel == device base + local pair, matching the device's baked base
        for it in items:
            self.assertEqual(it["osc_channel"], it["device"] * self.n_pairs + it["pair"])

    def test_device_and_pair_bounds(self):
        items, _sel, _n = self.ap.plan(FakeClient(70))
        for it in items:
            self.assertTrue(1 <= it["pair"] <= self.usable)    # pair 0 reserved
            self.assertEqual(it["device"], (_slot(items, it)) // self.usable)

    def test_duplicate_names_not_skipped(self):
        # 26x the same name used to be skipped (misroute risk); now each routes by index
        items, _sel, _n = self.ap.plan(FakeClient(26, names=["Serum 2"] * 26))
        self.assertEqual(len(items), 26)
        self.assertEqual(sorted(it["source_index"] for it in items), list(range(26)))

    def test_caps_at_max_instrument(self):
        cap = int(cfg("max_instrument"))
        items, _sel, _n = self.ap.plan(FakeClient(cap + 60))
        self.assertLessEqual(len(items), cap)
        self.assertTrue(all(it["kind"] != "master" for it in items))


def _slot(items, it):
    return items.index(it)


class PullFakeClient:
    """Records every send(); canned session: track 0 'Kick', track 1 =
    'AGG_ANALYSIS_0' with the Aggregator device loaded."""

    def __init__(self):
        self.calls = []
        self.tracks = [
            {"name": "Kick", "devices": []},
            {"name": "AGG_ANALYSIS_0",
             "devices": [{"name": "BAP Labs Mix Analysis Aggregator", "index": 0}]},
        ]

    def send(self, cmd, params=None):
        self.calls.append((cmd, dict(params or {})))
        if cmd == "get_session_info":
            return {"track_count": len(self.tracks)}
        if cmd == "get_track_info":
            i = params["track_index"]
            if i < 0 or i >= len(self.tracks):
                raise IndexError("out of range")
            return dict(self.tracks[i], track_index=i)
        if cmd == "set_device_audio_input":
            src = params.get("source_name")
            if src is None and params.get("source_index") is not None:
                src = self.tracks[params["source_index"]]["name"]
            return {"device_name": "BAP Labs Mix Analysis Aggregator",
                    "io_index": params["io_index"], "routing_type": src}
        raise AssertionError("unexpected command %s" % cmd)


class TestDevicePullApply(unittest.TestCase):
    def setUp(self):
        import aggregator_provision as ap
        self.ap = ap
        self.c = PullFakeClient()
        self.tmp = tempfile.TemporaryDirectory()
        self._old_state, self._old_cfg = ap.STATE, ap.cfg
        ap.STATE = Path(self.tmp.name) / "aggregator_state.json"
        ap.cfg = lambda key: {"aggregator_channels": 4, "max_instrument": 64}[key]
        self.items = [
            {"ref": 0, "name": "Kick", "kind": "regular", "group_id": "-1",
             "device": 0, "pair": 1, "osc_channel": 1,
             "source_index": 0, "reasons": ["named:drums"]},
            {"ref": "return:0", "name": "A-Reverb", "kind": "return", "group_id": "-1",
             "device": 0, "pair": 2, "osc_channel": 2,
             "source_index": None, "reasons": ["return"]},
        ]

    def tearDown(self):
        self.ap.STATE, self.ap.cfg = self._old_state, self._old_cfg
        self.tmp.cleanup()

    def test_no_capture_tracks_created(self):
        self.ap.apply(self.c, self.items, n_dev=1)
        cmds = [c for c, _ in self.c.calls]
        self.assertNotIn("create_audio_track", cmds)      # AGG track already exists
        self.assertNotIn("set_track_input_routing", cmds)
        self.assertNotIn("set_track_output_routing", cmds)

    def test_io_index_is_local_pair_on_agg_device(self):
        self.ap.apply(self.c, self.items, n_dev=1)
        sets = [p for c, p in self.c.calls if c == "set_device_audio_input"]
        routed = [p for p in sets if p.get("source_name") != "No Input"]
        self.assertEqual([(p["track_index"], p["device_index"], p["io_index"])
                          for p in routed],
                         [(1, 0, 1), (1, 0, 2)])
        # dup-safe index routing for the leaf, name routing for the return
        self.assertEqual(routed[0].get("source_index"), 0)
        self.assertEqual(routed[1].get("source_name"), "A-Reverb")

    def test_stale_ios_cleared_to_no_input(self):
        self.ap.apply(self.c, self.items, n_dev=1)
        cleared = [p["io_index"] for c, p in self.c.calls
                   if c == "set_device_audio_input" and p.get("source_name") == "No Input"]
        self.assertEqual(cleared, [3])                    # 4 pairs: io0 reserved, 1+2 used
        self.assertNotIn(0, cleared)                      # never touch the main input

    def test_state_and_bridge_map(self):
        bmap = self.ap.apply(self.c, self.items, n_dev=1)
        self.assertEqual(bmap[1]["track_id"], "agg-0")
        self.assertEqual(bmap[2]["kind"], "return")
        st = json.loads(self.ap.STATE.read_text())
        self.assertEqual(st["mode"], "device-pull")
        self.assertEqual(st["cap_tracks"], [])            # nothing for teardown to delete
        self.assertEqual(st["routed"], {"0": [1, 2]})
        self.assertEqual(st["map"]["1"]["name"], "Kick")


if __name__ == "__main__":
    unittest.main()
