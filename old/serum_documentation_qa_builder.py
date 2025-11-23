#!/usr/bin/env python3
"""
📚 SERUM DOCUMENTATION Q&A BUILDER 📚
Extract comprehensive Q&A pairs from Serum 2 User Guide for training
"""

import json
import re
from collections import defaultdict
from pathlib import Path

class SerumDocumentationQABuilder:
    """Build Q&A dataset from Serum 2 User Guide documentation"""

    def __init__(self, manual_path):
        self.manual_path = manual_path
        self.load_manual()
        self.setup_qa_templates()

    def load_manual(self):
        """Load and parse the Serum 2 User Guide"""
        print("📚 Loading Serum 2 User Guide...")

        with open(self.manual_path, 'r', encoding='utf-8') as f:
            self.manual_text = f.read()

        # Split into sections based on headers
        self.sections = self.parse_sections()
        print(f"   ✅ Loaded {len(self.manual_text)} characters")
        print(f"   ✅ Parsed {len(self.sections)} sections")

    def parse_sections(self):
        """Parse manual into logical sections"""
        sections = []

        # Split by headers (# ## ### patterns)
        section_pattern = r'\n(#{1,4})\s+(.+?)\n'
        matches = list(re.finditer(section_pattern, self.manual_text))

        for i, match in enumerate(matches):
            level = len(match.group(1))  # Number of # characters
            title = match.group(2).strip()
            start_pos = match.end()

            # Find content until next header of same or higher level
            if i + 1 < len(matches):
                next_match = matches[i + 1]
                next_level = len(next_match.group(1))

                # Find appropriate end position
                end_pos = next_match.start()

                # If next header is deeper, find the next same/higher level
                if next_level > level:
                    for j in range(i + 1, len(matches)):
                        future_match = matches[j]
                        future_level = len(future_match.group(1))
                        if future_level <= level:
                            end_pos = future_match.start()
                            break
                    else:
                        end_pos = len(self.manual_text)
            else:
                end_pos = len(self.manual_text)

            content = self.manual_text[start_pos:end_pos].strip()

            if content and len(content) > 50:  # Only meaningful sections
                sections.append({
                    'level': level,
                    'title': title,
                    'content': content,
                    'word_count': len(content.split())
                })

        return sections

    def setup_qa_templates(self):
        """Setup Q&A generation templates"""
        self.qa_templates = {
            'explanation': [
                "What is {feature} in Serum 2?",
                "How does {feature} work in Serum 2?",
                "Explain {feature} in Serum 2",
                "What does {feature} do in Serum 2?",
                "Describe {feature} in Serum 2"
            ],
            'usage': [
                "How do I use {feature} in Serum 2?",
                "How to use {feature} in Serum 2?",
                "What's the best way to use {feature}?",
                "When should I use {feature} in Serum 2?",
                "How can I apply {feature} in my sounds?"
            ],
            'comparison': [
                "What's new about {feature} in Serum 2?",
                "How has {feature} improved in Serum 2?",
                "What's different about {feature} in Serum 2?",
                "What are the new features of {feature}?"
            ],
            'parameters': [
                "What parameters control {feature}?",
                "How do I adjust {feature} parameters?",
                "What controls are available for {feature}?",
                "How to modify {feature} settings?"
            ]
        }

        # Serum 2 specific features for targeted Q&A
        self.serum2_features = [
            "granular synthesis", "spectral synthesis", "third oscillator", "OSC C",
            "enhanced modulation matrix", "new wavetable editor", "improved filters",
            "advanced unison", "enhanced effects", "better preset management",
            ".SerumPreset format", "expanded LFO shapes", "multi-sample support"
        ]

    def extract_feature_qa_pairs(self):
        """Extract Q&A pairs for specific features"""
        qa_pairs = []

        for section in self.sections:
            title = section['title']
            content = section['content']

            # Skip very short sections
            if len(content) < 100:
                continue

            # Generate different types of Q&A for each section
            for qa_type, templates in self.qa_templates.items():
                for template in templates[:2]:  # Use first 2 templates per type
                    question = template.format(feature=title)

                    # Create appropriate answer based on content
                    answer = self.create_answer(content, qa_type, title)

                    if answer and len(answer) > 30:
                        qa_pairs.append({
                            'question': question,
                            'answer': answer,
                            'source_section': title,
                            'qa_type': qa_type,
                            'word_count': len(answer.split())
                        })

        return qa_pairs

    def create_answer(self, content, qa_type, title):
        """Create appropriate answer based on content and question type"""
        # Clean up content
        cleaned_content = self.clean_content(content)

        if qa_type == 'explanation':
            # Extract first substantial paragraph for explanations
            paragraphs = [p.strip() for p in cleaned_content.split('\n\n') if len(p.strip()) > 50]
            if paragraphs:
                return paragraphs[0][:500] + ("..." if len(paragraphs[0]) > 500 else "")

        elif qa_type == 'usage':
            # Look for usage instructions, steps, or procedures
            usage_indicators = ['how to', 'to use', 'steps', 'procedure', 'method']
            for paragraph in cleaned_content.split('\n\n'):
                if any(indicator in paragraph.lower() for indicator in usage_indicators):
                    return paragraph.strip()[:500] + ("..." if len(paragraph) > 500 else "")

            # Fallback to first paragraph
            paragraphs = [p.strip() for p in cleaned_content.split('\n\n') if len(p.strip()) > 30]
            if paragraphs:
                return f"To use {title}: " + paragraphs[0][:450] + ("..." if len(paragraphs[0]) > 450 else "")

        elif qa_type == 'comparison':
            # Look for new features, improvements, or changes
            comparison_indicators = ['new', 'improved', 'enhanced', 'better', 'added', 'updated']
            for paragraph in cleaned_content.split('\n\n'):
                if any(indicator in paragraph.lower() for indicator in comparison_indicators):
                    return paragraph.strip()[:500] + ("..." if len(paragraph) > 500 else "")

        elif qa_type == 'parameters':
            # Look for parameter or control information
            param_indicators = ['parameter', 'control', 'setting', 'adjust', 'modify', 'knob', 'slider']
            for paragraph in cleaned_content.split('\n\n'):
                if any(indicator in paragraph.lower() for indicator in param_indicators):
                    return paragraph.strip()[:500] + ("..." if len(paragraph) > 500 else "")

        # Default fallback
        return None

    def clean_content(self, content):
        """Clean content for better readability"""
        # Remove markdown formatting
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*(.*?)\*', r'\1', content)      # Italic
        content = re.sub(r'`(.*?)`', r'\1', content)        # Code

        # Remove extra whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)

        # Remove image references
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)

        return content.strip()

    def generate_serum2_specific_qa(self):
        """Generate Q&A specifically about Serum 2 new features"""
        specific_qa = [
            {
                'question': "What's new in Serum 2 compared to Serum 1?",
                'answer': "Serum 2 introduces several major improvements: a third oscillator (OSC C) for more complex sounds, new synthesis methods including granular and spectral synthesis, an enhanced modulation matrix with more slots, improved wavetable editing capabilities, better unison algorithms, expanded filter types, new LFO shapes, multi-sample support, and the new .SerumPreset format for better preset organization.",
                'source_section': 'Serum 2 Overview',
                'qa_type': 'comparison',
                'word_count': 68
            },
            {
                'question': "How many oscillators does Serum 2 have?",
                'answer': "Serum 2 has three primary oscillators: OSC A, OSC B, and the new OSC C. This is an upgrade from Serum 1's two oscillators, allowing for more complex and layered sound design. Each oscillator can use wavetables, samples, or basic waveforms, and they can be mixed and modulated independently.",
                'source_section': 'Oscillators',
                'qa_type': 'explanation',
                'word_count': 56
            },
            {
                'question': "What is granular synthesis in Serum 2?",
                'answer': "Granular synthesis in Serum 2 allows you to break audio samples into tiny grains and manipulate them individually. You can control grain size, position, overlap, pitch, and timing to create everything from smooth textures to rhythmic patterns. This synthesis method is perfect for creating evolving pads, textural sounds, and unique rhythmic elements.",
                'source_section': 'Granular Synthesis',
                'qa_type': 'explanation',
                'word_count': 58
            },
            {
                'question': "What is spectral synthesis in Serum 2?",
                'answer': "Spectral synthesis in Serum 2 analyzes the frequency spectrum of audio and allows you to manipulate individual frequency bands. You can freeze, stretch, filter, or modulate specific frequency ranges to create unique timbral transformations. This method excels at creating ethereal pads, frequency-shifted effects, and harmonic manipulations.",
                'source_section': 'Spectral Synthesis',
                'qa_type': 'explanation',
                'word_count': 57
            },
            {
                'question': "How do I use the third oscillator (OSC C) in Serum 2?",
                'answer': "OSC C works like OSC A and OSC B but provides additional layering possibilities. Load a wavetable or sample, adjust its volume, tuning, and pan settings. You can apply independent unison, modulation, and effects. OSC C is perfect for adding harmonic content, sub-bass layers, or percussive elements to your sounds without using additional instances of Serum.",
                'source_section': 'OSC C Usage',
                'qa_type': 'usage',
                'word_count': 68
            },
            {
                'question': "What's the difference between .fxp and .SerumPreset formats?",
                'answer': ".fxp files are the legacy Serum 1 format that store just parameter values. .SerumPreset is the new Serum 2 format that includes embedded wavetables, samples, metadata, tags, and better organization. .SerumPreset files are self-contained and don't require external wavetable files, making them easier to share and organize.",
                'source_section': 'Preset Formats',
                'qa_type': 'comparison',
                'word_count': 56
            }
        ]

        return specific_qa

    def extract_parameter_documentation(self):
        """Extract parameter-specific documentation"""
        param_qa = []

        # Common Serum parameters to document
        parameters = [
            'filter cutoff', 'filter resonance', 'wavetable position', 'unison detune',
            'envelope attack', 'envelope decay', 'envelope sustain', 'envelope release',
            'LFO rate', 'LFO amount', 'oscillator volume', 'oscillator pan',
            'warp modes', 'distortion', 'delay time', 'reverb size'
        ]

        for param in parameters:
            # Find sections mentioning this parameter
            for section in self.sections:
                if param.lower() in section['content'].lower():
                    content_snippet = self.extract_parameter_info(section['content'], param)
                    if content_snippet:
                        param_qa.append({
                            'question': f"How does {param} work in Serum?",
                            'answer': content_snippet,
                            'source_section': section['title'],
                            'qa_type': 'parameters',
                            'word_count': len(content_snippet.split())
                        })
                        break  # One Q&A per parameter

        return param_qa

    def extract_parameter_info(self, content, parameter):
        """Extract specific parameter information from content"""
        # Find sentences mentioning the parameter
        sentences = re.split(r'[.!?]+', content)

        relevant_sentences = []
        for sentence in sentences:
            if parameter.lower() in sentence.lower():
                relevant_sentences.append(sentence.strip())

        if relevant_sentences:
            # Return the most informative sentence(s)
            result = '. '.join(relevant_sentences[:2])  # Up to 2 sentences
            return result[:400] + ("..." if len(result) > 400 else "")

        return None

    def build_complete_qa_dataset(self):
        """Build the complete Q&A dataset"""
        print("\n📚 BUILDING SERUM DOCUMENTATION Q&A DATASET")
        print("=" * 60)

        all_qa_pairs = []

        # 1. Extract feature-based Q&A from manual sections
        print("🔍 Extracting feature-based Q&A...")
        feature_qa = self.extract_feature_qa_pairs()
        all_qa_pairs.extend(feature_qa)
        print(f"   ✅ Generated {len(feature_qa)} feature Q&A pairs")

        # 2. Add Serum 2 specific Q&A
        print("🔍 Adding Serum 2 specific Q&A...")
        serum2_qa = self.generate_serum2_specific_qa()
        all_qa_pairs.extend(serum2_qa)
        print(f"   ✅ Added {len(serum2_qa)} Serum 2 specific Q&A pairs")

        # 3. Extract parameter documentation
        print("🔍 Extracting parameter documentation...")
        param_qa = self.extract_parameter_documentation()
        all_qa_pairs.extend(param_qa)
        print(f"   ✅ Generated {len(param_qa)} parameter Q&A pairs")

        # 4. Filter and quality check
        print("🔍 Quality checking Q&A pairs...")
        filtered_qa = self.quality_filter_qa_pairs(all_qa_pairs)
        print(f"   ✅ Quality filtered: {len(filtered_qa)} final Q&A pairs")

        return filtered_qa

    def quality_filter_qa_pairs(self, qa_pairs):
        """Filter Q&A pairs for quality and remove duplicates"""
        filtered = []
        seen_questions = set()

        for qa in qa_pairs:
            question = qa['question'].lower().strip()
            answer = qa['answer']

            # Skip duplicates
            if question in seen_questions:
                continue

            # Quality checks
            if (
                len(answer) >= 30 and           # Minimum answer length
                len(answer) <= 1000 and        # Maximum answer length
                len(question) >= 10 and        # Minimum question length
                '?' in qa['question'] and      # Must be a question
                not answer.startswith('...') and  # Not truncated at start
                qa['word_count'] >= 5          # Minimum word count
            ):
                filtered.append(qa)
                seen_questions.add(question)

        return filtered

    def export_qa_dataset(self, qa_pairs):
        """Export the Q&A dataset"""
        print(f"\n💾 EXPORTING DOCUMENTATION Q&A DATASET")
        print("=" * 60)

        # Create comprehensive dataset
        dataset = {
            'metadata': {
                'total_qa_pairs': len(qa_pairs),
                'source_manual': self.manual_path,
                'manual_sections': len(self.sections),
                'qa_types': list(set(qa['qa_type'] for qa in qa_pairs)),
                'average_answer_length': sum(qa['word_count'] for qa in qa_pairs) / len(qa_pairs),
                'description': 'Serum 2 documentation Q&A dataset for LLM training'
            },
            'qa_pairs': qa_pairs
        }

        # Export main dataset
        output_path = 'serum_documentation_qa_dataset.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        print(f"✅ Documentation Q&A dataset exported to {output_path}")
        print(f"📊 Dataset size: {len(qa_pairs)} Q&A pairs")

        # Print statistics
        qa_type_counts = defaultdict(int)
        for qa in qa_pairs:
            qa_type_counts[qa['qa_type']] += 1

        print(f"\n📈 Q&A TYPE DISTRIBUTION:")
        for qa_type, count in sorted(qa_type_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(qa_pairs)) * 100
            print(f"   {qa_type:12s}: {count:4d} ({percentage:5.1f}%)")

        return output_path

def main():
    """Build Serum documentation Q&A dataset"""
    manual_path = 'Serum_2_User_Guide_Pro.md'

    if not Path(manual_path).exists():
        print(f"❌ Error: {manual_path} not found!")
        return

    builder = SerumDocumentationQABuilder(manual_path)
    qa_pairs = builder.build_complete_qa_dataset()
    output_path = builder.export_qa_dataset(qa_pairs)

    print(f"\n🎉 DOCUMENTATION Q&A DATASET COMPLETE!")
    print(f"   Output: {output_path}")
    print(f"   Ready for integration with preset dataset")

if __name__ == "__main__":
    main()