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

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# MLX imports
try:
    from mlx_lm import load, generate
    from mlx_lm.sample_utils import make_sampler
    import mlx.core as mx
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    print("WARNING: mlx_lm not installed. Run: pip install mlx-lm")

# Anthropic imports for LLM-as-judge (Section D dialogue evaluation)
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("WARNING: anthropic not installed. Run: pip install anthropic")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configurations - MLX community quantized versions
# Updated to focus on best reasoning models based on HuggingFace leaderboard research
MODELS = {
    "qwen3-4b": {
        "repo": "mlx-community/Qwen3-4B-4bit",
        "name": "Qwen3-4B",
        "size_gb": 2.5,
        "description": "Latest Qwen with Thinking Mode - matches 72B performance",
        "thinking_mode": "qwen3",  # Use /think token and enable_thinking
        "sampler_config": {"temp": 0.6, "top_p": 0.95}
    },
    "phi-4-mini-reasoning": {
        "repo": "lmstudio-community/Phi-4-mini-reasoning-MLX-4bit",
        "name": "Phi-4-mini-reasoning",
        "size_gb": 2.4,
        "description": "Microsoft reasoning model - beats 7-8B on math reasoning",
        "thinking_mode": "phi4",  # Use <think>...</think> format
        "sampler_config": {"temp": 0.8, "top_p": 0.95}
    },
    # Legacy models kept for comparison
    "phi-3.5-mini": {
        "repo": "mlx-community/Phi-3.5-mini-instruct-4bit",
        "name": "Phi-3.5-mini-Instruct",
        "size_gb": 2.3,
        "description": "Previous eval winner - strong dialogue",
        "thinking_mode": None,
        "sampler_config": {}  # Use default greedy sampling
    },
    "qwen2.5-3b": {
        "repo": "mlx-community/Qwen2.5-3B-Instruct-4bit",
        "name": "Qwen2.5-3B-Instruct",
        "size_gb": 2.0,
        "description": "Previous eval - good MCQ performance",
        "thinking_mode": None,
        "sampler_config": {}  # Use default greedy sampling
    }
}


