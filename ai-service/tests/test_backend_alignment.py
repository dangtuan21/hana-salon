#!/usr/bin/env python3
"""
Test script to demonstrate BookingState alignment with backend IBooking
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    BookingState, 
    BookingStatus, 
    PaymentStatus, 
    PaymentMethod,
    ServiceStatus,
    TechnicianInfo, 
    ServiceInfo, 
    ServiceTechnicianPair, 
    BookingRating
)

def test_backend_alignment():
    print("🧪 Testing BookingState alignment with Backend IBooking")
    print("=" * 60)
    
    # Create a BookingState that matches backend structure
    booking_state = BookingState(
        # Conversation state
        customer_name="Teo",
        customer_phone="555-1234",
        services_requested="Gel Manicure",
        date_requested="Monday",
        time_requested="1 PM",
        
        # Backend IBooking fields
        customerId="customer123",
        appointmentDate="2025-11-24",
        startTime="13:00",
        endTime="13:45",
        status=BookingStatus.CONFIRMED,
        totalDuration=45,
        totalPrice=35.0,
        paymentStatus=PaymentStatus.PENDING,
        notes="Customer prefers window seat"
    )
    
    # Add a service-technician pair (matches backend IServiceTechnicianPair)
    service_pair = ServiceTechnicianPair(
        serviceId="service123",
        technicianId="tech456", 
        duration=45,
        price=35.0,
        status=ServiceStatus.SCHEDULED,
        notes="Use gentle polish"
    )
    booking_state.services.append(service_pair)
    
    print("📋 BookingState created with backend-compatible structure:")
    print()
    
    # Show conversation state
    print("🗣️ Conversation State:")
    print(f"  Customer: {booking_state.customer_name}")
    print(f"  Phone: {booking_state.customer_phone}")
    print(f"  Requested: {booking_state.services_requested}")
    print(f"  Date: {booking_state.date_requested} → {booking_state.appointmentDate}")
    print(f"  Time: {booking_state.time_requested} → {booking_state.startTime}")
    print()
    
    # Show backend-compatible data
    print("🔗 Backend IBooking Compatible Data:")
    backend_data = booking_state.to_backend_booking()
    print(json.dumps(backend_data, indent=2))
    print()
    
    # Show validation
    print("✅ Validation Results:")
    print(f"  Conversation Complete: {booking_state.is_conversation_complete()}")
    print(f"  Ready for Backend: {booking_state.is_ready_for_booking()}")
    print()
    
    print("🎯 Backend API Call Example:")
    print("POST /api/bookings")
    print("Content-Type: application/json")
    print()
    print(json.dumps(backend_data, indent=2))

if __name__ == "__main__":
    test_backend_alignment()
