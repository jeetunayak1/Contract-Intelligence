# AI Project Context - SOW Sentinel

## What This Project Does

**SOW Sentinel** is an AI-powered agentic system that prevents service companies from losing money through contract breaches, scope creep, and missed SLA deadlines. It automatically:

1. Parses Statement of Work (SOW) documents to extract obligations and penalties
2. Maps SOW requirements to execution tools (GitHub/Jira/Calendar)
3. Monitors compliance in real-time and detects risks
4. Sends proactive alerts before breaches occur
5. Takes automated actions (creates tasks, schedules meetings, sends notifications)

## Current Project State

### ✅ What's Working
- Backend API server running on http://localhost:8000
- Frontend React app running on http://localhost:3000
- Demo mode with comprehensive sample data
- All 3 core AI agents implemented
- Risk Report UI (the "wow" moment demo)
- Complete REST API with 8+ endpoints
- Python virtual environment set up
- Git repository created and pushed

### 🔄 In Progress
- IBM Cloud integration (watsonx.ai, Cloudant)
- Additional UI components (Dashboard, Scope Creep view)
- Real-time monitoring implementation

### ⏳ Not Yet Done
- Mapping Agent (GitHub/Jira integration)
- Production deployment to IBM Cloud
- Comprehensive testing suite
- Demo video creation

## Architecture Overview

### 4-Stage Agentic Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  1. INGESTION AGENT (The Reader)                            │
│     • Parses PDF/DOCX SOWs with watsonx.ai                 │
│     • Extracts obligations, SLAs, penalties                 │
│     • Detects vague clauses                                 │
│     • Risk scoring                                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. MAPPING AGENT (The Bridge) - TO BE IMPLEMENTED          │
│     • Links SOW obligations to GitHub/Jira                  │
│     • Creates tracking relationships                        │
│     • Syncs deadlines with calendars                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. MONITORING AGENT (The Watchman)                         │
│     • Compares deadlines vs. commit velocity               │
│     • Detects scope creep (work not in SOW)                │
│     • Calculates penalty exposure                           │
│     • Continuous compliance checking                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. EXECUTIVE AGENT (The Actor)                             │
│     • Creates Jira tasks automatically                      │
│     • Schedules calendar events                             │
│     • Sends Slack/email alerts                              │
│     • Generates status reports                              │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI (Python 3.13)
- IBM watsonx.ai (LLM for SOW parsing)
- IBM Watson Discovery (document intelligence)
- IBM Cloudant (NoSQL database)
- Celery + Redis (task queue)

**Frontend:**
- React 18 with TypeScript
- Material-UI (components)
- Recharts (data visualization)
- Vite (build tool)

**Infrastructure:**
- Podman/Docker (containers)
- IBM Cloud (hosting)

## Key Concepts

### 1. Statement of Work (SOW)
Documents that define service agreements with:
- Project scope and deliverables
- SLA commitments (response times, uptime)
- Financial penalties (Liquidated Damages)
- Deadlines and milestones
- Pricing and billing terms

### 2. Obligations
Specific requirements extracted from SOWs:
- **Deliverables**: Tangible outputs (e.g., "UAT Sign-off Document")
- **Milestones**: Project phases (e.g., "Phase 1: Database Migration")
- **SLA Metrics**: Performance targets (e.g., "99.9% uptime")
- **Recurring Tasks**: Ongoing requirements (e.g., "Monthly status reports")

### 3. Compliance Events
Monitoring results that track:
- Current progress vs. deadline
- Velocity trends (increasing/stable/declining)
- Penalty exposure calculations
- Risk severity levels

### 4. Scope Creep
Work performed that's not in the SOW:
- Unbilled hours and costs
- Out-of-scope features
- Additional services
- Potential revenue recovery opportunities

### 5. Alerts
Notifications based on severity:
- **Critical**: < 24 hours to penalty (immediate action)
- **High**: < 7 days, velocity declining (urgent attention)
- **Medium**: Scope creep detected (monitor)
- **Low**: Informational (upcoming milestone)

