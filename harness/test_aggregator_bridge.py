"""
Tests for aggregator_bridge — the /agg/ch -> /track/<id>/* translator.
Pure Python (mock OSC client). Run: python -m unittest test_aggregator_bridge
"""

import json
import math
import tempfile
import unittest
from pathlib import Path

import bands
from aggregator_bridge import (AggregatorBridge, agg_status, build_track_messages,
                               derive, load_agg_map)


class _MockClient:
    def __init__(self):
        self.sent = []

    def send_message(self, addr, args):
        self.sent.append((addr, args))


class TestDerive(unittest.TestCase):
    def test_fractions_and_rms(self):
        # one band dominant -> that fraction ~1
        raw = [0.0, 0.9, 0.0, 0.1, 0.0, 0.0, 0.0]
        fr, rms_db, lin = derive(raw)
        self.assertAlmostEqual(sum(fr), 1.0, places=6)
        self.assertGreater(fr[1], 0.95)                    # 0.9^2 dominates
        # overall linear = sqrt(0.81+0.01) ~ 0.906 -> ~ -0.86 dB
        self.assertAlmostEqual(lin, math.sqrt(0.82), places=5)

    def test_louder_higher_rms(self):
        _, q, _ = derive([0.05] * 7)
        _, l, _ = derive([0.5] * 7)
        self.assertAlmostEqual(l - q, 20.0, delta=0.5)     # 10x -> +20 dB

    def test_silence(self):
        fr, rms, lin = derive([0.0] * 7)
        self.assertEqual(rms, -120.0)
        self.assertEqual(lin, 0.0)

    def test_low_level_gate_zeros_spectrum(self):
        # a quiet channel (well below the gate) -> spectrum zeroed, not noise-shaped
        quiet = [0.00002] * 7                          # ~ -94 dB overall, below -70 gate
        fr, rms, _ = derive(quiet)
        self.assertLess(rms, -70.0)
        self.assertEqual(sum(fr), 0.0)
        # a loud channel is unaffected
        fr2, rms2, _ = derive([0.0, 0.5, 0.0, 0.1, 0.0, 0.0, 0.0])
        self.assertGreater(rms2, -70.0)
        self.assertAlmostEqual(sum(fr2), 1.0, places=5)


class TestMessages(unittest.TestCase):
    def test_message_shapes(self):
        raw = [0.1, 0.2, 0.05, 0.3, 0.1, 0.05, 0.02]
        meta = {"name": "Bass", "kind": "group", "group_id": "-1"}
        msgs = dict(build_track_messages("42", meta, raw, "v1_7band"))
        self.assertEqual(msgs["/track/42/meta"], ["Bass", "group", "-1", "v1_7band"])
        self.assertEqual(len(msgs["/track/42/levels"]), 6)          # rms_l r peak_l r mid side
        self.assertEqual(len(msgs["/track/42/spectrum"]), bands.n_bands("v1_7band"))
        self.assertEqual(len(msgs["/track/42/stereo"]), 3)          # corr mid side
        self.assertAlmostEqual(sum(msgs["/track/42/spectrum"]), 1.0, places=5)

    def test_stereo_from_side_rms(self):
        meta = {"name": "x", "kind": "audio"}
        # mono channel (side RMS = 0) -> correlation ~ 1, side 0
        mono = dict(build_track_messages("1", meta, [0.0, 0.4, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0], "v1_7band"))
        st = mono["/track/1/stereo"]
        self.assertAlmostEqual(st[0], 1.0, places=3)
        self.assertEqual(st[2], 0.0)
        # wide channel (side ~ mid) -> correlation ~ 0
        wide = dict(build_track_messages("1", meta, [0.0, 0.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3], "v1_7band"))
        stw = wide["/track/1/stereo"]
        self.assertLess(stw[0], 0.3)                    # correlation collapses with side energy
        self.assertGreater(stw[2], 0.0)


