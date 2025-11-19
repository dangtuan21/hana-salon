#!/usr/bin/env python3
"""
Test the date confirmation formatting fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_date_confirmation_fix():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Date Confirmation Fix...")
    print("=" * 60)
    
    # Test with relative date that should trigger confirmation
    print("📨 Testing: Request with relative date (Monday)...")
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "I'm John Smith, phone 555-1234. I want Gel Manicure for Monday at 2pm"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        response_text = data.get('response', '')
        booking_state = data.get('booking_state', {})
        
        print(f"📝 Response: {response_text}")
        print(f"📋 Services Requested: {booking_state.get('services_requested', 'None')}")
        print(f"📅 Date Requested: {booking_state.get('date_requested', 'None')}")
        print(f"🕐 Time Requested: {booking_state.get('time_requested', 'None')}")
        
        # Check if confirmation was created without error
        has_confirmation = "confirm" in response_text.lower()
        has_error_message = "trouble processing" in response_text.lower()
        
        if has_error_message:
            print("❌ ERROR: System returned error message")
        elif has_confirmation:
            print("✅ SUCCESS: Confirmation message generated without error")
        else:
            print("? INFO: No confirmation generated (might be expected)")
            
    else:
        print(f"❌ Request failed: {start_response.status_code}")

if __name__ == "__main__":
    test_date_confirmation_fix()
