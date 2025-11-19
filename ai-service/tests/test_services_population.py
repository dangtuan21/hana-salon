#!/usr/bin/env python3
"""
Test if services array gets populated from services_requested
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_services_population():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Services Array Population...")
    print("=" * 60)
    
    # Test with multiple services
    print("📨 Testing: Multiple services request...")
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "I want Gel Manicure and Acrylic Full Set for Friday at 2pm"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        booking_state = data.get('booking_state', {})
        
        print(f"📝 Services Requested: {booking_state.get('services_requested', 'None')}")
        print(f"📋 Services Array: {booking_state.get('services', [])}")
        print(f"💰 Total Price: ${booking_state.get('totalPrice', 0)}")
        print(f"⏱️ Total Duration: {booking_state.get('totalDuration', 0)} minutes")
        
        # Check if services array is populated
        services = booking_state.get('services', [])
        if services:
            print("✅ SUCCESS: Services array is populated!")
            for i, service in enumerate(services):
                print(f"   Service {i+1}: ID={service.get('serviceId', 'N/A')}, Price=${service.get('price', 0)}, Duration={service.get('duration', 0)}min")
        else:
            print("❌ ISSUE: Services array is empty")
            
        # Check totals
        total_price = booking_state.get('totalPrice', 0)
        total_duration = booking_state.get('totalDuration', 0)
        if total_price > 0 and total_duration > 0:
            print(f"✅ SUCCESS: Totals calculated - ${total_price}, {total_duration} minutes")
        else:
            print("❌ ISSUE: Totals not calculated")
            
    else:
        print(f"❌ Request failed: {start_response.status_code}")

if __name__ == "__main__":
    test_services_population()
