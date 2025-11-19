#!/usr/bin/env python3
"""
Test script to call the API endpoints and trigger debug logs
"""

import requests
import json

def test_api_conversation():
    print("🧪 Testing API conversation endpoints...")
    print("=" * 60)
    
    api_url = "http://localhost:8060"
    
    # Test message
    test_message = "Hi, I'm Teo and my phone is 555-1234. I want to book a Gel Manicure for Monday at 1 PM."
    
    print(f"📨 Sending API request to start conversation...")
    print(f"Message: {test_message}")
    print("-" * 60)
    
    try:
        # Start conversation via API
        response = requests.post(
            f"{api_url}/conversation/start",
            json={
                "message": test_message,
                "customer_phone": ""
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response received:")
            print(f"Session ID: {data.get('session_id')}")
            print(f"Response: {data.get('response')}")
            print(f"Booking State: {json.dumps(data.get('booking_state'), indent=2)}")
            print(f"Actions Taken: {data.get('actions_taken')}")
        else:
            print(f"❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error calling API: {e}")

if __name__ == "__main__":
    test_api_conversation()
