import os
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

# Load environment variables
load_dotenv()

# State definition for the enhanced booking workflow
class BookingState(TypedDict):
    messages: Annotated[list, add_messages]
    booking_request: str
    customer_name: str
    customer_phone: str
    service_id: str
    service_name: str
    technician_id: str
    technician_name: str
    date: str
    time: str
    duration_minutes: int
    total_cost: float
    validation_status: str
    confirmation_id: str
    final_response: str
    available_technicians: list
    service_details: dict

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY")
)

def booking_validation_node(state: BookingState) -> BookingState:
    """
    Node 1: Enhanced validation with service matching and technician availability
    """
    print("💅 Processing enhanced nail booking validation...")
    
    # Import database manager
    from database import get_db_manager, Customer
    
    booking_request = state["booking_request"]
    db = get_db_manager()
    
    # Create service catalog for AI reference
    services = db.get_all_services()
    service_catalog = "\n".join([
        f"- {service.name}: {service.description} (${service.price}, {service.duration_minutes} min)"
        for service in services
    ])
    
    # Get available technicians
    technicians = db.get_available_technicians()
    technician_list = "\n".join([
        f"- {tech.name} ({tech.skill_level}): {tech.bio[:100]}..."
        for tech in technicians
    ])
    
    validation_prompt = f"""
    You are an expert nail salon booking assistant. Analyze this booking request and extract information.
    
    Booking Request: {booking_request}
    
    Available Services:
    {service_catalog}
    
    Available Technicians:
    {technician_list}
    
    Extract and validate:
    1. Customer name
    2. Customer phone (if mentioned)
    3. Specific service name (match to our catalog)
    4. Preferred technician name (if mentioned)
    5. Date (format: YYYY-MM-DD, if relative like "tomorrow" convert to actual date)
    6. Time (format: HH:MM, use 24-hour format)
    
    Respond in this exact format:
    CUSTOMER_NAME: [name or "Not specified"]
    CUSTOMER_PHONE: [phone or "Not specified"]
    SERVICE_NAME: [exact service name from catalog or closest match]
    TECHNICIAN_NAME: [technician name or "No preference"]
    DATE: [YYYY-MM-DD or "Not specified"]
    TIME: [HH:MM or "Not specified"]
    VALIDATION_STATUS: [VALID/INVALID - detailed reason]
    """
    
    messages = [
        SystemMessage(content="You are a helpful booking validation assistant."),
        HumanMessage(content=validation_prompt)
    ]
    
    response = llm.invoke(messages)
    validation_result = response.content
    
    # Parse the validation result
    lines = validation_result.strip().split('\n')
    parsed_data = {}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            parsed_data[key.strip()] = value.strip()
    
    # Extract basic information
    state["customer_name"] = parsed_data.get("CUSTOMER_NAME", "Unknown")
    state["customer_phone"] = parsed_data.get("CUSTOMER_PHONE", "Not specified")
    state["date"] = parsed_data.get("DATE", "Unknown")
    state["time"] = parsed_data.get("TIME", "Unknown")
    state["validation_status"] = parsed_data.get("VALIDATION_STATUS", "INVALID - Unable to parse")
    
    # Match service to catalog using database
    service_name = parsed_data.get("SERVICE_NAME", "Unknown")
    matched_service = db.get_service_by_name(service_name)
    
    if matched_service:
        state["service_id"] = matched_service._id
        state["service_name"] = matched_service.name
        state["duration_minutes"] = matched_service.duration_minutes
        state["service_details"] = {
            "name": matched_service.name,
            "description": matched_service.description,
            "price": matched_service.price,
            "duration": matched_service.duration_minutes,
            "category": matched_service.category
        }
        
        # Find available technicians for this service
        available_techs = db.get_technicians_for_service(matched_service._id)
        state["available_technicians"] = [
            {
                "id": tech._id,
                "name": tech.name,
                "skill_level": tech.skill_level,
                "rating": tech.rating,
                "bio": tech.bio
            } for tech in available_techs
        ]
        
        # Handle technician preference
        preferred_tech_name = parsed_data.get("TECHNICIAN_NAME", "No preference")
        if preferred_tech_name != "No preference":
            preferred_tech = db.get_technician_by_name(preferred_tech_name)
            if preferred_tech and preferred_tech in available_techs:
                state["technician_id"] = preferred_tech._id
                state["technician_name"] = preferred_tech.name
                state["total_cost"] = db.calculate_total_cost(matched_service._id, preferred_tech._id)
            else:
                # Technician not available, suggest alternatives
                state["technician_id"] = ""
                state["technician_name"] = "Will suggest alternatives"
                state["total_cost"] = matched_service.price
        else:
            # No preference, will assign best available
            if available_techs:
                best_tech = available_techs[0]  # Highest rated specialist
                state["technician_id"] = best_tech._id
                state["technician_name"] = best_tech.name
                state["total_cost"] = db.calculate_total_cost(matched_service._id, best_tech._id)
            else:
                state["technician_id"] = ""
                state["technician_name"] = "No technicians available"
                state["total_cost"] = matched_service.price
    else:
        state["service_id"] = ""
        state["service_name"] = service_name
        state["duration_minutes"] = 0
        state["total_cost"] = 0.0
        state["service_details"] = {}
        state["available_technicians"] = []
        state["technician_id"] = ""
        state["technician_name"] = ""
        state["validation_status"] = "INVALID - Service not found in our catalog"
    
    state["messages"].append(HumanMessage(content=f"Validation completed: {state['validation_status']}"))
    
    print(f"✅ Enhanced validation completed for {state['customer_name']} - Service: {state['service_name']}")
    return state

