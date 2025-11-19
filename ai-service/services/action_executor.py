"""
Action Execution Service

Handles all booking actions including availability checks, booking creation,
technician lookup, and other booking-related operations.
"""

from typing import Dict, List, Any
from database.booking_state import BookingState, ServiceTechnicianPair, ConfirmationStatus, BookingStatus
from database.enums import BookingAction, ActionResult
from services.date_parser import parse_date, parse_time
from services.backend_client import BackendAPIClient


class ActionExecutor:
    """Executes booking actions identified by the LLM"""
    
    def __init__(self, api_client: BackendAPIClient):
        self.api_client = api_client
    
    def execute_actions(self, session_state: Dict, actions_needed: List[str]) -> List[str]:
        """Execute actions identified by the LLM"""
        
        actions_taken = []
        
        for action_str in actions_needed:
            # Convert string to enum (with fallback for invalid actions)
            try:
                action = BookingAction(action_str)
            except ValueError:
                actions_taken.append(f"{ActionResult.UNKNOWN_ACTION}: {action_str}")
                continue
            
            if action == BookingAction.CHECK_AVAILABILITY:
                result = self._check_availability(session_state)
                actions_taken.append(result)
                
            elif action == BookingAction.CONFIRM_DATETIME:
                result = self._confirm_datetime(session_state)
                actions_taken.append(result)
                
            elif action == BookingAction.GET_TECHNICIANS:
                result = self._get_technicians(session_state)
                actions_taken.append(result)
                
            elif action == BookingAction.CREATE_BOOKING:
                result = self._create_booking(session_state)
                actions_taken.append(result)
                
            elif action == BookingAction.CALCULATE_COST:
                result = self._calculate_cost(session_state)
                actions_taken.append(result)
                
            elif action == BookingAction.GET_SERVICES:
                result = self._get_services(session_state)
                actions_taken.append(result)
                
            elif action == BookingAction.UPDATE_BOOKING:
                result = self._update_booking(session_state)
                actions_taken.append(result)
                
            elif action == BookingAction.CANCEL_BOOKING:
                result = self._cancel_booking(session_state)
                actions_taken.append(result)
        
        return actions_taken
    
    def _check_availability(self, session_state: Dict) -> str:
        """Check availability for requested service, date, and time"""
        booking_state_dict = session_state["booking_state"]
        booking_state = BookingState.from_dict(booking_state_dict)
        service_name = booking_state.services_requested
        date = booking_state.date_requested
        time = booking_state.time_requested
        
        print(f"🔍 Checking availability for service: {service_name}, date: {date}, time: {time}")
        
        if service_name and date and time:
            # Check if confirmation is pending
            if booking_state.dateTimeConfirmationStatus == ConfirmationStatus.PENDING:
                print(f"⏳ Awaiting date/time confirmation")
                return f"{ActionResult.CHECKED_AVAILABILITY}: Awaiting confirmation"
            
            # Parse natural language date and time to proper formats
            parsed_date = parse_date(date)
            parsed_time = parse_time(time)
            
            if not parsed_date or not parsed_time:
                print(f"❌ Could not parse date '{date}' or time '{time}'")
                return f"{ActionResult.CHECKED_AVAILABILITY}: Invalid date/time format"
            
            print(f"📅 Parsed: {date} → {parsed_date}, {time} → {parsed_time}")
            
            # First get service details
            service = self.api_client.get_service_by_name(service_name)
            if service:
                # Get available technicians for this service
                technicians = self.api_client.get_technicians_for_service(service.get('_id'))
                # Convert to TechnicianInfo objects (simplified for now)
                booking_state.available_technicians = technicians
                
                if technicians:
                    # Check availability for the first available technician
                    first_tech = technicians[0]
                    duration = service.get('duration_minutes', 60)
                    availability = self.api_client.check_technician_availability(
                        first_tech.get('_id'), parsed_date, parsed_time, duration
                    )
                    
                    if availability.get('available'):
                        # Update BookingState with parsed date/time and technician info
                        booking_state.appointmentDate = parsed_date
                        booking_state.startTime = parsed_time
                        booking_state.customerId = None  # Will be set when customer is created
                        
                        # Create ServiceTechnicianPair
                        service_pair = ServiceTechnicianPair(
                            serviceId=service.get('_id'),
                            technicianId=first_tech.get('_id'),
                            duration=duration,
                            price=service.get('price', 0)
                        )
                        booking_state.services = [service_pair]
                        booking_state.totalDuration = duration
                        booking_state.totalPrice = service.get('price', 0)
                        
                        # Update session with modified BookingState
                        session_state["booking_state"] = booking_state.to_dict()
                        
                        print(f"✅ Available with {first_tech.get('firstName')} {first_tech.get('lastName')}")
                        return ActionResult.CHECKED_AVAILABILITY
                    else:
                        print(f"❌ Not available at requested time")
                        return f"{ActionResult.CHECKED_AVAILABILITY}: Not available"
                else:
                    print(f"❌ No technicians found for service")
                    return f"{ActionResult.CHECKED_AVAILABILITY}: No technicians found"
            else:
                print(f"❌ Service '{service_name}' not found")
                return f"{ActionResult.CHECKED_AVAILABILITY}: Service not found"
        else:
            # Missing required information
            missing = []
            if not service_name: missing.append("service")
            if not date: missing.append("date")
            if not time: missing.append("time")
            
            print(f"❌ Missing info: {', '.join(missing)}")
            return f"{ActionResult.CHECKED_AVAILABILITY}: Missing {', '.join(missing)}"
    
    def _confirm_datetime(self, session_state: Dict) -> str:
        """Handle date/time confirmation"""
        pending = session_state.get("pending_confirmation")
        if pending:
            # Update booking state with confirmed date/time
            booking_state_dict = session_state["booking_state"]
            booking_state = BookingState.from_dict(booking_state_dict)
            
            # Mark as confirmed and set parsed date/time
            booking_state.dateTimeConfirmationStatus = ConfirmationStatus.CONFIRMED
            booking_state.appointmentDate = pending["parsed_date"]
            booking_state.startTime = pending["parsed_time"]
            session_state["booking_state"] = booking_state.to_dict()
            
            # Clear pending confirmation
            session_state.pop("pending_confirmation", None)
            
            print(f"✅ Date/time confirmed: {pending['formatted_date']} at {pending['formatted_time']}")
            return "datetime_confirmed"
        else:
            print(f"❌ No pending confirmation found")
            return "no_pending_confirmation"
    
    def _get_technicians(self, session_state: Dict) -> str:
        """Get available technicians for the requested service"""
        booking_state = session_state["booking_state"]
        service_name = booking_state.get("services_requested")
        
        if service_name:
            # First get service by name
            service = self.api_client.get_service_by_name(service_name)
            if service:
                # Then get technicians for that service
                technicians = self.api_client.get_technicians_for_service(service.get('_id'))
                booking_state["available_technicians"] = technicians
                return ActionResult.RETRIEVED_TECHNICIANS
            else:
                return f"{ActionResult.RETRIEVED_TECHNICIANS}: Service not found"
        else:
            # Get all available technicians
            technicians = self.api_client.get_available_technicians()
            booking_state["available_technicians"] = technicians
            return ActionResult.RETRIEVED_TECHNICIANS
    
    def _create_booking(self, session_state: Dict) -> str:
        """Create a new booking"""
        booking_state_dict = session_state["booking_state"]
        booking_state = BookingState.from_dict(booking_state_dict)
        
        if booking_state.is_ready_for_booking():
            # First ensure customer exists
            customer_phone = booking_state.customer_phone
            customer = None
            
            if customer_phone:
                customer = self.api_client.get_customer_by_phone(customer_phone)
            
            if not customer:
                # Create new customer
                name_parts = booking_state.customer_name.split()
                customer_data = {
                    "firstName": name_parts[0] if name_parts else "Customer",
                    "lastName": " ".join(name_parts[1:]) if len(name_parts) > 1 else "Customer",
                    "phone": customer_phone or "",
                    "email": f"{customer_phone}@temp.com" if customer_phone else "temp@temp.com"
                }
                customer = self.api_client.create_customer(customer_data)
            
            if customer:
                # Set customer ID in booking state
                booking_state.customerId = customer.get("_id")
                
                # Create booking using the backend-compatible format
                booking_data = booking_state.to_backend_booking()
                
                print(f"🔄 Creating booking with data: {booking_data}")
                booking = self.api_client.create_booking(booking_data)
                
                if booking:
                    booking_state.status = BookingStatus.CONFIRMED
                    session_state["conversation_complete"] = True
                    session_state["booking_state"] = booking_state.to_dict()
                    return ActionResult.BOOKING_CREATED
                else:
                    return f"{ActionResult.BOOKING_CREATED}: Failed to create"
            else:
                return f"{ActionResult.BOOKING_CREATED}: Customer creation failed"
        else:
            return ActionResult.BOOKING_NOT_READY
    
    def _calculate_cost(self, session_state: Dict) -> str:
        """Calculate cost for requested services"""
        booking_state = session_state["booking_state"]
        service_name = booking_state.get("services_requested")
        
        if service_name:
            service = self.api_client.get_service_by_name(service_name)
            if service:
                booking_state["total_cost"] = service.get("price", 0)
                return ActionResult.COST_CALCULATED
            else:
                return f"{ActionResult.COST_CALCULATED}: Service not found"
        else:
            return f"{ActionResult.COST_CALCULATED}: No service specified"
    
    def _get_services(self, session_state: Dict) -> str:
        """Get all available services"""
        services = self.api_client.get_all_services()
        booking_state = session_state["booking_state"]
        booking_state["available_services"] = services
        return ActionResult.SERVICES_RETRIEVED
    
    def _update_booking(self, session_state: Dict) -> str:
        """Update an existing booking"""
        booking_state = session_state["booking_state"]
        if booking_state.get("booking_status") == BookingStatus.CONFIRMED:
            booking_state["booking_status"] = BookingStatus.CONFIRMED  # Keep confirmed
            return ActionResult.BOOKING_UPDATED
        else:
            return ActionResult.BOOKING_UPDATE_FAILED
    
    def _cancel_booking(self, session_state: Dict) -> str:
        """Cancel an existing booking"""
        booking_state = session_state["booking_state"]
        booking_state["booking_status"] = BookingStatus.CANCELLED
        booking_state["confirmation_id"] = ""
        return ActionResult.BOOKING_CANCELLED
