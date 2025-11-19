#!/usr/bin/env python3
"""
Test script to demonstrate conversation handler logging
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conversation_handler import conversation_handler

def test_conversation():
    print("🧪 Testing conversation handler with debug logging...")
    print("=" * 60)
    
    # Test message that should trigger backend calls
    test_message = "Hi, I'm Teo and my phone is 555-1234. I want to book a Gel Manicure for Monday at 1 PM."
    
    print(f"📨 Sending test message: {test_message}")
    print("-" * 60)
    
    try:
        # Start a conversation
        response = conversation_handler.start_conversation(test_message)
        
        print("-" * 60)
        print("📋 Response received:")
        print(f"Session ID: {response.get('session_id')}")
        print(f"Response: {response.get('response')}")
        print(f"Booking State: {response.get('booking_state')}")
        print(f"Actions Taken: {response.get('actions_taken')}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversation()
