#!/usr/bin/env python3
"""
Simple test script for the Hana AI Booking System
"""

from booking_app import process_booking

def interactive_booking():
    """
    Interactive booking system for testing
    """
    print("🏨 HANA AI BOOKING SYSTEM - INTERACTIVE MODE")
    print("=" * 50)
    print("Enter your booking request (or 'quit' to exit)")
    print("Example: 'Hi, I'm Alice and I want to book a spa appointment for tomorrow at 3 PM'")
    print("-" * 50)
    
    while True:
        booking_request = input("\n📝 Your booking request: ").strip()
        
        if booking_request.lower() in ['quit', 'exit', 'q']:
            print("👋 Thank you for using Hana AI Booking System!")
            break
            
        if not booking_request:
            print("❌ Please enter a valid booking request.")
            continue
            
        try:
            process_booking(booking_request)
        except Exception as e:
            print(f"❌ Error processing booking: {str(e)}")
            print("Please make sure you have set up your OpenAI API key in .env file")

def run_sample_tests():
    """
    Run predefined test cases
    """
    print("🧪 RUNNING SAMPLE TEST CASES")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Valid Restaurant Booking",
            "request": "Hello, I'm Emma Watson and I'd like to reserve a table for 4 people at your restaurant on December 25th, 2024 at 8:00 PM"
        },
        {
            "name": "Valid Medical Appointment",
            "request": "Hi, this is Dr. Smith's patient, Robert Brown. I need to schedule a follow-up appointment for January 5th, 2025 at 10:30 AM"
        },
        {
            "name": "Incomplete Hotel Booking",
            "request": "I want to book a room for Christmas"
        },
        {
            "name": "Valid Spa Appointment",
            "request": "My name is Lisa Chen, I'd like to book a massage therapy session for this Friday at 2 PM"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST CASE #{i}: {test_case['name']}")
        print("-" * 30)
        try:
            process_booking(test_case['request'])
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_booking()
    else:
        run_sample_tests()
