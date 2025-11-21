#!/usr/bin/env python3
"""
Session Manager for Hana Salon Booking System
Uses direct database storage for persistent conversation sessions
"""

from typing import Dict, Optional, Any
from datetime import datetime
import uuid
import requests
import json
from .booking_state import BookingState, BookingStatus


class SessionManager:
    """Manages conversation sessions using direct database storage"""
    
    def __init__(self, backend_url: str = "http://localhost:3060"):
        # Direct database connection
        self.backend_url = backend_url.rstrip('/')
        self.sessions_api = f"{self.backend_url}/api/sessions"
        # Keep minimal in-memory cache for active sessions
        self._active_sessions: Dict[str, Dict] = {}
    
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
        
        # Store in active cache for immediate access
        self._active_sessions[session_id] = session_state
        
        # Store in database for persistence
        try:
            response = requests.post(
                f"{self.sessions_api}",
                json=session_state,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if response.status_code == 201:
                print(f"📝 Created new session in database: {session_id}")
            else:
                print(f"⚠️ Session created in cache only: {session_id}")
        except Exception as e:
            print(f"⚠️ Failed to store session in database: {e}")
        
        print(f"📝 Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID - checks cache first, then database"""
        # First check active cache
        session = self._active_sessions.get(session_id)
        
        if session:
            # Update last activity
            session["last_activity"] = datetime.now().isoformat()
            return session
        
        # If not in cache, try to load from database
        try:
            response = requests.get(
                f"{self.sessions_api}/{session_id}",
                timeout=5
            )
            if response.status_code == 200:
                session = response.json()
                session["last_activity"] = datetime.now().isoformat()
                
                # Cache it for future access
                self._active_sessions[session_id] = session
                print(f"📖 Loaded session from database: {session_id}")
                return session
        except Exception as e:
            print(f"⚠️ Failed to load session from database: {e}")
        
        return None
    
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
        if session_id in self._active_sessions:
            session_data["last_activity"] = datetime.now().isoformat()
            self._active_sessions[session_id] = session_data
            
            # Persist to database
            try:
                response = requests.put(
                    f"{self.sessions_api}/{session_id}",
                    json=session_data,
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"💾 Updated session in database: {session_id}")
            except Exception as e:
                print(f"⚠️ Failed to update session in database: {e}")
            
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
            print(f"🗑️ Deleted session: {session_id}")
            return True
        return False
    
    def list_sessions(self) -> Dict[str, Dict]:
        """List all active sessions (for debugging)"""
        return self._active_sessions.copy()
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up sessions older than max_age_hours"""
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        sessions_to_delete = []
        
        for session_id, session_data in self._active_sessions.items():
            last_activity = datetime.fromisoformat(session_data.get("last_activity", session_data["created_at"]))
            if last_activity < cutoff_time:
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            del self._active_sessions[session_id]
        
        if sessions_to_delete:
            print(f"🧹 Cleaned up {len(sessions_to_delete)} old sessions")
        
        return len(sessions_to_delete)
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self._active_sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        total_sessions = len(self._active_sessions)
        completed_sessions = sum(1 for s in self._active_sessions.values() if s.get("conversation_complete", False))
        active_sessions = total_sessions - completed_sessions
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate": completed_sessions / total_sessions if total_sessions > 0 else 0
        }
