#!/usr/bin/env python3
"""
Serum Parameter Evaluation Script

Tests LLMs on Serum-specific parameter manipulation knowledge.
Section E: Parameter Identification (MCQ), Parameter Adjustment (Open), Preset Analysis (Scenario)
"""

import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Import from main eval harness
from run_eval import MusicProductionEvaluator, MODELS, logger

class SerumEvaluator(MusicProductionEvaluator):
    """Extended evaluator for Serum-specific questions."""

    def __init__(self, results_dir: str = 'results'):
        # Initialize with Serum eval file
        super().__init__('serum_parameter_eval.json', results_dir)

    def run_section_e1(self) -> Dict:
        """Run Section E1: Serum Parameter MCQ."""
        logger.info("Running Section E1: Parameter Identification (MCQ)")

        results = {
            "section": "E1",
            "name": "Parameter Identification",
            "questions": [],
            "total_correct": 0,
            "total_questions": 0
        }

        questions = self.eval_data.get('section_e1', {}).get('questions', [])
        total_inference_time = 0

        for q in questions:
            prompt = self.format_mcq_prompt(q)
            # Use 600 tokens for thinking models
            response, inference_ms, thinking_trace = self.generate_response(prompt, max_tokens=600)
            total_inference_time += inference_ms
            score, is_correct = self.score_mcq(response, q['correct'])

            results['questions'].append({
                "id": q['id'],
                "question": q['question'],
                "correct_answer": q['correct'],
                "model_response": response,
                "thinking_trace": thinking_trace,
                "is_correct": is_correct,
                "score": score,
                "inference_time_ms": inference_ms
            })

            results['total_correct'] += score
            results['total_questions'] += 1

            status = "✓" if is_correct else "✗"
            logger.info(f"  {q['id']}: {status} ({inference_ms:.0f}ms)")

        avg_time = total_inference_time / len(questions) if questions else 0
        logger.info(f"Section E1: {results['total_correct']}/{results['total_questions']} (avg {avg_time:.0f}ms/question)")

        return results

    def run_section_e2(self) -> Dict:
        """Run Section E2: Parameter Adjustment (Open-ended with LLM judge)."""
        logger.info("Running Section E2: Parameter Adjustment (Open-Ended)")

        results = {
            "section": "E2",
            "name": "Parameter Adjustment",
            "questions": [],
            "total_score": 0,
            "max_score": 0,
            "total_cot_score": 0,
            "max_cot_score": 0
        }

        questions = self.eval_data.get('section_e2', {}).get('questions', [])
        total_inference_time = 0

        for q in questions:
            prompt = f"""You are a professional sound designer specializing in Serum synthesizer.

Question: {q['question']}

Provide a detailed, technical response explaining the specific Serum parameters to adjust and why."""

            response, inference_ms, thinking_trace = self.generate_response(prompt, max_tokens=512)
            total_inference_time += inference_ms

            # Score with LLM judge
            # Convert scoring_criteria dict to reference string for the judge
            reference = "\n".join(f"Score {k}: {v}" for k, v in q['scoring_criteria'].items())
            score, matched, reasoning, cot_score = self.score_with_llm_judge(
                q['question'],
                response,
                q['expected_concepts'],
                reference=reference
            )

            results['questions'].append({
                "id": q['id'],
                "question": q['question'],
                "expected_concepts": q['expected_concepts'],
                "model_response": response,
                "thinking_trace": thinking_trace,
                "score": score,
                "cot_score": cot_score,
                "matched_concepts": matched,
                "llm_judge_reasoning": reasoning,
                "inference_time_ms": inference_ms
            })

            results['total_score'] += score
            results['max_score'] += 3
            results['total_cot_score'] += cot_score
            results['max_cot_score'] += 3

            logger.info(f"  {q['id']}: {score}/3 (CoT: {cot_score}/3) ({inference_ms:.0f}ms)")

        avg_time = total_inference_time / len(questions) if questions else 0
        logger.info(f"Section E2: {results['total_score']}/{results['max_score']} (CoT: {results['total_cot_score']}/{results['max_cot_score']}) (avg {avg_time:.0f}ms/question)")

        return results

    def run_section_e3(self) -> Dict:
        """Run Section E3: Preset Analysis (Scenario with LLM judge)."""
        logger.info("Running Section E3: Preset Analysis (Scenario)")

        results = {
            "section": "E3",
            "name": "Preset Analysis",
            "questions": [],
            "total_score": 0,
            "max_score": 0,
            "total_cot_score": 0,
            "max_cot_score": 0
        }

        questions = self.eval_data.get('section_e3', {}).get('questions', [])
        total_inference_time = 0

        for q in questions:
            scenario = q.get('scenario', '')
            question = q.get('question', '')

            prompt = f"""You are an expert Serum sound designer analyzing a preset configuration.

{scenario}

Question: {question}

Provide a detailed technical analysis explaining the sound design choices and how they work together."""

            response, inference_ms, thinking_trace = self.generate_response(prompt, max_tokens=512)
            total_inference_time += inference_ms

            # Score with LLM judge
            # Convert scoring_criteria dict to reference string for the judge
            reference = "\n".join(f"Score {k}: {v}" for k, v in q['scoring_criteria'].items())
            score, matched, reasoning, cot_score = self.score_with_llm_judge(
                f"{scenario}\n\n{question}",
                response,
                q['expected_concepts'],
                reference=reference
            )

            results['questions'].append({
                "id": q['id'],
                "scenario": scenario,
                "question": question,
                "expected_concepts": q['expected_concepts'],
                "model_response": response,
                "thinking_trace": thinking_trace,
                "score": score,
                "cot_score": cot_score,
                "matched_concepts": matched,
                "llm_judge_reasoning": reasoning,
                "inference_time_ms": inference_ms
            })

            results['total_score'] += score
            results['max_score'] += 3
            results['total_cot_score'] += cot_score
            results['max_cot_score'] += 3

            logger.info(f"  {q['id']}: {score}/3 (CoT: {cot_score}/3) ({inference_ms:.0f}ms)")

        avg_time = total_inference_time / len(questions) if questions else 0
        logger.info(f"Section E3: {results['total_score']}/{results['max_score']} (CoT: {results['total_cot_score']}/{results['max_cot_score']}) (avg {avg_time:.0f}ms/question)")

        return results

    def run_full_serum_eval(self) -> Dict:
        """Run all Serum evaluation sections."""
        start_time = time.time()

        results = {
            "e1": self.run_section_e1(),
            "e2": self.run_section_e2(),
            "e3": self.run_section_e3()
        }

        eval_time = time.time() - start_time

        # Calculate totals
        total_score = (
            results['e1']['total_correct'] +
            results['e2']['total_score'] +
            results['e3']['total_score']
        )
        max_score = (
            results['e1']['total_questions'] +
            results['e2']['max_score'] +
            results['e3']['max_score']
        )

        total_cot = results['e2']['total_cot_score'] + results['e3']['total_cot_score']
        max_cot = results['e2']['max_cot_score'] + results['e3']['max_cot_score']

        return {
            "sections": results,
            "summary": {
                "total_score": total_score,
                "max_score": max_score,
                "percentage": round(total_score / max_score * 100, 1) if max_score > 0 else 0,
                "e1_score": f"{results['e1']['total_correct']}/{results['e1']['total_questions']}",
                "e2_score": f"{results['e2']['total_score']}/{results['e2']['max_score']}",
                "e3_score": f"{results['e3']['total_score']}/{results['e3']['max_score']}",
                "total_cot_score": total_cot,
                "max_cot_score": max_cot,
                "cot_percentage": round(total_cot / max_cot * 100, 1) if max_cot > 0 else 0
            },
            "eval_time_seconds": eval_time
        }


