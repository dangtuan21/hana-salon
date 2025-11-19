#!/usr/bin/env python3
"""
Test the date/time confirmation feature
"""

import requests
import json

def test_confirmation_flow():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Date/Time Confirmation Feature...")
    print("=" * 60)
    
    # Start conversation with relative date
    print("📨 Step 1: Start conversation with relative date...")
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "Hi, I'm Teo and my phone is 555-1234. I want to book a Gel Manicure for Thursday at 3pm."
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        session_id = data["session_id"]
        print(f"✅ Session ID: {session_id}")
        print(f"📝 Response: {data['response']}")
        print(f"🎯 Actions: {data['actions_taken']}")
        
        # Check if confirmation is needed
        if "Awaiting confirmation" in str(data['actions_taken']) or "confirm" in data['response'].lower():
            print("\n📨 Step 2: Confirm the date/time...")
            confirm_response = requests.post(f"{base_url}/conversation/continue", json={
                "session_id": session_id,
                "message": "Yes, that's correct"
            })
            
            if confirm_response.status_code == 200:
                confirm_data = confirm_response.json()
                print(f"📝 Confirmation Response: {confirm_data['response']}")
                print(f"🎯 Actions: {confirm_data['actions_taken']}")
                
                # Check booking state
                booking_state = confirm_data.get('booking_state', {})
                print(f"📋 Appointment Date: {booking_state.get('appointmentDate')}")
                print(f"📋 Start Time: {booking_state.get('startTime')}")
            else:
                print(f"❌ Confirmation failed: {confirm_response.status_code}")
        else:
            print("❌ No confirmation requested")
    else:
        print(f"❌ Start conversation failed: {start_response.status_code}")

if __name__ == "__main__":
    test_confirmation_flow()