class MusicProductionEvaluator:
    """Evaluates LLM music production knowledge."""

    def __init__(self, eval_file: str, output_dir: str, dry_run: bool = False):
        self.eval_file = eval_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dry_run = dry_run

        # Load evaluation questions
        with open(eval_file, 'r') as f:
            self.eval_data = json.load(f)

        self.model = None
        self.tokenizer = None
        self.current_model_name = None

        if self.dry_run:
            logger.info("🧪 DRY RUN MODE - Using mock responses to test pipeline")

    def load_model(self, model_key: str) -> bool:
        """Load a model from MLX community."""
        model_config = MODELS.get(model_key)
        if not model_config:
            logger.error(f"Unknown model: {model_key}")
            return False

        if self.dry_run:
            logger.info(f"[DRY RUN] Would load model: {model_config['name']}")
            logger.info(f"  Repository: {model_config['repo']}")
            logger.info(f"  Expected size: ~{model_config['size_gb']}GB")
            self.current_model_name = model_key
            return True

        if not MLX_AVAILABLE:
            logger.error("MLX not available. Install with: pip install mlx-lm")
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
        if self.dry_run:
            logger.info(f"[DRY RUN] Would unload model: {self.current_model_name}")
            self.current_model_name = None
            return

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

    def _generate_mock_response(self, prompt: str) -> str:
        """Generate a mock response for dry-run testing."""
        import random

        # For MCQ, randomly pick an answer (simulates ~25% baseline)
        if "Answer with just the letter" in prompt:
            return random.choice(["A", "B", "C", "D"])

        # For open-ended, return a plausible-ish response with some keywords
        mock_responses = [
            "To achieve this, you would use an LFO routed to the filter cutoff. Start with a sawtooth oscillator and apply a low-pass filter with moderate resonance. The modulation creates movement in the sound.",
            "This involves balancing the frequency content between elements. Use sidechain compression to create space, and consider EQ cuts in the low-mid range around 200-400Hz to reduce muddiness.",
            "The key is understanding the relationship between transients and sustain. A fast attack on the compressor will catch the transient, while adjusting the release affects the tail of the sound.",
            "Consider using parallel compression to maintain dynamics while adding density. You can also layer sounds at different octaves and use saturation to add harmonics.",
            "I would recommend starting by analyzing the frequency spectrum to identify problem areas. Then use surgical EQ to address specific issues while preserving the overall character.",
        ]
        return random.choice(mock_responses)

    def _apply_thinking_format(self, prompt: str) -> str:
        """Apply thinking mode formatting based on current model."""
        if self.current_model_name is None:
            return prompt

        model_config = MODELS.get(self.current_model_name, {})
        thinking_mode = model_config.get("thinking_mode")

        if thinking_mode == "qwen3":
            # Qwen3: Add /think token to enable thinking mode
            return f"/think\n{prompt}"
        elif thinking_mode == "phi4":
            # Phi-4-reasoning: Add instruction to use <think> format
            thinking_instruction = "Please think through this step-by-step. Structure your response with your reasoning process first, then your final answer.\n\n"
            return f"{thinking_instruction}{prompt}"
        else:
            return prompt

    def _extract_answer_from_thinking(self, response: str) -> Tuple[str, str]:
        """Extract final answer and thinking trace from response.
        Returns (final_answer, thinking_trace)

        Handles both complete <think>...</think> blocks and various model output formats.
        """
        import re

        # Clean up model-specific prefixes (Phi-4 outputs "<|end|><|assistant|>" before thinking)
        cleaned = re.sub(r'^<\|end\|><\|assistant\|>', '', response).strip()

        # Try to extract <think>...</think> blocks (Qwen3 and Phi4 format)
        think_match = re.search(r'<think>(.*?)</think>', cleaned, re.DOTALL)
        if think_match:
            thinking_trace = think_match.group(1).strip()
            # Get content after </think>
            final_answer = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL).strip()
            return (final_answer, thinking_trace)

        # Check for incomplete thinking blocks (model ran out of tokens mid-think)
        incomplete_think = re.search(r'<think>(.*)', cleaned, re.DOTALL)
        if incomplete_think:
            thinking_trace = incomplete_think.group(1).strip()
            # No complete answer yet, return empty answer with the thinking trace
            return ("", thinking_trace)

        # No thinking tags found, return as-is
        return (cleaned, "")

    def generate_response(self, prompt: str, max_tokens: int = 512) -> Tuple[str, float, str]:
        """Generate a response from the current model.
        Returns (response, time_ms, thinking_trace).

        For thinking models, always enables thinking mode so we can measure
        the full thinking + response time as a baseline.
        """
        if self.dry_run:
            # Small delay to simulate inference
            time.sleep(0.05)
            return (self._generate_mock_response(prompt), 50.0, "")

        if self.model is None:
            return ("[ERROR: No model loaded]", 0.0, "")

        # Always apply thinking mode formatting - we want to measure thinking time
        formatted_prompt = self._apply_thinking_format(prompt)

        # Get sampler config for this model (temp, top_p, etc.)
        model_config = MODELS.get(self.current_model_name, {})
        sampler_config = model_config.get("sampler_config", {})

        # Create sampler if config provided, otherwise use default (greedy)
        sampler = make_sampler(**sampler_config) if sampler_config else None

        try:
            start_time = time.perf_counter()
            # Build generation kwargs
            gen_kwargs = {"max_tokens": max_tokens, "verbose": False}
            if sampler is not None:
                gen_kwargs["sampler"] = sampler

            response = generate(
                self.model,
                self.tokenizer,
                prompt=formatted_prompt,
                **gen_kwargs
            )
            inference_time_ms = (time.perf_counter() - start_time) * 1000

            # Extract answer from thinking response if applicable
            final_answer, thinking_trace = self._extract_answer_from_thinking(response)

            # Store thinking trace for later analysis (could be logged or saved)
            if thinking_trace:
                logger.debug(f"Thinking trace captured ({len(thinking_trace)} chars)")

            return (final_answer.strip() if final_answer else response.strip(), inference_time_ms, thinking_trace)
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return (f"[ERROR: {str(e)}]", 0.0, "")

    def format_mcq_prompt(self, question: dict) -> str:
        """Format an MCQ question as a prompt."""
        options_text = "\n".join([
            f"{key}. {val}" for key, val in question['options'].items()
        ])

        prompt = f"""You are a music production assistant. Answer the following multiple choice question by selecting ONLY the letter (A, B, C, or D) of the correct answer.

Question: {question['question']}

{options_text}

Answer with just the letter:"""
        return prompt

    def format_open_ended_prompt(self, question: dict) -> str:
        """Format an open-ended question as a prompt with CoT encouragement."""
        difficulty = question.get('difficulty', 'medium')
        cot_instruction = "Think through this step-by-step. " if difficulty in ['medium', 'hard'] else ""

        prompt = f"""You are a music production expert. {cot_instruction}Provide a detailed, technically accurate answer to the following question.

Question: {question['question']}

Think through your reasoning, then provide your answer:"""
        return prompt

    def format_scenario_prompt(self, scenario: dict) -> str:
        """Format a task-based scenario as a prompt with CoT encouragement."""
        context = scenario.get('context', '')
        context_text = f"\nContext: {context}" if context else ""
        difficulty = scenario.get('difficulty', 'medium')

        prompt = f"""You are a music production assistant helping a producer. Read the scenario carefully.

Scenario: {scenario['scenario']}{context_text}

Think step-by-step:
1. First, identify the core problem
2. Consider possible causes
3. Reason through potential solutions
4. Recommend specific actions

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

    def score_with_llm_judge(self, question: str, response: str, criteria: List[str],
                              reference: str = "", difficulty: str = "medium",
                              eval_type: str = "dialogue") -> Tuple[int, List[str], str, int]:
        """
        Use Claude Sonnet 4.5 as LLM-as-judge for comprehensive evaluation.
        Evaluates both answer correctness AND chain-of-thought reasoning quality.

        Returns (score 0-3, matched_criteria, reasoning, cot_score 0-3)
        """
        if not ANTHROPIC_AVAILABLE:
            logger.warning("Anthropic not available, falling back to keyword scoring")
            score, matched = self.score_scenario(response, criteria)
            return (score, matched, "Fallback to keyword scoring - Anthropic SDK not available", 0)

        if self.dry_run:
            return (2, criteria[:2], "[DRY RUN] Mock LLM judge evaluation", 2)

        # Build the judge prompt
        criteria_text = "\n".join(f"  - {c}" for c in criteria)

        judge_prompt = f"""You are an expert evaluator assessing an AI music production assistant's response.

