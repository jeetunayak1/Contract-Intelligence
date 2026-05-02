# SOW Sentinel - Agentic Compliance Framework

## 🎯 Project Vision

**SOW Sentinel** is an AI-powered agentic system that prevents service companies from losing money through contract breaches, scope creep, and missed SLA deadlines. It reads complex Statements of Work (SOWs), extracts obligations, and connects to execution tools (GitHub/Jira/Calendar) to ensure compliance and protect margins.

---

## 💡 The Core Problem

Service-based companies face critical challenges:

1. **Revenue Leakage**: Teams work on out-of-scope tasks without billing
2. **Financial Penalties**: Missing SLA deadlines triggers Liquidated Damages (LDs)
3. **Contract Breaches**: Vague SOW clauses lead to disputes and lost revenue
4. **Margin Erosion**: Scope creep eats into profitability
5. **Manual Tracking**: No automated way to monitor SOW compliance

**Real Impact**: A single missed milestone can cost $1,000-$10,000 per day in penalties.

---

## 🏗️ System Architecture: 4-Stage Agentic Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     SOW Sentinel System                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Stage 1: INGESTION AGENT (The Reader)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Input: PDF/DOCX SOW                                      │  │
│  │  Action: Extract Obligations using watsonx.ai            │  │
│  │  Output: Structured JSON with:                           │  │
│  │    - Deliverables & Milestones                           │  │
│  │    - SLA Metrics (response/resolution times)             │  │
│  │    - Financial Penalties (LDs)                           │  │
│  │    - Dates & Deadlines                                   │  │
│  │  Risk Scoring: Tag as "Vague", "High Financial Risk"     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Stage 2: MAPPING AGENT (The Bridge)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Input: Extracted Obligations + GitHub/Jira APIs         │  │
│  │  Action: Map SOW requirements to execution tools         │  │
│  │  Examples:                                               │  │
│  │    - "SOW Milestone 1" → "GitHub Project Board v1.0"    │  │
│  │    - "Security Audit" → "Jira Epic SECURITY-123"        │  │
│  │    - "Monthly Report" → "Recurring Calendar Event"      │  │
│  │  Output: Linked obligations with tracking IDs           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Stage 3: MONITORING AGENT (The Watchman)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Continuous Loop (Every 4 hours):                        │  │
│  │  1. Compare SOW Deadline vs Git Commit Velocity         │  │
│  │  2. Check Jira progress vs SOW milestones               │  │
│  │  3. Scan Slack/Email for undocumented change requests   │  │
│  │  4. Calculate "Days to Penalty" for each obligation     │  │
│  │  5. Detect scope creep (work not in SOW)                │  │
│  │  Output: Real-time compliance status & alerts           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Stage 4: EXECUTIVE AGENT (The Actor)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Automated Actions:                                       │  │
│  │  1. Create Jira tasks for upcoming SOW deliverables     │  │
│  │  2. Schedule Google Calendar "Pre-Delivery Reviews"     │  │
│  │  3. Send Slack nudges for SLA deadline warnings         │  │
│  │  4. Generate "Definition of Done" checklists            │  │
│  │  5. Auto-format status reports per SOW requirements     │  │
│  │  6. Block invoice release if milestones not met         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Key Features

### A. Loss Prevention Dashboard

**Purpose**: Real-time visibility into financial risks

**Components**:

1. **Penalty Countdown Timer**
   - Live countdown to next LD trigger
   - Shows: "48 hours until $5,000 penalty"
   - Color-coded: Green (safe), Yellow (warning), Red (critical)

2. **Margin Leakage Alert**
   - Detects out-of-scope work
   - Shows: "Team spent 15 hours on Feature X (not in SOW)"
   - Calculates lost revenue: "Unbilled work = $3,750"

3. **SLA Heatmap**
   - Visual grid of all SLA metrics
   - Green: Compliant, Yellow: At risk, Red: Breached
   - Metrics: Response time, Resolution time, Uptime

4. **Financial Risk Score**
   - Overall project health: 0-100
   - Factors: Deadline proximity, velocity, scope creep
   - Predictive: "85% chance of penalty in 2 weeks"

