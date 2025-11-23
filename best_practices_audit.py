#!/usr/bin/env python3
"""
Best Practices Audit for LLM Fine-tuning Dataset
Checks against industry standards for instruction fine-tuning
"""

import json
import re
from collections import Counter, defaultdict
import numpy as np

DATASET = "data/serum_gpt5_mistral_897_CORRECTED_hermes_training.jsonl"

class BestPracticesAuditor:
    def __init__(self):
        self.concerns = defaultdict(list)
        self.warnings = defaultdict(list)
        self.stats = defaultdict(int)

    def extract_instruction(self, text: str) -> str:
        match = re.search(r'<\|im_start\|>user\n(.*?)<\|im_end\|>', text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def extract_response(self, text: str) -> str:
        match = re.search(r'<\|im_start\|>assistant\n(.*?)<\|im_end\|>', text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def audit_dataset(self, dataset_path: str):
        print("🔍 LLM Fine-tuning Best Practices Audit")
        print("="*80 + "\n")

        examples = []
        instructions = []
        responses = []
        instruction_lengths = []
        response_lengths = []

        with open(dataset_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                entry = json.loads(line.strip())
                text = entry['text']

                instruction = self.extract_instruction(text)
                response = self.extract_response(text)

                examples.append((line_num, instruction, response))
                instructions.append(instruction)
                responses.append(response)
                instruction_lengths.append(len(instruction))
                response_lengths.append(len(response))

        self.stats['total_examples'] = len(examples)

        # Best Practice Checks
        self.check_dataset_size(len(examples))
        self.check_instruction_diversity(instructions)
        self.check_instruction_quality(instructions, examples)
        self.check_response_consistency(responses, examples)
        self.check_length_distributions(instruction_lengths, response_lengths)
        self.check_response_format_consistency(responses)
        self.check_for_data_leakage(instructions, responses)
        self.check_balance_and_coverage(instructions)

        return self.generate_report()

    def check_dataset_size(self, size: int):
        """Check if dataset size is appropriate"""
        print("📊 Dataset Size Check")
        print("-"*80)

        if size < 500:
            self.concerns['dataset_size'].append(
                f"Dataset has only {size} examples. Best practice: 500-10000+ for instruction tuning"
            )
            print(f"❌ CONCERN: Only {size} examples (recommended: 500-10000+)")
        elif size < 1000:
            self.warnings['dataset_size'].append(
                f"Dataset has {size} examples. Consider expanding to 1000+ for better generalization"
            )
            print(f"⚠️  WARNING: {size} examples (good, but 1000+ is better)")
        else:
            print(f"✅ GOOD: {size} examples")

        self.stats['dataset_size'] = size
        print()

    def check_instruction_diversity(self, instructions: list):
        """Check instruction diversity"""
        print("🎨 Instruction Diversity Check")
        print("-"*80)

        # Check for exact duplicates
        instruction_counts = Counter(instructions)
        duplicates = {inst: count for inst, count in instruction_counts.items() if count > 1}

        if duplicates:
            self.concerns['duplicates'].append(f"Found {len(duplicates)} duplicate instructions")
            print(f"❌ CONCERN: {len(duplicates)} duplicate instructions found")
            for inst, count in list(duplicates.items())[:5]:
                print(f"   '{inst[:60]}...' appears {count} times")
        else:
            print(f"✅ GOOD: All instructions are unique")

        # Check vocabulary diversity
        all_words = []
        for inst in instructions:
            all_words.extend(inst.lower().split())

        unique_words = len(set(all_words))
        total_words = len(all_words)
        vocab_diversity = unique_words / total_words if total_words > 0 else 0

        print(f"   Vocabulary diversity: {vocab_diversity:.2%}")
        if vocab_diversity < 0.3:
            self.warnings['vocab_diversity'].append(
                f"Low vocabulary diversity ({vocab_diversity:.2%}). Consider more varied instructions"
            )
            print(f"⚠️  WARNING: Low vocabulary diversity")
        else:
            print(f"✅ GOOD: Healthy vocabulary diversity")

        self.stats['unique_instructions'] = len(set(instructions))
        self.stats['vocab_diversity'] = vocab_diversity
        print()

    def check_instruction_quality(self, instructions: list, examples: list):
        """Check instruction quality"""
        print("📝 Instruction Quality Check")
        print("-"*80)

        too_short = []
        too_long = []
        unclear = []

        for line_num, inst, _ in examples:
            # Too short
            if len(inst) < 10:
                too_short.append((line_num, inst))

            # Too long
            if len(inst) > 200:
                too_long.append((line_num, inst))

            # Check for unclear instructions (no verbs, no context)
            if not any(word in inst.lower() for word in ['bass', 'lead', 'pad', 'pluck', 'arp', 'sound', 'synth']):
                unclear.append((line_num, inst))

        if too_short:
            self.warnings['too_short_instructions'].extend(too_short[:5])
            print(f"⚠️  WARNING: {len(too_short)} instructions under 10 chars")

        if too_long:
            self.warnings['too_long_instructions'].extend(too_long[:5])
            print(f"⚠️  WARNING: {len(too_long)} instructions over 200 chars")

        if unclear:
            self.warnings['unclear_instructions'].extend(unclear[:5])
            print(f"⚠️  WARNING: {len(unclear)} instructions may lack clear context")

        if not too_short and not too_long:
            print(f"✅ GOOD: Instruction lengths are appropriate")

        self.stats['too_short'] = len(too_short)
        self.stats['too_long'] = len(too_long)
        print()

    def check_response_consistency(self, responses: list, examples: list):
        """Check response format consistency"""
        print("🔧 Response Format Consistency Check")
        print("-"*80)

        malformed = []
        param_count_variations = []

        for line_num, _, resp in examples:
            try:
                resp_obj = json.loads(resp)

                # Check required fields
                if 'parameter_changes' not in resp_obj:
                    malformed.append((line_num, "Missing parameter_changes"))
                    continue

                param_count = len(resp_obj['parameter_changes'])
                param_count_variations.append(param_count)

            except json.JSONDecodeError:
                malformed.append((line_num, "Invalid JSON"))

        if malformed:
            self.concerns['malformed_responses'].extend(malformed[:5])
            print(f"❌ CONCERN: {len(malformed)} malformed responses")
        else:
            print(f"✅ GOOD: All responses are valid JSON")

        # Check parameter count consistency
        if param_count_variations:
            unique_counts = set(param_count_variations)
            if len(unique_counts) > 1:
                count_dist = Counter(param_count_variations)
                self.warnings['param_count_variation'].append(
                    f"Parameter counts vary: {dict(count_dist)}"
                )
                print(f"⚠️  WARNING: Parameter counts vary: {dict(count_dist)}")
            else:
                print(f"✅ GOOD: All responses have {param_count_variations[0]} parameters")

        self.stats['malformed_responses'] = len(malformed)
        print()

    def check_length_distributions(self, inst_lengths: list, resp_lengths: list):
        """Check length distributions"""
        print("📏 Length Distribution Check")
        print("-"*80)

        inst_mean = np.mean(inst_lengths)
        inst_std = np.std(inst_lengths)
        resp_mean = np.mean(resp_lengths)
        resp_std = np.std(resp_lengths)

        print(f"Instruction lengths: {inst_mean:.1f} ± {inst_std:.1f} chars")
        print(f"Response lengths:    {resp_mean:.1f} ± {resp_std:.1f} chars")

        # Check for extreme outliers
        inst_outliers = sum(1 for l in inst_lengths if l > inst_mean + 3*inst_std or l < inst_mean - 3*inst_std)
        resp_outliers = sum(1 for l in resp_lengths if l > resp_mean + 3*resp_std or l < resp_mean - 3*resp_std)

        if inst_outliers > len(inst_lengths) * 0.05:
            self.warnings['length_outliers'].append(f"{inst_outliers} instruction length outliers")
            print(f"⚠️  WARNING: {inst_outliers} instruction length outliers")

        if resp_outliers > len(resp_lengths) * 0.05:
            self.warnings['length_outliers'].append(f"{resp_outliers} response length outliers")
            print(f"⚠️  WARNING: {resp_outliers} response length outliers")

        if inst_outliers <= len(inst_lengths) * 0.05 and resp_outliers <= len(resp_lengths) * 0.05:
            print(f"✅ GOOD: Length distributions are normal")

        print()

    def check_response_format_consistency(self, responses: list):
        """Check that all responses follow the same JSON schema"""
        print("🔍 Response Schema Consistency Check")
        print("-"*80)

        schemas = []
        for resp in responses:
            try:
                resp_obj = json.loads(resp)
                schema = set(resp_obj.keys())
                schemas.append(schema)
            except:
                continue

        if schemas:
            # Check if all schemas are identical
            first_schema = schemas[0]
            inconsistent = [i for i, s in enumerate(schemas) if s != first_schema]

            if inconsistent:
                self.concerns['schema_inconsistency'].append(
                    f"{len(inconsistent)} responses have different schemas"
                )
                print(f"❌ CONCERN: {len(inconsistent)} responses have different schemas")

                # Show variations
                schema_variations = Counter([frozenset(s) for s in schemas])
                print(f"   Schema variations: {len(schema_variations)}")
            else:
                print(f"✅ GOOD: All responses follow identical schema")
                print(f"   Schema keys: {sorted(first_schema)}")

        print()

    def check_for_data_leakage(self, instructions: list, responses: list):
        """Check for potential data leakage"""
        print("🔒 Data Leakage Check")
        print("-"*80)

        leakage_found = []

        for idx, (inst, resp) in enumerate(zip(instructions, responses)):
            # Check if instruction appears in response (shouldn't for our use case)
            if len(inst) > 20 and inst.lower() in resp.lower():
                leakage_found.append(idx)

        if leakage_found:
            self.warnings['potential_leakage'].append(
                f"{len(leakage_found)} examples may have instruction->response leakage"
            )
            print(f"⚠️  WARNING: {len(leakage_found)} potential leakage cases")
        else:
            print(f"✅ GOOD: No obvious data leakage detected")

        print()

    def check_balance_and_coverage(self, instructions: list):
        """Check for balanced coverage of different sound types"""
        print("⚖️  Balance and Coverage Check")
        print("-"*80)

        categories = {
            'bass': 0,
            'lead': 0,
            'pad': 0,
            'pluck': 0,
            'arp': 0,
            'fx': 0,
            'stab': 0,
            'chord': 0
        }

        for inst in instructions:
            inst_lower = inst.lower()
            for category in categories.keys():
                if category in inst_lower:
                    categories[category] += 1

        total_categorized = sum(categories.values())
        uncategorized = len(instructions) - total_categorized

        print(f"Sound Type Coverage:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(instructions)) * 100
            print(f"  {cat:10s} {count:>4d} ({pct:>5.1f}%)")

        if uncategorized > len(instructions) * 0.2:
            self.warnings['coverage'].append(
                f"{uncategorized} instructions don't match common categories"
            )
            print(f"\n⚠️  WARNING: {uncategorized} uncategorized instructions")

        # Check for extreme imbalance
        if categories:
            max_cat = max(categories.values())
            min_cat = min(v for v in categories.values() if v > 0) if any(v > 0 for v in categories.values()) else 0

            if min_cat > 0 and max_cat / min_cat > 10:
                self.warnings['imbalance'].append(
                    f"Category imbalance detected (ratio: {max_cat/min_cat:.1f}:1)"
                )
                print(f"⚠️  WARNING: Significant category imbalance")
            else:
                print(f"\n✅ GOOD: Reasonable category distribution")

        print()

    def generate_report(self):
        """Generate final best practices report"""
        return {
            'concerns': dict(self.concerns),
            'warnings': dict(self.warnings),
            'stats': dict(self.stats)
        }

def print_final_verdict(report: dict):
    """Print final best practices verdict"""
    print("\n" + "="*80)
    print("🎯 BEST PRACTICES FINAL VERDICT")
    print("="*80 + "\n")

    concerns = report['concerns']
    warnings = report['warnings']

    concern_count = sum(len(v) if isinstance(v, list) else 1 for v in concerns.values())
    warning_count = sum(len(v) if isinstance(v, list) else 1 for v in warnings.values())

    print(f"Critical Concerns: {concern_count}")
    print(f"Warnings:          {warning_count}")
    print()

    if concern_count == 0 and warning_count == 0:
        print("🏆 EXCELLENT: Dataset follows all best practices!")
        verdict = "PRODUCTION READY"
        status = "🏆"
    elif concern_count == 0 and warning_count <= 5:
        print("🌟 VERY GOOD: Minor warnings, but dataset is solid")
        verdict = "PRODUCTION READY WITH NOTES"
        status = "🌟"
    elif concern_count <= 2:
        print("✅ GOOD: Some concerns to address, but usable")
        verdict = "USABLE WITH CAVEATS"
        status = "✅"
    else:
        print("⚠️  NEEDS WORK: Multiple concerns detected")
        verdict = "NEEDS IMPROVEMENT"
        status = "⚠️"

    print(f"\n{status} Final Verdict: {verdict}\n")

    # Recommendations
    print("📋 RECOMMENDATIONS")
    print("-"*80)

    if concern_count == 0 and warning_count == 0:
        print("✓ No changes needed - proceed with fine-tuning!")
    else:
        if concerns:
            print("\n❌ Critical Issues to Address:")
            for category, items in concerns.items():
                print(f"   - {category}: {items[0] if isinstance(items, list) else items}")

        if warnings:
            print("\n⚠️  Suggested Improvements:")
            for category, items in warnings.items():
                if isinstance(items, list):
                    print(f"   - {category}: {items[0]}")
                else:
                    print(f"   - {category}: {items}")

    print()

if __name__ == "__main__":
    auditor = BestPracticesAuditor()
    report = auditor.audit_dataset(DATASET)
    print_final_verdict(report)

    # Save report
    with open('data/best_practices_audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("📝 Detailed audit saved to: data/best_practices_audit_report.json\n")
