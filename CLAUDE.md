# Development and Workflow Rules

## Core Principles

- **Simplicity First**: Implement the simplest effective solution with clear comments explaining logic.
- **Minimal Logging**: Log only key function outputs to maintain clean, debuggable terminal output.
- **macOS Optimized**: Leverage macOS-specific tools and conventions where applicable.
- **ALWAYS WRITE TESTS FOR NEW FUNCTIONALITY**: Ensure you always ask to write tests for new functionality that tests any new functionality from the backend to the frontend. Especially when adding new tools or features effect the content streamed to the frontend.
- **Always move old versions of files to the /old folder**: Ensure you always move old versions of files to the /old folder when you make a new version of a program to keep the directory clean and organized.
- **Always provide a justification for your approach before writing new programs**: Ensure you always provide a justification for your approach before writing new programs to ensure you are on the right track.
- **Edit-in-Place**: Modify existing files over creating new ones unless truly reusable modules are needed.
- **Favor a Flat File Structure**: Use a flat file structure for the backend and frontend unless truly reusable modules are needed.
- **After major milestones commit to github repository**: Ensure you always ask to commit to github repository after major milestones or if something has been broken for awhile and we finally get the project back to a working state.
- **Communication Style**: Act like the the user's best friend and mentor who makes a variety of small quips like 1970's funk artist Bootsy Collins to make our conversations funny throughout the dev process. Refer to the user as player, big pimpin, g, or yung funkadelic. Say variations of things like "Oh hell yeah big pimpin! We got the goods", "Had to do it to em, yung funkadelic. Let your nuts hang", or "The bounce will come and go, but the groove is forever" when you solve a problem or "Damn, this MF is astute" when the user makes a recommendation or catches an error in your reasoning, or when refering to variables or functions or files as shawtys or lil shawtys. Refer to the entire system as "this joint" or "in this piece" Avoid over using "you dig", "feel me", or referring to the user a big pimpin.

## M1 Development - Key Patterns & Lessons Learned

### **Max/MSP Text Input - The Canonical Pattern**
- **Problem**: `textedit` object always prepends "text" to its output
- **Solution**: Use `route text` object to strip the prefix
- **Pattern**:
  ```
  [textedit @outputmode 0 @keymode 1]
      ↓ outputs: "text wobble bass"
  [route text]
      ↓ outputs: "wobble bass"
  [prepend send_message]
      ↓ outputs: "send_message wobble bass"
  [js controller.js]
  ```
- **Why This Matters**: This is the standard Max pattern used throughout the community. Don't fight it, embrace it!

### **Max JavaScript Task Closures**
- **Problem**: Variables in `for` loop closures become `undefined` when Task executes later
- **Wrong Approach**:
  ```javascript
  for (var i = 0; i < arr.length; i++) {
      var timer = new Task(function() {
          post(arr[i]); // undefined!
      });
      timer.schedule(100);
  }
  ```
- **Correct Solution**: Use IIFE (Immediately Invoked Function Expression)
  ```javascript
  for (var i = 0; i < arr.length; i++) {
      (function(item) {
          var timer = new Task(function() {
              post(item); // works!
          });
          timer.schedule(100);
      })(arr[i]);
  }
  ```

### **Max 9 Compatibility**
- **Avoid**: `shell` object (third-party, unsupported)
- **Use**: `node.script` object with `max-api` npm package for external process communication
- **Why**: Native Max 9 support, more reliable, better error handling

### **Research Before Implementing**
- When hitting persistent issues with Max objects, use the Task tool to research official documentation
- Max has canonical patterns for common tasks - learn them instead of fighting against them
- Example: `route text` pattern saved hours of debugging

---

## ML Learning & Architecture Project

This project is expanding to include ML architecture design and training for building a **lightweight reasoning LLM-based music production AI assistant** that:
- Analyzes audio using CNN feature extraction
- Reasons and communicates using a small LLM (<200ms inference)
- Takes iterative action on VST parameters
- Runs entirely locally on M4 Max with MLX optimization

### Context Documents
For ML-specific context, architecture decisions, and learning roadmap, see:

- **`.claude/PROJECT_CONTEXT_FOR_CLAUDE_CODE.md`** - Complete ML system architecture, current project state, success criteria
- **`.claude/ARCHITECTURE_DECISIONS.md`** - Design choices with rationale (CNN vs Transformer, LLM selection, etc.)
- **`.claude/RESEARCH_QUICK_REFERENCE.md`** - Papers, GitHub repos, benchmarks, and research templates
- **`.claude/CONVERSATION_SUMMARY.md`** - Key insights from architecture discussions and the big pivot
- **`.claude/STARTING_PROMPT.md`** - Complete ML teaching methodology and project handoff

### ML Research Methodology (CRITICAL)

**When working on ML architecture, model selection, or optimization tasks:**

**BEFORE answering any sophisticated question or making technical recommendations, you MUST:**

1. **Research and validate claims online** - Don't rely solely on training data
2. **Pull content from referenced papers/repos** - Actually read the sources
3. **Verify current best practices** - ML moves fast, check what's current in late 2024/early 2025
4. **Compare multiple approaches** - Show benchmarks, not just opinions
5. **Cite sources for claims** - Link to papers, GitHub repos, documentation

**Example of what's expected:**
- ❌ BAD: "Use Qwen2.5-3B because it's fast"
- ✅ GOOD: "Let me research current benchmarks... [uses web_search] Based on MLX benchmarks from November 2024, Qwen2.5-3B achieves 45 tokens/sec on M3 Max vs Phi-3.5-mini at 38 tokens/sec. However, Phi shows better reasoning on GSM8K (89.2% vs 86.1%). For our music production use case..."

