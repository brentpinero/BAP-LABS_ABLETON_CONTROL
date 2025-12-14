# VST Plugin Parameter Mapping - Research Notes

## Summary
- **217 plugin JSON files created** in `plugin_parameter_maps/`
- **44 plugins fully mapped** (SSL, FabFilter, Soundtoys, Valhalla, oeksound, Xfer)
- **173 plugins need param research** (Plugin Alliance, Antares, Cradle, Waves, some others)

## Issues Discovered

### 1. VST Hub M4L Device (Port 9878)
**Status:** Param dump not implemented
**Action Required:** Add the same logging code from VST FX Chain to VST Hub M4L
**Affects:** All synth plugins (Serum, Serum2, Analog Lab V, etc.)

### 2. VST FX Chain M4L Device (Port 9879)
**Status:** Param dump works for SOME plugins but not others
**Symptoms:**
- SSL Native plugins: **WORKED** (37 plugins mapped successfully earlier in session)
- FabFilter plugins: **WORKED** (Pro-L 2, Saturn 2)
- Soundtoys plugins: **WORKED** (LittleAlterBoy, EffectRack)
- Valhalla/oeksound: **WORKED**
- Plugin Alliance (bx_, elysia, Lindell, SPL, Unfiltered, NEOLD, etc.): **0 PARAMS**
- Antares (Auto-Tune, AVOX): **0 PARAMS**
- Cradle (God Particle, The Spirit): **0 PARAMS**

**Later in session:** Even SSL started returning 0 params - M4L device may have gotten into bad state.

### 3. Plugins Returning 0 Parameters
Many plugins return 0 params even when properly loaded. This could be due to:

1. **Different VST3 parameter exposure methods**
   - Some plugins use `IEditController::getParameterCount()`
   - Others may use `IComponentHandler` or different interfaces
   - Some may only expose params after initialization/GUI open

2. **VST3 vs VST2 differences**
   - VST3 has more complex parameter handling
   - Some vendors may have incomplete VST3 implementations

3. **Plugin-specific issues**
   - Shell plugins (WaveShell, EffectRack) have dynamic params
   - Some plugins require specific initialization sequence

## Research Needed

### Priority 1: Fix M4L Param Enumeration
- [ ] Check what method the M4L vst~ object uses to enumerate params
- [ ] Research VST3 `IEditController` interface for param access
- [ ] Test if `vst~ @parameter` attribute affects enumeration
- [ ] Check if plugins need audio processing started to expose params

### Priority 2: Alternative Param Access Methods
- [ ] Research JUCE-based plugin param exposure (Plugin Alliance uses JUCE)
- [ ] Check if Antares uses proprietary param system
- [ ] Investigate if VST3 `IUnitInfo` interface provides param data
- [ ] Look into `IParameterChanges` as alternative

### Priority 3: Vendor-Specific Research
- [ ] **Plugin Alliance/Brainworx:** All 145 plugins return 0 - likely common cause
- [ ] **Antares:** 22 plugins return 0 - check Auto-Tune SDK docs
- [ ] **Cradle:** Check their VST3 implementation

## Plugins That Worked (Reference)

These worked with our current M4L approach - can be used as reference:
- SSL Native (all 37 plugins)
- FabFilter Pro-L 2, Saturn 2
- Soundtoys LittleAlterBoy, EffectRack
- ValhallaRoom
- oeksound soothe2

## File Structure

```
plugin_parameter_maps/
├── ssl_*.json          # 37 fully mapped
├── fabfilter_*.json    # 2 fully mapped
├── soundtoys_*.json    # 2 fully mapped
├── valhalla_*.json     # 1 fully mapped
├── oeksound_*.json     # 1 fully mapped
├── xfer_*.json         # 2 (serum2 refs existing, serum placeholder)
├── antares_*.json      # 22 placeholders
├── pa_*.json           # 145 placeholders (Plugin Alliance)
├── cradle_*.json       # 2 placeholders
├── waves_*.json        # 1 placeholder
├── arturia_*.json      # 1 placeholder
└── RESEARCH_NOTES.md   # This file
```

## Next Steps

1. Restart Ableton Live and re-test SSL plugins to verify M4L is functioning
2. Investigate vst~ parameter enumeration in Max/MSP documentation
3. Research VST3 SDK for alternative parameter access methods
4. Consider using vstplugininfo or similar tools to dump params externally
