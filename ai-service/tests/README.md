# Test Suite

This folder contains all test files for the Hana AI Booking System.

## Test Files

### Core Functionality Tests
- **`test_conversation.py`** - Basic conversation flow testing
- **`test_backend_alignment.py`** - Tests alignment between AI service and backend API
- **`test_api_logs.py`** - API endpoint logging and debugging tests

### Date/Time Confirmation Tests
- **`test_confirmation.py`** - Main date/time confirmation flow test
- **`test_confirmation_action.py`** - Tests confirm_datetime action handling
- **`test_current_issue.py`** - Tests for the "November 3" date issue fix
- **`test_new_confirmation_format.py`** - Tests enhanced confirmation message format
- **`test_second_message_format.py`** - Tests LLM response formatting in multi-turn conversations

### Date Parsing Tests
- **`test_date_parser.py`** - General date/time parsing functionality
- **`test_date_parsing.py`** - Tests for abbreviated weekday name parsing (fri, mon, etc.)

## Running Tests

To run individual tests:
```bash
# From the ai-service directory
python tests/test_confirmation.py
python tests/test_date_parsing.py
```

To run all tests:
```bash
# From the ai-service directory
for test in tests/test_*.py; do echo "Running $test"; python "$test"; echo; done
```

## Test Dependencies

All tests require:
- AI service running on port 8060
- Backend API running on port 3060
- OPENAI_API_KEY environment variable set

Start the system with:
```bash
python start_booking_system.py
```