QUESTION/SETUP:
{question}

AI ASSISTANT'S RESPONSE:
{response}

{"REFERENCE ANSWER:" + chr(10) + reference + chr(10) if reference else ""}
EVALUATION CRITERIA:
{criteria_text}

DIFFICULTY LEVEL: {difficulty}

TASK: Evaluate the response on TWO dimensions:

1. **ANSWER QUALITY** - Does the response correctly address the question/task?
   - For {eval_type} questions: Assess based on criteria above

2. **REASONING QUALITY** - Does the response show good chain-of-thought reasoning?
   - Does it explain WHY, not just WHAT?
   - Does it show logical step-by-step thinking?
   - Does it consider multiple possibilities before concluding?
   - Is the reasoning coherent and well-structured?

Respond in this exact JSON format:
{{
  "answer_score": <0-3>,
  "matched_criteria": [<list of criteria that were MET>],
  "reasoning_score": <0-3>,
  "reasoning_quality": "<assessment of the model's reasoning process>",
  "overall_assessment": "<brief overall evaluation>"
}}

SCORING GUIDE:
- 3: Excellent - Strong performance, thorough reasoning
- 2: Good - Adequate performance, decent reasoning
- 1: Partial - Some correct elements, weak reasoning
- 0: Poor - Incorrect or no meaningful reasoning

