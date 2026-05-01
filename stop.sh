#!/bin/bash

# Contract Intelligence System - Stop Script
# This script stops both backend and frontend services

set -e

echo "🛑 Stopping Contract Intelligence System..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if PID files exist
if [ ! -f "logs/backend.pid" ] && [ ! -f "logs/frontend.pid" ]; then
    echo -e "${YELLOW}⚠️  No running services found${NC}"
    exit 0
fi

# Stop backend
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Stopping Backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo -e "${GREEN}✅ Backend stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend process not found${NC}"
    fi
    rm logs/backend.pid
fi

# Stop frontend
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend process not found${NC}"
    fi
    rm logs/frontend.pid
fi

# Also kill any remaining uvicorn or vite processes
echo ""
echo "Cleaning up any remaining processes..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ Application stopped successfully${NC}"

# Made with Bob
