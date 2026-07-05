# Render Node Setup — Isolated Ableton for the Faithful Sandbox

The render node is a **separate Ableton instance the model drives but you never touch**. It makes the sandbox loop faithful (real stock devices + plugins + content + offline quality) *and* non-intrusive (its own desktop → nothing steals focus from your working Mac). See `plan` (`floating-questing-pearl.md`) and `docs/fidelity_findings.md` for why this is required.

The host-side software is done and isolation-agnostic — everything is `host:port` config. This doc is the **node-side** provisioning (your action items).

## Render mode: real-time RESAMPLING (default) — no GUI automation

**Verified 2026-07-04:** Live's API exposes **no** export/render/freeze function (confirmed across the Live Object Model reference + AbletonOSC + a 220-tool LiveAPI project), and Ableton's Export **dialog** popup is drawn in a custom framework that macOS Accessibility can read but **cannot set** (zero `AXMenuItem`s). So the faithful path is **LOM-native real-time resampling**: for each role the loop creates a source MIDI track (instrument + arrangement clip) and an armed audio track routed from it (post-FX), then does **one real-time arrangement-record pass** that captures every stem at once, and reads each recorded clip's `file_path`. This is pure Live API — **no osascript, no Accessibility, no focus theft** — so it needs neither the automator nor (for a same-Mac/mounted node) the wav-fetch agent. `render.node_render_mode="resample"` (default). The legacy per-role GUI **Freeze** path remains as `render.node_render_mode="freeze"`.

Because rendering no longer uses GUI automation, steps 3–4 below (Accessibility, export pre-config) are only needed for the optional `freeze` mode.

## 1. Pick an isolation mechanism
| Option | Isolation | Cost | Notes |
|---|---|---|---|
| **Local macOS VM** (Parallels/UTM) | Own desktop on your Mac | 2nd Ableton auth + CPU/RAM/disk | Recommended: one machine, no focus theft. |
| **2nd machine on LAN** (spare Mac/Mac mini) | Physical | Spare hardware | Cleanest; uses your 2nd auth legitimately. |
| **Cloud desktop** | Remote | Paid | Off-machine; watch plugin licensing/content on cloud HW. |

Same-Mac `open -n` is **not** suitable for the continuous loop — it shares one desktop, so freeze/export would fight your foreground work.

## 2. Provision the node
1. Install **Ableton Live 12 Suite** (use your 2nd authorization).
2. Install the user's plugins — **Serum 2 + any third-party** the projects use.
3. **Install the exact factory content** the patches reference (root cause of the measured headless gap): Serum's `Serum Presets Path` (default `/Library/Audio/Presets/Xfer Records/Serum 2 Presets/`) must exist with the same wavetables/samples. Copy `~/Library/Preferences/Serum2Prefs.json` from your main Mac if paths differ.
4. Grant **Accessibility permission** to whatever runs `osascript` (Terminal/the agent) — required for Freeze/Export GUI automation.
5. Create and **SAVE a Live project** on the node (freeze needs a project folder). Note its path → this is `render.node_project_dir`.

## 3. Install + expose the Remote Script (on the node)
1. Copy `harness/AbletonMCP_Extended/` into the node's `MIDI Remote Scripts` folder and select it as a Control Surface (same as your main setup).
2. **Make it listen off-localhost** so the host can reach it. In the node's copy of `AbletonMCP_Extended/__init__.py`, change the bind host from `"localhost"` to `"0.0.0.0"` (near `DEFAULT_PORT = 9877`). **Do this only on the node**, and firewall port 9877 to your LAN — never expose it to the internet.
3. Reload the Control Surface (re-select it in Preferences → Link/MIDI).

## 4. Run the on-node agent (on the node)
GUI automation (Freeze/Export) and the freeze wavs are node-local, so a tiny agent runs there:
```bash
python harness/render_node_agent.py --host 0.0.0.0 --port 9878
```
It reuses `automator_bridge` (no new automation logic) and ships freeze wav bytes back to the host.

## 5. Point the host at the node
Set these via `sandbox_config` overrides (or session config):
```
render.backend        = "ableton"
render.node_host      = "<node LAN IP>"      # VM/machine/cloud; 127.0.0.1 for same-Mac testing
render.node_port      = 9877                  # Remote Script control socket
render.node_agent_port= 9878                  # render_node_agent
render.node_project_dir = "<SAVED project folder on the node>"
```

## 6. Phase-1 acceptance (verify before trusting the loop)
1. From the host: `RenderNodeClient(host, 9878).ping()` returns True.
2. `LiveClient(host, 9877).send("get_session_info")` returns the node's session.
3. Drive one role end-to-end (create track → load Serum + captured params → notes → freeze) and confirm the wav returns to the host — **with your main Mac's Ableton untouched and unfocused**.
4. **GUI-focus check**: Ableton's Freeze targets the *GUI-focused* track, not always LOM `selected_track`. Confirm the frozen wav is the intended track's audio. If not, enable `render.node_click_select` (uses the automator's click-select) and calibrate `AbletonLayoutConfig` pixel geometry for the node's screen.

## Security
The Remote Script socket is unauthenticated. Bind `0.0.0.0` **only** behind a LAN firewall (or a VM host-only network). Never port-forward 9877/9878 to the internet.
