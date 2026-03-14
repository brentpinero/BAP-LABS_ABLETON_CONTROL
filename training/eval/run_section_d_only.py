#!/usr/bin/env python3
"""
Section D Only Re-evaluation Script

Re-runs just Section D (Collaboration & Iteration) with the new LLM-as-judge
scoring method using Claude Haiku 4.5.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from run_eval import MusicProductionEvaluator, MODELS, logger

def run_section_d_only():
    """Run Section D evaluation on all models."""

    evaluator = MusicProductionEvaluator(
        'music_production_eval_v1.json',
        'results'
    )

    all_results = {}

    models_to_test = list(MODELS.keys())

    print(f"\n{'='*60}")
    print("SECTION D RE-EVALUATION WITH LLM-AS-JUDGE")
    print(f"Models: {', '.join(models_to_test)}")
    print(f"{'='*60}\n")

    for model_key in models_to_test:
        print(f"\n--- Loading {model_key} ---")

        if not evaluator.load_model(model_key):
            print(f"Failed to load {model_key}, skipping...")
            continue

        start_time = time.time()

        # Run only Section D
        section_d = evaluator.run_section_d()

        eval_time = time.time() - start_time

        all_results[model_key] = {
            "model": model_key,
            "section_d": section_d,
            "eval_time_seconds": eval_time,
            "timestamp": datetime.now().isoformat()
        }

        print(f"\n{model_key}: {section_d['total_score']}/{section_d['max_score']} ({eval_time:.1f}s)")

        # Show individual dialogue scores
        for d in section_d['dialogues']:
            print(f"  {d['id']}: {d['score']}/3 - {d.get('llm_judge_reasoning', '')[:80]}...")

        # Unload model
        evaluator.unload_model()

    # Save results
    output_file = Path('results') / f"section_d_reeval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'='*60}")
    print("SECTION D RESULTS SUMMARY")
    print(f"{'='*60}")

    # Sort by score
    sorted_results = sorted(
        all_results.items(),
        key=lambda x: x[1]['section_d']['total_score'],
        reverse=True
    )

    for rank, (model, data) in enumerate(sorted_results, 1):
        score = data['section_d']['total_score']
        max_score = data['section_d']['max_score']
        pct = (score / max_score * 100) if max_score > 0 else 0
        print(f"{rank}. {model}: {score}/{max_score} ({pct:.1f}%)")

    print(f"\nResults saved to: {output_file}")

    return all_results

if __name__ == "__main__":
    run_section_d_only()
