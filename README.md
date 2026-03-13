# BAP Labs Ableton Sleeve for LLMs

A comprehensive MCP bridge giving any LLM full control over Ableton Live — 70+ MCP tools across 13 categories, 500+ plugin parameter maps (111 Ableton native + 319 third-party VSTs), arrangement view GUI automation via AppleScript, and local-first inference on Apple Silicon via MLX. Developed on macOS/Apple Silicon, with core MCP tools (57 of 70+) working cross-platform on Windows and Linux. No cloud APIs required.

## Architecture

```
User Input → Qwen3-4B (MLX local) → Unified MCP Bridge
                                        ├→ Ableton Live (socket MCP, port 9877)
                                        ├→ VST Hub (OSC port 9878, synths)
                                        └→ VST FX Chain (OSC port 9879, effects)
```

## Quick Start

**Prerequisites**: Python 3.10+, Ableton Live 12

### macOS (full feature set, Apple Silicon recommended)

```bash
# Install dependencies
pip install mlx mlx-lm pythonosc pydantic librosa

# Install the Ableton Remote Script
# Copy ableton-mcp-fork/ contents to:
#   ~/Music/Ableton/User Library/Remote Scripts/AbletonMCP/

# Start Ableton Live (Remote Script connects on port 9877)

# Interactive mode (local Qwen3-4B via MLX)
python mlx_mcp_bridge.py

# Single command mode
python mlx_mcp_bridge.py -c "Set tempo to 128 and create a MIDI track called Drums"

# Claude API mode (requires ANTHROPIC_API_KEY)
python claude_mcp_bridge.py
```

### Windows (core MCP tools, 57 of 70+)

```bash
# Install dependencies (no MLX — use PyTorch + CUDA instead)
pip install torch pythonosc pydantic librosa anthropic

# Install the Ableton Remote Script
# Copy ableton-mcp-fork/ contents to:
#   ~\Documents\Ableton\User Library\Remote Scripts\AbletonMCP\

# Start Ableton Live (Remote Script connects on port 9877)

# Claude API mode (recommended entry point on Windows)
python claude_mcp_bridge.py

# For local inference, use Ollama (see Windows Alternatives below)
# ollama run qwen3:4b
```

**Example prompts:**
- "Create a 4-bar drum pattern at 140 BPM"
- "Mute the bass track and solo the vocals"
- "Split the clip at bar 8 and consolidate bars 1-4"
- "Load a Wavetable preset on track 3"
- "Set the reverb send on the Drums track to 60%"

## Platform Compatibility

| Component | macOS | Windows | Notes |
|-----------|:-----:|:-------:|-------|
| Core MCP Bridge (`unified_mcp_bridge.py`) | ✅ | ✅ | Pure socket + OSC |
| Claude API Bridge (`claude_mcp_bridge.py`) | ✅ | ✅ | Best Windows entry point |
| MLX Local Inference (`mlx_mcp_bridge.py`) | ✅ | ❌ | Apple Silicon only |
| GUI Automation — automator tools | ✅ | ❌ | AppleScript, see alternatives below |
| GUI Automation — smart_select tools | ✅ | ❌ | Coordinate-based click automation |
| Plugin Parameter Maps (500+) | ✅ | ✅ | Pure JSON |
| Ableton Remote Script | ✅ | ✅ | Standard Ableton Remote Script |
| LoRA Training (`train_llm_lora.py`) | ✅ | ✅ | PyTorch; CUDA recommended on Windows |
| Audio Analysis modules | ✅ | ✅ | librosa is cross-platform |
| Max/MSP Patches | ✅ | ⚠️ | VST3 mode works; AU references break |
| VST Hub/FX Chain (OSC) | ✅ | ✅ | pythonosc is cross-platform |

### Windows Alternatives

**For MLX Local Inference → Ollama or llama.cpp:**
- `ollama run qwen3:4b` gives you the same Qwen3-4B model on NVIDIA GPU
- Or use `llama-cpp-python` with CUDA for programmatic access
- Or use `claude_mcp_bridge.py` directly (cloud API, no local model needed)
- NVIDIA TensorRT-LLM achieves up to 16x speedup for Qwen3-4B vs baseline