### B. Automation & Execution

1. **Smart Calendar Invites**
   - Auto-schedule "Pre-Delivery Review" 48h before milestone
   - Include: Checklist, stakeholders, SOW reference

2. **Auto-Action Items**
   - Generate "Definition of Done" from SOW technical requirements
   - Create GitHub PR templates with compliance checks

3. **Status Report Generator**
   - One-click report generation
   - Pulls: Git commits, Jira progress, test results
   - Formats per SOW's required structure

4. **Scope Creep Detector**
   - Flags work not mapped to SOW
   - Suggests: "Create Change Request for Feature Y"

---

## 📊 Data Models

### SOW Document (Cloudant)
```json
{
  "_id": "SOW-2024-ACME-001",
  "type": "sow",
  "client_name": "Acme Corp",
  "project_name": "Enterprise Platform Migration",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "total_value": 500000,
  "obligations": [
    {
      "id": "OBL-001",
      "type": "deliverable",
      "description": "Phase 1: Database Migration",
      "deadline": "2024-03-31",
      "penalty_amount": 5000,
      "penalty_frequency": "per_day",
      "risk_level": "high",
      "status": "in_progress",
      "mapped_to": {
        "github_project": "acme-migration",
        "jira_epic": "ACME-123"
      }
    }
  ],
  "sla_terms": [
    {
      "id": "SLA-001",
      "metric": "incident_response_time",
      "target": 4,
      "unit": "hours",
      "penalty_amount": 1000,
      "measurement_period": "monthly"
    }
  ],
  "vague_clauses": [
    {
      "clause": "Reasonable efforts for performance optimization",
      "risk": "Undefined success criteria",
      "recommendation": "Request specific metrics"
    }
  ]
}
```

### Compliance Event (Cloudant)
```json
{
  "_id": "EVENT-2024-05-02-001",
  "type": "compliance_event",
  "sow_id": "SOW-2024-ACME-001",
  "obligation_id": "OBL-001",
  "event_type": "deadline_warning",
  "severity": "high",
  "days_remaining": 7,
  "current_progress": 65,
  "required_progress": 100,
  "velocity_trend": "declining",
  "predicted_completion": "2024-05-15",
  "penalty_exposure": 25000,
  "actions_taken": [
    "Created Jira task URGENT-456",
    "Scheduled team sync for tomorrow",
    "Sent Slack alert to PM"
  ],
  "timestamp": "2024-05-02T10:30:00Z"
}
```

### Scope Creep Detection
```json
{
  "_id": "SCOPE-2024-05-02-001",
  "type": "scope_creep",
  "sow_id": "SOW-2024-ACME-001",
  "detected_work": {
    "description": "Advanced Analytics Dashboard",
    "hours_spent": 40,
    "cost": 10000,
    "github_commits": ["abc123", "def456"],
    "jira_tickets": ["ACME-789"]
  },
  "sow_match": null,
  "recommendation": "Create Change Request CR-2024-05",
  "potential_revenue": 15000,
  "status": "pending_approval"
}
```

---

## 🔌 Integration Architecture

### GitHub Integration
```python
# Monitor commit velocity vs SOW deadlines
class GitHubMonitor:
    def check_milestone_progress(self, sow_obligation):
        # Get commits for mapped project
        commits = github_api.get_commits(
            repo=obligation.mapped_to.github_project,
            since=obligation.start_date
        )
        
        # Calculate velocity
        velocity = len(commits) / days_elapsed
        required_velocity = remaining_work / days_remaining
        
        if velocity < required_velocity * 0.8:
            return {
                "status": "at_risk",
                "action": "escalate_to_pm"
            }
```

### Jira Integration
```python
# Auto-create tasks from SOW obligations
class JiraExecutor:
    def create_compliance_tasks(self, sow_obligation):
        # Create epic for major deliverable
        epic = jira_api.create_epic(
            title=f"SOW: {obligation.description}",
            due_date=obligation.deadline,
            custom_fields={
                "penalty_amount": obligation.penalty_amount,
                "sow_reference": obligation.id
            }
        )
        
        # Create pre-delivery review task
        review_date = obligation.deadline - timedelta(days=2)
        jira_api.create_task(
            title=f"Pre-Delivery Review: {obligation.description}",
            due_date=review_date,
            parent=epic.id
        )
```

