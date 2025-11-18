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
python start_booking_system.py
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

## 🛠️ Manual Start (Alternative)

```bash
# Terminal 1: API Server
python api_server.py

# Terminal 2: Gradio UI
python gradio_ui.py
```

## 📋 Available Services

- Gel Manicure ($35, 45 min)
- Acrylic Full Set ($55, 90 min)
- Luxury Spa Pedicure ($65, 90 min)
- Complex Nail Art ($75, 120 min)
- Dip Powder Service ($45, 60 min)
- Basic Manicure ($25, 30 min)

## 👩‍💼 Expert Technicians

- Maria Rodriguez (Expert) - Nail art specialist
- Lauren Chen (Expert) - Spa treatments specialist
- Emma Wilson (Senior) - All-around technician
- Sofia Martinez (Master) - Premium nail art
- Isabella Torres (Senior) - Manicures & pedicures

## 🔧 Environment Variables

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## 📡 API Endpoints

- `POST /conversation/start` - Start booking conversation
- `POST /conversation/continue` - Continue conversation
- `GET /conversation/{id}/status` - Get conversation status
- `DELETE /conversation/{id}` - Clear conversation
- `GET /booking/{confirmation_id}` - Get booking details
- `GET /customer/{customer_id}` - Get customer info
- `GET /health` - Health check

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
pkill -f "start_booking_system.py"
```
