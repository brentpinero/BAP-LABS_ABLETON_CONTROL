#!/usr/bin/env python3
"""
Music Production LLM Evaluation Harness

Tests baseline music production knowledge across 5 small reasoning models
before fine-tuning to determine the best foundation model.

Models tested:
1. Qwen2.5-3B-Instruct (4-bit) - primary candidate
2. DeepSeek-R1-Distill-Qwen-1.5B (4-bit) - dark horse, reasoning-tuned
3. Phi-3.5-mini-Instruct (4-bit) - Microsoft's small reasoning model
4. Qwen2.5-1.5B-Instruct (4-bit) - smallest Qwen option
5. Gemma-2-2B-Instruct (4-bit) - Google's offering

Workflow: download -> test -> save results -> delete -> next model
"""

import json
import os
import re
import shutil
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# MLX imports
try:
    from mlx_lm import load, generate
    import mlx.core as mx
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    print("WARNING: mlx_lm not installed. Run: pip install mlx-lm")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configurations - MLX community quantized versions
MODELS = {
    "qwen2.5-3b": {
        "repo": "mlx-community/Qwen2.5-3B-Instruct-4bit",
        "name": "Qwen2.5-3B-Instruct",
        "size_gb": 2.0,
        "description": "Primary candidate - strong reasoning, fast"
    },
    "deepseek-r1-1.5b": {
        "repo": "mlx-community/DeepSeek-R1-Distill-Qwen-1.5B-4bit",
        "name": "DeepSeek-R1-Distill-Qwen-1.5B",
        "size_gb": 1.0,
        "description": "Dark horse - reasoning distilled from R1"
    },
    "phi-3.5-mini": {
        "repo": "mlx-community/Phi-3.5-mini-instruct-4bit",
        "name": "Phi-3.5-mini-Instruct",
        "size_gb": 2.3,
        "description": "Microsoft reasoning model"
    },
    "qwen2.5-1.5b": {
        "repo": "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
        "name": "Qwen2.5-1.5B-Instruct",
        "size_gb": 1.0,
        "description": "Smallest Qwen - speed test"
    },
    "gemma-2-2b": {
        "repo": "mlx-community/gemma-2-2b-it-4bit",
        "name": "Gemma-2-2B-Instruct",
        "size_gb": 1.5,
        "description": "Google's small model"
    }
}


