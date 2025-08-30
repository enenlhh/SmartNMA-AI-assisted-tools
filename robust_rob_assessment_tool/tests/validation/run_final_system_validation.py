#!/usr/bin/env python3
"""
Final comprehensive system validation for the ROB Assessment Tool.

This script runs all validation tests to ensure the system is ready for production.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Run final comprehensive system validation."""
    print("🚀 ROB Assessment Tool - Final System Validation")
    print("="*80)
    
    validation_scripts = [
        ("System Integration Tests", "python3 -m pytest tests/test_system_integration_simple.py -v"),
        ("Performance Validation", "python3 tests/validation/validate_system_performance.py"),
    ]
    
    all_passed = True
    
    for test_name, command in validation_scripts:
        print(f"\n📋 Running {test_name}...")
        print("-" * 60)
        
        try:
            result = subprocess.run(
                command.split(),
                cwd=Path(__file__).parent,
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL VALIDATION TESTS PASSED!")
        print("The ROB Assessment Tool is ready for production use.")
    else:
        print("❌ SOME VALIDATION TESTS FAILED!")
        print("Please review the failures above.")
    print("="*80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())