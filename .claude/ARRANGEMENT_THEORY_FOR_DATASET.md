# Arrangement Theory for Dataset Curation

**Date**: 2025-12-01
**Purpose**: Understanding music arrangement theory to inform dataset design for arrangement-aware mixing advice

---

## Executive Summary

The model must understand **arrangement context** to give appropriate advice. "Cut 200Hz on the bass" might be correct in a dense drop but wrong in a sparse breakdown. This document outlines:
1. Core arrangement concepts
2. How arrangement affects mixing decisions
3. Existing datasets and their limitations
4. Our strategy for arrangement-aware data collection

---

## Part 1: Core Arrangement Concepts (Multi-Genre)

**IMPORTANT**: Genre-specific arrangement is critical. The model cannot give universal advice - mixing decisions depend heavily on genre conventions. A "good" mix in boom-bap hip hop would be wrong for K-pop.

### Genre Classification Framework

We organize genres by their **structural paradigm**:

| Paradigm | Genres | Core Principle |
|----------|--------|----------------|
| **Verse-Hook** | Hip Hop, R&B, Reggaeton | 16-bar verses, 8-bar hooks, groove-centric |
| **Verse-Chorus** | Pop, Rock, Country, Gospel | Traditional Western form, melodic hooks |
| **Build-Drop** | EDM, Trap, Drill, Phonk | Tension-release, rhythmic climax |
| **Groove-Based** | Funk, Afrobeats, Amapiano | Vamp-centric, subtle variations |
| **Section-Switch** | K-pop, Progressive | Multiple distinct sections, genre-blending |

---

### HIP HOP FAMILY

