# Quick Start Guide - Demo Mode

Get the Contract Intelligence System running in under 5 minutes!

## ✅ What's Already Done

- ✅ Backend server running on http://localhost:8000
- ✅ Python dependencies installed
- ✅ Demo API with sample data
- ✅ Node.js installation in progress

## 🚀 Current Status

### Backend (Running)
```
✓ FastAPI server: http://localhost:8000
✓ API Documentation: http://localhost:8000/docs
✓ Demo mode: Works without IBM Cloud credentials
```

### Available Endpoints

1. **Root**: http://localhost:8000/
2. **Contracts**: http://localhost:8000/api/v1/contracts
3. **Compliance Metrics**: http://localhost:8000/api/v1/compliance/metrics
4. **Risks**: http://localhost:8000/api/v1/risks
5. **Alerts**: http://localhost:8000/api/v1/alerts
6. **Dashboard Analytics**: http://localhost:8000/api/v1/analytics/dashboard

### Test the API

```bash
# Get all contracts
curl http://localhost:8000/api/v1/contracts

# Get compliance metrics
curl http://localhost:8000/api/v1/compliance/metrics

# Get risk assessments
curl http://localhost:8000/api/v1/risks

# Get active alerts
curl http://localhost:8000/api/v1/alerts

# Get dashboard data
curl http://localhost:8000/api/v1/analytics/dashboard
```

## 📱 Next: Start Frontend

Once Node.js installation completes:

```bash
# In a new terminal
cd frontend
npm install
npm start
```

The frontend will be available at: http://localhost:3000

## 🎯 Demo Features

### Sample Data Included

**Contracts:**
- CTR-2024-001: Acme Corporation ($500,000)
- CTR-2024-002: TechStart Inc ($250,000)

**Compliance Metrics:**
- Overall compliance: 92%
- Active contracts: 15
- Compliant contracts: 14
- At-risk contracts: 1

**Risk Assessments:**
- RISK-001: SLA threshold approaching (Medium)
- RISK-002: Contract renewal at risk (High)

**Active Alerts:**
- ALERT-001: SLA breach detected (High)
- ALERT-002: Contract expiring in 30 days (Medium)

## 🔧 Troubleshooting

### Backend Not Responding?
```bash
# Check if server is running
curl http://localhost:8000/health

# Restart backend
cd backend
source venv/bin/activate
python -m uvicorn app.main_demo:app --reload --host 0.0.0.0 --port 8000
```

### Port Already in Use?
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

## 📚 Documentation

- [`README.md`](README.md) - Full project overview
- [`ARCHITECTURE.md`](ARCHITECTURE.md) - System architecture
- [`SETUP_GUIDE.md`](SETUP_GUIDE.md) - Complete setup instructions
- [`docs/PODMAN_SETUP.md`](docs/PODMAN_SETUP.md) - Podman deployment guide
- [`HACKATHON_GUIDE.md`](HACKATHON_GUIDE.md) - Day-by-day implementation plan

## 🎨 UI Preview

The frontend includes:
- **Dashboard**: Overview with key metrics and charts
- **Contracts**: List and manage contracts
- **Compliance**: Monitor SLA compliance
- **Risks**: View and assess risks
- **Alerts**: Active alerts and notifications
- **Analytics**: Detailed analytics and reports

## 🔐 Production Setup

For production with IBM Cloud:

1. **Get IBM Cloud credentials**:
   - Cloudant database
   - watsonx.ai API key
   - Watson Discovery credentials

2. **Update environment**:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your credentials
   ```

3. **Switch to production mode**:
   ```bash
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## 🐳 Container Deployment

### Using Podman
```bash
# Install podman-compose
pip3 install podman-compose

# Start all services
./start-podman.sh
```

### Using Docker
```bash
docker-compose up --build
```

## 💡 Tips

1. **API Documentation**: Visit http://localhost:8000/docs for interactive API testing
2. **Hot Reload**: Backend auto-reloads on code changes
3. **Demo Data**: All data is in-memory, resets on restart
4. **No Auth**: Demo mode has no authentication (add for production)

## 🎯 Hackathon Focus Areas

1. **Day 1-2**: Core agent implementation
2. **Day 3**: IBM Cloud integration
3. **Day 4**: UI/UX refinement
4. **Day 5**: Testing and demo preparation

See [`HACKATHON_GUIDE.md`](HACKATHON_GUIDE.md) for detailed timeline.

## 🆘 Need Help?

1. Check the logs in the terminal
2. Review the documentation files
3. Test endpoints with curl or Postman
4. Visit http://localhost:8000/docs for API reference

---

**Current Status**: Backend running ✓ | Frontend pending Node.js installation