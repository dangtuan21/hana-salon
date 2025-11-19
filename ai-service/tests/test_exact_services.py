#!/usr/bin/env python3
"""
Test to ensure services array matches exactly what's requested
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def test_exact_services():
    base_url = "http://localhost:8060"
    
    print("🧪 Testing Exact Services Matching...")
    print("=" * 60)
    
    # Test with specific 2 services
    print("📨 Testing: Acrylic Full Set, Gel Manicure (2 services)...")
    start_response = requests.post(f"{base_url}/conversation/start", json={
        "message": "I want Acrylic Full Set and Gel Manicure for Friday at 2pm"
    })
    
    if start_response.status_code == 200:
        data = start_response.json()
        booking_state = data.get('booking_state', {})
        
        services_requested = booking_state.get('services_requested', '')
        services_array = booking_state.get('services', [])
        
        print(f"📝 Services Requested: '{services_requested}'")
        print(f"📋 Services Array Count: {len(services_array)}")
        print(f"💰 Total Price: ${booking_state.get('totalPrice', 0)}")
        print(f"⏱️ Total Duration: {booking_state.get('totalDuration', 0)} minutes")
        
        # Parse requested services
        if services_requested:
            requested_names = [name.strip() for name in services_requested.split(',')]
            print(f"🔍 Requested Services: {requested_names}")
            print(f"🔍 Expected Count: {len(requested_names)}")
            
            if len(services_array) == len(requested_names):
                print("✅ SUCCESS: Services array count matches requested count")
                
                # Expected totals for Acrylic Full Set ($55, 90min) + Gel Manicure ($35, 45min)
                expected_price = 90.0  # $55 + $35
                expected_duration = 135  # 90 + 45
                
                actual_price = booking_state.get('totalPrice', 0)
                actual_duration = booking_state.get('totalDuration', 0)
                
                if actual_price == expected_price and actual_duration == expected_duration:
                    print(f"✅ SUCCESS: Correct totals - ${expected_price}, {expected_duration} minutes")
                else:
                    print(f"❌ ISSUE: Expected ${expected_price}, {expected_duration}min but got ${actual_price}, {actual_duration}min")
                    
            elif len(services_array) > len(requested_names):
                print(f"❌ ISSUE: Too many services - got {len(services_array)}, expected {len(requested_names)}")
                print("   This suggests services from previous requests are being kept")
            else:
                print(f"❌ ISSUE: Too few services - got {len(services_array)}, expected {len(requested_names)}")
        else:
            print("❌ No services requested found")
            
    else:
        print(f"❌ Request failed: {start_response.status_code}")

if __name__ == "__main__":
    test_exact_services()