### Google Calendar Integration
```python
# Auto-schedule compliance checkpoints
class CalendarExecutor:
    def schedule_compliance_events(self, sow_obligation):
        # Pre-delivery review
        calendar_api.create_event(
            title=f"SOW Compliance Review: {obligation.description}",
            start=obligation.deadline - timedelta(days=2),
            duration=60,
            attendees=["pm@company.com", "tech-lead@company.com"],
            description=f"Review checklist:\n{obligation.checklist}"
        )
        
        # Weekly progress sync
        calendar_api.create_recurring_event(
            title=f"SOW Progress: {obligation.description}",
            frequency="weekly",
            duration=30
        )
```

---

## 🚨 Alert System

### Alert Types & Actions

1. **Critical (Red) - Immediate Action Required**
   - Trigger: < 24 hours to penalty
   - Action: Slack DM to PM + CEO, Create P0 Jira ticket
   - Example: "URGENT: UAT sign-off due in 18 hours. $5,000/day penalty starts tomorrow."

2. **High (Orange) - Urgent Attention**
   - Trigger: < 7 days to deadline, velocity declining
   - Action: Slack channel alert, Schedule emergency meeting
   - Example: "WARNING: Phase 1 delivery at risk. Current velocity: 60% of required."

3. **Medium (Yellow) - Monitor Closely**
   - Trigger: Scope creep detected
   - Action: Email to PM, Create change request draft
   - Example: "SCOPE ALERT: 40 hours spent on out-of-scope Feature X. Potential revenue: $15k."

4. **Low (Blue) - Informational**
   - Trigger: Upcoming milestone in 30 days
   - Action: Calendar invite for planning session
   - Example: "INFO: Phase 2 kickoff in 30 days. Schedule requirements review."

---

## 🎬 Demo Flow (The "Wow" Moment)

### Opening Scene: Risk Report Screen

**Visual**: Dashboard with flashing red alert

**AI Voice**: "If you don't deliver the UAT sign-off by Friday, you lose $5,000 per day."

**Screen Shows**:
- PDF SOW with highlighted clause
- Countdown timer: "48:23:15 until penalty"
- Current status: "UAT document at 75% completion"
- Action items: "3 critical tasks blocking sign-off"

**Impact**: Immediate understanding of financial risk

### Scene 2: Scope Creep Detection

**Visual**: Margin leakage alert

**Screen Shows**:
- "Team spent 40 hours on Advanced Analytics Dashboard"
- "This feature is NOT in the SOW"
- "Unbilled work value: $10,000"
- "Recommended action: Create Change Request CR-2024-05"

**Impact**: Shows how system protects margins

### Scene 3: Auto-Execution

**Visual**: Executive Agent in action

**Screen Shows**:
- Jira task auto-created: "Complete UAT Documentation"
- Calendar invite sent: "Pre-Delivery Review - Thursday 2 PM"
- Slack message: "Reminder: UAT sign-off due Friday"
- GitHub PR checklist: "Security audit required per SOW Section 8.4"

**Impact**: Demonstrates automation value

---

## 🔮 Future Roadmap (Agentic Evolution)

### Phase 1: Self-Healing Invoices
- System blocks invoice release until all SOW milestones are "Green"
- Auto-generates invoice with SOW milestone references
- Flags any unbilled scope creep work

### Phase 2: Predictive Resourcing
- AI predicts breach 2 weeks in advance
- Suggests: "Reassign Developer X to speed up Module Y"
- Calculates: "Adding 1 developer reduces penalty risk by 80%"

### Phase 3: Agentic Negotiation
- AI reviews new draft SOWs
- Warns: "You lost 15% margin on last project with 'Uncapped Support' clause"
- Suggests: "Renegotiate to 'Max 40 hours/month support'"
- Provides: Historical data on similar clauses