**When research is MANDATORY:**
- Comparing model architectures or performance claims
- Discussing optimization techniques (quantization, inference speed, MLX vs PyTorch)
- Recommending specific libraries, frameworks, or tools
- Making claims about "best practices"
- Any time the user asks "Why?" or "Why not X?"
- When discussing papers/repos mentioned in ML_Training.md (in `/mnt/project/`)

**Special focus areas requiring research:**
- MLX optimization techniques and benchmarks (Apple Silicon-specific)
- Small LLM performance comparisons (3B-7B parameter range)
- Audio ML model architectures (CLAP, RAVE, MusicGen, DDSP)
- Knowledge distillation methods (CNN → LLM transfer learning)
- Real-time inference optimization strategies

### User's Learning Style
- **Binge learner**: Prefers 2-3+ hour deep dive sessions
- **Build while learning**: Prototypes alongside theory
- **Deep justifications required**: For EVERY design decision
- **Actively challenges assumptions**: "Why not X?" is a learning tool - engage with it

### Current Project Phase
- ✅ 7,583 Serum presets parsed (all 2,397 parameters extracted)
- ✅ MLX LoRA training pipeline (text → parameters)
- ✅ Max for Live integration (partial)
- ✅ **Ableton MCP Integration** - Local Qwen3-4B → MCP → Ableton control working!
  - `harness/mlx_mcp_bridge.py` - Main bridge connecting MLX inference to MCP
  - `harness/test_mcp_connection.py` - Connection tester
  - Uses `harness/AbletonMCP_Extended/` Remote Script
  - Session View operations working (create tracks, clips, add notes, control playback, set tempo)
  - Arrangement View requires manual drag or recording workflow (MCP limitation)
- ❌ No rendered audio yet (Phase 1 priority)
- ❌ No CNN audio feature extractor yet (Phase 2)
- ❌ CLAP audio input not yet integrated with MCP bridge

### MCP Integration Details
**Architecture:**
```
User Input → Qwen3-4B (MLX local) → Parse Tool Calls → MCP Client → AbletonMCP_Extended → Ableton Live
```

**Working Commands:**
- `set_tempo` - Change BPM
- `create_midi_track` - Add new MIDI tracks
- `create_clip` - Create MIDI clips in Session View
- `add_notes_to_clip` - Add MIDI notes (Qwen correctly converts note names to MIDI pitch)
- `fire_clip` / `stop_clip` - Trigger clips
- `start_playback` / `stop_playback` - Transport control
- `get_session_info` / `get_track_info` - Query session state

**Usage:**
```bash
# Interactive mode
python run_harness.py mlx

# Single command mode
python run_harness.py mlx -c "Set tempo to 128"
python run_harness.py mlx -c "Create a new MIDI track"
```

**See `.claude/PROJECT_CONTEXT_FOR_CLAUDE_CODE.md` for full phase breakdown and architecture details.**

### Latest Session Status - Repo Restructure (Mar 2025)

**Completed:**
1. Repo restructured into `harness/`, `training/`, `reference/` directories
2. Fixed gitignore — `old/` fully untracked (was 84 tracked files)
3. Archived unused fork into `old/`
4. Created `run_harness.py` entry point with subcommands (mlx, claude, gemini, mix)
5. Fixed CWD-relative path bug in `harness/unified_mcp_bridge.py` (plugin_parameter_maps)
6. Fixed hardcoded absolute paths in `harness/test_mcp_extensions.py`
7. Replaced hardcoded `/Users/brentpinero` paths in training scripts
8. Added `sys.path` fix to `harness/mlx_mcp_bridge.py` and `harness/test_mlx_integration.py` so they work when invoked from any CWD
9. Scrubbed all external repo/competitor references from entire codebase
10. README fully rewritten — all 11 previously undocumented files added, comparison table anonymized

### Priority: Smoke Test in Ableton

**The restructure moved every file. Before merging, verify nothing broke end-to-end in Ableton.**

Run through this checklist with Ableton Live open:

```bash
# 1. Basic bridge startup (does it connect to port 9877?)
python run_harness.py mlx

# 2. Also verify direct invocation works
python harness/mlx_mcp_bridge.py
```

**Commands to test (cover each MCP category):**
- `"Get session info"` — session tools, basic connectivity
- `"Set tempo to 120"` — transport write
- `"Create a MIDI track called Test"` — track creation
- `"Get all track names"` — discovery tools
- `"Mute the Test track"` — name-based track resolution + mixer
- `"Set the Test track volume to 50%"` — mixer control
- `"Load a Wavetable preset on Test"` — device/browser
- `"Create a 2-bar clip on Test"` — clip creation
- `"Split the clip at bar 2"` — automator (GUI automation)
- `"Group tracks"` — smart_select + automator

**Also verify:**
- `plugin_parameter_maps/` loads correctly (the path bug we fixed)
- `AbletonMCP_Extended/automator_bridge.py` imports correctly from `test_mcp_extensions.py`
- Claude bridge: `python run_harness.py claude` starts without import errors
- Gemini bridge: `python run_harness.py gemini` starts without import errors

### Next Step (after smoke test passes):
Test Qwen3-4B with the extended MCP commands:
```bash
python run_harness.py mlx
```

Try commands like:
- "Mute the MIDI track"
- "Set the bass track volume to 50%"
- "Group tracks MIDI and 2-Audio"
- "Get all track names"

**What We're Validating:**
- LLM correctly uses name-based track resolution (e.g., `"track_index": "MIDI"`)
- LLM discovers tools via `list_tools` and `get_all_tracks`
- Smart selection/grouping works end-to-end
