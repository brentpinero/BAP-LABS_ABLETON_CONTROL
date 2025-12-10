#!/usr/bin/env python3
"""
LLM-Powered Q&A Generator for Music Production Training Data
==============================================================
Uses Claude 3.5 Haiku via batch processing to generate high-quality Q&A pairs
from presets, MIDI files, and audio context.

This replaces template-based generation with contextually rich, varied responses
across multiple task types from our multi-task pre-training research.

Usage:
    # Generate from preset database
    python generate_qa_with_llm.py --presets --count 5000

    # Generate from MIDI-preset pairs
    python generate_qa_with_llm.py --midi-pairs --count 1000

    # Generate from documentation (improve existing)
    python generate_qa_with_llm.py --improve-docs

    # Full pipeline with cost estimate first
    python generate_qa_with_llm.py --all --estimate-cost

Environment:
    ANTHROPIC_API_KEY: Your Anthropic API key
"""

import argparse
import asyncio
import json
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class GeneratorConfig:
    """Configuration for Q&A generation."""
    # API Settings
    model: str = "claude-3-5-haiku-latest"  # Cost-effective, fast, capable
    max_tokens: int = 1024
    temperature: float = 0.7  # Some creativity for varied responses

    # Batch Processing
    batch_size: int = 20  # Requests per batch
    concurrent_batches: int = 5  # Parallel batches (respect rate limits)
    retry_attempts: int = 3
    retry_delay: float = 1.0

    # Input Paths
    preset_json: str = "data/ultimate_training_dataset/ultimate_serum_dataset_expanded.json"
    inventory_json: str = "data/sample_pack_inventory.json"
    serum_guide_path: str = "Serum_2_User_Guide_Pro.md"
    ableton_manual_path: str = "live12-manual-en.pdf"

    # Output
    output_dir: str = "data/llm_training/llm_generated"

    # Cost Control
    max_input_tokens_per_call: int = 2000
    cost_per_1k_input: float = 0.001  # Haiku pricing
    cost_per_1k_output: float = 0.005  # Haiku pricing


# =============================================================================
# TASK TYPES (From Multi-Task Pre-Training Research)
# =============================================================================

