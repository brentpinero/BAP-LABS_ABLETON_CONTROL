#!/usr/bin/env python3
"""
Section A Only Re-evaluation Script for Phi-4

Re-runs just Section A (MCQ) with increased token limit (600) to allow
Phi-4 to complete its verbose thinking and output answers.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from run_eval import MusicProductionEvaluator, MODELS, logger

def run_section_a_phi4():
    """Run Section A evaluation on Phi-4 only."""

    evaluator = MusicProductionEvaluator(
        'music_production_eval_v1.json',
        'results'
    )

    print(f"\n{'='*60}")
    print("SECTION A RE-EVALUATION FOR PHI-4 (600 token limit)")
    print(f"{'='*60}\n")

    model_key = "phi-4-mini-reasoning"

    print(f"--- Loading {model_key} ---")

    if not evaluator.load_model(model_key):
        print(f"Failed to load {model_key}")
        return None

    start_time = time.time()

    # Run only Section A
    section_a = evaluator.run_section_a()

    eval_time = time.time() - start_time

    result = {
        "model": model_key,
        "section_a": section_a,
        "eval_time_seconds": eval_time,
        "timestamp": datetime.now().isoformat(),
        "max_tokens_used": 600
    }

    print(f"\n{model_key}: {section_a['total_correct']}/{section_a['total_questions']} ({eval_time:.1f}s)")

    # Show individual MCQ results
    correct_count = 0
    for q in section_a['questions']:
        status = "✓" if q['is_correct'] else "✗"
        print(f"  {q['id']}: {status} (thinking: {q.get('thinking_tokens', 0)} tokens)")
        if q['is_correct']:
            correct_count += 1

    # Unload model
    evaluator.unload_model()

    # Save results
    output_file = Path('results') / f"section_a_phi4_reeval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n{'='*60}")
    print("SECTION A RESULTS (PHI-4 with 600 tokens)")
    print(f"{'='*60}")
    print(f"Score: {correct_count}/30 ({correct_count/30*100:.1f}%)")
    print(f"Results saved to: {output_file}")

    return result

if __name__ == "__main__":
    run_section_a_phi4()
