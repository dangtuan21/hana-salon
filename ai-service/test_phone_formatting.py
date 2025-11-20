#!/usr/bin/env python3
"""
Test script for phone number formatting issue
Tests the specific case: "Teo, 333333" should preserve "333333" not become "13333333333"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.action_executor import ActionExecutor
from services.backend_client import BackendAPIClient
import json

def test_phone_formatting():
    """Test phone number formatting preservation"""
    print("🧪 TESTING PHONE NUMBER FORMATTING")
    print("=" * 50)
    
    # Initialize ActionExecutor
    backend_client = BackendAPIClient()
    executor = ActionExecutor(backend_client)
    
    # Test cases
    test_cases = [
        # (input, expected_output, description)
        ("333333", "333333", "6-digit number should be preserved"),
        ("1234567890", "123-456-7890", "10-digit number should be formatted"),
        ("123456", "123456", "6-digit number should be preserved"),
        ("12345", "12345", "5-digit number should be preserved"),
        ("555-1234", "555-1234", "Already formatted should be preserved"),
        ("(555) 123-4567", "(555) 123-4567", "Parentheses format should be preserved"),
        ("", "", "Empty string should remain empty"),
        ("  333333  ", "333333", "Whitespace should be trimmed"),
    ]
    
    print("📋 Testing _format_phone_number method:")
    all_passed = True
    
    for input_phone, expected, description in test_cases:
        result = executor._format_phone_number(input_phone)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{input_phone}' → '{result}' (expected: '{expected}') - {description}")
        if result != expected:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL PHONE FORMATTING TESTS PASSED!")
    else:
        print("❌ SOME PHONE FORMATTING TESTS FAILED!")
    
    return all_passed

def test_conversation_flow():
    """Test the full conversation flow with phone number"""
    print("\n🧪 TESTING CONVERSATION FLOW WITH PHONE")
    print("=" * 50)
    
    try:
        import requests
        
        # Test the actual conversation flow
        print("📞 Testing conversation with 'Teo, 333333'")
        
        # Start conversation
        response = requests.post("http://localhost:8060/conversation/start", 
                               json={"message": "Teo, 333333"})
        
        if response.status_code == 200:
            data = response.json()
            booking_state = data.get('booking_state', {})
            customer_phone = booking_state.get('customer_phone', '')
            customer_name = booking_state.get('customer_name', '')
            
            print(f"✅ Conversation started successfully")
            print(f"📞 Customer Name: '{customer_name}'")
            print(f"📱 Customer Phone: '{customer_phone}'")
            
            # Check if phone number is preserved
            if customer_phone == "333333":
                print("✅ Phone number preserved correctly!")
                return True
            else:
                print(f"❌ Phone number modified! Expected '333333', got '{customer_phone}'")
                return False
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API server not running - skipping conversation flow test")
        print("💡 Start the server with: python start_booking_system.py")
        return None
    except Exception as e:
        print(f"❌ Error testing conversation flow: {e}")
        return False

def test_backend_phone_handling():
    """Test how backend handles phone numbers"""
    print("\n🧪 TESTING BACKEND PHONE HANDLING")
    print("=" * 50)
    
    try:
        import requests
        
        # Test customer lookup with original phone
        test_phone = "333333"
        print(f"🔍 Testing customer lookup with phone: '{test_phone}'")
        
        response = requests.get(f"http://localhost:3060/api/customers/phone/{test_phone}")
        print(f"📡 Backend response: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Customer not found (expected for new phone number)")
            return True
        elif response.status_code == 200:
            data = response.json()
            customer = data.get('data', {})
            stored_phone = customer.get('phone', '')
            print(f"✅ Customer found with phone: '{stored_phone}'")
            return stored_phone == test_phone
        else:
            print(f"❌ Unexpected response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend server not running - skipping backend test")
        print("💡 Start the backend server first")
        return None
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 PHONE NUMBER FORMATTING TEST SUITE")
    print("=" * 60)
    
    # Test 1: Phone formatting method
    formatting_passed = test_phone_formatting()
    
    # Test 2: Full conversation flow
    conversation_passed = test_conversation_flow()
    
    # Test 3: Backend phone handling
    backend_passed = test_backend_phone_handling()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"   Phone Formatting: {'✅ PASSED' if formatting_passed else '❌ FAILED'}")
    print(f"   Conversation Flow: {'✅ PASSED' if conversation_passed else '❌ FAILED' if conversation_passed is not None else '⚠️  SKIPPED'}")
    print(f"   Backend Handling: {'✅ PASSED' if backend_passed else '❌ FAILED' if backend_passed is not None else '⚠️  SKIPPED'}")
    
    if formatting_passed and (conversation_passed is not False) and (backend_passed is not False):
        print("\n🎉 OVERALL: TESTS SUCCESSFUL!")
        print("💡 Phone number '333333' should now be preserved correctly")
    else:
        print("\n❌ OVERALL: SOME TESTS FAILED!")
        print("🔧 Check the failed tests above for issues")

if __name__ == "__main__":
    main()
