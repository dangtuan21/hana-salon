#!/usr/bin/env python3
"""
Test to ensure no placeholder text is generated
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_placeholder_issue():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Placeholder Text Issue...")
    print("=" * 60)
    
    # Step 1: Start with service request (no customer info)
    print("📨 Step 1: Request service without customer info...")
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "I want Acrylic Full Set and Gel Manicure"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        session_id = data["session_id"]
        print(f"📝 Response: {data['response']}")
        
        # Step 2: Provide customer info (no date/time)
        print("\n📨 Step 2: Provide customer info...")
        continue_response = requests.post(f"{base_url}/conversation/continue", json={
            "session_id": session_id,
            "message": "I'm John Smith, phone 555-1234"
        })
        
        if continue_response.status_code == 200:
            continue_data = continue_response.json()
            response_text = continue_data['response']
            print(f"📝 Response: {response_text}")
            
            # Check for placeholder text
            has_placeholder = any(placeholder in response_text for placeholder in [
                '[insert', 'formatted_date', 'formatted_time', '[formatted_date]', '[formatted_time]'
            ])
            
            asks_for_datetime = any(phrase in response_text.lower() for phrase in [
                'when would you like', 'what time', 'what date', 'when do you want'
            ])
            
            if has_placeholder:
                print("❌ ISSUE: Response contains placeholder text")
            elif asks_for_datetime:
                print("✅ SUCCESS: System asks for date/time (no placeholders)")
            else:
                print("? UNCLEAR: Response doesn't contain placeholders but doesn't ask for date/time")
                
        else:
            print(f"❌ Continue request failed: {continue_response.status_code}")
    else:
        print(f"❌ Start request failed: {start_response.status_code}")

if __name__ == "__main__":
    test_placeholder_issue()