#### Standard Hip Hop Structure
From [Hip Hop Makers](https://hiphopmakers.com/how-to-make-beats-song-arrangements):

| Section | Function | Length | Notes |
|---------|----------|--------|-------|
| **Intro** | Set mood, minimal | 4-8 bars | Often just drums or sample |
| **Hook** | Memorable centerpiece | 8 bars | What people sing in cars |
| **Verse** | Storytelling, bars | 16 bars | Modern: often 12 bars |
| **Bridge** | Contrast, break pattern | 4-8 bars | Optional |
| **Outro** | Fade or cut | 4-8 bars | May repeat hook |

Common patterns:
- `Intro → Hook → Verse → Hook → Verse → Hook → Outro`
- `Intro → Verse → Hook → Verse → Hook → Bridge → Hook → Outro`

#### Boom-Bap (90s Hip Hop)
From [Native Instruments - What is Boom Bap](https://blog.native-instruments.com/what-is-boom-bap/):

**Key Characteristics:**
- **"Boom"** = kick, **"Bap"** = snare
- Swing quantization (not perfectly on grid)
- Jazzy samples, dusty vinyl aesthetic
- DJ Premier scratch hooks as chorus substitute
- MPC/SP-1200 workflow influences arrangement

**Mixing Implications:**
- Less sub-bass than modern hip hop
- Vinyl crackle/noise is intentional
- Drums are "punchy" not "booming"
- Sample-based, may have frequency limitations from source

#### Trap Music
From [Waves - How to Make Trap Beats](https://www.waves.com/make-trap-beats-6-step-formula):

**Tempo**: 70 BPM (140 halftime) typical

**Key Elements:**
- 808 bass carries melody AND rhythm
- Rapid triplet hi-hats (1/32 rolls)
- Sparse dark melodies (minor/phrygian)
- EDM-inspired builds and drops

**Structure**: Similar to hip hop but with:
- More dramatic breakdowns
- Filter sweeps before drops
- Layered builds with rising percussion

**Mixing Implications:**
- 808 is king - everything else makes room
- Hi-hats need space (panning, less compression)
- Kick and 808 relationship is critical (short kick for attack, 808 for sustain)

#### Drill Music (UK/Chicago)
From [Attack Magazine - UK Drill](https://www.attackmagazine.com/technique/beat-dissected/uk-drill/):

**Tempo**: 140 BPM (UK standard)

**Key Elements:**
- **Sliding 808s** (pitch glides between notes)
- Skippy, off-beat hi-hats
- Snare on beat 3 (not 2 and 4)
- Dark, eerie melodies (strings, piano, bells)
- Counter snares for variation

**Mixing Implications:**
- 808 glide needs clean low-end space
- Hi-hats can be more aggressive (distortion acceptable)
- Melodic elements are dark/minor - EQ can enhance eeriness

#### Lo-Fi Hip Hop / Chillhop
From [LANDR - What is Lo-Fi](https://blog.landr.com/lofi/):

**Tempo**: 60-95 BPM (very relaxed)

**Key Elements:**
- Jazz samples (piano, Rhodes, upright bass)
- "Imperfect" timing (off-grid, humanized)
- Lo-fi treatment (vinyl noise, bitcrushing, tape saturation)
- Boom-bap drum patterns with swing

**Mixing Implications:**
- Intentional degradation (remove high frequencies, add noise)
- Warmth over clarity
- Bass is rounded, not punchy
- Sidechain is subtle or absent

---

### R&B FAMILY

#### Contemporary R&B / Pop R&B
**Tempo**: Variable (70-130 BPM)

**Key Elements:**
- Whitney/Mariah influence: big vocals, polished production
- Electronic instrumentation + pop hooks
- Hip hop drum patterns common
- Often features rap verse

**Structure**: Traditional verse-chorus but with:
- Extended ad-libs/runs in chorus
- Breakdown sections for vocal spotlight

#### Neo-Soul
From [The Blues Project - Essential Guide to R&B](https://thebluesproject.co/2023/05/essential-guide-contemporary-rnb-soul-music/):

**Key Elements:**
- Live instrumentation emphasis
- Jazz chord extensions (maj7, min9, sus chords)
- Hip hop drum patterns but organic feel
- Erykah Badu, D'Angelo, J Dilla influence

**Mixing Implications:**
- More dynamic range than pop R&B
- Live instrument textures need space
- Bass is often upright or warm synth
- Less compression, more natural dynamics

#### Gospel-Influenced R&B
From [Fiveable - Contemporary R&B and Neo-Soul](https://fiveable.me/music-in-american-culture/unit-8/contemporary-randb-neo-soul/study-guide/NjLA65OsjECue6ss):

**Key Elements:**
- Call-and-response vocals (lead + backing)
- IV-I "amen" cadences
- Key lifts/modulations (especially at end)
- Organ pads, stacked thirds
- Melismatic vocals (runs, riffs)

**Mixing Implications:**
- Choir/backing vocals need careful layering
- Wide stereo field for group vocals
- Organ needs low-mid space
- Dynamic builds to climactic key change

---

### LATIN MUSIC

#### Reggaeton
From [MusicRadar - How to Make Reggaeton](https://www.musicradar.com/news/reggaeton-tips-bad-bunny):

**Tempo**: 85-110 BPM

**Key Element: Dembow Rhythm**
- 3+3+2 (tresillo) cross-rhythm
- TR-808/909 drum machine standard
- Kick on 1, snare pattern creates bounce

**Structure**: Hip hop-like (verse-hook) but with:
- Drops on bar 1 (strip everything, bring back on snare)
- Extended instrumental breaks for dancing

**Mixing Implications:**
- Bass needs to "bounce" with dembow
- Perreo (grinding dance) requires strong low-end
- Vocals often heavily processed (autotune common)

---

### AFRICAN DIASPORA

#### Afrobeats
From [Soundtrap - How to Make Afrobeats](https://blog.soundtrap.com/how-to-make-afrobeats/):

**Tempo**: 100-120 BPM

**Key Elements:**
- Layered percussion (shakers, congas, talking drums)
- Syncopated rhythms with unexpected accents
- Highlife/juju influence
- Call-and-response vocals

**Mixing Implications:**
- Percussion layers need careful frequency separation
- Less compression - let groove breathe
- Vocals are upfront but not overpowering

#### Amapiano
From [Roland - Production Hacks: Creating Amapiano](https://articles.roland.com/production-hacks-creating-amapiano-tracks/):

**Tempo**: 108-115 BPM

**Key Element: Log Drum**
- Functions like 808 but with unique timbre
- Carries both bass AND percussion role
- Deep, punchy, slightly pitched

**3-Step Rhythm:**
- Kick on 1 and 3, syncopated snare
- Jazzy piano chords (neo-soul influence)
- Space and simplicity over density

**Mixing Implications:**
- Log drum is the foundation - give it room
- Piano needs warmth, not brightness
- Let elements breathe - less is more

---

### K-POP / GENRE-SWITCHING

From [Kpopalypse - Song Structures in K-Pop](https://kpopalypse.com/2016/09/13/kpopalypse-explains-common-song-structures-in-k-pop/):

**Unique Characteristics:**
- **Multiple distinct sections** (not recycled progressions)
- **Genre switches** mid-song (verse = R&B, chorus = EDM)
- **Each member gets spotlight** (different sections for different vocalists)
- **Key/tempo changes** for fresh energy

**Structure**: Non-standard, examples:
- Verse (R&B) → Pre-chorus (trap) → Chorus (EDM drop) → Verse (hip hop) → ...
- Often 7+ distinct sections in one song

**Mixing Implications:**
- Each section may need different treatment
- Transitions are critical (smooth or dramatic?)
- Backing vocals are layered extensively
- Vocal processing varies by section

---

### ELECTRONIC MUSIC

#### EDM / House / Progressive
**Tempo**: 125-130 BPM (house), 128 BPM (progressive)

**Structure**:
```
Intro → Breakdown → Buildup → Drop → Breakdown → Buildup → Drop → Outro
  ↓        ↓          ↗        ↑        ↓          ↗        ↑↑      ↓
[LOW]   [LOW]     [RISING]  [HIGH]   [LOW]     [RISING]  [PEAK]  [LOW]
```

From [Cymatics - EDM Song Structure](https://cymatics.fm/blogs/production/edm-song-structure):
> "The structure Intro-Breakdown-Buildup-Drop-Breakdown-Buildup-Drop-Outro is quite frequent."

#### Phonk / Drift Phonk
From [LANDR - What is Phonk](https://blog.landr.com/what-is-phonk/):

**Tempo**: 105-200 BPM (drift phonk is faster)

**Key Elements:**
- TR-808 cowbell melodies (distorted, bit-crushed)
- Memphis rap vocal samples (chopped)
- Heavy distorted 808 bass
- Dark minor melodies (phrygian mode)

**Structure**: Simple, 8-bar sections
- Repetitive, loop-based
- Emphasis on vibe over complexity

**Mixing Implications:**
- Distortion is intentional (don't clean it up)
- Cowbell needs to cut through
- Lo-fi aesthetic embraced

---

### ROCK / METAL

From [Metal Mastermind - Song Structure](https://metalmastermind.com/understanding-song-structure-for-metal-songwriting/):

**Standard Structure**: ABABCB
- Verse (A) → Chorus (B) → Verse → Chorus → Bridge (C) → Chorus

**Metal-Specific Sections:**
- **Breakdown**: Heavy, slow section for headbanging
- **Guitar Solo**: Often after middle chorus
- **Outro**: May be extended, dramatic

**Mixing Implications:**
- Guitars need space (multiple layers, wide panning)
- Bass follows guitar riffs OR provides counter-melody
- Drums are massive (room mics, parallel compression)
- Vocal styles vary dramatically (clean vs screamed)

---

### FUNK

From [Splice - What is Funk](https://splice.com/blog/what-is-funk-music/):

**The "One"**: James Brown's innovation
- Emphasis on downbeat (beat 1), not backbeat
- Creates space for syncopation on other beats
- Every instrument treated as a drum

**Structure**: Vamp-based
- Extended grooves over 1-2 chord progressions
- Improvisation within tight ensemble structure
- Breakdowns and fills, not traditional sections

**Mixing Implications:**
- Groove is everything - don't squash dynamics
- Bass and drums lock together
- Rhythm guitar is percussive (muted, funky)
- Horns need punch without mud

---

### COUNTRY

From [Nashville Number System](https://nashvillenumbersystem.com/introduction/):

**Structure**: Traditional verse-chorus, often storytelling

**Nashville Number System:**
- Charts use numbers (1, 4, 5) instead of letter names
- Allows instant transposition
- Common patterns: 1-4-5-5, 1-4-1/6-5 (walk-down)

**Mixing Implications:**
- Acoustic instruments (guitar, fiddle, steel guitar)
- Vocals are front and center
- Clean production (minimal processing)
- Live room sound often desired

---

### GOSPEL / WORSHIP

From [Wikipedia - Contemporary Worship Music](https://en.wikipedia.org/wiki/Contemporary_worship_music):

**Structure**: Verse-Chorus-Bridge, emphasis on repetition

**Key Elements:**
- Extended chorus repeats (congregation singing)
- Key lifts for emotional climax
- Pre-chorus "climb" sections
- Bridge often builds to final chorus

**Mixing Implications:**
- Vocals must be intelligible (lyrics matter)
- Band supports, doesn't overpower
- Dynamic contrast is important (quiet verse → loud chorus)
- Live sound considerations (church acoustics)

---

### GENRE FUSION TRENDS (2024-2025)

From [Splice - Genre Trends 2025](https://splice.com/blog/splice-unveils-genre-trends/):

**Emerging Hybrids:**
- **Pluggnb**: Trap + 90s R&B (fastest growing on Splice)
- **K-R&B**: Korean neo-soul + Western influences
- **Latin Trap**: Trap + reggaeton elements
- **Punk Rap**: Rock guitars + hip hop flows
- **Jazz-Rap**: Return to boom-bap with jazz improvisation

**Implication for Model:**
Genre boundaries are increasingly blurry. The model needs to:
1. Identify primary genre
2. Recognize fusion elements
3. Apply appropriate conventions for each element

---

## Part 1.5: Structural Differences Across Genres (Comparative Analysis)

This section provides a **direct comparison** of how song structures differ across genres - not just what each genre does, but how they contrast with each other.

### Bar Length & Section Duration Comparison

| Genre | Typical Verse Length | Typical Chorus/Hook | Total Song Length |
|-------|---------------------|---------------------|-------------------|
| **Hip Hop** | 16 bars (12 modern) | 8 bars | 3:00-4:30 |
| **Pop** | 8 bars | 8 bars | 2:30-3:30 |
| **R&B** | 8-12 bars | 8 bars (with ad-libs extending to 12-16) | 3:30-4:30 |
| **EDM/House** | N/A (no traditional verse) | 16-32 bar drops | 4:00-6:00 |
| **Country** | 8 bars | 8-16 bars | 3:00-4:00 |
| **Rock** | 8-16 bars | 8 bars | 3:30-5:00 |
| **Metal** | Variable | Variable + breakdown | 4:00-7:00+ |
| **Funk** | Vamp-based (no fixed length) | Vamp-based | 4:00-7:00+ |
| **K-Pop** | 8 bars (changes genre mid-verse) | Multiple hooks, 8 bars each | 3:00-4:00 |
| **Gospel** | 8-16 bars | Extended vamps (16-32+ bars) | 4:00-8:00+ |

**Key Insight**: Hip hop verses are **twice as long** as pop verses (16 vs 8 bars), which affects how the model should approach vocal mixing and arrangement density recommendations.

---

### Structural Paradigm Deep Dive

#### 1. VERSE-HOOK (Hip Hop/R&B) vs VERSE-CHORUS (Pop/Rock)

| Aspect | Verse-Hook | Verse-Chorus |
|--------|------------|--------------|
| **Primary repetition** | Hook (shorter, catchier) | Chorus (longer, more melodic) |
| **Verse function** | Storytelling, bars, lyrical density | Setup, emotional build |
| **Verse length** | 16 bars (longer content time) | 8 bars (get to chorus faster) |
| **Hook/Chorus length** | 8 bars | 8-16 bars |
| **Groove consistency** | Same groove throughout | May change between sections |
| **Energy distribution** | Relatively flat | Verse (low) → Chorus (high) |

**Mixing Implication**: In verse-hook structures, the groove must carry the whole song, so drums/bass stay consistent. In verse-chorus, you can strip back verses and add elements in choruses.

#### 2. BUILD-DROP (EDM) vs VERSE-CHORUS (Pop)

| Aspect | Build-Drop (EDM) | Verse-Chorus (Pop) |
|--------|------------------|-------------------|
| **Climax mechanism** | Rhythmic/sonic (bass drops) | Melodic (hook/chorus) |
| **Tension source** | HP filter, risers, percussion builds | Harmonic tension, pre-chorus |
| **Release mechanism** | Beat 1 of drop (transient impact) | Chorus entry (melodic payoff) |
| **Energy curve** | Extreme peaks and valleys | Moderate contrast |
| **Vocal role** | Optional/minimal | Central |

**Critical Difference**: EDM uses **frequency removal** (HP filter) to build tension, then releases. Pop uses **element addition** (more instruments, higher melody).

#### 3. GROOVE-BASED (Funk/Afrobeats/Amapiano) vs LINEAR (Most Western Genres)

| Aspect | Groove-Based | Linear |
|--------|--------------|--------|
| **Section definition** | Subtle variation within same groove | Distinct sections |
| **Progression** | Circular (returns to same place) | Linear (verse → chorus → bridge) |
| **Climax concept** | "The pocket" is the destination | Build to chorus/drop |
| **Improvisation** | Encouraged within groove | Structured, arranged |
| **Mixing approach** | Lock the groove, subtle changes | Dynamic contrast between sections |

From funk research:
> "James Brown's innovation was the emphasis on 'the one' - the downbeat. The whole song could be a vamp over one chord, with every instrument treated as a drum. The groove IS the destination, not the journey to a chorus."

**Mixing Implication**: For groove-based music, compression and limiting should preserve the pocket. Over-compression kills funk. Let it breathe.

#### 4. SECTION-SWITCH (K-Pop) vs SINGLE-GENRE

| Aspect | K-Pop Section-Switch | Single-Genre |
|--------|---------------------|--------------|
| **Genre consistency** | Switches mid-song | One genre throughout |
| **Mixing continuity** | May need different treatment per section | Consistent approach |
| **Transitions** | Critical (smoothing genre changes) | Standard crossfades |
| **Section count** | 7+ distinct sections | 4-6 sections |
| **Production complexity** | Each section = different "song" | Unified sonic palette |

From K-pop research:
> "Dynamic structures, complex toplines, modal changes, blending multiple genres within the same song. A K-pop song might go: R&B verse → trap pre-chorus → EDM drop chorus → ballad bridge → hip hop rap verse."

**Mixing Implication**: K-pop mixing is essentially **mixing multiple songs** that need to feel cohesive. Transitions are where the magic happens.

---

### Genre-Specific Structural Elements

#### Hip Hop Specific

| Element | Description | Mixing Impact |
|---------|-------------|---------------|
| **The 808** | Not just bass - carries melody AND rhythm | Needs clean sub-bass space, often sidechained |
| **Ad-libs** | Background vocal interjections | Pan wide, reverb, lower volume |
| **Scratch hooks** | DJ scratching as hook (boom-bap) | Treat as lead instrument |
| **Tag/Producer drop** | Producer signature at start | Brief, then fade |
| **Beat switch** | Completely different beat mid-song | Treat as section change |

#### EDM Specific

| Element | Description | Mixing Impact |
|---------|-------------|---------------|
| **Riser** | Pitch-rising synth/noise | Automate gain AND filter |
| **Impact/downlifter** | Reverse cymbal, sub drop on beat 1 | Needs headroom before drop |
| **Drop** | Bass returns, energy peak | Clean transient on beat 1 |
| **Breakdown** | Stripped, emotional, often with vocal | Reverb/delay can increase |
| **Buildup** | 8-16 bars before drop | HP filter automation |

#### Gospel Specific

| Element | Description | Mixing Impact |
|---------|-------------|---------------|
| **Vamp** | Repeated section, escalating intensity | Build automation over time |
| **Key lift** | Modulation up (usually whole step) | May need EQ adjustment |
| **Call and response** | Lead + congregation/choir | Lead centered, choir wide |
| **Worship bridge** | Extended repetitive section | Dynamics are emotional |
| **The shout** | High energy climactic section | All elements at max |

From gospel research:
> "The vamp is 'ritual technology' - repetition and escalation as spiritual practice. A gospel song might vamp on the same 4 bars for 5 minutes, but the energy continuously builds. The form is 'terminally climactic' - always building toward transcendence."

#### Metal Specific

| Element | Description | Mixing Impact |
|---------|-------------|---------------|
| **Breakdown** | Slow, heavy, headbanging section | Needs maximum impact |
| **Blast beat** | Extremely fast drum pattern | High frequencies need control |
| **Guitar solo** | Extended instrumental section | Solo needs to cut through |
| **Chug/riff** | Palm-muted rhythmic guitar | Low-mid buildup common |
| **Double bass** | Rapid kick drum patterns | Low-end definition critical |

From metal research:
> "The breakdown is 'as much a building block as the thrash gallop.' It's not just a slow section - it's THE moment everyone in the pit waits for."

---

### Terminology Differences Across Genres

| Concept | Hip Hop Term | EDM Term | Pop Term | Rock Term |
|---------|-------------|----------|----------|-----------|
| **Main memorable part** | Hook | Drop | Chorus | Chorus |
| **Sparse section** | Verse | Breakdown | Verse | Verse |
| **Transition build** | -- | Buildup | Pre-chorus | Pre-chorus |
| **Energy peak** | Hook/808 drop | Drop | Chorus | Chorus/Guitar solo |
| **Contrast section** | Bridge | Breakdown | Bridge | Bridge/Solo |
| **Ending** | Outro/fade | Outro | Outro | Outro/breakdown |

**Dataset Implication**: The model needs to understand that "drop" ≠ "chorus" even though they're both high-energy sections. A drop is rhythmic/bass-focused; a chorus is melodic/vocal-focused.

---

### Energy Curve Comparison

```
HIP HOP (Verse-Hook):
▓▓▓▓░░░░▓▓▓▓░░░░░░░░▓▓▓▓░░░░░░░░▓▓▓▓░░░░
Intro  Verse    Hook    Verse    Hook    Outro
         (Relatively flat, groove carries)

POP (Verse-Chorus):
░░░░▓▓▓▓████░░░░▓▓▓▓████████░░░░████████
Intro V  Pre  C   V  Pre  Chorus  Br   Chorus
      (Dynamic contrast, builds to chorus)

EDM (Build-Drop):
░░░░░░░░▒▒▒▒████░░░░░░░░▒▒▒▒████████░░░░
Intro  BD  Build Drop  BD   Build  DROP  Outro
       (Extreme contrast, tension-release)

FUNK (Groove-Based):
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 (One groove throughout, subtle variation)

GOSPEL (Terminally Climactic):
░░░░▒▒▒▒▓▓▓▓████████████████████████████
 Verse  Build    VAMP ESCALATING TO CLIMAX
      (Continuous build, ends at maximum)

K-POP (Section-Switch):
░░▓▓░░░░████▒▒▒▒░░░░████▓▓▓▓████████░░░░
R&B  Trap  EDM  Rap   EDM  Ballad  EDM
     (Different genre = different energy)
```

---

### Implications for Dataset Design

Based on these structural differences, our dataset needs:

1. **Genre-specific section labels**
   - Not just "verse/chorus" but "hook" for hip hop, "drop" for EDM, "vamp" for gospel/funk

2. **Bar count annotations**
   - 16-bar verse (hip hop) needs different treatment than 8-bar verse (pop)

3. **Energy curve type**
   - Flat (funk), dynamic (pop), extreme (EDM), climactic (gospel)

4. **Section relationship markers**
   - "This drop follows an 8-bar buildup" vs "this chorus follows a pre-chorus"

5. **Terminology translation**
   - Model should understand "hook" and "chorus" are different concepts
   - "Drop" ≠ "chorus" even if both are high-energy

6. **Groove continuity flags**
   - Does the groove stay constant (funk) or change (pop)?
   - Mixing advice depends on this

---

## Part 2: Arrangement-Specific Mixing Decisions

### Why Arrangement Context Matters for Mixing

From [iZotope - Arranging Music for Better Mixdowns](https://www.izotope.com/en/learn/arranging-music-for-better-mixdown.html):
> "Great mixing is often born from great arrangements. Carefully planning an arrangement and making considered decisions regarding energy level, instrument selection, and frequency information will lead to better mixes."

From [Mastering.com - Arrangement is Mixing](https://mastering.com/arrangement-is-mixing-build-space-into-your-songs/):
> "Instead of going to EQ or compression to adjust levels, ask yourself if you can remove parts clogging up your mix."

### Section-Specific Production Decisions

#### Intro/Outro
- **Headroom**: 10-12 dB (more than drop/chorus)
- **Elements**: Sparse, establish key elements
- **Frequency**: Often high-passed or filtered
- **Purpose**: DJ mixing points (EDM), setting tone (Pop)

#### Verse/Breakdown
- **Headroom**: ~8-10 dB
- **Elements**: Stripped back, focus on vocal/lead melody
- **Frequency**: Less bass-heavy, more mid-focused
- **Width**: Narrower stereo field to contrast chorus

#### Build-up
Common techniques from [Myloops - 7 Ways to Create Better Buildups](https://www.myloops.net/7-ways-to-create-better-buildups-in-edm-tracks):
- Rising pitch synths/risers
- Rushing percussion (snares increase in frequency)
- High-pass filter sweep (automate cutoff from 80Hz → full)
- Low-pass filter on other elements (create "underwater" effect)
- Increasing reverb/delay
- Noise sweeps (white noise crescendo)

#### Chorus/Drop
- **Headroom**: ~6 dB (loudest section)
- **Elements**: Full arrangement, all key elements present
- **Frequency**: Full spectrum, big bass
- **Width**: Widest stereo field
- **Impact**: Clean first beat, strong transients

From [Mastering the Mix - Bigger Chorus](https://www.masteringthemix.com/blogs/learn/how-to-give-your-chorus-a-bigger-impact):
> "To give a chorus bigger impact, focus on dynamic contrast, cleaning up the first beat, simplifying the arrangement (to avoid muddiness), and widening the stereo field."

### Filter Sweep Automation Patterns

From [Unison Audio - Filter Sweeps 101](https://unison.audio/filter-sweeps/):

| Technique | Parameters | Duration | Use Case |
|-----------|------------|----------|----------|
| **LP Sweep Down** | 20kHz → 500Hz | 8-16 bars | Breakdown entrance |
| **HP Sweep Up** | 20Hz → 2kHz | 8-16 bars | Buildup to drop |
| **BP Sweep** | Moving center freq | 4-8 bars | Tension, movement |
| **Resonance Ride** | Q automation | Variable | Interest, wobble |

Typical buildup automation from [Flypaper - Filter Sweeps](https://flypaper.soundfly.com/produce/what-is-a-filter-sweep-and-how-can-i-use-it/):
```
High-pass filter on master:
- Start: 80 Hz
- End: 2000 Hz
- Duration: 8-16 bars
- Shape: Exponential curve
```

---

## Part 3: Existing Datasets for Structure Analysis

### Audio-Based Datasets

| Dataset | Size | Annotations | Limitation |
|---------|------|-------------|------------|
| **[SALAMI](https://paperswithcode.com/dataset/salami)** | 1,359 tracks | Hierarchical (fine/coarse/functional) | No mixing data |
| **[RWC-Pop](https://www.music-ir.org/mirex/wiki/2025:Music_Structure_Analysis)** | 100 tracks | Structure labels | Small, Japanese pop bias |
| **McGill Billboard** | 740 songs | Chord + structure | Pop only, no production data |

From [SALAMI Dataset](https://paperswithcode.com/dataset/salami):
> "The publicly available portion of SALAMI contains hierarchical annotations for 1,359 tracks, 884 of which have annotations from two distinct annotators."

SALAMI annotation levels:
1. **Fine level**: Short motives/phrases (lowercase letters: a, b, c)
2. **Coarse level**: Larger sections (uppercase letters: A, B, C)
3. **Functional level**: Semantic labels (verse, chorus, bridge)

### MIDI-Based Datasets

| Dataset | Size | Content | Limitation |
|---------|------|---------|------------|
| **[Lakh MIDI](https://colinraffel.com/projects/lmd/)** | 176,581 files | Multi-track MIDI | No arrangement labels |
| **[Slakh2100](https://www.slakh.com/)** | 2,100 tracks | MIDI + synthesized audio | No structure annotations |
| **[POP909](https://program.ismir2020.net/static/final_papers/89.pdf)** | 909 songs | MIDI + arrangement versions | Pop only, Chinese songs |
| **[GigaMIDI](https://arxiv.org/html/2502.17726v1)** | Large | Loop detection, track analysis | No functional labels |

From [GigaMIDI paper](https://arxiv.org/html/2502.17726v1):
> "File-level analysis examines global attributes such as duration, tempo, and metadata, aiding structural studies, while track-level analysis explores instrumentation and arrangement details."

### MIREX 2025 Structure Analysis Task

From [MIREX 2025 Wiki](https://www.music-ir.org/mirex/wiki/2025:Music_Structure_Analysis):
> "For MIREX 2025, participants are required to segment musical audio and classify each segment into one of seven functional categories: 'intro', 'verse', 'chorus', 'bridge', 'inst' (instrumental), 'outro', or 'other'."

**Key insight**: The field is moving from arbitrary labels (A, B, C) to **functional labels** (verse, chorus, drop).

---

## Part 4: What's Missing (Our Opportunity)

### Gap Analysis

| What Exists | What's Missing |
|-------------|----------------|
| Structure segmentation | **Section-specific mixing decisions** |
| Functional labels (verse, chorus) | **Why mixing changes between sections** |
| Beat/tempo tracking | **Automation patterns tied to structure** |
| Chord progressions | **EQ/compression settings per section** |
| Instrument identification | **How instruments should change by section** |

### The Core Problem

No dataset connects:
1. **Structure labels** → "This is a buildup"
2. **Audio characteristics** → "Energy is rising, high-pass filter increasing"
3. **Mixing decisions** → "Use these EQ settings for this section"
4. **Causal reasoning** → "Because it's a buildup, we high-pass to create tension"

---

## Part 5: Our Dataset Strategy

### ArrangementMixQA: Section-Aware Production Dataset

#### Data Requirements

For each song/project, we need:

```json
{
  "song_id": "song_001",
  "metadata": {
    "genre": "progressive_house",
    "tempo": 128,
    "key": "F minor"
  },
  "sections": [
    {
      "section_id": "sec_001",
      "type": "intro",
      "start_bar": 1,
      "end_bar": 16,
      "energy_level": 0.2,
      "audio_clip": "audio/song_001_sec_001.wav",
      "midi_data": "midi/song_001_sec_001.mid",
      "active_tracks": ["kick_light", "pad", "arp"],
      "mixing_state": {
        "master_hp_cutoff": 150,
        "master_headroom_db": -12,
        "reverb_send_level": 0.6
      }
    },
    {
      "section_id": "sec_002",
      "type": "buildup",
      "start_bar": 17,
      "end_bar": 24,
      "energy_level": "0.2 → 0.8",
      "audio_clip": "audio/song_001_sec_002.wav",
      "automation": {
        "master_hp_cutoff": {"start": 150, "end": 2000, "curve": "exponential"},
        "snare_frequency": {"start": "1/2 notes", "end": "1/16 notes"},
        "riser_gain": {"start": -inf, "end": 0}
      }
    },
    {
      "section_id": "sec_003",
      "type": "drop",
      "start_bar": 25,
      "end_bar": 56,
      "energy_level": 1.0,
      "audio_clip": "audio/song_001_sec_003.wav",
      "active_tracks": ["kick_full", "bass", "lead", "pad", "drums_full"],
      "mixing_state": {
        "master_hp_cutoff": 20,
        "master_headroom_db": -6,
        "bass_sidechain_ratio": "4:1"
      }
    }
  ],
  "qa_pairs": [
    {
      "context_section": "sec_003",
      "question_type": "ARRANGEMENT_AWARE",
      "question": "Why is the high-pass filter disabled in the drop?",
      "answer": "The drop is the highest energy section where we want full bass impact. The HP filter was at 2kHz during the buildup to create tension - releasing it on the first beat of the drop creates a powerful 'bass drop' sensation.",
      "reasoning_trace": "<think>Section type is 'drop' with energy_level 1.0. Prior section was 'buildup' with HP automation 150→2000Hz. The contrast between filtered buildup and unfiltered drop creates impact.</think>"
    },
    {
      "context_section": "sec_001",
      "question_type": "RECOMMENDATION",
      "question": "The intro feels too busy. How can I simplify it?",
      "answer": "Intro sections typically have 3-4 elements maximum. You have kick_light, pad, and arp - that's good. Consider removing the arp or sidechaining it heavily so it 'breathes' with the kick. Keep headroom high (-12dB) for contrast with the drop.",
      "tool_calls": [{"tool": "set_track_mute", "params": {"track": "arp", "mute": true}}]
    }
  ]
}
```

### Data Collection Approaches

#### Approach 1: Ableton Project Analysis
- Parse .als files to extract:
  - Arrangement markers (locators)
  - Clip positions and lengths
  - Automation data
  - Plugin states per section
- **Advantage**: Real-world mixing decisions
- **Challenge**: Need user consent, parsing complexity

#### Approach 2: Synthetic Section Generation
- Use our Serum stems + programmatic arrangement
- Generate sections with known structure:
  - Sparse intro (2-3 elements)
  - Full drop (5-6 elements)
  - Filtered buildup (HP automation)
- **Advantage**: Full control, ground truth
- **Challenge**: May not capture real-world complexity

#### Approach 3: SALAMI + Audio Feature Extraction
- Use SALAMI's section labels
- Extract audio features per section:
  - Spectral centroid (brightness)
  - RMS energy
  - Frequency band distribution
- Infer mixing characteristics from audio
- **Advantage**: Existing labeled data
- **Challenge**: No ground-truth mixing parameters

#### Approach 4: Reference Track Analysis
- Analyze commercial releases with known structure
- Extract:
  - Energy curves
  - Spectral changes between sections
  - Stereo width changes
- Generate Q&A about "why this section sounds this way"
- **Advantage**: Professional production quality
- **Challenge**: Copyright concerns for training

### Recommended Hybrid Strategy

1. **Use SALAMI for structure labels** (1,359 tracks)
2. **Extract audio features per section** (brightness, energy, width)
3. **Generate synthetic mixing data** from our Serum renders
4. **LLM-generate Q&A** linking structure to mixing decisions
5. **Validate with computed metrics** (does the drop actually have more bass?)

---

## Part 6: Detection Methods

### Audio-Based Structure Detection

From [ISMIR 2025 - Semantic Song Segmentation](https://ismir2025program.ismir.net/poster_79.html):
> "The model is a convolutional neural network trained to jointly predict frame-wise boundary activation functions and segment label probabilities. Input features consist of a log-magnitude log-frequency spectrogram and self-similarity lag matrices."

**Existing tools:**
- `msaf` (Music Structure Analysis Framework) - Python library
- `librosa` beat/segment detection
- CNN-based MIREX submissions

### MIDI-Based Structure Detection

From MIDI, we can detect:
- **Note density changes** → Section boundaries
- **Instrument entry/exit** → Arrangement changes
- **Velocity patterns** → Energy levels
- **Pitch range** → Build-up detection (rising sequences)

### Hybrid Detection (Our Approach)

```
┌─────────────────────────────────────────────────────────────┐
│                    ARRANGEMENT DETECTOR                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AUDIO FEATURES           MIDI FEATURES                     │
│  ─────────────            ─────────────                     │
│  • Spectrogram            • Note density                    │
│  • Self-similarity        • Instrument count                │
│  • RMS energy             • Velocity curves                 │
│  • Spectral centroid      • Pitch range                     │
│                                                             │
│           ↓                      ↓                          │
│           └──────────┬───────────┘                          │
│                      ↓                                      │
│           SECTION BOUNDARY DETECTION                        │
│                      ↓                                      │
│           FUNCTIONAL LABEL CLASSIFICATION                   │
│           (intro, verse, buildup, drop, etc.)              │
│                      ↓                                      │
│           PER-SECTION MIXING ANALYSIS                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 7: Implementation Plan

### Phase 1: Structure Detection Pipeline
1. Integrate `msaf` or similar for automatic segmentation
2. Extract audio features per detected section
3. Build section classifier (7 MIREX categories)
4. Validate against SALAMI ground truth

### Phase 2: Mixing Feature Extraction
1. For each section, compute:
   - Frequency band energy distribution
   - Stereo width (correlation)
   - Dynamic range
   - Estimated EQ curve (via spectral analysis)
2. Compare across sections to find patterns

### Phase 3: Q&A Generation
1. Template-based questions about arrangement:
   - "Why does this section have less bass?"
   - "What makes this sound like a buildup?"
   - "How should I transition from verse to chorus?"
2. LLM-assisted answer generation with grounding

### Phase 4: Integration with MixRelationalQA
1. Add `section_context` field to all Q&A pairs
2. Include arrangement-aware questions in dataset
3. Train model to consider arrangement in responses

---

## Key Research Sources

### Multi-Genre Arrangement Theory

**Hip Hop Family:**
- [Hip Hop Makers - Song Arrangements](https://hiphopmakers.com/how-to-make-beats-song-arrangements)
- [Native Instruments - What is Boom Bap](https://blog.native-instruments.com/what-is-boom-bap/)
- [Waves - How to Make Trap Beats](https://www.waves.com/make-trap-beats-6-step-formula)
- [Attack Magazine - UK Drill](https://www.attackmagazine.com/technique/beat-dissected/uk-drill/)
- [LANDR - What is Lo-Fi](https://blog.landr.com/lofi/)
- [LANDR - What is Phonk](https://blog.landr.com/what-is-phonk/)
- [eMastered - Rap Song Structure](https://emastered.com/blog/rap-song-structure)

**R&B / Soul:**
- [The Blues Project - Essential Guide to Contemporary R&B](https://thebluesproject.co/2023/05/essential-guide-contemporary-rnb-soul-music/)
- [Fiveable - Contemporary R&B and Neo-Soul](https://fiveable.me/music-in-american-culture/unit-8/contemporary-randb-neo-soul/study-guide/NjLA65OsjECue6ss)
- [Hit Songs Deconstructed - R&B/Soul Characteristics](https://www.hitsongsdeconstructed.com/hsd_wire/rbsoul-hit-songwriting-characteristics/)

**Latin / Reggaeton:**
- [MusicRadar - How to Make Reggaeton](https://www.musicradar.com/news/reggaeton-tips-bad-bunny)
- [Wikipedia - Dembow Beat](https://en.wikipedia.org/wiki/Dembow)
- [Luz Media - Urban Music Subgenres Explained](https://luzmedia.co/urban-music-subgenres-explained/)

**African Diaspora:**
- [Soundtrap - How to Make Afrobeats](https://blog.soundtrap.com/how-to-make-afrobeats/)
- [Roland - Creating Amapiano](https://articles.roland.com/production-hacks-creating-amapiano-tracks/)
- [Afroplug - Amapiano vs Afrobeats](https://afroplug.com/amapiano-vs-afrobeats-understanding-the-difference/)

**K-Pop / East Asian:**
- [Kpopalypse - Song Structures in K-Pop](https://kpopalypse.com/2016/09/13/kpopalypse-explains-common-song-structures-in-k-pop/)
- [Soundtrap - K-Pop Music Guide](https://blog.soundtrap.com/k-pop-music/)
- [Pibox - Production Tips from K-Pop](https://pibox.com/resources/music-production-tips-to-learn-from-k-pop/)

**Rock / Metal:**
- [Metal Mastermind - Song Structure](https://metalmastermind.com/understanding-song-structure-for-metal-songwriting/)
- [Develop Device - Modern Metal Guide](https://developdevice.com/blogs/news/the-art-of-crafting-a-modern-metal-song-a-comprehensive-guide)

**Funk / Groove:**
- [Splice - What is Funk](https://splice.com/blog/what-is-funk-music/)
- [Disc Makers - James Brown and Funk](https://blog.discmakers.com/2018/10/james-brown-and-the-invention-of-funk-music/)

**Country:**
- [Nashville Number System](https://nashvillenumbersystem.com/introduction/)
- [Sweetwater - Nashville Number System Demystified](https://www.sweetwater.com/insync/the-nashville-number-system-demystified/)

**Gospel / Worship:**
- [Wikipedia - Contemporary Worship Music](https://en.wikipedia.org/wiki/Contemporary_worship_music)
- [Worship Leader Magazine - Song Structure](https://worshipleader.com/worship-culture/music/songwriting-culture/the-structure-of-a-song/)

**EDM / Electronic:**
- [Cymatics - EDM Song Structure](https://cymatics.fm/blogs/production/edm-song-structure)
- [Hyperbits - Essential Guide to EDM Song Structure](https://hyperbits.com/edm-song-structure/)

### Genre Fusion & Trends
- [Splice - Genre Trends 2025](https://splice.com/blog/splice-unveils-genre-trends/)
- [The FADER - 2024's Top Genres in 2025](https://www.thefader.com/2025/02/04/how-will-2024s-top-genres-make-noise-in-2025)
- [Mastering the Mix - Hip Hop/R&B Production Trends 2024](https://www.masteringthemix.com/blogs/learn/rends-in-hip-hop-r-b-music-production-in-2024)

### Section-Specific Mixing
- [iZotope - Arranging Music for Better Mixdown](https://www.izotope.com/en/learn/arranging-music-for-better-mixdown.html)
- [Mastering.com - Arrangement is Mixing](https://mastering.com/arrangement-is-mixing-build-space-into-your-songs/)
- [Mastering the Mix - Bigger Chorus](https://www.masteringthemix.com/blogs/learn/how-to-give-your-chorus-a-bigger-impact)
- [Unison Audio - Filter Sweeps 101](https://unison.audio/filter-sweeps/)
- [Myloops - 7 Ways to Create Better Buildups](https://www.myloops.net/7-ways-to-create-better-buildups-in-edm-tracks)

### Datasets & Analysis
- [SALAMI Dataset](https://paperswithcode.com/dataset/salami)
- [MIREX 2025 Music Structure Analysis](https://www.music-ir.org/mirex/wiki/2025:Music_Structure_Analysis)
- [Lakh MIDI Dataset](https://colinraffel.com/projects/lmd/)
- [GigaMIDI Dataset](https://arxiv.org/html/2502.17726v1)
- [POP909 Dataset](https://program.ismir2020.net/static/final_papers/89.pdf)
- [Slakh Dataset](https://www.slakh.com/)

### Technical Approaches
- [ISMIR 2025 - Semantic Song Segmentation](https://ismir2025program.ismir.net/poster_79.html)
- [TISMIR - Audio-Based Music Structure Analysis](https://transactions.ismir.net/articles/10.5334/tismir.54)

### Structural Comparison Research
- [eMastered - Rap Song Structure](https://emastered.com/blog/rap-song-structure) - Hip hop bar lengths and verse structure
- [Music Theory Academy - Verse Length](https://www.musictheoryacademy.com/how-to-write-songs/verse-length/) - Pop vs hip hop verse comparison
- [SongTown - Songwriting Tips](https://www.songtown.com/learning-center/) - Nashville approach to section lengths
- [Music Production Nerds - Gospel Structure](https://musicproductionnerds.com) - Vamp mechanics and "terminally climactic" form
- [EDMProd - Drop vs Chorus](https://www.edmprod.com/drop-vs-chorus/) - Structural difference analysis

---

## Conclusion

Arrangement awareness is not optional - it's **fundamental** to giving contextually appropriate mixing advice. But arrangement conventions are **genre-specific**:

| What Works | Genre Context |
|------------|---------------|
| Heavy 808 sidechain | Trap, but NOT boom-bap |
| Vinyl crackle | Lo-fi hip hop, but NOT contemporary R&B |
| Key modulation | Gospel/K-pop, but RARE in EDM |
| Extended vamps | Funk/Amapiano, but NOT rock |
| HP filter builds | EDM/Trap, but NOT boom-bap |

### What Our Dataset Must Teach

1. **Genre identification** - What genre/subgenre is this?
2. **Structure identification** - What section is this (verse, hook, drop, etc.)?
3. **Genre-specific conventions** - What's expected in this genre+section?
4. **Causal reasoning** - Why do these decisions fit this context?
5. **Fusion handling** - When genres blend, which conventions apply?

### Open Questions for Dataset Design

1. **Genre taxonomy**: How granular? (Hip hop → Trap → Drill → UK Drill?)
2. **Fusion handling**: Pluggnb is trap + 90s R&B - which rules apply when?
3. **Regional variations**: UK drill vs Chicago drill have different 808 patterns
4. **Temporal context**: Same genre evolved over time (90s hip hop ≠ 2020s hip hop)

### Dataset Requirements (Updated)

The model needs training data that includes:
- `genre` and `subgenre` labels
- `era` markers (90s, 2000s, 2010s, 2020s)
- `regional_style` where applicable
- `fusion_elements` for hybrid tracks
- Section labels + genre-specific mixing conventions

The good news: We can bootstrap this with existing structure datasets (SALAMI) + audio feature extraction + LLM-generated Q&A. The challenge is grounding the Q&A in **genre-specific** conventions, not universal rules.
