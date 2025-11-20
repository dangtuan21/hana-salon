#!/usr/bin/env python3
"""
Test creating a new customer with phone number to verify backend changes
"""

import requests
import json

def test_create_new_customer():
    """Test creating a new customer with phone 333333"""
    print("🧪 TESTING NEW CUSTOMER CREATION")
    print("=" * 50)
    
    try:
        # Create a new customer with a unique phone number
        import time
        test_phone = f"55{int(time.time()) % 10000}"  # Generate unique phone
        customer_data = {
            "firstName": "TestUser",
            "phone": test_phone
        }
        
        print(f"📞 Creating customer with phone: '{test_phone}'")
        
        # Create customer
        response = requests.post("http://localhost:3060/api/customers", 
                               json=customer_data)
        
        if response.status_code == 201:
            data = response.json()
            customer = data.get('data', {})
            stored_phone = customer.get('phone', '')
            
            print(f"✅ Customer created successfully")
            print(f"📱 Stored phone: '{stored_phone}'")
            print(f"🎯 Expected: '{test_phone}'")
            
            if stored_phone == test_phone:
                print("✅ SUCCESS: Phone number preserved correctly!")
                return True, test_phone
            else:
                print(f"❌ FAILED: Phone number was modified from '{test_phone}' to '{stored_phone}'")
                return False, test_phone
        else:
            print(f"❌ Failed to create customer: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend server not running")
        return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_lookup_new_customer(test_phone):
    """Test looking up the newly created customer"""
    print("\n🔍 TESTING CUSTOMER LOOKUP")
    print("=" * 50)
    
    try:
        print(f"🔍 Looking up customer with phone: '{test_phone}'")
        
        response = requests.get(f"http://localhost:3060/api/customers/phone/{test_phone}")
        
        if response.status_code == 200:
            data = response.json()
            customer = data.get('data', {})
            stored_phone = customer.get('phone', '')
            
            print(f"✅ Customer found")
            print(f"📱 Retrieved phone: '{stored_phone}'")
            
            if stored_phone == test_phone:
                print("✅ SUCCESS: Phone lookup working correctly!")
                return True
            else:
                print(f"❌ FAILED: Retrieved phone '{stored_phone}' doesn't match expected '{test_phone}'")
                return False
        elif response.status_code == 404:
            print("❌ Customer not found (might not have been created)")
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run the test"""
    print("🚀 BACKEND PHONE FORMATTING TEST")
    print("=" * 60)
    
    create_result, test_phone = test_create_new_customer()
    lookup_result = test_lookup_new_customer(test_phone) if test_phone else False
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"   Customer Creation: {'✅ PASSED' if create_result else '❌ FAILED' if create_result is not None else '⚠️  SKIPPED'}")
    print(f"   Customer Lookup: {'✅ PASSED' if lookup_result else '❌ FAILED' if lookup_result is not None else '⚠️  SKIPPED'}")
    
    if create_result and lookup_result:
        print("\n🎉 SUCCESS: Backend phone formatting is working correctly!")
        print("💡 Phone numbers < 10 digits are now preserved in original format")
    else:
        print("\n❌ ISSUES DETECTED: Backend phone formatting needs more work")

if __name__ == "__main__":
    main()
