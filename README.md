# 💅 Hana AI Salon Booking System

An intelligent, microservices-based AI-powered salon booking application with advanced conversational AI, persistent memory, and Google Calendar integration.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │    Backend      │    │   AI Service    │
│   (In Progress) │    │                 │    │                 │
│  ├─ Web App     │◄──►│  Node.js +      │◄──►│  Python +       │
│  └─ Mobile App  │    │  Express +      │    │  LangChain +    │
│                 │    │  TypeScript +   │    │  FastAPI +      │
│                 │    │  MongoDB        │    │  Gradio UI      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                └────────────────────────┘
                                      MongoDB Atlas
                                   (Persistent Storage)
```

## ✨ Key Features

- **🤖 Conversational AI**: Natural language booking with LangChain-powered conversation handler
- **💾 Persistent Memory**: Database-backed session storage with conversation history
- **📅 Google Calendar Integration**: Automatic calendar sync for bookings and appointments
- **⚡ Batch Operations**: Optimized technician availability checking
- **🔄 Real-time Sync**: Live session updates with hybrid cache + database architecture
- **🎯 Smart Scheduling**: AI-powered technician matching and alternative time suggestions
- **📊 Business Intelligence**: Conversation analytics and booking pattern insights

## 📁 Project Structure

```
hana-ai/
├── backend/                    # Node.js + Express + TypeScript API
│   ├── src/
│   │   ├── controllers/        # Request handlers
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic & Google Calendar
│   │   ├── models/            # MongoDB schemas
│   │   ├── middleware/        # Auth, validation, logging
│   │   ├── types/             # TypeScript definitions
│   │   └── server.ts          # Express server setup
│   ├── tests/                 # Comprehensive test suite
│   ├── package.json
│   └── tsconfig.json
├── frontend/                   # Frontend applications (In Development)
│   ├── web/                   # React/Next.js web application
│   └── mobile/                # React Native mobile app
├── ai-service/                # Python LangChain AI service
│   ├── api_server.py          # FastAPI server
│   ├── conversation_handler.py # Core AI conversation logic
│   ├── database/              # Session & conversation storage
│   │   ├── session_manager.py # Persistent session management
│   │   └── models.py          # Database models
│   ├── services/              # AI service components
│   │   ├── action_executor.py # Booking actions
│   │   └── backend_api_client.py # Backend integration
│   ├── tests/                 # AI service test suite
│   ├── gradio_ui.py          # Interactive web UI
│   └── requirements.txt
├── scripts/                   # Deployment & utility scripts
└── docker-compose.yml         # Multi-service orchestration
```

## 🚀 Quick Start

### 🐳 Docker (Recommended)
```bash
# 1. Clone and setup
git clone <repository>
cd hana-ai

# 2. Configure environment
cp .env.docker .env
# Edit .env and add your OpenAI API key and MongoDB connection string

# 3. Build and start services
./scripts/docker-build.sh
./scripts/docker-start.sh

# Or use docker-compose directly
docker-compose up -d

# 4. Access the services
# - Backend API: http://localhost:3060
# - AI Service API: http://localhost:8060
# - AI Gradio UI: http://localhost:7860
# - API Documentation: http://localhost:8060/docs
```

### 🔧 Manual Setup (Development)

#### 1. Backend (Node.js + TypeScript)
```bash
cd backend
npm install
npm run dev
```

#### 2. AI Service (Python + LangChain + MongoDB Atlas)
```bash
# Setup AI Service
cd ai-service
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI API key and MongoDB Atlas connection string

# Start the AI service
python api_server.py

# Optional: Start Gradio UI for interactive testing
python gradio_ui.py
```

#### 3. Frontend (Coming Soon)
```bash
cd frontend/webapp
npm install
npm run dev
```

## 🐳 Docker Commands

### Production Mode
```bash
# Build all images
./scripts/docker-build.sh

# Start services
./scripts/docker-start.sh

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Development Mode
```bash
# Start in development mode (with hot reload)
./scripts/docker-start.sh --dev

# Or manually
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View specific service logs
docker-compose logs -f ai-service
docker-compose logs -f backend
```

### Database Management
```bash
# View session data and logs
docker-compose exec ai-service python view_logs.py

# Run comprehensive tests
docker-compose exec backend npm test
docker-compose exec ai-service python run_tests.py

# Restart all services with fresh data
docker-compose exec ai-service python restart_all.py
```

## 🔧 Services

### Backend API (Port 3060) - Full CRUD Operations
**Health & Booking:**
- **Health Check**: `GET /api/health`
- **Process Booking**: `POST /api/bookings/process`
- **Validate Booking**: `POST /api/bookings/validate`
- **Booking Status**: `GET /api/bookings/status/:id`

**Services Management:**
- **Get All Services**: `GET /api/services`
- **Get Service**: `GET /api/services/:id`
- **Create Service**: `POST /api/services`
- **Update Service**: `PUT /api/services/:id`
- **Delete Service**: `DELETE /api/services/:id`
- **Get Categories**: `GET /api/services/categories`

