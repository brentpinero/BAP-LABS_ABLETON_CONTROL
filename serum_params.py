#!/usr/bin/env python3
"""
Serum Parameter Definitions
============================
Centralized parameter lists for CNN training and LLM fine-tuning.

Two lists based on different criteria:
1. CNN_PARAMS: Data-driven, high-variance params the CNN can learn to differentiate
2. LLM_PARAMS: Includes fundamentals for teaching sound design concepts

These were derived from variance analysis of 7,583 Serum presets.
See: analyze_param_variance.py for methodology.
"""

from typing import Dict, Tuple

# =============================================================================
# CNN_PARAMS: High-variance parameters for audio feature learning
# =============================================================================
# These are the top ~30 parameters by standard deviation across 7,583 presets.
# The CNN can only learn to differentiate what actually differs in the data.
#
# Cutoff logic: Natural break after rank 15 (std drops from 0.467 to 0.412)
# We include top 30 to capture both high-variance AND some fundamentals.

CNN_PARAMS = [
    # --- Top 15 by variance (std > 0.46) ---
    'env1_sus_db',      # Amp envelope sustain in dB (std: 0.496)
    'fil_driv',         # Filter drive/saturation (std: 0.495)
    'noise_fine',       # Noise fine pitch (std: 0.494)
    'eq_voll_db',       # EQ low band volume (std: 0.491)
    'a_curve2',         # Envelope curve 2 (std: 0.491)
    'env3_atk_ms',      # Envelope 3 attack (std: 0.490)
    'porttime_ms',      # Portamento time (std: 0.490)
    'dly_link',         # Delay L/R link (std: 0.488)
    'decay_s',          # Reverb decay time (std: 0.487)
    'cho_dly_ms',       # Chorus delay time (std: 0.487)
    'dist_bw',          # Distortion bandwidth (std: 0.487)
    'phs_bpm_sync',     # Phaser BPM sync (std: 0.487)
    'cmp_att_ms',       # Compressor attack (std: 0.485)
    'b_unidet',         # Osc B unison detune (std: 0.483) *FUNDAMENTAL*
    'a_wtpos',          # Osc A wavetable position (std: 0.467) *FUNDAMENTAL*

    # --- Ranks 16-30 (std 0.35-0.41) ---
    'b_unison',         # Osc B unison voices (std: 0.412) *FUNDAMENTAL*
    'env1_dec_s',       # Amp envelope decay (std: 0.410)
    'noise_pitch',      # Noise pitch (std: 0.402)
    'a_coarsepit',      # Osc A coarse pitch (std: 0.402)
    'fil_reso',         # Filter resonance (std: 0.393) *FUNDAMENTAL*
    'env2_rel_ms',      # Filter envelope release (std: 0.380)
    'a_vol',            # Osc A volume (std: 0.374) *FUNDAMENTAL*
    'lfo4_rate',        # LFO 4 rate (std: 0.373)
    'r_curve1',         # Release curve 1 (std: 0.371)
    'eq_q_h',           # EQ high Q (std: 0.366)
    'verbsize',         # Reverb size (std: 0.365)
    'env2_sus',         # Filter envelope sustain (std: 0.364) *FUNDAMENTAL*
    'lfo3_rate',        # LFO 3 rate (std: 0.363)
    'fil_cutoff_hz',    # Filter cutoff (std: 0.361) *FUNDAMENTAL*
    'noise_level',      # Noise level (std: 0.357) *FUNDAMENTAL*
]

NUM_CNN_PARAMS = len(CNN_PARAMS)  # 30


# =============================================================================
# LLM_PARAMS: Sound design fundamentals for text-based learning
# =============================================================================
# These are essential for teaching the LLM about synthesis, even if they
# don't vary much in our preset dataset. A producer needs to understand
# attack/decay/sustain/release even if most presets use similar values.

LLM_PARAMS = [
    # --- Oscillator A (primary sound source) ---
    'a_wtpos',          # Wavetable position: timbre control
    'a_vol',            # Volume level
    'a_pan',            # Stereo position
    'a_octave',         # Octave shift (-4 to +4)
    'a_semi',           # Semitone shift (-12 to +12)
    'a_fine',           # Fine tune (cents)
    'a_unison',         # Unison voice count (1-16)
    'a_unidet',         # Unison detune amount
    'a_uniblend',       # Unison blend
    'a_warp',           # Warp mode amount
    'a_coarsepit',      # Coarse pitch

    # --- Oscillator B (secondary/layer) ---
    'b_wtpos',          # Wavetable position
    'b_vol',            # Volume level
    'b_pan',            # Stereo position
    'b_octave',         # Octave shift
    'b_unison',         # Unison voices
    'b_unidet',         # Unison detune

    # --- Filter (tonal shaping) ---
    'fil_cutoff_hz',    # Cutoff frequency
    'fil_reso',         # Resonance
    'fil_driv',         # Filter drive/saturation
    'fil_type',         # Filter type (LP, HP, BP, etc.)
    'fil_mix',          # Dry/wet mix

    # --- Amp Envelope (ADSR - volume shape) ---
    'env1_atk_ms',      # Attack time
    'env1_hold_ms',     # Hold time
    'env1_dec_s',       # Decay time
    'env1_sus_db',      # Sustain level
    'env1_rel_ms',      # Release time

    # --- Filter Envelope (timbral movement) ---
    'env2_atk_ms',      # Attack
    'env2_hld_ms',      # Hold
    'env2_dec_s',       # Decay
    'env2_sus',         # Sustain
    'env2_rel_ms',      # Release

    # --- LFO (modulation) ---
    'lfo1_rate',        # LFO 1 speed
    'lfo2_rate',        # LFO 2 speed
    'lfo3_rate',        # LFO 3 speed
    'lfo4_rate',        # LFO 4 speed

    # --- Sub & Noise (low end & texture) ---
    'sub_osc_level',    # Sub oscillator level
    'sub_osc_pan',      # Sub pan
    'noise_level',      # Noise level
    'noise_pitch',      # Noise pitch
    'noise_pan',        # Noise pan

    # --- Effects ---
    'verb_wet',         # Reverb wet mix
    'verbsize',         # Reverb size
    'decay_s',          # Reverb decay
    'dly_wet',          # Delay wet mix
    'dly_timl',         # Delay time left
    'dly_timr',         # Delay time right
    'dly_feed',         # Delay feedback
    'dist_drv',         # Distortion drive
    'dist_wet',         # Distortion wet
    'cho_wet',          # Chorus wet
    'cho_rate_hz',      # Chorus rate
    'flg_wet',          # Flanger wet
    'phs_wet',          # Phaser wet

    # --- Master ---
    'mastervol',        # Master volume
    'mast_tun',         # Master tuning

    # --- Portamento ---
    'porttime_ms',      # Glide time
]

