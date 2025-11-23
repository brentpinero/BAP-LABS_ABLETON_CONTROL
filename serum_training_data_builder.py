#!/usr/bin/env python3
"""
🎯 SERUM TRAINING DATA BUILDER 🎯
Creates comprehensive training dataset for Hermes-2-Pro fine-tuning
Combines documentation Q&A with preset generation training data
"""

import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any
import hashlib

class SerumTrainingDataBuilder:
    """Builds comprehensive training dataset for Serum LLM fine-tuning"""

    def __init__(self):
        self.qa_pairs = []
        self.preset_training_data = []
        self.stats = {
            'qa_pairs_extracted': 0,
            'preset_samples_created': 0,
            'total_training_examples': 0,
            'documentation_sections': 0,
            'preset_parameter_count': 0
        }

    def extract_qa_from_documentation(self, doc_path: str) -> List[Dict[str, Any]]:
        """Extract Q&A pairs from Serum 2 User Guide"""
        print("📖 EXTRACTING Q&A FROM SERUM 2 USER GUIDE...")
        print("=" * 60)

        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        qa_pairs = []

        # Extract sections and create Q&A pairs
        sections = self._parse_documentation_sections(content)

        for section in sections:
            # Create instructional Q&A pairs
            section_qa = self._create_section_qa_pairs(section)
            qa_pairs.extend(section_qa)

            # Create technical Q&A pairs
            technical_qa = self._create_technical_qa_pairs(section)
            qa_pairs.extend(technical_qa)

        self.stats['qa_pairs_extracted'] = len(qa_pairs)
        self.stats['documentation_sections'] = len(sections)

        print(f"✅ Extracted {len(qa_pairs)} Q&A pairs from {len(sections)} sections")

        return qa_pairs

    def _parse_documentation_sections(self, content: str) -> List[Dict[str, Any]]:
        """Parse documentation into structured sections"""
        sections = []

        # Split by major headings (## or # headers)
        section_pattern = r'^(#{1,3})\s+(.+?)(?=\n#{1,3}|\Z)'
        matches = re.finditer(section_pattern, content, re.MULTILINE | re.DOTALL)

        for match in matches:
            header_level = len(match.group(1))
            title = match.group(2).strip()
            content_text = match.group(0).strip()

            # Skip very short sections or table of contents
            if len(content_text) < 100 or "Table of Contents" in title:
                continue

            sections.append({
                'title': title,
                'level': header_level,
                'content': content_text,
                'subsections': self._extract_subsections(content_text)
            })

        return sections

    def _extract_subsections(self, section_content: str) -> List[str]:
        """Extract subsections from a main section"""
        # Find bullet points, numbered lists, and sub-headings
        subsection_patterns = [
            r'•\s+(.+?)(?=\n•|\n\n|\Z)',
            r'\d+\.\s+(.+?)(?=\n\d+\.|\n\n|\Z)',
            r'^\s*([A-Z][^.!?]*[.!?])\s*$'
        ]

        subsections = []
        for pattern in subsection_patterns:
            matches = re.findall(pattern, section_content, re.MULTILINE)
            subsections.extend(matches)

        return [sub.strip() for sub in subsections if len(sub.strip()) > 20]

    def _create_section_qa_pairs(self, section: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create Q&A pairs from a documentation section"""
        qa_pairs = []
        title = section['title']
        content = section['content']

        # Generate different types of questions for each section

        # 1. "How to" questions
        if any(word in title.lower() for word in ['using', 'setting', 'exploring', 'loading']):
            qa_pairs.append({
                'system': "You are an expert Serum synthesizer user providing detailed guidance.",
                'human': f"How do I {title.lower().replace('using', 'use').replace('setting', 'set').replace('exploring', 'explore').replace('loading', 'load')}?",
                'assistant': self._create_instructional_answer(content)
            })

        # 2. "What is" questions
        qa_pairs.append({
            'system': "You are an expert Serum synthesizer user providing detailed explanations.",
            'human': f"What is {title.lower()} in Serum?",
            'assistant': self._create_explanatory_answer(content)
        })

        # 3. Feature-specific questions
        if 'oscillator' in title.lower():
            qa_pairs.append({
                'system': "You are an expert Serum synthesizer user providing detailed guidance.",
                'human': f"How do oscillators work in Serum and how can I use them effectively?",
                'assistant': self._create_detailed_answer(content)
            })

        # 4. Troubleshooting questions
        if any(word in content.lower() for word in ['error', 'problem', 'note:', 'important:', 'warning']):
            qa_pairs.append({
                'system': "You are an expert Serum synthesizer user providing troubleshooting help.",
                'human': f"What should I know about potential issues with {title.lower()}?",
                'assistant': self._extract_warnings_and_notes(content)
            })

        return qa_pairs

    def _create_technical_qa_pairs(self, section: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create technical Q&A pairs from section content"""
        qa_pairs = []
        content = section['content']

        # Extract technical details and parameters
        technical_terms = re.findall(r'\b([A-Z]{2,}|[A-Z][a-z]+\s[A-Z][a-z]+)\b', content)

        for term in set(technical_terms[:3]):  # Limit to avoid too many
            if len(term) > 2 and term not in ['MIDI', 'DAW', 'VST']:
                qa_pairs.append({
                    'system': "You are an expert Serum synthesizer user providing technical explanations.",
                    'human': f"Can you explain the {term} parameter in Serum?",
                    'assistant': self._extract_parameter_explanation(content, term)
                })

        return qa_pairs

    def _create_instructional_answer(self, content: str) -> str:
        """Create instructional answer from content"""
        # Clean up content and focus on actionable steps
        cleaned = re.sub(r'##+\s*', '', content)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        # Extract step-by-step instructions
        steps = re.findall(r'(?:^\d+\.|•)\s+(.+?)(?=\n(?:\d+\.|•)|\n\n|\Z)', cleaned, re.MULTILINE | re.DOTALL)

        if steps:
            answer = "Here's how to do this in Serum:\n\n"
            for i, step in enumerate(steps[:5], 1):  # Limit to 5 steps
                answer += f"{i}. {step.strip()}\n"
            return answer
        else:
            # Return first few sentences if no clear steps
            sentences = re.split(r'[.!?]+', cleaned)
            return '. '.join(sentences[:3]).strip() + '.'

    def _create_explanatory_answer(self, content: str) -> str:
        """Create explanatory answer from content"""
        cleaned = re.sub(r'##+\s*', '', content)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        # Extract first paragraph or key explanation
        paragraphs = [p.strip() for p in cleaned.split('\n\n') if len(p.strip()) > 50]

        if paragraphs:
            return paragraphs[0][:500] + ('...' if len(paragraphs[0]) > 500 else '')
        else:
            return "This is a feature in Serum that allows you to control various aspects of sound synthesis."

    def _create_detailed_answer(self, content: str) -> str:
        """Create detailed technical answer"""
        cleaned = re.sub(r'##+\s*', '', content)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        # Extract key information and combine
        paragraphs = [p.strip() for p in cleaned.split('\n\n') if len(p.strip()) > 30]

        if len(paragraphs) >= 2:
            return f"{paragraphs[0]}\n\n{paragraphs[1]}"[:800]
        elif paragraphs:
            return paragraphs[0][:600]
        else:
            return "This is an advanced feature in Serum that provides comprehensive control over sound synthesis parameters."

    def _extract_warnings_and_notes(self, content: str) -> str:
        """Extract important notes and warnings"""
        notes = re.findall(r'(?:Note:|Important:|Warning:)\s*(.+?)(?=\n\n|\Z)', content, re.DOTALL | re.IGNORECASE)

        if notes:
            answer = "Here are important things to note:\n\n"
            for note in notes[:3]:
                answer += f"• {note.strip()}\n"
            return answer
        else:
            return "Be sure to follow the standard Serum workflow when using this feature."

    def _extract_parameter_explanation(self, content: str, parameter: str) -> str:
        """Extract explanation for a specific parameter"""
        # Look for sentences containing the parameter
        sentences = re.split(r'[.!?]+', content)
        relevant_sentences = [s for s in sentences if parameter.lower() in s.lower()]

        if relevant_sentences:
            return relevant_sentences[0].strip() + '.'
        else:
            return f"The {parameter} parameter in Serum controls specific aspects of sound synthesis. Refer to the manual for detailed information."

    def load_preset_dataset(self, dataset_path: str) -> List[Dict[str, Any]]:
        """Load the preset parameter dataset"""
        print("\n🎛️  LOADING PRESET PARAMETER DATASET...")
        print("=" * 60)

        with open(dataset_path, 'r') as f:
            preset_data = json.load(f)

        print(f"✅ Loaded {len(preset_data)} presets")

        return preset_data

    def create_preset_training_examples(self, preset_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create training examples from preset data"""
        print("\n🎯 CREATING PRESET TRAINING EXAMPLES...")
        print("=" * 60)

        training_examples = []

        for i, preset in enumerate(preset_data):
            if i % 500 == 0:
                print(f"   Processing preset {i+1}/{len(preset_data)}")

            # Create different types of preset-related training examples

            # 1. Preset description and parameters
            if 'parameters' in preset and 'preset_name' in preset:
                training_examples.append({
                    'system': "You are an expert Serum sound designer who can generate detailed preset parameters.",
                    'human': f"Create Serum preset parameters for a sound called '{preset['preset_name']}'",
                    'assistant': self._format_preset_parameters(preset)
                })

            # 2. Parameter modification requests
            key_params = self._extract_key_parameters(preset)
            if key_params:
                training_examples.append({
                    'system': "You are an expert Serum sound designer who can modify preset parameters.",
                    'human': f"How would you modify the '{preset['preset_name']}' preset to make it brighter?",
                    'assistant': self._create_modification_suggestion(preset, 'brighter')
                })

            # 3. Sound analysis
            if len(training_examples) % 3 == 0:  # Every 3rd preset
                training_examples.append({
                    'system': "You are an expert Serum sound designer who can analyze presets.",
                    'human': f"Analyze the sound characteristics of this Serum preset: {preset['preset_name']}",
                    'assistant': self._analyze_preset_characteristics(preset)
                })

        self.stats['preset_samples_created'] = len(training_examples)

        print(f"✅ Created {len(training_examples)} preset training examples")

        return training_examples

    def _format_preset_parameters(self, preset: Dict[str, Any]) -> str:
        """Format preset parameters for training"""
        if 'parameters' not in preset:
            return "No parameters available for this preset."

        params = preset['parameters']
        key_params = {}

        # Focus on most important parameters
        important_param_groups = [
            'OSC', 'FILTER', 'ENV', 'LFO', 'UNISON', 'DETUNE', 'CUTOFF', 'RESONANCE'
        ]

        for param_name, value in params.items():
            for group in important_param_groups:
                if group in param_name.upper():
                    key_params[param_name] = value
                    break

        # If we have key parameters, format them
        if key_params:
            result = f"Here are the key parameters for '{preset['preset_name']}':\n\n"
            for param, value in list(key_params.items())[:10]:  # Limit to 10
                if isinstance(value, (int, float)):
                    result += f"• {param}: {value:.3f}\n"
                else:
                    result += f"• {param}: {value}\n"
            return result
        else:
            return f"This preset contains {len(params)} parameters configured for the '{preset['preset_name']}' sound."

    def _extract_key_parameters(self, preset: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the most important parameters from a preset"""
        if 'parameters' not in preset:
            return {}

        params = preset['parameters']
        key_params = {}

        # Look for high-impact parameters
        important_keywords = [
            'OSC_A', 'OSC_B', 'FILTER_1', 'FILTER_2', 'ENV_1', 'ENV_2', 'LFO_1', 'LFO_2'
        ]

        for param_name, value in params.items():
            for keyword in important_keywords:
                if keyword in param_name:
                    key_params[param_name] = value
                    break

        return key_params

    def _create_modification_suggestion(self, preset: Dict[str, Any], modification: str) -> str:
        """Create parameter modification suggestions"""
        suggestions = {
            'brighter': [
                "Increase the filter cutoff frequency",
                "Add some high-frequency resonance",
                "Boost the high-frequency content with EQ",
                "Reduce low-pass filtering"
            ],
            'darker': [
                "Lower the filter cutoff frequency",
                "Add low-pass filtering",
                "Reduce high-frequency content"
            ],
            'wider': [
                "Increase stereo spread",
                "Add chorus or reverb",
                "Pan oscillators left and right",
                "Use stereo unison"
            ]
        }

        if modification in suggestions:
            mods = suggestions[modification]
            return f"To make '{preset['preset_name']}' {modification}, you could:\n\n" + \
                   '\n'.join([f"• {mod}" for mod in mods[:3]])
        else:
            return f"To modify '{preset['preset_name']}', consider adjusting the filter, oscillator, and envelope parameters."

    def _analyze_preset_characteristics(self, preset: Dict[str, Any]) -> str:
        """Analyze preset characteristics based on parameters"""
        if 'parameters' not in preset:
            return f"'{preset['preset_name']}' is a Serum preset with custom parameter configuration."

        params = preset['parameters']
        characteristics = []

        # Analyze key parameter ranges to infer characteristics
        if any('FILTER' in p and isinstance(v, (int, float)) and v > 0.7 for p, v in params.items()):
            characteristics.append("bright, open sound")

        if any('UNISON' in p and isinstance(v, (int, float)) and v > 0.5 for p, v in params.items()):
            characteristics.append("wide, chorused texture")

        if any('ENV' in p and 'ATTACK' in p and isinstance(v, (int, float)) and v > 0.5 for p, v in params.items()):
            characteristics.append("slow attack, pad-like")

        if any('LFO' in p and isinstance(v, (int, float)) and v > 0.3 for p, v in params.items()):
            characteristics.append("modulated, evolving")

        if characteristics:
            return f"'{preset['preset_name']}' appears to be a {', '.join(characteristics)} preset based on its parameter configuration."
        else:
            return f"'{preset['preset_name']}' is a Serum preset with {len(params)} configured parameters for sound synthesis."

    def combine_training_data(self, qa_pairs: List[Dict[str, Any]],
                            preset_examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine documentation and preset training data"""
        print("\n🔗 COMBINING TRAINING DATASETS...")
        print("=" * 60)

        # Format all examples for Hermes-2-Pro
        combined_data = []

        # Add documentation Q&A
        for qa in qa_pairs:
            combined_data.append({
                'conversations': [
                    {'from': 'system', 'value': qa['system']},
                    {'from': 'human', 'value': qa['human']},
                    {'from': 'gpt', 'value': qa['assistant']}
                ],
                'source': 'serum_documentation'
            })

        # Add preset examples
        for example in preset_examples:
            combined_data.append({
                'conversations': [
                    {'from': 'system', 'value': example['system']},
                    {'from': 'human', 'value': example['human']},
                    {'from': 'gpt', 'value': example['assistant']}
                ],
                'source': 'serum_presets'
            })

        self.stats['total_training_examples'] = len(combined_data)

        print(f"✅ Combined {len(qa_pairs)} documentation Q&A + {len(preset_examples)} preset examples")
        print(f"📊 Total training examples: {len(combined_data)}")

        return combined_data

    def save_training_dataset(self, training_data: List[Dict[str, Any]],
                            output_dir: str) -> Dict[str, Any]:
        """Save the final training dataset"""
        print("\n💾 SAVING TRAINING DATASET...")
        print("=" * 60)

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Save main training dataset
        dataset_file = output_path / "serum_hermes_training_dataset.json"
        with open(dataset_file, 'w') as f:
            json.dump(training_data, f, indent=2)

        # Create dataset statistics
        doc_examples = len([d for d in training_data if d['source'] == 'serum_documentation'])
        preset_examples = len([d for d in training_data if d['source'] == 'serum_presets'])

        dataset_stats = {
            'dataset_summary': {
                'total_examples': len(training_data),
                'documentation_examples': doc_examples,
                'preset_examples': preset_examples,
                'creation_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'format': 'hermes_2_pro_chat'
            },
            'statistics': self.stats,
            'example_distribution': {
                'documentation_percentage': (doc_examples / len(training_data)) * 100,
                'preset_percentage': (preset_examples / len(training_data)) * 100
            }
        }

        # Save statistics
        stats_file = output_path / "training_dataset_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(dataset_stats, f, indent=2)

        # Save sample examples
        sample_file = output_path / "training_examples_sample.json"
        sample_data = training_data[:10]  # First 10 examples
        with open(sample_file, 'w') as f:
            json.dump(sample_data, f, indent=2)

        print(f"✅ Training dataset saved: {dataset_file}")
        print(f"📊 Statistics saved: {stats_file}")
        print(f"🔍 Sample examples: {sample_file}")
        print(f"💾 Dataset size: {dataset_file.stat().st_size/1024/1024:.1f} MB")

        return dataset_stats

def main():
    """Build the complete Serum training dataset"""
    print("🎯🎯🎯 SERUM TRAINING DATA BUILDER 🎯🎯🎯")
    print("=" * 70)

    builder = SerumTrainingDataBuilder()

    # Extract Q&A from documentation
    doc_path = "/Users/brentpinero/Documents/serum_llm_2/Serum_2_User_Guide_Pro.md"
    qa_pairs = builder.extract_qa_from_documentation(doc_path)

    # Load preset dataset
    preset_dataset_path = "/Users/brentpinero/Documents/serum_llm_2/ultimate_training_dataset/ultimate_serum_dataset_expanded.json"
    preset_data = builder.load_preset_dataset(preset_dataset_path)

    # Create preset training examples
    preset_examples = builder.create_preset_training_examples(preset_data)

    # Combine all training data
    training_data = builder.combine_training_data(qa_pairs, preset_examples)

    # Save final dataset
    output_dir = "/Users/brentpinero/Documents/serum_llm_2/hermes_training_dataset"
    final_stats = builder.save_training_dataset(training_data, output_dir)

    print(f"\n🎉 SERUM TRAINING DATASET COMPLETE!")
    print("=" * 70)
    print(f"📚 Documentation examples: {final_stats['dataset_summary']['documentation_examples']:,}")
    print(f"🎛️  Preset examples: {final_stats['dataset_summary']['preset_examples']:,}")
    print(f"📊 Total training examples: {final_stats['dataset_summary']['total_examples']:,}")
    print(f"🧠 Ready for Hermes-2-Pro fine-tuning!")

if __name__ == "__main__":
    main()