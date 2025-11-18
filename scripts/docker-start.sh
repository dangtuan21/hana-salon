#!/bin/bash

# Hana AI Salon - Docker Start Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default mode
MODE="production"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dev|--development)
            MODE="development"
            shift
            ;;
        -p|--prod|--production)
            MODE="production"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -d, --dev, --development    Start in development mode"
            echo "  -p, --prod, --production    Start in production mode (default)"
            echo "  -h, --help                  Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🚀 Starting Hana AI Salon in $MODE mode..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    if [ -f .env.docker ]; then
        print_warning ".env file not found. Copying from .env.docker template..."
        cp .env.docker .env
        print_warning "Please edit .env file and add your OpenAI API key!"
    else
        print_error ".env file not found. Please create one with your configuration."
        exit 1
    fi
fi

# Start services based on mode
if [ "$MODE" = "development" ]; then
    print_status "Starting services in development mode..."
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
else
    print_status "Starting services in production mode..."
    docker-compose up -d
fi

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
sleep 10

# Check service health
print_status "Checking service health..."

# MongoDB Atlas - no local container to check
print_success "✅ MongoDB Atlas (cloud-hosted)"

# Check AI Service
if docker-compose ps ai-service | grep -q "healthy"; then
    print_success "✅ AI Service is healthy"
else
    print_warning "⚠️  AI Service is starting up..."
fi

# Check Backend
if docker-compose ps backend | grep -q "healthy"; then
    print_success "✅ Backend is healthy"
else
    print_warning "⚠️  Backend is starting up..."
fi

print_success "🎉 Hana AI Salon is starting up!"
print_status "Services:"
print_status "  • Backend API: http://localhost:3060"
print_status "  • AI Service: http://localhost:8060"
print_status "  • MongoDB: Atlas Cloud (configured via MONGODB_URL)"

print_status ""
print_status "To view logs: docker-compose logs -f"
print_status "To stop services: docker-compose down"
print_status "To initialize Atlas database: python scripts/init-atlas.py"
