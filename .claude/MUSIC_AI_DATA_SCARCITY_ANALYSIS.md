# Why Music AI Training Data Is Scarce: Root Cause Analysis

**Date**: 2025-11-30
**Purpose**: Understanding the systemic barriers to music AI dataset creation to inform our data collection strategy

---

## Executive Summary

The quote from M²UGen that prompted this investigation:
> "In the realm of LLM-assisted music understanding and generation, there is a **notable scarcity of readily available training data**."

This document analyzes the five root causes of this scarcity and identifies opportunities for our project.

---

## Root Cause 1: Copyright & Legal Minefield

### The Current Landscape (2025)

| Event | Date | Impact |
|-------|------|--------|
| Major labels sue Suno/Udio | 2024 | Chilling effect on AI music startups |
| Sony "AI Training Opt-Out" declaration | May 2024 | Explicit prohibition on training |
| GEMA sues OpenAI | Nov 2024 | European enforcement begins |
| GEMA sues Suno AI | Jan 2025 | Direct music AI targeting |
| US Copyright Office report | May 2025 | Training on copyrighted works = "prima facie infringement" |
| Merlin policy update | Dec 2024 | Requires "specific and express license, in advance" |

### Key Legal Findings

From the [US Copyright Office Report (May 2025)](https://www.skadden.com/insights/publications/2025/05/copyright-office-report):
> "Using copyrighted works to train AI models may constitute prima facie infringement of the right to reproduce such works. Where AI generated outputs are substantially similar to the training data inputs, there is a 'strong argument' that the models' weights themselves infringe."

From [Billboard's licensing analysis](https://www.billboard.com/pro/what-would-ai-music-license-look-like-complicated/):
> "A vocal line or beat can be pulled from a hit single, embedded in training, and then recombined into outputs with no traceable origin. That makes the traditional idea of licensing individual recordings or stems entirely obsolete."

### The Licensing Market

- **$2.5 billion** licensing market for AI training data now exists
- Major deals: OpenAI/Reddit, OpenAI/Wall Street Journal
- Music industry demanding **ongoing revenue share**, not one-time payments
- GEMA (Sept 2024): "A one-off lump sum payment for training data is not nearly sufficient"

### Investment Impact

From [Water & Music](https://www.waterandmusic.com/three-music-ai-trends-to-watch-in-2025-recording-takeaways/):
> "While early 2024 saw major funding rounds for companies like Udio ($10M), ElevenLabs ($80M), and Suno ($125M), investment has cooled significantly following high-profile lawsuits."

---

## Root Cause 2: Multitrack Stems Are Rare & Expensive

### Why Stems Don't Exist

| Barrier | Explanation |
|---------|-------------|
| **Trade secrets** | Session files reveal production techniques |
| **Remix rights** | Stems enable unauthorized derivatives |
| **Licensing complexity** | Each stem may have different rights holders |
| **Storage/delivery** | Stems are 10-50x larger than mixed audio |
| **No commercial incentive** | Labels don't profit from releasing stems |

### Available Multitrack Datasets

| Dataset | Size | Type | Limitation |
|---------|------|------|------------|
| [MUSDB18](https://sigsep.github.io/datasets/musdb.html) | 150 songs (~10 hrs) | Pop/Rock stems | Royalty-free only, small |
| [MedleyDB](https://medleydb.weebly.com/) | 196 tracks | Mixed genres | Academic collection, years to build |
| [Slakh2100](https://www.slakh.com/) | 2,100 tracks (145 hrs) | MIDI→VST synthesis | Synthetic, not real recordings |
| [The Spheres (2025)](https://arxiv.org/html/2511.21247) | ~1 hour | Orchestral | Very niche, classical only |
| [Piano Concerto Dataset](https://transactions.ismir.net/articles/10.5334/tismir.160) | 81 excerpts | Piano + Orchestra | Classical only |

From [The Spheres Dataset paper](https://arxiv.org/html/2511.21247):
> "Acquiring such data poses a major challenge due to copyright restrictions, and access to full multi-track recordings remains limited, as they are seldom released by artists."

### The "Holy Grail" Problem

From [Tracklib](https://www.tracklib.com/music/collections/651):
> "In the realm of music sampling, multitracks are the holy grail to have access to."

Getting separated stems requires:
1. **Original recording sessions** - Expensive, requires studio access
2. **Artist cooperation** - Rare, protective of IP
3. **AI separation** - Creates artifacts, legally questionable for training

---

## Root Cause 3: Annotation Is Expensive & Time-Consuming

### The MusicCaps Example

[MusicCaps](https://huggingface.co/datasets/google/MusicCaps) is the largest human-annotated music caption dataset:
- **5,521 clips** (compare to millions in vision/text)
- Each caption written by **professional musicians**
- Only 10-second clips, not full songs
- No stems, no production metadata

From [LP-MusicCaps research](https://arxiv.org/abs/2307.16372):
> "Researchers face challenges due to the costly and time-consuming collection process of existing music-language datasets, which are limited in size."

### Annotation Challenges Unique to Music

| Challenge | Why It's Hard |
|-----------|--------------|
| **Expert knowledge required** | Need musicians, not crowd workers |
| **Temporal complexity** | Must listen to entire piece, not glance |
| **Subjectivity** | "Good mix" varies by genre, taste, context |
| **Multi-dimensional** | Melody, harmony, rhythm, timbre, production all matter |
| **Cultural bias** | Western music theory dominates annotations |

### Synthetic Annotation Attempts

To address scarcity, researchers have tried LLM-generated captions:

| Dataset | Size | Method | Limitation |
|---------|------|--------|------------|
| LP-MusicCaps | 2.2M captions / 0.5M clips | LLM from tags | No human verification |
| [JamendoMaxCaps (2025)](https://arxiv.org/html/2502.07461v1) | 200K+ tracks | AI captioning | Instrumental only, Jamendo bias |

---

## Root Cause 4: Music Is Uniquely Complex

### Comparison to Other Modalities

| Aspect | Images | Text | Music |
|--------|--------|------|-------|
| **Temporal** | Static | Sequential | Sequential + layered |
| **Annotation** | Quick glance | Read once | Must listen in real-time |
| **Subjectivity** | Some | Some | High |
| **Expert required** | Sometimes | Rarely | Often |
| **Cultural context** | Moderate | High | Very high |

### Multi-Track Adds Another Dimension

Understanding a single track is hard enough. Multi-track reasoning requires:
- **Frequency analysis** - Which instruments overlap?
- **Temporal alignment** - How do rhythms interact?
- **Stereo field** - Where is everything placed?
- **Dynamic range** - How do levels compete?
- **Effect chains** - How do processors interact?

From [Can LLMs "Reason" in Music?](https://arxiv.org/html/2407.21531v1):
> "Current LLMs exhibit poor performance in song-level multi-step music reasoning, and typically fail to leverage learned music knowledge when addressing complex musical tasks."

---

## Root Cause 5: Commercial Incentives Are Misaligned

### Why Key Actors Don't Share Data

| Actor | What They Have | Why They Don't Share |
|-------|---------------|---------------------|
| **Major Labels** | Millions of masters + stems | Core revenue asset |
| **Recording Studios** | Session files, techniques | Trade secrets |
| **Producers** | Presets, effect chains | Competitive advantage |
| **DAW Companies** | User projects (with consent) | Privacy, no business model |
| **Plugin Makers** | Preset libraries | Product differentiation |
| **Streaming Services** | Usage data + audio | Licensing agreements prohibit |

### The Synthetic Data Push

From [Music Ally](https://musically.com/2025/05/08/licensing-ai-music-the-industry-is-focusing-on-the-wrong-problem/):
> "Due to a mix of rising licensing costs and a desire for more granular control and flexibility over the model training process, AI developers are increasingly exploring synthetic alternatives to acquiring data, including stem mixing and shuffling."

---

## Beyond Data Scarcity: Additional Limitations

While data scarcity is the most commonly cited issue, our research uncovered **five additional systemic limitations** that even abundant data wouldn't fully solve.

### Limitation 1: Audio Representation Problem (Discrete vs Continuous)

**The Core Issue**: Audio is continuous, but LLMs work with discrete tokens.

From [Music AI Trends 2025](https://www.nature.com/articles/s41467-024-53807-7):
> "Discrete Representation Inconsistency (DRI)" — the mismatch between continuous audio signals and discrete token vocabularies used by language models.

| Approach | Problem |
|----------|---------|
| **Discrete tokens** (Encodec, SoundStream) | Lose fine-grained audio detail |
| **Continuous latents** | Don't integrate with LLM text reasoning |
| **Hybrid** | Computational complexity, alignment challenges |

**Relevance to Our Project**: MEDIUM - CLAP handles this by producing continuous embeddings we project into LLM space, but the projection layer must learn the mapping.

### Limitation 2: Long-Term Structure & Coherence

**The Core Issue**: Music has hierarchical structure (motifs → phrases → sections → songs) that's hard to model.

From [Music Transformer research](https://arxiv.org/abs/1809.04281):
> "Generating coherent music with long-range structure remains challenging because attention mechanisms struggle with very long sequences."

Solutions in 2025:
- **Relative attention** (Music Transformer) - helps with local patterns
- **Hierarchical models** - generate structure first, then fill in
- **Memory-augmented transformers** - track themes across sections

**Relevance to Our Project**: UNKNOWN (Potentially HIGH)

While we're not *generating* long-form music, coherent *analysis and advice* may require understanding longer context:

| Scenario | Why Coherence Matters |
|----------|----------------------|
| **Section-aware mixing** | "Cut 200Hz on bass" might be right for the verse but wrong for the breakdown |
| **Track relationships change** | Bass and kick coexist fine in intro, clash in drop |
| **Iterative workflows** | Real mixing = fix this → check that section → adjust |
| **Genre conventions** | Build-ups, drops, bridges have different mixing needs |

**Open Questions:**
- What's the minimum context window for coherent mixing advice?
- Can we chunk a song into sections and reason about each, or do we need full-song context?
- How do we handle advice that's correct for one section but harmful to another?

**Mitigation Strategies to Explore:**
1. Section-level embeddings (intro/verse/chorus/drop tagging)
2. Hierarchical CLAP (clip-level → section-level → song-level)
3. Explicit temporal markers in Q&A ("In the drop, the bass and kick...")
4. Memory-augmented approach where model can "look back" at earlier sections

### Limitation 3: Evaluation Metrics Are Broken

**The Core Issue**: There's no reliable automated way to measure if music AI output is "good."

| Metric | What It Measures | Problem |
|--------|-----------------|---------|
| **FAD** (Fréchet Audio Distance) | Statistical similarity to training data | Doesn't correlate with human preference |
| **CLAP score** | Audio-text alignment | Biased toward training distribution |
| **MOS** (Mean Opinion Score) | Human ratings | Expensive, not scalable |
| **Music Information Retrieval metrics** | Pitch/rhythm accuracy | Miss perceptual quality |

From [MusicLM evaluation](https://arxiv.org/abs/2301.11325):
> "FAD scores showed weak correlation (r=0.23) with human preference ratings, suggesting automated metrics may not capture what listeners actually value."

**Relevance to Our Project**: HIGH - How do we validate that our model's mixing advice is actually good? We need:
1. Computed audio metrics (frequency overlap, dynamic range)
2. A/B testing with real producers
3. Consistency checks (does advice match genre conventions?)

### Limitation 4: Semantic Grounding Gap

**The Core Issue**: LLMs understand words but don't truly "hear" audio. They lack grounded understanding of what sounds actually sound like.

From [AudSemThinker (2025)](https://arxiv.org/abs/2505.04264):
> "Current audio LLMs lack structured reasoning over audio content. They can describe what they 'see' in embeddings but struggle to reason about causal relationships."

The AudSemThinker framework proposes structured reasoning:
- **WHO** - Sound source identification
- **WHAT** - Acoustic event classification
- **HOW** - Sound quality analysis
- **WHEN** - Temporal ordering
- **WHERE** - Spatial positioning

**Relevance to Our Project**: HIGH - This is exactly why we need MixRelationalQA. Our dataset must teach:
- What "muddy bass" sounds like (spectral characteristics)
- Why certain EQ moves fix masking (causal reasoning)
- How parameter changes affect timbre (grounded understanding)

### Limitation 5: Mode Collapse & Lack of Creativity

**The Core Issue**: Models trained on "average" mixing tend to give safe, generic advice.

From [Music AI research](https://arxiv.org/abs/2301.11325):
> "Models often converge to safe, middle-ground outputs that lack the distinctive character of professional mixes."

| Symptom | Impact |
|---------|--------|
| **Generic EQ curves** | Every mix sounds the same |
| **Conservative advice** | Model avoids bold creative choices |
| **Genre confusion** | Rock mixing applied to electronic |
| **Lack of context** | Doesn't account for artistic intent |

**Relevance to Our Project**: MEDIUM - We need:
- Genre-stratified training data
- Context about artistic intent in Q&A pairs
- Diversity in "correct" answers (multiple valid approaches)

---

### Summary: Limitations by Severity for Our Project

| Limitation | Severity | Mitigation Strategy |
|------------|----------|---------------------|
| Data scarcity | HIGH | Synthetic generation (our core strategy) |
| Semantic grounding | HIGH | MixRelationalQA with causal Q&A |
| Evaluation metrics | HIGH | Computed audio metrics + consistency checks |
| Long-term structure | UNKNOWN | Section tagging, hierarchical embeddings, memory-augmented approaches |
| Mode collapse | MEDIUM | Genre stratification, diverse answers |
| Audio representation | MEDIUM | CLAP embeddings + learned projection |

**Critical Unknown**: We need to determine minimum context window for coherent mixing advice. This affects architecture choices significantly.

---

## Implications for Our Project

### What This Means

1. **We can't rely on existing datasets** - They're too small, wrong format, or legally risky
2. **Human annotation at scale is impractical** - Cost prohibitive for our scope
3. **Multi-track relational data doesn't exist** - This is greenfield
4. **Synthetic generation is the path forward** - We must create our own data

### Our Advantages

| Asset | Why It Helps |
|-------|-------------|
| **108K Serum renders** | We generated them, we own them |
| **Parameter metadata** | We extracted it, full control |
| **Ableton integration** | Can generate more via M4L |
| **LLM annotation** | Can generate Q&A at scale |
| **Personal project files** | Your own sessions = your own data |

### Recommended Strategy

1. **Synthetic multi-track generation**
   - Programmatically combine our Serum stems
   - Vary tempo, key, layering systematically
   - Generate ground-truth frequency analysis

2. **LLM-assisted annotation**
   - Use Claude/GPT to generate Q&A pairs
   - Validate with computed audio metrics
   - Tier by complexity (Haiku/Sonnet/Opus)

3. **Ableton native plugin expansion**
   - Extract Ableton plugin parameters via M4L
   - Render before/after comparisons
   - Build causal understanding dataset

4. **Personal project mining**
   - Your .als files are goldmines
   - Extract actual mixing decisions
   - Real-world context, no copyright issues

---

## Key Research Sources

### Legal & Copyright
- [US Copyright Office Report (May 2025)](https://www.skadden.com/insights/publications/2025/05/copyright-office-report)
- [Billboard: What Would An AI Music License Look Like?](https://www.billboard.com/pro/what-would-ai-music-license-look-like-complicated/)
- [Water & Music: AI Ethics Playbook 2025](https://www.waterandmusic.com/music-industry-ai-ethics-playbook-2025/)
- [Music Ally: Licensing AI Music](https://musically.com/2025/05/08/licensing-ai-music-the-industry-is-focusing-on-the-wrong-problem/)

### Dataset Limitations
- [The Spheres Dataset (2025)](https://arxiv.org/html/2511.21247) - Multitrack scarcity quote
- [LP-MusicCaps](https://arxiv.org/abs/2307.16372) - Annotation cost issues
- [JamendoMaxCaps (2025)](https://arxiv.org/html/2502.07461v1) - Synthetic caption attempts
- [MusicCaps on HuggingFace](https://huggingface.co/datasets/google/MusicCaps) - Dataset size context

### Music AI Reasoning
- [Can LLMs "Reason" in Music?](https://arxiv.org/html/2407.21531v1) - LLM music reasoning limitations
- [M²UGen](https://arxiv.org/html/2311.11255v4) - Data scarcity quote origin
- [ChatMusician](https://arxiv.org/html/2402.16153v1) - Music theory with LLMs

### Multitrack Datasets
- [MUSDB18](https://sigsep.github.io/datasets/musdb.html)
- [MedleyDB](https://medleydb.weebly.com/)
- [Slakh2100](https://www.slakh.com/)

---

## Conclusion

The challenges facing music AI are **not just about data scarcity**—they're a combination of:

### Structural Problems (Data)
1. Legal uncertainty and active litigation
2. Economic incentives that discourage data sharing
3. The inherent complexity of music annotation
4. The rarity of multitrack source material

### Technical Limitations (Even with Data)
5. Audio representation gaps (discrete vs continuous)
6. Semantic grounding (LLMs don't "hear")
7. Evaluation metric failures (no reliable quality measure)
8. Mode collapse (safe, generic outputs)

**Our path forward**:
1. **Synthetic data generation** using assets we control
2. **CLAP embeddings** to bridge audio-text gap
3. **MixRelationalQA dataset** with causal reasoning Q&A
4. **Computed audio metrics** for validation
5. **Genre stratification** to avoid mode collapse

This approach sidesteps the copyright minefield while addressing the deeper technical limitations that plague music AI systems.
