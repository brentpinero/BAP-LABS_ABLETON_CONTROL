#!/usr/bin/env python3
"""
Training Data Curation Pipeline
================================
Downloads and processes multiple data sources for training the audio-aware LLM.

Data Sources:
1. External Datasets:
   - NSynth (300k synth notes with annotations)
   - MusicQA (112k Q&A pairs about music)
   - Music-Instruct (60k Q&A pairs about musical attributes)

2. Documentation:
   - Serum 2 User Guide (markdown) -> Q&A pairs
   - Ableton Live 12 Manual (PDF) -> Q&A pairs

3. Our Preset Database:
   - 7,583 Serum presets with parameters
   - Synthetic Q&A generation

Usage:
    # Download all external datasets
    python curate_training_data.py --download-all

    # Parse documentation only
    python curate_training_data.py --parse-docs

    # Generate synthetic Q&A from presets
    python curate_training_data.py --generate-synthetic

    # Full pipeline
    python curate_training_data.py --all
"""

import argparse
import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random

# For PDF parsing
try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

# For HuggingFace datasets
try:
    from datasets import load_dataset
    HAS_DATASETS = True
except ImportError:
    HAS_DATASETS = False


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class DataConfig:
    """Data curation configuration."""
    # Paths
    output_dir: str = "data/llm_training"
    serum_guide_path: str = "Serum_2_User_Guide_Pro.md"
    ableton_manual_path: str = "live12-manual-en.pdf"
    preset_json: str = "data/ultimate_training_dataset/ultimate_serum_dataset_expanded.json"

    # External datasets
    download_nsynth: bool = True
    download_musicqa: bool = True
    download_music_instruct: bool = True

    # Generation settings
    qa_per_section: int = 5  # Q&A pairs to generate per doc section
    synthetic_qa_count: int = 10000  # Synthetic Q&A from presets


# =============================================================================
# EXTERNAL DATASET DOWNLOADERS
# =============================================================================

def download_music_instruct(output_dir: Path) -> int:
    """
    Download Music-Instruct dataset from HuggingFace.
    Contains 60k Q&A pairs about musical attributes.
    """
    if not HAS_DATASETS:
        print("  [SKIP] datasets library not installed. Run: pip install datasets")
        return 0

    print("  Downloading Music-Instruct from HuggingFace...")

    try:
        # Load both versions (use default config, filter by version field if available)
        dataset = load_dataset("m-a-p/Music-Instruct", split="train", trust_remote_code=True)

        output_path = output_dir / "music_instruct.jsonl"
        count = 0

        with open(output_path, 'w') as f:
            for item in dataset:
                qa = {
                    "source": "music_instruct",
                    "user": item.get("question", ""),
                    "assistant": item.get("answer", ""),
                    "audio": None,  # Text-only dataset
                }
                f.write(json.dumps(qa) + '\n')
                count += 1

                if count % 10000 == 0:
                    print(f"    Processed {count} samples...")

        print(f"  Saved {count} Q&A pairs to {output_path}")
        return count

    except Exception as e:
        print(f"  [ERROR] Failed to download Music-Instruct: {e}")
        return 0


def download_musicqa_metadata(output_dir: Path) -> int:
    """
    Download MusicQA dataset metadata (Q&A pairs without audio).
    Full audio is 36GB - we just grab the Q&A JSON files.
    """
    if not HAS_DATASETS:
        print("  [SKIP] datasets library not installed")
        return 0

    print("  Downloading MusicQA metadata from HuggingFace...")

    try:
        # MusicQA has specific splits - use the pre-training one
        dataset = load_dataset(
            "mu-llama/MusicQA",
            split="MusicCaps.Pretraining",
            trust_remote_code=True
        )

        output_path = output_dir / "musicqa.jsonl"
        count = 0

        with open(output_path, 'w') as f:
            for item in dataset:
                qa = {
                    "source": "musicqa",
                    "user": item.get("question", ""),
                    "assistant": item.get("answer", ""),
                    "audio_file": item.get("audio_name", None),
                }
                f.write(json.dumps(qa) + '\n')
                count += 1

                if count % 10000 == 0:
                    print(f"    Processed {count} samples...")

        print(f"  Saved {count} Q&A pairs to {output_path}")
        return count

    except Exception as e:
        print(f"  [ERROR] Failed to download MusicQA: {e}")
        return 0


