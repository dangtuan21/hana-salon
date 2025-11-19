#!/usr/bin/env python3
"""
Pure LLM Conversational Booking Handler
Handles multi-turn conversations for salon booking without complex state machines
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

# Import organized services and database classes
from services import BackendAPIClient, parse_date, parse_time
from database import SessionManager, BookingState, BookingStatus, ServiceTechnicianPair

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)

class BookingAction(str, Enum):
    """Enum for booking actions that can be executed"""
    CHECK_AVAILABILITY = "check_availability"
    GET_TECHNICIANS = "get_technicians"
    CREATE_BOOKING = "create_booking"
    CALCULATE_COST = "calculate_cost"
    GET_SERVICES = "get_services"
    UPDATE_BOOKING = "update_booking"
    CANCEL_BOOKING = "cancel_booking"

class BookingStatus(str, Enum):
    """Enum for booking confirmation status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class ActionResult(str, Enum):
    """Enum for action execution results"""
    CHECKED_AVAILABILITY = "checked_availability"
    RETRIEVED_TECHNICIANS = "retrieved_technicians"
    BOOKING_CREATED = "booking_created"
    BOOKING_NOT_READY = "booking_not_ready"
    COST_CALCULATED = "cost_calculated"
    SERVICES_RETRIEVED = "services_retrieved"
    BOOKING_UPDATED = "booking_updated"
    BOOKING_UPDATE_FAILED = "booking_update_failed"
    BOOKING_CANCELLED = "booking_cancelled"
    UNKNOWN_ACTION = "unknown_action"

# Backend API client and session manager are now imported from organized modules

