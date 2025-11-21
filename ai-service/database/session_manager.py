#!/usr/bin/env python3
"""
Session Manager for Hana Salon Booking System
Handles in-memory conversation sessions (can be extended to use Redis/database)
"""

from typing import Dict, Optional, Any
from datetime import datetime
import uuid
from .booking_state import BookingState, BookingStatus


class SessionManager:
    """Manages conversation sessions for the booking system"""
    
    def __init__(self):
        # In-memory session storage (replace with Redis/database in production)
        self._sessions: Dict[str, Dict] = {}
    
    def create_session(self, customer_phone: str = None) -> str:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        
        # Create explicit BookingState instance
        booking_state = BookingState(
            customer_phone=customer_phone or "",
            status=BookingStatus.INITIAL  # Use correct default status
        )
        
        session_state = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "messages": [],
            "booking_state": booking_state.to_dict(),  # Convert to dict for storage
            "conversation_complete": False
        }
        
        self._sessions[session_id] = session_state
        print(f"📝 Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        session = self._sessions.get(session_id)
        if session:
            # Update last activity
            session["last_activity"] = datetime.now().isoformat()
        return session
    
    def get_booking_state(self, session_id: str) -> Optional[BookingState]:
        """Get BookingState as an explicit object"""
        session = self.get_session(session_id)
        if session and "booking_state" in session:
            return BookingState.from_dict(session["booking_state"])
        return None
    
    def update_booking_state(self, session_id: str, booking_state: BookingState) -> bool:
        """Update session with new BookingState"""
        session = self.get_session(session_id)
        if session:
            session["booking_state"] = booking_state.to_dict()
            session["last_activity"] = datetime.now().isoformat()
            return True
        return False
    
    def update_session(self, session_id: str, session_data: Dict) -> bool:
        """Update session data"""
        if session_id in self._sessions:
            session_data["last_activity"] = datetime.now().isoformat()
            self._sessions[session_id] = session_data
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            print(f"🗑️ Deleted session: {session_id}")
            return True
        return False
    
    def list_sessions(self) -> Dict[str, Dict]:
        """List all active sessions (for debugging)"""
        return self._sessions.copy()
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up sessions older than max_age_hours"""
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        sessions_to_delete = []
        
        for session_id, session_data in self._sessions.items():
            last_activity = datetime.fromisoformat(session_data.get("last_activity", session_data["created_at"]))
            if last_activity < cutoff_time:
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            del self._sessions[session_id]
        
        if sessions_to_delete:
            print(f"🧹 Cleaned up {len(sessions_to_delete)} old sessions")
        
        return len(sessions_to_delete)
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self._sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        total_sessions = len(self._sessions)
        completed_sessions = sum(1 for s in self._sessions.values() if s.get("conversation_complete", False))
        active_sessions = total_sessions - completed_sessions
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0
        }