**For AppleScript GUI Automation → pywinauto + pyautogui:**
- `pywinauto` — Windows GUI automation library, can target Ableton by window title, send keystrokes (`send_keys('^e')` for Ctrl+E = Split), click menu items
- `pyautogui` — Cross-platform mouse/keyboard control (click coordinates, hotkeys)
- Ableton uses the same keyboard shortcuts on Windows (Ctrl instead of Cmd):
  - Split: `Ctrl+E`, Consolidate: `Ctrl+J`, Group: `Ctrl+G`, etc.
- A `automator_bridge_win.py` would need to be written using `pywinauto.keyboard.send_keys()` — the operation list is identical, just the automation backend changes
- Note: requires Ableton to be in foreground (same constraint as macOS)

**For AudioUnit Max patches → VST3:**
- Change `"type": "AudioUnit"` to `"type": "VST3"` in Max patch JSON
- Or load VST3 versions manually in Max on Windows

---

# Section 1: LLM Ableton Harness & MCP

## Core MCP Bridge Files

| File | Description |
|------|-------------|
| **`mlx_mcp_bridge.py`** | Primary entry point. Connects Qwen3-4B (MLX) to Ableton via ReAct reasoning loop. Handles streaming inference, tool call parsing, and progressive tool disclosure. |
| **`unified_mcp_bridge.py`** | Universal bridge layer. All Ableton commands route through here. Provides name-based track resolution, dual VST control (synth hub + FX chain via OSC), and the full TOOL_CATALOG (13 categories). Single source of truth for all DAW control. |
| **`claude_mcp_bridge.py`** | Alternative bridge using Anthropic's Claude API SDK with native tool calling. Supports extended thinking. Imports `unified_mcp_bridge` for all Ableton operations. |

## MCP Tool Categories (70+ tools)

| Category | Tools | Description |
|----------|------:|-------------|
| `session` | 5 | Session state, tempo, playback |
| `track` | 9 | Create, delete, rename, route, fold, color tracks |
| `device` | 6 | Get/set parameters, enable/disable, load presets |
| `browser` | 3 | Browse presets, search by name |
| `clip` | 7 | Create, fire, stop, mute, set markers, color |
| `master` | 4 | Master volume, device parameters |
| `mixer` | 7 | Volume, pan, mute, solo, sends, return tracks |
| `audio_clip` | 6 | Gain, pitch, loop, warp mode, warp markers |
| `transport` | 4 | Playhead position, start/stop |
| `selection` | 2 | Select track or arrangement clip |
| `smart_select` | 4 | Multi-track selection, grouping, layout calibration |
| `automator` | 16 | GUI automation — split, consolidate, group, freeze, export, etc. |
| `vst` | 4 | VST plugin load, parameter control, GUI open |

All tools accept **track names or indices** (e.g., `"track_index": "Drums"` or `"track_index": 2`). The bridge resolves names automatically.

## Plugin Parameter Maps (500+ plugins)

**111 Ableton native devices** (`plugin_parameter_maps/ableton/`):
- Instruments: Analog, Collision, Drift, Electric, Emit, Granulator III, Meld, Operator, Sampler, Simpler, Tension, Wavetable
- Effects: EQ Eight, Compressor, Echo, Hybrid Reverb, Roar, Saturator, Chorus-Ensemble, Phaser-Flanger, and all stock effects
- DS drums, CV devices, and more

**319 third-party VSTs** (`plugin_parameter_maps/`):
- **Xfer**: Serum, Serum 2
- **FabFilter**: Pro-Q 3, Pro-L 2, Saturn 2, Pro-C 2, Pro-R, Pro-DS, Pro-MB, Pro-G, Timeless 3, Volcano 3, Simplon, Twin 3, Micro
- **Waves**: SSL E/G Channel, OneKnob series, H-Delay, CLA-76, dbx 160, L1/L2, Renaissance series, and dozens more
- **Antares**: Auto-Tune Pro, Auto-Tune Artist, Auto-Tune EFX+, Harmony Engine, AVOX suite (Aspire, Articulator, Choir, Duo, Mutator, Sybil, Warm, Throat)
- **Valhalla**: Room, Shimmer, Freq Echo, Delay, Supermassive, VintageVerb
- **Plugin Alliance**: bx_console (SSL 4000 E/G, Neve N), bx_masterdesk, bx_digital V3, Lindell 80, Elysia alpha, Shadow Hills, SPL, Neold
- **SoundToys**: Decapitator, EchoBoy, Crystallizer, Devil-Loc, Little AlterBoy, PanMan, PrimalTap, Radiator, Tremolator
- **SSL**: Channel Strip 2, Bus Compressor 2, Drumstrip, Vocalstrip 2, FlexVerb, X-EQ 2
- **Arturia**: Comp TUBE-STA, Comp VCA-65, Comp FET-76, Pre 1973, Pre TridA, Rev PLATE-140, Rev SPRING-636, Delay TAPE-201
- **Others**: Cradle, oeksound soothe2, Unison MIDI Chord

