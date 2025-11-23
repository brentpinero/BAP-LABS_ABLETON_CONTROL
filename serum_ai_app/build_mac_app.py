#!/usr/bin/env python3
"""
Build script for Serum AI Mac app
Creates a standalone .app bundle with bundled model and Python runtime
"""
import os
import sys
import shutil
from pathlib import Path

def build_mac_app():
    """Build the Mac app using PyInstaller"""

    print("🔨 Building Serum AI Mac App...")

    # Get paths
    project_root = Path(__file__).parent.parent
    server_script = project_root / "serum_ai_app" / "server" / "api_server.py"
    adapters_dir = project_root / "serum_lora_adapters" / "conservative_adapters"

    # Verify adapter path exists
    if not adapters_dir.exists():
        print(f"❌ Adapter directory not found: {adapters_dir}")
        sys.exit(1)

    print(f"📂 Server script: {server_script}")
    print(f"📂 Adapters: {adapters_dir}")

    # PyInstaller command
    # --onedir: Create a one-folder bundle (faster startup than --onefile)
    # --windowed: Don't show terminal window
    # --name: App name
    # --add-data: Include adapter files
    # --hidden-import: Ensure MLX dependencies are included

    cmd = [
        "pyinstaller",
        "--onedir",
        "--windowed",
        "--name", "SerumAI",
        "--icon", "serum_ai_app/icon.icns",  # We'll need to create this
        "--add-data", f"{adapters_dir}:adapters",
        "--hidden-import", "mlx",
        "--hidden-import", "mlx_lm",
        "--hidden-import", "flask",
        "--hidden-import", "flask_cors",
        str(server_script),
    ]

    print(f"\n🚀 Running PyInstaller...")
    print(f"   Command: {' '.join(cmd)}")

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("\n❌ PyInstaller not found. Installing...")
        os.system("pip install pyinstaller")

    # Run PyInstaller
    os.system(" ".join(cmd))

    print("\n✅ Build complete!")
    print(f"   App bundle: dist/SerumAI.app")
    print(f"   Size: ~15-20GB (includes model)")

if __name__ == "__main__":
    build_mac_app()
