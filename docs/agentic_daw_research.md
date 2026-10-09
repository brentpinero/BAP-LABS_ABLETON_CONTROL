# Agent-Native DAW: Research and Production Plan

Date: 2026-10-04. Not legal advice; have an IP attorney review sections 2 and 10 before any commercial release.

## How to read this document

Every claim carries an evidence tag:

| Tag | Meaning |
|---|---|
| **[V3]** | Verified by the deep-research harness: fetched from the source and confirmed by three independent adversarial verifiers (3-0 vote) |
| **[V1]** | Fetched and read by a single research agent this session; not adversarially verified |
| **[B]** | Standard published literature or common industry knowledge, cited from background knowledge; **not fetched this session** |
| **[I]** | Inference or design judgement made in this report |
| **[BENCH]** | Unknown until measured; a benchmark in section 12 resolves it |

Research volume: three deep-research runs (325 agents, 74 claims verified, 0 refuted) plus eight targeted research agents. The harness verifies only its top ~25 claims per run, so coverage is uneven. Section 15 lists what remains unverified. Where evidence is missing, this plan substitutes a measured acceptance test for a claim.

---

## 0. Executive summary

1. **The lane is open.** No shipped DAW has an agent API as its primary interface [V1]. Mozart AI, Suno Studio and FL Studio 2026's Gopher are chat layered on a GUI. Ableton's Extensions SDK (beta, June 2026) only runs from a right-click and has no headless mode [V1].
2. **Reverse engineering is mostly unnecessary, and the risky kind should be avoided.** Functionality, workflows and file formats are not copyrightable (SAS v. WPL [V1]). Ableton's EULA §5(1) bans decompiling [V1] and *Bowers v. Baystate* makes such clauses enforceable in the US [V1]. The clean path is black-box measurement of Live's behaviour, which section 3 turns into a spec.
3. **"DAWs sound different" is mostly defaults, not summing magic.** The one cross-DAW difference verified by measurement is pan law: up to 3 dB at centre between DAWs at identical settings [V3]. Live's own fact sheet documents the rest of its non-neutral operations (sample-rate conversion, Complex warp, clip-edge fades, delay-compensation gaps) [V3]. Each becomes a selectable, tested behaviour in our engine.
4. **The engine choice cannot be made from published data.** Public performance numbers for Tracktion Engine, and its automation resolution, summing width and headless behaviour, were not findable [V1]. The decision is therefore a 4-week benchmark bake-off (Phase 0) with twelve pass/fail gates, not a pick from a feature list.
5. **Competitive stock devices are buildable from published DSP**, but most high-quality open implementations are GPL [V3]. For a closed product, devices must be implemented from the papers, with a parity harness measuring them against commercial references.
6. **Agent-authored devices are a differentiator nobody ships.** A proof of concept exists (natural language → Faust → JIT → hot-swap into a live plugin) [V1]. Building this into the DAW gives agents the ability to write new effects and MIDI tools, not only turn knobs.

**Decisions taken 2026-10-05:** the project is **open source under GPLv3**, and the UI follows Live's general shape at the idea level only (session grid, arrangement, racks, device chain), never its pixels. The method is a **measured feedback loop**: the same probes run against the reference (Live, plus reference plugins for devices) and against the candidate, and the gap is the work list. GPLv3 makes Tracktion Engine, JUCE, chowdsp, Surge's DSP, Rubber Band and the FDN toolbox directly usable, which shortens Phase 4 by months [I].

Estimated effort for a solo developer with AI coding agents: roughly 18 to 24 months to a credible beta [I]. Section 11 breaks this down with acceptance criteria per phase.

---

## 1. The problem, measured in this repo

| Evidence | Value | Source |
|---|---|---|
| Separate access layers needed to control Live | 6 (Remote Script socket, M4L devices, OSC ports, AppleScript GUI automation, `.als` parsing, Extensions SDK) | Repo sweep |
| MCP tools exposed | 77 across 13 categories; 16 are GUI keystroke wrappers | `harness/unified_mcp_bridge.py` |
| Programmatic full-mix render | None; worked around with real-time resampling, 3–5 s per track after load | `docs/sandbox_research_brief.md` |
| Headless render fidelity | Serum renders 5–15 dB different in 20–250 Hz vs. in-Live | `docs/sandbox_research_brief.md` |
| Remote Script threading | Main thread only, ~100 ms tick | [V1] AbletonOSC paper (NIME 2023) |
| Extensions SDK autonomy | Right-click launch only; no events, no long-running process | [V1] Ableton docs |

Design consequence [I]: one write path, one read path, one render path. Sections 9 and 11 hold the target numbers.

---

## 2. Legal and ethical boundary

### 2.1 What the law protects

| Point | Evidence |
|---|---|
| Program functionality, programming languages and data file formats are not protected by copyright in the EU | [V1] SAS Institute v. World Programming (CJEU 2012) |
| Reverse engineering for compatibility can be fair use when the final product contains none of the original code | [V1] Sega v. Accolade (9th Cir. 1992); Sony v. Connectix (9th Cir. 2000) |
| These cases concern interoperability, not building a competitor; they are not a general licence | [I] |
| Ableton EULA §5(1): "You may not translate, reverse engineer, decompile, disassemble, or create derivative works from the Ableton Product" | [V1] ableton.com/en/eula |
| Anti-reverse-engineering clauses are enforceable as contract in the US even where fair use would excuse copyright | [V1] Bowers v. Baystate (Fed. Cir. 2003) |
| EU decompilation rights (Directive 2009/24/EC Art. 6) cannot be contracted away, but cover only interoperability and bar building a substantially similar program | [V1] |
| DMCA §1201(f) permits circumvention only for interoperability analysis of elements not otherwise available | [V1] |
| Ableton's listed patents are all Push hardware (US 8,822,803; 10,248,151; 10,840,041; 10,418,011; 11,727,905; D803,814) | [V1] ableton.com/en/legal/patents ("may not be all-inclusive") |
| No Ableton software patents on clip launching or warping were found | [V1] limited search; not a freedom-to-operate opinion |
| Bitwig was founded by ex-Ableton engineers who wrote all-new code; no legal dispute found | [V1] |
| Bitwig imports Live sets directly | [V1] bitwig.com |

### 2.2 Operating rules

| Zone | Activity |
|---|---|
| **Safe** | Black-box measurement of Live (render test signals, analyse output); public manuals, fact sheet, LOM docs; parsing your own `.als` files; reimplementing concepts; "imports Ableton Live sets" as a nominative statement |
| **Gray, avoid by default** | Reading community-decompiled Remote Scripts; reusing Ableton feature names ("Session View", "Groove Pool", "Complex Pro"); close visual imitation |
| **Never** | Disassembling the Live binary; defeating authorization; porting decompiled code; shipping factory content, samples or presets; "Ableton", "Live", "Push", "Max for Live" in product naming; reading GPL source and then writing the closed equivalent from memory |

### 2.3 Clean-room protocol for this project [I]

1. Every behavioural spec item cites a public document or a black-box measurement stored in the repo with the test signal and script.
2. DSP is implemented from papers. Each device has a provenance note listing the papers used.
3. No GPL or AGPL source is opened by the person or agent writing the equivalent closed component.
4. A dated design log records the source for each decision.

### 2.4 Outstanding legal work

- Freedom-to-operate search on DSP patents (time-stretch, pitch correction, amp modelling) before commercial launch. No patent data survived verification in this research.
- Trademark search on the product name and on generic feature names.
- One research agent "recalled" Ableton warping patents without checking; the direct patent search found none. Treat as unresolved until counsel confirms.

---

## 3. Why DAWs sound different, and the audio-quality spec that follows

The honest headline: of ten suspected causes, only a few have verified evidence. The widely repeated claim that all DAWs null bit-for-bit once settings are matched was **neither confirmed nor refuted** by verified sources. The measured blog series that makes this claim (Admiral Bumblebee, "DAW v DAW") was fetched, but that specific claim was not among those put through verification. A claim that REAPER uses 64-bit processing with sample-accurate automation was **refuted** in verification (1-2 vote) and is not relied on here.

### 3.1 Evidence and resulting spec

