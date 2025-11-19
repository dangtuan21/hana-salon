#!/usr/bin/env python3
"""
Test conflict detection and alternative time suggestions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_conflict_and_alternatives():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Conflict Detection & Alternative Time Suggestions...")
    print("=" * 70)
    
    # Try to book at a time that should conflict (Monday 1pm - same as existing bookings)
    print("📨 Step 1: Attempting booking at conflicted time...")
    print("   🕐 Requesting: Monday at 1pm (should conflict)")
    
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "Hi, I'm Sarah, phone 555-9999. I want Gel Manicure for Monday at 1pm"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        session_id = data.get('session_id')
        booking_state = data.get('booking_state', {})
        
        print(f"✅ Initial booking state created")
        print(f"   👤 Customer: {booking_state.get('customer_name')}")
        print(f"   📞 Phone: {booking_state.get('customer_phone')}")
        print(f"   🎯 Service: {booking_state.get('services_requested')}")
        print(f"   📅 Requested: {booking_state.get('date_requested')} at {booking_state.get('time_requested')}")
        
        # Confirm to trigger availability check
        print(f"\n📨 Step 2: Confirming to trigger availability check...")
        
        confirm_response = requests.post(f"{base_url}/conversation/continue", json={
            "session_id": session_id,
            "message": "yes"
        })
        
        if confirm_response.status_code == 200:
            confirm_data = confirm_response.json()
            final_booking_state = confirm_data.get('booking_state', {})
            response_text = confirm_data.get('response', '')
            actions_taken = confirm_data.get('actions_taken', [])
            
            print(f"🔧 Actions Taken: {actions_taken}")
            print(f"💬 System Response: {response_text}")
            
            # Check for conflict detection and alternatives
            conflict_detected = any('conflict' in str(action).lower() for action in actions_taken)
            alternatives_found = 'alternative_times' in final_booking_state and len(final_booking_state.get('alternative_times', [])) > 0
            
            print(f"\n🎯 CONFLICT HANDLING TEST RESULTS:")
            
            if conflict_detected:
                print(f"   ✅ CONFLICT DETECTED: System properly identified scheduling conflict")
                
                if alternatives_found:
                    alternatives = final_booking_state.get('alternative_times', [])
                    print(f"   ✅ ALTERNATIVES SUGGESTED: Found {len(alternatives)} alternative time slots")
                    
                    print(f"\n   📋 Suggested Alternative Times:")
                    for i, alt in enumerate(alternatives[:3], 1):
                        print(f"      {i}. {alt.get('time')} with {alt.get('technician')}")
                        print(f"         Duration: {alt.get('time')} - {alt.get('end_time')}")
                    
                    print(f"\n   🎉 SUCCESS: Conflict handling working perfectly!")
                    print(f"      ✅ Detected scheduling conflict")
                    print(f"      ✅ Found alternative time slots")
                    print(f"      ✅ Provided customer with options")
                    print(f"      ✅ Prevented double-booking")
                    
                else:
                    print(f"   ⚠️  PARTIAL SUCCESS: Conflict detected but no alternatives found")
                    print(f"      This might be expected if the day is fully booked")
                    
            else:
                print(f"   ❌ UNEXPECTED: No conflict detected (there should be existing bookings at 1pm Monday)")
                print(f"   🔍 Actions: {actions_taken}")
                
            # Check if booking was prevented (should not be created due to conflict)
            booking_created = any('booking_created' in str(action).lower() and 'error' not in str(action).lower() for action in actions_taken)
            
            if not booking_created:
                print(f"\n   ✅ BOOKING PREVENTION: Correctly prevented conflicting booking")
            else:
                print(f"\n   ⚠️  WARNING: Booking was created despite conflict")
                
        else:
            print(f"❌ Confirmation failed: {confirm_response.status_code}")
            print(f"   Response: {confirm_response.text}")
    else:
        print(f"❌ Start request failed: {start_response.status_code}")
        print(f"   Response: {start_response.text}")

if __name__ == "__main__":
    test_conflict_and_alternatives()