def download_nsynth_metadata(output_dir: Path) -> int:
    """
    Download NSynth annotations (not the full audio).
    We use this for vocabulary about synth sounds.
    Use TensorFlow datasets which handles NSynth properly.
    """
    print("  Downloading NSynth annotations...")

    try:
        # Try using tensorflow_datasets which handles NSynth natively
        try:
            import tensorflow_datasets as tfds

            # Load just validation set (smaller, ~12k samples)
            dataset = tfds.load('nsynth', split='valid', with_info=False)

            output_path = output_dir / "nsynth_annotations.jsonl"
            count = 0

            with open(output_path, 'w') as f:
                for item in dataset.take(50000):
                    annotation = {
                        "source": "nsynth",
                        "instrument_family": int(item['instrument']['family'].numpy()),
                        "instrument_source": int(item['instrument']['source'].numpy()),
                        "pitch": int(item['pitch'].numpy()),
                        "velocity": int(item['velocity'].numpy()),
                        "qualities": [int(q) for q in item['qualities'].numpy()],
                    }
                    f.write(json.dumps(annotation) + '\n')
                    count += 1

                    if count % 5000 == 0:
                        print(f"    Processed {count} samples...")

            print(f"  Saved {count} annotations to {output_path}")
            return count

        except ImportError:
            # Fallback: download JSON annotations directly
            print("  [INFO] tensorflow_datasets not available, using direct download...")
            import urllib.request
            import gzip

            # NSynth provides a smaller JSON-only file
            url = "https://storage.googleapis.com/magentadata/datasets/nsynth/nsynth-valid.jsonwav.tar.gz"

            print("  [SKIP] Direct download requires manual extraction. Install tensorflow_datasets.")
            return 0

    except Exception as e:
        print(f"  [ERROR] Failed to download NSynth: {e}")
        return 0


# =============================================================================
# DOCUMENTATION PARSERS
# =============================================================================

