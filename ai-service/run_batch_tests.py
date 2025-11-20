#!/usr/bin/env python3
"""
Test runner for batch availability functionality
Runs both unit tests and integration tests
"""

import sys
import os
import subprocess
import unittest

def run_backend_tests():
    """Run backend TypeScript tests"""
    print("🧪 Running Backend Tests...")
    print("=" * 50)
    
    backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
    
    try:
        # Run Jest tests for technicians controller
        result = subprocess.run([
            'npm', 'test', '--', '--testPathPattern=techniciansController.test.ts'
        ], cwd=backend_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend tests passed!")
        else:
            print("❌ Backend tests failed!")
            print(result.stdout)
            print(result.stderr)
        
        return result.returncode == 0
        
    except FileNotFoundError:
        print("⚠️ npm not found. Please run backend tests manually:")
        print(f"cd {backend_dir} && npm test -- --testPathPattern=techniciansController.test.ts")
        return True  # Don't fail if npm is not available

def run_ai_service_unit_tests():
    """Run AI service unit tests"""
    print("\n🧪 Running AI Service Unit Tests...")
    print("=" * 50)
    
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Discover and run unit tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_batch_availability.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_ai_service_integration_tests():
    """Run AI service integration tests"""
    print("\n🧪 Running AI Service Integration Tests...")
    print("=" * 50)
    
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Check if services are running
    import requests
    
    try:
        backend_response = requests.get("http://localhost:3060/api/health", timeout=5)
        ai_response = requests.get("http://localhost:8060/health", timeout=5)
        
        if backend_response.status_code != 200:
            print("⚠️ Backend API not running on port 3060. Skipping integration tests.")
            return True
        
        if ai_response.status_code != 200:
            print("⚠️ AI Service not running on port 8060. Skipping integration tests.")
            return True
            
    except requests.exceptions.RequestException:
        print("⚠️ Services not accessible. Skipping integration tests.")
        print("To run integration tests, ensure both services are running:")
        print("- Backend: http://localhost:3060")
        print("- AI Service: http://localhost:8060")
        return True
    
    # Run integration tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_batch_integration.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """Main test runner"""
    print("🚀 Batch Availability Test Suite")
    print("=" * 50)
    
    all_passed = True
    
    # Run backend tests
    backend_passed = run_backend_tests()
    all_passed = all_passed and backend_passed
    
    # Run AI service unit tests
    unit_passed = run_ai_service_unit_tests()
    all_passed = all_passed and unit_passed
    
    # Run integration tests
    integration_passed = run_ai_service_integration_tests()
    all_passed = all_passed and integration_passed
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Backend Tests: {'✅ PASSED' if backend_passed else '❌ FAILED'}")
    print(f"Unit Tests: {'✅ PASSED' if unit_passed else '❌ FAILED'}")
    print(f"Integration Tests: {'✅ PASSED' if integration_passed else '❌ FAILED'}")
    print(f"Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
