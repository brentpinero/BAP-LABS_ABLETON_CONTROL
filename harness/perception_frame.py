"""
perception_frame.py — the fixed-shape perception frame + its serializations.

One frame = a musically-timestamped, constant-dimensional snapshot of the mix in
canonical roles + the user's focus. Two forms:
  - to_vector(): fixed-length float vector for the future backbone projector.
  - to_text():   terse lines for the current text-LLM bridge.
  - to_dict()/from_dict(): JSON round-trip for the push snapshot.

Band count B is data-driven from bands.py; role count R from config — nothing
hardcodes 7 or 8. Vector length D is derived from (R,B) and constant per session.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field

import bands as _bands
from masking import Node, adaptive_config, compute_masking
from perception_config import cfg
from perception_roles import RoleAgg, canonical_aggs

# small enums for the focus block (index/len → a normalized scalar)
DEVICE_CLASSES = ["none", "eq", "comp", "reverb", "delay", "saturation", "filter", "gain", "other"]
ACTIONS = ["none", "select", "device_focus", "param_edit", "transport"]


def _clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


@dataclass
class Frame:
    t_wall: float
    bpm: float
    bar: int
    beat: float
    beats_per_bar: int
    playing: bool
    scheme: str
    roles: list
    aggs: list                       # list[RoleAgg], roles order
    masking: dict
    focus: dict = field(default_factory=dict)
    unmapped: list = field(default_factory=list)

    # ---- geometry (constant per (R,B)) ----
    @staticmethod
    def vector_len(roles, scheme) -> int:
        R, B = len(roles), _bands.n_bands(scheme)
        return 6 + R * B + R + R + (R * (R - 1) // 2) + B + (R + B + 2)

    def to_vector(self) -> list:
        roles, scheme = self.roles, self.scheme
        R, B = len(roles), _bands.n_bands(scheme)
        names = _bands.band_names(scheme)
        v: list[float] = []

        # 1) musical time (6)
        bpb = self.beats_per_bar or 4
        beat_phase = (self.beat / bpb) if bpb else 0.0
        hyper = ((self.bar % 4) + beat_phase) / 4.0
        v += [math.sin(2 * math.pi * beat_phase), math.cos(2 * math.pi * beat_phase),
              math.sin(2 * math.pi * hyper), math.cos(2 * math.pi * hyper),
              _clamp(self.bpm / 300.0), 1.0 if self.playing else 0.0]

        # 2) role×band energy (R·B), loudness-weighted, L1-normalized across matrix
        mat = [a.node.band_abs()[:B] + [0.0] * max(0, B - len(a.node.band_abs())) for a in self.aggs]
        tot = sum(sum(row) for row in mat) or 1.0
        for row in mat:
            v += [x / tot for x in row]

        # 3) per-role loudness (R)
        v += [_clamp((a.node.rms_db + 60.0) / 60.0) for a in self.aggs]
        # 4) per-role width (R)
        v += [_clamp(a.width) for a in self.aggs]

        # 5) masking upper-triangle (R(R-1)/2)
        idx = {r: i for i, r in enumerate(roles)}
        score = [[0.0] * R for _ in range(R)]
        for p in self.masking.get("pairs", []):
            i, j = idx.get(p["a"]), idx.get(p["b"])
            if i is not None and j is not None:
                score[i][j] = score[j][i] = p["score"]
        for i in range(R):
            for j in range(i + 1, R):
                v.append(_clamp(math.log1p(score[i][j])))

        # 6) master congestion per band (B)
        cong = {c["band"]: c["congestion"] for c in self.masking.get("master_congestion", [])}
        v += [_clamp(cong.get(nm, 0) / R) for nm in names]

        # 7) focus block: selected-role one-hot (R) + focused-band one-hot (B)
        #    + device-class scalar + last-action scalar
        sel = self.focus.get("selected_role")
        v += [1.0 if r == sel else 0.0 for r in roles]
        fb = self.focus.get("focused_band")
        v += [1.0 if nm == fb else 0.0 for nm in names]
        dc = self.focus.get("device_class", "none")
        v.append((DEVICE_CLASSES.index(dc) if dc in DEVICE_CLASSES else 0) / len(DEVICE_CLASSES))
        act = self.focus.get("last_action", "none")
        v.append((ACTIONS.index(act) if act in ACTIONS else 0) / len(ACTIONS))
        return v

    def to_text(self, topk: int = 3) -> str:
        lvl = " ".join(
            f"{a.role} {a.node.rms_db:.0f}" if a.node.rms_db > -119 else f"{a.role} --"
            for a in self.aggs if a.role != "master")
        master = next((a for a in self.aggs if a.role == "master"), None)
        clashes = " · ".join(
            f"{p['a']}~{p['b']} {p['top_band']}({p['score']:.2f})"
            for p in self.masking.get("pairs", [])[:topk]) or "none"
        crowded = " ".join(
            f"{c['band']}({c['congestion']})"
            for c in self.masking.get("master_congestion", []) if c["congestion"] >= 2) or "none"
        f = self.focus
        user = "none"
        if f.get("selected_role"):
            user = f"{f['selected_role']} selected"
            if f.get("device_class", "none") != "none":
                user += f", {f['device_class']}"
            if f.get("focused_band"):
                user += f" @ {f['focused_band']}"
        return "\n".join([
            f"LIVE MIX @ bar {self.bar}.{int(self.beat)} | {self.bpm:.0f} BPM | "
            f"{'playing' if self.playing else 'stopped'}",
            f"levels(dB): {lvl} | master {master.node.rms_db:.0f}" if master and master.node.rms_db > -119
            else f"levels(dB): {lvl}",
            f"clashes: {clashes}",
            f"crowded: {crowded}",
            f"USER: {user}",
        ])

    def to_dict(self) -> dict:
        return {
            "t_wall": self.t_wall, "bpm": self.bpm, "bar": self.bar, "beat": self.beat,
            "beats_per_bar": self.beats_per_bar, "playing": self.playing,
            "scheme": self.scheme, "roles": self.roles,
            "role_state": {a.role: {"bands": [round(b, 6) for b in a.node.bands],
                                    "rms_db": round(a.node.rms_db, 2),
                                    "width": round(a.width, 4)} for a in self.aggs},
            "masking": self.masking, "focus": self.focus, "unmapped": sorted(self.unmapped),
            "text": self.to_text(cfg("text_topk")),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Frame":
        roles = d["roles"]
        rs = d.get("role_state", {})
        aggs = []
        for r in roles:
            st = rs.get(r, {"bands": [], "rms_db": -120.0, "width": 0.0})
            structural = "master" if r == "master" else "group"
            aggs.append(RoleAgg(r, Node(id=r, name=r, role=structural,
                                        bands=st["bands"], rms_db=st["rms_db"]), st["width"]))
        return cls(t_wall=d["t_wall"], bpm=d["bpm"], bar=d["bar"], beat=d["beat"],
                   beats_per_bar=d["beats_per_bar"], playing=d["playing"], scheme=d["scheme"],
                   roles=roles, aggs=aggs, masking=d["masking"],
                   focus=d.get("focus", {}), unmapped=set(d.get("unmapped", [])))


def build_frame(tracks: dict, transport: dict, focus: dict | None = None,
                override: dict | None = None) -> Frame:
    """Assemble one Frame from the live bridge state + transport + current focus."""
    scheme = cfg("band_scheme", override)
    roles = cfg("roles", override)
    aggs, unmapped = canonical_aggs(tracks, override)
    nodes = [a.node for a in aggs]
    participants, max_pairs, crowded_min = adaptive_config(nodes)
    masking = compute_masking(nodes, scheme_id=scheme, participants=participants,
                              max_pairs=max_pairs, crowded_min=crowded_min)
    return Frame(
        t_wall=time.time(),
        bpm=float(transport.get("bpm", 120.0)),
        bar=int(transport.get("bar", 0)),
        beat=float(transport.get("beat", 0.0)),
        beats_per_bar=int(transport.get("beats_per_bar", 4)),
        playing=bool(transport.get("playing", False)),
        scheme=scheme, roles=roles, aggs=aggs, masking=masking,
        focus=focus or {"selected_role": None, "focused_band": None,
                        "device_class": "none", "last_action": "none"},
        unmapped=unmapped,
    )