def run_serum_eval(model_keys: List[str] = None):
    """Run Serum evaluation on specified models."""

    evaluator = SerumEvaluator('results')

    if model_keys is None:
        model_keys = ['qwen3-4b']  # Default to our best model

    all_results = {}

    print(f"\n{'='*60}")
    print("SERUM PARAMETER MANIPULATION EVALUATION")
    print(f"Models: {', '.join(model_keys)}")
    print(f"{'='*60}\n")

    for model_key in model_keys:
        print(f"\n--- Evaluating {model_key} ---")

        if not evaluator.load_model(model_key):
            print(f"Failed to load {model_key}, skipping...")
            continue

        results = evaluator.run_full_serum_eval()

        all_results[model_key] = {
            "model": model_key,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

        # Print summary
        summary = results['summary']
        print(f"\n{'='*40}")
        print(f"RESULTS: {model_key}")
        print(f"{'='*40}")
        print(f"Total Score: {summary['total_score']}/{summary['max_score']} ({summary['percentage']}%)")
        print(f"CoT Quality: {summary['total_cot_score']}/{summary['max_cot_score']} ({summary['cot_percentage']}%)")
        print(f"E1 (MCQ): {summary['e1_score']}")
        print(f"E2 (Open): {summary['e2_score']}")
        print(f"E3 (Scenario): {summary['e3_score']}")
        print(f"Eval time: {results['eval_time_seconds']:.1f}s")
        print(f"{'='*40}")

        evaluator.unload_model()

    # Save results
    output_file = Path('results') / f"serum_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    return all_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run Serum parameter evaluation')
    parser.add_argument('--models', nargs='+', default=['qwen3-4b'],
                       help='Models to evaluate (default: qwen3-4b)')

    args = parser.parse_args()
    run_serum_eval(args.models)
