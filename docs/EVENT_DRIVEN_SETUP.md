# Event-Driven Autonomous Compliance Monitoring - Setup Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements-minimal.txt
```

### 2. Configure Environment Variables

Create or update `backend/.env`:

```bash
# Google Cloud & Gemini AI
GOOGLE_API_KEY=your_gemini_api_key_here
GCP_PROJECT_ID=your_gcp_project_id
FIRESTORE_DB_NAME=(default)

# GitHub Integration
GITHUB_ACCESS_TOKEN=ghp_your_personal_access_token
GITHUB_REPO_NAME=owner/repository-name
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
DEFAULT_CONTRACT_ID=contract_default

# Application
DEBUG=True
LOG_LEVEL=INFO
```

### 3. Start Backend Server

```bash
cd backend
uvicorn app.main_demo:app --reload --port 8000
```

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📋 GitHub Setup

### Step 1: Create Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `admin:repo_hook` (Full control of repository hooks)
4. Copy the token and add to `.env` as `GITHUB_ACCESS_TOKEN`

### Step 2: Setup Webhook

#### Option A: Using ngrok (for local development)

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Start ngrok tunnel
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

#### Option B: Using GitHub Service (programmatic)

```python
from app.services.github_service import get_github_service

github = get_github_service()
github.setup_webhook(
    webhook_url="https://your-domain.com/api/v1/events/github/webhook",
    secret="your_webhook_secret",
    events=['issues', 'issue_comment']
)
```

https://shallow-siesta-willow.ngrok-free.dev

##### https://shallow-siesta-willow.ngrok-free.dev/api/v1/events/github/webhook

#### Option C: Manual Setup via GitHub UI

1. Go to your repository → Settings → Webhooks → Add webhook
2. Payload URL: `https://your-domain.com/api/v1/events/github/webhook`
3. Content type: `application/json`
4. Secret: Your webhook secret from `.env`
5. Events: Select "Issues" and "Issue comments"
6. Active: ✓
7. Click "Add webhook"

### Step 3: Test Webhook

Create a test issue in your GitHub repository:

```
Title: [P1] Test Payment Gateway Outage
Body: Testing autonomous compliance analysis
Labels: incident, p1
```

The system should:
1. Receive webhook
2. Create incident in Firestore
3. Trigger ComplianceCrew
4. Stream reasoning logs
5. Update War Room dashboard

## 🔥 API Endpoints

### GitHub Webhook
```
POST /api/v1/events/github/webhook
Headers:
  X-GitHub-Event: issues
  X-Hub-Signature-256: sha256=...
```

### Live Incidents Feed
```
GET /api/v1/events/incidents/live?limit=50&status=OPEN
```

### Reasoning Stream
```
GET /api/v1/events/reasoning/{incident_id}
```

### Crew Status
```
GET /api/v1/events/crew/{crew_execution_id}
```

### Manual Analysis Trigger
```
POST /api/v1/events/incidents/{incident_id}/analyze?contract_id=xxx&monthly_fee=100000
```

## 📊 Firestore Collections

The system creates these collections automatically:

- `contracts/` - Extracted contract SLA data
- `incidents/` - Live incident feed
- `reasoning_logs/` - AI reasoning stream
- `crew_events/` - CrewAI execution events
- `financial_snapshots/` - Point-in-time exposure tracking
- `alerts/` - System alerts

## 🎯 Demo Scenario

### 1. Upload Contract

```bash
curl -X POST http://localhost:8000/api/v1/contracts/upload \
  -F "file=@sample_contract.pdf"
```

Response:
```json
{
  "success": true,
  "contract_id": "contract_abc123",
  "data": {
    "incident_slas": [...],
    "service_credits": [...]
  }
}
```

### 2. Create GitHub Issue

Create issue with title: `[P1] Payment Gateway Complete Outage`

### 3. Watch Autonomous Analysis

1. **Webhook fires** → Incident created
2. **ComplianceCrew activates** → Analysis starts
3. **Reasoning streams** → Live logs appear
4. **SLA evaluated** → Breach detected
5. **Liability checked** → Exclusion applied
6. **Financial calculated** → Exposure updated
7. **Dashboard updates** → Real-time KPIs

### 4. View Results

- War Room: http://localhost:5173/warroom
- API: http://localhost:8000/api/v1/events/incidents/live

## 🔧 Troubleshooting

### Webhook Not Firing

1. Check ngrok is running: `ngrok http 8000`
2. Verify webhook URL in GitHub settings
3. Check webhook deliveries in GitHub (Settings → Webhooks → Recent Deliveries)
4. Look for errors in backend logs

