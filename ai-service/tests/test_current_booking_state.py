#!/usr/bin/env python3
"""
Get the current booking state in JSON format
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def get_current_booking_state():
    base_url = "http://localhost:8060"
    
    print("🔍 Getting Current BookingState...")
    print("=" * 60)
    
    # Start a fresh conversation to get current state
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "Hi, I'm John Doe, phone 555-9999. I want Gel Manicure for Friday at 3pm"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        session_id = data.get('session_id')
        booking_state = data.get('booking_state', {})
        
        print("📋 **INITIAL BOOKING STATE (JSON):**")
        print(json.dumps(booking_state, indent=2))
        
        # Confirm to trigger availability check
        print("\n" + "="*60)
        print("📨 Confirming to trigger availability check...")
        
        confirm_response = requests.post(f"{base_url}/conversation/continue", json={
            "session_id": session_id,
            "message": "yes"
        })
        
        if confirm_response.status_code == 200:
            confirm_data = confirm_response.json()
            final_booking_state = confirm_data.get('booking_state', {})
            
            print("\n📋 **FINAL BOOKING STATE AFTER AVAILABILITY CHECK (JSON):**")
            print(json.dumps(final_booking_state, indent=2))
            
            # Summary
            print("\n" + "="*60)
            print("📊 **BOOKING SUMMARY:**")
            print(f"Customer: {final_booking_state.get('customer_name')} ({final_booking_state.get('customer_phone')})")
            print(f"Services: {final_booking_state.get('services_requested')}")
            print(f"Date: {final_booking_state.get('appointmentDate')} at {final_booking_state.get('startTime')}-{final_booking_state.get('endTime')}")
            print(f"Confirmation Status: {final_booking_state.get('dateTimeConfirmationStatus')}")
            print(f"Total: ${final_booking_state.get('totalPrice')} for {final_booking_state.get('totalDuration')} minutes")
            
            services = final_booking_state.get('services', [])
            print(f"Service Assignments: {len(services)} service(s)")
            for i, service in enumerate(services):
                tech_id = service.get('technicianId')
                status = "✅ Assigned" if tech_id else "❌ No technician"
                print(f"  Service {i+1}: {status}")
                
        else:
            print(f"❌ Confirmation failed: {confirm_response.status_code}")
    else:
        print(f"❌ Start request failed: {start_response.status_code}")

if __name__ == "__main__":
    get_current_booking_state()
