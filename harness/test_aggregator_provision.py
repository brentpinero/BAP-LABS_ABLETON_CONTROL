"""
Tests for aggregator_provision.plan — multi-device allocation + index-based routing,
the hardening that makes coverage work on ANY project (up to max_instrument nodes),
regardless of naming/grouping. Pure Python (fake LiveClient). Run:
    python -m unittest test_aggregator_provision
"""

import unittest

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


if __name__ == "__main__":
    unittest.main()
