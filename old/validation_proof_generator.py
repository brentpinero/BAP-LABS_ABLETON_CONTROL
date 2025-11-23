#!/usr/bin/env python3
"""
🔍 CATEGORIZATION VALIDATION PROOF 🔍
Detailed evidence and validation for preset categorization decisions
"""

import json
import re
from collections import defaultdict, Counter
from pathlib import Path

class CategorizationValidator:
    """Generate detailed validation proof for categorization decisions"""

    def __init__(self):
        self.load_datasets()

    def load_datasets(self):
        """Load original analysis and tagged results"""
        # Load preset name analysis
        with open('preset_name_analysis.json', 'r') as f:
            self.name_analysis = json.load(f)

        # Load tagged dataset
        with open('tagged_serum_dataset.json', 'r') as f:
            self.tagged_data = json.load(f)

        # Load original dataset for cross-reference
        with open('ultimate_training_dataset/ultimate_serum_dataset_expanded.json', 'r') as f:
            self.original_dataset = json.load(f)

        print(f"📊 Loaded datasets:")
        print(f"   - Original: {len(self.original_dataset)} presets")
        print(f"   - Tagged: {len(self.tagged_data['presets'])} presets")

    def validate_prefix_mappings(self):
        """Validate prefix-to-instrument mappings with evidence"""
        print("\n🏷️  PREFIX MAPPING VALIDATION")
        print("=" * 80)

        prefixes = self.name_analysis['prefixes']

        # Analyze each major prefix
        evidence = {}

        for prefix, preset_names in prefixes.items():
            if len(preset_names) >= 50:  # Only analyze frequent prefixes
                print(f"\n🔍 ANALYZING PREFIX: '{prefix}' ({len(preset_names)} presets)")
                print("-" * 60)

                # Sample analysis
                sample_names = preset_names[:10]

                # Clean names for analysis
                cleaned_samples = []
                for name in sample_names:
                    cleaned = name.replace('\x00', '').strip()
                    cleaned_samples.append(cleaned)

                print("Sample preset names:")
                for i, name in enumerate(cleaned_samples, 1):
                    print(f"  {i:2d}. {name}")

                # Keyword analysis within this prefix group
                keyword_counts = defaultdict(int)

                for name in preset_names:
                    cleaned_name = name.replace('\x00', '').strip().lower()

                    # Count instrument keywords
                    if any(word in cleaned_name for word in ['bass', 'sub', 'kick', '808', 'reese', 'wobble']):
                        keyword_counts['bass_related'] += 1
                    if any(word in cleaned_name for word in ['lead', 'saw', 'sync', 'acid', 'solo']):
                        keyword_counts['lead_related'] += 1
                    if any(word in cleaned_name for word in ['pad', 'string', 'choir', 'ambient']):
                        keyword_counts['pad_related'] += 1
                    if any(word in cleaned_name for word in ['pluck', 'arp', 'seq', 'stab']):
                        keyword_counts['pluck_related'] += 1
                    if any(word in cleaned_name for word in ['key', 'keys', 'piano', 'organ']):
                        keyword_counts['keys_related'] += 1
                    if any(word in cleaned_name for word in ['fx', 'riser', 'sweep', 'noise', 'effect']):
                        keyword_counts['fx_related'] += 1

                # Determine dominant category
                if keyword_counts:
                    dominant_category = max(keyword_counts.items(), key=lambda x: x[1])
                    total_analyzed = sum(keyword_counts.values())

                    print(f"\nKeyword analysis within '{prefix}' presets:")
                    for category, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
                        if count > 0:
                            percentage = (count / len(preset_names)) * 100
                            print(f"  {category:15s}: {count:4d} ({percentage:5.1f}% of all {prefix} presets)")

                    print(f"\n🎯 CONCLUSION: '{prefix}' is predominantly {dominant_category[0].replace('_related', '')}")
                    print(f"   Evidence strength: {dominant_category[1]}/{len(preset_names)} = {(dominant_category[1]/len(preset_names))*100:.1f}%")

                    evidence[prefix] = {
                        'total_presets': len(preset_names),
                        'dominant_category': dominant_category[0].replace('_related', ''),
                        'evidence_count': dominant_category[1],
                        'confidence': (dominant_category[1] / len(preset_names)) * 100,
                        'keyword_breakdown': dict(keyword_counts),
                        'sample_names': cleaned_samples
                    }
                else:
                    print(f"\n❓ CONCLUSION: '{prefix}' - insufficient keyword evidence")
                    evidence[prefix] = {
                        'total_presets': len(preset_names),
                        'dominant_category': 'unknown',
                        'evidence_count': 0,
                        'confidence': 0.0,
                        'sample_names': cleaned_samples
                    }

        return evidence

    def validate_keyword_classifications(self):
        """Validate keyword-based classifications"""
        print(f"\n🔍 KEYWORD CLASSIFICATION VALIDATION")
        print("=" * 80)

        # Load tagged presets that were classified by keywords
        keyword_classified = []
        for preset in self.tagged_data['presets']:
            tags = preset['tags']
            if 'error' not in tags and tags['instrument']['detection_method'] == 'keywords':
                keyword_classified.append(preset)

        print(f"Found {len(keyword_classified)} presets classified by keywords")

        # Group by instrument type
        by_instrument = defaultdict(list)
        for preset in keyword_classified:
            instrument = preset['tags']['instrument']['type']
            by_instrument[instrument].append(preset)

        # Validate each instrument category
        validation_results = {}

        for instrument, presets in by_instrument.items():
            if len(presets) >= 20:  # Only validate categories with sufficient data
                print(f"\n🎵 VALIDATING: {instrument.upper()} ({len(presets)} presets)")
                print("-" * 60)

                # Sample 10 presets for detailed analysis
                sample = presets[:10]

                evidence_count = 0
                for i, preset in enumerate(sample, 1):
                    name = preset['tags']['preset_name']
                    confidence = preset['tags']['instrument']['confidence']

                    # Check what keywords triggered classification
                    name_lower = name.lower()
                    triggered_keywords = []

                    if instrument == 'bass':
                        for kw in ['bass', 'sub', 'kick', '808', 'reese', 'wobble', 'low']:
                            if kw in name_lower:
                                triggered_keywords.append(kw)
                    elif instrument == 'lead':
                        for kw in ['lead', 'saw', 'sync', 'acid', 'solo', 'melody']:
                            if kw in name_lower:
                                triggered_keywords.append(kw)
                    elif instrument == 'pad':
                        for kw in ['pad', 'string', 'choir', 'ambient', 'atmosphere']:
                            if kw in name_lower:
                                triggered_keywords.append(kw)
                    elif instrument == 'keys':
                        for kw in ['key', 'keys', 'piano', 'organ', 'chord']:
                            if kw in name_lower:
                                triggered_keywords.append(kw)
                    elif instrument == 'fx':
                        for kw in ['fx', 'riser', 'sweep', 'noise', 'effect', 'impact']:
                            if kw in name_lower:
                                triggered_keywords.append(kw)
                    elif instrument == 'pluck':
                        for kw in ['pluck', 'arp', 'seq', 'stab', 'short']:
                            if kw in name_lower:
                                triggered_keywords.append(kw)

                    if triggered_keywords:
                        evidence_count += 1
                        status = "✅ VALID"
                    else:
                        status = "❓ UNCLEAR"

                    print(f"  {i:2d}. {name[:40]:40s} -> {status}")
                    if triggered_keywords:
                        print(f"      Keywords: {', '.join(triggered_keywords)} (conf: {confidence:.2f})")
                    else:
                        print(f"      No obvious keywords found (conf: {confidence:.2f})")

                validation_accuracy = (evidence_count / len(sample)) * 100
                print(f"\n🎯 VALIDATION RESULT: {evidence_count}/{len(sample)} = {validation_accuracy:.1f}% accurate")

                validation_results[instrument] = {
                    'total_presets': len(presets),
                    'sample_size': len(sample),
                    'valid_samples': evidence_count,
                    'accuracy': validation_accuracy
                }

        return validation_results

    def cross_validate_with_parameters(self):
        """Cross-validate categorizations with actual preset parameters"""
        print(f"\n🎛️  PARAMETER CROSS-VALIDATION")
        print("=" * 80)

        # Load parameter importance analysis
        with open('serum_parameter_analysis.json', 'r') as f:
            param_analysis = json.load(f)

        print("Cross-validating instrument classifications with actual Serum parameters...")

        # Sample validation across different instrument types
        cross_validation = {}

        for preset in self.tagged_data['presets'][:100]:  # Sample first 100
            tags = preset['tags']
            if 'error' not in tags and tags['instrument']['type']:
                instrument = tags['instrument']['type']
                name = tags['preset_name']

                # Get parameters from original dataset
                original_preset = None
                for orig in self.original_dataset:
                    if orig.get('preset_name', '').replace('\x00', '').strip() == name:
                        original_preset = orig
                        break

                if original_preset and 'parameters' in original_preset:
                    params = original_preset['parameters']

                    # Analyze key parameters that should correlate with instrument type
                    param_evidence = self.analyze_parameter_evidence(params, instrument)

                    if instrument not in cross_validation:
                        cross_validation[instrument] = []

                    cross_validation[instrument].append({
                        'name': name,
                        'param_evidence': param_evidence,
                        'supports_classification': param_evidence['supports_classification']
                    })

        # Report cross-validation results
        for instrument, validations in cross_validation.items():
            if len(validations) >= 5:
                supporting = sum(1 for v in validations if v['supports_classification'])
                accuracy = (supporting / len(validations)) * 100

                print(f"\n{instrument.upper()} parameter validation:")
                print(f"  Samples analyzed: {len(validations)}")
                print(f"  Parameter evidence supports classification: {supporting}/{len(validations)} ({accuracy:.1f}%)")

        return cross_validation

    def analyze_parameter_evidence(self, params, instrument):
        """Analyze if parameters support the instrument classification"""
        evidence = {
            'supports_classification': False,
            'evidence_points': [],
            'contradiction_points': []
        }

        # Convert flat parameter dict if needed
        if isinstance(params, dict):
            # Look for instrument-specific parameter patterns

            if instrument == 'bass':
                # Bass should have low-frequency emphasis
                if any('sub' in str(k).lower() for k in params.keys()):
                    evidence['evidence_points'].append('Has sub oscillator parameters')

                # Check for typical bass parameter values
                for param_name, value in params.items():
                    if isinstance(value, (int, float)):
                        if 'octave' in str(param_name).lower() and value < 0:
                            evidence['evidence_points'].append(f'Low octave setting: {param_name}={value}')
                        elif 'cutoff' in str(param_name).lower() and value < 0.5:
                            evidence['evidence_points'].append(f'Low-pass filtering: {param_name}={value}')

            elif instrument == 'lead':
                # Lead should have higher frequency content
                for param_name, value in params.items():
                    if isinstance(value, (int, float)):
                        if 'resonance' in str(param_name).lower() and value > 0.3:
                            evidence['evidence_points'].append(f'Resonant filtering: {param_name}={value}')
                        elif 'detune' in str(param_name).lower() and value > 0:
                            evidence['evidence_points'].append(f'Detuning for width: {param_name}={value}')

            elif instrument == 'pad':
                # Pad should have slow attack, long release
                for param_name, value in params.items():
                    if isinstance(value, (int, float)):
                        if 'attack' in str(param_name).lower() and value > 0.2:
                            evidence['evidence_points'].append(f'Slow attack: {param_name}={value}')
                        elif 'release' in str(param_name).lower() and value > 0.3:
                            evidence['evidence_points'].append(f'Long release: {param_name}={value}')

        # Determine if evidence supports classification
        evidence['supports_classification'] = len(evidence['evidence_points']) > 0

        return evidence

    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        print(f"\n📋 GENERATING COMPREHENSIVE VALIDATION REPORT")
        print("=" * 80)

        # Run all validations
        prefix_evidence = self.validate_prefix_mappings()
        keyword_validation = self.validate_keyword_classifications()
        parameter_validation = self.cross_validate_with_parameters()

        # Compile comprehensive report
        report = {
            'validation_summary': {
                'total_presets_analyzed': len(self.tagged_data['presets']),
                'successfully_tagged': self.tagged_data['metadata']['tagged_presets'],
                'success_rate': (self.tagged_data['metadata']['tagged_presets'] / len(self.tagged_data['presets'])) * 100
            },
            'prefix_validation': {
                'methodology': 'Analyzed frequency and keyword co-occurrence within prefix groups',
                'evidence': prefix_evidence
            },
            'keyword_validation': {
                'methodology': 'Verified keyword-based classifications against actual preset names',
                'results': keyword_validation
            },
            'parameter_validation': {
                'methodology': 'Cross-validated instrument classifications with actual Serum parameters',
                'results': parameter_validation
            },
            'overall_confidence': self.calculate_overall_confidence(prefix_evidence, keyword_validation)
        }

        # Export report
        with open('categorization_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        print(f"\n🎯 VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total presets: {report['validation_summary']['total_presets_analyzed']}")
        print(f"Successfully tagged: {report['validation_summary']['successfully_tagged']}")
        print(f"Success rate: {report['validation_summary']['success_rate']:.1f}%")

        print(f"\nValidation methods used:")
        print(f"1. Prefix frequency analysis (statistical)")
        print(f"2. Keyword co-occurrence validation (linguistic)")
        print(f"3. Parameter cross-validation (technical)")

        print(f"\n✅ Comprehensive validation report exported to 'categorization_validation_report.json'")

        return report

    def calculate_overall_confidence(self, prefix_evidence, keyword_validation):
        """Calculate overall confidence in categorization system"""
        confidence_scores = []

        # Prefix-based confidence
        for prefix, evidence in prefix_evidence.items():
            if evidence['confidence'] > 0:
                confidence_scores.append(evidence['confidence'])

        # Keyword-based confidence
        for instrument, validation in keyword_validation.items():
            confidence_scores.append(validation['accuracy'])

        if confidence_scores:
            return sum(confidence_scores) / len(confidence_scores)
        else:
            return 0.0

def main():
    """Run comprehensive validation"""
    validator = CategorizationValidator()
    report = validator.generate_validation_report()

if __name__ == "__main__":
    main()