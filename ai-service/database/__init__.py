"""
Database package for Hana AI Salon Booking System
Contains database and session management classes with explicit type definitions
"""

from .session_manager import SessionManager
from .booking_state import (
    BookingState, 
    BookingStatus, 
    PaymentStatus, 
    PaymentMethod,
    ConfirmationStatus,
    ServiceStatus,
    TechnicianInfo, 
    ServiceInfo, 
    ServiceTechnicianPair, 
    BookingRating
)

__all__ = [
    'SessionManager', 
    'BookingState', 
    'BookingStatus',
    'PaymentStatus',
    'PaymentMethod',
    'ConfirmationStatus',
    'ServiceStatus',
    'TechnicianInfo', 
    'ServiceInfo', 
    'ServiceTechnicianPair',
    'BookingRating'
]