class TestBridge(unittest.TestCase):
    def _bridge(self):
        return AggregatorBridge(client=_MockClient(), recv_port=0)

    def test_mapped_channel_reemits_four_messages(self):
        b = self._bridge()
        b.set_channel(1, track_id="99", name="Vox", kind="group")
        b.on_spectrum("/agg/ch/1/spectrum", 0.1, 0.1, 0.4, 0.2, 0.1, 0.05, 0.05)
        addrs = [a for a, _ in b.client.sent]
        self.assertEqual(set(addrs), {"/track/99/meta", "/track/99/levels",
                                      "/track/99/spectrum", "/track/99/stereo"})
        self.assertEqual(b.stats["sent"], 4)

    def test_unmapped_channel_dropped(self):
        b = self._bridge()
        b.on_spectrum("/agg/ch/7/spectrum", 0.1, 0.2, 0.3, 0.1, 0.1, 0.1, 0.1)
        self.assertEqual(b.client.sent, [])
        self.assertEqual(b.stats["unmapped"], 1)

    def test_map_id_indirection(self):
        # channel k routes to whatever track-id the provisioning map says
        b = self._bridge()
        b.set_map({2: {"track_id": "id-abc", "name": "Kick", "kind": "audio", "group_id": "5"}})
        b.on_spectrum("/agg/ch/2/spectrum", *([0.2] * 7))
        meta = next(args for a, args in b.client.sent if a.endswith("/meta"))
        self.assertEqual(meta[:3], ["Kick", "audio", "5"])


# the exact schema aggregator_provision.apply() writes: map keyed by global osc channel
# (device*n_pairs + pair). At aggregator_channels=32, dev0 owns ch 1..31, dev1 owns 33..63.
def _multi_device_state():
    return {
        "agg_tracks": [70, 71],
        "cap_tracks": [72, 73, 74, 75],
        "map": {
            "1":  {"track_id": "agg-0",  "name": "Kick",  "kind": "audio", "group_id": "-1"},
            "2":  {"track_id": "agg-1",  "name": "Snare", "kind": "audio", "group_id": "-1"},
            "33": {"track_id": "agg-40", "name": "Vox",   "kind": "audio", "group_id": "5"},
            "34": {"track_id": "agg-41", "name": "Lead",  "kind": "audio", "group_id": "5"},
        },
    }


class TestLoadAggMap(unittest.TestCase):
    def test_parses_multi_device_schema(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "aggregator_state.json"
            p.write_text(json.dumps(_multi_device_state()))
            m = load_agg_map(p)
            self.assertEqual(set(m), {1, 2, 33, 34})       # int keys, spanning two devices
            self.assertTrue(all(isinstance(k, int) for k in m))
            self.assertEqual(m[33]["name"], "Vox")

    def test_missing_file_returns_none(self):
        # None (not {}) so the watcher keeps its prior map instead of wiping it
        self.assertIsNone(load_agg_map(Path("/nonexistent/aggregator_state.json")))

    def test_half_written_json_returns_none(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "aggregator_state.json"
            p.write_text('{"agg_tracks": [70], "map": {"1": {"track')   # truncated mid-write
            self.assertIsNone(load_agg_map(p))

    def test_watcher_keeps_map_on_bad_read(self):
        # simulate the watcher tick: a None load must NOT clear an already-loaded bridge map
        b = AggregatorBridge(client=_MockClient(), recv_port=0)
        b.set_map({int(k): v for k, v in _multi_device_state()["map"].items()})
        before = dict(b.map)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "aggregator_state.json"
            p.write_text("{ this is not json")
            mapping = load_agg_map(p)
            if mapping is not None:                          # watcher's guard
                b.clear(); b.set_map(mapping)
        self.assertEqual(b.map, before)                      # untouched


class TestAggStatus(unittest.TestCase):
    def test_device_count_and_span_from_global_channels(self):
        mapping = {int(k): v for k, v in _multi_device_state()["map"].items()}
        st = agg_status(mapping, {"recv": 100, "sent": 96, "unmapped": 4}, n_pairs=32)
        self.assertEqual(st["devices"], 2)                   # ch //32 -> {0, 1}
        self.assertEqual(st["channels"], 4)
        self.assertEqual((st["gch_min"], st["gch_max"]), (1, 34))
        self.assertEqual((st["recv"], st["sent"], st["unmapped"]), (100, 96, 4))

    def test_empty_map_is_zero_devices(self):
        st = agg_status({}, {}, n_pairs=32)
        self.assertEqual(st["devices"], 0)
        self.assertEqual(st["channels"], 0)
        self.assertIsNone(st["gch_min"])


class TestStateRoundTrip(unittest.TestCase):
    def test_atomic_write_then_load(self):
        # aggregator_provision._write_state (atomic) -> load_agg_map reads back identical channels
        import aggregator_provision as ap
        with tempfile.TemporaryDirectory() as d:
            orig = ap.STATE
            ap.STATE = Path(d) / "aggregator_state.json"
            try:
                ap._write_state(_multi_device_state())
                m = load_agg_map(ap.STATE)
                self.assertEqual(set(m), {1, 2, 33, 34})
                # no .tmp left behind (os.replace consumed it)
                self.assertFalse((Path(d) / "aggregator_state.tmp").exists())
            finally:
                ap.STATE = orig


if __name__ == "__main__":
    unittest.main()
