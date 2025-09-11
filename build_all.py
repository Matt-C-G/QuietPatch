#!/usr/bin/env python3
"""
Build script for QuietPatch v0.4.0
Builds PyInstaller binaries for all platforms
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✓ Success: {cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {cmd}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main build function"""
    print("QuietPatch v0.4.0 Build Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Install PyInstaller if not available
    print("Checking PyInstaller...")
    if not run_command("python -c 'import PyInstaller'", cwd="."):
        print("Installing PyInstaller...")
        if not run_command("pip install pyinstaller"):
            print("Failed to install PyInstaller")
            sys.exit(1)
    
    # Install project dependencies
    print("Installing dependencies...")
    if not run_command("pip install -e ."):
        print("Failed to install project dependencies")
        sys.exit(1)
    
    # Create output directories
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)
    
    # Build GUI wizard
    print("\nBuilding GUI wizard...")
    if not run_command("pyinstaller build/quietpatch_wizard.spec"):
        print("Failed to build GUI wizard")
        sys.exit(1)
    
    # Build CLI
    print("\nBuilding CLI...")
    if not run_command("pyinstaller build/quietpatch_cli.spec"):
        print("Failed to build CLI")
        sys.exit(1)
    
    # Check outputs
    print("\nChecking outputs...")
    gui_path = Path("dist/QuietPatchWizard.exe" if platform.system() == "Windows" else "dist/QuietPatchWizard")
    cli_path = Path("dist/quietpatch.exe" if platform.system() == "Windows" else "dist/quietpatch")
    
    if gui_path.exists():
        print(f"✓ GUI built: {gui_path}")
        print(f"  Size: {gui_path.stat().st_size / (1024*1024):.1f} MB")
    else:
        print(f"✗ GUI not found: {gui_path}")
    
    if cli_path.exists():
        print(f"✓ CLI built: {cli_path}")
        print(f"  Size: {cli_path.stat().st_size / (1024*1024):.1f} MB")
    else:
        print(f"✗ CLI not found: {cli_path}")
    
    print("\nBuild complete!")
    print("\nNext steps:")
    print("1. Test the GUI: python gui/wizard.py")
    print("2. Test the CLI: python qp_cli.py --help")
    print("3. Run packaging scripts for your platform")

if __name__ == "__main__":
    main()
