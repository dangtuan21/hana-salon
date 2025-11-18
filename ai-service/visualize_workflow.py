#!/usr/bin/env python3
"""
Visualize the Langraph workflow structure
"""

def print_workflow_diagram():
    """
    Print ASCII diagram of the booking workflow
    """
    diagram = """
🏨 HANA AI BOOKING WORKFLOW
═══════════════════════════════════════════════════════════════

    ┌─────────────────┐
    │      START      │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │   NODE 1:       │
    │ BOOKING         │
    │ VALIDATION      │
    │                 │
    │ • Extract info  │
    │ • Validate data │
    │ • Check format  │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │   NODE 2:       │
    │ BOOKING         │
    │ CONFIRMATION    │
    │                 │
    │ • Generate ID   │
    │ • Create msg    │
    │ • Finalize      │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │       END       │
    └─────────────────┘

═══════════════════════════════════════════════════════════════

📋 WORKFLOW DETAILS:

1️⃣  BOOKING VALIDATION NODE:
    • Input: Raw booking request text
    • Process: Extract customer name, service type, date, time
    • Validate: Check if all required information is present
    • Output: Structured booking data + validation status

2️⃣  BOOKING CONFIRMATION NODE:
    • Input: Validated booking data
    • Process: Generate confirmation ID and professional message
    • Handle: Invalid bookings with appropriate error messages
    • Output: Final confirmation response

🔄 STATE MANAGEMENT:
    • BookingState tracks all information between nodes
    • Messages are accumulated for conversation history
    • Each node updates specific state fields

🎯 USE CASES:
    ✅ Restaurant reservations
    ✅ Medical appointments  
    ✅ Hotel bookings
    ✅ Service appointments
    ✅ Event bookings

═══════════════════════════════════════════════════════════════
"""
    print(diagram)

def print_state_structure():
    """
    Print the state structure used in the workflow
    """
    state_info = """
📊 BOOKING STATE STRUCTURE:
═══════════════════════════════════════════════════════════════

class BookingState(TypedDict):
    messages: list              # Conversation history
    booking_request: str        # Original user request
    customer_name: str          # Extracted customer name
    service_type: str           # Type of service/booking
    date: str                   # Booking date (YYYY-MM-DD)
    time: str                   # Booking time (HH:MM)
    validation_status: str      # VALID/INVALID + reason
    confirmation_id: str        # Generated booking ID
    final_response: str         # Final confirmation message

═══════════════════════════════════════════════════════════════

🔄 STATE FLOW:

START → booking_request (user input)
  ↓
NODE 1 → Extract: customer_name, service_type, date, time
       → Set: validation_status
  ↓
NODE 2 → Generate: confirmation_id
       → Create: final_response
  ↓
END → Complete booking process

═══════════════════════════════════════════════════════════════
"""
    print(state_info)

if __name__ == "__main__":
    print_workflow_diagram()
    print_state_structure()