## Code Structure Explained

### Backend Structure
```
backend/app/
├── main_demo.py              # Demo FastAPI app (current)
├── main.py                   # Production app (needs IBM Cloud)
├── agents/                   # AI agents
│   ├── ingestion_agent.py    # Parses SOWs with watsonx.ai
│   ├── monitoring_agent.py   # Tracks compliance
│   └── executive_agent.py    # Takes automated actions
├── api/                      # REST API endpoints
│   └── sow.py                # SOW management endpoints
├── core/                     # Core functionality
│   ├── config.py             # Settings from .env
│   └── cloudant_db.py        # Cloudant connection
└── models/                   # Data models
    └── sow_models.py         # SOW document models
```

### Frontend Structure
```
frontend/src/
├── App.tsx                   # Main React app
├── main.tsx                  # Entry point
├── pages/                    # Page components
│   ├── Dashboard.tsx         # Main dashboard
│   └── RiskReport.tsx        # Risk report (demo starter!)
├── components/               # Reusable components (to be added)
├── services/                 # API clients (to be added)
└── types/                    # TypeScript types (to be added)
```

## Data Flow

### 1. SOW Upload Flow
```
User uploads PDF → 
  Backend receives file → 
    Ingestion Agent parses with watsonx.ai → 
      Extract obligations, SLAs, penalties → 
        Save to Cloudant → 
          Return SOW ID and risk assessment
```

### 2. Compliance Monitoring Flow
```
Scheduled job runs (every 4 hours) → 
  Monitoring Agent checks all obligations → 
    Compare deadline vs. progress → 
      Calculate velocity trend → 
        Predict completion date → 
          If at risk: Create compliance event → 
            Executive Agent handles event → 
              Create alerts, tasks, notifications
```

### 3. Risk Detection Flow
```
Compliance event created → 
  Determine severity (critical/high/medium/low) → 
    Calculate penalty exposure → 
      Generate recommended actions → 
        Executive Agent takes actions:
          - Create Jira task
          - Schedule meeting
          - Send Slack alert
          - Update dashboard
```

### 4. Scope Creep Detection Flow
```
Monitoring Agent analyzes GitHub/Jira → 
  Compare work done vs. SOW obligations → 
    Identify unmapped work → 
      Calculate hours and cost → 
        Create scope creep document → 
          Alert PM with recovery recommendation
```

## Database Schema (Cloudant)

### SOW Document
```json
{
  "_id": "SOW-2024-ACME-001",
  "type": "sow",
  "sow_number": "2024-ACME-001",
  "client_name": "Acme Corporation",
  "project_name": "Enterprise Platform Migration",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "total_value": 500000,
  "status": "active",
  "obligations": [...],
  "sla_terms": [...],
  "vague_clauses": [...],
  "financial_summary": {
    "total_penalties_at_risk": 9000,
    "penalties_avoided": 2000,
    "scope_creep_value": 15000
  }
}
```

### Obligation
```json
{
  "id": "OBL-001",
  "type": "deliverable",
  "description": "Phase 1: Database Migration",
  "deadline": "2024-03-31",
  "penalty_amount": 5000,
  "penalty_frequency": "per_day",
  "risk_level": "critical",
  "status": "in_progress",
  "progress_percentage": 75,
  "mapped_to": {
    "github_project": "acme-migration",
    "jira_epic": "ACME-123"
  }
}
```

### Compliance Event
```json
{
  "_id": "EVENT-20240502-001",
  "type": "compliance_event",
  "sow_id": "SOW-2024-ACME-001",
  "obligation_id": "OBL-002",
  "event_type": "deadline_warning",
  "severity": "critical",
  "days_remaining": 2,
  "current_progress": 60,
  "velocity_trend": "declining",
  "penalty_exposure": 1000
}
```

## API Endpoints Reference

