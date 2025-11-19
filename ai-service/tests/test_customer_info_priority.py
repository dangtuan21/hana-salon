#!/usr/bin/env python3
"""
Test if system asks for missing customer information before proceeding
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_customer_info_priority():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Customer Info Priority...")
    print("=" * 60)
    
    # Test with service and date/time but no customer info
    print("📨 Testing: Service request without customer info...")
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "I want Gel Manicure for Friday at 2pm"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        response_text = data['response'].lower()
        booking_state = data.get('booking_state', {})
        
        print(f"📝 System Response: {data['response']}")
        print(f"👤 Customer Name: '{booking_state.get('customer_name', '')}'")
        print(f"📞 Customer Phone: '{booking_state.get('customer_phone', '')}'")
        
        # Check if system asks for customer info instead of confirming date/time
        asks_for_customer_info = any(phrase in response_text for phrase in [
            'name', 'phone', 'contact', 'your name', 'phone number'
        ])
        
        asks_for_confirmation = any(phrase in response_text for phrase in [
            'confirm', 'please confirm', 'friday'
        ])
        
        if asks_for_customer_info and not asks_for_confirmation:
            print("✅ SUCCESS: System asks for customer info first")
        elif asks_for_confirmation and not asks_for_customer_info:
            print("❌ ISSUE: System asks for confirmation without customer info")
        elif asks_for_customer_info and asks_for_confirmation:
            print("⚠️ MIXED: System asks for both customer info and confirmation")
        else:
            print("? UNCLEAR: System response doesn't clearly ask for either")
            
    else:
        print(f"❌ Request failed: {start_response.status_code}")

if __name__ == "__main__":
    test_customer_info_priority()
