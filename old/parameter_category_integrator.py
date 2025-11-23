#!/usr/bin/env python3
"""
🎛️ PARAMETER-CATEGORY INTEGRATOR 🎛️
Combine parameter importance analysis with categorized presets for optimal training data
"""

import json
import numpy as np
from collections import defaultdict
from pathlib import Path

class ParameterCategoryIntegrator:
    """Integrate parameter importance tiers with categorized preset data"""

    def __init__(self):
        self.load_datasets()
        self.setup_integration_rules()

    def load_datasets(self):
        """Load all the datasets we've built"""
        print("📊 Loading datasets...")

        # Load parameter importance analysis
        with open('serum_parameter_analysis.json', 'r') as f:
            self.param_analysis = json.load(f)

        # Load categorized presets
        with open('tagged_serum_dataset.json', 'r') as f:
            self.categorized_data = json.load(f)

        # Load original preset data for parameters
        with open('ultimate_training_dataset/ultimate_serum_dataset_expanded.json', 'r') as f:
            self.original_presets = json.load(f)

        print(f"   ✅ Parameter analysis: {self.param_analysis['total_presets_analyzed']} presets")
        print(f"   ✅ Categorized data: {len(self.categorized_data['presets'])} presets")
        print(f"   ✅ Original presets: {len(self.original_presets)} presets")

    def setup_integration_rules(self):
        """Setup rules for integrating parameters with categories"""

        # Extract parameter importance tiers from analysis
        self.param_tiers = self.param_analysis.get('final_recommendations', {})

        # Map synthesis methods to optimal parameter sets
        self.synthesis_param_mapping = {
            'wavetable': {
                'essential': ['a_wtpos', 'b_wtpos', 'c_wtpos', 'a_warp', 'b_warp'],
                'important': ['a_vol', 'b_vol', 'mastervol', 'fil_cutoff']
            },
            'sample_based': {
                'essential': ['noise_level', 'noise_pitch', 'noise_fine'],
                'important': ['fil_cutoff', 'fil_reso', 'env1_att', 'env1_rel']
            },
            'subtractive': {
                'essential': ['a_vol', 'b_vol', 'fil_cutoff', 'fil_reso'],
                'important': ['env1_att', 'env1_dec', 'env1_sus', 'env1_rel']
            }
        }

        # Map instrument types to parameter priorities
        self.instrument_param_mapping = {
            'bass': {
                'critical': ['mastervol', 'a_vol', 'sub_osc_level', 'fil_cutoff'],
                'important': ['a_octave', 'a_semi', 'fil_reso', 'env1_sus'],
                'synthesis_preference': 'subtractive'
            },
            'lead': {
                'critical': ['mastervol', 'a_vol', 'fil_cutoff', 'fil_reso'],
                'important': ['a_wtpos', 'a_warp', 'a_unidet', 'env1_att'],
                'synthesis_preference': 'wavetable'
            },
            'pad': {
                'critical': ['mastervol', 'a_vol', 'env1_att', 'env1_rel'],
                'important': ['fil_cutoff', 'a_wtpos', 'fx_reverb', 'fx_delay'],
                'synthesis_preference': 'wavetable'
            },
            'pluck': {
                'critical': ['mastervol', 'a_vol', 'env1_att', 'env1_dec'],
                'important': ['fil_cutoff', 'fil_envelope', 'a_wtpos'],
                'synthesis_preference': 'wavetable'
            },
            'keys': {
                'critical': ['mastervol', 'a_vol', 'env1_att', 'env1_rel'],
                'important': ['fil_cutoff', 'a_wtpos', 'b_vol'],
                'synthesis_preference': 'sample_based'
            },
            'fx': {
                'critical': ['mastervol', 'noise_level', 'fx_distortion'],
                'important': ['lfo1_rate', 'lfo1_amt', 'fil_cutoff'],
                'synthesis_preference': 'sample_based'
            }
        }

    def find_matching_preset(self, categorized_preset):
        """Find matching original preset with parameters"""
        # The categorized preset IS the original preset with tags added
        if 'tags' in categorized_preset:
            return categorized_preset
        else:
            return None

    def extract_relevant_parameters(self, preset_params, instrument_type, tier_focus='essential'):
        """Extract most relevant parameters for training based on instrument and tier"""
        if not preset_params:
            return {}

        relevant_params = {}

        # Get tier 1 essential parameters
        tier_1_params = self.param_tiers.get('tier_1_essential', {}).get('params', [])

        # Get instrument-specific critical parameters
        instrument_mapping = self.instrument_param_mapping.get(instrument_type, {})
        critical_params = instrument_mapping.get('critical', [])
        important_params = instrument_mapping.get('important', [])

        # Combine parameter priorities
        priority_params = set(tier_1_params + critical_params + important_params)

        # Extract parameters with fuzzy matching
        for target_param in priority_params:
            matching_value = self.find_parameter_value(preset_params, target_param)
            if matching_value is not None:
                relevant_params[target_param] = matching_value

        return relevant_params

    def find_parameter_value(self, params, target_param):
        """Find parameter value with fuzzy matching"""
        target_lower = target_param.lower()

        # Direct match
        if target_param in params:
            return params[target_param]

        # Fuzzy matching
        for param_name, value in params.items():
            param_lower = str(param_name).lower()

            # Remove common suffixes for matching
            for suffix in ['_hz', '_ms', '_db', '_percent', '_oct', '_semitones', '_cents']:
                if param_lower.endswith(suffix):
                    param_lower = param_lower[:-len(suffix)]
                    break

            # Check if target is contained in parameter name or vice versa
            if (target_lower in param_lower or param_lower in target_lower) and isinstance(value, (int, float)):
                return float(value)

        return None

    def categorize_preset_complexity(self, params):
        """Categorize preset complexity based on parameter usage"""
        if not params:
            return 'simple'

        # Count non-default parameters (assuming 0.0 is default)
        non_default_count = sum(1 for v in params.values() if isinstance(v, (int, float)) and abs(v) > 0.01)

        if non_default_count < 10:
            return 'simple'
        elif non_default_count < 25:
            return 'moderate'
        else:
            return 'complex'

    def detect_synthesis_method(self, params):
        """Detect likely synthesis method from parameters"""
        if not params:
            return 'unknown'

        # Check for wavetable indicators
        wt_indicators = ['wtpos', 'warp', 'wavetable']
        if any(any(ind in str(k).lower() for ind in wt_indicators) for k in params.keys()):
            return 'wavetable'

        # Check for sample/noise indicators
        sample_indicators = ['noise', 'sample', 'granular']
        if any(any(ind in str(k).lower() for ind in sample_indicators) for k in params.keys()):
            return 'sample_based'

        # Default to subtractive
        return 'subtractive'

    def create_enriched_preset(self, categorized_preset):
        """Create enriched preset with parameter analysis"""
        # Check if this preset has tags (was successfully categorized)
        if 'tags' not in categorized_preset:
            return None

        tags = categorized_preset['tags']
        if 'error' in tags:
            return None

        instrument_type = tags['instrument']['type']
        if not instrument_type:
            return None

        # Extract original parameters
        original_params = categorized_preset.get('parameters', {})

        # Get relevant parameters for this instrument type
        relevant_params = self.extract_relevant_parameters(original_params, instrument_type)

        # Additional analysis
        complexity = self.categorize_preset_complexity(original_params)
        synthesis_method = self.detect_synthesis_method(original_params)

        # Create enriched preset
        enriched = {
            'preset_name': tags['preset_name'],
            'categorization': {
                'instrument': {
                    'type': instrument_type,
                    'confidence': tags['instrument']['confidence'],
                    'detection_method': tags['instrument']['detection_method']
                },
                'sound_character': tags.get('sound_character', []),
                'genre': tags.get('genre'),
                'producer': tags.get('producer')
            },
            'synthesis_analysis': {
                'method': synthesis_method,
                'complexity': complexity,
                'parameter_count': len(original_params),
                'relevant_parameter_count': len(relevant_params)
            },
            'parameters': {
                'all_parameters': original_params,
                'tier_1_essential': relevant_params,
                'parameter_mapping': self.create_parameter_mapping(relevant_params, instrument_type)
            },
            'training_metadata': {
                'priority_score': self.calculate_training_priority(tags, complexity, len(relevant_params)),
                'recommended_for_training': len(relevant_params) >= 5,  # Must have enough relevant params
                'parameter_tier_focus': 'tier_1_essential'
            }
        }

        return enriched

    def create_parameter_mapping(self, params, instrument_type):
        """Create structured parameter mapping for training"""
        mapping = {
            'oscillators': {},
            'filters': {},
            'envelopes': {},
            'lfos': {},
            'effects': {},
            'global': {}
        }

        for param_name, value in params.items():
            param_lower = param_name.lower()

            # Categorize parameters
            if any(osc in param_lower for osc in ['a_', 'b_', 'c_', 'osc', 'wtpos', 'warp']):
                mapping['oscillators'][param_name] = value
            elif any(filt in param_lower for filt in ['fil_', 'filter', 'cutoff', 'reso']):
                mapping['filters'][param_name] = value
            elif any(env in param_lower for env in ['env', 'att', 'dec', 'sus', 'rel']):
                mapping['envelopes'][param_name] = value
            elif any(lfo in param_lower for lfo in ['lfo', 'mod']):
                mapping['lfos'][param_name] = value
            elif any(fx in param_lower for fx in ['fx_', 'reverb', 'delay', 'chorus', 'distortion']):
                mapping['effects'][param_name] = value
            else:
                mapping['global'][param_name] = value

        return mapping

    def calculate_training_priority(self, tags, complexity, relevant_param_count):
        """Calculate training priority score"""
        score = 0.0

        # Instrument confidence
        score += tags['instrument']['confidence'] * 0.3

        # Detection method reliability
        if tags['instrument']['detection_method'] == 'prefix':
            score += 0.2
        elif tags['instrument']['detection_method'] == 'keywords':
            score += 0.15

        # Complexity bonus
        complexity_scores = {'simple': 0.1, 'moderate': 0.2, 'complex': 0.3}
        score += complexity_scores.get(complexity, 0.0)

        # Relevant parameter count
        score += min(relevant_param_count / 20.0, 0.25)  # Max 0.25 for parameter richness

        # Sound character bonus
        if tags.get('sound_character'):
            score += 0.1

        return min(score, 1.0)  # Cap at 1.0

    def process_all_presets(self):
        """Process all categorized presets and create enriched dataset"""
        print("\n🔧 INTEGRATING PARAMETER ANALYSIS WITH CATEGORIES")
        print("=" * 60)

        enriched_presets = []
        stats = defaultdict(int)

        total_presets = len(self.categorized_data['presets'])

        for i, categorized_preset in enumerate(self.categorized_data['presets']):
            if i % 1000 == 0:
                print(f"   Processing {i}/{total_presets} presets...")

            enriched = self.create_enriched_preset(categorized_preset)

            if enriched:
                enriched_presets.append(enriched)
                stats['enriched_successfully'] += 1

                # Update statistics
                instrument = enriched['categorization']['instrument']['type']
                stats[f'instrument_{instrument}'] += 1

                complexity = enriched['synthesis_analysis']['complexity']
                stats[f'complexity_{complexity}'] += 1

                synthesis = enriched['synthesis_analysis']['method']
                stats[f'synthesis_{synthesis}'] += 1

                if enriched['training_metadata']['recommended_for_training']:
                    stats['recommended_for_training'] += 1

            else:
                stats['failed_to_enrich'] += 1

        # Print statistics
        print(f"\n📈 INTEGRATION STATISTICS")
        print("=" * 60)
        print(f"Total processed: {total_presets}")
        print(f"Successfully enriched: {stats['enriched_successfully']}")
        print(f"Failed to enrich: {stats['failed_to_enrich']}")
        print(f"Recommended for training: {stats['recommended_for_training']}")

        print(f"\n🎵 INSTRUMENT DISTRIBUTION")
        for key, count in sorted(stats.items()):
            if key.startswith('instrument_'):
                instrument = key.replace('instrument_', '')
                percentage = (count / stats['enriched_successfully']) * 100
                print(f"   {instrument:12s}: {count:4d} ({percentage:5.1f}%)")

        print(f"\n🎛️ SYNTHESIS METHOD DISTRIBUTION")
        for key, count in sorted(stats.items()):
            if key.startswith('synthesis_'):
                synthesis = key.replace('synthesis_', '')
                percentage = (count / stats['enriched_successfully']) * 100
                print(f"   {synthesis:12s}: {count:4d} ({percentage:5.1f}%)")

        print(f"\n🔧 COMPLEXITY DISTRIBUTION")
        for key, count in sorted(stats.items()):
            if key.startswith('complexity_'):
                complexity = key.replace('complexity_', '')
                percentage = (count / stats['enriched_successfully']) * 100
                print(f"   {complexity:12s}: {count:4d} ({percentage:5.1f}%)")

        return enriched_presets, dict(stats)

    def export_enriched_dataset(self, enriched_presets, stats):
        """Export the final enriched dataset"""
        print(f"\n💾 EXPORTING ENRICHED DATASET")
        print("=" * 60)

        # Create final dataset
        final_dataset = {
            'metadata': {
                'total_presets': len(enriched_presets),
                'integration_statistics': stats,
                'parameter_tiers_used': list(self.param_tiers.keys()),
                'synthesis_methods': ['wavetable', 'sample_based', 'subtractive'],
                'instrument_types': list(self.instrument_param_mapping.keys()),
                'description': 'Enriched Serum preset dataset with parameter importance analysis and categorization'
            },
            'parameter_analysis_reference': self.param_analysis,
            'presets': enriched_presets
        }

        # Export main dataset
        output_path = 'enriched_serum_training_dataset.json'
        with open(output_path, 'w') as f:
            json.dump(final_dataset, f, indent=2)

        print(f"✅ Enriched dataset exported to {output_path}")
        print(f"📊 Dataset size: {len(enriched_presets)} presets")

        # Create training-ready subset (high priority presets)
        training_ready = [p for p in enriched_presets if p['training_metadata']['recommended_for_training']]

        training_output = 'training_ready_serum_dataset.json'
        with open(training_output, 'w') as f:
            json.dump({
                'metadata': {
                    'total_presets': len(training_ready),
                    'selection_criteria': 'High priority presets with sufficient parameter coverage',
                    'min_relevant_parameters': 5
                },
                'presets': training_ready
            }, f, indent=2)

        print(f"✅ Training-ready subset exported to {training_output}")
        print(f"📊 Training subset size: {len(training_ready)} presets")

        return output_path, training_output

def main():
    """Run parameter-category integration"""
    print("🎛️ PARAMETER-CATEGORY INTEGRATOR")
    print("=" * 70)

    integrator = ParameterCategoryIntegrator()
    enriched_presets, stats = integrator.process_all_presets()
    output_path, training_path = integrator.export_enriched_dataset(enriched_presets, stats)

    print(f"\n🎉 INTEGRATION COMPLETE!")
    print(f"   Full dataset: {output_path}")
    print(f"   Training-ready: {training_path}")

if __name__ == "__main__":
    main()