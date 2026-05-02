#!/bin/bash

echo "🚀 Starting Contract Intelligence System with Podman..."

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "⚠️  podman-compose not found. Installing..."
    pip3 install podman-compose
fi

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "⚠️  Warning: backend/.env file not found"
    echo "Creating .env from .env.example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please update backend/.env with your IBM Cloud credentials"
fi

# Start services with podman-compose
echo "📦 Starting services with Podman..."
podman-compose -f podman-compose.yml up --build

echo "✅ Services started!"
echo ""
echo "Access points:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Frontend: http://localhost:3000"
echo ""
echo "To stop services, run: ./stop-podman.sh"

# Made with Bob
