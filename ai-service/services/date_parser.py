#!/usr/bin/env python3
"""
Date and Time Parser for Natural Language Processing
Converts human-friendly date/time expressions to structured formats
"""

from datetime import datetime, timedelta
import re
from typing import Optional, Tuple


class DateTimeParser:
    """Parses natural language date and time expressions"""
    
    def __init__(self):
        self.weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        self.time_patterns = {
            # 12-hour format patterns
            r'(\d{1,2})\s*pm': lambda h: str(int(h) + 12 if int(h) != 12 else 12).zfill(2) + ':00',
            r'(\d{1,2})\s*am': lambda h: str(int(h) if int(h) != 12 else 0).zfill(2) + ':00',
            r'(\d{1,2}):(\d{2})\s*pm': lambda h, m: str(int(h) + 12 if int(h) != 12 else 12).zfill(2) + ':' + m,
            r'(\d{1,2}):(\d{2})\s*am': lambda h, m: str(int(h) if int(h) != 12 else 0).zfill(2) + ':' + m,
            # 24-hour format patterns
            r'(\d{1,2}):(\d{2})$': lambda h, m: h.zfill(2) + ':' + m,
            r'(\d{1,2})$': lambda h: h.zfill(2) + ':00',
        }
        
        self.common_times = {
            'morning': '09:00',
            'afternoon': '14:00',
            'evening': '18:00',
            'noon': '12:00',
            'midnight': '00:00'
        }
    
    def parse_date(self, date_str: str, current_date: Optional[datetime] = None) -> Optional[str]:
        """
        Parse natural language date to ISO format (YYYY-MM-DD)
        
        Args:
            date_str: Natural language date like "Monday", "tomorrow", "next Friday"
            current_date: Reference date (defaults to today)
            
        Returns:
            ISO formatted date string or None if parsing fails
        """
        if current_date is None:
            current_date = datetime.now()
        
        date_str = date_str.lower().strip()
        print(f"🗓️ Parsing date: '{date_str}' (today: {current_date.strftime('%Y-%m-%d')})")
        
        # Handle relative dates
        if date_str == 'today':
            result = current_date.strftime('%Y-%m-%d')
            print(f"✅ Parsed 'today' → {result}")
            return result
            
        elif date_str == 'tomorrow':
            result = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"✅ Parsed 'tomorrow' → {result}")
            return result
            
        elif date_str == 'yesterday':
            result = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"✅ Parsed 'yesterday' → {result}")
            return result
        
        # Handle "next [weekday]"
        if date_str.startswith('next '):
            weekday_name = date_str[5:]
            if weekday_name in self.weekdays:
                target_weekday = self.weekdays[weekday_name]
                current_weekday = current_date.weekday()
                days_ahead = (target_weekday - current_weekday + 7) % 7
                if days_ahead == 0:  # If it's the same weekday, go to next week
                    days_ahead = 7
                result_date = current_date + timedelta(days=days_ahead)
                result = result_date.strftime('%Y-%m-%d')
                print(f"✅ Parsed 'next {weekday_name}' → {result}")
                return result
        
        # Handle weekday names (assume next occurrence)
        if date_str in self.weekdays:
            target_weekday = self.weekdays[date_str]
            current_weekday = current_date.weekday()
            days_ahead = (target_weekday - current_weekday) % 7
            
            # If it's the same weekday, decide based on context
            if days_ahead == 0:
                # If it's still early in the day, assume today; otherwise next week
                if current_date.hour < 18:  # Before 6 PM
                    result = current_date.strftime('%Y-%m-%d')
                    print(f"✅ Parsed '{date_str}' (today) → {result}")
                else:
                    result = (current_date + timedelta(days=7)).strftime('%Y-%m-%d')
                    print(f"✅ Parsed '{date_str}' (next week) → {result}")
                return result
            else:
                result_date = current_date + timedelta(days=days_ahead)
                result = result_date.strftime('%Y-%m-%d')
                print(f"✅ Parsed '{date_str}' → {result}")
                return result
        
        # Handle "in X days"
        in_days_match = re.match(r'in (\d+) days?', date_str)
        if in_days_match:
            days = int(in_days_match.group(1))
            result = (current_date + timedelta(days=days)).strftime('%Y-%m-%d')
            print(f"✅ Parsed 'in {days} days' → {result}")
            return result
        
        # Handle ISO format (already correct)
        iso_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        if iso_match:
            print(f"✅ Already ISO format → {date_str}")
            return date_str
        
        print(f"❌ Could not parse date: '{date_str}'")
        return None
    
    def parse_time(self, time_str: str) -> Optional[str]:
        """
        Parse natural language time to 24-hour format (HH:MM)
        
        Args:
            time_str: Natural language time like "1 PM", "2:30 AM", "morning"
            
        Returns:
            24-hour formatted time string or None if parsing fails
        """
        time_str = time_str.lower().strip()
        print(f"🕐 Parsing time: '{time_str}'")
        
        # Handle common time expressions
        if time_str in self.common_times:
            result = self.common_times[time_str]
            print(f"✅ Parsed common time '{time_str}' → {result}")
            return result
        
        # Try each time pattern
        for pattern, converter in self.time_patterns.items():
            match = re.search(pattern, time_str)
            if match:
                try:
                    if len(match.groups()) == 1:
                        result = converter(match.group(1))
                    else:
                        result = converter(match.group(1), match.group(2))
                    
                    # Validate time format
                    hour, minute = result.split(':')
                    if 0 <= int(hour) <= 23 and 0 <= int(minute) <= 59:
                        print(f"✅ Parsed time '{time_str}' → {result}")
                        return result
                except (ValueError, IndexError):
                    continue
        
        # Handle 24-hour format (already correct)
        if re.match(r'^\d{2}:\d{2}$', time_str):
            hour, minute = time_str.split(':')
            if 0 <= int(hour) <= 23 and 0 <= int(minute) <= 59:
                print(f"✅ Already 24-hour format → {time_str}")
                return time_str
        
        print(f"❌ Could not parse time: '{time_str}'")
        return None
    
    def parse_datetime(self, date_str: str, time_str: str, current_date: Optional[datetime] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse both date and time together
        
        Returns:
            Tuple of (parsed_date, parsed_time) or (None, None) if either fails
        """
        parsed_date = self.parse_date(date_str, current_date)
        parsed_time = self.parse_time(time_str)
        
        print(f"📅 Combined parsing result: {date_str} + {time_str} → {parsed_date} {parsed_time}")
        return parsed_date, parsed_time


# Global instance for easy importing
date_parser = DateTimeParser()


def parse_date(date_str: str, current_date: Optional[datetime] = None) -> Optional[str]:
    """Convenience function for date parsing"""
    return date_parser.parse_date(date_str, current_date)


def parse_time(time_str: str) -> Optional[str]:
    """Convenience function for time parsing"""
    return date_parser.parse_time(time_str)


def parse_datetime(date_str: str, time_str: str, current_date: Optional[datetime] = None) -> Tuple[Optional[str], Optional[str]]:
    """Convenience function for datetime parsing"""
    return date_parser.parse_datetime(date_str, time_str, current_date)
