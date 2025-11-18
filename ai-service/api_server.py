#!/usr/bin/env python3
"""
FastAPI server for Hana AI Nail Salon Booking Service
Wraps the Langraph workflow in a REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Import the existing booking workflow
from booking_app import process_booking, create_booking_workflow

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Hana AI Nail Salon Booking Service",
    description="AI-powered nail salon booking system using Langraph",
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
    validation_status: str
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
    validation_status: str
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
        "message": "💅 Hana AI Nail Salon Booking & Scheduling Service",
        "version": "1.0.0",
        "status": "running",
        "focus": "Booking and scheduling operations only",
        "endpoints": {
            "health": "/health",
            "process_booking": "/process-booking",
            "validate_booking": "/validate-booking",
            "get_booking": "/booking/{confirmation_id}",
            "update_booking_status": "/booking/{confirmation_id}/status",
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
            validation_status=result['validation_status'],
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
        
        response = ValidationResponse(
            customer_name=validation_result['customer_name'],
            service_type=validation_result['service_type'],
            date=validation_result['date'],
            time=validation_result['time'],
            validation_status=validation_result['validation_status']
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

@app.put("/booking/{confirmation_id}/status")
async def update_booking_status(confirmation_id: str, status: str):
    """Update booking status (confirmed, completed, cancelled)"""
    from database import get_db_manager
    
    valid_statuses = ["confirmed", "completed", "cancelled", "no_show"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    db = get_db_manager()
    booking = db.get_booking_by_confirmation_id(confirmation_id)
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    success = db.update_booking_status(booking._id, status)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update booking status")
    
    return {
        "success": True,
        "confirmation_id": confirmation_id,
        "new_status": status,
        "message": f"Booking status updated to {status}"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8060))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Hana AI Booking Service on {host}:{port}")
    print(f"📋 API Documentation available at: http://{host}:{port}/docs")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
