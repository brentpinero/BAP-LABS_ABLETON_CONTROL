"""
Tests for perception_select.select_nodes — the Phase 3 provisioning heuristic.
Pure Python. Run: python -m unittest test_perception_select
"""

import unittest

from perception_select import select_nodes, selection_summary


def nd(ref, name, kind="audio", gid="-1", rms=None):
    return {"ref": ref, "name": name, "kind": kind, "group_id": gid, "rms_db": rms}


class TestSelect(unittest.TestCase):
    def _refs(self, sel):
        return [s["ref"] for s in sel]

    def test_master_and_groups_always_kept(self):
        nodes = [nd(-1, "Main", "master"), nd(2, "Drums", "group"), nd(5, "Bass", "group"),
                 nd(10, "Audio 1"), nd(11, "Zxq")]
        sel = select_nodes(nodes)
        refs = self._refs(sel)
        self.assertIn(-1, refs)
        self.assertIn(2, refs)
        self.assertIn(5, refs)
        # master ranks first
        self.assertEqual(sel[0]["ref"], -1)

    def test_named_leaf_beats_unnamed(self):
        nodes = [nd(10, "Kick"), nd(11, "Audio 7"), nd(12, "Reese Bass")]
        sel = select_nodes(nodes)
        # named (Kick, Reese Bass) rank above the generic "Audio 7"
        self.assertLess(self._refs(sel).index(10), self._refs(sel).index(11))
        self.assertIn("named:drums", sel[self._refs(sel).index(10)]["reasons"])

    def test_focus_overrides(self):
        nodes = [nd(10, "Audio 1"), nd(11, "Audio 2")]
        sel = select_nodes(nodes, focus_ref=11)
        self.assertEqual(sel[0]["ref"], 11)
        self.assertIn("focused", sel[0]["reasons"])

    def test_capacity_cap(self):
        nodes = [nd(-1, "Main", "master")] + [nd(i, "Audio %d" % i) for i in range(50)]
        sel = select_nodes(nodes, override={"select_capacity": 8})
        self.assertEqual(len(sel), 8)
        self.assertIn(-1, self._refs(sel))          # master survives the cap

    def test_loud_beats_quiet_leaf(self):
        nodes = [nd(10, "Audio 1", rms=-6.0), nd(11, "Audio 2", rms=-55.0)]
        sel = select_nodes(nodes)
        self.assertEqual(sel[0]["ref"], 10)          # louder generic track ranks first
        self.assertIn("loud", sel[0]["reasons"])

    def test_flat_project_no_groups(self):
        # ungrouped project: named leaves still get selected, master kept
        nodes = [nd(-1, "Main", "master"), nd(0, "Kick"), nd(1, "Bass"), nd(2, "Vocals"),
                 nd(3, "Synth Lead"), nd(4, "Random Audio")]
        sel = select_nodes(nodes)
        refs = self._refs(sel)
        for r in (-1, 0, 1, 2, 3):
            self.assertIn(r, refs)
        s = selection_summary(sel)
        self.assertIn("named", s)

    def test_returns_included_low_priority(self):
        nodes = [nd(-1, "Main", "master"), nd("return:0", "A-Reverb", "return"),
                 nd(0, "Kick")]
        sel = select_nodes(nodes)
        self.assertIn("return:0", self._refs(sel))


if __name__ == "__main__":
    unittest.main()