class MusicProductionEvaluator:
    """Evaluates LLM music production knowledge."""

    def __init__(self, eval_file: str, output_dir: str):
        self.eval_file = eval_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load evaluation questions
        with open(eval_file, 'r') as f:
            self.eval_data = json.load(f)

        self.model = None
        self.tokenizer = None
        self.current_model_name = None

    def load_model(self, model_key: str) -> bool:
        """Load a model from MLX community."""
        if not MLX_AVAILABLE:
            logger.error("MLX not available")
            return False

        model_config = MODELS.get(model_key)
        if not model_config:
            logger.error(f"Unknown model: {model_key}")
            return False

        logger.info(f"Loading model: {model_config['name']}")
        logger.info(f"  Repository: {model_config['repo']}")
        logger.info(f"  Expected size: ~{model_config['size_gb']}GB")

        start_time = time.time()

        try:
            self.model, self.tokenizer = load(model_config['repo'])
            self.current_model_name = model_key

            load_time = time.time() - start_time
            logger.info(f"Model loaded in {load_time:.1f}s")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def unload_model(self):
        """Unload current model to free memory."""
        if self.model is not None:
            logger.info(f"Unloading model: {self.current_model_name}")
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            self.current_model_name = None

            # Clear MLX cache
            if MLX_AVAILABLE:
                mx.metal.clear_cache()

    def generate_response(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate a response from the current model."""
        if self.model is None:
            return "[ERROR: No model loaded]"

        try:
            response = generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                verbose=False
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return f"[ERROR: {str(e)}]"

    def format_mcq_prompt(self, question: dict) -> str:
        """Format an MCQ question as a prompt."""
        options_text = "\n".join([
            f"{key}. {val}" for key, val in question['options'].items()
        ])

        prompt = f"""You are a music production expert. Answer the following multiple choice question by selecting ONLY the letter (A, B, C, or D) of the correct answer.

Question: {question['question']}

{options_text}

Answer with just the letter:"""
        return prompt

    def format_open_ended_prompt(self, question: dict) -> str:
        """Format an open-ended question as a prompt."""
        prompt = f"""You are a music production expert. Provide a detailed, technically accurate answer to the following question.

Question: {question['question']}

Answer:"""
        return prompt

    def format_scenario_prompt(self, scenario: dict) -> str:
        """Format a task-based scenario as a prompt."""
        context = scenario.get('context', '')
        context_text = f"\nContext: {context}" if context else ""

        prompt = f"""You are a music production assistant helping a producer. Read the scenario and provide a complete solution including your diagnosis, reasoning, and specific recommended actions.

Scenario: {scenario['scenario']}{context_text}

Your response:"""
        return prompt

    def format_dialogue_prompt(self, dialogue: dict) -> str:
        """Format a dialogue scenario as a prompt."""
        # For multi-turn dialogues, we'll evaluate the initial response
        setup = dialogue.get('setup', '')

        prompt = f"""You are a music production assistant. A user has said the following to you. Respond appropriately - ask clarifying questions if needed, provide helpful suggestions, and be collaborative.

User: {setup}

Your response:"""
        return prompt

    def score_mcq(self, response: str, correct: str) -> Tuple[int, bool]:
        """Score an MCQ response. Returns (score, is_correct)."""
        # Extract just the letter from response
        response_clean = response.strip().upper()

        # Try to find a single letter answer
        # First check if response starts with the letter
        if response_clean and response_clean[0] in 'ABCD':
            answer = response_clean[0]
        else:
            # Look for patterns like "A.", "A)", "Answer: A", etc.
            match = re.search(r'\b([ABCD])[.\):]|\b([ABCD])\b', response_clean)
            if match:
                answer = match.group(1) or match.group(2)
            else:
                answer = None

        is_correct = answer == correct.upper()
        return (1 if is_correct else 0, is_correct)

    def score_open_ended(self, response: str, key_concepts: List[str]) -> Tuple[int, List[str]]:
        """
        Score open-ended response based on key concept coverage.
        Returns (score 0-3, matched_concepts)
        """
        response_lower = response.lower()
        matched = []

        for concept in key_concepts:
            # Check for concept or related keywords
            concept_words = concept.lower().split()
            # Count how many key words from the concept appear
            matches = sum(1 for word in concept_words if len(word) > 3 and word in response_lower)
            if matches >= len(concept_words) * 0.5:  # At least 50% of words match
                matched.append(concept)

        # Score based on coverage
        coverage = len(matched) / len(key_concepts) if key_concepts else 0

        if coverage >= 0.75:
            score = 3
        elif coverage >= 0.5:
            score = 2
        elif coverage >= 0.25:
            score = 1
        else:
            score = 0

        return (score, matched)

    def score_scenario(self, response: str, criteria: List[str]) -> Tuple[int, List[str]]:
        """
        Score scenario response based on evaluation criteria.
        Returns (score 0-3, matched_criteria)
        """
        response_lower = response.lower()
        matched = []

        for criterion in criteria:
            # Extract key terms from criterion
            key_terms = [word.lower() for word in criterion.split() if len(word) > 4]
            matches = sum(1 for term in key_terms if term in response_lower)
            if matches >= len(key_terms) * 0.4:
                matched.append(criterion)

        coverage = len(matched) / len(criteria) if criteria else 0

        if coverage >= 0.7:
            score = 3
        elif coverage >= 0.5:
            score = 2
        elif coverage >= 0.3:
            score = 1
        else:
            score = 0

        return (score, matched)

    def run_section_a(self) -> Dict:
        """Run Section A: MCQ factual knowledge."""
        logger.info("Running Section A: Factual Knowledge (MCQ)")

        results = {
            "section": "A",
            "name": "Factual Knowledge",
            "questions": [],
            "total_correct": 0,
            "total_questions": 0
        }

        section = self.eval_data.get('section_a', {})
        subsections = section.get('subsections', {})

        for subsection_key, subsection in subsections.items():
            questions = subsection.get('questions', [])

            for q in questions:
                prompt = self.format_mcq_prompt(q)
                response = self.generate_response(prompt, max_tokens=50)
                score, is_correct = self.score_mcq(response, q['correct'])

                results['questions'].append({
                    "id": q['id'],
                    "question": q['question'],
                    "correct_answer": q['correct'],
                    "model_response": response,
                    "is_correct": is_correct,
                    "score": score
                })

                results['total_correct'] += score
                results['total_questions'] += 1

                status = "✓" if is_correct else "✗"
                logger.info(f"  {q['id']}: {status}")

        logger.info(f"Section A: {results['total_correct']}/{results['total_questions']}")
        return results

    def run_section_b(self) -> Dict:
        """Run Section B: Open-ended applied knowledge."""
        logger.info("Running Section B: Applied Knowledge (Open-Ended)")

        results = {
            "section": "B",
            "name": "Applied Knowledge",
            "questions": [],
            "total_score": 0,
            "max_score": 0
        }

        section = self.eval_data.get('section_b', {})
        subsections = section.get('subsections', {})

        for subsection_key, subsection in subsections.items():
            questions = subsection.get('questions', [])

            for q in questions:
                prompt = self.format_open_ended_prompt(q)
                response = self.generate_response(prompt, max_tokens=400)

                key_concepts = q.get('key_concepts', [])
                score, matched = self.score_open_ended(response, key_concepts)

                results['questions'].append({
                    "id": q['id'],
                    "question": q['question'],
                    "model_response": response,
                    "key_concepts": key_concepts,
                    "matched_concepts": matched,
                    "score": score,
                    "max_score": 3
                })

                results['total_score'] += score
                results['max_score'] += 3

                logger.info(f"  {q['id']}: {score}/3 ({len(matched)}/{len(key_concepts)} concepts)")

        logger.info(f"Section B: {results['total_score']}/{results['max_score']}")
        return results

    def run_section_c(self) -> Dict:
        """Run Section C: Task-based scenarios."""
        logger.info("Running Section C: Task-Based Scenarios")

        results = {
            "section": "C",
            "name": "Task-Based Scenarios",
            "scenarios": [],
            "total_score": 0,
            "max_score": 0
        }

        section = self.eval_data.get('section_c', {})
        subsections = section.get('subsections', {})

        for subsection_key, subsection in subsections.items():
            scenarios = subsection.get('scenarios', [])

            for s in scenarios:
                prompt = self.format_scenario_prompt(s)
                response = self.generate_response(prompt, max_tokens=500)

                criteria = s.get('evaluation_criteria', [])
                score, matched = self.score_scenario(response, criteria)

                results['scenarios'].append({
                    "id": s['id'],
                    "scenario": s['scenario'],
                    "model_response": response,
                    "evaluation_criteria": criteria,
                    "matched_criteria": matched,
                    "score": score,
                    "max_score": 3
                })

                results['total_score'] += score
                results['max_score'] += 3

                logger.info(f"  {s['id']}: {score}/3 ({len(matched)}/{len(criteria)} criteria)")

        logger.info(f"Section C: {results['total_score']}/{results['max_score']}")
        return results

    def run_section_d(self) -> Dict:
        """Run Section D: Collaboration & dialogue."""
        logger.info("Running Section D: Collaboration & Iteration")

        results = {
            "section": "D",
            "name": "Collaboration & Iteration",
            "dialogues": [],
            "total_score": 0,
            "max_score": 0
        }

        section = self.eval_data.get('section_d', {})
        dialogues = section.get('dialogues', [])

        for d in dialogues:
            prompt = self.format_dialogue_prompt(d)
            response = self.generate_response(prompt, max_tokens=400)

            criteria = d.get('evaluation_criteria', [])
            score, matched = self.score_scenario(response, criteria)

            results['dialogues'].append({
                "id": d['id'],
                "name": d.get('name', ''),
                "setup": d.get('setup', ''),
                "model_response": response,
                "evaluation_criteria": criteria,
                "matched_criteria": matched,
                "score": score,
                "max_score": 3
            })

            results['total_score'] += score
            results['max_score'] += 3

            logger.info(f"  {d['id']}: {score}/3 ({len(matched)}/{len(criteria)} criteria)")

        logger.info(f"Section D: {results['total_score']}/{results['max_score']}")
        return results

    def run_full_eval(self, model_key: str) -> Optional[Dict]:
        """Run the complete evaluation for a single model."""
        logger.info(f"\n{'='*60}")
        logger.info(f"EVALUATING: {model_key}")
        logger.info(f"{'='*60}\n")

        # Load model
        if not self.load_model(model_key):
            return None

        start_time = time.time()

        # Run all sections
        section_a = self.run_section_a()
        section_b = self.run_section_b()
        section_c = self.run_section_c()
        section_d = self.run_section_d()

        eval_time = time.time() - start_time

        # Calculate totals
        total_score = (
            section_a['total_correct'] +
            section_b['total_score'] +
            section_c['total_score'] +
            section_d['total_score']
        )

        max_score = (
            section_a['total_questions'] +
            section_b['max_score'] +
            section_c['max_score'] +
            section_d['max_score']
        )

        results = {
            "model": model_key,
            "model_info": MODELS[model_key],
            "timestamp": datetime.now().isoformat(),
            "eval_time_seconds": eval_time,
            "summary": {
                "total_score": total_score,
                "max_score": max_score,
                "percentage": round(total_score / max_score * 100, 1) if max_score > 0 else 0,
                "section_a_score": f"{section_a['total_correct']}/{section_a['total_questions']}",
                "section_b_score": f"{section_b['total_score']}/{section_b['max_score']}",
                "section_c_score": f"{section_c['total_score']}/{section_c['max_score']}",
                "section_d_score": f"{section_d['total_score']}/{section_d['max_score']}"
            },
            "sections": {
                "A": section_a,
                "B": section_b,
                "C": section_c,
                "D": section_d
            }
        }

        # Log summary
        logger.info(f"\n{'='*40}")
        logger.info(f"RESULTS: {model_key}")
        logger.info(f"{'='*40}")
        logger.info(f"Total Score: {total_score}/{max_score} ({results['summary']['percentage']}%)")
        logger.info(f"Section A (MCQ): {results['summary']['section_a_score']}")
        logger.info(f"Section B (Open): {results['summary']['section_b_score']}")
        logger.info(f"Section C (Task): {results['summary']['section_c_score']}")
        logger.info(f"Section D (Dialog): {results['summary']['section_d_score']}")
        logger.info(f"Eval time: {eval_time:.1f}s")
        logger.info(f"{'='*40}\n")

        # Save individual results
        output_file = self.output_dir / f"results_{model_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to: {output_file}")

        # Unload model
        self.unload_model()

        return results

    def run_all_models(self, models: List[str] = None) -> Dict:
        """Run evaluation on all specified models."""
        if models is None:
            models = list(MODELS.keys())

        all_results = {
            "eval_version": self.eval_data.get('metadata', {}).get('version', 'unknown'),
            "eval_date": datetime.now().isoformat(),
            "models_tested": len(models),
            "results": {}
        }

        for model_key in models:
            if model_key not in MODELS:
                logger.warning(f"Unknown model: {model_key}, skipping")
                continue

            result = self.run_full_eval(model_key)
            if result:
                all_results['results'][model_key] = result['summary']

        # Generate comparison
        all_results['ranking'] = self._generate_ranking(all_results['results'])

        # Save combined results
        combined_file = self.output_dir / f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(combined_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        logger.info(f"Comparison saved to: {combined_file}")

        # Print comparison table
        self._print_comparison(all_results)

        return all_results

    def _generate_ranking(self, results: Dict) -> List[Dict]:
        """Generate ranked list of models by score."""
        rankings = []
        for model, summary in results.items():
            rankings.append({
                "model": model,
                "total_score": summary['total_score'],
                "max_score": summary['max_score'],
                "percentage": summary['percentage']
            })

        rankings.sort(key=lambda x: x['percentage'], reverse=True)

        for i, r in enumerate(rankings):
            r['rank'] = i + 1

        return rankings

    def _print_comparison(self, results: Dict):
        """Print a comparison table to console."""
        logger.info("\n" + "="*70)
        logger.info("FINAL MODEL COMPARISON")
        logger.info("="*70)
        logger.info(f"{'Rank':<6}{'Model':<25}{'Score':<15}{'Percentage':<12}")
        logger.info("-"*70)

        for r in results.get('ranking', []):
            logger.info(
                f"{r['rank']:<6}{r['model']:<25}"
                f"{r['total_score']}/{r['max_score']:<10}{r['percentage']:.1f}%"
            )

        logger.info("="*70)

        # Recommendation
        if results.get('ranking'):
            winner = results['ranking'][0]
            logger.info(f"\n🏆 RECOMMENDED MODEL: {winner['model']}")
            logger.info(f"   Score: {winner['percentage']:.1f}%")
            logger.info(f"   {MODELS[winner['model']]['description']}")


def main():
    parser = argparse.ArgumentParser(description="Music Production LLM Evaluation")
    parser.add_argument(
        "--eval-file",
        default="music_production_eval_v1.json",
        help="Path to evaluation JSON file"
    )
    parser.add_argument(
        "--output-dir",
        default="./results",
        help="Directory to save results"
    )
    parser.add_argument(
        "--models",
        nargs="+",
        choices=list(MODELS.keys()),
        help="Specific models to test (default: all)"
    )
    parser.add_argument(
        "--single",
        choices=list(MODELS.keys()),
        help="Test a single model only"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models and exit"
    )

    args = parser.parse_args()

    if args.list_models:
        print("\nAvailable Models:")
        print("-" * 60)
        for key, config in MODELS.items():
            print(f"  {key:<20} - {config['description']}")
            print(f"  {'':20}   Repo: {config['repo']}")
            print(f"  {'':20}   Size: ~{config['size_gb']}GB")
            print()
        return

    # Determine eval file path
    eval_file = args.eval_file
    if not os.path.isabs(eval_file):
        # Check in current directory and script directory
        script_dir = Path(__file__).parent
        if (script_dir / eval_file).exists():
            eval_file = str(script_dir / eval_file)

    if not os.path.exists(eval_file):
        logger.error(f"Evaluation file not found: {eval_file}")
        return

    # Initialize evaluator
    evaluator = MusicProductionEvaluator(eval_file, args.output_dir)

    if args.single:
        # Run single model
        evaluator.run_full_eval(args.single)
    else:
        # Run all specified models (or all if none specified)
        evaluator.run_all_models(args.models)


if __name__ == "__main__":
    main()
