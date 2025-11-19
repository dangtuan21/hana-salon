#!/usr/bin/env python3
"""
FastAPI server for Hana Salon Booking Service
Pure LLM conversational booking system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Legacy imports removed - using conversational approach now

# Legacy validation status handling removed - conversational approach handles this naturally

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Hana Salon Booking Service",
    description="AI-powered conversational booking system",
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

# Legacy models removed - using conversational approach now

# New conversational booking models
class ConversationStartRequest(BaseModel):
    message: str
    customer_phone: str = None

class ConversationContinueRequest(BaseModel):
    session_id: str
    message: str

class ConversationResponse(BaseModel):
    session_id: str
    response: str
    booking_state: dict
    conversation_complete: bool
    actions_taken: List[str] = []
    next_suggestions: List[str] = []

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
            "get_booking": "/booking/{confirmation_id}",
            "get_customer": "/customer/{customer_id}",
            "start_conversation": "/conversation/start",
            "continue_conversation": "/conversation/continue",
            "conversation_status": "/conversation/{session_id}/status",
            "clear_conversation": "/conversation/{session_id}",
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

# Import conversation handler
from conversation_handler import conversation_handler

@app.post("/conversation/start", response_model=ConversationResponse)
async def start_conversation(request: ConversationStartRequest):
    """Start a new conversation"""
    try:
        print("=" * 80)
        print(f"🚨 DEBUG: API ENDPOINT CALLED - START CONVERSATION")
        print(f"🗣️ Starting new conversation: {request.message}")
        print("=" * 80)
        
        response = conversation_handler.start_conversation(
            message=request.message,
            customer_phone=request.customer_phone
        )
        
        print(f"✅ Conversation started with session ID: {response['session_id']}")
        return ConversationResponse(**response)
        
    except Exception as e:
        print(f"❌ Error starting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start conversation: {str(e)}")

@app.post("/conversation/continue", response_model=ConversationResponse)
async def continue_conversation(request: ConversationContinueRequest):
    """Continue an existing conversation"""
    try:
        print("=" * 80)
        print(f"🚨 DEBUG: API ENDPOINT CALLED - CONTINUE CONVERSATION")
        print(f"🗣️ Continuing conversation {request.session_id}: {request.message}")
        print("=" * 80)
        
        response = conversation_handler.continue_conversation(
            session_id=request.session_id,
            message=request.message
        )
        
        print(f"✅ Conversation continued for session: {request.session_id}")
        return ConversationResponse(**response)
        
    except ValueError as e:
        print(f"❌ Session not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ Error continuing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to continue conversation: {str(e)}")

@app.get("/conversation/{session_id}/status")
async def get_conversation_status(session_id: str):
    """Get the current status of a conversation session"""
    try:
        session_info = conversation_handler.get_session_info(session_id)
        
        if not session_info:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "session_id": session_id,
            "created_at": session_info["created_at"],
            "message_count": len(session_info["messages"]),
            "booking_state": session_info["booking_state"],
            "conversation_complete": session_info["conversation_complete"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting conversation status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation status: {str(e)}")

@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear a conversation session"""
    try:
        success = conversation_handler.clear_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {"message": f"Session {session_id} cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation: {str(e)}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8060))  # AI service runs on 8060, backend on 3060
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
