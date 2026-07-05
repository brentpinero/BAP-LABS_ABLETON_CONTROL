# Headless-vs-Ableton Fidelity: Validation Findings

**Question (user mandate):** *Be 100% sure the headless sandbox truly mirrors mission-critical Ableton audio processing, effects, and third-party VST/AU — validated by measurement, not assumed.*

**Answer:** It does **not** mirror Ableton bit-exact for real Serum patches — and this document proves *why*, which is more actionable than a false "yes." The fix is architectural (two-tier), not a bug hunt.

Test date: 2026-07-03. Test subject: `suicide boys v5` project, track 66 (`67-Serum 2`) — an FX-free, automation-free Serum 2 track (the cleanest possible instrument-parity test).

---

## What was proven solid ✅

1. **Serum patch state transplants byte-identical.** Track 66's 2575-byte `XferJson` `<ProcessorState>` extracted from the `.als` is byte-for-byte (sha `887a0a0e…`) what the headless renderer injects via `juce_state.swap_component`. The JUCE codec + `.als` → pedalboard `raw_state` path works.
2. **`.als` document order == Live LOM `track_index`** in this project (verified idx 66, 106). Not the mapping bug initially suspected.
3. **The injected state applies** — headless render is audibly distinct from Serum's default patch.
4. **Loudness matches** — LUFS delta within ±0.2 dB against the Ableton freeze.
5. **High-mid spectrum roughly agrees** — 250 Hz–16 kHz within ~2 dB.

## What diverges ❌

On the same patch bytes + same note (pitch 27, 16 beats) + same tempo (100 BPM) + no FX + no automation, headless is **consistently bassier/darker** than the Ableton freeze:

| Band | headless vs Ableton freeze |
|---|---|
| 20–60 Hz | +5.6 dB |
| 60–120 Hz | +6.8 dB |
| 120–250 Hz | +15.5 dB |
| 250–500 Hz | +3.1 dB |
| 500–1000 Hz | −2.9 dB |
| 1000–2000 Hz | −1.9 dB |

Null depth is negative (no cancellation). This is a **real timbral difference**, not a measurement artifact.

## Root-cause isolation

| Hypothesis | Method | Verdict |
|---|---|---|
| Plugin format (AU vs VST3) | `.als` shows `Vst3PluginInfo`; headless uses VST3 | ❌ Ruled out — both VST3 |
| Serum version mismatch | `.als` `productVersion` vs installed `Info.plist` | ❌ Ruled out — both **2.1.2** |
| Async content-load / no warmup | 2 s MIDI pre-roll before the note | ❌ Ruled out — gap persists in steady state |
| **Render quality / oversampling** | Re-render headless at 96 kHz | ✅ **Confirmed factor** — dom freq moved 1440 → 1653 Hz toward Ableton's 1927 Hz; LUFS delta → ~0 |
| **External content resolution** | Decompress patch (zstd), inspect refs | ✅ **Primary factor** — see below |

### The decisive finding: patches reference external content, they don't embed it

Track 66's patch payload is `{"product":"Serum2","productVersion":"2.1.2",...}` + a **zstd-compressed** (magic `28 B5 2F FD`) blob that decompresses to 8928 bytes. That blob references factory content **by relative path**, not embedded data:

- `Analog/Basic Shapes.wav` — WT oscillator wavetable
- `S2 Tables/Default Shapes.wav` — table position
- `Factory/Massive/Cold Abyss.flac`, `Factory/Synth/SID Tarkus C2.flac` — Spectral-osc samples

Serum's binary has `SpectralOscController::toggleEmbedContent` — content *can* be embedded, but this patch has it **off**. Serum resolves the relative paths against its content root, stored in `~/Library/Preferences/Serum2Prefs.json`:

```
Serum Presets Path: /Library/Audio/Presets/Xfer Records/Serum 2 Presets/
Use Ultra on Render: (offline-render quality flag)
Default Oversampling Level: (realtime quality)
```

The content exists and is world-readable (`.../Serum 2 Presets/Tables/Analog/Basic Shapes.wav` etc.). But the headless-hosted instance voices the low range differently — consistent with the wavetable/spectral content not resolving or loading identically to Ableton's GUI-configured instance. Combined with the offline-Ultra vs realtime-quality difference, the two renders can't be bit-identical.

## Architectural conclusion

**Byte-identical state transfer is NECESSARY BUT NOT SUFFICIENT.** A Serum patch = state bytes **+** external content (loaded from disk by relative path) **+** a render-quality mode. Headless nails the bytes and misses the other two. For any patch that references factory content — i.e. most real patches — **headless cannot reproduce the final timbre exactly.**

Therefore the honest, achievable architecture is **two-tier**:

- **Headless sandbox** — the fast iterate loop. Validates *composition* and *relative* sound-design direction. Never claims bit-exact timbre.
- **Ableton Freeze** — the ground-truth checkpoint. The only thing that renders the real sound (content + FX + automation + Ultra quality). Runs at explicit, user-approved moments (calibration / post-commit verify), never mid-loop, never borrowing the user's open set unsupervised.

The fidelity registry + review-UI A/B players exist precisely to make this boundary transparent: every measurement is descriptive evidence with audible A/B, and the user's ears are the judge.

## Open work

- **Automation transfer (prioritized).** The sandbox currently copies **no** automation. In this project automation is stored as **clip envelopes** (`<ClipEnvelope>` inside each clip's `<Envelopes>`), *not* track/arrangement-level `<AutomationEnvelopes>` (those are empty here). Building it = (1) parse clip envelopes → `{param: [(time, value)]}` via `PointeeId` → `AutomationTarget` → param mapping; (2) apply time-varying during headless render (block-by-block param setting, since pedalboard's one-shot `plug(midi, duration)` can't automate). Needed for both a representative preview and any valid Freeze-comparison.
- **Confirm instrument-parity ceiling** via a clean scratch-project A/B calibration (never the user's real set): force Ultra/oversampling, verify content resolution, measure the best achievable null depth on one patch.
- **Stock-FX boundary** — EQ Eight / Saturator / Roar / AutoFilter cannot run headless (`live_only`). Full-processed-sound parity is Freeze-only. In this project the 3 FX-free Serum tracks (66/107/110) are sparse sub/stab layers; all real sound design lives on FX+automation tracks.

## Test-methodology gotchas (for reproducing)

- An Ableton freeze wav is the **full arrangement**, stereo, at project SR (48 k here). Slice by **note-onset region**, don't assume t=0 / bar 1. Track 66's freeze had 2 blocks (0–10 s, 57.5–67.5 s) = its 2 clips.
- `sandbox/fidelity.py` `compare()` mono-sums before band math, so file-level mono changes nothing; use `stereo_width()` / `channels` for the width story.
- Use the **real project tempo** (100 BPM here), not a guess — wrong tempo changes note length and spectrum.
- Staged A/B pairs live in the review UI (127.0.0.1:8765) Fidelity tab: `serum2:track66_realpatch`, `serum2:track106_fxboundary`.
