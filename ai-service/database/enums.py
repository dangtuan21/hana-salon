"""
Enums for the booking system
"""

from enum import Enum


class BookingAction(str, Enum):
    """Enum for booking actions that can be executed"""
    CHECK_AVAILABILITY = "check_availability"
    CONFIRM_DATETIME = "confirm_datetime"
    GET_TECHNICIANS = "get_technicians"
    CREATE_BOOKING = "create_booking"
    CALCULATE_COST = "calculate_cost"
    GET_SERVICES = "get_services"
    UPDATE_BOOKING = "update_booking"
    CANCEL_BOOKING = "cancel_booking"


class ActionResult(str, Enum):
    """Enum for action execution results"""
    CHECKED_AVAILABILITY = "availability_checked"
    RETRIEVED_TECHNICIANS = "technicians_retrieved"
    BOOKING_CREATED = "booking_created"
    BOOKING_NOT_READY = "booking_not_ready"
    COST_CALCULATED = "cost_calculated"
    SERVICES_RETRIEVED = "services_retrieved"
    BOOKING_UPDATED = "booking_updated"
    BOOKING_UPDATE_FAILED = "booking_update_failed"
    BOOKING_CANCELLED = "booking_cancelled"
    UNKNOWN_ACTION = "unknown_action"
