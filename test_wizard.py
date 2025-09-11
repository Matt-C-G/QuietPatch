#!/usr/bin/env python3
"""
Test script for QuietPatch wizard
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter imported")
    except ImportError as e:
        print(f"✗ tkinter import failed: {e}")
        return False
    
    try:
        from gui.wizard import Wizard
        print("✓ Wizard imported")
    except ImportError as e:
        print(f"✗ Wizard import failed: {e}")
        return False
    
    return True

def test_wizard_creation():
    """Test that the wizard can be created"""
    print("\nTesting wizard creation...")
    
    try:
        from gui.wizard import Wizard
        import tkinter as tk
        
        # Create a test instance (don't show it)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        wizard = Wizard()
        print("✓ Wizard created successfully")
        
        # Test some basic properties
        assert wizard.title() == 'QuietPatch'
        print("✓ Window title is correct")
        
        # Check that frames exist
        assert 'Welcome' in wizard.frames
        assert 'Options' in wizard.frames
        assert 'Progress' in wizard.frames
        print("✓ Frames initialized")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Wizard creation failed: {e}")
        return False

def test_cli_integration():
    """Test that CLI integration works"""
    print("\nTesting CLI integration...")
    
    try:
        from gui.wizard import Wizard
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        wizard = Wizard()
        
        # Test CLI path detection
        from gui.wizard import CLI
        cli_path = CLI
        print(f"CLI path: {cli_path}")
        
        # Check if CLI exists (it might not in test environment)
        if cli_path.exists():
            print("✓ CLI binary found")
        else:
            print("⚠ CLI binary not found (expected in test environment)")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ CLI integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("QuietPatch Wizard Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_wizard_creation,
        test_cli_integration,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
