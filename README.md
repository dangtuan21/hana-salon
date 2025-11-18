# Hana AI - Nail Salon Booking System

A microservices-based AI-powered nail salon booking application with service-oriented architecture.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │    Backend      │    │   AI Service    │
│                 │    │                 │    │                 │
│  ├─ Web App     │◄──►│  Node.js +      │◄──►│  Python +       │
│  └─ Mobile App  │    │  Express +      │    │  Langraph +     │
│                 │    │  TypeScript     │    │  FastAPI        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
hana-ai/
├── backend/           # Node.js + Express + TypeScript API
│   ├── src/
│   │   ├── controllers/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── types/
│   │   └── server.ts
│   ├── package.json
│   └── tsconfig.json
├── frontend/
│   ├── webapp/        # React/Next.js web application
│   └── mobile-app/    # React Native mobile app
├── ai-service/        # Python Langraph AI service
│   ├── booking_app.py
│   ├── api_server.py
│   ├── salon_data.py
│   └── requirements.txt
└── README.md
```

## 🚀 Quick Start

### 🐳 Docker (Recommended)
```bash
# 1. Clone and setup
git clone <repository>
cd hana-ai

# 2. Configure environment
cp .env.docker .env
# Edit .env and add your OpenAI API key

# 3. Build and start services
./scripts/docker-build.sh
./scripts/docker-start.sh

# Or use docker-compose directly
docker-compose up -d

# Initialize database
docker-compose exec ai-service python init_database.py
```

### 🔧 Manual Setup (Development)

#### 1. Backend (Node.js + TypeScript)
```bash
cd backend
npm install
npm run dev
```

#### 2. AI Service (Python + Langraph + MongoDB)
```bash
# Install MongoDB (macOS)
brew install mongodb-community
brew services start mongodb-community

# Setup AI Service
cd ai-service
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI API key

# Initialize database with salon data
python init_database.py

# Start the AI service
python api_server.py
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
# Initialize database with sample data
docker-compose exec ai-service python init_database.py

# Access MongoDB shell
docker-compose exec mongodb mongosh

# Access Mongo Express (development mode)
# http://localhost:8081 (admin/admin123)
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

**Customers Management:**
- **Get All Customers**: `GET /api/customers`
- **Get Customer**: `GET /api/customers/:id`
- **Get by Phone**: `GET /api/customers/phone/:phone`
- **Create Customer**: `POST /api/customers`
- **Update Customer**: `PUT /api/customers/:id`
- **Delete Customer**: `DELETE /api/customers/:id`
- **Search Customers**: `GET /api/customers/search?q=term`
- **Add Booking**: `PUT /api/customers/:id/bookings`

### AI Service (Port 8060) - Booking & Scheduling Only
- **Process Booking**: `POST /process-booking`
- **Validate Booking**: `POST /validate-booking`
- **Get Booking**: `GET /booking/{confirmation_id}`
- **Update Booking Status**: `PUT /booking/{confirmation_id}/status`
- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs`

## 💅 Supported Nail Services
- Basic Manicure/Pedicure
- Gel Manicure/Pedicure  
- Acrylic Nails
- Nail Extensions
- Nail Art/Design
- French Manicure
- Dip Powder Nails

## 🔄 Langraph Workflow
The AI service uses a 2-node Langraph workflow:
- **Node 1**: Nail Booking Validation
- **Node 2**: Nail Booking Confirmation
