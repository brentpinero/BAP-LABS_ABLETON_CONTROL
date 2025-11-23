#!/usr/bin/env python3
"""
🎛️ REAL-WORLD PRESET TAGGER 🎛️
Accurate rule-based tagging system based on actual preset naming patterns
"""

import json
import re
from collections import defaultdict
from pathlib import Path

class RealWorldPresetTagger:
    """Tag presets using patterns discovered from real preset names"""

    def __init__(self):
        # REAL INSTRUMENT MAPPING - Based on actual analysis
        self.prefix_instrument_map = {
            # High confidence mappings (>100 presets each)
            'BS': 'bass_synth',       # 1,128 presets - Bass Synth
            'LD': 'lead',             # 569 presets - Lead
            'BASS': 'bass',           # 489 presets - Bass (explicit)
            'BA': 'bass',             # 451 presets - Bass (abbreviated)
            'PD': 'pad',              # 302 presets - Pad
            'PL': 'pluck',            # 260 presets - Pluck
            'XLNT': 'misc',           # 254 presets - Producer tag (XLNT)
            'BSS': 'bass',            # 197 presets - Bass plural
            'SY': 'synth',            # 184 presets - Synth
            'SUB': 'bass',            # 166 presets - Sub bass
            'FX': 'fx',               # 159 presets - Effects
            'REESE': 'bass',          # 127 presets - Reese bass
            'KEYS': 'keys',           # 122 presets - Keys
            'CH': 'chord',            # 115 presets - Chord
            'LEAD': 'lead',           # 104 presets - Lead (explicit)
            'KEY': 'keys',            # 94 presets - Keys (singular)
            'PAD': 'pad',             # 82 presets - Pad (explicit)
            'ARP': 'arp',             # 67 presets - Arpeggio
            'PLUCK': 'pluck',         # 61 presets - Pluck (explicit)
        }

        # KEYWORD DETECTION - Based on actual preset content
        self.instrument_keywords = {
            'bass': {
                'primary': ['bass', 'sub', 'kick', '808', 'reese'],
                'secondary': ['low', 'bottom', 'wobble', 'growl']
            },
            'lead': {
                'primary': ['lead', 'saw', 'sync', 'acid'],
                'secondary': ['solo', 'melody', 'main']
            },
            'pad': {
                'primary': ['pad', 'string', 'choir', 'ambient'],
                'secondary': ['atmosphere', 'background', 'wash']
            },
            'pluck': {
                'primary': ['pluck', 'arp', 'seq', 'stab'],
                'secondary': ['short', 'percussive', 'attack']
            },
            'keys': {
                'primary': ['key', 'keys', 'piano', 'organ'],
                'secondary': ['chord', 'harmony']
            },
            'fx': {
                'primary': ['fx', 'riser', 'sweep', 'noise', 'impact'],
                'secondary': ['effect', 'transition', 'build']
            }
        }

        # SOUND CHARACTER DETECTION
        self.character_keywords = {
            'aggressive': ['dirty', 'distorted', 'gritty', 'hard', 'brutal', 'sharp'],
            'smooth': ['smooth', 'warm', 'soft', 'mellow', 'silky', 'gentle'],
            'bright': ['bright', 'crisp', 'clear', 'crystal', 'sharp'],
            'dark': ['dark', 'deep', 'heavy', 'low', 'sub'],
            'evolving': ['wobble', 'lfo', 'sweep', 'morph', 'evolving', 'movement']
        }

        # GENRE DETECTION
        self.genre_keywords = {
            'dubstep': ['dubstep', 'dub', 'step', 'wobble', 'growl', 'drop'],
            'house': ['house', 'tech', 'deep', 'groove', 'club'],
            'trance': ['trance', 'uplifting', 'epic', 'emotional', 'progressive'],
            'dnb': ['dnb', 'jungle', 'break', 'neuro', 'liquid'],
            'trap': ['trap', '808', 'snap', 'drill', 'hip', 'hop'],
            'future': ['future', 'chill', 'ambient', 'wave']
        }

        # PRODUCER/PACK DETECTION (from bracket analysis)
        self.known_producers = {
            'L.U.X', 'GS', 'ASL', 'SN', '7S', 'FN', 'AF', 'CFA',
            'LCV', 'FP', 'BR', 'SD', 'GI', 'SW', 'TI', 'LT', 'ROY'
        }

    def clean_preset_name(self, name):
        """Clean preset name by removing null bytes and extra whitespace"""
        if not name:
            return ""

        # Remove null bytes
        cleaned = name.replace('\x00', '').strip()
        return cleaned

    def extract_prefix(self, name):
        """Extract instrument prefix from preset name"""
        # Pattern 1: "PREFIX - Name" or "PREFIX Name"
        match = re.match(r'^([A-Z]{2,8})\s*[-\s]\s*', name)
        if match:
            return match.group(1)

        # Pattern 2: Just prefix at start
        match = re.match(r'^([A-Z]{2,4})\s+', name)
        if match:
            return match.group(1)

        return None

    def extract_brackets(self, name):
        """Extract producer/pack tags from brackets"""
        brackets = re.findall(r'\[([^\]]+)\]', name)
        return [b.strip() for b in brackets]

    def detect_instrument_from_prefix(self, name):
        """Detect instrument type from prefix with high confidence"""
        prefix = self.extract_prefix(name)
        if prefix and prefix in self.prefix_instrument_map:
            return self.prefix_instrument_map[prefix], 'prefix', 0.95
        return None, None, 0.0

    def detect_instrument_from_keywords(self, name):
        """Detect instrument type from keywords"""
        name_lower = name.lower()
        best_match = None
        best_score = 0.0
        best_method = None

        for instrument, keywords in self.instrument_keywords.items():
            score = 0.0

            # Check primary keywords (higher weight)
            for keyword in keywords['primary']:
                if keyword in name_lower:
                    score += 0.8

            # Check secondary keywords (lower weight)
            for keyword in keywords['secondary']:
                if keyword in name_lower:
                    score += 0.3

            if score > best_score:
                best_score = score
                best_match = instrument
                best_method = 'keywords'

        # Normalize score
        confidence = min(best_score, 1.0)

        return best_match, best_method, confidence

    def detect_sound_character(self, name):
        """Detect sound characteristics"""
        name_lower = name.lower()
        characteristics = []

        for character, keywords in self.character_keywords.items():
            for keyword in keywords:
                if keyword in name_lower:
                    characteristics.append(character)
                    break

        return list(set(characteristics))  # Remove duplicates

    def detect_genre(self, name):
        """Detect genre from name"""
        name_lower = name.lower()

        for genre, keywords in self.genre_keywords.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return genre

        return None

    def detect_producer(self, name):
        """Detect producer/pack from brackets"""
        brackets = self.extract_brackets(name)

        for bracket in brackets:
            if bracket in self.known_producers:
                return bracket

        return None

    def tag_preset(self, preset_data):
        """Tag a single preset with comprehensive analysis"""
        name = self.clean_preset_name(preset_data.get('preset_name', ''))

        if not name:
            return {'error': 'no_name'}

        # Instrument detection (try prefix first, then keywords)
        instrument, method, confidence = self.detect_instrument_from_prefix(name)

        if confidence < 0.7:  # If prefix confidence is low, try keywords
            kw_instrument, kw_method, kw_confidence = self.detect_instrument_from_keywords(name)
            if kw_confidence > confidence:
                instrument, method, confidence = kw_instrument, kw_method, kw_confidence

        # Other detections
        character = self.detect_sound_character(name)
        genre = self.detect_genre(name)
        producer = self.detect_producer(name)

        return {
            'preset_name': name,
            'instrument': {
                'type': instrument,
                'detection_method': method,
                'confidence': confidence
            },
            'sound_character': character,
            'genre': genre,
            'producer': producer,
            'raw_analysis': {
                'prefix': self.extract_prefix(name),
                'brackets': self.extract_brackets(name),
                'has_numbers': any(c.isdigit() for c in name),
                'has_special_chars': any(c in '!@#$%^&*()_+-={}[]|\\:";\'<>?,./' for c in name)
            }
        }

    def batch_tag_presets(self, dataset_path, output_path=None):
        """Tag entire preset dataset"""
        print(f"🏷️  REAL-WORLD PRESET TAGGER")
        print("=" * 50)

        # Load dataset
        with open(dataset_path, 'r') as f:
            dataset = json.load(f)

        print(f"📊 Tagging {len(dataset)} presets...")

        # Tag all presets
        tagged_presets = []
        stats = defaultdict(int)

        for i, preset in enumerate(dataset):
            if i % 1000 == 0:
                print(f"   Processed {i}/{len(dataset)} presets...")

            tags = self.tag_preset(preset)

            # Add tags to original preset data
            preset_with_tags = preset.copy()
            preset_with_tags['tags'] = tags

            tagged_presets.append(preset_with_tags)

            # Update statistics
            if 'error' not in tags:
                instrument_type = tags['instrument']['type']
                if instrument_type:
                    stats[f"instrument_{instrument_type}"] += 1
                    stats[f"method_{tags['instrument']['detection_method']}"] += 1
                else:
                    stats['instrument_unknown'] += 1

                stats['total_tagged'] += 1

                if tags['genre']:
                    stats[f"genre_{tags['genre']}"] += 1

                if tags['sound_character']:
                    for char in tags['sound_character']:
                        stats[f"character_{char}"] += 1

        # Print statistics
        print(f"\n📈 TAGGING STATISTICS")
        print("=" * 50)

        total = len(dataset)
        print(f"Total presets: {total}")
        print(f"Successfully tagged: {stats['total_tagged']}")
        print(f"Success rate: {(stats['total_tagged']/total)*100:.1f}%")

        print(f"\n🎵 INSTRUMENT DISTRIBUTION")
        for key, count in sorted(stats.items()):
            if key.startswith('instrument_') and not key.endswith('_unknown'):
                instrument = key.replace('instrument_', '')
                percentage = (count / stats['total_tagged']) * 100
                print(f"  {instrument:12s}: {count:4d} ({percentage:5.1f}%)")

        print(f"\n🎭 DETECTION METHODS")
        for key, count in sorted(stats.items()):
            if key.startswith('method_'):
                method = key.replace('method_', '')
                percentage = (count / stats['total_tagged']) * 100
                print(f"  {method:12s}: {count:4d} ({percentage:5.1f}%)")

        # Export results
        if output_path is None:
            output_path = 'tagged_preset_dataset.json'

        with open(output_path, 'w') as f:
            json.dump({
                'metadata': {
                    'total_presets': total,
                    'tagged_presets': stats['total_tagged'],
                    'tagging_statistics': dict(stats)
                },
                'presets': tagged_presets
            }, f, indent=2)

        print(f"\n✅ Tagged dataset exported to {output_path}")
        return tagged_presets, dict(stats)

def main():
    """Run real-world preset tagging"""
    tagger = RealWorldPresetTagger()

    dataset_path = 'ultimate_training_dataset/ultimate_serum_dataset_expanded.json'
    output_path = 'tagged_serum_dataset.json'

    tagged_presets, stats = tagger.batch_tag_presets(dataset_path, output_path)

    print(f"\n🎉 TAGGING COMPLETE!")
    print(f"Results: {len(tagged_presets)} presets tagged with real-world accuracy")

if __name__ == "__main__":
    main()