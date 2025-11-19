#!/usr/bin/env python3
"""
Test the enhanced availability check functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_availability_check():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Enhanced Availability Check...")
    print("=" * 60)
    
    # Test multi-service availability check
    print("📨 Testing: Multi-service availability check...")
    
    # Start conversation with customer info and multiple services
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "Hi, I'm Sarah Johnson, phone 555-1234. I want Acrylic Full Set and Gel Manicure for Wednesday at 2pm"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        session_id = data.get('session_id')
        booking_state = data.get('booking_state', {})
        
        print(f"📝 Customer: {booking_state.get('customer_name')} ({booking_state.get('customer_phone')})")
        print(f"📋 Services: {booking_state.get('services_requested')}")
        print(f"📅 Date/Time: {booking_state.get('date_requested')} at {booking_state.get('time_requested')}")
        print(f"🔄 Services Array: {len(booking_state.get('services', []))} services")
        
        # Confirm the date/time
        print("\n📨 Confirming date/time...")
        confirm_response = requests.post(f"{base_url}/conversation/continue", json={
            "session_id": session_id,
            "message": "yes"
        })
        
        if confirm_response.status_code == 200:
            confirm_data = confirm_response.json()
            confirm_booking_state = confirm_data.get('booking_state', {})
            
            print(f"✅ Confirmation Status: {confirm_booking_state.get('dateTimeConfirmationStatus')}")
            print(f"📅 Appointment Date: {confirm_booking_state.get('appointmentDate')}")
            print(f"🕐 Start Time: {confirm_booking_state.get('startTime')}")
            print(f"🕐 End Time: {confirm_booking_state.get('endTime')}")
            
            # Check services with technician assignments
            services = confirm_booking_state.get('services', [])
            print(f"\n🔍 Service Assignments:")
            for i, service in enumerate(services):
                tech_id = service.get('technicianId')
                tech_status = "✅ Assigned" if tech_id else "❌ No technician"
                print(f"  Service {i+1}: {service.get('serviceId')} - {tech_status}")
            
            # Check if availability was checked
            response_text = confirm_data.get('response', '')
            if 'available' in response_text.lower():
                print("✅ SUCCESS: Availability check completed")
            elif 'not available' in response_text.lower():
                print("⚠️  INFO: Services not available at requested time")
            else:
                print("? INFO: Availability check status unclear")
                
        else:
            print(f"❌ Confirmation failed: {confirm_response.status_code}")
    else:
        print(f"❌ Start request failed: {start_response.status_code}")

if __name__ == "__main__":
    test_availability_check()
