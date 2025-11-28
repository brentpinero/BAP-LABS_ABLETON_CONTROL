#!/usr/bin/env python3
"""Debug GPT-5 batch 2 processing - find where it's hanging"""

import json
import os
import sys
from dotenv import load_dotenv
import openai
import asyncio
import logging

# Set up logging with debug level
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_pipeline():
    # Load environment
    logger.info("Loading environment...")
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ No OPENAI_API_KEY found in environment")
        return False
    else:
        logger.info("✅ API key loaded")

    # Test OpenAI connection
    logger.info("Testing OpenAI connection...")
    try:
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Use a simple model for testing
            messages=[{"role": "user", "content": "Say 'hello'"}],
            max_tokens=10
        )
        logger.info(f"✅ OpenAI API working: {response.choices[0].message.content}")
    except Exception as e:
        logger.error(f"❌ OpenAI API error: {e}")
        return False

    # Load input data
    logger.info("Loading input data...")
    try:
        with open('data/gpt5_input_500_diverse_batch2.json', 'r') as f:
            data = json.load(f)
        logger.info(f"✅ Loaded {len(data['presets'])} presets")
    except Exception as e:
        logger.error(f"❌ Error loading input: {e}")
        return False

    # Check parameter mapping file
    logger.info("Checking parameter mapping...")
    mapping_files = [
        'data/serum2_parameter_mapping.json',
        'data/serum2_parameter_mapping_final.json'
    ]

    mapping_found = False
    for mapping_file in mapping_files:
        if os.path.exists(mapping_file):
            logger.info(f"✅ Found mapping file: {mapping_file}")
            mapping_found = True
            break

    if not mapping_found:
        logger.error("❌ No parameter mapping file found")
        return False

    # Try to import the pipeline module
    logger.info("Importing pipeline module...")
    try:
        import gpt5_serum_mistral_pipeline_batch2
        logger.info("✅ Pipeline module imported successfully")
    except Exception as e:
        logger.error(f"❌ Error importing pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False

    logger.info("\n✅ All checks passed! Pipeline should be ready to run.")
    logger.info("\nNow trying to initialize the actual pipeline...")

    # Try to initialize the pipeline
    try:
        config = {
            "openai_api_key": api_key,
            "parameter_mapping_file": mapping_file,
            "input_dataset": "data/gpt5_input_500_diverse_batch2.json",
            "output_file": "data/serum_gpt5_mistral_500_diverse_batch2_dataset.json",
            "max_presets": 1,  # Just process 1 for testing
            "use_gpt5": True,
            "gpt5_reasoning_effort": "medium",
            "batch_size": 1,
            "save_interval": 1,
            "resume_from": 0
        }

        logger.info("Creating pipeline with config...")
        pipeline = gpt5_serum_mistral_pipeline_batch2.SerumGPT5Pipeline(config)
        logger.info("✅ Pipeline created successfully")

        # Try to process just one preset
        logger.info("\nProcessing first preset as a test...")
        first_preset = data['presets'][0]
        result = await pipeline.process_preset(first_preset)

        if result:
            logger.info("✅ Successfully processed first preset!")
            # Result is a list of examples
            if isinstance(result, list) and len(result) > 0:
                logger.info(f"  Generated {len(result)} example(s)")
                logger.info(f"  First instruction: {result[0].instruction[:50] if hasattr(result[0], 'instruction') else 'N/A'}...")
            elif hasattr(result, 'instruction'):
                logger.info(f"  Instruction: {result.instruction[:50]}...")
        else:
            logger.error("❌ Failed to process first preset")

    except Exception as e:
        logger.error(f"❌ Error during pipeline initialization/processing: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    logger.info("Starting debug test...")
    result = asyncio.run(test_pipeline())
    if result:
        print("\n✅ Debug test successful! The pipeline should work.")
    else:
        print("\n❌ Debug test failed. Check the errors above.")
        sys.exit(1)