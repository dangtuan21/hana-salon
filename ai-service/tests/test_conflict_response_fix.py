#!/usr/bin/env python3
"""
Test that the system properly responds to scheduling conflicts with alternative suggestions
instead of saying "Perfect! Your appointment is available"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_conflict_response():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Conflict Response Fix...")
    print("=" * 60)
    
    # Try to book at a time that should conflict (Monday 1pm)
    print("📨 Step 1: Requesting conflicted time...")
    
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "Hi, I'm Alex, phone 555-TEST. I want Gel Manicure for Monday at 1pm"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        session_id = data.get('session_id')
        
        print(f"✅ Session created: {session_id}")
        
        # Confirm to trigger conflict detection
        print(f"\n📨 Step 2: Confirming to trigger conflict detection...")
        
        confirm_response = requests.post(f"{base_url}/conversation/continue", json={
            "session_id": session_id,
            "message": "yes"
        })
        
        if confirm_response.status_code == 200:
            confirm_data = confirm_response.json()
            response_text = confirm_data.get('response', '')
            actions_taken = confirm_data.get('actions_taken', [])
            
            print(f"🔧 Actions Taken: {actions_taken}")
            print(f"💬 System Response: '{response_text}'")
            
            # Check if response properly handles conflict
            conflict_handled_properly = (
                "conflict" in response_text.lower() or 
                "alternative" in response_text.lower() or
                "available" in response_text.lower() and "perfect" not in response_text.lower()
            )
            
            misleading_response = (
                "perfect" in response_text.lower() and 
                "available and confirmed" in response_text.lower()
            )
            
            print(f"\n🎯 RESPONSE ANALYSIS:")
            
            if misleading_response:
                print(f"   ❌ MISLEADING RESPONSE: Still saying 'Perfect! Available and confirmed'")
                print(f"   🔍 This is incorrect when there's a scheduling conflict")
                return False
            elif conflict_handled_properly:
                print(f"   ✅ PROPER CONFLICT HANDLING: Response mentions conflict/alternatives")
                
                # Check if alternatives are mentioned
                if "alternative" in response_text.lower():
                    print(f"   ✅ ALTERNATIVES MENTIONED: System suggests other times")
                
                # Check if specific times are mentioned
                time_mentioned = any(time in response_text for time in ["9:00", "11:00", "11:30", "9am", "11am"])
                if time_mentioned:
                    print(f"   ✅ SPECIFIC TIMES: Alternative times are specified")
                
                print(f"\n   🎉 SUCCESS: Conflict response is now accurate and helpful!")
                return True
            else:
                print(f"   ⚠️  UNCLEAR: Response doesn't clearly indicate conflict or availability")
                print(f"   📝 Response: '{response_text}'")
                return False
                
        else:
            print(f"❌ Confirmation failed: {confirm_response.status_code}")
            return False
    else:
        print(f"❌ Start request failed: {start_response.status_code}")
        return False

if __name__ == "__main__":
    success = test_conflict_response()
    if success:
        print(f"\n🎉 CONFLICT RESPONSE FIX: WORKING CORRECTLY!")
    else:
        print(f"\n❌ CONFLICT RESPONSE FIX: NEEDS MORE WORK")
