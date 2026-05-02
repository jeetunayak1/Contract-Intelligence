# Setup Guide - Contract Intelligence System

## Current Setup Status

### ✅ Completed
- Git repository initialized and pushed to GitHub
- Project structure created
- Python virtual environment created
- Dependencies being installed

### 🔄 In Progress
- Installing Python dependencies (FastAPI, IBM Cloud SDKs, etc.)

### ⚠️ Prerequisites Needed

#### 1. Node.js Installation (for Frontend)
```bash
# Install Node.js using Homebrew
brew install node

# Verify installation
node --version
npm --version
```

#### 2. Docker Installation (Optional - for containerized deployment)
```bash
# Install Docker Desktop for Mac
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker-compose --version
```

#### 3. IBM Cloud Credentials Required
You need to set up the following in `backend/.env`:

```env
# IBM Cloud Cloudant
CLOUDANT_URL=https://your-instance.cloudantnosqldb.appdomain.cloud
CLOUDANT_API_KEY=your-cloudant-api-key

# IBM watsonx.ai
WATSONX_API_KEY=your-watsonx-api-key
WATSONX_PROJECT_ID=your-project-id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# IBM Watson Discovery
WATSON_DISCOVERY_API_KEY=your-discovery-api-key
WATSON_DISCOVERY_URL=https://api.us-south.discovery.watson.cloud.ibm.com
WATSON_DISCOVERY_PROJECT_ID=your-discovery-project-id
```

## Quick Start (After Prerequisites)

### Option 1: Using Startup Script
```bash
# Make script executable
chmod +x start.sh

# Run the application
./start.sh
```

### Option 2: Manual Start

#### Backend Only (Current Status)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (After Node.js is installed)
```bash
cd frontend
npm install
npm start
```

### Option 3: Docker (After Docker is installed)
```bash
docker-compose up --build
```

## Access Points

Once running:
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000 (after Node.js setup)

## Next Steps

1. **Install Node.js** to run the frontend
2. **Get IBM Cloud credentials** from your IBM Cloud account
3. **Update backend/.env** with your credentials
4. **Start the application** using one of the methods above

## Troubleshooting

### Python 3.13 Compatibility Issues
If you encounter issues with IBM SDK packages:
```bash
cd backend
source venv/bin/activate
pip install setuptools
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Environment Variables Not Loading
Make sure `backend/.env` exists and contains all required variables.

## Documentation

- [`README.md`](README.md) - Project overview
- [`ARCHITECTURE.md`](ARCHITECTURE.md) - System architecture
- [`HACKATHON_GUIDE.md`](HACKATHON_GUIDE.md) - Day-by-day implementation guide
- [`docs/CLOUDANT_SETUP.md`](docs/CLOUDANT_SETUP.md) - Cloudant database setup
- [`docs/UI_PREVIEW.md`](docs/UI_PREVIEW.md) - UI features and components

## Support

For issues or questions:
1. Check the documentation files
2. Review error logs in the terminal
3. Verify all environment variables are set correctly
4. Ensure all prerequisites are installed