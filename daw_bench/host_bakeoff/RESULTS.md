# Plugin-hosting bake-off: results (2026-11-08)

M4 Max, macOS 26, 48 kHz, 512-sample blocks. Run data: `sandbox_sessions/host_bakeoff/`
(`compat_run3/`, `serum_refreeze3/`, `serum_july_tempo/`, `kill_run3/`; not in git). How to
reproduce: `README.md`. Serum vs a fresh freeze:
`python daw_bench/host_bakeoff/bakeoff.py --only serum --freeze-wav "<Freeze/....wav>" --clip-start-beats 0 --bpm 126`
(or `--freeze-dir <project>/Samples/Processed/Freeze` to watch for one).

## Verdict

**Use plughost (Rust) as the out-of-process plugin host, behind the Tracktion C++ engine.**
It ran every hostable plugin, crash recovery comes built in, and its IPC overhead is about
1/20 of the gate. To match it in C++ we would first have to build what plughost already
ships: a helper process, a shared-memory transport, snapshot and recovery, and per-bus
layout negotiation.

## Phase 1 gates

| Gate | Target | C++ (JUCE, in-process) | Rust (plughost, out-of-process) |
|---|---|---|---|
| Load, process, save and restore without error | ≥ 95% of the list | 47/48 = 97.9% (Pro-Q 3 AU segfaults) | **48/48 = 100%** |
| Restore nulls, deterministic plugins | — | 22/22 | 26/27 (Disperser AU loses the edit) |
| Kill the plugin process, engine keeps running | yes | n/a: the plugin is in the host process | **yes: recovered in 123 ms, render finished** |
| Added time per block, out-of-process | ≤ 0.3 ms | baseline | **median 0.013 ms, p90 0.024, max 0.089** (47 plugins) |
| Serum 2 vs Ableton freeze, 20–250 Hz | ≤ 1 dB | **+0.27 dB, flat across bands** (with transport tempo; +14.3 dB without) | **+0.27 dB** (bit-identical to C++) |
| Realtime: CPU ≤ 10%, 300 tracks at 128 samples | | not measured | not measured |

The list has 50 plugins (25 VST3, 25 AU, `plugin_list.json`). Two are excluded from every
rate: Vital VST3 is x86_64-only, and Oxford Inflator is unlicensed on this machine.

Single combined figure (`bakeoff.py --summarize`): probe finished, output finite, and restore
passes. That means a null for deterministic plugins and a single-pair spectral check for the
rest. **Rust 44/48 (91.7%), C++ 43/48 (89.6%).** Neither reaches 95% on this rule, but the
spectral half is noise-limited (see finding 6). The deterministic-only figures in the table
are the reliable comparison.

## Findings

1. **The two hosts produce the same audio.** Serum 2 rendered by JUCE and by plughost nulls
   to zero, offline and in realtime mode, and so do the passing plugins in the integration
   test. Neither host adds a sound of its own.
2. **The Serum low-end gap was missing tempo, not the host.** All three headless renderers
   (JUCE, plughost, and the July pedalboard render) agreed with each other, but none sent the
   plugin a transport. The patch has tempo-synced modulation, so Serum ran it at its own
   default tempo.

   Sending a playing transport at the set's tempo (job field `bpm`) closes the gap, against
   both freezes:

   | Freeze | No transport (20–60 / 60–120 / 120–250 Hz) | With tempo | Null |
   |---|---|---|---|
   | Fresh, 2026-11-08 (Serum 2.1.5, 126 BPM, 44.1 kHz) | −1.4 / −5.4 / −0.8 dB | **+0.27 dB flat in all 8 bands** | 19 dB |
   | July (Serum 2.1.2, 100 BPM, 48 kHz) | +6.1 / +14.3 / +6.9 dB | **+0.6 dB flat** | 11 dB |

   A flat offset is a level difference, not timbre. Ruled out on the way: offline vs realtime
   mode (bit-identical), the hosting library, and the Serum version.

   **Consequence for the sandbox:** pedalboard 0.9.17's `VST3Plugin` has no tempo or playhead
   API, and `daw_translation/render_worker.py` uses `--bpm` only to time the MIDI notes. So
   every headless render of a tempo-synced patch in the sandbox has been off-tempo.

   Live gotcha: a freeze file starts at the track's **first clip**, not bar 1.
3. **The C++ host needed four fixes that plughost already handles:**
   - module and instance calls belong on the main thread (Kontakt starts Qt, which deadlocked
     until moved there);
   - instruments that declare an input bus need it disabled, not dropped;
   - when a plugin refuses stereo and mono, fall back to its own default layout;
   - instances must be released on the message thread (a UAD AU hung at teardown).
   Even after these, Pro-Q 3 AU crashes inside its render (null pointer in `AudioUnitRender`,
   called from JUCE's AU wrapper), and four AUs (Pultec, Disperser, God Particle, Trash 2)
   don't repeat after `reset()` in JUCE (−12 to −38 dBFS), while plughost renders them
   bit-exactly.
4. **plughost's real weak spot: Disperser AU loses a parameter edit across save and restore**
   (the restored render equals the unedited one). JUCE keeps it. Report this upstream with a
   minimal repro before relying on Audio Unit state.
5. **Loading is slower out-of-process.** Median 132 ms vs 39 ms, restore 165 ms vs 19 ms,
   because each chain starts a helper. This doesn't matter offline. For live use, keep
   helpers warm.
6. **About half the list is non-deterministic by design** (random oscillator phase, analog
   noise, free LFOs): 21 plugins under plughost, 25 under JUCE. A single repeat can't decide
   their state restore. A sample-level null doesn't apply, and a spectral check with one
   repeat pair was too noisy (verdicts flipped between hosts). Settle these with N ≥ 5
   repeats per plugin.

## Method changes made after seeing data (disclosed)

- **Restore rule.** v1 accepted a restore within 6 dB of the plugin's own repeat. That let
  random-phase synths pass trivially. Now: deterministic plugins must null to −80 dBFS; for
  the rest the result is reported as undecided rather than guessed.
- **Harness bugs fixed between runs** (none favour one host): the C++ items in finding 3,
  mono input channel count in the Rust probe, recovery limited to real helper deaths, and
  never editing a bypass control (Audio Unit state doesn't store bypass).

## Not covered yet

- **Realtime gates:** plughost's `RealtimeEndpoint` driven by an audio device at 128 samples,
  missed-quantum rate, track ramp, CPU.
- **Determinism over 10 renders, and a larger list** (gate for beta: 200 plugins).
- **CLAP**, through plughost (3 FabFilter CLAPs installed).
- **Licence and authorisation dialogs while unattended.** Oxford Inflator failed fast in
  both hosts once loading moved to the main thread; no dialog was observed.