def booking_confirmation_node(state: BookingState) -> BookingState:
    """
    Node 2: Processes and confirms the nail booking with database storage
    """
    print("💅 Processing nail booking confirmation...")
    
    from database import get_db_manager, Customer, Booking
    
    if "VALID" not in state["validation_status"]:
        # Handle invalid booking
        state["final_response"] = f"❌ Booking could not be processed: {state['validation_status']}"
        state["confirmation_id"] = "N/A"
        print("❌ Booking rejected due to validation failure")
        return state
    
    db = get_db_manager()
    
    # Handle customer creation/retrieval
    customer = None
    if state["customer_phone"] != "Not specified":
        customer = db.get_customer_by_phone(state["customer_phone"])
        
    if not customer and state["customer_name"] != "Unknown":
        # Create new customer
        customer = Customer(
            name=state["customer_name"],
            phone=state["customer_phone"] if state["customer_phone"] != "Not specified" else "",
            preferences={"preferred_technician": state["technician_name"] if state["technician_name"] else None}
        )
        customer_id = db.create_customer(customer)
        customer._id = customer_id
        print(f"📝 Created new customer: {customer.name}")
    
    # Generate confirmation ID
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    state["confirmation_id"] = f"NAIL-{timestamp}"
    
    # Save booking to database
    if customer and state["service_id"] and state["technician_id"]:
        booking = Booking(
            customer_id=customer._id,
            service_id=state["service_id"],
            technician_id=state["technician_id"],
            date=state["date"],
            time=state["time"],
            duration_minutes=state["duration_minutes"],
            total_cost=state["total_cost"],
            status="confirmed",
            confirmation_id=state["confirmation_id"],
            notes=f"Booked via AI assistant for {state['service_name']}"
        )
        
        booking_id = db.create_booking(booking)
        print(f"💾 Saved booking to database: {booking_id}")
        
        # Update customer booking history
        if customer.booking_history is None:
            customer.booking_history = []
        customer.booking_history.append(booking_id)
        db.update_customer(customer._id, {"booking_history": customer.booking_history})
    
    confirmation_prompt = f"""
    Create a professional nail salon booking confirmation message for:
    
    Customer: {state['customer_name']}
    Phone: {state['customer_phone']}
    Service: {state['service_name']} 
    Description: {state['service_details'].get('description', 'Professional nail service')}
    Technician: {state['technician_name']}
    Date: {state['date']}
    Time: {state['time']}
    Duration: {state['duration_minutes']} minutes
    Total Cost: ${state['total_cost']:.2f}
    Confirmation ID: {state['confirmation_id']}
    
    Make it professional and welcoming. Include:
    - All appointment details
    - Technician information and expertise
    - Service preparation tips
    - Cancellation policy (24-hour notice required)
    - Contact information for changes
    
    Format it as a complete booking confirmation that a real nail salon would send.
    """
    
    messages = [
        SystemMessage(content="You are a friendly booking confirmation assistant."),
        HumanMessage(content=confirmation_prompt)
    ]
    
    response = llm.invoke(messages)
    state["final_response"] = response.content
    
    state["messages"].append(HumanMessage(content=f"Nail booking confirmed with ID: {state['confirmation_id']}"))
    
    print(f"✅ Nail booking confirmed with ID: {state['confirmation_id']}")
    return state

