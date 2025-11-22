#!/usr/bin/env python3
"""
Backend API Client for Hana Salon Booking System
Handles all communication with the backend API
"""

import requests
from typing import Dict, Any, List, Optional
import json


class BackendAPIClient:
    """Client for making HTTP requests to the backend API"""
    
    def __init__(self, base_url: str = "http://localhost:3060"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_service_by_name(self, name: str) -> Optional[Dict]:
        """Get service by name"""
        try:
            url = f"{self.base_url}/api/services/name/{name}"
            print(f"🌐 API CALL: GET {url}")
            response = self.session.get(url)
            print(f"📡 Response: {response.status_code} - {response.text[:200]}...")
            if response.status_code == 200:
                data = response.json().get('data')
                print(f"✅ Service found: {data.get('name') if data else 'None'}")
                return data
            print(f"❌ Service not found: {response.status_code}")
            return None
        except Exception as e:
            print(f"💥 Error getting service by name: {e}")
            return None
    
    def get_available_technicians(self) -> List[Dict]:
        """Get all available technicians"""
        try:
            url = f"{self.base_url}/api/technicians/available"
            print(f"🌐 API CALL: GET {url}")
            response = self.session.get(url)
            print(f"📡 Response: {response.status_code} - {response.text[:200]}...")
            if response.status_code == 200:
                data = response.json().get('data', {}).get('technicians', [])
                print(f"✅ Found available technicians: {len(data)} ")
                return data
            print(f"❌ Failed to get technicians: {response.status_code}")
            return []
        except Exception as e:
            print(f"💥 Error getting available technicians: {e}")
            return []
    
    def get_technicians_for_service(self, service_id: str) -> List[Dict]:
        """Get technicians qualified for a specific service"""
        try:
            url = f"{self.base_url}/api/technicians/service/{service_id}"
            print(f"🌐 API CALL: GET {url}")
            response = self.session.get(url)
            print(f"📡 Response: {response.status_code} - {response.text[:200]}...")
            if response.status_code == 200:
                data = response.json().get('data', {}).get('technicians', [])
                print(f"✅ Found technicians for service: {len(data)}")
                return data
            print(f"❌ No technicians found: {response.status_code}")
            return []
        except Exception as e:
            print(f"💥 Error getting technicians for service: {e}")
            return []
    
    def batch_check_technician_availability(self, technician_ids: List[str], date: str, start_time: str, duration: int) -> Dict:
        """Check availability for multiple technicians at once"""
        try:
            url = f"{self.base_url}/api/technicians/batch-check-availability"
            payload = {
                'technicianIds': technician_ids,
                'date': date,
                'startTime': start_time,
                'duration': duration
            }
            print(f"🌐 BATCH API CALL: POST {url}")
            print(f"📤 Payload: {payload}")
            response = self.session.post(url, json=payload)
            print(f"📡 Response: {response.status_code} - {response.text[:200]}...")
            if response.status_code == 200:
                data = response.json().get('data', {})
                print(f"✅ Batch availability check completed for {len(technician_ids)} technicians")
                return data
            print(f"❌ Batch availability check failed: {response.status_code}")
            return {}
        except Exception as e:
            print(f"💥 Error in batch availability check: {e}")
            return {}
    
    def get_customer_by_phone(self, phone: str) -> Optional[Dict]:
        """Get customer by phone number"""
        try:
            url = f"{self.base_url}/api/customers/phone/{phone}"
            print(f"🌐 API CALL: GET {url}")
            response = self.session.get(url)
            print(f"📡 Response: {response.status_code} - {response.text[:200]}...")
            if response.status_code == 200:
                data = response.json().get('data')
                print(f"✅ Customer found: {data.get('firstName') if data else 'None'}")
                return data
            print(f"❌ Customer not found: {response.status_code}")
            return None
        except Exception as e:
            print(f"💥 Error getting customer by phone: {e}")
            return None
    
    def create_customer(self, customer_data: Dict) -> Optional[Dict]:
        """Create a new customer"""
        try:
            url = f"{self.base_url}/api/customers"
            print(f"🌐 API CALL: POST {url}")
            print(f"📤 Payload: {customer_data}")
            response = self.session.post(url, json=customer_data)
            print(f"📡 Response: {response.status_code} - {response.text[:200]}...")
            if response.status_code == 201:
                data = response.json().get('data')
                print(f"✅ Customer created: {data.get('firstName') if data else 'None'}")
                return data
            print(f"❌ Customer creation failed: {response.status_code}")
            return None
        except Exception as e:
            print(f"💥 Error creating customer: {e}")
            return None
    
    def create_booking(self, booking_data: Dict) -> Optional[Dict]:
        """Create a new booking"""
        try:
            url = f"{self.base_url}/api/bookings"
            print(f"🌐 API CALL: POST {url}")
            print(f"📤 Payload: {json.dumps(booking_data, indent=2)}")
            response = self.session.post(url, json=booking_data)
            print(f"📡 Response: {response.status_code} - {response.text[:200]}...")
            if response.status_code == 201:
                data = response.json().get('data')
                print(f"✅ Booking created: {data.get('_id') if data else 'None'}")
                return data
            print(f"❌ Booking creation failed: {response.status_code}")
            return None
        except Exception as e:
            print(f"💥 Error creating booking: {e}")
            return None
    
    def get_all_services(self) -> List[Dict]:
        """Get all available services"""
        try:
            url = f"{self.base_url}/api/services"
            print(f"🌐 API CALL: GET {url}")
            response = self.session.get(url)
            print(f"📡 Response: {response.status_code} - {response.text[:200]}...")
            if response.status_code == 200:
                data = response.json().get('data', {}).get('services', [])
                print(f"✅ Found services: {len(data)}")
                return data
            print(f"❌ Failed to get services: {response.status_code}")
            return []
        except Exception as e:
            print(f"💥 Error getting all services: {e}")
            return []
    
    def health_check(self) -> Dict:
        """Check backend health status"""
        try:
            url = f"{self.base_url}/api/health"
            print(f"🌐 API CALL: GET {url}")
            response = self.session.get(url)
            print(f"📡 Response: {response.status_code} - {response.text[:200]}...")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend health: {data.get('data', {}).get('status', 'unknown')}")
                return data
            print(f"❌ Health check failed: {response.status_code}")
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            print(f"💥 Error checking backend health: {e}")
            return {'success': False, 'error': str(e)}
