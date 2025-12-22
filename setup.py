#!/usr/bin/env python3
"""
Vulnhalla Setup Script - Cross platform one line installation
Usage: python setup.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from src.utils.config import SUPPORTED_LANGUAGES

# Get project root
PROJECT_ROOT = Path(__file__).parent

# Add project root to Python path for imports
sys.path.insert(0, str(PROJECT_ROOT))

# Initialize logging early
from src.utils.logger import setup_logging, get_logger
setup_logging()
logger = get_logger(__name__)
# Check Python version
if sys.version_info >= (3, 14):
    logger.error("Python 3.14+ is not yet supported (grpcio wheels unavailable). Please use Python 3.11 or 3.12.")
    sys.exit(1)


def check_dependencies_installed() -> bool:
    """
    Check if all required dependencies are already installed by trying to import them.
    
    Returns:
        bool: True if all dependencies are installed, False otherwise.
    """
    try:
        import requests
        import dotenv
        import litellm
        import yaml
        import textual
        import pySmartDL
        return True
    except ImportError:
        return False


def install_pack(directory: Path, codeql_cmd: str, description: str):
    """
    Helper function to install a CodeQL pack in a specific directory.
    Running 'codeql pack install' ensures the cache is populated even if a lock file exists.
    """
    if not directory.exists():
        return

    logger.info(f"📦 Installing {description}...")
    try:
        # We must change directory because 'codeql pack install' expects to run in the pack root
        os.chdir(str(directory))
        
        result = subprocess.run(
            [codeql_cmd, "pack", "install"], 
            check=False, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            logger.warning(f"Failed to install {description}:")
            logger.warning(result.stderr)
        else:
            logger.info(f"✅ {description} installed/verified.")
            
    except Exception as e:
        logger.error(f"❌ Exception installing {description}: {e}")
    finally:
        # Always return to project root
        os.chdir(str(PROJECT_ROOT))


def main():
    """Run the Vulnhalla setup process.

    This script installs Python dependencies, verifies the CodeQL
    CLI configuration, installs required CodeQL packs, and prints
    next steps for running the analysis pipeline.
    """
    logger.info("Vulnhalla Setup")
    logger.info("=" * 50)
    
    # Install CodeQL packs
    # Check for CodeQL in PATH or .env
    codeql_cmd = None
    
    try:
        from src.utils.config import get_codeql_path
        from src.utils.config_validator import find_codeql_executable
        
        codeql_path = get_codeql_path()
        logger.info("Checking CodeQL path: %s", codeql_path)
        
        # Use helper function to find executable
        codeql_cmd = find_codeql_executable()
        
        if codeql_cmd:
            if codeql_path == "codeql":
                logger.info("🔍 Checking if 'codeql' is in PATH...")
                logger.info("✅ Found in PATH: %s", codeql_cmd)
            else:
                logger.info("✅ Found CodeQL path: %s", codeql_cmd)
        else:
            # Provide detailed error messages
            if codeql_path and codeql_path != "codeql":
                # Custom path specified - strip quotes if present
                codeql_path_clean = codeql_path.strip('"').strip("'")
                logger.error("❌ Path does not exist: %s", codeql_path_clean)
                if os.name == 'nt':
                    logger.info("Also checked: %s.cmd", codeql_path_clean)
            else:
                logger.info("🔍 Checking if 'codeql' is in PATH...")
                logger.error("❌ 'codeql' not found in PATH")
    except Exception as e:
        # Fallback to checking PATH
        logger.error("❌ Error loading config: %s", e)
        logger.info("🔍 Falling back to PATH check...")
        codeql_cmd = shutil.which("codeql")
        if codeql_cmd:
            logger.info("✅ Found in PATH: %s", codeql_cmd)
    
    if codeql_cmd:
        logger.info("📦 Installing CodeQL packs... This may take a moment ⏳")

        for lang in SUPPORTED_LANGUAGES:
            gh_lang = "cpp" if lang == "c" else lang
        
            # Tools packs
            tools_dir = PROJECT_ROOT / "data/queries" / gh_lang / "tools"
            install_pack(tools_dir, codeql_cmd, f"{lang} tools pack")

            # Issues packs
            issues_dir = PROJECT_ROOT / "data/queries" / gh_lang / "issues"
            install_pack(issues_dir, codeql_cmd, f"{lang} issues pack")
            
    else:
        logger.error("❌ CodeQL CLI not found. Skipping CodeQL pack installation.")
        logger.info("🔗 Install CodeQL CLI from: https://github.com/github/codeql-cli-binaries/releases")
        logger.info("   After installation, either add CodeQL to your PATH or set CODEQL_PATH in your .env file.")
        logger.info("   Then run: python setup.py or install packages manually")
        return
    
    # Optional: Validate CodeQL configuration if .env file exists
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        logger.info("\n🔍 Validating CodeQL configuration...")
        try:
            from src.utils.config_validator import validate_codeql_path
            is_valid, error = validate_codeql_path()
            if is_valid:
                logger.info("✅ CodeQL configuration validated successfully!")
            else:
                logger.warning("⚠️  CodeQL configuration issue detected:")
                logger.warning("   %s", error.split(chr(10))[0])  # Print first line of error
                logger.warning("   Please fix this before running the pipeline.")
        except Exception as e:
            logger.warning("⚠️  Could not validate CodeQL configuration: %s", e)
            logger.info("   This is not critical - you can fix configuration later.")
    
    logger.info("🎉 Setup completed successfully! 🎉")
    logger.info("🔗 Next steps:")
    if not env_file.exists():
        logger.info("1. Create a .env file with all the required variables (see README.md)")
        logger.info("2. Run one of the following commands to start the pipeline:")
    else:
        logger.info("Run one of the following commands to start the pipeline:")
    logger.info("   • python src/pipeline.py <repo_org/repo_name>    # Analyze a specific repository")
    logger.info("   • python src/pipeline.py                         # Analyze top 100 repositories")
    logger.info("   • python examples/example.py                     # See a full pipeline run")

if __name__ == "__main__":
    main()