## Arrangement View Capabilities

> **This is the key differentiator.** The Ableton Live Object Model (LOM) does NOT expose split, consolidate, group, freeze, flatten, or reverse operations. Every other Ableton MCP is limited by this.

Our solution: **AppleScript GUI automation** via `AbletonMCP_Extended/automator_bridge.py`.

**Full operation list:**

| Operation | Method | Shortcut |
|-----------|--------|----------|
| Split clip | keystroke | `Cmd+E` |
| Consolidate | keystroke | `Cmd+J` |
| Group tracks | keystroke | `Cmd+G` |
| Ungroup tracks | keystroke | `Cmd+Shift+G` |
| Duplicate | keystroke | `Cmd+D` |
| Quantize | keystroke | `Cmd+U` |
| Freeze track | menu click | Edit > Freeze Track |
| Flatten track | menu click | Edit > Flatten |
| Reverse clip | menu click | Edit > Reverse |
| Export audio | keystroke | `Cmd+Shift+R` |
| Move track up/down | keystroke | `Cmd+Up/Down` |
| Undo/Redo | keystroke | `Cmd+Z` / `Cmd+Shift+Z` |
| Custom keystroke | passthrough | Any key + modifiers |

**Smart multi-track selection**: Click automation for non-contiguous track selection (e.g., select tracks "Drums", "Bass", "Vocals" simultaneously). Includes layout calibration for different screen sizes.

