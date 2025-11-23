#!/usr/bin/env python3
"""
🔍 DUPLICATE DETECTOR 🔍
Compares new DT_Serum_Presets against existing ultimate dataset
Finds duplicates by filename, preset name, and parameter fingerprints
"""

import json
import hashlib
from pathlib import Path
from ultimate_preset_converter import UltimatePresetConverter
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

class DuplicateDetector:
    """Detects duplicates between new presets and existing dataset"""

    def __init__(self):
        self.converter = UltimatePresetConverter()
        self.existing_dataset = {}
        self.new_presets = {}
        self.duplicates = {
            'exact_filename': [],
            'preset_name': [],
            'parameter_fingerprint': [],
            'potential_variants': []
        }

    def load_existing_dataset(self, dataset_path: str):
        """Load existing ultimate dataset for comparison"""
        print("📖 Loading existing ultimate dataset...")

        with open(dataset_path, 'r') as f:
            dataset = json.load(f)

        print(f"   Loaded {len(dataset)} existing presets")

        # Index by various criteria for fast lookup
        self.existing_dataset = {
            'by_filename': {},
            'by_preset_name': {},
            'by_param_hash': {},
            'by_source_path': {},
            'all_presets': dataset
        }

        for preset in dataset:
            # Index by filename
            filename = Path(preset['source_file']).name
            self.existing_dataset['by_filename'][filename] = preset

            # Index by preset name (normalized)
            preset_name = preset['preset_name'].strip().lower()
            if preset_name not in self.existing_dataset['by_preset_name']:
                self.existing_dataset['by_preset_name'][preset_name] = []
            self.existing_dataset['by_preset_name'][preset_name].append(preset)

            # Index by source path
            self.existing_dataset['by_source_path'][preset['source_file']] = preset

            # Create parameter fingerprint for deep comparison
            if 'parameters' in preset and isinstance(preset['parameters'], dict):
                param_hash = self._create_parameter_fingerprint(preset['parameters'])
                if param_hash not in self.existing_dataset['by_param_hash']:
                    self.existing_dataset['by_param_hash'][param_hash] = []
                self.existing_dataset['by_param_hash'][param_hash].append(preset)

        print("✅ Dataset indexed for duplicate detection")

    def process_new_presets(self, new_preset_dir: str):
        """Process new presets directory"""
        print(f"\\n🆕 Processing new presets from: {new_preset_dir}")

        # Find all new preset files
        fxp_files = list(Path(new_preset_dir).glob("**/*.fxp"))
        serum_files = list(Path(new_preset_dir).glob("**/*.SerumPreset"))

        total_new = len(fxp_files) + len(serum_files)
        print(f"   Found {len(fxp_files)} .fxp files")
        print(f"   Found {len(serum_files)} .SerumPreset files")
        print(f"   Total new files: {total_new}")

        processed_presets = []

        # Process .fxp files
        print("\\n🔓 Converting new .fxp files...")
        for i, fxp_file in enumerate(fxp_files, 1):
            result = self.converter.convert_fxp_file(str(fxp_file))
            if result:
                processed_presets.append(result)

            if i % 200 == 0 or i == len(fxp_files):
                print(f"   Progress: {i}/{len(fxp_files)} ({i/len(fxp_files)*100:.1f}%)")

        # Process .SerumPreset files
        print("\\n🎛️  Processing new .SerumPreset files...")
        for i, preset_file in enumerate(serum_files, 1):
            result = self.converter.process_serum_preset_file(str(preset_file))
            if result:
                processed_presets.append(result)

            if i % 50 == 0 or i == len(serum_files):
                print(f"   Progress: {i}/{len(serum_files)} ({i/len(serum_files)*100:.1f}%)")

        print(f"\\n✅ Processed {len(processed_presets)} new presets successfully")
        print(f"⚠️  Skipped non-Serum: {self.converter.stats['skipped_non_serum']}")
        print(f"❌ Failed conversions: {self.converter.stats['failed_conversions']}")

        return processed_presets

    def detect_duplicates(self, new_presets: List[Dict[str, Any]]):
        """Detect duplicates using multiple criteria"""
        print("\\n🔍 DETECTING DUPLICATES...")
        print("=" * 50)

        for new_preset in new_presets:
            self._check_exact_filename_match(new_preset)
            self._check_preset_name_match(new_preset)
            self._check_parameter_fingerprint_match(new_preset)
            # Skip potential variants - we only want exact duplicates

        # Generate summary
        print(f"\\n📊 DUPLICATE DETECTION RESULTS:")
        print(f"   🎯 Exact filename matches: {len(self.duplicates['exact_filename'])}")
        print(f"   📝 Preset name matches: {len(self.duplicates['preset_name'])}")
        print(f"   🔢 Parameter fingerprint matches: {len(self.duplicates['parameter_fingerprint'])}")
        print(f"   🤔 Potential variants: {len(self.duplicates['potential_variants'])}")

        return self.duplicates

    def _check_exact_filename_match(self, new_preset: Dict[str, Any]):
        """Check for exact filename matches"""
        filename = Path(new_preset['source_file']).name

        if filename in self.existing_dataset['by_filename']:
            existing = self.existing_dataset['by_filename'][filename]
            self.duplicates['exact_filename'].append({
                'new_preset': new_preset,
                'existing_preset': existing,
                'match_type': 'exact_filename',
                'confidence': 'high'
            })

    def _check_preset_name_match(self, new_preset: Dict[str, Any]):
        """Check for preset name matches"""
        preset_name = new_preset['preset_name'].strip().lower()

        if preset_name in self.existing_dataset['by_preset_name']:
            for existing in self.existing_dataset['by_preset_name'][preset_name]:
                # Skip if already found as filename match
                if Path(new_preset['source_file']).name == Path(existing['source_file']).name:
                    continue

                self.duplicates['preset_name'].append({
                    'new_preset': new_preset,
                    'existing_preset': existing,
                    'match_type': 'preset_name',
                    'confidence': 'medium'
                })

    def _check_parameter_fingerprint_match(self, new_preset: Dict[str, Any]):
        """Check for EXACT parameter matches only"""
        if 'parameters' not in new_preset or not isinstance(new_preset['parameters'], dict):
            return

        # Only check if we have meaningful parameters (not just notes)
        new_params = new_preset['parameters']
        if isinstance(new_params, dict) and 'note' in new_params:
            return  # Skip SerumPreset files with just notes

        param_hash = self._create_parameter_fingerprint(new_params)

        if param_hash in self.existing_dataset['by_param_hash']:
            for existing in self.existing_dataset['by_param_hash'][param_hash]:
                # Skip if already found by other methods
                existing_filename = Path(existing['source_file']).name
                new_filename = Path(new_preset['source_file']).name

                if (existing_filename == new_filename or
                    existing['preset_name'].strip().lower() == new_preset['preset_name'].strip().lower()):
                    continue

                # ADDITIONAL CHECK: Verify exact parameter match
                existing_params = existing.get('parameters', {})
                if self._are_parameters_exactly_equal(new_params, existing_params):
                    self.duplicates['parameter_fingerprint'].append({
                        'new_preset': new_preset,
                        'existing_preset': existing,
                        'match_type': 'exact_parameters',
                        'confidence': 'absolute'
                    })

    def _check_potential_variants(self, new_preset: Dict[str, Any]):
        """Check for potential variants (similar names, close parameters)"""
        new_name = new_preset['preset_name'].strip().lower()
        new_filename = Path(new_preset['source_file']).name.lower()

        # Check for similar names (fuzzy matching)
        for existing_name, existing_presets in self.existing_dataset['by_preset_name'].items():
            if existing_name == new_name:  # Skip exact matches (handled elsewhere)
                continue

            # Check for similar names (remove common variations)
            similarity = self._calculate_name_similarity(new_name, existing_name)
            if similarity > 0.8:  # 80% similarity threshold
                for existing in existing_presets:
                    self.duplicates['potential_variants'].append({
                        'new_preset': new_preset,
                        'existing_preset': existing,
                        'match_type': 'similar_name',
                        'confidence': 'low',
                        'similarity_score': similarity
                    })

    def _are_parameters_exactly_equal(self, params1: Dict[str, Any], params2: Dict[str, Any]) -> bool:
        """Check if two parameter sets are exactly equal"""
        if len(params1) != len(params2):
            return False

        for key in params1:
            if key not in params2:
                return False

            val1, val2 = params1[key], params2[key]

            # Handle float comparison with tiny tolerance for precision
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if abs(float(val1) - float(val2)) > 1e-10:
                    return False
            else:
                if val1 != val2:
                    return False

        return True

    def _create_parameter_fingerprint(self, parameters: Dict[str, Any]) -> str:
        """Create a hash fingerprint of parameter values"""
        # Sort parameters and create a reproducible hash
        sorted_params = sorted(parameters.items())

        # Round floats to avoid floating point precision issues, handle non-float values
        rounded_params = []
        for k, v in sorted_params:
            if isinstance(v, (int, float)):
                rounded_params.append((k, round(float(v), 6)))
            else:
                rounded_params.append((k, str(v)))  # Convert non-numeric to string

        fingerprint_str = str(rounded_params)
        return hashlib.md5(fingerprint_str.encode()).hexdigest()

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two preset names"""
        # Simple Jaccard similarity on words
        words1 = set(name1.lower().split())
        words2 = set(name2.lower().split())

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def generate_duplicate_report(self, output_path: str):
        """Generate detailed duplicate report"""
        print(f"\\n📋 Generating duplicate report...")

        report = {
            'detection_summary': {
                'total_duplicates_found': sum(len(dupes) for dupes in self.duplicates.values()),
                'exact_filename_matches': len(self.duplicates['exact_filename']),
                'preset_name_matches': len(self.duplicates['preset_name']),
                'parameter_fingerprint_matches': len(self.duplicates['parameter_fingerprint']),
                'potential_variants': len(self.duplicates['potential_variants'])
            },
            'recommendations': {
                'high_confidence_duplicates': [],
                'medium_confidence_duplicates': [],
                'low_confidence_variants': []
            },
            'detailed_matches': self.duplicates
        }

        # Categorize by confidence
        for category, matches in self.duplicates.items():
            for match in matches:
                confidence = match['confidence']

                summary = {
                    'new_file': match['new_preset']['source_file'],
                    'existing_file': match['existing_preset']['source_file'],
                    'new_preset_name': match['new_preset']['preset_name'],
                    'existing_preset_name': match['existing_preset']['preset_name'],
                    'match_type': match['match_type']
                }

                if 'similarity_score' in match:
                    summary['similarity_score'] = match['similarity_score']

                if confidence in ['high', 'very_high']:
                    report['recommendations']['high_confidence_duplicates'].append(summary)
                elif confidence == 'medium':
                    report['recommendations']['medium_confidence_duplicates'].append(summary)
                else:
                    report['recommendations']['low_confidence_variants'].append(summary)

        # Save report
        report_file = Path(output_path) / "duplicate_detection_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✅ Report saved to: {report_file}")
        return report

def main():
    """Run duplicate detection"""
    print("🔍🔍🔍 DUPLICATE DETECTION SYSTEM 🔍🔍🔍")
    print("=" * 60)

    detector = DuplicateDetector()

    # Load existing dataset
    existing_dataset_path = "/Users/brentpinero/Documents/serum_llm_2/ultimate_training_dataset/ultimate_serum_dataset.json"
    detector.load_existing_dataset(existing_dataset_path)

    # Process new presets
    new_preset_dir = "/Users/brentpinero/Documents/serum_llm_2/DT_Serum_Presets"
    new_presets = detector.process_new_presets(new_preset_dir)

    # Detect duplicates
    duplicates = detector.detect_duplicates(new_presets)

    # Generate report
    output_dir = "/Users/brentpinero/Documents/serum_llm_2/duplicate_analysis"
    Path(output_dir).mkdir(exist_ok=True)

    report = detector.generate_duplicate_report(output_dir)

    print(f"\\n🎉 DUPLICATE DETECTION COMPLETE!")
    print("=" * 60)
    print(f"📊 Found {report['detection_summary']['total_duplicates_found']} potential duplicates")
    print(f"⚠️  High confidence: {len(report['recommendations']['high_confidence_duplicates'])}")
    print(f"🤔 Medium confidence: {len(report['recommendations']['medium_confidence_duplicates'])}")
    print(f"💭 Low confidence variants: {len(report['recommendations']['low_confidence_variants'])}")

if __name__ == "__main__":
    main()