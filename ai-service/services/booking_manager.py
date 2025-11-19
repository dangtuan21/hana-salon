"""
Booking State Management Service

Handles all booking state operations including updates, validation,
and services array population.
"""

from typing import Dict, List, Any
from database.booking_state import BookingState, ServiceTechnicianPair, ConfirmationStatus
from services.date_parser import parse_date, parse_time


class BookingManager:
    """Manages booking state operations"""
    
    def __init__(self):
        pass
    
    def update_booking_state(self, session_state: Dict, updates: Dict) -> None:
        """Update booking state with LLM extracted information"""
        
        # Get BookingState object from session
        booking_state = BookingState.from_dict(session_state["booking_state"])
        
        # Track what was updated for confirmation logic
        date_updated = False
        time_updated = False
        
        # Update fields if they exist in updates
        for field, value in updates.items():
            if hasattr(booking_state, field) and value:
                old_value = getattr(booking_state, field)
                if old_value != value:
                    setattr(booking_state, field, value)
                    print(f"🔍 Updated {field}: '{old_value}' -> '{value}'")
                    
                    # Track date/time updates for confirmation
                    if field == 'date_requested':
                        date_updated = True
                        print(f"📝 Updated date_requested: {value}")
                    elif field == 'time_requested':
                        time_updated = True
                        print(f"📝 Updated time_requested: {value}")
        
        # Populate services array if ready
        self.populate_services_if_ready(booking_state, session_state)
        
        # Check if we need confirmation for new date/time
        # BUT ONLY if there's no existing pending confirmation AND customer info is complete
        customer_info_complete = booking_state.customer_name and booking_state.customer_phone
        if (date_updated or time_updated) and booking_state.dateTimeConfirmationStatus == ConfirmationStatus.PENDING and not session_state.get("pending_confirmation") and customer_info_complete:
            date = booking_state.date_requested
            time = booking_state.time_requested
            
            if date and time:
                parsed_date = parse_date(date)
                parsed_time = parse_time(time)
                
                if parsed_date and parsed_time:
                    needs_confirmation = self.needs_date_confirmation(date, time, parsed_date, parsed_time)
                    
                    if needs_confirmation:
                        # Create pending confirmation
                        # Convert parsed_date string to datetime object for formatting
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(parsed_date)
                        time_obj = datetime.strptime(parsed_time, "%H:%M").time()
                        
                        formatted_date = date_obj.strftime("%A, %B %d")
                        formatted_time = time_obj.strftime("%-I%p").lower()
                        
                        session_state["pending_confirmation"] = {
                            "type": "datetime",
                            "original_date": date,
                            "original_time": time,
                            "parsed_date": parsed_date,
                            "parsed_time": parsed_time,
                            "formatted_date": formatted_date,
                            "formatted_time": formatted_time,
                            "services": booking_state.services_requested or "your appointment"
                        }
                        
                        print(f"❓ Created pending confirmation for {formatted_date} at {formatted_time}")
        
        # Update session with modified BookingState
        session_state["booking_state"] = booking_state.to_dict()
    
    def populate_services_if_ready(self, booking_state: BookingState, session_state: Dict) -> None:
        """Populate services array if we have both requested services and available services"""
        
        # Only populate if we have services_requested and services array needs population
        if not booking_state.services_requested:
            return
        
        # Parse requested services
        requested_service_names = [name.strip() for name in booking_state.services_requested.split(',')]
        
        # Only populate if we have available_services data
        if not booking_state.available_services:
            return
        
        # Check if current services match exactly what's requested
        if booking_state.services:
            current_service_count = len(booking_state.services)
            requested_service_count = len(requested_service_names)
            
            # If we have the exact number of requested services, check if they match
            if current_service_count == requested_service_count:
                # Get current service names to compare
                available_services_by_id = {svc.get('_id') if isinstance(svc, dict) else svc._id: 
                                          svc.get('name') if isinstance(svc, dict) else svc.name 
                                          for svc in booking_state.available_services}
                
                current_service_names = []
                for service in booking_state.services:
                    service_name = available_services_by_id.get(service.serviceId, '')
                    current_service_names.append(service_name)
                
                # If current services match requested services, no need to repopulate
                if set(current_service_names) == set(requested_service_names):
                    return
        
        # Clear existing services and rebuild from requested services
        service_pairs = []
        existing_service_ids = set()
        
        # Start fresh with totals
        total_duration = 0
        total_price = 0.0
        
        for service_name in requested_service_names:
            # Find the service in available_services
            matching_service = None
            for available_service in booking_state.available_services:
                # Handle both dict and ServiceInfo object formats
                if hasattr(available_service, 'name'):
                    # ServiceInfo object
                    service_name_check = available_service.name.lower()
                    service_id = available_service._id
                    service_duration = available_service.duration_minutes
                    service_price = available_service.price
                else:
                    # Dictionary format
                    service_name_check = available_service.get('name', '').lower()
                    service_id = available_service.get('_id')
                    service_duration = available_service.get('duration_minutes', 0)
                    service_price = available_service.get('price', 0.0)
                
                if service_name_check == service_name.lower():
                    matching_service = {
                        '_id': service_id,
                        'name': service_name,
                        'duration_minutes': service_duration,
                        'price': service_price
                    }
                    break
            
            if matching_service:
                # Create ServiceTechnicianPair (without technician for now)
                service_pair = ServiceTechnicianPair(
                    serviceId=matching_service['_id'],
                    technicianId=None,  # Will be set during availability check
                    duration=matching_service['duration_minutes'],
                    price=matching_service['price']
                )
                service_pairs.append(service_pair)
                total_duration += matching_service['duration_minutes']
                total_price += matching_service['price']
                print(f"📋 Added service: {service_name} (${matching_service['price']}, {matching_service['duration_minutes']} min)")
        
        # Update booking state if we found any matching services
        if service_pairs:
            booking_state.services = service_pairs
            booking_state.totalDuration = total_duration
            booking_state.totalPrice = total_price
            print(f"💰 Total: ${total_price}, {total_duration} minutes")
    
    def is_booking_ready(self, booking_state_dict: Dict) -> bool:
        """Check if booking has all required information"""
        booking_state = BookingState.from_dict(booking_state_dict)
        return booking_state.is_ready_for_booking()
    
    def needs_date_confirmation(self, original_date: str, original_time: str, parsed_date: str, parsed_time: str) -> bool:
        """Check if the parsed date/time needs confirmation from the user"""
        # Relative dates that need confirmation
        relative_dates = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                         'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
                         'tomorrow', 'today', 'next week', 'this week']
        
        date_lower = original_date.lower()
        time_lower = original_time.lower()
        
        # Check if date is relative
        if any(rel_date in date_lower for rel_date in relative_dates):
            return True
        
        # Check for ambiguous times (numbers without AM/PM)
        if any(hour in time_lower for hour in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']):
            if 'am' not in time_lower and 'pm' not in time_lower:
                # Ambiguous time without AM/PM
                return True
        
        return False
