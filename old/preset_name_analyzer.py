#!/usr/bin/env python3
"""
🎛️ PRESET NAME ANALYZER 🎛️
Analyze actual preset names to understand real categorization patterns
"""

import json
import re
from collections import defaultdict, Counter
from pathlib import Path

class PresetNameAnalyzer:
    """Analyze preset naming patterns to understand real-world categorization"""

    def __init__(self, dataset_path):
        with open(dataset_path, 'r') as f:
            self.dataset = json.load(f)

        self.preset_names = []
        for preset in self.dataset:
            name = preset.get('preset_name', '').strip()
            if name:
                self.preset_names.append(name)

        print(f"📊 Analyzing {len(self.preset_names)} preset names")

    def analyze_prefixes(self):
        """Analyze common prefixes (likely instrument/type indicators)"""
        prefixes = defaultdict(list)

        for name in self.preset_names:
            # Look for patterns like "BD", "SAW", "PR", "BA" at start
            match = re.match(r'^([A-Z]{2,4})\s+', name)
            if match:
                prefix = match.group(1)
                prefixes[prefix].append(name)

            # Also check for patterns like "word -" or "word:"
            match = re.match(r'^([A-Za-z]+)\s*[-:]\s*', name)
            if match:
                prefix = match.group(1).upper()
                prefixes[prefix].append(name)

        # Sort by frequency
        sorted_prefixes = sorted(prefixes.items(), key=lambda x: len(x[1]), reverse=True)

        print("\n🏷️  COMMON PREFIXES (Likely Instrument Categories)")
        print("=" * 60)
        for prefix, names in sorted_prefixes[:20]:
            print(f"{prefix:8s} ({len(names):4d}): {names[:3]}")

        return prefixes

    def analyze_brackets(self):
        """Analyze content in brackets [like this] - likely producer/pack indicators"""
        bracket_contents = defaultdict(list)

        for name in self.preset_names:
            # Find all bracket contents
            brackets = re.findall(r'\[([^\]]+)\]', name)
            for bracket in brackets:
                bracket_contents[bracket].append(name)

        # Sort by frequency
        sorted_brackets = sorted(bracket_contents.items(), key=lambda x: len(x[1]), reverse=True)

        print("\n🎨 BRACKET CONTENTS (Likely Producer/Pack Tags)")
        print("=" * 60)
        for bracket, names in sorted_brackets[:20]:
            print(f"[{bracket:8s}] ({len(names):4d}): {names[0]}")

        return bracket_contents

    def analyze_keywords(self):
        """Analyze common keywords that indicate sound characteristics"""
        # Define keyword categories to look for
        instrument_keywords = {
            'bass': ['bass', 'kick', '808', 'sub'],
            'lead': ['lead', 'saw', 'sync', 'acid'],
            'pad': ['pad', 'string', 'choir', 'ambient'],
            'pluck': ['pluck', 'arp', 'seq', 'stab'],
            'percussion': ['snare', 'hat', 'perc', 'drum'],
            'fx': ['fx', 'riser', 'sweep', 'noise', 'impact']
        }

        sound_keywords = {
            'aggressive': ['dirty', 'distorted', 'gritty', 'hard', 'brutal'],
            'smooth': ['smooth', 'warm', 'soft', 'mellow', 'silky'],
            'bright': ['bright', 'sharp', 'crystal', 'crisp', 'clean'],
            'dark': ['dark', 'deep', 'low', 'sub', 'heavy'],
            'movement': ['wobble', 'lfo', 'sweep', 'morph', 'evolving']
        }

        genre_keywords = {
            'dubstep': ['dubstep', 'dub', 'step', 'wobble', 'growl'],
            'house': ['house', 'tech', 'deep', 'groove'],
            'trance': ['trance', 'uplifting', 'epic', 'emotional'],
            'dnb': ['dnb', 'jungle', 'break', 'neuro'],
            'trap': ['trap', '808', 'snap', 'drill']
        }

        # Analyze each category
        results = {}
        for category_name, categories in [
            ('Instruments', instrument_keywords),
            ('Sound Character', sound_keywords),
            ('Genres', genre_keywords)
        ]:
            print(f"\n🎵 {category_name.upper()} KEYWORD ANALYSIS")
            print("=" * 60)

            category_results = {}
            for subcategory, keywords in categories.items():
                matches = []
                for name in self.preset_names:
                    name_lower = name.lower()
                    for keyword in keywords:
                        if keyword in name_lower:
                            matches.append(name)
                            break

                if matches:
                    category_results[subcategory] = matches
                    print(f"{subcategory:12s} ({len(matches):4d}): {matches[:3]}")

            results[category_name] = category_results

        return results

    def analyze_naming_patterns(self):
        """Analyze overall naming pattern structures"""
        patterns = {
            'prefix_space_name': 0,
            'prefix_dash_name': 0,
            'name_brackets': 0,
            'all_caps': 0,
            'mixed_case': 0,
            'contains_numbers': 0,
            'contains_special': 0
        }

        for name in self.preset_names:
            # Pattern analysis
            if re.match(r'^[A-Z]{2,4}\s+', name):
                patterns['prefix_space_name'] += 1
            if re.match(r'^[A-Za-z]+\s*-\s*', name):
                patterns['prefix_dash_name'] += 1
            if '[' in name and ']' in name:
                patterns['name_brackets'] += 1
            if name.isupper():
                patterns['all_caps'] += 1
            if any(c.islower() for c in name) and any(c.isupper() for c in name):
                patterns['mixed_case'] += 1
            if any(c.isdigit() for c in name):
                patterns['contains_numbers'] += 1
            if any(c in '!@#$%^&*()_+-={}[]|\\:";\'<>?,./' for c in name):
                patterns['contains_special'] += 1

        print("\n📊 NAMING PATTERN STATISTICS")
        print("=" * 60)
        total = len(self.preset_names)
        for pattern, count in patterns.items():
            percentage = (count / total) * 100
            print(f"{pattern:20s}: {count:5d} ({percentage:5.1f}%)")

        return patterns

    def generate_categorization_rules(self, prefixes, keywords):
        """Generate rule-based categorization based on analysis"""
        print("\n🎯 GENERATED CATEGORIZATION RULES")
        print("=" * 60)

        # Create instrument mapping from prefixes
        instrument_rules = {}

        # Map common prefixes to instruments based on frequency and examples
        prefix_mappings = {
            'BD': 'bass_drum',
            'BA': 'bass',
            'SAW': 'lead',
            'PR': 'percussion',
            'MID': 'lead',
            'HV': 'lead',
            'GS': 'misc',
            'KY': 'keys',
            'CONTROL': 'pad'
        }

        for prefix, names in prefixes.items():
            if len(names) >= 10:  # Only map frequent prefixes
                if prefix in prefix_mappings:
                    instrument_rules[prefix] = prefix_mappings[prefix]
                    print(f"Prefix '{prefix}' -> {prefix_mappings[prefix]} ({len(names)} presets)")

        # Create keyword-based rules
        keyword_rules = {}
        for category, subcategories in keywords.items():
            keyword_rules[category] = {}
            for subcategory, matches in subcategories.items():
                if matches:
                    keyword_rules[category][subcategory] = len(matches)

        return {
            'instrument_rules': instrument_rules,
            'keyword_rules': keyword_rules
        }

    def export_analysis(self):
        """Export complete analysis results"""
        print("\n🔍 RUNNING COMPLETE PRESET NAME ANALYSIS")
        print("=" * 70)

        prefixes = self.analyze_prefixes()
        brackets = self.analyze_brackets()
        keywords = self.analyze_keywords()
        patterns = self.analyze_naming_patterns()
        rules = self.generate_categorization_rules(prefixes, keywords)

        # Export results
        results = {
            'total_presets': len(self.preset_names),
            'prefixes': dict(prefixes),
            'brackets': dict(brackets),
            'keywords': keywords,
            'patterns': patterns,
            'categorization_rules': rules,
            'sample_names': self.preset_names[:50]
        }

        with open('preset_name_analysis.json', 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Analysis exported to preset_name_analysis.json")
        return results

def main():
    analyzer = PresetNameAnalyzer('ultimate_training_dataset/ultimate_serum_dataset_expanded.json')
    results = analyzer.export_analysis()

if __name__ == "__main__":
    main()