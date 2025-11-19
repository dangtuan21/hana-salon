#!/usr/bin/env python3
"""
Test the improved date/time confirmation format
"""

import requests
import json

def test_new_confirmation_format():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Improved Confirmation Format...")
    print("=" * 60)
    
    # Test with Wednesday (should show "Wednesday, November 19")
    print("📨 Testing: Wednesday at 3pm")
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "Hi, I'm Alice and my phone is 555-9999. I want to book a Gel Manicure for Wednesday at 3pm."
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        print(f"📝 Response: {data['response']}")
        print(f"🎯 Actions: {data['actions_taken']}")
        
        # Check if it shows the improved format
        response_text = data['response'].lower()
        if "wednesday" in response_text and "november" in response_text:
            print("✅ SUCCESS: Shows improved format with day name and full date!")
        else:
            print("❌ Still using old format")
    else:
        print(f"❌ Request failed: {start_response.status_code}")

if __name__ == "__main__":
    test_new_confirmation_format()
