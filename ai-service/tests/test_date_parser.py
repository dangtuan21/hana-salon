#!/usr/bin/env python3
"""
Test script for date/time parser
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.date_parser import parse_date, parse_time
from datetime import datetime

def test_date_parser():
    print("🧪 Testing Date/Time Parser")
    print("=" * 50)
    
    # Current date for reference (2025-11-18)
    current_date = datetime(2025, 11, 18)  # Tuesday (Nov 18, 2025 is actually Tuesday)
    print(f"📅 Reference date: {current_date.strftime('%Y-%m-%d %A')}")
    print()
    
    # Test date parsing
    print("🗓️ Testing Date Parsing:")
    test_dates = [
        "Monday",
        "Tuesday", 
        "Friday",
        "next Monday",
        "tomorrow",
        "today"
    ]
    
    for date_str in test_dates:
        result = parse_date(date_str, current_date)
        print(f"  '{date_str}' → {result}")
    
    print()
    
    # Test time parsing
    print("🕐 Testing Time Parsing:")
    test_times = [
        "1 PM",
        "2:30 PM",
        "9 AM",
        "12:00 PM",
        "morning",
        "afternoon",
        "13:00"
    ]
    
    for time_str in test_times:
        result = parse_time(time_str)
        print(f"  '{time_str}' → {result}")

if __name__ == "__main__":
    test_date_parser()
