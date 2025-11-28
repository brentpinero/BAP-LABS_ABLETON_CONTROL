#!/usr/bin/env python3

import asyncio
import json
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gpt5_response():
    """Debug what GPT-5 is actually returning"""

    # Load API key
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Simple test prompt
    system_prompt = """You are an expert music producer and sound designer with deep knowledge of Serum synthesizer.

Your task: Generate 3 natural, diverse instructions that real producers would use.

OUTPUT FORMAT:
Return exactly this JSON structure:
{
  "instructions": [
    {"text": "Create a dark dubstep wobble bass", "type": "genre", "complexity": "simple"},
    {"text": "Make a lead that cuts through the mix", "type": "technical", "complexity": "moderate"},
    {"text": "Design something mysterious and evolving", "type": "character", "complexity": "advanced"}
  ]
}"""

    user_prompt = """Preset: Test Bass

Active Parameters:
- Master Volume (1): 0.8
- Filter 1 Freq (206): 0.3
- Osc A Level (22): 0.9

Generate 3 diverse instructions for this preset."""

    try:
        print("🔍 Testing GPT-5 response...")

        response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=8000,
            reasoning_effort="high"
        )

        # Print raw response details
        print(f"\n📊 Response Details:")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage}")

        # Print raw content
        raw_content = response.choices[0].message.content
        print(f"\n📄 Raw Content Length: {len(raw_content)}")
        print(f"\n📝 Raw Content:")
        print("=" * 80)
        print(raw_content)
        print("=" * 80)

        # Test parsing logic
        import re
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if json_match:
            print(f"\n✅ JSON Found!")
            try:
                data = json.loads(json_match.group())
                print(f"Parsed JSON: {json.dumps(data, indent=2)}")
                instructions = data.get("instructions", [])
                print(f"Instructions count: {len(instructions)}")
            except Exception as e:
                print(f"❌ JSON Parse Error: {e}")
        else:
            print(f"\n❌ No JSON found in response")

            # Try fallback parsing
            print(f"\n🔄 Trying fallback parsing...")
            lines = raw_content.strip().split('\n')
            for i, line in enumerate(lines[:10]):  # First 10 lines
                print(f"Line {i}: '{line.strip()}'")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gpt5_response())