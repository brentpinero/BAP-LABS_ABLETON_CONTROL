# ARCHITECTURE DECISIONS LOG

## Decision 1: CNN for Audio Feature Extraction
**Date**: Session 1  
**Decision**: Use CNN (not Transformer) for initial audio → parameter feature extraction  
**Rationale**:
- Spectrograms have spatial structure (frequency × time)
- CNNs have translational equivariance (good for spectrograms)
- More data-efficient (works with 7,583 samples)
- Faster training/inference on M4 Max
- Proven track record (InverSynth, DDSP)

**Trade-offs**:
- Limited global context (vs Transformers)
- No pre-trained models available (vs AST)
- Less flexible than attention-based models

**Status**: Approved for Phase 1 implementation

---

## Decision 2: Small LLM for Reasoning (Not Just CNN Regression)
**Date**: Session 1  
**Decision**: Use CNN outputs to train a small reasoning LLM, NOT use CNN alone  
**Rationale**:
- Music production requires COMMUNICATION (explain decisions)
- Need ITERATIVE reasoning (adjust → listen → re-adjust)
- CNNs lack language capability
- Small LLM can integrate multiple modalities (audio features + text + parameter state)

**Architecture**:
```
CNN (audio features) ──┐
                       ├──> Small LLM ──> Actions + Explanations
User text ────────────┤
Current params ───────┘
```

**Status**: Core design principle

---

## Decision 3: <200ms Inference Constraint
**Date**: Session 1  
**Decision**: Target <200ms for LLM inference on M4 Max  
**Rationale**:
- Real-time feel for music production workflow
- Enables iterative back-and-forth conversations
- Competitive with commercial AI tools

**Implementation Strategies**:
- 4-bit quantization (MLX)
- Small model (3B parameters max)
- Optimized context length
- KV cache optimization

**Status**: Hard requirement

---

## Decision 4: Transfer Learning Pipeline
**Date**: Session 1  
**Decision**: CNN → LLM distillation via transfer learning  
**Approach**: TBD (needs research)
**Options**:
1. Fine-tune LLM on (CNN_features + text) → parameter_changes
2. Use CNN as "perception module" + LLM as "reasoning module"
3. Multi-modal adapter layers

**Status**: To be designed in Phase 3

---

## Decision 5: Dataset Strategy
**Date**: Session 1  
**Decision**: Render all 7,583 presets as audio for CNN training  
**Format**:
- Note: C3 (bass-focused)
- Duration: 2 seconds
- Sample rate: 44.1kHz
- File format: WAV (uncompressed)

**Status**: Phase 1 priority

---

## Future Decisions to Make:

### Small LLM Selection
**Options**:
- Qwen2.5-3B (best reasoning?)
- Phi-3.5-mini (optimized inference?)
- Llama-3.2-3B (Meta's latest?)

**Criteria**:
- Inference speed on M4 Max + MLX
- Reasoning capability
- Context length support
- Fine-tuning ease

### Multi-Modal Fusion Strategy
**Question**: How to combine CNN audio features with text input in LLM?
**Options**:
- Simple concatenation
- Adapter layers
- Cross-attention
- Prefix tuning

### Iterative Reasoning Pattern
**Question**: How to implement listen → reason → adjust → repeat?
**Options**:
- ReAct pattern
- Chain-of-thought prompting
- Custom feedback loop

---

## Technical Debt / Open Questions:

1. How many parameters should CNN predict? All 2,397 or subset?
2. Should CNN output embeddings or direct parameters?
3. Optimal mel-spectrogram configuration for Serum sounds?
4. How to handle temporal dynamics (e.g., evolving pads)?
5. Evaluation metrics beyond MSE for parameter prediction?

---

## Notes:
- User prefers deep justifications for all decisions
- "Why not X?" discussions encouraged
- Build prototypes to test hypotheses, don't over-engineer
