"""
Tests for aggregator_bridge — the /agg/ch -> /track/<id>/* translator.
Pure Python (mock OSC client). Run: python -m unittest test_aggregator_bridge
"""

import math
import unittest

import bands
from aggregator_bridge import AggregatorBridge, build_track_messages, derive


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


if __name__ == "__main__":
    unittest.main()