**Technicians Management:**
- **Get All Technicians**: `GET /api/technicians`
- **Get Technician**: `GET /api/technicians/:id`
- **Create Technician**: `POST /api/technicians`
- **Update Technician**: `PUT /api/technicians/:id`
- **Delete Technician**: `DELETE /api/technicians/:id`
- **Get by Service**: `GET /api/technicians/service/:serviceId`
- **Update Availability**: `PUT /api/technicians/:id/availability`
- **Batch Check Availability**: `POST /api/technicians/batch-check-availability`

**Customers Management:**
- **Get All Customers**: `GET /api/customers`
- **Get Customer**: `GET /api/customers/:id`
- **Get by Phone**: `GET /api/customers/phone/:phone`
- **Create Customer**: `POST /api/customers`
- **Update Customer**: `PUT /api/customers/:id`
- **Delete Customer**: `DELETE /api/customers/:id`
- **Search Customers**: `GET /api/customers/search?q=term`
- **Add Booking**: `PUT /api/customers/:id/bookings`

### AI Service (Port 8060) - Conversational AI & Session Management
**Conversation Endpoints:**
- **Start Conversation**: `POST /conversation`
- **Send Message**: `POST /conversation/{session_id}/message`
- **Get Session**: `GET /conversation/{session_id}`
- **Clear Session**: `DELETE /conversation/{session_id}`

**Legacy Booking Endpoints:**
- **Process Booking**: `POST /process-booking`
- **Validate Booking**: `POST /validate-booking`
- **Get Booking**: `GET /booking/{confirmation_id}`
- **Update Booking Status**: `PUT /booking/{confirmation_id}/status`

**System Endpoints:**
- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs`

### Gradio UI (Port 7860) - Interactive Testing Interface
- **Web Interface**: `http://localhost:7860`
- **Real-time Conversation Testing**
- **Session Management Tools**
- **Booking Flow Simulation**

## 💅 Supported Services
- Basic Manicure/Pedicure
- Gel Manicure/Pedicure  
- Acrylic Nails
- Nail Extensions
- Nail Art/Design
- French Manicure
- Dip Powder Nails

## 🤖 AI Architecture

### LangChain Conversation Handler
The AI service uses an advanced conversation handler with:
- **Natural Language Processing**: Understands customer booking requests
- **Context Awareness**: Maintains conversation state and booking context
- **Smart Actions**: Executes booking operations based on conversation flow
- **Error Handling**: Graceful fallbacks and user guidance

### Session Management
- **Persistent Storage**: Sessions survive service restarts
- **Hybrid Architecture**: Active cache + MongoDB database
- **Real-time Sync**: All updates immediately persisted
- **TTL Cleanup**: Automatic session expiration management

### Performance Optimizations
- **Batch Operations**: Multiple technician availability checks in single API call
- **Intelligent Caching**: Frequently accessed data cached for speed
- **Async Processing**: Non-blocking operations for better responsiveness

## 🧪 Testing

### Backend Tests
```bash
cd backend
npm test                    # Run all tests
npm run test:watch         # Watch mode
npm run test:crud          # CRUD operations
npm run test:calendar      # Google Calendar integration
```

### AI Service Tests
```bash
cd ai-service
python run_tests.py        # Individual test runner
python run_batch_tests.py  # Batch test execution
```

## 📈 Performance Metrics

- **50-100% improvement** in technician availability checking via batch operations
- **Persistent memory** enables conversation continuity across restarts
- **Real-time sync** maintains data consistency between cache and database
- **Comprehensive test coverage** with 34+ backend tests and 12+ AI service tests

## 🔧 Environment Configuration

### Required Environment Variables

**Backend (.env):**
```bash
# Database
MONGODB_URI=mongodb+srv://...
DATABASE_NAME=hana_salon

# Google Calendar Integration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3060/auth/google/callback

# Server Configuration
PORT=3060
NODE_ENV=development
```

**AI Service (.env):**
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Database
MONGODB_URI=mongodb+srv://...
DATABASE_NAME=hana_salon

# Service Configuration
BACKEND_URL=http://localhost:3060
```

## 🚀 Deployment

### Production Considerations
- **MongoDB Atlas**: Configured for cloud database hosting
- **Environment Security**: All sensitive keys in environment variables
- **Docker Orchestration**: Multi-service deployment with docker-compose
- **Health Checks**: Comprehensive monitoring endpoints
- **Logging**: Structured logging with Winston (backend) and Python logging (AI service)
- **Error Handling**: Graceful degradation and user-friendly error messages

### Scaling Options
- **Horizontal Scaling**: Multiple AI service instances with shared MongoDB
- **Load Balancing**: Backend API can be load balanced across multiple instances
- **Database Optimization**: MongoDB Atlas provides automatic scaling and optimization
- **Caching Strategy**: Redis can be added for enhanced session caching

## 📚 Additional Documentation

- **Backend Setup**: `backend/README.md`
- **AI Service Details**: `ai-service/README.md`
- **Google Calendar Setup**: `backend/GOOGLE_CALENDAR_SETUP.md`
- **HTTPS Configuration**: `backend/HTTPS_SETUP.md`

---

**Built with ❤️ for intelligent salon management**
