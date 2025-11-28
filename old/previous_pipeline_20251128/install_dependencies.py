#!/usr/bin/env python3
"""
Install and check dependencies for Serum MLX pipeline.
"""

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_package(package):
    """Install a Python package."""
    logger.info(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        return True
    except subprocess.CalledProcessError:
        logger.error(f"Failed to install {package}")
        return False

def check_package(package, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package.replace('-', '_')

    try:
        subprocess.check_call([
            sys.executable, '-c', f'import {import_name}'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    logger.info("🔧 Setting up Serum MLX Pipeline Dependencies")
    logger.info("=" * 50)

    required_packages = [
        ('mlx', 'mlx'),
        ('mlx-lm', 'mlx_lm'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('pydantic', 'pydantic'),
        ('numpy', 'numpy'),
        ('datasets', 'datasets'),
        ('transformers', 'transformers')
    ]

    missing_packages = []

    # Check what's already installed
    logger.info("Checking existing packages...")
    for package, import_name in required_packages:
        if check_package(package, import_name):
            logger.info(f"✅ {package} - already installed")
        else:
            logger.info(f"❌ {package} - missing")
            missing_packages.append(package)

    # Install missing packages
    if missing_packages:
        logger.info(f"\nInstalling {len(missing_packages)} missing packages...")

        failed_installs = []
        for package in missing_packages:
            if not install_package(package):
                failed_installs.append(package)

        if failed_installs:
            logger.error(f"❌ Failed to install: {', '.join(failed_installs)}")
            return False
        else:
            logger.info("✅ All packages installed successfully")
    else:
        logger.info("✅ All required packages already installed")

    # Final verification
    logger.info("\nFinal verification...")
    all_good = True
    for package, import_name in required_packages:
        if check_package(package, import_name):
            logger.info(f"✅ {package}")
        else:
            logger.error(f"❌ {package} - still not working")
            all_good = False

    if all_good:
        logger.info("\n🎉 All dependencies ready!")
        logger.info("You can now run: python run_complete_pipeline.py --test-mode")
        return True
    else:
        logger.error("\n❌ Some dependencies still missing")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)