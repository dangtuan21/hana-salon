#!/usr/bin/env python3
"""
Test booking flow with single name customer (no lastName)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_single_name_customer():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Single Name Customer Booking...")
    print("=" * 60)
    
    # Test with single name customer
    print("📨 Step 1: Starting conversation with single name...")
    
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "Hi, I'm Teo, phone 333-333-3333. I want Gel Manicure for Tuesday at 11am"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        session_id = data.get('session_id')
        booking_state = data.get('booking_state', {})
        
        print(f"✅ Initial State:")
        print(f"   Customer: {booking_state.get('customer_name')} ({booking_state.get('customer_phone')})")
        print(f"   Services: {booking_state.get('services_requested')}")
        print(f"   Date/Time: {booking_state.get('date_requested')} at {booking_state.get('time_requested')}")
        
        # Step 2: Confirm to trigger the complete flow
        print(f"\n📨 Step 2: Confirming to trigger booking flow...")
        
        confirm_response = requests.post(f"{base_url}/conversation/continue", json={
            "session_id": session_id,
            "message": "yes"
        })
        
        if confirm_response.status_code == 200:
            confirm_data = confirm_response.json()
            final_booking_state = confirm_data.get('booking_state', {})
            response_text = confirm_data.get('response', '')
            actions_taken = confirm_data.get('actions_taken', [])
            conversation_complete = confirm_data.get('conversation_complete', False)
            
            print(f"✅ Final Response: {response_text}")
            print(f"🔧 Actions Taken: {actions_taken}")
            print(f"🏁 Conversation Complete: {conversation_complete}")
            
            # Check results
            customer_created = any('booking_created' in str(action).lower() and 'error' not in str(action).lower() and 'failed' not in str(action).lower() for action in actions_taken)
            customer_id = final_booking_state.get('customerId')
            
            print(f"\n🎯 SINGLE NAME CUSTOMER TEST RESULTS:")
            
            if customer_created and customer_id:
                print(f"   ✅ SUCCESS: Single name customer booking created!")
                print(f"   👤 Customer: {final_booking_state.get('customer_name')}")
                print(f"   🆔 Customer ID: {customer_id}")
                print(f"   📅 Appointment: {final_booking_state.get('appointmentDate')} {final_booking_state.get('startTime')}")
                print(f"   💰 Total: ${final_booking_state.get('totalPrice')}")
                print(f"   🎉 BACKEND NOW ACCEPTS EMPTY LASTNAME AND EMAIL!")
            else:
                print(f"   ❌ FAILED: Customer creation still failing")
                print(f"   🔍 Actions: {actions_taken}")
                
        else:
            print(f"❌ Confirmation failed: {confirm_response.status_code}")
    else:
        print(f"❌ Start request failed: {start_response.status_code}")

if __name__ == "__main__":
    test_single_name_customer()