def create_booking_workflow():
    """
    Creates the Langraph workflow with 2 nodes
    """
    # Create the state graph
    workflow = StateGraph(BookingState)
    
    # Add the two nodes
    workflow.add_node("booking_validation", booking_validation_node)
    workflow.add_node("booking_confirmation", booking_confirmation_node)
    
    # Define the workflow edges
    workflow.set_entry_point("booking_validation")
    workflow.add_edge("booking_validation", "booking_confirmation")
    workflow.add_edge("booking_confirmation", END)
    
    # Compile the workflow
    app = workflow.compile()
    return app

def process_booking(booking_request: str):
    """
    Process a nail booking request through the Langraph workflow
    """
    print("� Starting nail booking process...")
    print(f"📝 Request: {booking_request}")
    print("-" * 50)
    
    # Create the workflow
    app = create_booking_workflow()
    
    # Enhanced initial state
    initial_state = {
        "messages": [],
        "booking_request": booking_request,
        "customer_name": "",
        "customer_phone": "",
        "service_id": "",
        "service_name": "",
        "technician_id": "",
        "technician_name": "",
        "date": "",
        "time": "",
        "duration_minutes": 0,
        "total_cost": 0.0,
        "validation_status": "",
        "confirmation_id": "",
        "final_response": "",
        "available_technicians": [],
        "service_details": {}
    }
    
    # Run the workflow
    final_state = app.invoke(initial_state)
    
    print("-" * 50)
    print("💅 ENHANCED NAIL BOOKING SUMMARY:")
    print(f"Customer: {final_state['customer_name']}")
    print(f"Phone: {final_state['customer_phone']}")
    print(f"Service: {final_state['service_name']} ({final_state['service_id']})")
    print(f"Technician: {final_state['technician_name']} ({final_state['technician_id']})")
    print(f"Date: {final_state['date']}")
    print(f"Time: {final_state['time']}")
    print(f"Duration: {final_state['duration_minutes']} minutes")
    print(f"Total Cost: ${final_state['total_cost']:.2f}")
    print(f"Status: {final_state['validation_status']}")
    print(f"Confirmation ID: {final_state['confirmation_id']}")
    print("-" * 50)
    print("💬 FINAL RESPONSE:")
    print(final_state['final_response'])
    print("=" * 50)
    
    return final_state

if __name__ == "__main__":
    # Realistic nail salon booking requests
    sample_requests = [
        "Hi, I'm Emma Watson (555-0123) and I'd like to book a gel manicure with Isabella for December 15th, 2024 at 2:30 PM",
        "Hello, my name is Sarah Johnson. I need to schedule an acrylic full set for next Friday at 11 AM. Do you have any expert level technicians available?",
        "Hi, this is Lisa Chen. I want to book a luxury spa pedicure this Saturday. My phone is 555-0456",
        "I'm Maria Rodriguez (555-0789) and I want complex nail art for my wedding on December 25th at 10:00 AM. I'd prefer your best artist please!",
        "Book a basic manicure for tomorrow at 3 PM. Name is Jennifer Smith, phone 555-0321",
        "Hi, I need a dip powder service with Sophia Chen if she's available. This is Amanda Wilson, December 20th around 1 PM would be perfect"
    ]
    
    print("💅 HANA AI NAIL SALON BOOKING SYSTEM")
    print("=" * 50)
    
    for i, request in enumerate(sample_requests, 1):
        print(f"\n� NAIL BOOKING REQUEST #{i}")
        process_booking(request)
        
    print("\n✨ All nail booking requests processed!")
