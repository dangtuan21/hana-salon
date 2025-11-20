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
from services.booking_manager import BookingManager


class ActionExecutor:
    """Executes booking actions identified by the LLM"""
    
    def __init__(self, api_client: BackendAPIClient):
        self.api_client = api_client
        self.booking_manager = BookingManager()
    
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
        """Check availability for all services in the booking"""
        booking_state_dict = session_state["booking_state"]
        booking_state = BookingState.from_dict(booking_state_dict)
        date = booking_state.date_requested
        time = booking_state.time_requested
        
        print(f"🔍 Checking availability for {len(booking_state.services)} service(s), date: {date}, time: {time}")
        
        # Check if we have required information
        if not booking_state.services:
            print(f"❌ No services in booking state")
            return f"{ActionResult.CHECKED_AVAILABILITY}: No services found"
            
        if not date or not time:
            missing = []
            if not date: missing.append("date")
            if not time: missing.append("time")
            print(f"❌ Missing info: {', '.join(missing)}")
            return f"{ActionResult.CHECKED_AVAILABILITY}: Missing {', '.join(missing)}"
        
        # Only proceed if date/time is confirmed
        if booking_state.dateTimeConfirmationStatus != ConfirmationStatus.CONFIRMED:
            print(f"⏳ Date/time not confirmed yet (status: {booking_state.dateTimeConfirmationStatus})")
            return f"{ActionResult.CHECKED_AVAILABILITY}: Date/time not confirmed"
        
        # Parse natural language date and time to proper formats
        parsed_date = parse_date(date)
        parsed_time = parse_time(time)
        
        if not parsed_date or not parsed_time:
            print(f"❌ Could not parse date '{date}' or time '{time}'")
            return f"{ActionResult.CHECKED_AVAILABILITY}: Invalid date/time format"
        
        print(f"📅 Parsed: {date} → {parsed_date}, {time} → {parsed_time}")
        
        # Check availability for each service
        current_start_time = parsed_time
        all_available = True
        unavailable_services = []
        
        for i, service_pair in enumerate(booking_state.services):
            print(f"🔍 Checking service {i+1}/{len(booking_state.services)}: {service_pair.serviceId}")
            
            # Get specialized technicians for this service
            technicians = self.api_client.get_technicians_for_service(service_pair.serviceId)
            
            if not technicians:
                print(f"❌ No technicians found for service {service_pair.serviceId}")
                unavailable_services.append(f"Service {i+1}: No technicians")
                all_available = False
                continue
            
            # Find best available technician
            best_technician = self._find_best_technician(technicians, service_pair.serviceId, parsed_date, current_start_time, service_pair.duration)
            
            if best_technician:
                # Update service pair with technician assignment
                service_pair.technicianId = best_technician['_id']
                print(f"✅ Service {i+1} available with {best_technician.get('firstName')} {best_technician.get('lastName')}")
                
                # Calculate next start time for sequential services
                from datetime import datetime, timedelta
                current_time = datetime.strptime(current_start_time, "%H:%M")
                next_time = current_time + timedelta(minutes=service_pair.duration)
                current_start_time = next_time.strftime("%H:%M")
            else:
                print(f"❌ Service {i+1} not available at requested time")
                unavailable_services.append(f"Service {i+1}: No availability")
                all_available = False
        
        if all_available:
            # Update booking state with confirmed availability
            booking_state.appointmentDate = parsed_date
            booking_state.startTime = parsed_time
            
            # Calculate end time based on total duration
            from datetime import datetime, timedelta
            start_time_obj = datetime.strptime(parsed_time, "%H:%M")
            end_time_obj = start_time_obj + timedelta(minutes=booking_state.totalDuration)
            booking_state.endTime = end_time_obj.strftime("%H:%M")
            
            # Update session with modified BookingState
            session_state["booking_state"] = booking_state.to_dict()
            
            print(f"🎉 All services available! Appointment: {parsed_date} {parsed_time}-{booking_state.endTime}")
            return ActionResult.CHECKED_AVAILABILITY
        else:
            print(f"❌ Some services unavailable: {', '.join(unavailable_services)}")
            
            # Find alternative time slots on the same day
            alternative_times = self._find_alternative_times(booking_state, parsed_date)
            
            if alternative_times:
                alternatives_text = ", ".join([f"{time['time']} ({time['technician']})" for time in alternative_times[:3]])
                print(f"💡 Found alternative times: {alternatives_text}")
                
                # Store alternatives in booking state for LLM to use
                booking_state.alternative_times = alternative_times[:3]  # Top 3 alternatives
                session_state["booking_state"] = booking_state.to_dict()
                
                return f"{ActionResult.CHECKED_AVAILABILITY}: Conflict detected. Available alternatives on {parsed_date}: {alternatives_text}"
            else:
                return f"{ActionResult.CHECKED_AVAILABILITY}: No availability on {parsed_date}. Please try a different date."
    
    def _find_best_technician(self, technicians: List[Dict], service_id: str, date: str, start_time: str, duration: int) -> Dict:
        """Find the best available technician using batch availability check"""
        
        # Sort technicians by preference: Senior > Junior, higher rating first
        sorted_technicians = sorted(technicians, key=lambda t: (
            t.get('skillLevel') == 'Senior',  # Senior technicians first
            t.get('rating', 0)  # Higher rating first
        ), reverse=True)
        
        # Extract technician IDs in preference order
        technician_ids = [t.get('_id') for t in sorted_technicians]
        
        print(f"🔍 Batch checking {len(technician_ids)} technicians for availability")
        
        # Single batch API call for all technicians
        batch_result = self.api_client.batch_check_technician_availability(
            technician_ids, date, start_time, duration
        )
        
        if batch_result and batch_result.get('results'):
            # Find first available technician in preference order
            for technician in sorted_technicians:
                tech_id = technician.get('_id')
                
                # Check if this technician is available in batch results
                for result in batch_result['results']:
                    if result['technicianId'] == tech_id and result['available']:
                        print(f"✅ {technician.get('firstName')} {technician.get('lastName')} is available")
                        return technician
                
                print(f"❌ {technician.get('firstName')} {technician.get('lastName')} is not available")
        else:
            print("❌ Batch availability check failed")
        
        # No technician available
        return None
    
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
        """Create a new booking with enhanced multi-service support"""
        booking_state_dict = session_state["booking_state"]
        booking_state = BookingState.from_dict(booking_state_dict)
        
        print(f"🔄 Creating booking for {len(booking_state.services)} service(s)")
        
        # Validate booking readiness
        if not self._is_booking_ready_for_creation(booking_state):
            missing_items = self._get_missing_booking_items(booking_state)
            print(f"❌ Booking not ready: Missing {', '.join(missing_items)}")
            return f"{ActionResult.BOOKING_NOT_READY}: Missing {', '.join(missing_items)}"
        
        try:
            # Step 1: Ensure customer exists or create new one
            customer = self._ensure_customer_exists(booking_state)
            if not customer:
                print(f"❌ Failed to create/find customer")
                return f"{ActionResult.BOOKING_CREATED}: Customer creation failed"
            
            # Step 2: Set customer ID in booking state
            booking_state.customerId = customer.get("_id")
            print(f"✅ Customer ready: {customer.get('firstName')} {customer.get('lastName')} (ID: {customer.get('_id')})")
            
            # Step 3: Validate all services have technicians assigned
            unassigned_services = [i+1 for i, service in enumerate(booking_state.services) if not service.technicianId]
            if unassigned_services:
                print(f"❌ Services without technicians: {unassigned_services}")
                return f"{ActionResult.BOOKING_CREATED}: Services {unassigned_services} need technician assignment"
            
            # Step 4: Create booking using backend-compatible format
            booking_data = booking_state.to_backend_booking()
            print(f"🔄 Creating booking with data: {booking_data}")
            
            booking = self.api_client.create_booking(booking_data)
            
            if booking:
                # Step 5: Update booking state with success
                booking_state.status = BookingStatus.CONFIRMED  # Use proper enum
                booking_state.customerId = customer.get("_id")
                session_state["conversation_complete"] = True
                session_state["booking_state"] = booking_state.to_dict()
                
                print(f"🎉 Booking created successfully! ID: {booking.get('_id', 'Unknown')}")
                print(f"📅 Appointment: {booking_state.appointmentDate} {booking_state.startTime}-{booking_state.endTime}")
                print(f"💰 Total: ${booking_state.totalPrice} for {booking_state.totalDuration} minutes")
                
                return ActionResult.BOOKING_CREATED
            else:
                print(f"❌ Backend booking creation failed")
                return f"{ActionResult.BOOKING_CREATED}: Backend creation failed"
                
        except Exception as e:
            print(f"💥 Error creating booking: {e}")
            return f"{ActionResult.BOOKING_CREATED}: Error - {str(e)}"
    
    def _is_booking_ready_for_creation(self, booking_state: BookingState) -> bool:
        """Check if booking has all required information for creation"""
        required_fields = [
            booking_state.customer_name,
            booking_state.customer_phone,
            booking_state.appointmentDate,
            booking_state.startTime,
            booking_state.services
        ]
        
        # Check basic required fields
        if not all(required_fields):
            return False
        
        # Check that all services have technicians assigned
        for service in booking_state.services:
            if not service.technicianId:
                return False
        
        # Check confirmation status
        if booking_state.dateTimeConfirmationStatus != ConfirmationStatus.CONFIRMED:
            return False
            
        return True
    
    def _get_missing_booking_items(self, booking_state: BookingState) -> List[str]:
        """Get list of missing items preventing booking creation"""
        missing = []
        
        if not booking_state.customer_name:
            missing.append("customer name")
        if not booking_state.customer_phone:
            missing.append("customer phone")
        if not booking_state.appointmentDate:
            missing.append("appointment date")
        if not booking_state.startTime:
            missing.append("start time")
        if not booking_state.services:
            missing.append("services")
        if booking_state.dateTimeConfirmationStatus != ConfirmationStatus.CONFIRMED:
            missing.append("date/time confirmation")
            
        # Check for unassigned technicians
        unassigned_count = sum(1 for service in booking_state.services if not service.technicianId)
        if unassigned_count > 0:
            missing.append(f"technician assignment for {unassigned_count} service(s)")
            
        return missing
    
    def _ensure_customer_exists(self, booking_state: BookingState) -> Dict:
        """Ensure customer exists in backend, create if necessary"""
        customer_phone = booking_state.customer_phone
        customer = None
        
        # Try to find existing customer by phone
        if customer_phone:
            try:
                customer = self.api_client.get_customer_by_phone(customer_phone)
                if customer:
                    print(f"✅ Found existing customer: {customer.get('firstName')} {customer.get('lastName')}")
                    return customer
            except Exception as e:
                print(f"⚠️ Error finding customer: {e}")
        
        # Create new customer if not found
        try:
            name_parts = booking_state.customer_name.split() if booking_state.customer_name else ["Customer"]
            
            # Format phone number properly (ensure it's in a valid format)
            formatted_phone = self._format_phone_number(customer_phone) if customer_phone else ""
            
            customer_data = {
                "firstName": name_parts[0],
                "lastName": " ".join(name_parts[1:]) if len(name_parts) > 1 else "",
                "phone": formatted_phone,
                "email": ""  # Allow empty email
            }
            
            print(f"🔄 Creating new customer: {customer_data}")
            customer = self.api_client.create_customer(customer_data)
            
            if customer:
                print(f"✅ Created new customer: {customer.get('firstName')} {customer.get('lastName')}")
            
            return customer
            
        except Exception as e:
            print(f"💥 Error creating customer: {e}")
            return None
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number - preserve original format"""
        if not phone:
            return ""
        
        # Keep the original phone number as entered by the user
        # Only clean up obvious formatting issues but preserve the core number
        cleaned = phone.strip()
        
        # If it's all digits and 10 digits long, format nicely
        if cleaned.isdigit() and len(cleaned) == 10:
            return f"{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"
        else:
            # Keep original format for all other cases
            return cleaned
    
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
        booking_state_dict = session_state["booking_state"]
        booking_state_dict["available_services"] = services
        
        # Convert to BookingState object and populate services if ready
        booking_state = BookingState.from_dict(booking_state_dict)
        self.booking_manager.populate_services_if_ready(booking_state, session_state)
        
        # Update session with populated services
        session_state["booking_state"] = booking_state.to_dict()
        print(f"📋 Services populated: {len(booking_state.services)} service(s) in booking state")
        
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
    
    def _find_alternative_times(self, booking_state: BookingState, date: str) -> List[Dict]:
        """Find alternative available time slots on the same day"""
        alternatives = []
        
        # Define business hours (9 AM to 6 PM)
        business_start = 9  # 9:00 AM
        business_end = 18   # 6:00 PM
        slot_duration = 30  # 30-minute slots
        
        print(f"🔍 Searching for alternatives on {date}...")
        
        try:
            # Get all technicians for the first service (assuming all services need similar technicians)
            first_service = booking_state.services[0] if booking_state.services else None
            if not first_service:
                return alternatives
                
            service_id = first_service.serviceId
            technicians = self.api_client.get_technicians_for_service(service_id)
            
            if not technicians:
                return alternatives
            total_duration = booking_state.totalDuration
            
            # Check each 30-minute slot during business hours
            for hour in range(business_start, business_end):
                for minute in [0, 30]:  # Check :00 and :30
                    if hour == business_end - 1 and minute == 30:
                        continue  # Don't start appointments too close to closing
                        
                    slot_time = f"{hour:02d}:{minute:02d}"
                    
                    # Check if this slot can accommodate the total appointment duration
                    slot_hour = hour
                    slot_minute = minute
                    end_minute = slot_minute + total_duration
                    end_hour = slot_hour + (end_minute // 60)
                    end_minute = end_minute % 60
                    
                    # Skip if appointment would go past business hours
                    if end_hour > business_end or (end_hour == business_end and end_minute > 0):
                        continue
                    
                    # Batch check all technicians for this time slot
                    technician_ids = [t.get('_id') for t in technicians]
                    batch_result = self.api_client.batch_check_technician_availability(
                        technician_ids, date, slot_time, total_duration
                    )
                    
                    # Find first available technician for this slot
                    if batch_result and batch_result.get('results'):
                        for technician in technicians:
                            tech_id = technician.get('_id')
                            tech_name = f"{technician.get('firstName')} {technician.get('lastName')}"
                            
                            # Check if this technician is available in batch results
                            for result in batch_result['results']:
                                if result['technicianId'] == tech_id and result['available']:
                                    alternatives.append({
                                        'time': slot_time,
                                        'technician': tech_name,
                                        'technician_id': tech_id,
                                        'end_time': f"{end_hour:02d}:{end_minute:02d}"
                                    })
                                    break  # Found one technician for this slot, move to next slot
                            else:
                                continue  # Continue to next technician
                            break  # Break out of technician loop if we found one
                    
                    # Limit to reasonable number of alternatives
                    if len(alternatives) >= 5:
                        break
                        
                if len(alternatives) >= 5:
                    break
                    
        except Exception as e:
            print(f"⚠️ Error finding alternatives: {e}")
            
        print(f"💡 Found {len(alternatives)} alternative time slots")
        return alternatives
