#!/usr/bin/env python3
"""
Monitor batch2 processing and automatically combine datasets when complete.
"""

import time
import subprocess
import os
from pathlib import Path
import json

def get_process_status():
    """Check if GPT-5 processing is still running."""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )
        return 'gpt5_serum_mistral_pipeline_batch2.py' in result.stdout
    except:
        return False

def get_progress_stats():
    """Get current processing statistics."""
    log_file = 'batch2_output.log'
    if not Path(log_file).exists():
        return None

    try:
        result = subprocess.run(
            f"tail -100 {log_file} | grep -E '(Processing preset:|✅ Accepted|❌ Filtered)' | tail -10",
            shell=True,
            capture_output=True,
            text=True
        )

        # Count totals
        with open(log_file, 'r') as f:
            content = f.read()
            processed = content.count("Processing preset:")
            accepted = content.count("✅ Accepted")
            filtered = content.count("❌ Filtered")

        return {
            'processed': processed,
            'accepted': accepted,
            'filtered': filtered,
            'recent': result.stdout
        }
    except:
        return None

def check_final_dataset():
    """Check if the final batch2 dataset exists and is complete."""
    final_file = 'data/serum_gpt5_mistral_500_diverse_batch2_dataset.json'
    if Path(final_file).exists():
        with open(final_file, 'r') as f:
            data = json.load(f)
            return len(data.get('examples', []))
    return 0

def main():
    print("🔍 MONITORING BATCH2 PROCESSING")
    print("=" * 50)

    check_interval = 60  # Check every minute
    start_time = time.time()

    while True:
        # Check if process is running
        is_running = get_process_status()

        # Get progress stats
        stats = get_progress_stats()

        # Check for final dataset
        final_count = check_final_dataset()

        # Display status
        elapsed = time.time() - start_time
        elapsed_mins = int(elapsed / 60)

        print(f"\n[{time.strftime('%H:%M:%S')}] Status Update (running for {elapsed_mins} mins)")
        print("-" * 40)

        if stats:
            print(f"📊 Progress: {stats['processed']} processed")
            print(f"   ✅ {stats['accepted']} accepted")
            print(f"   ❌ {stats['filtered']} filtered")
            print(f"   📈 Acceptance rate: {stats['accepted']/(stats['accepted']+stats['filtered'])*100:.1f}%")

        if final_count > 0:
            print(f"📦 Final dataset: {final_count} examples")

        print(f"🔄 Process running: {'Yes' if is_running else 'No'}")

        # Check if processing is complete
        if not is_running and final_count > 0:
            print("\n✅ BATCH2 PROCESSING COMPLETE!")
            print(f"Generated {final_count} examples")

            print("\n🚀 Running combination script...")
            time.sleep(2)

            # Run combination script
            result = subprocess.run(
                ['python3', 'combine_datasets_final.py'],
                capture_output=True,
                text=True
            )
            print(result.stdout)

            if result.returncode == 0:
                print("\n🎉 DATASETS SUCCESSFULLY COMBINED!")

                # Run validation
                print("\n🔍 Running validation on combined dataset...")
                result = subprocess.run(
                    ['python3', 'validate_training_data.py', 'data/serum_gpt5_mistral_FINAL_combined.json'],
                    capture_output=True,
                    text=True
                )
                print(result.stdout)

                print("\n✅ ALL DONE! Dataset ready for finetuning!")
                break
            else:
                print("\n❌ Combination failed. Check errors above.")
                break

        elif not is_running and stats and stats['processed'] > 0:
            print("\n⚠️  Process stopped but dataset not complete.")
            print("Check batch2_output.log for errors")
            print("You may need to restart the processing")
            break

        # Wait before next check
        print(f"\nNext check in {check_interval} seconds... (Ctrl+C to stop)")
        try:
            time.sleep(check_interval)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
            break

if __name__ == "__main__":
    main()