### Firestore Connection Issues

```bash
# Check if GOOGLE_APPLICATION_CREDENTIALS is set
echo $GOOGLE_APPLICATION_CREDENTIALS

# Verify service account has Firestore permissions
# The system will fall back to in-memory storage if Firestore unavailable
```

### CrewAI Not Running

```bash
# Verify CrewAI installed
pip list | grep crewai

# Check Gemini API key
python -c "import os; print(os.getenv('GOOGLE_API_KEY'))"
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements-minimal.txt --force-reinstall
```

## 📱 Frontend Integration

### Add Firestore Realtime Listeners

```typescript
import { collection, onSnapshot, query, where } from 'firebase/firestore';

// Listen to incidents
const unsubscribe = onSnapshot(
  collection(db, 'incidents'),
  (snapshot) => {
    const incidents = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));
    setIncidents(incidents);
  }
);

// Listen to reasoning logs
const unsubscribe = onSnapshot(
  query(
    collection(db, 'reasoning_logs'),
    where('incident_id', '==', incidentId)
  ),
  (snapshot) => {
    const logs = snapshot.docs.map(doc => doc.data());
    setReasoningLogs(logs);
  }
);
```

## 🎬 Production Deployment

### 1. Deploy Backend

```bash
# Using Docker
docker build -t contract-intelligence .
docker run -p 8000:8000 --env-file .env contract-intelligence

# Or using Cloud Run
gcloud run deploy contract-intelligence \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 2. Update GitHub Webhook

Replace ngrok URL with production URL:
```
https://your-app.run.app/api/v1/events/github/webhook
```

### 3. Configure Firestore

1. Enable Firestore in GCP Console
2. Create database in Native mode
3. Set up security rules
4. Add service account credentials

### 4. Monitor Logs

```bash
# View backend logs
tail -f backend/logs/app.log

# View Firestore operations
gcloud logging read "resource.type=cloud_firestore"
```

## 🔐 Security Checklist

- [ ] Rotate GitHub personal access token regularly
- [ ] Use strong webhook secret (32+ characters)
- [ ] Enable HTTPS for webhook endpoint
- [ ] Verify webhook signatures in production
- [ ] Set Firestore security rules
- [ ] Limit API rate limits
- [ ] Enable authentication for sensitive endpoints
- [ ] Use environment variables for all secrets
- [ ] Never commit `.env` file to git

## 📈 Monitoring

### Key Metrics to Track

1. **Webhook Success Rate**: % of webhooks processed successfully
2. **Analysis Latency**: Time from incident creation to analysis completion
3. **Firestore Operations**: Read/write counts and latency
4. **Crew Execution Time**: Average time for compliance analysis
5. **Error Rate**: Failed analyses or webhook processing errors

### Logging

All components log to stdout with structured JSON:

```json
{
  "timestamp": "2026-05-14T10:30:00Z",
  "level": "INFO",
  "message": "Incident created",
  "incident_id": "INC-431",
  "priority": "P1",
  "service": "payment-gateway"
}
```

## 🎓 Architecture Overview

```
GitHub Issue Created
        ↓
GitHub Webhook (HTTPS POST)
        ↓
FastAPI /api/v1/events/github/webhook
        ↓
GitHubWebhookHandler.handle_issues_event()
        ↓
IncidentService.create_incident_from_github()
        ↓
FirebaseEventService.create_incident()
        ↓
[IF P1/P2/SEV1] → BackgroundTask
        ↓
ComplianceCrew.analyze_incident()
        ↓
├─ Load contract from Firestore
├─ Run ComplianceAgent.analyze_compliance()
├─ Stream reasoning logs to Firestore
├─ Calculate financial exposure
├─ Check liability exclusions
├─ Create financial snapshot
└─ Update incident status
        ↓
Firestore (realtime updates)
        ↓
Frontend (snapshot listeners)
        ↓
War Room Dashboard (live updates)
```

## 🚦 Status Indicators

- 🟢 **GREEN**: All systems operational
- 🟡 **YELLOW**: Degraded performance (using in-memory fallback)
- 🔴 **RED**: Critical failure (webhook not reachable)

## 📞 Support

For issues or questions:
1. Check logs: `backend/logs/app.log`
2. Review Firestore console
3. Test webhook deliveries in GitHub
4. Verify environment variables
5. Check API health: `http://localhost:8000/health`

---

**Made with Bob** - Autonomous Contract Risk Intelligence Platform