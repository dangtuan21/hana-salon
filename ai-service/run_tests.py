#!/usr/bin/env python3
"""
Test runner for Hana AI Booking System
Runs all tests in the tests/ directory
"""

import os
import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run all test files in the tests directory"""
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    tests_dir = script_dir / "tests"
    
    if not tests_dir.exists():
        print("❌ Tests directory not found!")
        return False
    
    # Find all test files
    test_files = list(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ No test files found!")
        return False
    
    print(f"🧪 Found {len(test_files)} test files")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_file in sorted(test_files):
        test_name = test_file.name
        print(f"\n📋 Running {test_name}...")
        print("-" * 40)
        
        try:
            # Run the test
            result = subprocess.run([
                sys.executable, str(test_file)
            ], capture_output=True, text=True, cwd=script_dir)
            
            if result.returncode == 0:
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                failed += 1
                
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"💥 {failed} test(s) failed!")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
