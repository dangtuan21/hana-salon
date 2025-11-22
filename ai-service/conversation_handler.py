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
from services.booking_manager import BookingManager
from services.action_executor import ActionExecutor
from database import SessionManager, BookingState, BookingStatus, ServiceTechnicianPair
from database.enums import ActionResult, BookingAction

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)


# Backend API client and session manager are now imported from organized modules

class ConversationHandler:
    """Pure LLM-powered conversation handler for salon bookings"""
    
    def __init__(self, backend_url: str = "http://localhost:3060"):
        self.session_manager = SessionManager(backend_url)
        self.api_client = BackendAPIClient(backend_url)
        self.booking_manager = BookingManager()
        self.action_executor = ActionExecutor(self.api_client)
        
        # Register session start event handler
        self.session_manager.set_on_session_start_callback(self._on_session_start)
    
    def _on_session_start(self, session_id: str, session_state: Dict):
        """Handle session start event - preload resources"""
        print("🔄 Preloading services and technicians for new session...")
        preload_actions = self.action_executor.execute_actions(session_state, [BookingAction.GET_SERVICES, BookingAction.GET_TECHNICIANS])
        print(f"✅ Preloaded: {len(preload_actions)} actions completed")
        
        # Update session with preloaded data
        self.session_manager.update_session(session_id, session_state)
    
    def start_conversation(self, message: str, customer_phone: str = None) -> Dict[str, Any]:
        """Start a new booking conversation"""
        # Create new session using SessionManager (triggers session start event)
        session_id = self.session_manager.create_session(customer_phone)
        session_state = self.session_manager.get_session(session_id)
        
        # Process the initial message (resources already preloaded by session start event)
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
        print(f"DEBUG: Processing message: {user_message}")
        
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
                    "date_requested": "EXTRACT EXACTLY as mentioned: Monday, Tuesday, tomorrow, next Friday, Dec 15, etc. DO NOT convert relative dates to absolute dates. If no date mentioned OR if customer is confirming existing pending confirmation, use empty string",
                    "time_requested": "EXTRACT any time mentioned: 2pm, 10:30am, 3 PM, etc. SMART ALTERNATIVE MATCHING: If booking_state contains alternative_times and user mentions a number/time that matches an alternative (e.g., '10' matches '10:00' alternative), extract the full matched time. If no time mentioned OR if customer is confirming existing pending confirmation, use empty string",
                    "technician_preference": "extracted preference or current value"
                }},
                "actions_neededs": ["check_availability", "get_technicians", "create_booking"],
                "conversation_complete": false,
                "next_suggestions": ["What the customer might say next"]
            }}
            """)
        ]
        
        try:
            # First pass: Get LLM extraction only to update booking state
            llm_response = llm.invoke(messages)
            original_response_data = json.loads(llm_response.content)
            
            # Update booking state with extracted data
            booking_state = BookingState.from_dict(session_state["booking_state"])

            updates = original_response_data.get("booking_state_updates", {})
            
            # Check if user selected an alternative time
            selected_alternative = None
            if updates.get("time_requested") and booking_state.alternative_times:
                selected_time = updates["time_requested"]
                for alt in booking_state.alternative_times:
                    if alt["time"] == selected_time:
                        selected_alternative = alt
                        print(f" Matched alternative selection: {selected_time} with {alt['technician']}")
                        break
            
            booking_state_dict = session_state["booking_state"]
            for key, value in updates.items():
                if value and value.strip():  # Only update if value is not empty
                    booking_state_dict[key] = value
                    print(f" Updated {key}: {value}")
                    if key == "services_requested" and len(booking_state_dict.get("services", [])) == 0:
                        # Create updated BookingState with new services_requested
                        updated_booking_state = BookingState.from_dict(booking_state_dict)
                        print(f"ttt Calling populate_services_if_ready with services_requested: {value}")
                        self.booking_manager.populate_services_if_ready(updated_booking_state)
                        # Update the session with populated services
                        session_state["booking_state"] = updated_booking_state.to_dict()


            booking_state = BookingState.from_dict(session_state["booking_state"])
            print(f"ttt Final booking_state: {booking_state}")
                            
            # If alternative was selected, update technician and clear alternatives
            if selected_alternative:
                # Update technician assignment for the service
                if booking_state.services and len(booking_state.services) > 0:
                    booking_state.services[0]["technicianId"] = selected_alternative["technician_id"]
                    print(f" Assigned technician: {selected_alternative['technician']} ({selected_alternative['technician_id']})")
                
                # Clear alternatives since one was selected
                booking_state.alternative_times
                print(" Cleared alternative times after selection")
            
            session_state["booking_state"] = booking_state.to_dict()
            
            print(f"📋 Current booking state: {session_state['booking_state']}")
                        
            # Check data collection status
            name_collected = bool(booking_state.customer_name)
            phone_collected = bool(booking_state.customer_phone)
            service_collected = bool(booking_state.services_requested)
            date_collected = bool(booking_state.date_requested)
            time_collected = bool(booking_state.time_requested)
            
            # Debug: Track data collection and services array state
            print(f"🔍 DEBUG: Data collection status - name:{name_collected}, phone:{phone_collected}, service:{service_collected}, date:{date_collected}, time:{time_collected}")
            print(f"🔍 DEBUG: services_requested: '{booking_state.services_requested}'")
            print(f"🔍 DEBUG: services : {booking_state.services}")
            
            all_data_collected = (name_collected and phone_collected and 
                                service_collected and date_collected and time_collected)
            
            print(f"📊 Data Status: name={name_collected}, phone={phone_collected}, service={service_collected}, date={date_collected}, time={time_collected}")
            
            # Check if user is confirming appointment details
            is_confirmation_response = self._is_confirmation_response(user_message, session_state)
            is_appointment_confirmation = self._is_appointment_confirmation(user_message, session_state)
            
            # Check if user is confirming a ready-to-book appointment
            is_ready_to_book = (all_data_collected and 
                               user_message.lower().strip() in ['ok', 'okay', 'yes', 'confirm', 'correct'])
            
            if (is_confirmation_response or is_appointment_confirmation or is_ready_to_book) and all_data_collected:
                print(f" Detected confirmation response: '{user_message}' - Processing booking")
                
                # User confirmed - proceed with booking actions
                print("✅ User confirmed - proceeding with booking")
                
                # Ensure services are populated before checking availability
                actions_taken = self.action_executor.execute_actions(session_state, [BookingAction.GET_SERVICES, BookingAction.CHECK_AVAILABILITY])
                
                # Generate response based on availability check results
                availability_result = None
                for action in actions_taken:
                    if "availability_checked" in str(action) or "CHECKED_AVAILABILITY" in str(action):
                        availability_result = action
                        break
                
                print(f"🔍 DEBUG: availability_result = {availability_result}")
                print(f"🔍 DEBUG: str(availability_result) = {str(availability_result)}")
                print(f"🔍 DEBUG: type(availability_result) = {type(availability_result)}")
                
                if availability_result and "CHECKED_AVAILABILITY" in str(availability_result):
                    # Check if there was a conflict or if booking is available
                    if "Conflict detected" in str(availability_result):
                        # Extract alternative times from the result
                        alternatives_text = str(availability_result).split("Available alternatives on")[1] if "Available alternatives on" in str(availability_result) else "some alternative times"
                        response_text = f"I found a scheduling conflict with your requested time. However, I have some great alternatives available{alternatives_text}. Which time would work better for you?"
                    elif (availability_result == ActionResult.CHECKED_AVAILABILITY or 
                          str(availability_result) == "ActionResult.CHECKED_AVAILABILITY" or
                          str(availability_result) == "availability_checked"):
                        # No conflict, booking is available - proceed with booking creation
                        booking_actions = self.action_executor.execute_actions(session_state, ["create_booking"])
                        actions_taken.extend(booking_actions)
                        # Don't use hardcoded response - let the completion message generation handle this
                        # The action_executor sets conversation_complete = True, which will trigger our LLM completion message
                        response_text = "Perfect! Your booking has been confirmed."
                    else:
                        response_text = "Let me check the availability details and get back to you."
                else:
                    response_text = "I'm checking availability for your appointment. Please wait a moment..."
                
                # If conversation is complete after booking creation, generate personalized completion message
                if session_state.get("conversation_complete", False):
                    print("🎉 Booking complete - generating personalized completion message")
                    completion_response = self._generate_completion_message(session_state, response_text)
                    response_text = completion_response
                
                session_state["messages"].append({
                    "role": "assistant", 
                    "content": response_text,
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "session_id": session_state["session_id"],
                    "response": response_text,
                    "booking_state": session_state["booking_state"],
                    "conversation_complete": session_state["conversation_complete"],
                    "actions_taken": actions_taken,
                    "next_suggestions": []
                }
            
            # Use LLM response instead of hardcoded templates
            if not name_collected or not phone_collected:
                print("🔄 STEP 1: Missing customer info - using LLM response")
                response_data = {
                    "response": original_response_data.get("response", "Hi! Could I get your name and phone number?"),
                    "actions_neededs": original_response_data.get("actions_neededs", [])
                }
            if not service_collected:
                print("🔄 STEP 2: Missing service - using LLM response")
                response_data = {
                    "response": original_response_data.get("response", "What service would you like to book today?"),
                    "actions_neededs": original_response_data.get("actions_neededs", [])
                }
            if not date_collected or not time_collected:
                print("🔄 STEP 3: Missing date/time - using LLM response")
                response_data = {
                    "response": original_response_data.get("response", "When would you like your appointment?"),
                    "actions_neededs": original_response_data.get("actions_neededs", [])
                }
            if all_data_collected:
                # Check if appointment data is ready for booking
                is_ready_for_booking = (booking_state.appointmentDate is not None and
                                      booking_state.startTime is not None)
                
                if is_ready_for_booking:
                    print("🔄 STEP 5: Appointment already confirmed - using LLM response")
                    response_data = {
                        "response": original_response_data.get("response", "Perfect! Let me finalize your appointment details."),
                        "actions_neededs": original_response_data.get("actions_neededs", ["create_booking"])
                    }
                else:
                    print("🔄 STEP 4: All data collected - using LLM response for confirmation")
                    response_data = {
                        "response": original_response_data.get("response", "Let me confirm your appointment details."),
                        "actions_neededs": original_response_data.get("actions_neededs", [])
                    }
            else:
                # Fallback - let LLM handle
                print("🔄 Fallback: Letting LLM handle the conversation")
                response_data = None
            
            # If we didn't override response_data, use the original LLM response
            if response_data is None:
                response_data = original_response_data
            
            # Check if we created a pending confirmation that needs LLM attention
            if session_state.get("datetime_parsing") and not hasattr(self, '_confirmation_handled'):
                print(f"🔄 Pending confirmation detected, regenerating LLM response...")
                
                # Second pass: Regenerate LLM response with pending confirmation visible
                updated_messages = [
                    SystemMessage(content=self._create_system_prompt(session_state)),
                    HumanMessage(content=f"""
                    {self._build_conversation_context(session_state)}
                    
                    Current message: {user_message}
                    
                    CRITICAL: There is a PENDING CONFIRMATION that needs customer confirmation.
                    
                    If customer message is confirmation (yes, correct, that's right, etc.):
                    - Use "confirm_datetime" action
                    - DO NOT extract any booking_state_updates
                    - Proceed with availability check
                    
                    If customer message is NOT confirmation:
                    - Use the exact "formatted_date" and "formatted_time" from PENDING CONFIRMATION
                    - Ask customer to confirm BOTH service and date/time: "Please confirm your [service] appointment on [formatted_date] at [formatted_time]"
                    
                    Return your response in this JSON format:
                    {{
                        "response": "Your natural response",
                        "booking_state_updates": {{}},
                        "actions_neededs": ["confirm_datetime" if confirming, otherwise []],
                        "conversation_complete": false,
                        "next_suggestions": ["What the customer might say next"]
                    }}
                    """)
                ]
                
                # Mark that we're handling confirmation to avoid infinite loop
                self._confirmation_handled = True
                llm_response = llm.invoke(updated_messages)
                response_data = json.loads(llm_response.content)
                delattr(self, '_confirmation_handled')
            
            # Execute any needed actions
            requested_actions = response_data.get("actions_neededs", [])
            print(f"🎯 LLM requested actions: {requested_actions}")
            
            
            # Special handling for create_booking - ensure all prerequisites are met
            if "create_booking" in requested_actions:
                booking_state = session_state["booking_state"]
                if booking_state.appointmentDate is None:
                    # Need to parse date/time first
                    print("🔄 Booking requested but date/time not parsed, triggering availability check")
                    requested_actions = ["check_availability", "create_booking"]
            
            actions_taken = self.action_executor.execute_actions(session_state, requested_actions)
            
            # Add assistant message to history
            session_state["messages"].append({
                "role": "assistant", 
                "content": response_data["response"],
                "timestamp": datetime.now().isoformat()
            })
            
            # Update conversation completion status
            session_state["conversation_complete"] = response_data.get("conversation_complete", False)
            
            # If conversation is complete, generate personalized completion message
            if session_state["conversation_complete"]:
                completion_response = self._generate_completion_message(session_state, response_data["response"])
                response_data["response"] = completion_response
            
            # Session is automatically persisted by SessionManager
            # No need for separate conversation storage - it's handled by database-backed sessions
            
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
        
        # Use preloaded data from booking state (loaded at session start)
        booking_state = BookingState.from_dict(session_state["booking_state"])
        
        # Get preloaded services and technicians
        services = booking_state.available_services or []
        technicians = booking_state.available_technicians or []
        
        # Format services
        services_text = ""
        for service in services:
            # Handle both dict and ServiceInfo object formats
            if hasattr(service, 'name'):
                # ServiceInfo object
                services_text += f"- {service.name}: ${service.price}, {service.duration_minutes} minutes\n"
            else:
                # Dict format (fallback)
                services_text += f"- {service.get('name')}: ${service.get('price')}, {service.get('duration_minutes')} minutes\n"
        
        # Format technicians
        technicians_text = ""
        for tech in technicians:
            # Handle both dict and TechnicianInfo object formats
            if hasattr(tech, 'firstName'):
                # TechnicianInfo object
                name = f"{tech.firstName} {tech.lastName}"
                level = tech.skillLevel or 'Technician'
                specialties = ", ".join(tech.specialties or [])
            else:
                # Dict format (fallback)
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
        
        PENDING CONFIRMATION:
        {json.dumps(session_state.get("datetime_parsing", {}), indent=2) if session_state.get("datetime_parsing") else "None"}
        
        CONFIRMATION INSTRUCTIONS:
        - If PENDING CONFIRMATION exists, use the exact "formatted_date" and "formatted_time" in your response
        - ALWAYS include BOTH service and date/time in confirmation: "Please confirm [service] on [formatted_date] at [formatted_time]"
        - Example: "Please confirm your Gel Manicure appointment on Wednesday, November 19 at 3pm"
        - DO NOT create your own date format - use the provided formatted_date
        - If customer says "yes", "correct", "that's right" when PENDING CONFIRMATION exists, use "confirm_datetime" action
        - DO NOT extract new date/time when customer is confirming existing pending confirmation
        
        CONVERSATION HISTORY:
        {len(session_state["messages"])} previous messages
        
        YOUR TASKS (IN PRIORITY ORDER):
        1. Extract booking information naturally from conversation
        2. FIRST PRIORITY: Ask for missing CUSTOMER INFO (name and phone) before anything else
        3. SECOND PRIORITY: Ask for SERVICE SELECTION before date/time - "What service would you like to book today?"
        4. THIRD PRIORITY: Ask for date/time information ONLY after service is selected
        5. FOURTH PRIORITY: For relative dates/times, ask for confirmation before checking availability
        5. If PENDING CONFIRMATION exists, ask customer to confirm the parsed date/time
        6. Handle conflicts by offering alternatives
        7. Confirm bookings when all details are ready
        8. Be friendly, professional, and helpful
        
        IMPORTANT GUIDELINES:
        - Always be natural, warm, and conversational - like a friendly salon receptionist
        - NEVER use robotic or template language - be genuine and human-like
        - Respond naturally to what the customer actually said, don't ignore their greeting or tone
        - IMMEDIATELY capture customer name and phone when mentioned (even in greetings!)
        - Ask for missing information in a friendly, conversational way
        - NEVER proceed with date/time confirmation if customer name, phone, or service is missing
        - If missing customer info, ask naturally: "I'd love to help you book an appointment! What's your name?" or "Could I get your name and phone number so I can set this up for you?"
        - If customer info is complete but service is missing, ask warmly: "What service are you interested in today?" or "What can we do for you today?"
        - If customer info and service are complete but date/time is missing, ask conversationally: "When would work best for you?" or "What day and time would you prefer?"
        - NEVER create pending confirmations without service selection
        - NEVER use placeholder text like "[insert formatted_date]" - always use real data or ask for missing info
        - Only proceed with service/date/time confirmation AFTER customer info is collected
        - Offer specific alternatives when there are conflicts
        - Confirm all details before finalizing booking
        - Handle date/time parsing intelligently (e.g., "tomorrow", "next Friday")
        - Remember context from previous messages
        - If customer changes their mind, adapt gracefully
        - Pay special attention to introductions: "Hi, I'm...", "This is...", "My name is..."
        - Extract phone numbers from any format: (555) 123-4567, 555-123-4567, 5551234567
        - ALWAYS confirm relative dates/times: "Thursday" → "Please confirm your [service] appointment on Thursday, November 20 at 3pm"
        - Wait for customer confirmation before checking availability for relative dates
        - If PENDING CONFIRMATION exists, ask customer "Please confirm your [service] appointment on [formatted_date] at [formatted_time]" but DO NOT use "confirm_datetime" action yet
        - Only use "confirm_datetime" action when customer says "yes", "correct", "that's right", etc.
        - Only use "check_availability" AFTER date/time is confirmed
        
        AVAILABLE ACTIONS:
        When you need to perform actions, use these exact action names:
        - "check_availability" - Check if requested time slots are available
        - "confirm_datetime" - Confirm the parsed date/time with customer
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
    
    def _is_confirmation_response(self, user_message: str, session_state: Dict) -> bool:
        """Check if user message is confirming a pending confirmation"""
        # Only check if there's a pending confirmation
        if not session_state.get("datetime_parsing"):
            return False
        
        # Common confirmation phrases
        confirmation_phrases = [
            'yes', 'yeah', 'yep', 'correct', 'right', 'that\'s right', 'that\'s correct',
            'confirm', 'confirmed', 'ok', 'okay', 'sure', 'absolutely', 'exactly',
            'perfect', 'good', 'sounds good', 'looks good', 'that works'
        ]
        
        user_lower = user_message.lower().strip()
        
        # Check for exact matches or phrases that start with confirmation words
        for phrase in confirmation_phrases:
            if user_lower == phrase or user_lower.startswith(phrase + ' '):
                return True
        
        # Check for "yes" variations with punctuation
        if user_lower in ['yes.', 'yes!', 'yes,', 'yeah.', 'yeah!', 'yep.', 'yep!']:
            return True
            
        return False
    
    def _is_appointment_confirmation(self, user_message: str, session_state: Dict) -> bool:
        """Check if user message is confirming appointment details even without pending confirmation"""
        booking_state = BookingState.from_dict(session_state["booking_state"])
        
        # Only check if we have all the basic info but no confirmed appointment
        has_customer_info = booking_state.customer_name and booking_state.customer_phone
        has_service = booking_state.services_requested
        has_datetime = booking_state.date_requested and booking_state.time_requested
        no_appointment_date = not booking_state.appointmentDate
        
        if not (has_customer_info and has_service and has_datetime and no_appointment_date):
            return False
        
        # Common confirmation phrases
        confirmation_phrases = [
            'yes', 'yeah', 'yep', 'correct', 'right', 'that\'s right', 'that\'s correct',
            'confirm', 'confirmed', 'ok', 'okay', 'sure', 'absolutely', 'exactly',
            'perfect', 'good', 'sounds good', 'looks good', 'that works'
        ]
        
        user_lower = user_message.lower().strip()
        
        # Check for exact matches or phrases that start with confirmation words
        for phrase in confirmation_phrases:
            if user_lower == phrase or user_lower.startswith(phrase + ' '):
                return True
        
        return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        return self.session_manager.get_session(session_id)
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session and store conversation history"""
        # Get session data before deleting
        session_data = self.session_manager.get_session(session_id)
        
        # Session is automatically persisted in database by SessionManager
        # No need to store separately - just delete from cache
        return self.session_manager.delete_session(session_id)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return self.session_manager.get_session_stats()
    
    def _generate_completion_message(self, session_state: Dict, original_response: str) -> str:
        """Generate personalized completion message with LLM"""
        try:
            booking_state = session_state.get("booking_state", {})
            customer_name = booking_state.get("customer_name", "")
            service = booking_state.get("services_requested", "service")
            appointment_date = booking_state.get("appointmentDate", "")
            appointment_time = booking_state.get("startTime", "")
            booking_id = booking_state.get("booking_id", "")
            
            # Create personalized completion prompt
            completion_prompt = f"""
            Generate a warm, conversational chat message to confirm a salon booking.
            
            BOOKING DETAILS:
            - Customer: {customer_name}
            - Service: {service}
            - Date: {appointment_date}
            - Time: {appointment_time}
            - Booking ID: {booking_id}
            
            REQUIREMENTS:
            - Write as a CHAT MESSAGE, not an email
            - Be warm, friendly, and conversational
            - Confirm the booking details naturally in 2-3 sentences
            - Thank the customer by name
            - Ask if they need any additional help
            - Keep it concise and chat-like
            - Use 1-2 emojis maximum
            - NO email format, NO subject lines, NO formal signatures
            
            Example format: "Perfect, [Name]! Your [service] is confirmed for [date] at [time]. Is there anything else I can help you with today?"
            
            Generate a natural chat completion message:
            """
            
            messages = [
                SystemMessage(content="You are a friendly salon receptionist confirming a booking."),
                HumanMessage(content=completion_prompt)
            ]
            
            # Generate completion message with LLM
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))
            completion_response = llm.invoke(messages)
            
            return completion_response.content
            
        except Exception as e:
            print(f"❌ Error generating completion message: {e}")
            # Fallback to a simple personalized message
            customer_name = session_state.get("booking_state", {}).get("customer_name", "")
            service = session_state.get("booking_state", {}).get("services_requested", "appointment")
            return f"Perfect, {customer_name}! Your {service} is all confirmed. Is there anything else I can help you with today?"

# Global conversation handler instance
conversation_handler = ConversationHandler()