class ConversationHandler:
    """Pure LLM-powered conversation handler for salon bookings"""
    
    def __init__(self, backend_url: str = "http://localhost:3060"):
        self.session_manager = SessionManager()
        self.api_client = BackendAPIClient(backend_url)
    
    def start_conversation(self, message: str, customer_phone: str = None) -> Dict[str, Any]:
        """Start a new booking conversation"""
        # Create new session using SessionManager
        session_id = self.session_manager.create_session(customer_phone)
        session_state = self.session_manager.get_session(session_id)
        
        # Process the initial message
        response = self._process_message(session_state, message)
        
        # Update session
        self.session_manager.update_session(session_id, session_state)
        
        return response
    
    def continue_conversation(self, session_id: str, message: str) -> Dict[str, Any]:
        """Continue an existing conversation"""
        session_state = self.session_manager.get_session(session_id)
        if not session_state:
            raise ValueError(f"Session {session_id} not found")
        
        # Process the message
        response = self._process_message(session_state, message)
        
        # Update session
        self.session_manager.update_session(session_id, session_state)
        
        return response
    
    def _process_message(self, session_state: Dict, user_message: str) -> Dict[str, Any]:
        """Process a single message using pure LLM intelligence"""
        
        # Add user message to history
        session_state["messages"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create context-aware system prompt
        system_prompt = self._create_system_prompt(session_state)
        
        # Create conversation context
        conversation_context = self._build_conversation_context(session_state)
        
        # Get LLM response
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
            Current conversation context:
            {conversation_context}
            
            Latest user message: {user_message}
            
            Please respond naturally and update the booking state as needed.
            
            CRITICAL: Always extract customer name and phone number when mentioned!
            - Look for names in greetings: "Hi, I'm Sarah", "This is John", "My name is..."
            - Look for phone numbers in any format: "555-1234", "(555) 123-4567", "my number is 5551234567"
            - If customer provides contact info, ALWAYS capture it even if they're just introducing themselves
            
            Return your response in this JSON format:
            {{
                "response": "Your natural response to the customer",
                "booking_state_updates": {{
                    "customer_name": "ALWAYS extract full name if mentioned, even in greetings",
                    "customer_phone": "ALWAYS extract phone if mentioned in any format",
                    "services_requested": "single service name or empty string",
                    "date_requested": "EXTRACT any date mentioned: Monday, Tuesday, tomorrow, next Friday, Dec 15, etc. If no date mentioned, use empty string",
                    "time_requested": "EXTRACT any time mentioned: 2pm, 10:30am, 3 PM, etc. If no time mentioned, use empty string",
                    "technician_preference": "extracted preference or current value"
                }},
                "actions_neededs": ["check_availability", "get_technicians", "create_booking"],
                "conversation_complete": false,
                "next_suggestions": ["What the customer might say next"]
            }}
            """)
        ]
        
        try:
            llm_response = llm.invoke(messages)
            response_data = json.loads(llm_response.content)
            
            # Update booking state with LLM extracted information
            booking_updates = response_data.get("booking_state_updates", {})
            print(f"📋 LLM extracted updates: {booking_updates}")
            self._update_booking_state(session_state, booking_updates)
            print(f"🗂️ Current booking state: {session_state['booking_state']}")
            
            # Execute any needed actions
            requested_actions = response_data.get("actions_neededs", [])
            print(f"🎯 LLM requested actions: {requested_actions}")
            actions_taken = self._execute_actions(session_state, requested_actions)
            
            # Add assistant message to history
            session_state["messages"].append({
                "role": "assistant", 
                "content": response_data["response"],
                "timestamp": datetime.now().isoformat()
            })
            
            # Update conversation completion status
            session_state["conversation_complete"] = response_data.get("conversation_complete", False)
            
            return {
                "session_id": session_state["session_id"],
                "response": response_data["response"],
                "booking_state": session_state["booking_state"],
                "conversation_complete": session_state["conversation_complete"],
                "actions_taken": actions_taken,
                "next_suggestions": response_data.get("next_suggestions", [])
            }
            
        except Exception as e:
            # Enhanced error logging
            print(f"💥 ERROR in _process_message: {str(e)}")
            print(f"💥 Error type: {type(e).__name__}")
            import traceback
            print(f"💥 Traceback: {traceback.format_exc()}")
            
            # Fallback response if LLM fails
            fallback_response = "I apologize, but I'm having trouble processing your request right now. Could you please repeat that?"
            
            session_state["messages"].append({
                "role": "assistant",
                "content": fallback_response,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "session_id": session_state["session_id"],
                "response": fallback_response,
                "booking_state": session_state["booking_state"],
                "conversation_complete": False,
                "actions_taken": [f"error_handled: {str(e)}"],
                "next_suggestions": ["Please try rephrasing your request"]
            }
    
    def _create_system_prompt(self, session_state: Dict) -> str:
        """Create a comprehensive system prompt for the LLM"""
        
        # Get real data from API
        services = self.api_client.get_all_services()
        technicians = self.api_client.get_available_technicians()
        
        # Format services
        services_text = ""
        for service in services:
            services_text += f"- {service.get('name')}: ${service.get('price')}, {service.get('duration_minutes')} minutes\n"
        
        # Format technicians
        technicians_text = ""
        for tech in technicians:
            name = f"{tech.get('firstName')} {tech.get('lastName')}"
            level = tech.get('skillLevel', 'Technician')
            specialties = ", ".join(tech.get('specialties', []))
            technicians_text += f"- {name} ({level}): {specialties}\n"
        
        return f"""
        You are an expert salon booking assistant for Hana Salon. You handle booking conversations naturally and intelligently.
        
        AVAILABLE SERVICES:
        {services_text}
        
        AVAILABLE TECHNICIANS:
        {technicians_text}
        
        CURRENT BOOKING STATE:
        {json.dumps(session_state["booking_state"], indent=2)}
        
        CONVERSATION HISTORY:
        {len(session_state["messages"])} previous messages
        
        YOUR TASKS:
        1. Extract booking information naturally from conversation
        2. Ask for missing information when needed
        3. Check availability when you have enough details
        4. Handle conflicts by offering alternatives
        5. Confirm bookings when all details are ready
        6. Be friendly, professional, and helpful
        
        IMPORTANT GUIDELINES:
        - Always be natural and conversational
        - IMMEDIATELY capture customer name and phone when mentioned (even in greetings!)
        - Ask for one piece of missing information at a time
        - Offer specific alternatives when there are conflicts
        - Confirm all details before finalizing booking
        - Handle date/time parsing intelligently (e.g., "tomorrow", "next Friday")
        - Remember context from previous messages
        - If customer changes their mind, adapt gracefully
        - Pay special attention to introductions: "Hi, I'm...", "This is...", "My name is..."
        - Extract phone numbers from any format: (555) 123-4567, 555-123-4567, 5551234567
        
        AVAILABLE ACTIONS:
        When you need to perform actions, use these exact action names:
        - "check_availability" - Check if requested time slots are available
        - "get_technicians" - Find technicians for requested services
        - "create_booking" - Create the final booking
        - "calculate_cost" - Calculate total cost for services
        - "get_services" - Look up service details
        - "update_booking" - Modify existing booking
        - "cancel_booking" - Cancel a booking
        
        RESPONSE FORMAT:
        Always respond with valid JSON containing your natural response and any booking state updates.
        """
    
    def _build_conversation_context(self, session_state: Dict) -> str:
        """Build conversation context for the LLM"""
        
        messages = session_state["messages"]
        if not messages:
            return "This is the start of a new booking conversation."
        
        # Get last few messages for context
        recent_messages = messages[-6:]  # Last 3 exchanges
        
        context = "Recent conversation:\n"
        for msg in recent_messages:
            role = "Customer" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
        
        return context
    
    def _update_booking_state(self, session_state: Dict, updates: Dict) -> None:
        """Update booking state with LLM extracted information"""
        
        # Get BookingState object from session
        booking_state_dict = session_state["booking_state"]
        booking_state = BookingState.from_dict(booking_state_dict)
        
        for key, value in updates.items():
            if value and str(value).strip():  # Update if value is not empty
                # Special handling for customer info - always update if provided
                if key in ["customer_name", "customer_phone"] and value:
                    old_value = getattr(booking_state, key, "")
                    new_value = str(value).strip()
                    setattr(booking_state, key, new_value)
                    print(f"🔍 Updated {key}: '{old_value}' -> '{new_value}'")
                # For other fields, only update if different
                elif hasattr(booking_state, key):
                    old_value = getattr(booking_state, key, "")
                    if value != old_value:
                        setattr(booking_state, key, value)
                        print(f"📝 Updated {key}: {value}")
        
        # Update session with modified BookingState
        session_state["booking_state"] = booking_state.to_dict()
    
    def _execute_actions(self, session_state: Dict, actions_neededs: List[str]) -> List[str]:
        """Execute actions identified by the LLM"""
        
        actions_taken = []
        
        for action_str in actions_neededs:
            # Convert string to enum (with fallback for invalid actions)
            try:
                action = BookingAction(action_str)
            except ValueError:
                actions_taken.append(f"{ActionResult.UNKNOWN_ACTION}: {action_str}")
                continue
            
            if action == BookingAction.CHECK_AVAILABILITY:
                # Real availability check
                booking_state_dict = session_state["booking_state"]
                booking_state = BookingState.from_dict(booking_state_dict)
                service_name = booking_state.services_requested
                date = booking_state.date_requested
                time = booking_state.time_requested
                
                print(f"🔍 Checking availability for service: {service_name}, date: {date}, time: {time}")
                
                if service_name and date and time:
                    # Parse natural language date and time to proper formats
                    parsed_date = parse_date(date)
                    parsed_time = parse_time(time)
                    
                    if not parsed_date or not parsed_time:
                        actions_taken.append(f"{ActionResult.CHECKED_AVAILABILITY}: Invalid date/time format")
                        print(f"❌ Could not parse date '{date}' or time '{time}'")
                    else:
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
                                    
                                    actions_taken.append(ActionResult.CHECKED_AVAILABILITY)
                                    print(f"✅ Available with {first_tech.get('firstName')} {first_tech.get('lastName')}")
                                else:
                                    actions_taken.append(f"{ActionResult.CHECKED_AVAILABILITY}: Not available")
                                    print(f"❌ Not available at requested time")
                            else:
                                actions_taken.append(f"{ActionResult.CHECKED_AVAILABILITY}: No technicians found")
                                print(f"❌ No technicians found for service")
                        else:
                            actions_taken.append(f"{ActionResult.CHECKED_AVAILABILITY}: Service not found")
                            print(f"❌ Service '{service_name}' not found")
                else:
                    missing = []
                    if not service_name: missing.append("service")
                    if not date: missing.append("date") 
                    if not time: missing.append("time")
                    actions_taken.append(f"{ActionResult.CHECKED_AVAILABILITY}: Missing {', '.join(missing)}")
                    print(f"❌ Missing info: {', '.join(missing)}")
                
            elif action == BookingAction.GET_TECHNICIANS:
                # Real technician lookup
                booking_state = session_state["booking_state"]
                service_name = booking_state.get("services_requested")
                
                if service_name:
                    # First get service by name
                    service = self.api_client.get_service_by_name(service_name)
                    if service:
                        # Then get technicians for that service
                        technicians = self.api_client.get_technicians_for_service(service.get('_id'))
                        booking_state["available_technicians"] = technicians
                        actions_taken.append(ActionResult.RETRIEVED_TECHNICIANS)
                    else:
                        actions_taken.append(f"{ActionResult.RETRIEVED_TECHNICIANS}: Service not found")
                else:
                    # Get all available technicians
                    technicians = self.api_client.get_available_technicians()
                    booking_state["available_technicians"] = technicians
                    actions_taken.append(ActionResult.RETRIEVED_TECHNICIANS)
                
            elif action == BookingAction.CREATE_BOOKING:
                # Real booking creation
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
                            actions_taken.append(ActionResult.BOOKING_CREATED)
                        else:
                            actions_taken.append(f"{ActionResult.BOOKING_CREATED}: Failed to create")
                    else:
                        actions_taken.append(f"{ActionResult.BOOKING_CREATED}: Customer creation failed")
                else:
                    actions_taken.append(ActionResult.BOOKING_NOT_READY)
                    
            elif action == BookingAction.CALCULATE_COST:
                # Real cost calculation
                booking_state = session_state["booking_state"]
                service_name = booking_state.get("services_requested")
                
                if service_name:
                    service = self.api_client.get_service_by_name(service_name)
                    if service:
                        booking_state["total_cost"] = service.get("price", 0)
                        actions_taken.append(ActionResult.COST_CALCULATED)
                    else:
                        actions_taken.append(f"{ActionResult.COST_CALCULATED}: Service not found")
                else:
                    actions_taken.append(f"{ActionResult.COST_CALCULATED}: No service specified")
                
            elif action == BookingAction.GET_SERVICES:
                # Real service lookup
                services = self.api_client.get_all_services()
                booking_state = session_state["booking_state"]
                booking_state["available_services"] = services
                actions_taken.append(ActionResult.SERVICES_RETRIEVED)
                
            elif action == BookingAction.UPDATE_BOOKING:
                # Simulate booking update
                booking_state = session_state["booking_state"]
                if booking_state.get("booking_status") == BookingStatus.CONFIRMED:
                    booking_state["booking_status"] = BookingStatus.CONFIRMED  # Keep confirmed
                    actions_taken.append(ActionResult.BOOKING_UPDATED)
                else:
                    actions_taken.append(ActionResult.BOOKING_UPDATE_FAILED)
                
            elif action == BookingAction.CANCEL_BOOKING:
                # Simulate booking cancellation
                booking_state = session_state["booking_state"]
                booking_state["booking_status"] = BookingStatus.CANCELLED
                booking_state["confirmation_id"] = ""
                actions_taken.append(ActionResult.BOOKING_CANCELLED)
        
        return actions_taken
    
    def _is_booking_ready(self, booking_state_dict: Dict) -> bool:
        """Check if booking has all required information"""
        booking_state = BookingState.from_dict(booking_state_dict)
        return booking_state.is_ready_for_booking()
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        return self.session_manager.get_session(session_id)
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session"""
        return self.session_manager.delete_session(session_id)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return self.session_manager.get_session_stats()

# Global conversation handler instance
conversation_handler = ConversationHandler()
