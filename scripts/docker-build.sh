#!/bin/bash

# Hana AI Salon - Docker Build Script

set -e

echo "🚀 Building Hana AI Salon Docker Images..."

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

# Build AI Service
print_status "Building AI Service (Python + FastAPI)..."
docker build -t hana-ai-service:latest ./ai-service
print_success "AI Service built successfully!"

# Build Backend
print_status "Building Backend (Node.js + TypeScript)..."
docker build -t hana-backend:latest ./backend
print_success "Backend built successfully!"

# Pull MongoDB image
print_status "Pulling MongoDB image..."
docker pull mongo:7.0
print_success "MongoDB image pulled successfully!"

# Pull Mongo Express (optional)
print_status "Pulling Mongo Express image..."
docker pull mongo-express:1.0.0
print_success "Mongo Express image pulled successfully!"

print_success "All images built successfully! 🎉"
print_status "To start the services, run: docker-compose up -d"
print_status "To start with development mode: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d"
