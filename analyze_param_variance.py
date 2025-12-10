#!/usr/bin/env python3
"""
Analyze Parameter Variance Across Serum Presets
================================================
Find which parameters have the highest variance (most differentiation power)
and cross-reference with sound design fundamentals.

This helps us define a principled Tier1 parameter list for CNN training.
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# Sound Design Basics - parameters that are fundamentally important
# regardless of variance (these MUST be in Tier1)
SOUND_DESIGN_FUNDAMENTALS = {
    # Oscillator A (primary sound source)
    'a_wtpos', 'a_vol', 'a_pan', 'a_octave', 'a_semi', 'a_fine',
    'a_unison', 'a_unidet', 'a_uniblend',

    # Oscillator B (secondary/layering)
    'b_wtpos', 'b_vol', 'b_pan', 'b_octave', 'b_semi', 'b_fine',
    'b_unison', 'b_unidet',

    # Filter (tonal shaping)
    'fil_cutoff', 'fil_reso', 'fil_type', 'fil_drive', 'fil_mix',

    # Amp Envelope (volume shape)
    'env1_atk', 'env1_dec', 'env1_sus', 'env1_rel',

    # Filter Envelope (timbral movement)
    'env2_atk', 'env2_dec', 'env2_sus', 'env2_rel',

    # LFO 1 (modulation)
    'lfo1_rate', 'lfo1_amt',

    # Sub & Noise (low end & texture)
    'sub_osc_level', 'noise_level',

    # Master
    'master_vol', 'mastervol',
}


def load_preset_database(json_path: str) -> List[Dict]:
    """Load the preset database."""
    print(f"Loading preset database from {json_path}...")
    with open(json_path, 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} presets")
    return data


def analyze_parameter_variance(presets: List[Dict]) -> Dict[str, Dict]:
    """
    Analyze variance statistics for each parameter across all presets.

    Returns dict with:
        param_name -> {
            'mean': float,
            'std': float,
            'min': float,
            'max': float,
            'range': float,
            'cv': float,  # coefficient of variation (std/mean)
            'count': int,  # number of presets with this param
            'unique_values': int,
        }
    """
    # Collect all values for each parameter
    param_values = defaultdict(list)

    for preset in presets:
        params = preset.get('parameters', {})
        for param_name, value in params.items():
            if isinstance(value, (int, float)):
                param_values[param_name].append(float(value))

    # Compute statistics
    stats = {}
    for param_name, values in param_values.items():
        values_arr = np.array(values)
        mean = np.mean(values_arr)
        std = np.std(values_arr)

        stats[param_name] = {
            'mean': float(mean),
            'std': float(std),
            'min': float(np.min(values_arr)),
            'max': float(np.max(values_arr)),
            'range': float(np.max(values_arr) - np.min(values_arr)),
            'cv': float(std / mean) if mean != 0 else 0,
            'count': len(values),
            'unique_values': len(np.unique(values_arr)),
        }

    return stats


def rank_parameters_by_variance(stats: Dict[str, Dict], min_count: int = 100) -> List[Tuple[str, float]]:
    """
    Rank parameters by their standard deviation (variance).
    Filter out params that appear in fewer than min_count presets.
    """
    ranked = []
    for param_name, s in stats.items():
        if s['count'] >= min_count and s['range'] > 0:
            # Use std as primary ranking metric
            ranked.append((param_name, s['std'], s))

    # Sort by std descending
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


def find_tier1_candidates(
    ranked_params: List[Tuple],
    fundamentals: set,
    top_n: int = 50
) -> Tuple[List[str], List[str], List[str]]:
    """
    Find Tier1 candidates by combining:
    1. High-variance parameters (data-driven)
    2. Sound design fundamentals (domain knowledge)

    Returns:
        tier1_both: params that are both high-variance AND fundamental
        tier1_variance: high-variance but not fundamental
        tier1_fundamental: fundamental but low-variance
    """
    # Get top N by variance
    top_variance = set(p[0] for p in ranked_params[:top_n])

    # Categorize
    tier1_both = []
    tier1_variance_only = []
    tier1_fundamental_only = []

    # First, add params that are both
    for param, std, s in ranked_params[:top_n]:
        if param in fundamentals:
            tier1_both.append(param)
        else:
            tier1_variance_only.append(param)

    # Add fundamentals not in top variance
    for param in fundamentals:
        if param not in top_variance:
            # Check if it exists in stats
            matching = [p for p in ranked_params if p[0] == param]
            if matching:
                tier1_fundamental_only.append(param)

    return tier1_both, tier1_variance_only, tier1_fundamental_only


def main():
    # Load data
    preset_path = '/Users/brentpinero/Documents/serum_llm_2/data/ultimate_training_dataset/ultimate_serum_dataset_expanded.json'
    presets = load_preset_database(preset_path)

    # Analyze variance
    print("\nAnalyzing parameter variance...")
    stats = analyze_parameter_variance(presets)
    print(f"Found {len(stats)} unique parameters")

    # Rank by variance
    ranked = rank_parameters_by_variance(stats, min_count=100)
    print(f"\n{len(ranked)} parameters have sufficient data (100+ presets)")

    # Show top 30 by variance
    print("\n" + "=" * 80)
    print("TOP 30 PARAMETERS BY VARIANCE (Standard Deviation)")
    print("=" * 80)
    print(f"{'Rank':<5} {'Parameter':<25} {'Std':<10} {'Range':<10} {'Mean':<10} {'Fundamental?'}")
    print("-" * 80)

    for i, (param, std, s) in enumerate(ranked[:30], 1):
        is_fund = "✓" if param in SOUND_DESIGN_FUNDAMENTALS else ""
        print(f"{i:<5} {param:<25} {std:<10.4f} {s['range']:<10.4f} {s['mean']:<10.4f} {is_fund}")

    # Find Tier1 candidates
    tier1_both, tier1_var, tier1_fund = find_tier1_candidates(ranked, SOUND_DESIGN_FUNDAMENTALS, top_n=40)

    print("\n" + "=" * 80)
    print("TIER 1 RECOMMENDATIONS")
    print("=" * 80)

    print(f"\n🎯 HIGH VARIANCE + FUNDAMENTAL ({len(tier1_both)} params):")
    print("   These are the MUST-HAVE parameters for CNN training")
    for p in tier1_both:
        s = stats[p]
        print(f"   - {p}: std={s['std']:.4f}, range={s['range']:.4f}")

    print(f"\n📊 HIGH VARIANCE ONLY ({len(tier1_var)} params):")
    print("   Data says these differentiate sounds, but not 'classic' sound design")
    for p in tier1_var[:15]:  # Show top 15
        s = stats[p]
        print(f"   - {p}: std={s['std']:.4f}")
    if len(tier1_var) > 15:
        print(f"   ... and {len(tier1_var) - 15} more")

    print(f"\n📚 FUNDAMENTAL BUT LOW VARIANCE ({len(tier1_fund)} params):")
    print("   Classic params that don't vary much in this dataset")
    for p in tier1_fund:
        if p in stats:
            s = stats[p]
            print(f"   - {p}: std={s['std']:.4f}, range={s['range']:.4f}")
        else:
            print(f"   - {p}: (not found in dataset)")

    # Generate recommended Tier1 list
    recommended_tier1 = tier1_both + tier1_var[:10]  # Both + top 10 high-variance

    print("\n" + "=" * 80)
    print(f"RECOMMENDED TIER 1 LIST ({len(recommended_tier1)} parameters)")
    print("=" * 80)
    print("\nTIER1_PARAMS = [")
    for p in sorted(recommended_tier1):
        print(f"    '{p}',")
    print("]")

    # Save full analysis
    output = {
        'total_presets': len(presets),
        'total_params': len(stats),
        'ranked_by_variance': [(p, s) for p, _, s in ranked[:100]],
        'tier1_both': tier1_both,
        'tier1_variance_only': tier1_var,
        'tier1_fundamental_only': tier1_fund,
        'recommended_tier1': recommended_tier1,
    }

    output_path = Path('/Users/brentpinero/Documents/serum_llm_2/data/param_variance_analysis.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nFull analysis saved to: {output_path}")


if __name__ == '__main__':
    main()