TASK_TYPES = {
    "sound_description": {
        "description": "Describe the sonic characteristics of a preset",
        "system_prompt": """You are an expert music producer and sound designer.
Describe sounds using professional audio terminology - timbre, texture, harmonic content,
envelope characteristics, spatial qualities, and musical context where this sound would fit.
Be specific but concise (2-4 sentences).""",
        "question_templates": [
            "Describe what this {category} preset sounds like.",
            "What are the sonic characteristics of this {category} sound?",
            "How would you characterize the timbre and texture of this preset?",
            "What kind of sound does this {category} produce?",
        ],
    },

    "parameter_identification": {
        "description": "Identify and explain key parameters in a preset",
        "system_prompt": """You are a Serum synthesis expert who can read preset parameters.
Explain the key settings that define this sound - focus on the 3-5 most important parameters.
Use actual parameter names and values where provided. Be technical but accessible.""",
        "question_templates": [
            "What are the key parameter settings in this preset?",
            "Which parameters are most important for this {category} sound?",
            "Explain the filter and oscillator settings in this preset.",
            "What makes this preset sound the way it does technically?",
        ],
    },

    "sound_modification": {
        "description": "Advice on how to modify or tweak a sound",
        "system_prompt": """You are a sound design mentor helping producers modify presets.
Give specific, actionable advice with exact parameter names and suggested values.
Consider the starting point of the current settings when making recommendations.""",
        "question_templates": [
            "How can I make this {category} sound brighter?",
            "How do I add more movement and modulation to this preset?",
            "How can I make this sound punchier and more aggressive?",
            "How do I make this {category} sound darker and more subdued?",
            "How can I widen the stereo image of this preset?",
            "How do I make the attack sharper on this sound?",
            "How can I add more sustain and body to this preset?",
        ],
    },

    "sound_matching": {
        "description": "How to recreate or match a sound type",
        "system_prompt": """You are a sound design teacher explaining synthesis techniques.
Describe the general approach to creating this type of sound in Serum,
then connect it to the specific settings in this preset. Be educational.""",
        "question_templates": [
            "How do I create a {category} sound like this in Serum?",
            "What synthesis technique is used to make this {category}?",
            "Walk me through recreating this type of sound from scratch.",
            "What's the signal flow to achieve this {category} sound?",
        ],
    },

    "comparison": {
        "description": "Compare preset to typical/standard settings",
        "system_prompt": """You are an experienced producer comparing presets.
Note what makes this preset unique compared to typical {category} sounds.
Be specific about which parameters deviate from standard approaches.""",
        "question_templates": [
            "How does this {category} compare to a typical {category} preset?",
            "What makes this preset unique compared to standard {category} sounds?",
            "Is this a traditional or experimental approach to {category}?",
        ],
    },

    "musical_context": {
        "description": "When/where to use this sound in production",
        "system_prompt": """You are a professional music producer advising on sound selection.
Suggest genres, production contexts, and layering approaches for this sound.
Be specific about BPM ranges, key frequencies, and mix placement.""",
        "question_templates": [
            "What genre or style would this {category} work best in?",
            "How should I layer this {category} in a mix?",
            "What BPM range suits this preset?",
            "Where in the frequency spectrum does this sound sit best?",
        ],
    },

    "midi_awareness": {
        "description": "Questions involving MIDI context (when MIDI is paired)",
        "system_prompt": """You are a producer analyzing how a preset sounds with specific MIDI.
Consider the note patterns, velocity, chord structures, and how the preset's
envelope/modulation settings interact with the MIDI performance.""",
        "question_templates": [
            "How does this preset respond to the MIDI pattern?",
            "What velocity dynamics work well with this {category}?",
            "How do the envelope settings affect this melodic line?",
            "Would this preset work better with sustained or staccato notes?",
        ],
    },

    "troubleshooting": {
        "description": "Diagnosing and fixing sound issues",
        "system_prompt": """You are a technical support expert for Serum.
Provide diagnostic advice and specific solutions for common issues.
Reference actual parameter names and typical problem values.""",
        "question_templates": [
            "Why might this preset sound harsh or piercing?",
            "This {category} sounds muddy - how do I fix it?",
            "The preset has unwanted clicking - what's causing it?",
            "Why does this sound different between DAWs?",
        ],
    },
}


# =============================================================================
# CONTEXT FORMATTERS
# =============================================================================

def format_preset_context(preset: Dict, include_all_params: bool = False) -> str:
    """Format a preset's data into context for the LLM."""

    name = preset.get("preset_name", "Unknown")
    category = preset.get("category", "synth")
    params = preset.get("parameters", {})

    # Select key parameters to include
    key_params = [
        # Oscillator A
        ("a_wtpos", "OSC A Wavetable Position"),
        ("a_unison", "OSC A Unison Voices"),
        ("a_unidet", "OSC A Unison Detune"),
        ("a_pan", "OSC A Pan"),
        ("a_level", "OSC A Level"),

        # Oscillator B
        ("b_wtpos", "OSC B Wavetable Position"),
        ("b_unison", "OSC B Unison Voices"),
        ("b_level", "OSC B Level"),

        # Filter
        ("fil_cutoff_hz", "Filter Cutoff"),
        ("fil_reso", "Filter Resonance"),
        ("fil_type", "Filter Type"),

        # Envelopes
        ("env1_atk_ms", "Amp Env Attack"),
        ("env1_dec_ms", "Amp Env Decay"),
        ("env1_sus", "Amp Env Sustain"),
        ("env1_rel_ms", "Amp Env Release"),

        # LFO
        ("lfo1_rate", "LFO 1 Rate"),
        ("lfo1_shp", "LFO 1 Shape"),

        # Effects
        ("cho_wet", "Chorus Mix"),
        ("del_wet", "Delay Mix"),
        ("rev_wet", "Reverb Mix"),
        ("dist_amt", "Distortion Amount"),
    ]

    context_parts = [
        f"Preset Name: {name}",
        f"Category: {category}",
        "",
        "Key Parameters:",
    ]

    for param_key, param_name in key_params:
        if param_key in params:
            value = params[param_key]
            # Format nicely based on parameter type
            if isinstance(value, float):
                if value < 0.01:
                    formatted = f"{value:.4f}"
                elif value < 1:
                    formatted = f"{value*100:.1f}%"
                else:
                    formatted = f"{value:.2f}"
            else:
                formatted = str(value)
            context_parts.append(f"  {param_name}: {formatted}")

    # Add parameter count summary
    context_parts.append(f"\n(Total parameters in preset: {len(params)})")

    return "\n".join(context_parts)