| # | Factor | What is verified | Size of effect | Our spec | Acceptance test |
|---|---|---|---|---|---|
| 1 | **Pan law** | Three families at defaults (2019 versions, 1 kHz sine): centre cut 3 dB (Cubase, Pro Tools), centre unity with +3 dB at hard pan (Live, FL Studio, Logic), no compensation (Studio One) [V3, single author's measurement]. Live's law confirmed by its fact sheet: constant power, sinusoidal, 0 dB centre, +3 dB at sides [V3] | Up to 3 dB at centre | Selectable law per project: −3 dB centre constant-power default [I], plus 0/+3 dB (Live-compatible), −4.5, −6, linear. `.als` import selects the Live-compatible law | Pan sweep of 1 kHz sine; gain error ≤ 0.01 dB vs. analytic curve at 101 points |
| 2 | **Summing precision** | Live sums in 64-bit at each mix point; other processing is 32-bit, so chains of mix points incur "an extremely small amount of signal degradation" (unquantified) [V3, vendor statement] | Unquantified | 64-bit float end to end between devices; 32-bit only at plugin boundaries that require it | 100 tracks at −0.1 dBFS: residual vs. double-precision reference ≤ −140 dBFS |
| 3 | **Sample-rate conversion** | Live's SRC is non-neutral in playback and render; export uses the SoX resampler [V3]. REAPER offers selectable modes up to r8brain-free [V3]. Infinite Wave tests only 96→44.1 kHz with a −6 dBFS sweep on a 180 dB scale, so visible artefacts may be inaudible [V3]. No per-DAW results verified | Unverified per DAW | One high-quality SRC for both realtime and offline; no separate "Hi-Q" switch | Infinite Wave-style sweep at 96→44.1, 44.1→48 and 48→44.1: passband ripple ≤ 0.01 dB to 20 kHz, aliasing ≤ −120 dBFS [I thresholds] |
| 4 | **Warp at 1:1** | Live's Beats, Tones, Texture and Re-Pitch are neutral at original tempo; Complex and Complex Pro are never neutral [V3] | Mode-dependent | Stretcher bypassed at ratio 1.0 and zero transposition in every mode | Null test at 1:1: bit-identical to source |
| 5 | **Warp quality** | REAPER ships élastique 3.3 and 2.28, SoundTouch, Rubber Band and its own modes [V3]. Bungee's page compares 11 stretchers on frequency error, noise, transient response and onset displacement; vendor-run, rankings not citable [V3]. Tracktion Engine supports Élastique Pro, SoundTouch, Rubber Band [V1] | Unverified | Pluggable stretch backends; ship Signalsmith Stretch (MIT) and Bungee (MPL-2.0); élastique as an optional licensed upgrade | Re-implement Bungee's metric set (cents error, tone/noise dB, onset displacement ms) at ratios 0.5–2.0; publish our own table |
| 6 | **Clip-edge fades** | Live applies fades of up to 4 ms at clip edges and 4 ms crossfades between adjacent arrangement clips, as a preference [V3] | ≤ 4 ms | Default-on, defeatable edge fade; length and curve stored per clip in the document | Click test: discontinuity at clip edge ≤ −90 dBFS broadband with fade on; bit-exact edge with fade off |
| 7 | **Delay compensation** | Live compensates audio, automation and modulation, with documented exceptions: transport-synced device modulation after high-latency devices, and returns routed back into tracks with an active send [V3, vendor statement]. Ardour 6 claims sample-accurate compensation on every path [V1]. Tracktion fixed a rack-latency render bug recently (PR #442) [V1] | Up to the device latency | Compensation on every path including sends, sidechains, automation and synced modulation | Nested rack with a 2048-sample plugin on a send and a master plugin: sample-exact null vs. reference |
| 8 | **Automation resolution** | No verified data for any DAW. Pro Tools online-bounce variance (reported up to 100 ms) was extracted from the Admiral Bumblebee series but not verified | Unverified | Sample-accurate parameter events for internal devices; per-block ramps with sample offsets for plugins (CLAP and VST3 both carry sample offsets [B]) | Gain ramp vs. analytic reference: timing error < 1 sample |
| 9 | **Render vs. realtime** | Not verified for any DAW. Repo's own measurement: headless plugin host vs. Live differs 5–15 dB in the bass | Large in our own data | One engine for both; offline is the same graph run faster | Realtime capture vs. offline render of the same project: null ≤ −120 dBFS with deterministic plugins |
| 10 | **Dither, headroom, denormals, oversampling of stock devices** | Nothing verified | Unknown | Explicit: no clipping inside the float bus; TPDF dither only at fixed-point export, default on for 16-bit; flush-to-zero set identically in realtime and offline | Covered by tests 2, 9 and the device tests in section 6 |

### 3.1a Phase 0 measurements to date (2026-10-08)

Same probes (`daw_bench/profile.py`), three targets, all measured. Live 12 at 44.1 kHz on Brent's default template (master chain bypassed for the run, source fader at 0 dB).

| Probe | Reference engine (`ref_engine.py`, the spec) | Tracktion Engine as shipped | Tracktion with options (`sincBest`, −3 dB law, 4 ms fades) | Live 12 (measured 2026-10-08) |
|---|---|---|---|---|
| Pan law | `sin_-3_0`, fit error 0.000 dB | **`linear_0_+6`**: linear, 0 dB centre, +6 dB hard-panned, fit error 0.000 dB | `sin_-3_0`, fit error 0.000 dB | **`sin_0_+3`, fit error 0.000 dB** (matches the fact sheet exactly) |
| Unity playback (same-rate file) | latency 0, gain 0.000 dB, residual −104 dBFS (edge fades on) / < −140 off | latency 0, gain 0.000 dB, **residual −172 dBFS** (bit-transparent) | latency 0, **residual −35 dBFS**: the sinc resampler stays in the path at ratio 1:1 | gain 0.000 dB, **residual −149 dBFS** (bit-transparent); capture offset 8704–9216 samples varies by one 512 buffer between runs (record path, not playback) |
| Clip-edge fade | 4 ms raised-cosine (reads 3.3 ms) | **0.02 ms: none** | 3.7 ms (linear) | **0.02 ms: none** on an API-created clip in this template (the fade preference is off, or does not apply to API-created clips) |
| SRC, 96 kHz file in 48 kHz project | ripple 0.001 dB, alias −122 dB | ripple 0.001 dB, **alias 0 dB**: no anti-alias filtering on the direct-read path (Lagrange); enabling proxies changed nothing for an unwarped clip | ripple 0.001 dB, **alias −142 to −145 dB** (libsamplerate best) | 88.2→44.1 kHz: ripple 0.004 dB, **alias −69 dB** (an earlier run at 12 dB lower level read −81 dB; repeat before relying on the figure) |

What this says, measured rather than assumed [I from the numbers above]:

0. Live's pan law and 1:1 playback transparency match its documentation exactly; the first black-box measurements agree with the fact sheet, which validates the harness against a known reference.
1. Tracktion's playback path is bit-transparent at 1:1 with its defaults, which is the property that matters most for a render oracle.
2. Its defaults fail three spec items (pan law, edge fades, SRC aliasing), and all three are fixable with existing per-clip/per-track settings, so these are configuration gaps, not engine gaps.
3. One engine gap: with sinc resampling selected, the resampler is not bypassed at 1:1 (residual −35 dBFS, +0.05 dB gain). The spec requires bypass at ratio 1.0; this is the first item for a Tracktion fork or a fix upstream.
4. Live's real-time SRC sits at roughly −70 to −80 dB aliasing: audibly fine, but 50–70 dB short of the reference engine and of Tracktion's sinc option. The spec's −120 dB target is therefore an improvement over Live, not parity.
5. The gate for Phase 1 therefore becomes: Tracktion configured to the spec must null against `ref_engine.py` at ≤ −120 dBFS on the unity probe. Today it does not, by 85 dB.

### 3.1b Warp at ratio 1:1, measured 2026-10-08

Probe: `daw_bench/profile.py::probe_warp`. A 3 s noise clip warped with clip tempo equal to the set tempo (stretch ratio exactly 1.0), one capture per stretch mode; residual after alignment and gain match against the source.

| Target | Mode | Residual (dBFS) | Null depth (dB) | Note |
|---|---|---|---|---|
| Live 12 | Beats, Tones, Texture, Re-Pitch | −149 | 120 (bit-transparent) | matches the fact sheet: neutral at original tempo |
| Live 12 | Complex | **−68** | 48 | never neutral, as documented; output also lands 1,025 samples earlier than the other modes |
| Live 12 | Complex Pro | **−70** | 50 | never neutral, as documented |
| Tracktion Engine + Signalsmith Stretch (MIT) | signalsmithDefault, signalsmithCheaper | −150 | 120 (bit-transparent) | stretcher is bypassed or exact at ratio 1.0 |
| Reference engine | bypass | −104 (edge fades) / < −140 with fades off | — | the spec |

Reading [I]: Live's two highest-quality modes alter audio even when they have nothing to do; the spec's "bypass the stretcher at ratio 1.0 in every mode" is already met by Tracktion with Signalsmith and is a measurable improvement over Live. Signalsmith Stretch is MIT and header-only, so it is the default stretcher for the engine; élastique stays an optional upgrade.

### 3.2 Measuring the incumbents ourselves [I]

Because public data is thin, Phase 0 includes a black-box characterisation of Live (which Brent owns) using the same harness: pan curve, SRC sweep, 1:1 warp null, fade shape, delay-compensation alignment, limiter overshoot. This is legal black-box observation and produces the "Live-compatible" profile.

### 3.3 What has to be owned [I]

Only Live is required. Most targets in this plan are absolute (analytic pan curves, ITU and AES standards, a double-precision summing reference, an exact automation ramp) and need no other DAW.

| Item | Needed for | Status |
|---|---|---|
| Ableton Live | "Live-compatible" profile so imported `.als` sets sound right; stock-device parity baseline | Owned; **required** |
| REAPER | External render check during development | Free evaluation, low-cost licence; **recommended** |
| FabFilter Pro-L 2, Pro-Q | Limiter and EQ parity references; run inside any host, including ours | Trial, then buy the ones kept as permanent references; **recommended** |
| Logic, Cubase, Studio One, Bitwig, FL Studio, Pro Tools | Extra comparison points only | Optional; trial or free tiers where their terms allow rendering (terms not verified this session) |

Hard parity gates in this plan reference Live's stock devices plus the reference plugins above. No gate depends on a DAW other than Live.

---

## 4. Master bus and limiter spec

### 4.1 Verified evidence

| Item | Finding |
|---|---|
| Loudness measurement | ITU-R BS.1770-5: 400 ms blocks, 75% overlap, absolute gate −70 LKFS, relative gate −10 dB [V3] |
| True-peak reference | 4x oversampling, FIR low-pass, absolute value [V3] |
| Meter under-read by oversampling ratio | 4x: up to 0.69 dB; 8x: 0.17 dB; 16x: 0.04 dB; 32x: 0.01 dB (worst case, recomputed by a verifier) [V3] |
| Delivery ceiling | AES TD1008: ≤ −1 dBTP at the codec input for lossy streams; high-bitrate codecs may tolerate −0.5 dBTP; insufficient headroom can cause up to 3 dB of decode-side limiting [V3] |
| Loudness targets | AES TD1008: −16 LUFS for track-normalised music; −14 LUFS for the loudest album track [V3]. These are distributor normalisation targets, not mastering targets |
| FabFilter Pro-L 2 | Two-pass true-peak design; vendor states ~0.1 dB inter-sample overshoot at 4x oversampling with ≥ 0.1 ms lookahead "in most cases" [V3, vendor figure] |
| Live 12 Limiter | Lookahead 1.5/3/6 ms; ceiling modes Standard, Soft Clip, True Peak; true-peak protection is opt-in; no published oversampling or overshoot figure [V3] |
| Other stock limiters (Logic, FL, Studio One, Cubase, Pro Tools, REAPER, Bitwig), Ozone, Oxford, Limitless | **Nothing verified.** Platform targets for Spotify, Apple Music and YouTube also unverified |

### 4.2 Spec [I]

| Parameter | Target | Rationale |
|---|---|---|
| Default ceiling mode | True peak, −1.0 dBTP | TD1008; Live makes this opt-in, so default-on is a concrete improvement |
| Detection oversampling | ≥ 8x | 4x can under-read 0.69 dB |
| True-peak overshoot | ≤ 0.1 dBTP measured with a 16x meter | Matches Pro-L 2's stated figure, measured more strictly |
| Lookahead | Continuous 0.1–10 ms plus presets | Live offers three fixed values |
| Modes | Transparent, punchy, soft-clip, clip-then-limit | Parity with Live's three, plus a clipper stage |
| Built-in metering | Integrated, short-term, momentary LUFS; true peak; loudness range | Returned as data to the agent on every render |

### 4.2a Measured 2026-10-08: Live 12 Limiter vs FabFilter Pro-L 2

Probe: `daw_bench/profile.py::probe_limiter`, 16x true-peak meter, self-calibrated ceiling (a 0 dBFS steady sine reads back as the ceiling). Signals: fs/4 inter-sample stress tone (true peak 3.01 dB above its samples) and a −6 dB RMS noise burst. Live 12 at 44.1 kHz, device defaults except the mode switch.

| Device | Ceiling read back | Stress-tone overshoot (dBTP above ceiling) | Noise-burst overshoot |
|---|---|---|---|
| Live Limiter, mode 0 (Standard) | −0.30 dBFS | **+2.93 dB** | +1.82 dB |
| Live Limiter, mode 1 (Soft Clip) | −1.32 dBFS | +2.85 dB | +3.15 dB |
| Live Limiter, mode 2 (True Peak) | −0.30 dBFS | +0.02 dB | **+0.66 dB** |
| Live Limiter, mode 2, lookahead setting 2 | −0.30 dBFS | +0.02 dB | +0.66 dB (no change; the lookahead parameter write may not have applied) |
| FabFilter Pro-L 2, defaults | −0.02 dBFS | +0.01 dB | **+0.13 dB** |

Reading [I]: Live's default mode is a sample-peak limiter and lets the full 3 dB inter-sample overshoot through, as the manual implies. Its True Peak mode holds the synthetic stress tone but still overshoots a noise burst by 0.66 dB; Pro-L 2 holds both to within its stated ~0.1 dB. The spec target (≤ 0.1 dBTP overshoot, true-peak mode on by default) therefore sits at Pro-L 2's level and is an improvement over Live's stock device on both counts (default mode and worst-case overshoot). The Soft Clip mode's lower read-back ceiling is the clipper shaving the steady sine, not a different ceiling setting.

### 4.3 Limiter acceptance tests

1. Inter-sample stress signals (fs/4 phase-shifted sine, clipped square, dense EDM master): overshoot ≤ 0.1 dBTP at 16x metering.
2. THD and IMD at 3, 6 and 9 dB gain reduction on a 50 Hz + 7 kHz pair; must be at or below the same measurement on Pro-L 2 and Live 12 Limiter run through the same harness.
3. Blind ABX against Pro-L 2 at matched loudness, 6 dB gain reduction (protocol in section 12.3).

---

## 5. Engine foundation

### 5.1 What is known

| Topic | Finding |
|---|---|
| Tracktion Engine scope | High-level DAW data model as a JUCE module, C++20, GPLv3-or-commercial, separate JUCE licence needed [V3] |
| Tracktion graph | Static node graph, lock-free multithreaded player, latency nodes at sum points [V1] |
| Tracktion published benchmarks | A benchmarks page exists but returned no numbers; "primarily for internal use" [V1] |
| Tracktion pricing 2026 | Not published on the page fetched [V1]. 2018 tiers (free under ~$50k revenue, then ~$35–50/month) are unconfirmed |
| Tracktion automation resolution, 64-bit summing, headless use, crash isolation | Not found [BENCH] |
| JUCE licence | JUCE modules including `juce_dsp` are AGPLv3 or commercial [V3]. JUCE 8 tiers: free under $20k revenue, Indie $40/month to $300k, Pro $175/month [V1] |
| Rust | Dropseed is AGPL and archived; `plugin_host` crate's VST3/CLAP bridges are stubs [V3]. `clack` is a real CLAP host library [V1]. No proven Rust path for Audio Unit hosting [I] |
| VST3 SDK | MIT since 3.8.0, October 2025 [V1] |
| CLAP | MIT [V1] |
| REAPER as engine | Mature and scriptable with CLI render, but closed, not embeddable, and not Live-like [V1] |

### 5.2 Architecture worth adopting from each DAW

| Source | Technique | Evidence |
|---|---|---|
| Ableton | Work-stealing task scheduling across the audio graph | [V1] ADC 2025 talk (Susser); no numbers extracted |
| Bitwig | Five plugin sandbox modes, from in-process to one process per plugin | [V1] Bitwig user guide |
| REAPER | Anticipative processing: render non-live tracks ahead on large buffers | [V1] Cockos forum |
| Cubase | ASIO-Guard: large pre-processing buffer for non-monitored tracks, small buffer for live ones | [V1] Steinberg help centre |
| Ardour 6 | Sample-accurate latency compensation on every signal path | [V1] ardour.org |
| Apple | Realtime threads must join the device's audio workgroup on Apple silicon | [V1] Apple developer docs |

### 5.3 Decision matrix

| Criterion | Weight | Tracktion Engine | Custom C++ core | Rust core + C++ plugin host | REAPER-backed |
|---|---|---|---|---|---|
| Delay compensation on all paths | 3 | Present, recent fixes [V1] | Build | Build | Mature [I] |
| Multicore scheduling | 3 | Present, unmeasured [BENCH] | Build | Build | Mature [V1] |
| Sample-accurate automation | 3 | Unknown [BENCH] | By design | By design | Unverified |
| 64-bit summing | 2 | Unknown [BENCH] | By design | By design | Unverified |
| Deterministic offline render | 3 | Unknown [BENCH] | By design | By design | [BENCH] |
| Headless | 3 | No evidence [BENCH] | By design | By design | CLI only |
| Plugin crash isolation | 2 | None built in [I] | Build | Build | Available |
| Clip launcher and warp ready | 2 | Yes (v3) [V1] | Build | Build | No |
| Control over pan law, SRC, fades (section 3) | 3 | Requires engine modification | Full | Full | None |
| Licence cost for closed source | 1 | Tracktion + JUCE | JUCE only, or none | None | Per-user REAPER |
| Time to first sound | 2 | Weeks | Months | Months+ | Days |

### 5.4 Recommendation [I]

Do not commit before Phase 0. The quality spec in section 3 needs control over summing, pan law, SRC, fades and automation timing. Tracktion Engine supplies the most features soonest, but those exact properties are its unknowns. So:

1. **Fixed regardless of engine:** the project document model, the agent API, the out-of-process plugin host (C++ on the MIT VST3 SDK, CLAP, and AudioToolbox), the test harness, and a small **Python reference engine** (`daw_bench/ref_engine.py`) that is the audio-quality spec made executable: selectable pan law, flat SRC, 64-bit summing, defeatable edge fades. The real engine must null against it.
2. **Phase 0 loop:** run the same probes against Live and against Tracktion Engine, and the twelve benchmarks in section 12.1 against Tracktion Engine. GPLv3 removes the licence cost, so the question is only whether its measured gaps (delay compensation null, automation timing, determinism, headless) can be closed in a fork we maintain. If they can, build on it; if not, build a custom C++ graph on JUCE and keep Tracktion as a measured reference.
3. **REAPER** serves as an external render oracle during development, not as a foundation.
4. **Rust** is deferred: the plugin-hosting gap is the dominant risk.

---

## 6. Competitive stock audio effects and instruments

### 6.1 Licensing reality

| Source | Licence | Usable in a closed product? | Evidence |
|---|---|---|---|
| chowdsp_utils effect modules (compressor, EQ, filters, reverb, waveshapers) | GPLv3 | No, unless separately licensed from the author | [V3] |
| chowdsp_wdf (wave digital filters) | BSD-3-Clause | Yes | [V3] |
| RTNeural (realtime neural inference) | BSD-3-Clause | Yes | [V3] |
| Signalsmith DSP (delays, interpolators, envelopes, FFT/STFT) | MIT | Yes | [V3] |
| Surge XT | GPLv3 | No (sst-* sub-libraries unverified) | [V3] |
| Schlecht's FDN Toolbox | GPL-3.0 | No; implement from the paper | [V3] |
| JUCE `juce_dsp` | AGPLv3 or commercial | Only with a JUCE licence | [V3] |
| Faust compiler | Generated code generally carries the licence of the DSP source [V1]; per-library licences must be checked | Case by case | [V1] |
| Cmajor | Licence page fetched; terms not verified | Unverified | — |
| Airwindows, DaisySP, HIIR, STK, Cycfi Q, KFR, Vital, Dragonfly, Calf, LSP, x42, ZL plugins | **Unverified this session** | Check each before use | — |

Consequence: the project is GPLv3 (section 14), so chowdsp, Surge's DSP, the FDN toolbox and Rubber Band are directly usable; the "closed-source OK" column above is kept only so a later relicensing decision can see what it would cost. The loop in section 12.2 measures each adopted component against the reference device and decides whether to tune, swap or rewrite it [I].

### 6.2 Algorithm plan per device class

| Device | Algorithm | Evidence | Measurable target |
|---|---|---|---|
| **EQ** | Vicanek matched biquads: poles by impulse invariance, numerator fitted to the analog response; closed-form, cheaper than Orfanidis/Massberg, no oversampling | [V3] Vicanek 2016 (self-published, widely adopted) | Magnitude error vs. analog prototype ≤ 0.1 dB to 20 kHz at 44.1 kHz for a +12 dB bell at 16 kHz |
| EQ modulation | TPT/state-variable structures for click-free fast modulation | [B] Zavalishin, *The Art of VA Filter Design*; Simper (Cytomic) SVF notes | No audible zipper on a 20 Hz–20 kHz sweep in 10 ms |
| EQ phase modes | Minimum phase default; linear phase via FFT/FIR; dynamic bands | [B] | Linear-phase mode: phase deviation ≤ 1° in passband; latency reported to the host |
| **Compressor** | Feedforward, log-domain detector with smooth decoupled peak detection; lookahead; program-dependent release; sidechain filter | [B] Giannoulis, Massberg & Reiss, JAES 2012. Fetch failed this session | Static curve error ≤ 0.1 dB; attack/release within 5% of setting; THD at 10 dB reduction ≤ reference device |
| **Limiter** | Section 4 | [V3] for targets | Section 4.3 |
| **Saturation, waveshaping** | Antiderivative anti-aliasing (ADAA) plus 2x oversampling. Holters' stateful ADAA at 2x gives low-frequency aliasing comparable to 5x unmitigated on a diode clipper and a Tube Screamer-style circuit | [V3] Holters, DAFx-19 (qualitative spectra, one tone, two circuits) | 1244.5 Hz sine, +24 dB drive: aliasing components ≤ −90 dBFS below 20 kHz |
| ADAA caveat | In feedback loops the scheme adds a half-sample delay; response above fs/3 degrades, so ~2x oversampling is still needed | [V3] | Included in the test above |
| Memoryless ADAA | First- and second-order ADAA for static waveshapers | [B] Parker, Zavalishin & Le Bivic, DAFx-16 | Same aliasing test |
| **Reverb, algorithmic** | Feedback delay network with graphic-EQ-class attenuation filters for accurate per-band decay; one-pole shelves are cheaper but miss the specified T60 | [V3] Schlecht, DAFx-20 | Per-band T60 error ≤ 5%; echo density and modal density reported; no metallic ringing in MUSHRA |
| Reverb, plate | Dattorro plate: 4 input diffusers into a figure-eight tank; published values are for 29,761 Hz and must be rescaled; modulate tank all-passes ~1 Hz with user-controllable depth; all-pass interpolation preferred | [V3] Dattorro, JAES 1997 | Decay matches setting ≤ 5%; no pitch wobble on piano at default depth |
| Reverb, convolution | Partitioned convolution with non-uniform partitions for zero latency | [B] Gardner 1995; Wefers 2014 | Null vs. direct convolution ≤ −120 dBFS; latency 0 samples |
| **Analog delay, chorus, flanger** | Holters–Parker bucket-brigade model running at the BBD clock rate with input/output filters folded in | [V3] Holters & Parker, DAFx-18 (abstract only) | Aliasing and clock-noise behaviour matches a measured hardware reference qualitatively; no zipper under delay-time modulation |
| Delay-line interpolation | Lagrange, polyphase and Kaiser-sinc interpolators | [V3] available in Signalsmith DSP (MIT) | THD of a modulated 1 kHz tone ≤ −80 dB |
| **Virtual-analog filters** | Zero-delay-feedback ladder, Sallen-Key, diode and state-variable with nonlinear solve | [B] Zavalishin; Huovilainen; D'Angelo & Välimäki | Self-oscillation tuning error ≤ 3 cents 20 Hz–10 kHz; stable under audio-rate cutoff modulation |
| **Circuit models** | Wave digital filters for white-box models | [V3] chowdsp_wdf, BSD-3 | Frequency response within 0.5 dB of SPICE reference |
| **Neural effects** | RTNeural for inference. NAM A2 vendor figures: ~64 full or ~200 lite instances on an M-series MacBook (conditions unstated) | [V3] licence; [V3, vendor figure] performance | ≤ 2% of one core per instance at 48 kHz for the lite model on M4 Max [BENCH] |
| **Oscillators, wavetable synth** | Mip-mapped wavetables with high-order interpolation; BLEP/minBLEP for classic shapes | [B] Välimäki & Huovilainen; nothing verified | Sweep 20 Hz–20 kHz saw: aliasing ≤ −90 dBFS below 18 kHz |
| **Sampler** | Windowed-sinc interpolation, selectable length | [B] | Transposition ±24 semitones: aliasing ≤ −100 dBFS with the high-quality kernel |
| **FM, granular, physical modelling** | Not researched in depth | — | Defined in Phase 3 |

### 6.3 What the incumbents' devices actually do

Nothing verified. No claim survived about EQ Eight's oversampling mode, Pro-Q's natural phase, Logic's Channel EQ, Live's Wavetable/Operator, or Vital/Serum interpolation. The plan therefore measures the references directly with the parity harness (section 12.2) instead of relying on descriptions.

### 6.4 Proving parity

| Method | Use | Evidence |
|---|---|---|
| Signal measurements (null depth, THD+N, aliasing sweep, impulse and step response, latency, CPU) | Primary gate | [I] |
| Perceptual metrics (PEAQ, ViSQOL, 2f-model) | Supporting only. Such measures are often used outside their validated domain; in one study the 2f-model outperformed PEAQ, POLQA, PEMO-Q and ViSQOLAudio on coding and separation tasks | [V3] Torcoli et al., IEEE/ACM TASLP 2021 (authors developed the 2f-model) |
| Listening tests (MUSHRA per ITU-R BS.1534, ABX) | Final confirmation | [B] standard not fetched |
| pluginval, Plugin Doctor | Host-compliance and curve inspection | [B] |

### 6.5 Agent-authored devices

A working proof of concept exists: natural language → Faust → validated → JIT-compiled through libfaust/LLVM → hot-swapped into a live VST3 without stopping playback [V1, `Losera/incant-audio`]. Plan [I]:

- Embed a DSP language with a JIT (Faust first; Cmajor if its licence permits) as a first-class device type.
- The agent writes source text; the engine compiles, runs the device test suite (stability, DC, denormals, CPU budget, aliasing), and only then inserts it.
- Device source lives in the project document, so it diffs and versions like everything else.

---

## 7. MIDI engine and MIDI effects

### 7.1 The bar to match

| Reference | What it does | Evidence |
|---|---|---|
| Live 12 MIDI Tools | Clip-level Transformations (Arpeggiate, Chop, Connect, Glissando, LFO, Ornament, Quantize, Recombine, Span, Strum, Time Warp, Velocity Shaper) and Generators (Rhythm, Seed, Shape, Stacks, Euclidean). Native tools closed; user tools via Max for Live patching | [V3] Live 12 manual |
| Bitwig Operators | Per-event properties: Chance, Repeats (2–128 or rate 1/2–1/128, with curve and velocity target), Occurrence (11 conditions incl. fill and first/previous), Recurrence. Apply to audio events too | [V3] Bitwig user guide |
| Logic Scripter | User-authored JavaScript MIDI effect; processes once per audio block, so not sample-accurate by design | [V1] Apple docs |
| REAPER JSFX | Text files, hot-reload, sample-offset MIDI send and receive | [I] |
| Cubase Logical Editor | Declarative filter-then-act rule engine with presets | [I] |
| Realtime MIDI devices in Live, Bitwig, Logic, FL, Studio One, Reason | Arpeggiators, chord, scale, random, velocity, note length, echo, strum, humanise | [I] not verified |

### 7.2 Protocol facts

| Topic | Finding |
|---|---|
| VST3 | Carries no raw MIDI. Host translates notes to Events, controllers to parameters via `IMidiMapping`, per-note data to NoteExpression; the plugin declares CC assignments | [V3] Steinberg developer portal |
| VST 3.8 | Adds `IMidiMapping2`/`IMidiLearn2` for MIDI 2.0; a UMP-carrying extension is not yet in the SDK | [V1] Steinberg forum |
| CLAP | Note events carry port, channel, key and `note_id`; note expressions for volume, pan, tuning, vibrato, expression, brightness, pressure; dialects MIDI, MPE, MIDI2 | [V1] CLAP headers |
| Windows MIDI Services | Generally available February 2026 with UMP as the internal format | [V1] Microsoft |
| DAW-level MIDI 2.0 support | Only one low-reliability blog; treat as unknown | — |
| MTS-ESP | One master plugin defines tuning for unlimited clients; licence not fetched | [V1] |
| Live 12 tuning systems, PPQ per DAW, groove pool details, MPE support per DAW | Background knowledge only | [I] |

### 7.3 Design [I]

| Element | Decision | Rationale |
|---|---|---|
| Time base | Rational beat positions plus sample offsets resolved at render; no fixed PPQ exposed | Avoids tick quantisation; sample-accurate delivery |
| Note identity | Stable note IDs; per-note expression lanes (pitch, pressure, timbre, volume, pan) at 32-bit | Maps cleanly to CLAP, VST3 NoteExpression, MPE and MIDI 2.0 |
| Pitch | Continuous pitch resolved through a tuning table at note-on; import Scala `.scl/.kbm`; MTS-ESP client and master | Microtonality without per-device hacks |
| Per-event operators | Chance, repeats, occurrence and recurrence stored on the note | Parity with Bitwig, declarative, diffable |
| Clip-level tools | Transform and generate functions over note lists, covering every Live 12 tool | Parity with Live |
| Groove | Per-subdivision timing and velocity offset vectors, swing ratio, humanise term; extraction from audio or MIDI. Reuse `sandbox/groove.py` | Feel as a first-class object |
| Scriptable note effects, tier 1 | Declarative ruleset (filter → action), validated before run | Safe target for agents; Logical Editor model |
| Scriptable note effects, tier 2 | `process(events_in, block_ctx) → events_out` with sample offsets, compiled to WASM with an instruction budget, deterministic seeded RNG, hot-reload at block boundaries | Sample-accurate, sandboxed, unlike Scripter's per-block model |
| Agent note format | Compact JSON note lists over the lossless model. ABC notation uses ~38% of the tokens of MIDI-like sequences but loses micro-timing and per-note dynamics [V1, ChatMusician and MIDI-LLM papers] | Offer an ABC-like summary view for reasoning, JSON for edits |

### 7.4 MIDI acceptance tests

1. Note onset delivered to an internal test device within ±0 samples of its document position at 44.1, 48 and 96 kHz.
2. Each of Live 12's 17 MIDI tools and Bitwig's 4 operators has an equivalent with a documented behavioural test.
3. MPE round trip: record, edit, play to a CLAP and a VST3 instrument with per-note pitch error ≤ 1 cent.
4. A tier-2 script that exceeds its instruction budget is stopped without an audio dropout.
5. Seeded generative tools produce identical output across 10 runs.

---

## 8. Best of all DAWs

The strengths below are common knowledge [I]; no reviews or manuals were fetched for this matrix. Copying functionality is legally fine; the names are trademarks and are not reused.

| Rank | Capability to adopt | From | Why (agent value × human value ÷ cost) |
|---|---|---|---|
| 1 | Text-serialisable project and open action list | REAPER | Agents read and write everything declaratively |
| 2 | Clip launcher plus arrangement on one timeline model | Live | Core human workflow; the reason for the project |
| 3 | Racks with macros | Live | One control surface for many parameters |
| 4 | Unified modulation of any parameter | Bitwig | Movement as data an agent can author |
| 5 | Plugin sandboxing with selectable granularity | Bitwig | Long agent runs survive plugin crashes |
| 6 | Declarative note-rule engine | Cubase | Safe agent-authored MIDI transforms |
| 7 | Routing matrix and per-clip effects | REAPER | Simple to describe programmatically |
| 8 | Anticipative large-buffer processing for non-live tracks | REAPER, Cubase | Headroom for agent-heavy sessions |
| 9 | Chord track and arranger sections | Cubase, Studio One | Harmonic and structural spine for agents |
| 10 | Scratch pads | Studio One | Branch-and-compare for agent experiments |
| 11 | Clip gain and comping playlists | Pro Tools | High human value |
| 12 | Expression maps | Cubase | Separates notes from articulation |
| 13 | Groove extraction | Live | Feel as a parameter |
| 14 | Clip aliases and hybrid audio/MIDI tracks | Bitwig | Reuse without duplication |
| 15 | Per-note effect commands | Renoise | Compact text-friendly note control |

Deferred: generative session players (Logic) are costly to do well and overlap with the agent itself.

---

## 9. Agent-native architecture

| # | Requirement | Evidence |
|---|---|---|
| 1 | One canonical, text-serialisable project document; the GUI is a view | Zoo code-CAD, Remotion `Clip[]` [V1] |
| 2 | Git-diffable: line-oriented, stable IDs, plugin state as referenced blobs | Ardour XML and REAPER `.rpp` diff complaints [V1] |
| 3 | Code-mode API: `search_api` + `execute` in a sandbox, typed bindings, a few high-level tools | Cloudflare (2 tools ≈ 1,000 tokens vs. >1M for one tool per endpoint), Anthropic code-execution write-up [V1]; DAWZY uses 3 MCP tools over REAPER [V1] |
| 4 | Transactions: atomic, dry-run, diff preview, one undo stack shared with the human, attribution per change | DAWZY [V1] |
| 5 | Query-first reads with filtering and pagination | Blender MCP reports [V1] |
| 6 | Headless, deterministic, faster-than-realtime render as a first-class call | Repo's own need |
| 7 | Analysis as return values: LUFS, true peak, spectrum, stem deltas. Deterministic measures lead; audio LLMs are secondary | Multimodal models are near ceiling on MIDI but unreliable on audio [V1, arXiv 2510.22455] |
| 8 | Symbolic-first: notes, automation, parameters as data | Same |
| 9 | Out-of-process plugin hosting | Bitwig [V1] |
| 10 | Agent-authored devices and MIDI tools (sections 6.5, 7.3) | incant-audio [V1] |
| 11 | Project format: own native text model; DAWproject (MIT spec; Bitwig, Studio One, Cubase 14) as export; `.als` as import | [V1] |

Determinism contract [I, from V1 sources]: identical output on the same machine, same plugin versions and same seeds. Requires a fixed summing topology, explicit flush-to-zero in both realtime and offline paths, pinned floating-point flags (no implicit FMA contraction), and seeded RNG in every internal device. Third-party plugins are flagged deterministic or not by a ten-render test.

Headless constraints on macOS [V1, weak sources]: Audio Units need a pumped main-thread run loop; many plugins need a logged-in GUI session; licence dialogs cannot be suppressed generically. The plugin host process therefore runs with a hidden window and a main-thread loop.

### Reuse from this repo

| Asset | Role |
|---|---|
| `daw_translation/als_parser.py` | `.als` import bridge |
| `daw_translation/render_host.py`, `render_pool.py`, `render_worker.py` | Warm plugin host; becomes an external render oracle |
| `harness/stem_analysis.py`, `harness/enrich_sidecars.py`, `sandbox/audio_metrics.py`, `sandbox/midi_metrics.py` | Analysis-as-return-value library |
| `sandbox/fidelity.py`, `eval_fidelity.py`, `compare_frozen.py` | Seed of the parity harness |
| `sandbox/groove.py` | Groove model |
| `harness/perception_recorder.py` | Observation trajectories for training |
| `harness/unified_mcp_bridge.py` | The 77-tool surface to collapse; also the migration test list |

---

## 10. Dependency licence register

| Component | Licence | Closed-source OK | Evidence |
|---|---|---|---|
| VST3 SDK 3.8 | MIT | Yes | [V1] |
| CLAP | MIT | Yes | [V1] |
| Audio Unit hosting (AudioToolbox) | Apple SDK | Yes | [B] |
| JUCE | AGPLv3 or commercial | With licence | [V3] |
| Tracktion Engine | GPLv3 or commercial | With licence | [V3] |
| Signalsmith DSP | MIT | Yes | [V3] |
| Signalsmith Stretch | MIT | Yes | [V1] |
| Bungee | MPL-2.0 (Ableton maintains a fork) | Yes, file-level copyleft | [V1] |
| Rubber Band | GPL or commercial | With licence | [V1] |
| zplane élastique | Commercial | With licence | [V1] |
| chowdsp_wdf | BSD-3 | Yes | [V3] |
| RTNeural | BSD-3 (Eigen MPL-2.0, xsimd BSD-3) | Yes | [V3] |
| chowdsp_utils DSP modules, Surge XT, FDN Toolbox | GPLv3 | No | [V3] |
| beat_this (beat tracking) | MIT code and weights | Yes; check training-data terms | [V1] |
| madmom models, Essentia models | Non-commercial | No | [V1] |
| Ableton Link | GPLv2+ or proprietary licence from Ableton | With licence | [V1] |
| DAWproject | MIT spec | Yes | [V1] |
| Faust, Cmajor, libebur128, r8brain-free, HIIR, MTS-ESP | **Verify before use** | — | Not verified |
| Pedalboard, DawDreamer | GPLv3 | Only as a separate test-time process, never linked | [V1] |

---

## 11. Production roadmap

Effort figures are estimates for one developer on an M4 Max with AI coding agents [I]. Every phase ends at a gate; a failed gate blocks the next phase.

### Phase 0: Measure before building (4 weeks)

| Deliverable | Gate |
|---|---|
| Test and benchmark harness (section 12) with BS.1770-5 meter at 16x | Meter matches EBU reference signals within ±0.1 LU and ±0.1 dBTP |
| Black-box profile of Live: pan curve, SRC sweep, 1:1 warp null, fade shape, delay-compensation alignment, limiter overshoot | Profile stored with signals and scripts in the repo |
| Python reference engine passes the section 3 probes (executable spec) | Pan law fit exact, SRC alias ≤ −120 dB, fade 4 ms ± 0.3, unity residual ≤ −140 dBFS |
| Tracktion Engine through the same probes plus the twelve benchmarks in 12.1 | **Probes done 2026-10-08 (sections 3.1a, 3.1b, 4.2a)**; benchmarks pending. Go/no-go with numbers: gap to the reference engine per probe |
| Acquire references per section 3.3: REAPER, Pro-L 2 and Pro-Q trials | Installed and rendering through the harness |
| Counsel review of section 2; product name search | No blocking issue |
| Go-to-market decision (section 14) | **Decided 2026-10-05: open source, GPLv3** |

### Phase 1: Engine core and plugin host (3–4 months)

| Deliverable | Gate |
|---|---|
| Audio graph, 64-bit bus, selectable pan law, SRC, fades | Section 3 tests 1, 2, 3, 6 pass |
| Delay compensation on all paths | Test 7 passes (sample-exact null) |
| Sample-accurate automation | Test 8 passes (< 1 sample) |
| Out-of-process VST3/AU/CLAP host | ≥ 95% of a 50-plugin compatibility list load, process and restore state; killing a plugin process does not stop the engine |
| Sandbox overhead | ≤ 0.3 ms added round trip and ≤ 10% CPU vs. in-process [BENCH threshold] |
| Offline render | ≥ 20x realtime on a 64-track, 5-minute project; 10 renders byte-identical with deterministic plugins |
| Realtime | ≥ 300 tracks of a fixed 6-plugin chain at 128 samples with zero dropouts [BENCH threshold; one unverified blog reports Logic at ~405] |
| Headless | Full render with AU and VST3 instruments, unattended |
| Serum fidelity | Gap vs. in-Live render ≤ 1 dB in 20–250 Hz (repo baseline: 5–15 dB) |

### Phase 2: Document model and agent API (2–3 months, overlaps Phase 1)

| Deliverable | Gate |
|---|---|
| Native text project format with stable IDs | Round trip load→save is byte-identical; a one-note edit yields a ≤ 3-line diff |
| Code-mode API with transactions, dry-run, undo | The 77 existing tool behaviours are reproducible through ≤ 5 tools; API description ≤ 2,000 tokens |
| Analysis return values on every render | LUFS, true peak, spectrum and stem deltas returned in one call |
| `.als` import, DAWproject export | 20 of Brent's own sets import with tracks, clips, tempo and stock-mappable devices intact |

### Phase 3: Musical model (3 months)

| Deliverable | Gate |
|---|---|
| Clip launcher, scenes, follow actions, arrangement | 64 clips launched on a bar boundary start within 1 sample |
| Warp markers, stretch backends, auto-warp via beat tracking | 1:1 null passes; stretch metric table published; auto-warp downbeat error ≤ 20 ms on a 50-track test set [I threshold] |
| Racks, macros, unified modulation | Modulation is sample-accurate on internal devices |

### Phase 4: Stock devices v1 (4–6 months)

| Deliverable | Gate |
|---|---|
| EQ, compressor, limiter, saturator, delay, chorus/flanger/phaser, algorithmic and convolution reverb, filter, utility | Each passes its section 6.2 target and is at or better than Live's equivalent on the measured axes |
| Wavetable synth, sampler, drum sampler | Aliasing targets in 6.2 |
| Listening tests | No device rated significantly below its reference in MUSHRA (≥ 12 listeners) |
| Agent-authored device pipeline | An agent-written Faust effect compiles, passes the safety suite and loads without a dropout |

### Phase 5: MIDI engine and tools (2 months, overlaps Phase 4)

Gate: the five tests in section 7.4.

### Phase 6: Human GUI (4–6 months)

| Deliverable | Gate |
|---|---|
| GUI as a view of the document, sharing undo and selection with the agent | Every GUI action produces the same document diff as its API call |
| Performance | 60 fps with 100 tracks; GUI process crash does not stop audio |

### Phase 7: Beta (2 months)

Gate: 10 external producers complete a track; crash-free session rate ≥ 99%; plugin compatibility list ≥ 200 plugins at ≥ 95%.

---

## 12. Test and benchmark harness

### 12.1 Engine benchmarks (Phase 0 bake-off and Phase 1 gates)

| # | Benchmark | Workload | Pass threshold |
|---|---|---|---|
| 1 | Track ramp | N tracks × fixed 6-plugin chain, 64 and 128 samples | ≥ 300 tracks, zero dropouts |
| 2 | Graph topology | 100-plugin serial chain; 200 parallel tracks; fan-in to a bus | Near-linear scaling to performance-core count |
| 3 | Delay compensation | Nested rack, 2048-sample plugin on a send, master plugins | Sample-exact null |
| 4 | Automation timing | Gain ramp vs. analytic reference | Error < 1 sample |
| 5 | Offline speed | 64 tracks, 5 minutes | ≥ 20x realtime |
| 6 | Determinism | 10 renders, varied thread counts | Byte-identical |
| 7 | Summing precision | 100 tracks at −0.1 dBFS | Residual ≤ −140 dBFS |
| 8 | Sandbox overhead | Same chain in-process vs. per-plugin process | ≤ 0.3 ms, ≤ 10% CPU |
| 9 | Crash isolation | Kill a plugin process mid-render | Engine continues |
| 10 | Time-stretch load | 32 warped tracks at 128 samples | No dropouts |
| 11 | Headless | No GUI interaction, AU + VST3 instruments | Completes unattended |
| 12 | Clip launch | 64 clips quantised to the bar | All within 1 sample |

Thresholds are proposals [I]; Phase 0 replaces them with measured baselines from Live (and REAPER if installed) on the same machine.

### 12.1a Measured on Tracktion Engine, 2026-10-08 (`daw_bench/engine_bench.py`, M4 Max, 48 kHz, plain clips, no plugins)

| # | Benchmark | Result | Gate |
|---|---|---|---|
| 5 | Offline speed | 64 tracks × 30 s in 1.40 s wall = **21x realtime** including ~0.8 s fixed engine start-up per job; 16 tracks × 60 s = 48x; the render itself runs at roughly 3,000 track-seconds per second | ≥ 20x: **pass** (with no plugins) |
| 6 | Determinism | 16 tracks × 10 s rendered 5 times: **byte-identical** (one SHA-256) | pass |
| 7 | Summing precision | 100 identical tracks at −0.1 dBFS: residual **−126 dB relative to the sum**, exactly where 100 single-precision additions land; a 64-bit bus would sit near −150 dB | ≤ −140: **fail**; Tracktion mixes in 32-bit float |
| 3 | Delay compensation | Latency Tester 20 ms: null −121 dBFS; 250 ms: null **−86 dBFS** | sample-exact: pass at 20 ms, degraded at 250 ms (cause not yet found) |
| 1, 2, 4, 8–12 | track ramp, topology, automation, sandbox, crash, stretch load, headless, clip launch | not yet run (headless rendering itself is proven by every probe above) | — |

Reading [I]: Tracktion is deterministic and fast enough offline. Its mix bus is 32-bit float, which is inaudible at −126 dB but below the spec, so the spec's 64-bit summing is a fork item alongside the sinc-at-1:1 bypass (section 3.1a). The 250 ms compensation residual needs a cause before Phase 1.

### 12.2 Device parity harness

This is the feedback loop the project runs on: reference and candidate go through identical signals, and the difference per metric is the work list. One runner drives any plugin or internal device through: swept-sine linear and harmonic analysis, THD+N vs. level and frequency, two-tone IMD, aliasing sweep, impulse and step response, latency, null against a reference, CPU per instance. References (Live stock devices via black-box render, FabFilter and others as plugins) run through the identical signals. Built on `sandbox/fidelity.py` and `sandbox/audio_metrics.py`.

### 12.3 Listening tests

MUSHRA for multi-condition quality comparisons and ABX for transparency claims, with hidden reference and anchor, loudness-matched to 0.1 LU. Listener counts and statistics follow ITU-R BS.1534 [B, not fetched].

### 12.4 Continuous integration

Every commit: document round-trip, determinism, summing, pan, delay-compensation and automation tests. Nightly: full device parity suite and plugin compatibility list.

---

## 13. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Third-party plugin hosting edge cases (state restore, threading, licence dialogs) consume the schedule | High | High | Out-of-process host first; compatibility list in CI from Phase 1 |
| Tracktion Engine fails a hard gate | Medium | High | Phase 0 bake-off before any commitment; document model and API are engine-independent |
| Stock devices measure well but sound worse | Medium | High | MUSHRA gates; agent-authored devices and third-party plugins cover gaps |
| GPL contamination of a closed product | Medium | High | Section 2.3 protocol; licence register in CI |
| A DSP patent covers a chosen algorithm | Low–Medium | High | Freedom-to-operate search before launch; stretch backends are swappable |
| Ableton ships a real agent API | Medium | Medium | Differentiate on headless render, determinism, agent-authored devices, open document |
| Headless macOS plugin behaviour blocks unattended rendering | Medium | Medium | Hidden-window host with main-thread loop; flag non-compliant plugins |
| Scope: GUI competitive with 20-year-old products | High | Medium | Agent-first release with a minimal GUI; GUI phase last |
| Solo-developer bus factor | High | High | Text formats, tests as spec, open-source option |

---

## 14. Go-to-market and licensing

**Decided 2026-10-05: open source under GPLv3.**

| Consequence | Detail |
|---|---|
| Usable at no cost | Tracktion Engine, JUCE, chowdsp_utils, Surge XT DSP, Rubber Band, FDN Toolbox, Ableton Link (GPLv2+), Pedalboard and DawDreamer as in-process tools |
| Still to license or negotiate | zplane élastique (optional stretch upgrade); none required |
| Revenue options | Hosted or cloud rendering, support, content, a later dual licence if the project owns its copyright (requires a contributor licence agreement from day one) |
| Keep open regardless | The project document format and the agent API specification: they are what makes the product agent-native for third parties |
| Trademark | Still needs a product-name search; GPL does not change section 2 |

Alternatives considered and set aside: closed commercial (needs JUCE and Tracktion licences and in-house devices from papers; longer Phase 4) and open core (needs a CLA and GPL-free closed parts).

---

## 15. What remains unverified

| Area | Gap | How the plan covers it |
|---|---|---|
| Cross-DAW null tests | Neither confirmed nor refuted | Our own null tests in Phase 0 |
| Per-DAW SRC, automation resolution, bounce determinism, fade curves, dither, denormals | No verified data | Black-box profile of Live; spec set by our own targets |
| Stretch algorithms in Logic, Pro Tools, Cubase, Studio One, FL, Bitwig; any listening comparison | No verified data | Own metric table |
| All stock limiters except Live's; Ozone, Oxford, Limitless; measured overshoot or distortion for any limiter | No verified data | Section 4.3 measures references directly |
| Spotify, Apple Music, YouTube loudness targets; EBU R128 | Not verified | AES TD1008 used instead |
| Compressors, VA filters, oscillators, samplers, convolution | Literature cited from background only | Acceptance tests carry the weight |
| What EQ Eight, Pro-Q, Channel EQ, Wavetable, Vital, Serum implement | Nothing verified | Parity harness measures them |
| DSP patents in force | Not researched to a usable standard | Counsel |
| Engine performance numbers for any candidate | Not public | Phase 0 |
| Tracktion and élastique commercial pricing in 2026 | Not published | Request quotes in Phase 0 |
| Best-of-DAWs matrix, PPQ values, per-DAW MIDI 2.0 and MPE support | Background knowledge | Low risk; verify when each feature is specified |
| Repo docs say the LOM cannot write arrangement clips; current LOM docs list `Track.create_audio_clip` | Conflict | Re-test on Live 12.4.x |

---

## 16. Sources

### Standards and primary papers
- ITU-R BS.1770-5: https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-5-202311-I!!PDF-E.pdf
- AES TD1008 v3.13: https://aes2.org/wp-content/uploads/2024/01/20210924_TD1008_v3.13.pdf
- Vicanek, matched biquads: https://vicanek.de/articles/BiquadFits.pdf
- Holters, stateful ADAA (DAFx-19): https://www.hsu-hh.de/ant/wp-content/uploads/sites/699/2020/10/DAFx2019_paper_4.pdf
- Schlecht, FDN Toolbox (DAFx-20): https://dafx2020.mdw.ac.at/proceedings/papers/DAFx2020_paper_53.pdf
- Dattorro, Effect Design Part 1: https://ccrma.stanford.edu/~dattorro/EffectDesignPart1.pdf
- Holters & Parker, BBD model (DAFx-18): https://www.dafx.de/paper-archive/details/KbFTgvcTMmHQ2bHZvOUekw
- Torcoli et al., objective measures of perceptual audio quality: https://arxiv.org/pdf/2110.11438
- Multimodal models on MIDI vs. audio: https://arxiv.org/abs/2510.22455
- DAWZY: https://arxiv.org/abs/2512.03289
- ChatMusician: https://arxiv.org/html/2402.16153v1
- MIDI-LLM: https://arxiv.org/html/2511.03942
- Gareus, latency compensation thesis: https://gareus.org/misc/thesis-p8/2017-12-Gareus-Lat.pdf

### DAW behaviour
- Ableton Audio Fact Sheet: https://www.ableton.com/en/manual/audio-fact-sheet/
- Ableton Delay Compensation FAQ: https://help.ableton.com/hc/en-us/articles/209072409-Delay-Compensation-FAQ
- Ableton clip-edge fades: https://help.ableton.com/hc/en-us/articles/209069969-Create-Fades-on-Clip-Edges-to-avoid-clicks
- Live audio effect reference: https://www.ableton.com/en/manual/live-audio-effect-reference/
- Live limiter in Max: https://docs.cycling74.com/reference/abl.device.limiter~
- Live 12 MIDI Tools: https://www.ableton.com/en/live-manual/12/midi-tools/
- Ableton Extensions SDK: https://ableton.github.io/extensions-sdk/ and https://www.ableton.com/en/blog/introducing-extensions-sdk/
- Admiral Bumblebee, pan curves: https://www.admiralbumblebee.com/music/2019/12/08/Daw-V-Daw-Pan-Curves.html
- Admiral Bumblebee, DAW v DAW part 1: https://www.admiralbumblebee.com/music/2019/02/17/Daw-V-Daw-Differ.html
- Admiral Bumblebee, automation part 4: https://www.admiralbumblebee.com/music/2019/06/22/Daw-V-Daw-Automation-Part-4.html
- Infinite Wave SRC methodology: https://src.infinitewave.ca/help.html
- REAPER feature list: https://www.reaper.fm/about.php
- REAPER anticipative FX: https://forum-amz.cockos.com/showthread.php?t=191452
- Bitwig Operators: https://www.bitwig.com/userguide/latest/operators/
- Bitwig plugin hosting modes: https://www.bitwig.com/userguide/latest/vst_plug-in_handling_and_options/
- Steinberg ASIO-Guard: https://helpcenter.steinberg.de/hc/en-us/articles/206103564-Details-on-ASIO-Guard-in-Cubase-and-Nuendo
- Ardour 6: https://ardour.org/news/6.0.html
- Ableton ADC 2025 scheduling talk: https://conference.audio.dev/efficient-task-scheduling-in-a-multithreaded-audio-engine-rachel-susser-adc-2025
- Apple audio workgroups: https://developer.apple.com/documentation/audiotoolbox/adding-parallel-real-time-threads-to-audio-workgroups
- FabFilter Pro-L 2 true-peak limiting: https://www.fabfilter.com/help/pro-l/using/truepeaklimiting
- Bungee stretch comparison: https://bungee.parabolaresearch.com/compare-audio-stretch-tempo-pitch-change
- Logic Scripter: https://support.apple.com/guide/logicpro/processmidi-function-lgce225e4d89/mac

### Engines, libraries, licences
- Tracktion Engine: https://github.com/Tracktion/tracktion_engine and https://github.com/Tracktion/tracktion_engine/blob/develop/LICENSE.md
- Tracktion benchmarks page: https://tracktion.github.io/tracktion_engine/benchmarks.html
- Tracktion graph discussion: https://forum.juce.com/t/node-graph-clarifications/56170
- JUCE licence: https://github.com/juce-framework/JUCE/blob/master/LICENSE.md and https://juce.com/get-juce/
- VST3 licensing: https://steinbergmedia.github.io/vst3_dev_portal/pages/VST+3+Licensing/VST3+License.html
- VST3 and MIDI: https://steinbergmedia.github.io/vst3_dev_portal/pages/Technical+Documentation/About+MIDI/Index.html
- VST 3.8 release: https://forums.steinberg.net/t/vst-3-8-0-sdk-released/1011988
- CLAP note ports: https://github.com/free-audio/clap/blob/main/include/clap/ext/note-ports.h
- clack (Rust CLAP host): https://github.com/prokopyl/clack
- Dropseed: https://github.com/MeadowlarkDAW/Dropseed
- plugin_host crate: https://lib.rs/crates/plugin_host
- chowdsp_utils: https://github.com/Chowdhury-DSP/chowdsp_utils
- chowdsp_wdf: https://github.com/Chowdhury-DSP/chowdsp_wdf
- RTNeural: https://github.com/jatinchowdhury18/RTNeural
- NAM Architecture 2: https://www.tone3000.com/blog/introducing-neural-amp-modeler-nam-architecture-2-a2
- Signalsmith DSP: https://signalsmith-audio.co.uk/code/dsp/
- Signalsmith Stretch: https://github.com/Signalsmith-Audio/signalsmith-stretch
- Bungee: https://github.com/bungee-audio-stretch/bungee and https://github.com/Ableton/bungee
- Rubber Band: https://breakfastquay.com/rubberband/
- Surge XT FAQ: https://surge-synthesizer.github.io/faq/
- beat_this: https://github.com/CPJKU/beat_this
- Ableton Link: https://github.com/ableton/link
- DAWproject: https://github.com/bitwig/dawproject
- MTS-ESP: https://github.com/ODDSound/MTS-ESP
- Faust: https://github.com/grame-cncm/faust
- Cmajor licence: https://cmajor.dev/docs/Licence
- incant-audio: https://github.com/Losera/incant-audio
- yabridge: https://github.com/robbert-vdh/yabridge
- Windows MIDI Services: https://blogs.windows.com/windowsexperience/2026/02/17/making-music-with-midi-just-got-a-real-boost-in-windows-11/

### Legal
- Ableton EULA: https://www.ableton.com/en/eula/
- Ableton patents: https://www.ableton.com/en/legal/patents/
- 17 USC §1201: https://www.law.cornell.edu/uscode/text/17/1201
- Directive 2009/24/EC: https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32009L0024
- SAS v. WPL: https://www.wipo.int/wipolex/en/judgments/details/1728
- Bowers v. Baystate: https://caselaw.findlaw.com/court/us-federal-circuit/1202776.html
- Sega v. Accolade: https://copyright.gov/fair-use/summaries/segaenters-accolade-9thcir1992.pdf
- Sony v. Connectix: https://law.justia.com/cases/federal/appellate-courts/F3/203/596/474793/
- Google v. Oracle: https://supreme.justia.com/cases/federal/us/593/18-956/
- Interfaces after Google v. Oracle: https://texaslawreview.org/interfaces-and-interoperability-after-google-v-oracle/

### Agent-native design and landscape
- Anthropic, code execution with MCP: https://www.anthropic.com/engineering/code-execution-with-mcp
- Cloudflare Code Mode: https://blog.cloudflare.com/code-mode-mcp/
- Zoo text-to-CAD: https://zoo.dev/research/introducing-text-to-cad
- Remotion OTIO export: https://www.remotion.dev/docs/export-opentimeline
- Figma canvas for agents: https://www.figma.com/blog/the-figma-canvas-is-now-open-to-agents/
- Suno acquires WavTool: https://suno.com/blog/suno-acquires-wavtool
- MCP in audio survey: https://sonicfield.org/ai-agents-enter-the-studio-the-mcp-turn-in-audio
- AbletonOSC paper (NIME 2023): https://nime.org/proceedings/2023/nime2023_60.pdf
