#!/usr/bin/env python3
"""
FastAPI server for Hana Salon Booking Service
Wraps the Langraph workflow in a REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import Dict, Any
import os
from dotenv import load_dotenv
from enum import Enum

# Import the existing booking workflow
from booking_app import process_booking, create_booking_workflow

class ValidationStatusCode(str, Enum):
    """Validation status codes for booking requests"""
    VALID = "VALID"
    INVALID = "INVALID"
    MISSING_INFO = "MISSING_INFO"
    INVALID_DATE = "INVALID_DATE"
    INVALID_SERVICE = "INVALID_SERVICE"
    INVALID_TECHNICIAN = "INVALID_TECHNICIAN"
    UNKNOWN = "UNKNOWN"

def parse_validation_status(validation_status: str) -> tuple[ValidationStatusCode, str]:
    """Parse validation status into code and text"""
    if " - " in validation_status:
        parts = validation_status.split(" - ", 1)
        code_str = parts[0].strip()
        text = parts[1].strip()
        
        # Map to enum
        if code_str == "VALID":
            return ValidationStatusCode.VALID, text
        elif code_str == "INVALID":
            return ValidationStatusCode.INVALID, text
        else:
            return ValidationStatusCode.UNKNOWN, text
            
    elif validation_status.startswith("VALID"):
        return ValidationStatusCode.VALID, "Booking validated successfully"
    elif validation_status.startswith("INVALID"):
        # Determine specific invalid type based on text
        text = validation_status.replace("INVALID", "").strip()
        if "service" in text.lower():
            return ValidationStatusCode.INVALID_SERVICE, text
        elif "date" in text.lower() or "time" in text.lower():
            return ValidationStatusCode.INVALID_DATE, text
        elif "technician" in text.lower():
            return ValidationStatusCode.INVALID_TECHNICIAN, text
        else:
            return ValidationStatusCode.INVALID, text
    else:
        return ValidationStatusCode.UNKNOWN, validation_status

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Hana Salon Booking Service",
    description="AI-powered salon booking system using Langraph",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class BookingRequest(BaseModel):
    booking_request: str

class ValidationRequest(BaseModel):
    booking_request: str

# Response models
class BookingResponse(BaseModel):
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
    validation_status_code: ValidationStatusCode
    validation_status_text: str
    confirmation_id: str
    final_response: str
    available_technicians: list
    service_details: dict
    messages: list

class ValidationResponse(BaseModel):
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
    validation_status_code: ValidationStatusCode
    validation_status_text: str
    available_technicians: list
    service_details: dict

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    langraph_status: str

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with service information"""
    return {
        "message": "💅 Hana Salon Booking & Scheduling Service",
        "version": "1.0.0",
        "status": "running",
        "focus": "Booking and scheduling operations only",
        "endpoints": {
            "health": "/health",
            "process_booking": "/process-booking",
            "validate_booking": "/validate-booking",
            "get_booking": "/booking/{confirmation_id}",
            "get_customer": "/customer/{customer_id}",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test if we can create the workflow
        workflow = create_booking_workflow()
        langraph_status = "healthy"
    except Exception as e:
        langraph_status = f"unhealthy: {str(e)}"
    
    return HealthResponse(
        status="healthy",
        service="hana-ai-booking-service",
        version="1.0.0",
        langraph_status=langraph_status
    )

@app.post("/process-booking", response_model=BookingResponse)
async def process_booking_endpoint(request: BookingRequest):
    """
    Process a complete booking request through the Langraph workflow
    """
    try:
        print(f"🔄 Processing booking request: {request.booking_request}")
        
        # Process the booking using the existing workflow
        result = process_booking(request.booking_request)
        
        # Parse validation status into structured format
        status_code, status_text = parse_validation_status(result['validation_status'])
        
        # Convert the result to our enhanced response model
        response = BookingResponse(
            customer_name=result['customer_name'],
            customer_phone=result['customer_phone'],
            service_id=result['service_id'],
            service_name=result['service_name'],
            technician_id=result['technician_id'],
            technician_name=result['technician_name'],
            date=result['date'],
            time=result['time'],
            duration_minutes=result['duration_minutes'],
            total_cost=result['total_cost'],
            validation_status_code=status_code,
            validation_status_text=status_text,
            confirmation_id=result['confirmation_id'],
            final_response=result['final_response'],
            available_technicians=result['available_technicians'],
            service_details=result['service_details'],
            messages=[msg.content if hasattr(msg, 'content') else str(msg) for msg in result.get('messages', [])]
        )
        
        print(f"✅ Booking processed successfully for {response.customer_name}")
        return response
        
    except Exception as e:
        print(f"❌ Error processing booking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process booking: {str(e)}")

@app.post("/validate-booking", response_model=ValidationResponse)
async def validate_booking_endpoint(request: ValidationRequest):
    """
    Validate a booking request without full processing (validation node only)
    """
    try:
        print(f"🔍 Validating booking request: {request.booking_request}")
        
        # Create workflow and run only validation node
        workflow = create_booking_workflow()
        
        # Initial state for validation only
        initial_state = {
            "messages": [],
            "booking_request": request.booking_request,
            "customer_name": "",
            "service_type": "",
            "date": "",
            "time": "",
            "validation_status": "",
            "confirmation_id": "",
            "final_response": ""
        }
        
        # Run only the validation node
        from booking_app import booking_validation_node
        validation_result = booking_validation_node(initial_state)
        
        # Parse validation status into structured format
        status_code, status_text = parse_validation_status(validation_result.get('validation_status', ''))
        
        response = ValidationResponse(
            customer_name=validation_result.get('customer_name', ''),
            customer_phone=validation_result.get('customer_phone', ''),
            service_id=validation_result.get('service_id', ''),
            service_name=validation_result.get('service_name', ''),
            technician_id=validation_result.get('technician_id', ''),
            technician_name=validation_result.get('technician_name', ''),
            date=validation_result.get('date', ''),
            time=validation_result.get('time', ''),
            duration_minutes=validation_result.get('duration_minutes', 0),
            total_cost=validation_result.get('total_cost', 0.0),
            validation_status_code=status_code,
            validation_status_text=status_text,
            available_technicians=validation_result.get('available_technicians', []),
            service_details=validation_result.get('service_details', {})
        )
        
        print(f"✅ Validation completed for {response.customer_name}")
        return response
        
    except Exception as e:
        print(f"❌ Error validating booking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate booking: {str(e)}")

@app.get("/booking/{confirmation_id}")
async def get_booking_by_confirmation(confirmation_id: str):
    """Get booking details by confirmation ID"""
    from database import get_db_manager
    
    db = get_db_manager()
    booking = db.get_booking_by_confirmation_id(confirmation_id)
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Get related information
    service = db.get_service_by_id(booking.service_id)
    technician = db.get_technician_by_id(booking.technician_id)
    customer = db.get_customer_by_id(booking.customer_id)
    
    return {
        "booking": {
            "id": booking._id,
            "confirmation_id": booking.confirmation_id,
            "date": booking.date,
            "time": booking.time,
            "duration_minutes": booking.duration_minutes,
            "total_cost": booking.total_cost,
            "status": booking.status,
            "notes": booking.notes,
            "created_at": booking.created_at.isoformat() if booking.created_at else None
        },
        "customer": {
            "name": customer.name if customer else "Unknown",
            "phone": customer.phone if customer else "N/A"
        },
        "service": {
            "name": service.name if service else "Unknown Service",
            "description": service.description if service else ""
        },
        "technician": {
            "name": technician.name if technician else "Unknown Technician",
            "skill_level": technician.skill_level if technician else "N/A"
        }
    }

@app.get("/customer/{customer_id}")
async def get_customer_by_id(customer_id: str):
    """Get customer details by customer ID"""
    from database import get_db_manager
    
    try:
        db = get_db_manager()
        customer = db.get_customer_by_id(customer_id)
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return {
            "customer": {
                "id": customer._id,
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email,
                "preferences": customer.preferences or {},
                "booking_history": customer.booking_history or [],
                "created_at": customer.created_at.isoformat() if customer.created_at else None
            }
        }
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        print(f"❌ Error in customer endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8060))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Hana Salon Booking Service on {host}:{port}")
    print(f"📋 API Documentation available at: http://{host}:{port}/docs")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
