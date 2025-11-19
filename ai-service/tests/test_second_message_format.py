#!/usr/bin/env python3
"""
Test if the LLM uses the formatted date in the second message
"""

import requests
import json

def test_second_message_format():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Second Message Format...")
    print("=" * 60)
    
    # Start conversation
    print("📨 Step 1: Start conversation...")
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "Hi, I'm Bob and my phone is 555-7777. I want a Gel Manicure."
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        session_id = data["session_id"]
        print(f"📝 First Response: {data['response']}")
        
        # Continue with relative date
        print("\n📨 Step 2: Provide relative date...")
        continue_response = requests.post(f"{base_url}/conversation/continue", json={
            "session_id": session_id,
            "message": "Wednesday at 3pm"
        })
        
        if continue_response.status_code == 200:
            continue_data = continue_response.json()
            print(f"📝 Second Response: {continue_data['response']}")
            
            # Check if it shows the improved format
            response_text = continue_data['response'].lower()
            if "wednesday" in response_text and "november" in response_text:
                print("✅ SUCCESS: Shows improved format in second message!")
            else:
                print("❌ Still using old format in second message")
        else:
            print(f"❌ Continue failed: {continue_response.status_code}")
    else:
        print(f"❌ Start failed: {start_response.status_code}")

if __name__ == "__main__":
    test_second_message_format()
