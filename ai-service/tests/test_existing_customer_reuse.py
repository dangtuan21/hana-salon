#!/usr/bin/env python3
"""
Test that existing customers are reused instead of creating duplicates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_existing_customer_reuse():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Existing Customer Reuse...")
    print("=" * 60)
    
    # Use the same customer info as our previous booking (Teo, +14434343434)
    customer_phone = "443-434-3434"  # Same phone, different format
    customer_name = "Teo"
    
    print(f"📨 Step 1: Making booking with existing customer...")
    print(f"   👤 Customer: {customer_name}")
    print(f"   📞 Phone: {customer_phone}")
    
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": f"Hi, I'm {customer_name}, phone {customer_phone}. I want Basic Manicure for Sunday at 10am"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        session_id = data.get('session_id')
        booking_state = data.get('booking_state', {})
        
        print(f"✅ Initial booking state created")
        
        # Confirm to trigger booking creation
        print(f"\n📨 Step 2: Confirming to trigger booking creation...")
        
        confirm_response = requests.post(f"{base_url}/conversation/continue", json={
            "session_id": session_id,
            "message": "yes"
        })
        
        if confirm_response.status_code == 200:
            confirm_data = confirm_response.json()
            final_booking_state = confirm_data.get('booking_state', {})
            actions_taken = confirm_data.get('actions_taken', [])
            
            print(f"🔧 Actions Taken: {actions_taken}")
            
            # Check if customer was found vs created
            booking_successful = any('booking_created' in str(action).lower() and 'error' not in str(action).lower() for action in actions_taken)
            customer_id = final_booking_state.get('customerId')
            
            if booking_successful and customer_id:
                print(f"\n✅ Booking created successfully!")
                print(f"   🆔 Customer ID: {customer_id}")
                
                # Check if this matches our previous customer ID
                expected_customer_id = "691d6615cc48beafeba05e7c"  # From previous booking
                
                if customer_id == expected_customer_id:
                    print(f"🎉 SUCCESS: EXISTING CUSTOMER REUSED!")
                    print(f"   ✅ Same customer ID as previous booking")
                    print(f"   ✅ No duplicate customer created")
                    print(f"   ✅ Phone number lookup working correctly")
                else:
                    print(f"⚠️  Different customer ID: {customer_id}")
                    print(f"   Expected: {expected_customer_id}")
                    print(f"   This might be due to phone format differences")
                
                # Get customer details from backend
                print(f"\n📊 Verifying customer in database...")
                customer_response = requests.get(f"http://localhost:3060/api/customers/phone/{customer_phone.replace('-', '')}")
                if customer_response.status_code == 200:
                    customer_data = customer_response.json()
                    print(f"✅ Customer found in database:")
                    print(f"   Name: {customer_data.get('data', {}).get('firstName', 'N/A')}")
                    print(f"   Phone: {customer_data.get('data', {}).get('phone', 'N/A')}")
                    print(f"   ID: {customer_data.get('data', {}).get('_id', 'N/A')}")
                
            else:
                print(f"❌ Booking creation failed")
                print(f"   Actions: {actions_taken}")
                
        else:
            print(f"❌ Confirmation failed: {confirm_response.status_code}")
    else:
        print(f"❌ Start request failed: {start_response.status_code}")

if __name__ == "__main__":
    test_existing_customer_reuse()
