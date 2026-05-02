#!/bin/bash

echo "🚀 Starting Contract Intelligence System (Local Mode)..."

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "⚠️  Warning: backend/.env file not found"
    echo "Creating .env from .env.example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please update backend/.env with your IBM Cloud credentials"
fi

# Check if virtual environment exists
if [ ! -d backend/venv ]; then
    echo "📦 Creating Python virtual environment..."
    cd backend && python3 -m venv venv && cd ..
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is not installed"
    echo "Please install Node.js: brew install node"
    echo ""
    echo "Starting backend only..."
    
    # Start backend only
    cd backend
    source venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -f venv/lib/python*/site-packages/fastapi ]; then
        echo "📦 Installing Python dependencies..."
        pip install -r requirements-minimal.txt
    fi
    
    echo "🚀 Starting backend server..."
    python -m uvicorn app.main_demo:app --reload --host 0.0.0.0 --port 8000
    
else
    echo "✅ Node.js found"
    
    # Start backend in background
    cd backend
    source venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -f venv/lib/python*/site-packages/fastapi ]; then
        echo "📦 Installing Python dependencies..."
        pip install -r requirements-minimal.txt
    fi
    
    echo "🚀 Starting backend server..."
    python -m uvicorn app.main_demo:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    cd frontend
    if [ ! -d node_modules ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
    fi
    
    echo "🚀 Starting frontend..."
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✅ Services started!"
    echo ""
    echo "Access points:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - Frontend: http://localhost:3000"
    echo ""
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo ""
    echo "To stop services, run: ./stop-local.sh"
    
    # Wait for both processes
    wait
fi

# Made with Bob