def parse_serum_guide(guide_path: str, output_dir: Path, qa_per_section: int = 5) -> int:
    """
    Parse Serum 2 User Guide markdown into Q&A pairs.

    Strategy:
    1. Split by ## headers into sections
    2. For each section, generate Q&A pairs about the content
    3. Mix of factual Q&A and "how to" Q&A
    """
    print(f"  Parsing Serum User Guide from {guide_path}...")

    if not Path(guide_path).exists():
        print(f"  [ERROR] File not found: {guide_path}")
        return 0

    with open(guide_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into sections by ## headers
    sections = re.split(r'\n##\s+', content)

    qa_pairs = []

    for section in sections[1:]:  # Skip first (before any header)
        lines = section.strip().split('\n')
        if not lines:
            continue

        title = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()

        # Skip TOC entries (very short bodies)
        if len(body) < 100:
            continue

        # Skip meta sections
        skip_titles = ['Serum 2 User Guide', 'Table of Contents', 'Copyright', 'Manual Version']
        if any(skip in title for skip in skip_titles):
            continue

        # Generate Q&A pairs for this section
        section_qa = generate_serum_qa(title, body)
        qa_pairs.extend(section_qa[:qa_per_section])

    # Save to file
    output_path = output_dir / "serum_guide_qa.jsonl"
    with open(output_path, 'w') as f:
        for qa in qa_pairs:
            f.write(json.dumps(qa) + '\n')

    print(f"  Generated {len(qa_pairs)} Q&A pairs from Serum guide")
    return len(qa_pairs)


def generate_serum_qa(title: str, body: str) -> List[Dict]:
    """
    Generate Q&A pairs from a section of the Serum manual.
    Uses template-based generation (will be enhanced with LLM later).
    """
    qa_pairs = []

    # Clean up body text
    body_clean = re.sub(r'\s+', ' ', body).strip()

    # Truncate very long sections
    if len(body_clean) > 2000:
        body_clean = body_clean[:2000] + "..."

    # Template 1: "What is X?"
    qa_pairs.append({
        "source": "serum_guide",
        "section": title,
        "user": f"What is {title} in Serum?",
        "assistant": body_clean[:500] + ("..." if len(body_clean) > 500 else ""),
    })

    # Template 2: "How do I use X?"
    qa_pairs.append({
        "source": "serum_guide",
        "section": title,
        "user": f"How do I use {title} in Serum?",
        "assistant": body_clean,
    })

    # Template 3: "Explain X"
    qa_pairs.append({
        "source": "serum_guide",
        "section": title,
        "user": f"Explain {title} in Serum synthesizer.",
        "assistant": body_clean,
    })

    # Template 4: Feature-specific if title contains keywords
    if any(kw in title.lower() for kw in ['filter', 'oscillator', 'envelope', 'lfo', 'wavetable']):
        qa_pairs.append({
            "source": "serum_guide",
            "section": title,
            "user": f"How does the {title} affect the sound in Serum?",
            "assistant": body_clean,
        })

    # Template 5: Workflow question
    if any(kw in title.lower() for kw in ['saving', 'loading', 'creating', 'setting']):
        qa_pairs.append({
            "source": "serum_guide",
            "section": title,
            "user": f"What's the workflow for {title.lower()}?",
            "assistant": body_clean,
        })

    return qa_pairs


def parse_ableton_pdf(pdf_path: str, output_dir: Path, qa_per_section: int = 3) -> int:
    """
    Parse Ableton Live 12 manual PDF into Q&A pairs.
    Focuses on relevant sections: Audio, MIDI, Instruments, Effects, Mixing.
    """
    print(f"  Parsing Ableton Live manual from {pdf_path}...")

    if not HAS_PYPDF:
        print("  [SKIP] pypdf not installed. Run: pip install pypdf")
        return 0

    if not Path(pdf_path).exists():
        print(f"  [ERROR] File not found: {pdf_path}")
        return 0

    try:
        reader = pypdf.PdfReader(pdf_path)

        # Relevant chapter keywords
        relevant_keywords = [
            'audio', 'midi', 'instrument', 'synthesizer', 'effect',
            'mixing', 'routing', 'automation', 'modulation', 'filter',
            'envelope', 'sampler', 'wavetable', 'operator', 'analog',
            'compressor', 'eq', 'reverb', 'delay', 'distortion'
        ]

        qa_pairs = []
        current_section = ""
        current_content = []

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue

            # Simple section detection (headings are often in CAPS or numbered)
            lines = text.split('\n')

            for line in lines:
                line = line.strip()

                # Detect potential section headers (short, possibly numbered)
                if len(line) < 100 and len(line) > 3:
                    # Check if relevant
                    if any(kw in line.lower() for kw in relevant_keywords):
                        # Save previous section
                        if current_section and current_content:
                            content = ' '.join(current_content)
                            if len(content) > 100:
                                qa = generate_ableton_qa(current_section, content)
                                qa_pairs.extend(qa[:qa_per_section])

                        current_section = line
                        current_content = []
                    else:
                        current_content.append(line)
                else:
                    current_content.append(line)

            # Progress update
            if (page_num + 1) % 100 == 0:
                print(f"    Processed {page_num + 1}/{len(reader.pages)} pages...")

        # Save final section
        if current_section and current_content:
            content = ' '.join(current_content)
            if len(content) > 100:
                qa = generate_ableton_qa(current_section, content)
                qa_pairs.extend(qa[:qa_per_section])

        # Save to file
        output_path = output_dir / "ableton_manual_qa.jsonl"
        with open(output_path, 'w') as f:
            for qa in qa_pairs:
                f.write(json.dumps(qa) + '\n')

        print(f"  Generated {len(qa_pairs)} Q&A pairs from Ableton manual")
        return len(qa_pairs)

    except Exception as e:
        print(f"  [ERROR] Failed to parse PDF: {e}")
        return 0


def generate_ableton_qa(title: str, body: str) -> List[Dict]:
    """Generate Q&A pairs from Ableton manual section."""
    qa_pairs = []

    body_clean = re.sub(r'\s+', ' ', body).strip()
    if len(body_clean) > 2000:
        body_clean = body_clean[:2000] + "..."

    qa_pairs.append({
        "source": "ableton_manual",
        "section": title,
        "user": f"How does {title} work in Ableton Live?",
        "assistant": body_clean,
    })

    qa_pairs.append({
        "source": "ableton_manual",
        "section": title,
        "user": f"Explain {title} in Ableton Live.",
        "assistant": body_clean,
    })

    return qa_pairs


# =============================================================================
# SYNTHETIC Q&A GENERATION
# =============================================================================

def generate_synthetic_qa(preset_json: str, output_dir: Path, count: int = 10000) -> int:
    """
    Generate synthetic Q&A pairs from our Serum preset database.
    Uses templates based on the task types we researched.
    """
    print(f"  Generating synthetic Q&A from preset database...")

    if not Path(preset_json).exists():
        print(f"  [ERROR] Preset database not found: {preset_json}")
        return 0

    with open(preset_json, 'r') as f:
        presets = json.load(f)

    print(f"  Loaded {len(presets)} presets")

    # Import parameter info
    try:
        from serum_params import LLM_PARAMS, PARAM_DESCRIPTIONS, denormalize_param
    except ImportError:
        print("  [ERROR] Could not import serum_params")
        return 0

    qa_pairs = []

    # Task templates based on our research
    templates = [
        # Category 1: Sound Description (MC style)
        {
            "type": "describe",
            "questions": [
                "Describe what this {category} preset sounds like.",
                "What are the characteristics of this {category} sound?",
                "How would you describe the timbre of this preset?",
            ],
        },
        # Category 2: Parameter Identification (MNA style)
        {
            "type": "identify_param",
            "questions": [
                "What's the filter cutoff frequency on this preset?",
                "How much unison detune is used in this sound?",
                "What are the envelope settings for this preset?",
            ],
        },
        # Category 3: Sound Modification (MQA style)
        {
            "type": "modify",
            "questions": [
                "How do I make this {category} sound brighter?",
                "How can I add more movement to this sound?",
                "How do I make the attack faster on this preset?",
                "How can I make this sound wider in the stereo field?",
            ],
        },
        # Category 4: Sound Matching
        {
            "type": "match",
            "questions": [
                "What parameters create a {category} sound like this?",
                "How do I recreate this type of {category}?",
            ],
        },
        # Category 5: Comparison
        {
            "type": "compare",
            "questions": [
                "What makes this {category} different from a typical {category}?",
                "Compare the filter settings of this preset to standard values.",
            ],
        },
    ]

    for i in range(count):
        preset = random.choice(presets)
        template_group = random.choice(templates)
        question_template = random.choice(template_group["questions"])

        category = preset.get("category", "synth")
        preset_name = preset.get("preset_name", "Unknown")
        params = preset.get("parameters", {})

        question = question_template.format(category=category)

        # Generate answer based on template type
        if template_group["type"] == "describe":
            answer = generate_description_answer(preset_name, category, params)
        elif template_group["type"] == "identify_param":
            answer = generate_param_answer(params)
        elif template_group["type"] == "modify":
            answer = generate_modification_answer(question, params)
        elif template_group["type"] == "match":
            answer = generate_match_answer(category, params)
        elif template_group["type"] == "compare":
            answer = generate_comparison_answer(category, params)
        else:
            answer = f"This is a {category} preset with various parameters configured."

        qa_pairs.append({
            "source": "synthetic_serum",
            "preset": preset_name,
            "category": category,
            "user": question,
            "assistant": answer,
        })

        if (i + 1) % 2000 == 0:
            print(f"    Generated {i + 1}/{count} pairs...")

    # Save to file
    output_path = output_dir / "synthetic_serum_qa.jsonl"
    with open(output_path, 'w') as f:
        for qa in qa_pairs:
            f.write(json.dumps(qa) + '\n')

    print(f"  Generated {len(qa_pairs)} synthetic Q&A pairs")
    return len(qa_pairs)


def generate_description_answer(name: str, category: str, params: Dict) -> str:
    """Generate a descriptive answer about a preset."""

    # Analyze key parameters
    cutoff = params.get("fil_cutoff_hz", 0.5)
    reso = params.get("fil_reso", 0)
    attack = params.get("env1_atk_ms", 0)
    unison = params.get("a_unison", 1)
    detune = params.get("a_unidet", 0)

    brightness = "bright" if cutoff > 0.6 else "dark" if cutoff < 0.3 else "balanced"
    resonance = "resonant" if reso > 0.5 else ""
    attack_desc = "punchy" if attack < 0.1 else "slow" if attack > 0.5 else "moderate"
    width = "wide stereo" if unison > 4 and detune > 0.3 else "focused" if unison <= 2 else "moderate stereo"

    parts = [
        f"This {category} preset has a {brightness}",
        f"{resonance}" if resonance else "",
        f"character with a {attack_desc} attack.",
        f"The sound is {width} in the stereo field.",
    ]

    return " ".join(p for p in parts if p)


def generate_param_answer(params: Dict) -> str:
    """Generate an answer about specific parameter values."""

    answers = []

    if "fil_cutoff_hz" in params:
        # Convert normalized to approximate Hz (Serum range is ~20Hz to 20kHz)
        cutoff_norm = params["fil_cutoff_hz"]
        cutoff_hz = int(20 * (1000 ** cutoff_norm))  # Logarithmic scale approximation
        answers.append(f"Filter cutoff is approximately {cutoff_hz}Hz")

    if "a_unison" in params:
        unison = int(params.get("a_unison", 1) * 15) + 1  # 1-16 range
        answers.append(f"Unison voices: {unison}")

    if "a_unidet" in params:
        detune = params["a_unidet"]
        answers.append(f"Unison detune: {detune*100:.0f}%")

    if "env1_atk_ms" in params:
        attack = params["env1_atk_ms"]
        attack_ms = int(attack * 1000)  # Rough approximation
        answers.append(f"Amp envelope attack: ~{attack_ms}ms")

    return ". ".join(answers) if answers else "Parameter information not available."


def generate_modification_answer(question: str, params: Dict) -> str:
    """Generate an answer about how to modify a sound."""

    if "brighter" in question.lower():
        cutoff = params.get("fil_cutoff_hz", 0.5)
        return f"To make this sound brighter, increase the filter cutoff (fil_cutoff_hz). Currently at {cutoff*100:.0f}%, try raising it to {min(100, cutoff*100 + 20):.0f}%. You can also reduce the filter resonance for a cleaner high end."

    elif "movement" in question.lower():
        return "To add movement, try modulating the wavetable position (a_wtpos) with an LFO. You can also add subtle filter cutoff modulation or use the chorus effect (cho_wet) for shimmer."

    elif "attack" in question.lower():
        attack = params.get("env1_atk_ms", 0.1)
        return f"To get a faster attack, reduce env1_atk_ms. Currently at {attack*100:.0f}%, try setting it close to 0% for instant transients. Also check that the filter envelope (env2_atk_ms) isn't adding extra attack time."

    elif "wider" in question.lower():
        unison = params.get("a_unison", 1)
        detune = params.get("a_unidet", 0)
        return f"For a wider stereo image, increase unison voices (a_unison) to 4-8 and boost the detune amount (a_unidet). Currently using {unison:.0f} voices with {detune*100:.0f}% detune. Also consider adding chorus (cho_wet)."

    return "Adjust the relevant parameters based on the desired change. Check the filter, envelope, and modulation settings."


def generate_match_answer(category: str, params: Dict) -> str:
    """Generate an answer about recreating a sound type."""

    key_params = []

    if params.get("fil_cutoff_hz", 0.5) < 0.4:
        key_params.append("low filter cutoff for warmth")
    if params.get("fil_reso", 0) > 0.4:
        key_params.append("high resonance for character")
    if params.get("a_unison", 0) > 0.3:
        key_params.append("multiple unison voices for thickness")
    if params.get("env1_atk_ms", 0) < 0.1:
        key_params.append("fast attack for punch")

    if key_params:
        return f"This {category} sound is created using: {', '.join(key_params)}. The combination creates the signature character of this preset."

    return f"This {category} uses a combination of oscillator, filter, and modulation settings working together."


def generate_comparison_answer(category: str, params: Dict) -> str:
    """Generate a comparison answer."""

    cutoff = params.get("fil_cutoff_hz", 0.5)
    reso = params.get("fil_reso", 0)

    comparisons = []

    if cutoff < 0.3:
        comparisons.append("darker than typical with a very low filter cutoff")
    elif cutoff > 0.7:
        comparisons.append("brighter than typical with an open filter")

    if reso > 0.6:
        comparisons.append("more resonant than standard")

    if not comparisons:
        comparisons.append("fairly standard settings")

    return f"This {category} preset is {', '.join(comparisons)}."


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run_download_pipeline(config: DataConfig):
    """Download all external datasets."""
    print("\n" + "="*60)
    print("DOWNLOADING EXTERNAL DATASETS")
    print("="*60 + "\n")

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    total = 0

    if config.download_music_instruct:
        total += download_music_instruct(output_dir)

    if config.download_musicqa:
        total += download_musicqa_metadata(output_dir)

    if config.download_nsynth:
        total += download_nsynth_metadata(output_dir)

    print(f"\nTotal external samples: {total}")
    return total


def run_doc_parsing_pipeline(config: DataConfig):
    """Parse documentation into Q&A pairs."""
    print("\n" + "="*60)
    print("PARSING DOCUMENTATION")
    print("="*60 + "\n")

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    total = 0

    # Parse Serum guide
    total += parse_serum_guide(
        config.serum_guide_path,
        output_dir,
        config.qa_per_section
    )

    # Parse Ableton manual
    total += parse_ableton_pdf(
        config.ableton_manual_path,
        output_dir,
        config.qa_per_section
    )

    print(f"\nTotal documentation Q&A pairs: {total}")
    return total


def run_synthetic_pipeline(config: DataConfig):
    """Generate synthetic Q&A from preset database."""
    print("\n" + "="*60)
    print("GENERATING SYNTHETIC Q&A")
    print("="*60 + "\n")

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    total = generate_synthetic_qa(
        config.preset_json,
        output_dir,
        config.synthetic_qa_count
    )

    print(f"\nTotal synthetic Q&A pairs: {total}")
    return total


def merge_all_datasets(config: DataConfig):
    """Merge all datasets into train/val splits."""
    print("\n" + "="*60)
    print("MERGING DATASETS")
    print("="*60 + "\n")

    output_dir = Path(config.output_dir)
    all_samples = []

    # Load all JSONL files
    for jsonl_file in output_dir.glob("*.jsonl"):
        if jsonl_file.name in ["train.jsonl", "val.jsonl"]:
            continue

        with open(jsonl_file, 'r') as f:
            for line in f:
                try:
                    sample = json.loads(line)
                    all_samples.append(sample)
                except:
                    pass

        print(f"  Loaded {jsonl_file.name}")

    # Shuffle
    random.shuffle(all_samples)

    # Split 90/10
    split_idx = int(len(all_samples) * 0.9)
    train_samples = all_samples[:split_idx]
    val_samples = all_samples[split_idx:]

    # Save
    train_path = output_dir / "train.jsonl"
    with open(train_path, 'w') as f:
        for sample in train_samples:
            f.write(json.dumps(sample) + '\n')

    val_path = output_dir / "val.jsonl"
    with open(val_path, 'w') as f:
        for sample in val_samples:
            f.write(json.dumps(sample) + '\n')

    print(f"\n  Train samples: {len(train_samples)}")
    print(f"  Val samples: {len(val_samples)}")
    print(f"\n  Saved to: {train_path}")
    print(f"  Saved to: {val_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Curate training data for audio-aware LLM")

    parser.add_argument('--download-all', action='store_true',
                        help='Download all external datasets')
    parser.add_argument('--parse-docs', action='store_true',
                        help='Parse documentation into Q&A pairs')
    parser.add_argument('--generate-synthetic', action='store_true',
                        help='Generate synthetic Q&A from presets')
    parser.add_argument('--merge', action='store_true',
                        help='Merge all datasets into train/val splits')
    parser.add_argument('--all', action='store_true',
                        help='Run full pipeline')

    # Config overrides
    parser.add_argument('--output-dir', type=str, default='data/llm_training',
                        help='Output directory')
    parser.add_argument('--synthetic-count', type=int, default=10000,
                        help='Number of synthetic Q&A pairs to generate')

    args = parser.parse_args()

    config = DataConfig()
    config.output_dir = args.output_dir
    config.synthetic_qa_count = args.synthetic_count

    if args.all:
        args.download_all = True
        args.parse_docs = True
        args.generate_synthetic = True
        args.merge = True

    if not any([args.download_all, args.parse_docs, args.generate_synthetic, args.merge]):
        parser.print_help()
        return

    print("="*60)
    print("TRAINING DATA CURATION PIPELINE")
    print("="*60)

    if args.download_all:
        run_download_pipeline(config)

    if args.parse_docs:
        run_doc_parsing_pipeline(config)

    if args.generate_synthetic:
        run_synthetic_pipeline(config)

    if args.merge:
        merge_all_datasets(config)

    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
