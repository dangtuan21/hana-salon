#!/usr/bin/env python3
"""
Test the complete booking flow with a different time to avoid conflicts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_success_booking_flow():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing SUCCESS Complete Booking Flow...")
    print("=" * 60)
    
    # Test with a different time to avoid conflicts
    print("📨 Step 1: Starting conversation with different time...")
    
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "Hi, I'm Michael Johnson, phone 555-999-8888. I want Basic Manicure for Monday at 10am"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        session_id = data.get('session_id')
        booking_state = data.get('booking_state', {})
        
        print(f"✅ Initial State:")
        print(f"   Customer: {booking_state.get('customer_name')} ({booking_state.get('customer_phone')})")
        print(f"   Services: {booking_state.get('services_requested')}")
        print(f"   Date/Time: {booking_state.get('date_requested')} at {booking_state.get('time_requested')}")
        print(f"   Services Array: {len(booking_state.get('services', []))} services")
        print(f"   Total: ${booking_state.get('totalPrice')} for {booking_state.get('totalDuration')} minutes")
        
        # Step 2: Confirm to trigger the complete flow
        print(f"\n📨 Step 2: Confirming to trigger complete booking flow...")
        
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
            
            # Success criteria check
            print(f"\n🎯 SUCCESS CRITERIA CHECK:")
            
            success_count = 0
            total_criteria = 8
            
            # 1. Date/Time Confirmed
            if final_booking_state.get('dateTimeConfirmationStatus') == 'confirmed':
                print(f"   ✅ 1. Date/time confirmed")
                success_count += 1
            else:
                print(f"   ❌ 1. Date/time not confirmed")
            
            # 2. Availability Checked
            if any('availability_checked' in str(action).lower() for action in actions_taken):
                print(f"   ✅ 2. Availability check performed")
                success_count += 1
            else:
                print(f"   ❌ 2. Availability check not performed")
            
            # 3. Technician Assigned
            services = final_booking_state.get('services', [])
            if services and all(service.get('technicianId') for service in services):
                print(f"   ✅ 3. All services have technicians assigned")
                success_count += 1
            else:
                print(f"   ❌ 3. Missing technician assignments")
            
            # 4. Customer Created/Found
            if final_booking_state.get('customerId'):
                print(f"   ✅ 4. Customer ID assigned: {final_booking_state.get('customerId')}")
                success_count += 1
            else:
                print(f"   ❌ 4. No customer ID")
            
            # 5. Booking Creation Successful
            if any('booking_created' in str(action).lower() and 'error' not in str(action).lower() and 'failed' not in str(action).lower() for action in actions_taken):
                print(f"   ✅ 5. Booking creation successful")
                success_count += 1
            else:
                print(f"   ❌ 5. Booking creation failed or not attempted")
            
            # 6. Appointment Times Set
            if final_booking_state.get('appointmentDate') and final_booking_state.get('startTime'):
                print(f"   ✅ 6. Appointment times set: {final_booking_state.get('appointmentDate')} {final_booking_state.get('startTime')}")
                success_count += 1
            else:
                print(f"   ❌ 6. Appointment times not set")
            
            # 7. Conversation Complete
            if conversation_complete:
                print(f"   ✅ 7. Conversation marked complete")
                success_count += 1
            else:
                print(f"   ❌ 7. Conversation not complete")
            
            # 8. No Errors in Actions
            error_actions = [action for action in actions_taken if 'failed' in str(action).lower() or 'error' in str(action).lower()]
            if not error_actions:
                print(f"   ✅ 8. No errors in actions")
                success_count += 1
            else:
                print(f"   ❌ 8. Errors found: {error_actions}")
            
            # Final verdict
            success_rate = (success_count / total_criteria) * 100
            print(f"\n📊 OVERALL RESULT: {success_count}/{total_criteria} criteria met ({success_rate:.1f}%)")
            
            if success_count == total_criteria:
                print(f"🎉 PERFECT SUCCESS: Complete booking flow working flawlessly!")
                print(f"   📅 Booking: {final_booking_state.get('appointmentDate')} {final_booking_state.get('startTime')}-{final_booking_state.get('endTime')}")
                print(f"   💰 Total: ${final_booking_state.get('totalPrice')} for {final_booking_state.get('totalDuration')} minutes")
                print(f"   👤 Customer: {final_booking_state.get('customer_name')} (ID: {final_booking_state.get('customerId')})")
                print(f"   🆔 Booking Status: {final_booking_state.get('status')}")
            elif success_count >= 6:
                print(f"✅ SUCCESS: Booking flow working with minor issues")
            elif success_count >= 4:
                print(f"⚠️  PARTIAL SUCCESS: Core functionality working")
            else:
                print(f"❌ NEEDS WORK: Major issues in booking flow")
                
        else:
            print(f"❌ Confirmation failed: {confirm_response.status_code}")
    else:
        print(f"❌ Start request failed: {start_response.status_code}")

if __name__ == "__main__":
    test_success_booking_flow()
