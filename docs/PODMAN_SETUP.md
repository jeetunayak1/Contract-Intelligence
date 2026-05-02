# Podman Setup Guide

This guide explains how to run the Contract Intelligence System using Podman instead of Docker.

## Why Podman?

Podman is a daemonless container engine that's compatible with Docker but doesn't require root privileges. It's a great alternative to Docker Desktop, especially on macOS and Linux.

## Prerequisites

### 1. Install Podman

```bash
# macOS (using Homebrew)
brew install podman

# Initialize Podman machine (macOS only)
podman machine init
podman machine start

# Verify installation
podman --version
```

### 2. Install podman-compose

```bash
pip3 install podman-compose
```

## Running with Podman

### Option 1: Using podman-compose (Recommended)

This method uses containers for all services (backend, frontend, Redis):

```bash
# Start all services
./start-podman.sh

# Or manually:
podman-compose -f podman-compose.yml up --build
```

**Access Points:**
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend: http://localhost:3000

**Stop Services:**
```bash
./stop-podman.sh

# Or manually:
podman-compose -f podman-compose.yml down
```

### Option 2: Local Development (No Containers)

If you prefer to run services directly without containers:

```bash
# Start backend and frontend locally
./start-local.sh
```

This script will:
1. Create Python virtual environment if needed
2. Install Python dependencies
3. Start backend on port 8000
4. Install Node.js dependencies (if Node.js is installed)
5. Start frontend on port 3000

## Podman vs Docker Commands

Podman commands are nearly identical to Docker:

| Docker Command | Podman Equivalent |
|----------------|-------------------|
| `docker ps` | `podman ps` |
| `docker images` | `podman images` |
| `docker build` | `podman build` |
| `docker run` | `podman run` |
| `docker-compose up` | `podman-compose up` |
| `docker-compose down` | `podman-compose down` |

## Configuration

### Environment Variables

Make sure to configure your environment variables in `backend/.env`:

```bash
# Copy example file
cp backend/.env.example backend/.env

# Edit with your IBM Cloud credentials
nano backend/.env
```

Required variables:
- `CLOUDANT_URL` - Your Cloudant database URL
- `CLOUDANT_API_KEY` - Cloudant API key
- `WATSONX_API_KEY` - watsonx.ai API key
- `WATSONX_PROJECT_ID` - watsonx.ai project ID

### Redis Configuration

Redis is included in the podman-compose setup and runs on port 6379. The backend automatically connects to it.

## Troubleshooting

### Podman Machine Not Running (macOS)

```bash
# Check status
podman machine list

# Start machine
podman machine start

# If issues persist, recreate machine
podman machine stop
podman machine rm
podman machine init
podman machine start
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Find process using port 3000
lsof -ti:3000 | xargs kill -9
```

### Container Build Fails

```bash
# Clean up old containers and images
podman system prune -a

# Rebuild from scratch
podman-compose -f podman-compose.yml build --no-cache
```

### Permission Issues

Podman runs rootless by default, but if you encounter permission issues:

```bash
# Check Podman info
podman info

# Reset Podman machine (macOS)
podman machine stop
podman machine rm
podman machine init --rootful
podman machine start
```

## Development Workflow

### 1. Start Services
```bash
./start-podman.sh
```

### 2. View Logs
```bash
# All services
podman-compose -f podman-compose.yml logs -f

# Specific service
podman-compose -f podman-compose.yml logs -f backend
podman-compose -f podman-compose.yml logs -f frontend
```

### 3. Restart a Service
```bash
podman-compose -f podman-compose.yml restart backend
```

### 4. Access Container Shell
```bash
# Backend container
podman exec -it contract-backend /bin/bash

# Frontend container
podman exec -it contract-frontend /bin/sh
```

### 5. Stop Services
```bash
./stop-podman.sh
```

## Performance Tips

1. **Allocate More Resources** (macOS):
```bash
podman machine stop
podman machine set --cpus 4 --memory 8192
podman machine start
```

2. **Use Volume Mounts for Development**:
The podman-compose.yml already includes volume mounts for hot-reloading during development.

3. **Clean Up Regularly**:
```bash
# Remove unused containers, images, and volumes
podman system prune -a --volumes
```

## Advantages of Podman

1. **No Daemon**: Podman doesn't require a background daemon
2. **Rootless**: Runs without root privileges by default
3. **Docker Compatible**: Uses the same CLI commands and Dockerfile syntax
4. **Systemd Integration**: Can generate systemd unit files for services
5. **Pod Support**: Native support for Kubernetes-style pods

## Migration from Docker

If you're migrating from Docker:

1. **Alias Podman as Docker** (optional):
```bash
# Add to ~/.zshrc or ~/.bashrc
alias docker=podman
alias docker-compose=podman-compose
```

2. **Import Docker Images**:
```bash
# Save Docker image
docker save myimage:tag -o myimage.tar

# Load into Podman
podman load -i myimage.tar
```

3. **Use Existing Dockerfiles**:
Podman can use your existing Dockerfiles without modification.

## Additional Resources

- [Podman Documentation](https://docs.podman.io/)
- [Podman Desktop](https://podman-desktop.io/) - GUI for Podman
- [Podman Compose](https://github.com/containers/podman-compose)
- [Migrating from Docker to Podman](https://docs.podman.io/en/latest/markdown/podman-docker.1.html)

## Support

For issues specific to this project:
1. Check the main [SETUP_GUIDE.md](../SETUP_GUIDE.md)
2. Review [ARCHITECTURE.md](../ARCHITECTURE.md) for system design
3. See [CLOUDANT_SETUP.md](CLOUDANT_SETUP.md) for database configuration