#!/usr/bin/env python3
"""
Pure LLM Conversational Booking Handler
Handles multi-turn conversations for salon booking without complex state machines
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

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

# In-memory session storage (replace with Redis/database in production)
conversation_sessions: Dict[str, Dict] = {}

class ConversationHandler:
    """Pure LLM-powered conversation handler for salon bookings"""
    
    def __init__(self):
        self.sessions = conversation_sessions
    
    def start_conversation(self, message: str, customer_phone: str = None) -> Dict[str, Any]:
        """Start a new booking conversation"""
        session_id = str(uuid.uuid4())
        
        # Initialize session state
        session_state = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "booking_state": {
                "customer_name": "",
                "customer_phone": customer_phone or "",
                "services_requested": [],
                "date_requested": "",
                "time_requested": "",
                "technician_preference": "",
                "confirmed_services": [],
                "total_cost": 0.0,
                "booking_status": BookingStatus.PENDING
            },
            "conversation_complete": False
        }
        
        # Process the initial message
        response = self._process_message(session_state, message)
        
        # Store session
        self.sessions[session_id] = session_state
        
        return response
    
    def continue_conversation(self, session_id: str, message: str) -> Dict[str, Any]:
        """Continue an existing conversation"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session_state = self.sessions[session_id]
        
        # Process the message
        response = self._process_message(session_state, message)
        
        # Update session
        self.sessions[session_id] = session_state
        
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
            Return your response in this JSON format:
            {{
                "response": "Your natural response to the customer",
                "booking_state_updates": {{
                    "customer_name": "extracted name or current value",
                    "customer_phone": "extracted phone or current value",
                    "services_requested": ["list of services mentioned"],
                    "date_requested": "extracted date or current value",
                    "time_requested": "extracted time or current value",
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
            self._update_booking_state(session_state, response_data.get("booking_state_updates", {}))
            
            # Execute any needed actions
            actions_taken = self._execute_actions(session_state, response_data.get("actions_neededs", []))
            
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
        
        return f"""
        You are an expert salon booking assistant for Hana Salon. You handle booking conversations naturally and intelligently.
        
        AVAILABLE SERVICES:
        - Gel Manicure: $35, 45 minutes
        - Acrylic Full Set: $55, 90 minutes  
        - Luxury Spa Pedicure: $65, 90 minutes
        - Complex Nail Art: $75, 120 minutes
        - Dip Powder Service: $45, 60 minutes
        - Basic Manicure: $25, 30 minutes
        
        AVAILABLE TECHNICIANS:
        - Maria Rodriguez (Expert): Specializes in nail art and complex designs
        - Lauren Chen (Expert): Spa treatments and luxury services specialist
        - Emma Wilson (Senior): All-around technician, great with gel and acrylics
        - Sofia Martinez (Master): Premium nail art and special occasion specialist
        - Isabella Torres (Senior): Manicures and pedicures specialist
        
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
        - Ask for one piece of missing information at a time
        - Offer specific alternatives when there are conflicts
        - Confirm all details before finalizing booking
        - Handle date/time parsing intelligently (e.g., "tomorrow", "next Friday")
        - Remember context from previous messages
        - If customer changes their mind, adapt gracefully
        
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
        
        booking_state = session_state["booking_state"]
        
        for key, value in updates.items():
            if value and value != booking_state.get(key, ""):
                booking_state[key] = value
    
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
                # Simulate availability check
                actions_taken.append(ActionResult.CHECKED_AVAILABILITY)
                
            elif action == BookingAction.GET_TECHNICIANS:
                # Simulate technician lookup
                actions_taken.append(ActionResult.RETRIEVED_TECHNICIANS)
                
            elif action == BookingAction.CREATE_BOOKING:
                # Simulate booking creation
                booking_state = session_state["booking_state"]
                if self._is_booking_ready(booking_state):
                    booking_state["booking_status"] = BookingStatus.CONFIRMED
                    booking_state["confirmation_id"] = f"SPA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    session_state["conversation_complete"] = True
                    actions_taken.append(ActionResult.BOOKING_CREATED)
                else:
                    actions_taken.append(ActionResult.BOOKING_NOT_READY)
                    
            elif action == BookingAction.CALCULATE_COST:
                # Simulate cost calculation
                actions_taken.append(ActionResult.COST_CALCULATED)
                
            elif action == BookingAction.GET_SERVICES:
                # Simulate service lookup
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
    
    def _is_booking_ready(self, booking_state: Dict) -> bool:
        """Check if booking has all required information"""
        
        required_fields = [
            "customer_name",
            "services_requested", 
            "date_requested",
            "time_requested"
        ]
        
        for field in required_fields:
            if not booking_state.get(field):
                return False
        
        return len(booking_state.get("services_requested", [])) > 0
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        return self.sessions.get(session_id)
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

# Global conversation handler instance
conversation_handler = ConversationHandler()
