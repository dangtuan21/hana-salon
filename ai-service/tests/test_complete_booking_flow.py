#!/usr/bin/env python3
"""
Test the complete booking flow: Confirmation → Availability → Booking Creation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_complete_booking_flow():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Complete Booking Flow...")
    print("=" * 60)
    
    # Test complete flow with multi-service booking
    print("📨 Step 1: Starting conversation with multi-service request...")
    
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "Hi, I'm Emma Wilson, phone 555-7777. I want Acrylic Full Set and Basic Manicure for Thursday at 11am"
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
        
        # Step 2: Confirm to trigger availability check and booking creation
        print(f"\n📨 Step 2: Confirming to trigger full flow...")
        
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
            
            # Analyze final booking state
            print(f"\n📋 Final Booking State Analysis:")
            print(f"   Confirmation Status: {final_booking_state.get('dateTimeConfirmationStatus')}")
            print(f"   Appointment Date: {final_booking_state.get('appointmentDate')}")
            print(f"   Time Slot: {final_booking_state.get('startTime')}-{final_booking_state.get('endTime')}")
            print(f"   Customer ID: {final_booking_state.get('customerId')}")
            print(f"   Booking Status: {final_booking_state.get('status')}")
            
            # Check service assignments
            services = final_booking_state.get('services', [])
            print(f"\n🔍 Service Assignments ({len(services)} services):")
            all_assigned = True
            for i, service in enumerate(services):
                tech_id = service.get('technicianId')
                if tech_id:
                    print(f"   Service {i+1}: ✅ Assigned to technician {tech_id}")
                else:
                    print(f"   Service {i+1}: ❌ No technician assigned")
                    all_assigned = False
            
            # Overall assessment
            print(f"\n📊 Flow Assessment:")
            
            success_indicators = []
            issues = []
            
            # Check each step
            if "availability_checked" in str(actions_taken) or "CHECKED_AVAILABILITY" in str(actions_taken):
                success_indicators.append("✅ Availability check completed")
            else:
                issues.append("❌ Availability check not performed")
            
            if "booking_created" in str(actions_taken) or "BOOKING_CREATED" in str(actions_taken):
                success_indicators.append("✅ Booking creation attempted")
            else:
                issues.append("❌ Booking creation not attempted")
            
            if final_booking_state.get('dateTimeConfirmationStatus') == 'confirmed':
                success_indicators.append("✅ Date/time confirmed")
            else:
                issues.append("❌ Date/time not confirmed")
            
            if all_assigned:
                success_indicators.append("✅ All services have technicians")
            else:
                issues.append("❌ Some services missing technicians")
            
            if conversation_complete:
                success_indicators.append("✅ Conversation marked complete")
            else:
                issues.append("❌ Conversation not complete")
            
            if final_booking_state.get('customerId'):
                success_indicators.append("✅ Customer ID assigned")
            else:
                issues.append("❌ No customer ID")
            
            # Print results
            for indicator in success_indicators:
                print(f"   {indicator}")
            
            for issue in issues:
                print(f"   {issue}")
            
            # Final verdict
            if len(issues) == 0:
                print(f"\n🎉 SUCCESS: Complete booking flow working perfectly!")
                print(f"   📅 Booking: {final_booking_state.get('appointmentDate')} {final_booking_state.get('startTime')}-{final_booking_state.get('endTime')}")
                print(f"   💰 Total: ${final_booking_state.get('totalPrice')} for {final_booking_state.get('totalDuration')} minutes")
                print(f"   👤 Customer: {final_booking_state.get('customer_name')} (ID: {final_booking_state.get('customerId')})")
            elif len(issues) <= 2:
                print(f"\n⚠️  PARTIAL SUCCESS: Flow mostly working with minor issues")
            else:
                print(f"\n❌ ISSUES FOUND: Flow needs attention")
                
        else:
            print(f"❌ Confirmation failed: {confirm_response.status_code}")
    else:
        print(f"❌ Start request failed: {start_response.status_code}")

if __name__ == "__main__":
    test_complete_booking_flow()