def format_midi_context(midi_info: Dict) -> str:
    """Format MIDI file information into context."""

    context_parts = [
        "Associated MIDI:",
        f"  Filename: {midi_info.get('filename', 'Unknown')}",
    ]

    # If we have parsed MIDI data
    if "notes" in midi_info:
        context_parts.extend([
            f"  Duration: {midi_info.get('duration_bars', '?')} bars",
            f"  Note count: {midi_info.get('note_count', '?')}",
            f"  Key: {midi_info.get('key', 'Unknown')}",
        ])

    return "\n".join(context_parts)


# =============================================================================
# LLM Q&A GENERATOR
# =============================================================================

class LLMQAGenerator:
    """Generate Q&A pairs using Claude 3.5 Haiku."""

    def __init__(self, config: GeneratorConfig):
        self.config = config

        if not HAS_ANTHROPIC:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=api_key)

        # Statistics
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0
        self.failed_requests = 0

    def generate_single_qa(
        self,
        preset: Dict,
        task_type: str,
        midi_info: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """Generate a single Q&A pair for a preset."""

        task = TASK_TYPES.get(task_type)
        if not task:
            return None

        # Build context
        preset_context = format_preset_context(preset)

        # Add MIDI context if available
        if midi_info and task_type == "midi_awareness":
            midi_context = format_midi_context(midi_info)
            full_context = f"{preset_context}\n\n{midi_context}"
        else:
            full_context = preset_context

        # Select question template
        category = preset.get("category", "synth")
        question_template = random.choice(task["question_templates"])
        question = question_template.format(category=category)

        # Build prompt
        user_prompt = f"""Context about a Serum synthesizer preset:

{full_context}

Question from a music producer:
{question}

Provide a helpful, specific response based on the preset data above."""

        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=task["system_prompt"],
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            # Track usage
            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens
            self.total_requests += 1

            # Extract response text
            answer = response.content[0].text

            return {
                "source": f"llm_generated_{task_type}",
                "task_type": task_type,
                "preset": preset.get("preset_name", "Unknown"),
                "category": preset.get("category", "synth"),
                "user": question,
                "assistant": answer,
                "has_midi": midi_info is not None,
            }

        except Exception as e:
            self.failed_requests += 1
            print(f"    [ERROR] API call failed: {e}")
            return None

    async def generate_batch_async(
        self,
        presets: List[Dict],
        task_types: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Generate Q&A pairs for a batch of presets asynchronously."""

        if task_types is None:
            task_types = list(TASK_TYPES.keys())

        results = []

        # Process in batches
        for i in range(0, len(presets), self.config.batch_size):
            batch = presets[i:i + self.config.batch_size]

            for preset in batch:
                # Random task type for variety
                task_type = random.choice(task_types)

                result = self.generate_single_qa(preset, task_type)
                if result:
                    results.append(result)

                # Small delay to respect rate limits
                await asyncio.sleep(0.1)

            print(f"    Batch {i//self.config.batch_size + 1}: Generated {len(results)} Q&A pairs")

        return results

    def generate_batch(
        self,
        presets: List[Dict],
        task_types: Optional[List[str]] = None,
        count: int = 1000,
    ) -> List[Dict]:
        """Synchronous batch generation wrapper."""

        if task_types is None:
            # Exclude midi_awareness unless we have MIDI data
            task_types = [t for t in TASK_TYPES.keys() if t != "midi_awareness"]

        # Sample presets if we have more than needed
        if len(presets) > count:
            sampled_presets = random.sample(presets, count)
        else:
            # Repeat presets with different task types
            sampled_presets = []
            while len(sampled_presets) < count:
                sampled_presets.extend(presets)
            sampled_presets = sampled_presets[:count]

        results = []

        print(f"  Generating {count} Q&A pairs...")

        for i, preset in enumerate(sampled_presets):
            task_type = random.choice(task_types)

            # Retry logic
            for attempt in range(self.config.retry_attempts):
                result = self.generate_single_qa(preset, task_type)
                if result:
                    results.append(result)
                    break
                else:
                    time.sleep(self.config.retry_delay * (attempt + 1))

            # Progress update
            if (i + 1) % 100 == 0:
                print(f"    Progress: {i + 1}/{count} ({len(results)} successful)")
                print(f"    Tokens: {self.total_input_tokens:,} in / {self.total_output_tokens:,} out")

        return results

    def estimate_cost(self, count: int) -> Tuple[float, int, int]:
        """Estimate API cost for generating Q&A pairs."""

        # Average tokens per request (estimated)
        avg_input_tokens = 800  # Context + question
        avg_output_tokens = 200  # Response

        total_input = count * avg_input_tokens
        total_output = count * avg_output_tokens

        cost = (
            (total_input / 1000) * self.config.cost_per_1k_input +
            (total_output / 1000) * self.config.cost_per_1k_output
        )

        return cost, total_input, total_output

    def get_usage_stats(self) -> Dict:
        """Get current usage statistics."""

        cost = (
            (self.total_input_tokens / 1000) * self.config.cost_per_1k_input +
            (self.total_output_tokens / 1000) * self.config.cost_per_1k_output
        )

        return {
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "estimated_cost_usd": round(cost, 4),
        }


# =============================================================================
# PIPELINE FUNCTIONS
# =============================================================================

def load_presets(config: GeneratorConfig) -> List[Dict]:
    """Load presets from JSON file."""

    preset_path = Path(config.preset_json)
    if not preset_path.exists():
        print(f"[ERROR] Preset file not found: {preset_path}")
        return []

    with open(preset_path, 'r') as f:
        presets = json.load(f)

    print(f"  Loaded {len(presets)} presets from {preset_path}")
    return presets


def load_midi_pairs(config: GeneratorConfig) -> List[Tuple[Dict, Dict]]:
    """Load MIDI-preset pairs from inventory."""

    inventory_path = Path(config.inventory_json)
    if not inventory_path.exists():
        print(f"[INFO] Inventory file not found: {inventory_path}")
        return []

    # The inventory file is too large, let's just get MIDI-preset pairs section
    # For now, return empty - we'll implement this when we have smaller inventory
    print("  [TODO] MIDI pair loading from large inventory")
    return []


def save_results(
    results: List[Dict],
    output_path: Path,
    stats: Dict,
):
    """Save generated Q&A pairs and statistics."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save Q&A pairs
    with open(output_path, 'w') as f:
        for qa in results:
            f.write(json.dumps(qa) + '\n')

    print(f"  Saved {len(results)} Q&A pairs to {output_path}")

    # Save stats
    stats_path = output_path.with_suffix('.stats.json')
    stats["output_file"] = str(output_path)
    stats["timestamp"] = datetime.now().isoformat()
    stats["qa_count"] = len(results)

    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"  Saved stats to {stats_path}")


def estimate_cost_only(config: GeneratorConfig, count: int) -> Tuple[float, int, int]:
    """Estimate API cost without needing API key."""
    # Average tokens per request (estimated)
    avg_input_tokens = 800  # Context + question
    avg_output_tokens = 200  # Response

    total_input = count * avg_input_tokens
    total_output = count * avg_output_tokens

    cost = (
        (total_input / 1000) * config.cost_per_1k_input +
        (total_output / 1000) * config.cost_per_1k_output
    )

    return cost, total_input, total_output


def run_preset_generation(config: GeneratorConfig, count: int, estimate_only: bool = False):
    """Generate Q&A from preset database."""

    print("\n" + "="*60)
    print("LLM Q&A GENERATION: PRESETS")
    print("="*60 + "\n")

    # Load presets
    presets = load_presets(config)
    if not presets:
        return

    # Cost estimate (without needing API)
    cost, input_tokens, output_tokens = estimate_cost_only(config, count)
    print(f"\n  Cost Estimate for {count} Q&A pairs:")
    print(f"    Input tokens: ~{input_tokens:,}")
    print(f"    Output tokens: ~{output_tokens:,}")
    print(f"    Estimated cost: ${cost:.2f} USD")

    if estimate_only:
        print("\n  [ESTIMATE ONLY] - No API calls made")
        return

    # Now we need the API key
    generator = LLMQAGenerator(config)

    # Confirm
    print("\n  Starting generation...")

    # Generate
    results = generator.generate_batch(presets, count=count)

    # Save
    output_path = Path(config.output_dir) / "preset_qa_llm.jsonl"
    stats = generator.get_usage_stats()
    save_results(results, output_path, stats)

    print(f"\n  Final Stats:")
    print(f"    Total requests: {stats['total_requests']}")
    print(f"    Failed requests: {stats['failed_requests']}")
    print(f"    Actual cost: ${stats['estimated_cost_usd']:.4f} USD")


def run_improve_docs(config: GeneratorConfig, estimate_only: bool = False):
    """Improve existing template-based Q&A from documentation."""

    print("\n" + "="*60)
    print("LLM Q&A IMPROVEMENT: DOCUMENTATION")
    print("="*60 + "\n")

    # Load existing template Q&A
    serum_qa_path = Path("data/llm_training/serum_guide_qa.jsonl")
    ableton_qa_path = Path("data/llm_training/ableton_manual_qa.jsonl")

    existing_qa = []

    if serum_qa_path.exists():
        with open(serum_qa_path, 'r') as f:
            for line in f:
                existing_qa.append(json.loads(line))
        print(f"  Loaded {len(existing_qa)} existing Serum Q&A")

    if ableton_qa_path.exists():
        with open(ableton_qa_path, 'r') as f:
            for line in f:
                existing_qa.append(json.loads(line))
        print(f"  Total existing Q&A: {len(existing_qa)}")

    if not existing_qa:
        print("  [ERROR] No existing Q&A found to improve")
        return

    generator = LLMQAGenerator(config)

    # Cost estimate
    cost, _, _ = generator.estimate_cost(len(existing_qa))
    print(f"\n  Cost Estimate: ${cost:.2f} USD for {len(existing_qa)} Q&A pairs")

    if estimate_only:
        print("\n  [ESTIMATE ONLY] - No API calls made")
        return

    print("\n  [TODO] Doc improvement implementation")
    # This would rewrite the answers using LLM while keeping questions


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate high-quality Q&A pairs using Claude 3.5 Haiku"
    )

    # Generation modes
    parser.add_argument('--presets', action='store_true',
                        help='Generate Q&A from preset database')
    parser.add_argument('--midi-pairs', action='store_true',
                        help='Generate Q&A from MIDI-preset pairs')
    parser.add_argument('--improve-docs', action='store_true',
                        help='Improve existing documentation Q&A')
    parser.add_argument('--all', action='store_true',
                        help='Run all generation modes')

    # Parameters
    parser.add_argument('--count', type=int, default=1000,
                        help='Number of Q&A pairs to generate (default: 1000)')
    parser.add_argument('--estimate-cost', action='store_true',
                        help='Only estimate cost, don\'t make API calls')

    # Config overrides
    parser.add_argument('--output-dir', type=str,
                        default='data/llm_training/llm_generated',
                        help='Output directory')
    parser.add_argument('--model', type=str,
                        default='claude-3-5-haiku-latest',
                        help='Claude model to use')

    args = parser.parse_args()

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY") and not args.estimate_cost:
        print("="*60)
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("="*60)
        print("\nTo use this script:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nOr run with --estimate-cost to see pricing without API calls")
        return

    config = GeneratorConfig()
    config.output_dir = args.output_dir
    config.model = args.model

    print("="*60)
    print("LLM-POWERED Q&A GENERATOR")
    print(f"Model: {config.model}")
    print("="*60)

    if args.all:
        args.presets = True
        args.midi_pairs = True
        args.improve_docs = True

    if not any([args.presets, args.midi_pairs, args.improve_docs]):
        parser.print_help()
        return

    if args.presets:
        run_preset_generation(config, args.count, args.estimate_cost)

    if args.improve_docs:
        run_improve_docs(config, args.estimate_cost)

    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
