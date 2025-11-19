#!/usr/bin/env python3
"""
Test to reproduce the November 3 issue
"""

import requests
import json

def test_current_issue():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Current November 3 Issue...")
    print("=" * 60)
    
    # Start fresh conversation
    print("📨 Step 1: Start conversation with 'Fri, 3pm'...")
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "I want a Basic Manicure for Fri, 3pm"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        session_id = data["session_id"]
        print(f"📝 Response: {data['response']}")
        
        # Check if it shows correct date
        response_text = data['response'].lower()
        if "november 21" in response_text:
            print("✅ SUCCESS: Shows correct November 21")
        elif "november 3" in response_text:
            print("❌ ISSUE: Still shows November 3")
        else:
            print("? No specific date mentioned in first response")
        
        # Try confirming
        print("\n📨 Step 2: Confirm with 'yes'...")
        confirm_response = requests.post(f"{base_url}/conversation/continue", json={
            "session_id": session_id,
            "message": "yes"
        })
        
        if confirm_response.status_code == 200:
            confirm_data = confirm_response.json()
            print(f"📝 Confirmation Response: {confirm_data['response']}")
            
            # Check final response for date
            final_text = confirm_data['response'].lower()
            if "november 21" in final_text:
                print("✅ SUCCESS: Final response shows November 21")
            elif "november 3" in final_text:
                print("❌ ISSUE: Final response shows November 3")
            else:
                print("? No specific date in final response")
        else:
            print(f"❌ Confirmation failed: {confirm_response.status_code}")
    else:
        print(f"❌ Start failed: {start_response.status_code}")

if __name__ == "__main__":
    test_current_issue()