For {difficulty.upper()} difficulty, be {"lenient" if difficulty == "easy" else "moderately strict" if difficulty == "medium" else "very strict"} in your evaluation."""

        try:
            client = anthropic.Anthropic()
            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=800,
                messages=[{"role": "user", "content": judge_prompt}]
            )

            # Parse the response
            judge_response = message.content[0].text

            # Extract JSON from response - handle nested objects
            import re
            json_match = re.search(r'\{[\s\S]*\}', judge_response)
            if json_match:
                result = json.loads(json_match.group())
                answer_score = min(3, max(0, int(result.get('answer_score', 0))))
                matched = result.get('matched_criteria', [])
                cot_score = min(3, max(0, int(result.get('reasoning_score', 0))))
                reasoning = result.get('overall_assessment', 'No assessment provided')
                return (answer_score, matched, reasoning, cot_score)
            else:
                logger.warning(f"Could not parse LLM judge response: {judge_response[:200]}")
                return (0, [], f"Parse error: {judge_response[:200]}", 0)

        except Exception as e:
            logger.error(f"LLM judge error: {e}")
            # Fallback to keyword scoring
            score, matched = self.score_scenario(response, criteria)
            return (score, matched, f"LLM judge error, fallback used: {str(e)}", 0)

    # Keep backwards compatibility alias
    def score_dialogue_with_llm(self, setup: str, response: str, criteria: List[str],
                                 expected_behavior: str) -> Tuple[int, List[str], str]:
        """Backwards compatible wrapper for dialogue scoring."""
        score, matched, reasoning, _ = self.score_with_llm_judge(
            question=setup,
            response=response,
            criteria=criteria,
            reference=expected_behavior,
            eval_type="dialogue"
        )
        return (score, matched, reasoning)

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

        total_inference_time = 0.0

        for subsection_key, subsection in subsections.items():
            questions = subsection.get('questions', [])

            for q in questions:
                prompt = self.format_mcq_prompt(q)
                # Give enough tokens for thinking + answer (thinking models need room to reason)
                # Phi-4 is verbose - needs ~500+ tokens to complete thinking and output answer
                response, inference_ms, thinking_trace = self.generate_response(prompt, max_tokens=600)
                total_inference_time += inference_ms
                score, is_correct = self.score_mcq(response, q['correct'])

                results['questions'].append({
                    "id": q['id'],
                    "question": q['question'],
                    "correct_answer": q['correct'],
                    "model_response": response,
                    "thinking_trace": thinking_trace,
                    "thinking_tokens": len(thinking_trace.split()) if thinking_trace else 0,
                    "is_correct": is_correct,
                    "score": score,
                    "inference_time_ms": inference_ms
                })

                results['total_correct'] += score
                results['total_questions'] += 1

                status = "✓" if is_correct else "✗"
                logger.info(f"  {q['id']}: {status} ({inference_ms:.0f}ms)")

        results['total_inference_time_ms'] = total_inference_time
        results['avg_inference_time_ms'] = total_inference_time / results['total_questions'] if results['total_questions'] > 0 else 0
        logger.info(f"Section A: {results['total_correct']}/{results['total_questions']} (avg {results['avg_inference_time_ms']:.0f}ms/question)")
        return results

    def run_section_b(self, use_llm_judge: bool = True) -> Dict:
        """Run Section B: Open-ended applied knowledge.
        Uses LLM-as-judge for comprehensive evaluation including CoT quality."""
        logger.info("Running Section B: Applied Knowledge (Open-Ended)")

        results = {
            "section": "B",
            "name": "Applied Knowledge",
            "questions": [],
            "total_score": 0,
            "max_score": 0,
            "total_cot_score": 0,
            "max_cot_score": 0,
            "scoring_method": "llm_judge" if (use_llm_judge and ANTHROPIC_AVAILABLE) else "keyword"
        }

        section = self.eval_data.get('section_b', {})
        subsections = section.get('subsections', {})

        total_inference_time = 0.0
        question_count = 0

        for subsection_key, subsection in subsections.items():
            questions = subsection.get('questions', [])

            for q in questions:
                prompt = self.format_open_ended_prompt(q)
                response, inference_ms, thinking_trace = self.generate_response(prompt, max_tokens=400)
                total_inference_time += inference_ms
                question_count += 1

                key_concepts = q.get('key_concepts', [])
                difficulty = q.get('difficulty', 'medium')

                if use_llm_judge and ANTHROPIC_AVAILABLE and not self.dry_run:
                    # Use LLM-as-judge for comprehensive evaluation
                    score, matched, reasoning, cot_score = self.score_with_llm_judge(
                        question=q['question'],
                        response=response,
                        criteria=key_concepts,
                        difficulty=difficulty,
                        eval_type="open-ended knowledge"
                    )
                else:
                    # Fall back to keyword matching
                    score, matched = self.score_open_ended(response, key_concepts)
                    reasoning = "Keyword matching (LLM judge not available)"
                    cot_score = 0

                results['questions'].append({
                    "id": q['id'],
                    "question": q['question'],
                    "model_response": response,
                    "thinking_trace": thinking_trace,
                    "key_concepts": key_concepts,
                    "matched_concepts": matched,
                    "score": score,
                    "cot_score": cot_score,
                    "max_score": 3,
                    "llm_judge_reasoning": reasoning,
                    "inference_time_ms": inference_ms
                })

                results['total_score'] += score
                results['max_score'] += 3
                results['total_cot_score'] += cot_score
                results['max_cot_score'] += 3

                logger.info(f"  {q['id']}: {score}/3 ({len(matched)}/{len(key_concepts)} concepts) ({inference_ms:.0f}ms)")

        results['total_inference_time_ms'] = total_inference_time
        results['avg_inference_time_ms'] = total_inference_time / question_count if question_count > 0 else 0
        results['cot_percentage'] = round(results['total_cot_score'] / results['max_cot_score'] * 100, 1) if results['max_cot_score'] > 0 else 0
        logger.info(f"Section B: {results['total_score']}/{results['max_score']} (CoT: {results['total_cot_score']}/{results['max_cot_score']}) (avg {results['avg_inference_time_ms']:.0f}ms/question)")
        return results

    def run_section_c(self, use_llm_judge: bool = True) -> Dict:
        """Run Section C: Task-based scenarios.
        Uses LLM-as-judge for comprehensive evaluation including CoT quality."""
        logger.info("Running Section C: Task-Based Scenarios")

        results = {
            "section": "C",
            "name": "Task-Based Scenarios",
            "scenarios": [],
            "total_score": 0,
            "max_score": 0,
            "total_cot_score": 0,
            "max_cot_score": 0,
            "scoring_method": "llm_judge" if (use_llm_judge and ANTHROPIC_AVAILABLE) else "keyword"
        }

        section = self.eval_data.get('section_c', {})
        subsections = section.get('subsections', {})

        total_inference_time = 0.0
        scenario_count = 0

        for subsection_key, subsection in subsections.items():
            scenarios = subsection.get('scenarios', [])

            for s in scenarios:
                prompt = self.format_scenario_prompt(s)
                response, inference_ms, thinking_trace = self.generate_response(prompt, max_tokens=500)
                total_inference_time += inference_ms
                scenario_count += 1

                criteria = s.get('evaluation_criteria', [])
                difficulty = s.get('difficulty', 'medium')

                if use_llm_judge and ANTHROPIC_AVAILABLE and not self.dry_run:
                    # Use LLM-as-judge for comprehensive evaluation
                    score, matched, reasoning, cot_score = self.score_with_llm_judge(
                        question=s['scenario'],
                        response=response,
                        criteria=criteria,
                        difficulty=difficulty,
                        eval_type="task-based scenario"
                    )
                else:
                    # Fall back to keyword matching
                    score, matched = self.score_scenario(response, criteria)
                    reasoning = "Keyword matching (LLM judge not available)"
                    cot_score = 0

                results['scenarios'].append({
                    "id": s['id'],
                    "scenario": s['scenario'],
                    "model_response": response,
                    "thinking_trace": thinking_trace,
                    "evaluation_criteria": criteria,
                    "matched_criteria": matched,
                    "score": score,
                    "cot_score": cot_score,
                    "max_score": 3,
                    "llm_judge_reasoning": reasoning,
                    "inference_time_ms": inference_ms
                })

                results['total_score'] += score
                results['max_score'] += 3
                results['total_cot_score'] += cot_score
                results['max_cot_score'] += 3

                logger.info(f"  {s['id']}: {score}/3 ({len(matched)}/{len(criteria)} criteria) ({inference_ms:.0f}ms)")

        results['total_inference_time_ms'] = total_inference_time
        results['avg_inference_time_ms'] = total_inference_time / scenario_count if scenario_count > 0 else 0
        results['cot_percentage'] = round(results['total_cot_score'] / results['max_cot_score'] * 100, 1) if results['max_cot_score'] > 0 else 0
        logger.info(f"Section C: {results['total_score']}/{results['max_score']} (CoT: {results['total_cot_score']}/{results['max_cot_score']}) (avg {results['avg_inference_time_ms']:.0f}ms/question)")
        return results

    def run_section_d(self) -> Dict:
        """Run Section D: Collaboration & dialogue using LLM-as-judge."""
        logger.info("Running Section D: Collaboration & Iteration (LLM-as-Judge)")

        results = {
            "section": "D",
            "name": "Collaboration & Iteration",
            "dialogues": [],
            "total_score": 0,
            "max_score": 0,
            "total_cot_score": 0,
            "max_cot_score": 0,
            "scoring_method": "llm_judge" if ANTHROPIC_AVAILABLE else "keyword_fallback"
        }

        section = self.eval_data.get('section_d', {})
        dialogues = section.get('dialogues', [])

        total_inference_time = 0.0
        dialogue_count = 0

        for d in dialogues:
            prompt = self.format_dialogue_prompt(d)
            response, inference_ms, thinking_trace = self.generate_response(prompt, max_tokens=400)
            total_inference_time += inference_ms
            dialogue_count += 1

            criteria = d.get('evaluation_criteria', [])
            setup = d.get('setup', '')
            expected_behavior = d.get('expected_behavior', '')
            difficulty = d.get('difficulty', 'medium')

            # Use LLM-as-judge for behavioral evaluation (includes CoT scoring)
            score, matched, reasoning, cot_score = self.score_with_llm_judge(
                question=setup,
                response=response,
                criteria=criteria,
                reference=expected_behavior,
                difficulty=difficulty,
                eval_type="dialogue"
            )

            results['dialogues'].append({
                "id": d['id'],
                "name": d.get('name', ''),
                "setup": setup,
                "model_response": response,
                "thinking_trace": thinking_trace,
                "evaluation_criteria": criteria,
                "matched_criteria": matched,
                "llm_judge_reasoning": reasoning,
                "score": score,
                "cot_score": cot_score,
                "max_score": 3,
                "inference_time_ms": inference_ms
            })

            results['total_score'] += score
            results['max_score'] += 3
            results['total_cot_score'] += cot_score
            results['max_cot_score'] += 3

            logger.info(f"  {d['id']}: {score}/3 ({len(matched)}/{len(criteria)} criteria) ({inference_ms:.0f}ms)")

        results['total_inference_time_ms'] = total_inference_time
        results['avg_inference_time_ms'] = total_inference_time / dialogue_count if dialogue_count > 0 else 0
        results['cot_percentage'] = round(results['total_cot_score'] / results['max_cot_score'] * 100, 1) if results['max_cot_score'] > 0 else 0
        logger.info(f"Section D: {results['total_score']}/{results['max_score']} (CoT: {results['total_cot_score']}/{results['max_cot_score']}) (avg {results['avg_inference_time_ms']:.0f}ms/question)")
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

        # Calculate totals (answer scores)
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

        # Calculate CoT totals (reasoning quality scores from B, C, D)
        total_cot_score = (
            section_b.get('total_cot_score', 0) +
            section_c.get('total_cot_score', 0) +
            section_d.get('total_cot_score', 0)
        )
        max_cot_score = (
            section_b.get('max_cot_score', 0) +
            section_c.get('max_cot_score', 0) +
            section_d.get('max_cot_score', 0)
        )
        cot_percentage = round(total_cot_score / max_cot_score * 100, 1) if max_cot_score > 0 else 0

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
                "section_d_score": f"{section_d['total_score']}/{section_d['max_score']}",
                # CoT (Chain-of-Thought) reasoning quality scores
                "total_cot_score": total_cot_score,
                "max_cot_score": max_cot_score,
                "cot_percentage": cot_percentage,
                "section_b_cot": f"{section_b.get('total_cot_score', 0)}/{section_b.get('max_cot_score', 0)}",
                "section_c_cot": f"{section_c.get('total_cot_score', 0)}/{section_c.get('max_cot_score', 0)}",
                "section_d_cot": f"{section_d.get('total_cot_score', 0)}/{section_d.get('max_cot_score', 0)}"
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
        logger.info(f"CoT Quality: {total_cot_score}/{max_cot_score} ({cot_percentage}%)")
        logger.info(f"Section A (MCQ): {results['summary']['section_a_score']}")
        logger.info(f"Section B (Open): {results['summary']['section_b_score']} | CoT: {results['summary']['section_b_cot']}")
        logger.info(f"Section C (Task): {results['summary']['section_c_score']} | CoT: {results['summary']['section_c_cot']}")
        logger.info(f"Section D (Dialog): {results['summary']['section_d_score']} | CoT: {results['summary']['section_d_cot']}")
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
                "percentage": summary['percentage'],
                "cot_score": summary.get('total_cot_score', 0),
                "max_cot_score": summary.get('max_cot_score', 0),
                "cot_percentage": summary.get('cot_percentage', 0)
            })

        rankings.sort(key=lambda x: x['percentage'], reverse=True)

        for i, r in enumerate(rankings):
            r['rank'] = i + 1

        return rankings

    def _print_comparison(self, results: Dict):
        """Print a comparison table to console."""
        logger.info("\n" + "="*90)
        logger.info("FINAL MODEL COMPARISON")
        logger.info("="*90)
        logger.info(f"{'Rank':<6}{'Model':<25}{'Answer Score':<18}{'CoT Quality':<18}{'Combined':<12}")
        logger.info("-"*90)

        for r in results.get('ranking', []):
            cot_pct = r.get('cot_percentage', 0)
            cot_score = r.get('cot_score', 0)
            max_cot = r.get('max_cot_score', 0)
            logger.info(
                f"{r['rank']:<6}{r['model']:<25}"
                f"{r['total_score']}/{r['max_score']} ({r['percentage']:.1f}%)    "
                f"{cot_score}/{max_cot} ({cot_pct:.1f}%)    "
                f"{(r['percentage'] + cot_pct) / 2:.1f}%"
            )

        logger.info("="*90)

        # Recommendation
        if results.get('ranking'):
            winner = results['ranking'][0]
            logger.info(f"\n🏆 RECOMMENDED MODEL: {winner['model']}")
            logger.info(f"   Answer Score: {winner['percentage']:.1f}%")
            logger.info(f"   CoT Quality: {winner.get('cot_percentage', 0):.1f}%")
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
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test pipeline with mock responses (no model download)"
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
    evaluator = MusicProductionEvaluator(eval_file, args.output_dir, dry_run=args.dry_run)

    if args.single:
        # Run single model
        evaluator.run_full_eval(args.single)
    else:
        # Run all specified models (or all if none specified)
        evaluator.run_all_models(args.models)


if __name__ == "__main__":
    main()