### Phase 4: Contract Intelligence
- AI learns from past SOWs
- Identifies: "Vague clauses that led to disputes"
- Recommends: "Standard clauses that protect margins"
- Generates: "Risk-adjusted pricing for new SOWs"

---

## 🛠️ Technology Stack

### Backend (Python)
- **Framework**: FastAPI
- **Agent Framework**: LangChain or CrewAI
- **LLM**: IBM watsonx.ai (granite-13b-chat-v2)
- **Document Processing**: Watson Discovery
- **Database**: IBM Cloudant (NoSQL)
- **Task Queue**: Celery + Redis
- **APIs**: GitHub, Jira, Google Calendar, Slack

### Frontend (React)
- **Framework**: React 18 + TypeScript
- **UI**: Material-UI
- **Charts**: Recharts
- **State**: Redux Toolkit
- **Real-time**: WebSockets

### IBM Cloud Services
- watsonx.ai (SOW parsing, risk analysis)
- Watson Discovery (document intelligence)
- Cloudant (data storage)
- Cloud Functions (scheduled monitoring)
- Event Streams (real-time events)

---

## 📈 Success Metrics

### Financial Impact
- **Penalties Avoided**: Track $ saved from prevented breaches
- **Revenue Recovered**: Scope creep converted to change requests
- **Margin Protected**: % improvement in project profitability

### Operational Impact
- **Early Warning Time**: Average days before deadline when alert triggered
- **Compliance Rate**: % of SOW obligations met on time
- **Automation Rate**: % of manual tasks eliminated

### Business Value
- **ROI**: (Penalties Avoided + Revenue Recovered) / System Cost
- **Time Saved**: Hours saved on manual SOW tracking
- **Risk Reduction**: % decrease in contract disputes

---

## 🎯 Competitive Advantage

**Why SOW Sentinel Wins**:

1. **Service Provider Perspective**: Built for companies delivering services, not buying them
2. **Financial Focus**: Directly prevents revenue loss and penalties
3. **Agentic Automation**: Not just monitoring - takes action
4. **Execution Integration**: Connects SOW to actual work (GitHub/Jira)
5. **Predictive Intelligence**: Warns before problems occur

**The Pitch**: "We save service companies from losing money on contracts they've already won."

---

## 📝 Sample Action Items (AI-Generated)

### Financial Tasks
```
CRITICAL: Penalty Clause 5.2 active
- Deliverable: UAT Sign-off Document
- Deadline: May 15th, 2024 (48 hours)
- Penalty: $1,000/day after deadline
- Action: Schedule emergency review meeting
- Blocker: Security audit pending
```

### Operational Tasks
```
RECURRING: Bi-Weekly Progress Call
- SOW Reference: Section 3.1
- Frequency: Every 2 weeks
- Attendees: PM, Tech Lead, Client Stakeholder
- Agenda: Milestone progress, risk review
- Calendar: Auto-scheduled
```

### Technical Tasks
```
REQUIREMENT: Data Encryption at Rest
- SOW Reference: Security Clause 8.4
- GitHub Issue: Created as SECURITY-789
- Definition of Done:
  ✓ Implement AES-256 encryption
  ✓ Document key management
  ✓ Pass security audit
  ✓ Update deployment guide
```

---

## 🚀 Getting Started

### For Developers
```bash
# Clone repository
git clone https://github.com/your-org/sow-sentinel.git

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure IBM Cloud credentials
cp .env.example .env
# Edit .env with your watsonx.ai API keys

# Start backend
python -m uvicorn app.main:app --reload

# Frontend setup
cd frontend
npm install
npm run dev
```

### For Business Users
1. Upload your SOW (PDF/DOCX)
2. Review extracted obligations
3. Connect GitHub/Jira/Calendar
4. Monitor the Loss Prevention Dashboard
5. Let the agents handle compliance

---

## 📞 Support & Documentation

- **Architecture**: This document
- **API Docs**: http://localhost:8000/docs
- **User Guide**: docs/USER_GUIDE.md
- **Integration Guide**: docs/INTEGRATIONS.md
- **Demo Video**: [Link to 3-minute demo]

---

**Built with ❤️ for service companies who want to protect their margins and deliver on time.**