"""
Tests for the streaming perception foundation: role canonicalization (fixed shape),
frame vector geometry, focus encoding, and dict round-trip. Pure Python — no Max,
no Ableton. Run:  python -m unittest test_perception -v
"""

import unittest

import bands
import perception_frame as pf
from mix_analysis_bridge import TrackState
from perception_config import DEFAULTS
from perception_roles import canonical_aggs, role_of


def ts(tid, name, kind="audio", gid="-1", b=None, rms=-8.0, mid=0.5, side=0.1):
    return TrackState(track_id=str(tid), name=name, kind=kind, group_id=str(gid),
                      bands=(b if b is not None else [0.3, 0.25, 0.15, 0.1, 0.1, 0.05, 0.05]),
                      rms_l=rms, rms_r=rms, mid_energy=mid, side_energy=side)


ROLES = DEFAULTS["roles"]
SCHEME = DEFAULTS["band_scheme"]
TRANSPORT = {"bpm": 128.0, "bar": 41, "beat": 2.0, "beats_per_bar": 4, "playing": True}


class TestCanonicalization(unittest.TestCase):
    def test_constant_D_for_0_3_70_tracks(self):
        want = pf.Frame.vector_len(ROLES, SCHEME)
        for tracks in ({},
                       {"1": ts(1, "Drums", "group"), "2": ts(2, "Bass", "group"), "3": ts(3, "Vox", "group")},
                       {str(i): ts(i, f"synth {i}") for i in range(70)}):
            frame = pf.build_frame(tracks, TRANSPORT)
            self.assertEqual(len(frame.to_vector()), want, f"D drift for {len(tracks)} tracks")

    def test_nested_group_inherits_top_role(self):
        tracks = {
            "1": ts(1, "Drums", "group", "-1"),
            "2": ts(2, "Percussion", "group", "1"),   # nested under Drums
            "3": ts(3, "shaker", "audio", "2"),        # leaf under Percussion
        }
        rmap, rr = DEFAULTS["role_map"], DEFAULTS["return_role"]
        self.assertEqual(role_of(tracks["3"], tracks, rmap, rr), "drums")

    def test_two_synth_groups_sum_into_one(self):
        tracks = {
            "1": ts(1, "Synths", "group", b=[0.0, 0.0, 0.1, 0.4, 0.3, 0.1, 0.1], rms=-6),
            "2": ts(2, "Lead Synth", "group", b=[0.0, 0.0, 0.1, 0.4, 0.3, 0.1, 0.1], rms=-6),
        }
        aggs, _ = canonical_aggs(tracks)
        synth = next(a for a in aggs if a.role == "synth")
        # two equal -6 dB busses summed → louder than either (≈ +6 dB)
        self.assertGreater(synth.node.rms_db, -3.0)
        self.assertTrue(any(x > 0 for x in synth.node.bands))

    def test_unmapped_to_other(self):
        tracks = {"1": ts(1, "Zxqwq Thing")}
        aggs, unmapped = canonical_aggs(tracks)
        self.assertIn("Zxqwq Thing", unmapped)
        self.assertTrue(any(a.role == "other" and any(x > 0 for x in a.node.bands) for a in aggs))

    def test_return_to_fx(self):
        rmap, rr = DEFAULTS["role_map"], DEFAULTS["return_role"]
        self.assertEqual(role_of(ts(1, "A-Reverb", "return"), {}, rmap, rr), "fx")

    def test_sub_before_bass(self):
        rmap, rr = DEFAULTS["role_map"], DEFAULTS["return_role"]
        self.assertEqual(role_of(ts(1, "Sub Bass", "audio"), {}, rmap, rr), "sub")
        self.assertEqual(role_of(ts(2, "Reese Bass", "audio"), {}, rmap, rr), "bass")


