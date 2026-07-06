# SIM — Coverage & Eval Roadmap (are we missing anything / too shallow?)

**Date:** 2026-07-06 · Synthesis of 4 research passes (audio-analysis coverage, Ableton
action coverage, evaluation strategy, aggregator substrate). Sources are cited in each
pass's transcript; the load-bearing ones are linked inline below.

---

## 0. Honest verdict on the nervousness

**You're right to be nervous — and the gaps are nameable, not vague.** We are solid on the
real-time *attention skeleton* (who's loud, who clashes, where the master is crowded), which
is genuinely useful for routing a duplex model's attention. But as a mix/master *analyst* and
*operator* we are shallow in **four specific, fixable places**:

1. **Loudness/dynamics currency is wrong.** We have RMS + sample-peak; we have **no LUFS,
   true-peak, LRA, or crest/PLR/PSR** — the actual vocabulary of mixing/mastering. (We even
   stream peak+RMS but never form the crest ratio.)
2. **Spectral resolution is too coarse to *name* problems.** 7 linear bands, with one `mid`
   bucket spanning 350–2000 Hz (2.4 octaves), can't isolate **mud (200–500)**, **harshness
   (2–5 k)**, or **sibilance (5–10 k)** — the words engineers actually use.
3. **We can perceive but not *act over time*.** No automation-envelope writing, no MIDI-note
   editing/quantize via API — so the model can see a problem and load a device, but can't
   perform half the fixes.
4. **The perception frame is a single snapshot.** No time-varying / dynamics / build /
   transition axis, and masking is role-pairwise only.

**None are dead ends.** Most of #1/#2 are cheap Python/DSP; most action gaps are pure-LOM
(same class of fix as the track-resolver we just shipped). The rest of this doc is the
prioritized fix list **plus the evaluation plan that proves each fix earns its place** before
we commit to it — which is the real answer to "how do we know it's deep enough."

> Correction banked: one research pass read the *superseded* `Mix Analysis Hub (Per-Track).maxpat`
> and concluded we're on 6 dB/oct one-poles. We already shipped + calibrated the **biquad** bank
> (`...(Per-Track Biquad)`), so that fidelity caveat is stale. Coverage gaps below are about
> *what we measure*, independent of filter type.

---

## 1. Perception coverage (what we LISTEN for)

Have today (per-track/group/master): 7-band biquad energy (calibrated), RMS + peak (dB),
broadband mid/side width + correlation, group↔master masking + per-band congestion, transport,
hysteretic events (mask on/off, clip, level-jump). Frame = 130-float fixed vector + terse text.

| Gap | Stage | Why it matters | Where to build | Prio |
|---|---|---|---|---|
| **LUFS** (integ/short/momentary) | mix, master | RMS ≠ perceived loudness; streaming targets are LUFS (BS.1770/R128) | Python (from the L/R stream) | **P0** |
| **True-peak dBTP** | mix, master | sample-peak misses inter-sample overs; our clip detect under-reports | Python (4× oversample) or DSP on master | **P0** |
| **Crest / PLR / PSR** | mix, master | how much compression/limiting is needed; **we already have peak+RMS** | Python (just the ratio) | **P0** |
| **Bark/ERB ~24-band scheme** | mix, master | 7 linear bands too coarse; `bands.py` already swappable | DSP (new `v2` scheme) | **P0** |
| **Named zones: mud / harsh / sibilance** | mix, master | the literal vocabulary of mix notes | Python rollups over v2 bands | **P0** |
| **Spectral scalars** (centroid/flatness/flux/rolloff) | produce, mix | compact timbre descriptors | Python | P1 |
| **Per-band stereo correlation + low-end mono flag** | mix, master | broadband misses the one stereo problem that matters (bass phase) | DSP (per-band M/S) + Python flag | P1 |
| **Reference-track matching** (tonal + loudness delta) | mix, master | the dominant mastering loop (Ozone-style) | Python (store profile + diff) | P1 |
| **Masking → Bark + spreading function** | mix | same-band min-overlap mis-ranks real masking; ~free once v2 bands land | Python | P1 |
| **DC offset** | record | steals headroom; one-line mean check | Python | P1 |
| **Key/scale, tempo-groove, tuning, onsets** | produce | pitch/rhythm, not band energy | **defer to MiniCPM-o raw-audio path** | P2 |
| **Time-varying / dynamics / build axis** | all | frame is a single snapshot (structural blind spot) | frame schema (window/deltas) | P1 |

Refs: [EBU R128](https://tech.ebu.ch/docs/r/r128.pdf) · [Crest/PSR/PLR](https://www.meterplugs.com/blog/2017/05/18/crest-factor-psr-and-plr.html) · [Essentia spectral features](https://essentia.upf.edu/streaming_extractor_music.html) · [mix-clarity via perceptual masking (MPEG PM II)](https://www.mdpi.com/2076-3417/11/20/9578).

**Layer split:** DSP layer owns finer bands + per-band M/S (needs per-sample audio); Python owns
LUFS/dBTP/LRA/PLR/scalars/zones/masking/reference/DC (cheapest iteration, most P0/P1 value);
backbone owns musical semantics (key/groove/tuning).

---

## 2. Action coverage (what we DO)

Have today (~90 MCP tools): session/query, transport, track lifecycle, mixer (now on all node
kinds via the resolver), **recording primitives** (arm/input-routing/record-mode/monitor/loop),
clips session+arrangement (add-only notes), warp read+mode, device params, browser/load, a
**GUI-automation fallback** (split/consolidate/freeze/flatten/export/quantize/group), and a
VST/AU parameter hub.

| Gap | Why it matters | Closable? | Prio |
|---|---|---|---|
| **Edit existing MIDI notes** (vel/length/pitch) | core produce; we're add-only | **LOM now** (`apply_note_modifications`) | **P0** |
| **Delete MIDI notes** | can't erase mistakes | **LOM now** (`remove_notes_extended`) | **P0** |
| **Quantize (LOM)** | retire brittle GUI Cmd+U | **LOM now** (`Clip.quantize`) | **P0** |
| **Write Session-clip automation envelopes** | in-clip mixing moves over time — biggest closable mixing gap | **LOM now** (`automation_envelope().insert_step`) | **P0** |
| **MIDI capture** | "capture what I just played" | **LOM now** (`Song.capture_midi`) | P1 |
| **Scenes** (create/fire/name/capture) | session song structure — zero coverage | **LOM now** | P1 |
| **Session record + overdub** | completes the half-built recording loop | **LOM now** (`trigger_session_record`) | P1 |
| **Warp markers** add/move/remove | actually warp audio (AbletonOSC *lacks* this — we can beat it) | **LOM now** | P1 |
| **Locators/cues** | section navigation | **LOM now** | P1 |
| **Undo/redo, metronome/punch, named macros** | polish | **LOM now** | P2 |
| **Arrangement-timeline automation authoring** | "automate the filter across the drop" | **hard** (`automation_envelope()`=None for arr. clips) | — |
| **Split / consolidate / freeze / flatten / render** | edits + deliverables | **GUI-only** (no LOM) — keep automator | keep GUI |
| **Headless render / export** | deliverables | **no API** — real-time resample or GUI export only | keep GUI/resample |

Refs: [Live API (structure-void)](https://midiremotescripts.structure-void.com/reference/) · [Clip LOM](https://docs.cycling74.com/apiref/lom/clip/) · [Song LOM](https://docs.cycling74.com/apiref/lom/song/).

**The truths you asked for:** automation — *session-clip envelopes ARE writable (P0 win), arrangement-timeline is genuinely not*. Recording — *primitives done, the rest is scriptable*. Warping — *we can add/move markers via LOM (OSC can't)*. Render/export — *no API exists; GUI + resample are correct*. Every new tool inherits all-track-kind addressing for free from the resolver fix.

> Verify exact method signatures against a live `LiveAPI` object before coding — the C74 apiref
> renderer intermittently drops long property lists; cross-checked but confirm `insert_step` arg
> order and the `apply_note_modifications` dict shape live.

---

## 3. How we KNOW it's enough (evaluation plan)

The frame projector (`MixProjector`) is still a `ZeroProjector` stub — so **we can test the
frame's sufficiency NOW, before spending a dollar on backbone training.** That's the cheapest
high-signal validation and directly answers the depth worry.

1. **Probing (build first).** Freeze `to_vector()`, train dead-simple linear probes to decode
   mix properties (which role is masked, is the vocal buried, too bright, LUFS bucket). Do it
   **with control tasks + selectivity** ([Hewitt & Liang 2019](https://aclanthology.org/D19-1275/))
   and **MDL** ([Voita & Titov 2020](https://arxiv.org/pdf/2003.12298)) so we measure the *frame's*
   info, not the probe's power. ([Belinkov 2022](https://direct.mit.edu/coli/article/48/1/207/107571/)).
2. **Ablation.** **Mean-ablate** each feature (drop masking, coarsen 7→3 bands, kill stereo) and
   measure the downstream hit. **Every feature in the vector must earn its slot** — passes neither
   probe nor ablation → cut it. ([Optimal Ablation, Li & Janson 2024](https://lucasjanson.fas.harvard.edu/papers/Optimal_Ablation_For_Interpretability-Li_Janson-2024.pdf)).
3. **Closed-loop task suites.** Use the render node (`sandbox/renderer_live.py`) so *action* tasks
   self-score: apply the model's EQ move → re-render → check the 3 kHz band actually dropped.
   Objective before/after DSP delta, no human. Per-stage tasks (record/produce/mix/master).
4. **Ground truth, cheapest first:** synthetic perturbations (boost 3 kHz +6 dB — the perturbation
   *is* the label) → offline DSP gold (LUFS/masking/tonal) → the `.als` raw→mastered pairs →
   sparse expert calibration → MUSHRA last. Borrow stems from [MedleyDB](https://medleydb.weebly.com/)/[MUSDB18](https://sigsep.github.io/datasets/musdb.html).
5. **Frame ON/OFF A/B** (after the real projector exists) — identical backbone with vs without the
   frame; shallow vs rich; the headline experiment.
6. **Coverage matrix.** Score every task in the [Reiss "Intelligent Music Production"](https://www.routledge.com/Intelligent-Music-Production/Man-Stables-Reiss/p/book/9781138055193)
   taxonomy on **can-perceive? × can-act?** → coverage becomes a **number per stage**, and
   perceive-✓/act-✗ cells are the explicit backlog. This is the antidote to "is it shallow."

**Strategic note:** no existing benchmark couples mix-perception → DAW actions → closed-loop DSP
scoring. That intersection is SIM's defensible, publishable contribution.

---

## 4. Substrate (Phase 2) — aggregator decision

Research says the ~73-instance saturation is structural (per-instance Max runtime, not DSP).
The aggregator collapses **73 → 3 devices** (one M4L device = 64 ch = 32 stereo pairs): inside,
**7 `mc.biquad~` objects** run our exact `bandpass_coeffs` + `pink_gains` across all channels;
sources feed in via a **capture-track layer** (thin, zero-Max-code routing tracks, non-destructive
Post-FX tap), and *our automation owns the channel→track-id map*.

**⚠️ Validate ONE thing first (10-min probe, not the full build):** does `output_routing_channel`
enumerate + select an individual `plugin~` input *pair* of a multi-input M4L device via LOM/OSC,
and does it stick? Build a trivial `mc.plugin~ 4` device + 3 capture tracks + meters; confirm each
pair lights independently. Green → whole architecture is automatable. (Design the aggregator to
carry the **v2 Bark scheme** from §1 so the substrate + resolution upgrades land together.)

Refs: [Audio Routes](https://cycling74.com/articles/audio-routings-a-new-system-for-multi-channel-routing-in-ableton-live) · [mc.biquad~](https://docs.cycling74.com/reference/mc.biquad~/) · [AbletonOSC routing](https://github.com/ideoforms/AbletonOSC).

---

## 5. Prioritized cross-cutting roadmap

**Do now (cheap, high-signal, no Ableton/backbone needed):**
- **E1** Synthetic-perturbation generator + offline DSP gold (LUFS/masking/tonal) over rendered stems.
- **E2** Probing harness (control tasks + selectivity + MDL) over `to_vector()` → *first real "is it deep enough" answer.*
- **A-P0** Python loudness/dynamics pack: **LUFS + true-peak + LRA + PLR/PSR** (feeds probes as gold too).

**Do next (LOM tool adds — same class as the resolver fix, one Remote Script pass + reload):**
- **T-P0** MIDI note edit/delete + `quantize` + **session-clip automation envelope write**.
- **E3** Ablation grid (mean-ablation) → first keep/cut verdict per frame feature.

**Then (bigger builds):**
- **B1** `v2` Bark/ERB band scheme + named zones + spectral scalars; upgrade masking to spreading-function (perception depth).
- **B2** Aggregator: routing-channel probe → build 3 aggregators on the v2 scheme (substrate).
- **E4** Closed-loop per-stage task suite via the render node.
- **T-P1** capture_midi, scenes, session-record/overdub, warp markers, locators.

**Later:** frame ON/OFF A/B (post-projector), coverage matrix as a living scorecard, MUSHRA.

**Kept on GUI automation (correct as-is):** split/consolidate, freeze/flatten, export/render,
comping, arrangement time surgery. **Genuinely hard (park):** arrangement-timeline automation,
headless render, tempo curves.
