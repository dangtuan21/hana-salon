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
from database import SessionManager, BookingState, BookingStatus, ServiceTechnicianPair, ConfirmationStatus
from database.enums import BookingAction, ActionResult

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
        self.session_manager = SessionManager()
        self.api_client = BackendAPIClient(backend_url)
        self.booking_manager = BookingManager()
        self.action_executor = ActionExecutor(self.api_client)
    
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
                    "date_requested": "EXTRACT EXACTLY as mentioned: Monday, Tuesday, tomorrow, next Friday, Dec 15, etc. DO NOT convert relative dates to absolute dates. If no date mentioned OR if customer is confirming existing pending confirmation, use empty string",
                    "time_requested": "EXTRACT any time mentioned: 2pm, 10:30am, 3 PM, etc. If no time mentioned OR if customer is confirming existing pending confirmation, use empty string",
                    "technician_preference": "extracted preference or current value"
                }},
                "actions_neededs": ["check_availability", "get_technicians", "create_booking"],
                "conversation_complete": false,
                "next_suggestions": ["What the customer might say next"]
            }}
            """)
        ]
        
        try:
            # First pass: Get LLM extraction only
            llm_response = llm.invoke(messages)
            response_data = json.loads(llm_response.content)
            
            # Check if user is confirming a pending confirmation BEFORE updating booking state
            is_confirmation_response = self._is_confirmation_response(user_message, session_state)
            if is_confirmation_response:
                print(f"✅ Detected confirmation response: '{user_message}'")
                # Automatically trigger confirm_datetime and check_availability actions
                actions_taken = self.action_executor.execute_actions(session_state, ["confirm_datetime", "check_availability"])
                
                # Generate response based on availability check results
                availability_result = None
                for action in actions_taken:
                    if "availability_checked" in str(action) or "CHECKED_AVAILABILITY" in str(action):
                        availability_result = action
                        break
                
                if availability_result and "CHECKED_AVAILABILITY" in str(availability_result):
                    # Check if there was a conflict or if booking is available
                    if "Conflict detected" in str(availability_result):
                        # Extract alternative times from the result
                        alternatives_text = str(availability_result).split("Available alternatives on")[1] if "Available alternatives on" in str(availability_result) else "some alternative times"
                        response_text = f"I found a scheduling conflict with your requested time. However, I have some great alternatives available{alternatives_text}. Which time would work better for you?"
                    elif "No availability" in str(availability_result):
                        response_text = "I'm sorry, but there's no availability on your requested date. Could you try a different date?"
                    elif str(availability_result) == "ActionResult.CHECKED_AVAILABILITY":
                        # No conflict, booking is available
                        response_text = "Perfect! Your appointment is available and confirmed. Let me create your booking."
                        # Trigger booking creation
                        booking_actions = self.action_executor.execute_actions(session_state, ["create_booking"])
                        actions_taken.extend(booking_actions)
                    else:
                        response_text = "Let me check the availability details and get back to you."
                else:
                    response_text = "I'm checking availability for your appointment. Please wait a moment..."
                
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
            
            # Update booking state with LLM extracted information
            booking_updates = response_data.get("booking_state_updates", {})
            print(f"📋 LLM extracted updates: {booking_updates}")
            self.booking_manager.update_booking_state(session_state, booking_updates)
            print(f"🗂️ Current booking state: {session_state['booking_state']}")
            
            # Check if we created a pending confirmation that needs LLM attention
            if session_state.get("pending_confirmation") and not hasattr(self, '_confirmation_handled'):
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
            actions_taken = self.action_executor.execute_actions(session_state, requested_actions)
            
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
        
        # Update BookingState with available services and technicians
        booking_state_dict = session_state["booking_state"]
        booking_state = BookingState.from_dict(booking_state_dict)
        booking_state.available_services = services
        booking_state.available_technicians = technicians
        session_state["booking_state"] = booking_state.to_dict()
        
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
        
        PENDING CONFIRMATION:
        {json.dumps(session_state.get("pending_confirmation", {}), indent=2) if session_state.get("pending_confirmation") else "None"}
        
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
        3. SECOND PRIORITY: Ask for missing service/date/time information
        4. THIRD PRIORITY: For relative dates/times, ask for confirmation before checking availability
        5. If PENDING CONFIRMATION exists, ask customer to confirm the parsed date/time
        6. Handle conflicts by offering alternatives
        7. Confirm bookings when all details are ready
        8. Be friendly, professional, and helpful
        
        IMPORTANT GUIDELINES:
        - Always be natural and conversational
        - IMMEDIATELY capture customer name and phone when mentioned (even in greetings!)
        - Ask for one piece of missing information at a time
        - NEVER proceed with date/time confirmation if customer name or phone is missing
        - Ask "Could I get your name and phone number?" if either is missing
        - If customer info is complete but date/time is missing, ask "When would you like your appointment?"
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
        if not session_state.get("pending_confirmation"):
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
