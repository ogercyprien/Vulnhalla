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

# Get project root
PROJECT_ROOT = Path(__file__).parent

# Add project root to Python path for imports
sys.path.insert(0, str(PROJECT_ROOT))

# Check Python version
if sys.version_info >= (3, 14):
    print("ERROR: Python 3.14+ is not yet supported (grpcio wheels unavailable). Please use Python 3.11 or 3.12.")
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


def main():
    print("Vulnhalla Setup")
    print("=" * 50)
    
    # Check if virtual environment exists
    venv_path = PROJECT_ROOT / "venv"
    use_venv = venv_path.exists()
    
    if use_venv:
        # Use virtual environment pip
        if os.name == 'nt':  # Windows
            pip_exe = [str(PROJECT_ROOT / "venv/Scripts/pip.exe")]
        else:  # Unix/macOS/Linux
            pip_exe = [str(PROJECT_ROOT / "venv/bin/pip")]
        print("Using virtual environment...")
    else:
        # Use system pip
        pip_exe = [sys.executable, "-m", "pip"]
        print("Installing to current Python environment...")
    
    if check_dependencies_installed():
        print("✅ All dependencies are already installed! Skipping installation.")
    else:
        # Install dependencies
        print("📦 Installing Python dependencies... This may take a moment ⏳")
        try:
            subprocess.run(pip_exe + ["install","-q", "-r", str(PROJECT_ROOT / "requirements.txt")], check=True)
            print("✅ Python dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print("\n❌ Setup failed. Please fix the missing dependencies and run setup.py again.")
            sys.exit(1)
    
    # Install CodeQL packs
    # Check for CodeQL in PATH or .env
    codeql_cmd = None
    
    try:
        from src.utils.config import get_codeql_path
        from src.utils.config_validator import find_codeql_executable
        
        codeql_path = get_codeql_path()
        print(f"Checking CodeQL path: {codeql_path}")
        
        # Use helper function to find executable
        codeql_cmd = find_codeql_executable()
        
        if codeql_cmd:
            if codeql_path == "codeql":
                print(f"🔍 Checking if 'codeql' is in PATH...")
                print(f"✅ Found in PATH: {codeql_cmd}")
            else:
                print(f"✅ Found CodeQL path: {codeql_cmd}")
        else:
            # Provide detailed error messages
            if codeql_path and codeql_path != "codeql":
                # Custom path specified - strip quotes if present
                codeql_path_clean = codeql_path.strip('"').strip("'")
                print(f"❌ Path does not exist: {codeql_path_clean}")
                if os.name == 'nt':
                    print(f"Also checked: {codeql_path_clean}.cmd")
                    print(f"Also checked: {codeql_path_clean}.exe")
            else:
                print(f"🔍 Checking if 'codeql' is in PATH...")
                print(f"❌ 'codeql' not found in PATH")
    except Exception as e:
        # Fallback to checking PATH
        print(f"❌ Error loading config: {e}")
        print(f"🔍 Falling back to PATH check...")
        codeql_cmd = shutil.which("codeql")
        if codeql_cmd:
            print(f"✅ Found in PATH: {codeql_cmd}")
    
    if codeql_cmd:
        print("📦 Installing CodeQL packs... This may take a moment ⏳")
        
        # Tools pack
        tools_dir = PROJECT_ROOT / "data/queries/cpp/tools"
        if tools_dir.exists():
            os.chdir(str(tools_dir))
            result = subprocess.run([codeql_cmd, "pack", "install"], check=False, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Warning: Failed to install tools pack: {result.stderr}")
            os.chdir(str(PROJECT_ROOT))
        
        # Issues pack
        issues_dir = PROJECT_ROOT / "data/queries/cpp/issues"
        if issues_dir.exists():
            os.chdir(str(issues_dir))
            result = subprocess.run([codeql_cmd, "pack", "install"], check=False, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Warning: Failed to install issues pack: {result.stderr}")
            os.chdir(str(PROJECT_ROOT))
    else:
        print("❌ CodeQL CLI not found. Skipping CodeQL pack installation.")
        print("🔗 Install CodeQL CLI from: https://github.com/github/codeql-cli-binaries/releases")
        print("   After installation, either add CodeQL to your PATH or set CODEQL_PATH in your .env file.")
        print("   Then run: python setup.py or install packages manually")
        return
    
    # Optional: Validate CodeQL configuration if .env file exists
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        print("\n🔍 Validating CodeQL configuration...")
        try:
            from src.utils.config_validator import validate_codeql_path
            is_valid, error = validate_codeql_path()
            if is_valid:
                print("✅ CodeQL configuration validated successfully!")
            else:
                print("⚠️  CodeQL configuration issue detected:")
                print(f"   {error.split(chr(10))[0]}")  # Print first line of error
                print("   Please fix this before running the pipeline.")
        except Exception as e:
            print(f"⚠️  Could not validate CodeQL configuration: {e}")
            print("   This is not critical - you can fix configuration later.")
    
    print("\n🎉 Setup completed successfully! 🎉")
    print("🔗 Next steps:")
    if not env_file.exists():
        print("1. Create a .env file with all the required variables (see README.md)")
        print("2. Run one of the following commands to start the pipeline:")
    else:
        print("Run one of the following commands to start the pipeline:")
    print("   • python src/pipeline.py <repo_org/repo_name>    # Analyze a specific repository")
    print("   • python src/pipeline.py                         # Analyze top 100 repositories")
    print("   • python examples/example.py                     # See a full pipeline run")

if __name__ == "__main__":
    main()

