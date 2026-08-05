"""
Tests for the presentation meter UI (device_ui) across every Mix Analysis device
builder: each device must open in presentation, show a meter for EVERYTHING it
tracks (fed from the same objects the OSC path uses), carry no buttons, and fit
Live's fixed M4L device height. Pure Python, no Max/Ableton.
Run: python -m unittest test_device_ui
"""

import json
import unittest
from pathlib import Path

import bands
import build_aggregator_device as bag
import build_master_device as bmd
import build_pertrack_device as bpt
import build_probe_device as bpr
import device_ui

HERE = Path(__file__).resolve().parent
BUTTON_CLASSES = {"live.text", "live.button", "button", "textbutton", "live.tab"}


def _load(path):
    d = json.loads(Path(path).read_text())
    return d["patcher"]


def _pres_boxes(p):
    return [b["box"] for b in p["boxes"] if b["box"].get("presentation") == 1]


def _lines_into(p, dst_id):
    return [l["patchline"]["source"] for l in p["lines"]
            if l["patchline"]["destination"][0] == dst_id]


class TestHelpers(unittest.TestCase):
    def test_meter_and_mslider_are_presentation_boxes(self):
        m = device_ui.meter("m", 10, 18)["box"]
        s = device_ui.mslider("s", 8, 10, 16, 40, 144)["box"]
        for b in (m, s):
            self.assertEqual(b["presentation"], 1)
            x, y, w, h = b["presentation_rect"]
            self.assertLessEqual(y + h, device_ui.DEVICE_H)
        self.assertEqual(s["size"], 8)

    def test_pnum_is_display_only(self):
        self.assertEqual(device_ui.pnum("n", 0, 0)["box"]["cantchange"], 1)


class HubDeviceUI:
    """Shared assertions for the two hub devices (per-track + master)."""
    OUT = None
    EXTRA = 0            # extra meters beyond L/R/S + bands (master: onset)

    def setUp(self):
        self.p = _load(self.OUT)

    def test_opens_in_presentation(self):
        self.assertEqual(self.p.get("openinpresentation"), 1)

    def test_meter_per_tracked_signal(self):
        n = bands.n_bands()
        meters = [b for b in _pres_boxes(self.p) if b["maxclass"] == "live.meter~"]
        self.assertEqual(len(meters), 3 + n + self.EXTRA)   # L, R, S, bands(, extra)
        # every meter is FED (a patchline into inlet 0) — no dead displays
        for b in meters:
            self.assertTrue(_lines_into(self.p, b["id"]), f"meter {b['id']} unfed")

    def test_meters_fed_by_the_osc_signal_sources(self):
        srcs = {s[0] for b in _pres_boxes(self.p) if b["maxclass"] == "live.meter~"
                for s in _lines_into(self.p, b["id"])}
        for want in ("obj-plugin-in-L", "obj-plugin-in-R", "obj-side-scale",
                     "obj-avg-0", f"obj-avg-{bands.n_bands() - 1}"):
            self.assertIn(want, srcs)

    def test_correlation_readout_wired(self):
        self.assertEqual(_lines_into(self.p, "obj-ui-corr"),
                         [["obj-snapshot-corr", 0]])

    def test_no_buttons_and_fits_device_height(self):
        for b in _pres_boxes(self.p):
            self.assertNotIn(b["maxclass"], BUTTON_CLASSES)
            self.assertNotEqual(b["maxclass"], "toggle")     # enable stays hidden
            x, y, w, h = b["presentation_rect"]
            self.assertLessEqual(y + h, device_ui.DEVICE_H, f"{b['id']} overflows")


class TestPerTrackUI(HubDeviceUI, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bpt.main()
        cls.OUT = bpt.OUT


class TestMasterUI(HubDeviceUI, unittest.TestCase):
    EXTRA = 1            # the fast onset envelope meter

    @classmethod
    def setUpClass(cls):
        bmd.main()
        cls.OUT = bmd.OUT

    def test_onset_meter_fed_from_fast_envelope(self):
        srcs = {s[0] for b in _pres_boxes(self.p) if b["maxclass"] == "live.meter~"
                for s in _lines_into(self.p, b["id"])}
        self.assertIn("obj-onset-env", srcs)


class TestAggregatorUI(unittest.TestCase):
    N_PAIRS, BASE = 8, 32

    @classmethod
    def setUpClass(cls):
        cls.out = bag.main(cls.N_PAIRS, cls.BASE)
        cls.p = _load(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.out.unlink()                     # base-offset variant is test scratch

    def test_one_multislider_per_pair_showing_all_values(self):
        ms = [b for b in _pres_boxes(self.p) if b["maxclass"] == "multislider"]
        self.assertEqual(len(ms), self.N_PAIRS)
        nb = bands.n_bands()
        for b in ms:
            self.assertEqual(b["size"], nb + 1)             # bands + side RMS
        # each fed from ITS pair's pak (the exact list that goes out over OSC)
        for k in range(self.N_PAIRS):
            self.assertEqual(_lines_into(self.p, "ui-ms%d" % k),
                             [["obj-pak%d" % k, 0]])

    def test_labels_show_global_channel_numbers(self):
        labels = {b["text"] for b in _pres_boxes(self.p)
                  if b["maxclass"] == "comment"}
        self.assertIn("c%d" % self.BASE, labels)
        self.assertIn("c%d" % (self.BASE + self.N_PAIRS - 1), labels)

    def test_presentation_on_no_buttons_fits_height(self):
        self.assertEqual(self.p.get("openinpresentation"), 1)
        for b in _pres_boxes(self.p):
            self.assertNotIn(b["maxclass"], BUTTON_CLASSES)
            x, y, w, h = b["presentation_rect"]
            self.assertLessEqual(y + h, device_ui.DEVICE_H)


class TestProbeUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bpr.main()
        cls.p = _load(bpr.OUT)

    def test_pair_meter_present_and_fed(self):
        self.assertEqual(self.p.get("openinpresentation"), 1)
        ms = [b for b in _pres_boxes(self.p) if b["maxclass"] == "multislider"]
        self.assertEqual(len(ms), 1)
        self.assertEqual(ms[0]["size"], bpr.NPAIRS)
        self.assertEqual(_lines_into(self.p, "ui-ms"), [["obj-pak", 0]])


if __name__ == "__main__":
    unittest.main()
