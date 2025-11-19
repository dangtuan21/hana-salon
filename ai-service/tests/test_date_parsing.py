#!/usr/bin/env python3
"""
Test date parsing with abbreviated weekday names
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.date_parser import parse_date
from datetime import datetime

def test_abbreviated_dates():
    print("🧪 Testing Abbreviated Date Parsing...")
    print("=" * 50)
    
    # Test current date context
    current_date = datetime(2025, 11, 18)  # Monday
    print(f"📅 Reference date: {current_date.strftime('%A, %Y-%m-%d')} (Monday)")
    
    test_cases = [
        "fri",
        "friday", 
        "mon",
        "monday",
        "tue",
        "tuesday"
    ]
    
    for date_str in test_cases:
        result = parse_date(date_str, current_date)
        if result:
            parsed_date = datetime.fromisoformat(result)
            print(f"✅ '{date_str}' → {result} ({parsed_date.strftime('%A')})")
        else:
            print(f"❌ '{date_str}' → Failed to parse")

if __name__ == "__main__":
    test_abbreviated_dates()