class TestFrameGeometry(unittest.TestCase):
    def test_D_adjusts_for_band_scheme(self):
        bands.SCHEMES["test_3band"] = [("lo", 20, 250), ("mid", 250, 4000), ("hi", 4000, 20000)]
        try:
            ov = {"band_scheme": "test_3band"}
            want = pf.Frame.vector_len(ROLES, "test_3band")
            frame = pf.build_frame({"1": ts(1, "Bass", "group")}, TRANSPORT, override=ov)
            self.assertEqual(len(frame.to_vector()), want)
            self.assertLess(want, pf.Frame.vector_len(ROLES, SCHEME))  # fewer bands → shorter
        finally:
            del bands.SCHEMES["test_3band"]

    def test_focus_block_encodes_selection(self):
        tracks = {"1": ts(1, "Bass", "group")}
        focus = {"selected_role": "bass", "focused_band": "low",
                 "device_class": "eq", "last_action": "select"}
        frame = pf.build_frame(tracks, TRANSPORT, focus=focus)
        self.assertIn("bass selected", frame.to_text())
        self.assertIn("eq", frame.to_text())
        # the selected-role one-hot slot for bass must be hot in the vector
        v = frame.to_vector()
        R, B = len(ROLES), bands.n_bands(SCHEME)
        focus_start = 6 + R * B + R + R + (R * (R - 1) // 2) + B
        sel_onehot = v[focus_start:focus_start + R]
        self.assertEqual(sel_onehot[ROLES.index("bass")], 1.0)


class TestSerialization(unittest.TestCase):
    def test_dict_round_trip(self):
        tracks = {"1": ts(1, "Drums", "group"), "2": ts(2, "Bass", "group", rms=-6)}
        frame = pf.build_frame(tracks, TRANSPORT,
                               focus={"selected_role": "drums", "focused_band": None,
                                      "device_class": "comp", "last_action": "device_focus"})
        d1 = frame.to_dict()
        d2 = pf.Frame.from_dict(d1).to_dict()
        self.assertEqual(d1["role_state"], d2["role_state"])
        self.assertEqual(d1["focus"], d2["focus"])
        self.assertEqual(d1["bar"], d2["bar"])
        self.assertEqual(d1["text"], d2["text"])


class _Node:
    def __init__(self, rms): self.rms_db = rms
class _Agg:
    def __init__(self, role, rms=-8.0, peak=-6.0):
        self.role, self.node, self.peak_db, self.width = role, _Node(rms), peak, 0.0
class _Frame:
    def __init__(self, t, pairs=(), aggs=()):
        self.t_wall, self.bar, self.beat = t, 1, 0.0
        self.masking = {"pairs": list(pairs)}
        self.aggs = list(aggs)

def _pair(score): return {"a": "bass", "b": "drums", "score": score, "top_band": "low"}


class TestEvents(unittest.TestCase):
    def _detector(self):
        from perception_stream import EventDetector
        return EventDetector()

    def test_mask_hysteresis_single_on_off(self):
        d = self._detector()
        got = []
        for score in [0.0, 0.0, 0.0]:            # off
            got += d.update(_Frame(0, [_pair(score)]))
        for score in [0.2, 0.2, 0.2, 0.2]:       # cross T_on, dwell -> one mask_on
            got += d.update(_Frame(0, [_pair(score)]))
        for score in [0.1, 0.1]:                 # between T_off/T_on -> stays on, no flap
            got += d.update(_Frame(0, [_pair(score)]))
        for score in [0.02, 0.02, 0.02]:         # cross T_off, dwell -> one mask_off
            got += d.update(_Frame(0, [_pair(score)]))
        ons = [e for e in got if e.type == "mask_on"]
        offs = [e for e in got if e.type == "mask_off"]
        self.assertEqual(len(ons), 1)
        self.assertEqual(len(offs), 1)
        self.assertEqual(ons[0].band, "low")

    def test_clip_rearm(self):
        d = self._detector()
        seq = [-6.0, -0.1, -0.1, -0.1, -5.0, -0.1]   # fire, hold, rearm, fire
        got = []
        for pk in seq:
            got += d.update(_Frame(0, [], [_Agg("drums", peak=pk)]))
        self.assertEqual(len([e for e in got if e.type == "clip"]), 2)

    def test_level_jump_refractory(self):
        d = self._detector()
        got = []
        got += d.update(_Frame(0.0, [], [_Agg("bass", rms=-20)]))
        got += d.update(_Frame(0.1, [], [_Agg("bass", rms=-8)]))   # +12 dB -> one jump
        got += d.update(_Frame(0.2, [], [_Agg("bass", rms=-8)]))   # refractory -> none
        jumps = [e for e in got if e.type == "level_jump"]
        self.assertEqual(len(jumps), 1)
        self.assertEqual(jumps[0].dir, "up")


if __name__ == "__main__":
    unittest.main()
