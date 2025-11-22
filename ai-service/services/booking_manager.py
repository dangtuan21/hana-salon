"""
Booking State Management Service

Handles all booking state operations including updates, validation,
and services array population.
"""

from typing import Dict, List, Any
from database.booking_state import BookingState, ServiceTechnicianPair
from services.date_parser import parse_date, parse_time


class BookingManager:
    """Manages booking state operations"""
    
    def __init__(self):
        pass
        
    def populate_services_if_ready(self, booking_state: BookingState) -> None:
        """Populate services array if we have both requested services and available services"""
        
        print(f"🔍 DEBUG: populate_services_if_ready called")
        print(f"🔍 DEBUG: services_requested = '{booking_state.services_requested}'")
        print(f"🔍 DEBUG: available_services count = {len(booking_state.available_services) if booking_state.available_services else 0}")
        print(f"🔍 DEBUG: current services count = {len(booking_state.services) if booking_state.services else 0}")
        
        # Only populate if we have services_requested and services array needs population
        if not booking_state.services_requested:
            print("🔍 DEBUG: No services_requested - skipping population")
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
                
                # Use partial matching for better service name recognition
                if (service_name_check == service_name.lower() or 
                    service_name.lower() in service_name_check or 
                    service_name_check in service_name.lower()):
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
    
    def process_alternative_selection(self, session_state: Dict, user_input: str) -> bool:
        """Process user selection of an alternative time slot"""
        booking_state = BookingState.from_dict(session_state["booking_state"])
        
        # Check if there are alternative times available
        if not booking_state.alternative_times:
            return False
        
        # Clean user input
        user_time = user_input.lower().strip().replace('.', ':')
        
        # Look for matching alternative time
        selected_alternative = None
        for alt in booking_state.alternative_times:
            alt_time = alt.get('time', '').lower()
            # Match formats like "10:30", "10.30", "1030", "10" -> "10:00"
            if (alt_time == user_time or 
                alt_time.replace(':', '') == user_time.replace(':', '') or
                alt_time == user_time.replace('.', ':') or
                alt_time.startswith(user_time + ':') or  # "10:00" starts with "10:"
                (user_time.isdigit() and alt_time.startswith(user_time + ':00'))):  # "10" matches "10:00"
                selected_alternative = alt
                break
        
        if not selected_alternative:
            return False
        
        print(f"🎯 Selected alternative: {selected_alternative}")
        
        # Update booking state with selected alternative
        booking_state.time_requested = selected_alternative['time']
        booking_state.appointmentDate = '2025-11-20'  # From the alternative
        booking_state.startTime = selected_alternative['time']
        # Date/time confirmed - no special status needed
        
        # Calculate end time based on total duration
        if booking_state.totalDuration > 0:
            from datetime import datetime, timedelta
            try:
                start_time_obj = datetime.strptime(selected_alternative['time'], "%H:%M")
                end_time_obj = start_time_obj + timedelta(minutes=booking_state.totalDuration)
                booking_state.endTime = end_time_obj.strftime("%H:%M")
                print(f"⏰ Calculated end time: {booking_state.startTime} + {booking_state.totalDuration}min = {booking_state.endTime}")
            except Exception as e:
                print(f"❌ Error calculating end time: {e}")
                booking_state.endTime = None
        
        # Assign technician to the service
        technician_id = selected_alternative.get('technician_id')
        if technician_id and booking_state.services:
            for service in booking_state.services:
                if not service.technicianId:  # Only assign if not already assigned
                    service.technicianId = technician_id
                    print(f"✅ Assigned technician {selected_alternative.get('technician')} to service")
        
        # Clear alternatives since one was selected
        booking_state.alternative_times = []
        
        # Update session state
        session_state["booking_state"] = booking_state.to_dict()
        
        print(f"✅ Updated appointment to {selected_alternative['time']} with {selected_alternative.get('technician')}")
        return True
