#!/usr/bin/env python3
"""
Test specific case: Acrylic Full Set, Basic Manicure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_basic_manicure_case():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Basic Manicure Case...")
    print("=" * 60)
    
    # Test the specific failing case
    print("📨 Testing: Acrylic Full Set, Basic Manicure...")
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "I want Acrylic Full Set and Basic Manicure for Friday at 3pm"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        booking_state = data.get('booking_state', {})
        
        print(f"📝 Services Requested: {booking_state.get('services_requested', 'None')}")
        print(f"📋 Services Array: {len(booking_state.get('services', []))} services")
        print(f"💰 Total Price: ${booking_state.get('totalPrice', 0)}")
        print(f"⏱️ Total Duration: {booking_state.get('totalDuration', 0)} minutes")
        
        # Check services
        services = booking_state.get('services', [])
        expected_total = 55 + 25  # Acrylic Full Set ($55) + Basic Manicure ($25)
        expected_duration = 90 + 35  # 90 min + 35 min
        
        if len(services) == 2:
            print("✅ SUCCESS: Both services found!")
            for i, service in enumerate(services):
                print(f"   Service {i+1}: Price=${service.get('price', 0)}, Duration={service.get('duration', 0)}min")
        else:
            print(f"❌ ISSUE: Expected 2 services, got {len(services)}")
            
        if booking_state.get('totalPrice', 0) == expected_total:
            print(f"✅ SUCCESS: Correct total price ${expected_total}")
        else:
            print(f"❌ ISSUE: Expected ${expected_total}, got ${booking_state.get('totalPrice', 0)}")
            
    else:
        print(f"❌ Request failed: {start_response.status_code}")

if __name__ == "__main__":
    test_basic_manicure_case()
