"""
juce_state.py — JUCE plugin-state codec (no pedalboard import; pure stdlib).

pedalboard's ExternalPlugin.raw_state is JUCE's wrapper:
    b"VC2!" + uint32le(xml_len) + b"<VST3PluginState><IComponent>SIZE.DATA</IComponent>..."
where SIZE.DATA is JUCE MemoryBlock::toBase64Encoding — a CUSTOM base64
(alphabet starts with '.', bits packed LSB-first) prefixed by the decoded byte
count and a dot.

The IComponent payload is the plugin's NATIVE component state — the exact same
chunk Ableton stores in the .als as <ProcessorState> (verified on Serum 2:
XferJson header, byte-identical transplant). swap_component() lets us load a
patch captured from a Live project into a headless pedalboard instance.
"""
from __future__ import annotations

import re
import struct

TABLE = ".ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+"
_IDX = {c: i for i, c in enumerate(TABLE)}


def juce_b64_decode(s: str) -> bytes:
    size_s, _, data = s.partition(".")
    size = int(size_s)
    out = bytearray(size)
    bitpos = 0
    for ch in data:
        v = _IDX[ch]
        for b in range(6):
            if v & (1 << b):
                byte_i = (bitpos + b) >> 3
                if byte_i < size:
                    out[byte_i] |= 1 << ((bitpos + b) & 7)
        bitpos += 6
    return bytes(out)


def juce_b64_encode(raw: bytes) -> str:
    bits = len(raw) * 8
    chars = []
    bitpos = 0
    while bitpos < bits:
        v = 0
        for b in range(6):
            p = bitpos + b
            if p < bits and (raw[p >> 3] >> (p & 7)) & 1:
                v |= 1 << b
        chars.append(TABLE[v])
        bitpos += 6
    return f"{len(raw)}.{''.join(chars)}"


def get_component(raw_state: bytes) -> bytes:
    """Extract the plugin-native component chunk from a JUCE raw_state blob."""
    xml = bytes(raw_state)[8:].rstrip(b"\x00").decode("utf-8", errors="ignore")
    m = re.search(r"<IComponent>([^<]+)</IComponent>", xml)
    if not m:
        raise ValueError("no IComponent in JUCE state (not a VST3 wrapper?)")
    return juce_b64_decode(m.group(1))


def swap_component(raw_state: bytes, component: bytes) -> bytes:
    """Return a new JUCE raw_state with the component chunk replaced."""
    xml = bytes(raw_state)[8:].rstrip(b"\x00").decode("utf-8", errors="ignore")
    m = re.search(r"<IComponent>([^<]+)</IComponent>", xml)
    if not m:
        raise ValueError("no IComponent in JUCE state (not a VST3 wrapper?)")
    new_xml = xml[: m.start(1)] + juce_b64_encode(component) + xml[m.end(1):]
    return b"VC2!" + struct.pack("<I", len(new_xml)) + new_xml.encode()
