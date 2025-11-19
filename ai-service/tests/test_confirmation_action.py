#!/usr/bin/env python3
"""
Test if LLM requests confirm_datetime action
"""

import requests
import json

def test_confirmation_action():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Confirmation Action...")
    print("=" * 60)
    
    # Start conversation
    print("📨 Step 1: Start conversation...")
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "Hi, I'm Test and my phone is 555-0000. I want a Gel Manicure for Monday at 2pm."
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        session_id = data["session_id"]
        print(f"📝 First Response: {data['response']}")
        print(f"🎯 First Actions: {data['actions_taken']}")
        
        # Confirm with explicit "yes"
        print("\n📨 Step 2: Confirm with 'yes'...")
        confirm_response = requests.post(f"{base_url}/conversation/continue", json={
            "session_id": session_id,
            "message": "yes"
        })
        
        if confirm_response.status_code == 200:
            confirm_data = confirm_response.json()
            print(f"📝 Confirmation Response: {confirm_data['response']}")
            print(f"🎯 Confirmation Actions: {confirm_data['actions_taken']}")
            
            # Check if confirm_datetime action was used
            actions_str = str(confirm_data['actions_taken'])
            if "confirm_datetime" in actions_str or "datetime_confirmed" in actions_str:
                print("✅ SUCCESS: confirm_datetime action was used!")
            else:
                print("❌ FAIL: confirm_datetime action was NOT used")
                print(f"   Actions were: {confirm_data['actions_taken']}")
        else:
            print(f"❌ Confirmation failed: {confirm_response.status_code}")
    else:
        print(f"❌ Start failed: {start_response.status_code}")

if __name__ == "__main__":
    test_confirmation_action()
