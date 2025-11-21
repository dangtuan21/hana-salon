# 💅 Hana Salon Booking Service

AI-powered conversational booking system for salon appointments.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start the system (API + UI)
python restart_all.py
```

## 🌐 Access Points

- **💬 Chat Interface**: http://localhost:7860
- **📋 API Documentation**: http://localhost:8060/docs
- **🔧 Health Check**: http://localhost:8060/health

## 📁 Project Structure

```
ai-service/
├── api_server.py              # FastAPI server
├── conversation_handler.py    # Core conversational logic
├── gradio_ui.py              # Simple chat interface
├── start_booking_system.py   # System launcher
├── database.py               # Database operations
├── requirements.txt          # Dependencies
└── .env                      # Environment variables
```

## 💬 Example Conversations

```
"Hi, I'm Emma. I need a gel manicure tomorrow at 3 PM"
"Hello, I want complex nail art for my wedding on Dec 25th"
"Hi, I want a pedicure this Saturday. What times are available?"
```

## 🎯 Features

- **Natural Conversations** - Chat like you're calling the salon
- **Multi-Service Bookings** - Book multiple services in one appointment
- **Technician Preferences** - Request specific technicians
- **Conflict Resolution** - Handle scheduling conflicts intelligently
- **Real-time Availability** - Check and book available time slots
- **Simple UI** - Clean, focused chat interface

## 🛑 Stop System

Press `Ctrl+C` in the terminal or:
```bash
pkill -f "restart_all.py"
```