> **Windows note**: Arrangement view automation is currently macOS only (AppleScript). Windows port planned using `pywinauto` — same keyboard shortcuts (Ctrl instead of Cmd), different automation backend. See [Platform Compatibility](#platform-compatibility).

## Built on Anthropic MCP Best Practices

This project implements patterns recommended in Anthropic's [Building Effective Agents with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp):

1. **Progressive Tool Disclosure** — Instead of dumping 70+ tool definitions into the LLM context (which costs ~150K tokens), the bridge exposes `list_tools(category)` and `search_presets(query)` so the model discovers tools on-demand. This mirrors Anthropic's "filesystem navigation" pattern — achieving ~98% token savings on tool definitions.

2. **Categorical Tool Organization** — Tools are organized into 13 semantic categories (session, track, mixer, device, browser, clip, audio_clip, master, transport, selection, smart_select, automator, vst) following Anthropic's file-tree structure recommendation. Models explore categories first, then drill into specific tools.

3. **Local Execution Environment** — Following the article's emphasis on keeping processing local, all inference runs on-device via MLX. Intermediate results (track resolution, parameter filtering) are processed in the bridge layer before returning to the model, minimizing token round-trips.

4. **Detail Levels** — `list_tools` supports `detail="names"`, `"brief"`, or `"full"` — matching Anthropic's recommendation for customizable detail levels so models can get just tool names for orientation or full schemas when needed.

## How This Compares to Other Ableton MCPs

| Feature | BAP Labs Sleeve | ahujasid (base) | ableton-copilot | mcp-extended | cafeTechne |
|---------|:---:|:---:|:---:|:---:|:---:|
| Total MCP Tools | 70+ | ~16 | ~25 | ~20 | 220+ |
| Plugin Parameter Maps | 500+ | 0 | 0 | 0 | 0 |
| Arrangement View Editing | ✅ | ❌ | Partial | ❌ | ❌ |
| GUI Automation (Split/Consolidate/Group) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Name-Based Track Resolution | ✅ | ❌ | ❌ | ❌ | Partial |
| Progressive Tool Disclosure | ✅ | ❌ | ❌ | ❌ | ❌ |
| Local LLM (no cloud) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Dual VST Control (synth + FX) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Audio Clip Properties (warp/gain/pitch) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Mixer Controls (vol/pan/mute/solo/sends) | ✅ | ❌ | Partial | Partial | ✅ |
| Master Track Control | ✅ | ❌ | ❌ | ❌ | ? |
| macOS (full) / Windows (core MCP) | ✅ | ✅ | ✅ | ✅ | Win/Ab11 only |

**Key differentiators expanded:**

- **Plugin Parameter Maps**: No other MCP knows what parameters a plugin has. Our 500+ JSON maps let the LLM set "Filter Cutoff" on Serum by name instead of guessing parameter indices.
- **Arrangement View**: Operations like split, consolidate, group, freeze, and reverse are impossible through the LOM API. We bypass this with AppleScript GUI automation — the only MCP that can do this.
- **Name-Based Track Resolution**: Say `"track_index": "Drums"` instead of remembering that Drums is track 3. The bridge resolves names to indices automatically.
- **Progressive Disclosure**: Other MCPs dump all tool definitions upfront, consuming context window. We let the model discover tools categorically, following Anthropic's recommended pattern.
- **Local LLM**: Runs Qwen3-4B on Apple Silicon via MLX — no API keys, no latency, no cost.

## Key Ableton Integration Files

| File/Directory | Description |
|----------------|-------------|
| `ableton-mcp-fork/` | Forked ahujasid/ableton-mcp Remote Script (Ableton ↔ socket) |
| `AbletonMCP_Extended/automator_bridge.py` | AppleScript GUI automation (27 operations) |
| `plugin_parameter_maps/` | 500+ JSON parameter maps for VSTs and Ableton devices |

## Max/MSP Integration

| File | Description |
|------|-------------|
| `BAP Labs VST Hub.maxpat` | 8-slot synth VST control (OSC port 9878) |
| `BAP Labs VST FX Chain.maxpat` | 8-slot FX control (OSC port 9879) |
| `universal_vst_controller.js` | JavaScript controller for Max patches |
| `BAP Labs Serum Control.amxd` | Max for Live Serum device |

## Tests

| File | Description |
|------|-------------|
| `test_mcp_extensions.py` | 8-phase MCP command validation (1000+ lines) |
| `test_mlx_integration.py` | End-to-end MLX bridge integration test |
| `test_mcp_connection.py` | Basic MCP connectivity check |

```bash
pytest test_mlx_integration.py -v
```

---

# Section 2: LLM LoRA Fine-Tuning

## Training Pipeline

| File | Description |
|------|-------------|
| `train_llm_lora.py` | LoRA fine-tuning for Qwen3-4B with audio embeddings |

**Training data** (`data/llm_training/`):

| Dataset | Lines | Description |
|---------|------:|-------------|
| `train.jsonl` | 14,566 | Primary training data |
| `synthetic_serum_qa.jsonl` | 10,000 | Synthetic Serum preset Q&A |
| `ableton_manual_qa.jsonl` | 3,890 | Ableton manual Q&A |
| `serum_guide_qa.jsonl` | 2,295 | Serum guide Q&A |
| `val.jsonl` | 1,619 | Validation set |

- 7,583 Serum presets parsed (2,397 parameters each)
- Checkpoints saved to `checkpoints/`

## Audio Analysis

| File | Description |
|------|-------------|
| `structure_detector.py` | Song structure detection (librosa) |
| `beat_similarity.py` | Rhythm pattern evaluation |
| `bassline_similarity.py` | Bassline analysis |
| `mix_encoder.py` | CLAP-based audio encoding |
| `benchmark_midi_generation.py` | LLM MIDI generation benchmarks |

## Evaluation

- `eval/` — Evaluation scripts and results
- `benchmark_midi_generation.py` — Multi-task LLM benchmarking

---

## Current Status

- ✅ 70+ MCP tools across 13 categories
- ✅ 500+ plugin parameter maps (111 native + 319 third-party)
- ✅ Arrangement view GUI automation (27 operations)
- ✅ Local Qwen3-4B inference via MLX
- ✅ Name-based track resolution
- ✅ Progressive tool disclosure
- ✅ Dual VST control (synth hub + FX chain)
- ✅ Session View operations (create tracks, clips, add notes, control playback)
- ✅ 7,583 Serum presets parsed
- ✅ LoRA training pipeline
- ❌ Rendered audio dataset (planned)
- ❌ CNN audio feature extractor (planned)
- ❌ CLAP audio input integration with MCP bridge (planned)

## Tech Stack

Python 3.10 · MLX · Qwen3-4B · Ableton Live 12 · Max for Live · ahujasid/ableton-mcp (forked) · pythonosc · pydantic · librosa · Anthropic SDK · Ollama/llama.cpp (Windows alternative to MLX)

## Project Context

See `.claude/PROJECT_CONTEXT_FOR_CLAUDE_CODE.md` for full architecture docs, phase breakdown, and design decisions.