### SOW Management
- `POST /api/v1/sow/upload` - Upload and parse SOW
- `GET /api/v1/sow/list` - List all SOWs
- `GET /api/v1/sow/{id}` - Get SOW details

### Risk & Compliance
- `GET /api/v1/sow/{id}/risk-report` - **THE DEMO STARTER!**
- `GET /api/v1/sow/{id}/penalty-countdown` - Real-time countdown
- `GET /api/v1/sow/{id}/margin-leakage` - Scope creep detection

### Dashboard
- `GET /api/v1/sow/dashboard/summary` - Dashboard summary data

## Development Commands

### Backend
```bash
# Start demo server (no IBM Cloud needed)
cd backend
source venv/bin/activate
python -m uvicorn app.main_demo:app --reload --host 0.0.0.0 --port 8000

# Install dependencies
pip install -r requirements-minimal.txt  # For demo
pip install -r requirements.txt          # For production
```

### Frontend
```bash
# Install and start
cd frontend
npm install
npm run dev

# Build for production
npm run build
```

## Next Development Steps

### Phase 1: Core Functionality (70% Complete)
- ✅ Project structure
- ✅ Backend API with 3 agents
- ✅ Demo mode
- ✅ Risk Report UI
- ⏳ Dashboard UI
- ⏳ Additional UI components

### Phase 2: IBM Cloud Integration
- ⏳ Connect to Cloudant
- ⏳ Integrate watsonx.ai API
- ⏳ Set up Watson Discovery
- ⏳ Configure Cloud Object Storage

### Phase 3: Integrations
- ⏳ Implement Mapping Agent
- ⏳ GitHub API integration
- ⏳ Jira API integration
- ⏳ Google Calendar API
- ⏳ Slack notifications

### Phase 4: Testing & Deployment
- ⏳ Unit tests
- ⏳ Integration tests
- ⏳ Deploy to IBM Cloud
- ⏳ Demo preparation

## Demo Strategy

### Opening Scene: Risk Report
**URL**: http://localhost:3000/risk-report

**The "Wow" Moment**:
```
🚨 CRITICAL ALERT
"If you don't deliver the UAT sign-off by Friday, you lose $1,000 per day"
⏰ 48 hours remaining
📊 Current progress: 60%
🔴 3 blockers identified
💡 4 recommended actions
```

**Impact**: Immediate understanding of financial risk and urgency

### Key Features to Demonstrate:
1. **Penalty Countdown Timer** - Live countdown with pulsing animation
2. **Financial Summary** - $9K penalty exposure, $15K scope creep
3. **Automated Actions** - Jira tasks, calendar events, Slack alerts
4. **Scope Creep Detection** - Unbilled work identification

## Troubleshooting Guide

### Backend Won't Start
- Check if port 8000 is in use: `lsof -ti:8000`
- Verify venv is activated: `which python`
- Review error logs in terminal

### Frontend Won't Start
- Check if port 3000 is in use: `lsof -ti:3000`
- Verify Node.js installed: `node --version`
- Clear npm cache: `npm cache clean --force`

### API Not Responding
- Check backend is running: `curl http://localhost:8000/health`
- Verify CORS settings in main_demo.py
- Check browser console for errors

## Resources

### Documentation
- Main README: `README.md`
- Architecture: `ARCHITECTURE.md`
- API Docs: http://localhost:8000/docs

### Code
- Backend: `backend/app/`
- Frontend: `frontend/src/`

### IBM Cloud
- watsonx.ai: https://www.ibm.com/watsonx
- Watson Discovery: https://cloud.ibm.com/docs/discovery-data
- Cloudant: https://cloud.ibm.com/docs/Cloudant

## Contact & Support
- GitHub: https://github.com/jeetunayak1/Contract-Intelligence
- Developer: Jeetendra Nayak

---

**Built with ❤️ for the IBM Hackathon - Preventing revenue leakage and contract breaches for service companies**