NUM_LLM_PARAMS = len(LLM_PARAMS)  # 56


# =============================================================================
# PARAMETER NORMALIZATION
# =============================================================================
# Most Serum params are already 0-1, but some need special handling

PARAM_RANGES: Dict[str, Tuple[float, float]] = {
    # Oscillator pitch
    'a_octave': (-4, 4),
    'b_octave': (-4, 4),
    'a_semi': (-12, 12),
    'b_semi': (-12, 12),
    'suboscoctave_oct': (-2, 2),

    # Unison (integer count)
    'a_unison': (1, 16),
    'b_unison': (1, 16),

    # Filter (some units in Hz, need normalization)
    # fil_cutoff_hz is already normalized in our dataset

    # Envelope times (already normalized in dataset)
    # env1_atk_ms, env1_dec_s, etc. are 0-1 normalized
}


def normalize_param(value: float, param_name: str) -> float:
    """Normalize parameter value to [0, 1] range."""
    if param_name in PARAM_RANGES:
        min_val, max_val = PARAM_RANGES[param_name]
        return (value - min_val) / (max_val - min_val)
    # Most Serum params are already 0-1, just clip
    return max(0.0, min(1.0, float(value)))


def denormalize_param(value: float, param_name: str) -> float:
    """Convert normalized value back to original range."""
    if param_name in PARAM_RANGES:
        min_val, max_val = PARAM_RANGES[param_name]
        return value * (max_val - min_val) + min_val
    return value


# =============================================================================
# PARAM INFO FOR DOCUMENTATION
# =============================================================================

PARAM_DESCRIPTIONS = {
    # Oscillators
    'a_wtpos': 'Oscillator A wavetable position - controls timbre/brightness',
    'b_wtpos': 'Oscillator B wavetable position',
    'a_unison': 'Number of unison voices (1-16) - adds thickness',
    'a_unidet': 'Unison detune amount - creates width and chorus effect',
    'b_unidet': 'Oscillator B unison detune',

    # Filter
    'fil_cutoff_hz': 'Filter cutoff frequency - controls brightness',
    'fil_reso': 'Filter resonance - adds nasal/squelchy character',
    'fil_driv': 'Filter drive/saturation - adds harmonics and grit',

    # Envelopes
    'env1_atk_ms': 'Amp attack - how quickly sound reaches full volume',
    'env1_dec_s': 'Amp decay - how quickly it falls to sustain level',
    'env1_sus_db': 'Amp sustain - held volume level',
    'env1_rel_ms': 'Amp release - how long sound fades after note off',

    # Effects
    'verb_wet': 'Reverb amount - adds space and ambience',
    'decay_s': 'Reverb decay time',
    'noise_level': 'Noise oscillator level - adds texture/breathiness',
}


# =============================================================================
# QUICK REFERENCE
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("SERUM PARAMETER DEFINITIONS")
    print("=" * 60)

    print(f"\nCNN_PARAMS ({NUM_CNN_PARAMS} total):")
    print("  High-variance parameters for audio feature learning")
    for i, p in enumerate(CNN_PARAMS[:10], 1):
        print(f"  {i:2}. {p}")
    print(f"  ... and {NUM_CNN_PARAMS - 10} more")

    print(f"\nLLM_PARAMS ({NUM_LLM_PARAMS} total):")
    print("  Sound design fundamentals for text-based learning")
    for i, p in enumerate(LLM_PARAMS[:10], 1):
        print(f"  {i:2}. {p}")
    print(f"  ... and {NUM_LLM_PARAMS - 10} more")

    # Show overlap
    overlap = set(CNN_PARAMS) & set(LLM_PARAMS)
    print(f"\nOverlap: {len(overlap)} params appear in both lists")

    cnn_only = set(CNN_PARAMS) - set(LLM_PARAMS)
    print(f"CNN-only (high variance, not fundamental): {len(cnn_only)}")
    for p in sorted(cnn_only)[:5]:
        print(f"  - {p}")
