"""
Pure-logic tests for stem_ablation — the ablation ladder, node parsing, sidecars,
and (critically) restore-on-exit — all with a fake client, no Ableton.
Run: python -m unittest test_stem_ablation
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import stem_ablation as sa
from live_client import LiveError
from stem_ablation import NodeChain


class FakeClient:
    """Minimal client.send stand-in: tracks per-device on/off state so restore is
    observable. `no_on_off` device indices raise on set_device_enabled."""

    def __init__(self, enabled=None, no_on_off=(), track_info=None, track_count=0):
        self.enabled = dict(enabled or {})        # (ref, device_index) -> bool
        self.no_on_off = set(no_on_off)           # device indices lacking on/off
        self.track_info = track_info or {}        # track_index -> get_track_info dict
        self.track_count = track_count
        self.calls = []

    def send(self, cmd, params=None):
        params = params or {}
        self.calls.append((cmd, params))
        if cmd == "get_session_info":
            return {"tempo": 120.0, "track_count": self.track_count}
        if cmd == "get_track_info":
            ti = self.track_info.get(params.get("track_index"))
            if ti is None:
                raise LiveError("no such track")
            return ti
        if cmd == "get_device_parameters":
            ref, di = params["track_index"], params["device_index"]
            return {"parameters": [{"name": "Device On",
                                    "value": 1.0 if self.enabled.get((ref, di), True) else 0.0}]}
        if cmd == "set_device_enabled":
            ref, di = params["track_index"], params["device_index"]
            if di in self.no_on_off:
                raise LiveError("Device does not have on/off control")
            self.enabled[(ref, di)] = bool(params["enabled"])
            return {}
        return {}


def _node(ref="0", name="Drums", kind="regular", ndev=3):
    return NodeChain(ref=ref, name=name, kind=kind,
                     devices=[{"index": i, "name": f"D{i}", "class_name": "Eq8"} for i in range(ndev)])


class TestLadder(unittest.TestCase):
    def test_no_devices_single_rung(self):
        lad = sa.ablation_ladder([])
        self.assertEqual(len(lad), 1)
        self.assertEqual(lad[0]["kind"], "no_devices")
        self.assertEqual(lad[0]["enabled_mask"], [])

    def test_ladder_is_n_plus_two_rungs(self):
        lad = sa.ablation_ladder(["a", "b", "c"])
        self.assertEqual(len(lad), 5)                     # N+2
        self.assertEqual([r["index"] for r in lad], [0, 1, 2, 3, 4])

    def test_masks_progress_all_off_to_all_on(self):
        lad = sa.ablation_ladder(["a", "b", "c"])
        self.assertEqual(lad[0]["enabled_mask"], [True, True, True])    # baseline
        self.assertEqual(lad[1]["enabled_mask"], [False, False, False])  # all_off
        self.assertEqual(lad[2]["enabled_mask"], [True, False, False])   # through_0
        self.assertEqual(lad[3]["enabled_mask"], [True, True, False])    # through_1
        self.assertEqual(lad[4]["enabled_mask"], [True, True, True])     # through_2 == baseline
        self.assertEqual([r["newly_enabled"] for r in lad[2:]], ["a", "b", "c"])


class TestNodeParsing(unittest.TestCase):
    def test_node_from_info_defaults_device_index(self):
        info = {"name": "Rev", "kind": "return",
                "devices": [{"name": "Reverb", "class_name": "Reverb"}]}   # no index (returns)
        node = sa.node_from_info("return:0", info)
        self.assertEqual(node.kind, "return")
        self.assertEqual(node.devices[0]["index"], 0)                      # positional fallback

    def test_node_slug_is_filesystem_safe(self):
        self.assertEqual(sa.node_slug(NodeChain(-1, "Master Bus!", "master")), "master_-1_Master-Bus")
        self.assertEqual(sa.node_slug(NodeChain("return:0", "A-Rev", "return")),
                         "return_return-0_A-Rev")


class TestSidecar(unittest.TestCase):
    def test_sidecar_pairs_devices_with_enabled(self):
        node = _node(ndev=2)
        rung = sa.ablation_ladder(["D0", "D1"])[2]        # through_0 -> [True, False]
        sc = sa.sidecar(node, rung, "resample", "x.wav", True, None)
        self.assertEqual([d["enabled"] for d in sc["devices"]], [True, False])
        self.assertEqual(sc["rung"]["label"], "through_0_D0")
        self.assertEqual(sc["render_mode"], "resample")
        self.assertTrue(sc["rendered"])


class TestApplyMask(unittest.TestCase):
    def test_outcomes_ok_and_no_on_off(self):
        node = _node(ref="0", ndev=3)
        client = FakeClient(no_on_off={1})
        out = sa.apply_enabled_mask(client, node, [True, False, True])
        self.assertEqual(out, ["ok", "no_on_off", "ok"])
        self.assertEqual(client.enabled[("0", 0)], True)
        self.assertEqual(client.enabled[("0", 2)], True)


class TestFilterNodes(unittest.TestCase):
    def test_selects_by_ref_alias_and_name(self):
        nodes = [_node("0", "Drums"), _node("3", "Lead Synth"), NodeChain(-1, "Master", "master")]
        self.assertEqual([n.name for n in sa.filter_nodes(nodes, ["master"])], ["Master"])
        self.assertEqual([n.name for n in sa.filter_nodes(nodes, ["lead"])], ["Lead Synth"])
        self.assertEqual([n.ref for n in sa.filter_nodes(nodes, ["0"])], ["0"])
        self.assertEqual(len(sa.filter_nodes(nodes, None)), 3)


class TrackFakeClient:
    """Models a track list with names + arm state, for the capture-sweep test."""
    def __init__(self, tracks):
        self.tracks = list(tracks)         # list of {"name":..., "arm":bool}

    def send(self, cmd, params=None):
        params = params or {}
        if cmd == "get_session_info":
            return {"track_count": len(self.tracks)}
        if cmd == "get_track_info":
            return dict(self.tracks[params["track_index"]], index=params["track_index"])
        if cmd == "set_track_arm":
            self.tracks[params["track_index"]]["arm"] = bool(params["arm"])
            return {}
        if cmd == "delete_track":
            del self.tracks[params["track_index"]]
            return {}
        return {}


class TestCaptureSweep(unittest.TestCase):
    def test_sweep_disarms_and_deletes_all_capture_tracks(self):
        client = TrackFakeClient([
            {"name": "Kick", "arm": False},
            {"name": "ABLCAP_111", "arm": True},        # leftover, still armed -> would co-record
            {"name": "Bass", "arm": False},
            {"name": "ABLCAP_222", "arm": True},        # another leftover
        ])
        removed = sa._sweep_capture_tracks(client)
        self.assertEqual(removed, 2)
        names = [t["name"] for t in client.tracks]
        self.assertEqual(names, ["Kick", "Bass"])       # user tracks untouched
        self.assertFalse(any(t["arm"] for t in client.tracks))

    def test_sweep_noop_when_no_capture_tracks(self):
        client = TrackFakeClient([{"name": "Kick", "arm": False}, {"name": "Bass", "arm": True}])
        self.assertEqual(sa._sweep_capture_tracks(client), 0)
        self.assertEqual([t["name"] for t in client.tracks], ["Kick", "Bass"])  # user arm untouched


class SoloFakeClient:
    """Models track solo state, for the solo-guard test."""
    def __init__(self, solos):
        self.solo = list(solos)                          # bool per track index

    def send(self, cmd, params=None):
        params = params or {}
        if cmd == "get_session_info":
            return {"track_count": len(self.solo)}
        if cmd == "get_track_info":
            return {"index": params["track_index"], "solo": self.solo[params["track_index"]]}
        if cmd == "set_track_solo":
            self.solo[params["track_index"]] = bool(params["solo"])
            return {}
        return {}


class TestSoloGuard(unittest.TestCase):
    def test_detects_and_toggles_solos(self):
        client = SoloFakeClient([False, True, False, True])
        self.assertEqual(sa._soloed_tracks(client), [1, 3])
        sa._set_solos(client, [1, 3], False)
        self.assertEqual(client.solo, [False, False, False, False])
        sa._set_solos(client, [1, 3], True)
        self.assertEqual(client.solo, [False, True, False, True])   # restored exactly


class TestRunAblationRestores(unittest.TestCase):
    def _run(self, render_fn):
        node = _node(ref="0", name="Drums", ndev=3)
        # user's original chain: device 1 was OFF, others ON — must be restored exactly.
        orig = {("0", 0): True, ("0", 1): False, ("0", 2): True}
        client = FakeClient(enabled=dict(orig))
        tmp = tempfile.mkdtemp()                          # persists for assertions (cleaned below)
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        man = sa.run_ablation(client, [node], "resample", tmp, render_fn=render_fn, started_at=1.0)
        files = sorted(p.name for p in Path(tmp).iterdir())
        return client, orig, man, tmp, files

    def test_restores_original_states_and_writes_artifacts(self):
        rendered = []

        def render_fn(node, rung, out_wav):
            Path(out_wav).write_bytes(b"RIFFfake")      # dummy stem
            rendered.append(rung["index"])

        client, orig, man, tmp, files = self._run(render_fn)
        # every device restored to the user's original on/off state
        self.assertEqual({k: client.enabled[k] for k in orig}, orig)
        # N+2 = 5 stems + 5 sidecars + manifest.json
        self.assertEqual(rendered, [0, 1, 2, 3, 4])
        self.assertEqual(sum(1 for f in files if f.endswith(".wav")), 5)
        self.assertEqual(sum(1 for f in files if f.endswith(".json")), 6)  # 5 sidecars + manifest
        self.assertEqual(man["nodes"][0]["n_rungs"], 5)
        sc = json.loads((Path(tmp) /
                         [f for f in files if f.endswith(".json") and f != "manifest.json"][0]).read_text())
        self.assertIn("devices", sc)

    def test_restores_even_when_render_raises(self):
        def render_fn(node, rung, out_wav):
            if rung["index"] == 2:
                raise RuntimeError("render blew up")     # one bad rung
            Path(out_wav).write_bytes(b"RIFFfake")

        client, orig, man, tmp, files = self._run(render_fn)
        self.assertEqual({k: client.enabled[k] for k in orig}, orig)   # still restored
        # the failed rung still produced a sidecar recording the error
        bad = json.loads((Path(tmp) / "regular_0_Drums__rung02_through_0_D0.json").read_text())
        self.assertFalse(bad["rendered"])
        self.assertIn("render blew up", bad["error"])


if __name__ == "__main__":
    unittest.main()
