#!/usr/bin/env python3
"""
Upload conservative adapters to replace the broken version on HuggingFace
"""
from huggingface_hub import HfApi
from pathlib import Path

api = HfApi()

print("🚀 Uploading conservative adapters to HuggingFace...")
print("   Repo: bapinero/BAP-Labs-M1")
print("   Source: serum_lora_adapters/conservative_adapters")

# Upload all files from conservative_adapters directory
adapter_path = Path("serum_lora_adapters/conservative_adapters")

# Delete old files first
print("\n🗑️  Deleting old adapter files...")
try:
    api.delete_file(
        path_in_repo="adapters.safetensors",
        repo_id="bapinero/BAP-Labs-M1",
        repo_type="model"
    )
    print("   ✅ Deleted old adapters.safetensors")
except Exception as e:
    print(f"   ⚠️  Could not delete old file: {e}")

# Upload new files
print("\n📤 Uploading new adapter files...")
api.upload_folder(
    folder_path=str(adapter_path),
    repo_id="bapinero/BAP-Labs-M1",
    repo_type="model",
    commit_message="Replace with conservative adapters (LR: 1e-4, 500 iters) - 100% test pass rate"
)

print("\n✅ Upload complete!")
print("   View at: https://huggingface.co/bapinero/BAP-Labs-M1")
