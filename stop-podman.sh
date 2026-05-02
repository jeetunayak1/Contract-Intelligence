#!/bin/bash

echo "🛑 Stopping Contract Intelligence System (Podman)..."

# Stop all services
podman-compose -f podman-compose.yml down

echo "✅ All services stopped!"

# Made with Bob
