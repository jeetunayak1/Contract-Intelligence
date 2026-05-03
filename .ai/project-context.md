# AI Project Context - SOW Sentinel

## What This Project Does

**SOW Sentinel** is an AI-powered governed contract-to-execution system for service organizations. It helps teams prevent revenue leakage, avoid SLA penalties, reduce contract ambiguity, and operationalize contract obligations safely.

The product centers on this workflow:

1. Upload a new Statement of Work
2. Parse obligations, SLA terms, vague clauses, and financial signals
3. Generate alerts and action items through agentic analysis
4. Persist a review package for later inspection
5. Let a human accept, reject, or clear the review decision
6. Execute only approved actions into operational systems such as GitHub and meeting workflows

This is not just a document parser and not just a dashboard. It is a **governed workflow system**.

---

## Current Project State

### ✅ What's Working
- backend API server and demo flow are active
- frontend React app contains the SOW management workflow
- upload/list/detail/timeline/dashboard SOW APIs exist
- persisted review package model is implemented
- saved SOW review and detail inspection is supported
- action items and alerts surface numeric risk and SLA context
- review decisions support:
  - approved
  - rejected
  - clear
- approved action execution path exists
- per-SOW integration modeling exists for GitHub, Slack, and Outlook-oriented routing
- architecture and product docs are being refreshed to match the latest workflow

### 🔄 In Progress
- backend hardening for stage-aware execution behavior
- frontend stage-aware UX polish and verification
- reducing remaining demo logic in monitoring and execution flows
- documentation alignment across pitch, architecture, setup, and AI context
- full end-to-end validation of decision and execution states

### ⏳ Not Yet Done
- full live watsonx inference in the ingestion path
- continuous monitoring loop for revenue leakage over downstream work
- fully production-grade execution integrations
- comprehensive automated test coverage
- production deployment hardening

---

## Architecture Overview

### Core Product Flow

```text
Upload SOW
  -> Ingestion Agent parses document
  -> Monitoring Agent derives compliance and financial risk findings
  -> Executive Agent creates alerts and action items
  -> Persist review package in Cloudant
  -> User reviews saved package later
  -> User accepts / rejects / clears
  -> Approved actions execute through configured downstream systems
```

### Stage-Aware Flow

```text
Pre-Acceptance
  -> validate SLA and contractual delivery feasibility
  -> create review tasks
  -> schedule review meetings

Post-Approval
  -> create delivery-governance tasks
  -> coordinate execution work
  -> preserve traceability to SLA and SOW source
```

This separation is intentional so the system does not create delivery work too early.

---

## Agent Roles

### 1. Ingestion Agent
- parses uploaded SOW files
- extracts:
  - obligations
  - SLA terms
  - vague clauses
  - financial indicators
- produces normalized SOW structure

### 2. Monitoring Agent
- evaluates extracted obligations
- estimates risk and penalty exposure
- detects possible scope creep and leakage signals
- is expected to evolve into a more continuous monitoring role

### 3. Executive Agent
- turns findings into alerts
- proposes recommended actions
- generates human-reviewable operational work

### 4. Integration / Execution Layer
- uses SOW-scoped operational routing
- maps approved action items to execution systems
- preserves traceability from SOW to downstream work

---

## Technology Stack

### Backend
- FastAPI
- Python 3.x
- IBM Cloudant
- watsonx.ai configuration present
- Pydantic / pydantic-settings
- `python-multipart` for uploads

### Frontend
- React 18
- TypeScript
- Material UI
- Vite
- react-router-dom
- react-toastify

### Infrastructure / Docs
- local demo stack via backend and frontend dev servers
- IBM Cloud setup documentation
- Docker / Podman scripts for alternative startup models

---

## Key Concepts

### 1. Statement of Work (SOW)
A services contract containing:
- scope and deliverables
- milestones and obligations
- SLA commitments
- penalties / liquidated damages
- timelines and dependencies
- financial and delivery expectations

### 2. Review Package
A persisted SOW analysis bundle containing:
- extracted obligations
- SLA terms
- vague clauses
- risk assessment
- alerts
- action items
- scope creep findings
- timeline events
- approval history
- integration execution status

### 3. Human-in-the-Loop Governance
The system is intentionally controlled:
- agents recommend
- humans decide
- only approved work executes

### 4. SOW-Scoped Operations
Each SOW can carry its own operational routing for:
- GitHub review or delivery destinations
- labels and issue mapping
- Slack alert routing
- Outlook-style calendar and stakeholder targeting

### 5. Review Decisions
The current review model supports:
- **approved**
- **rejected**
- **clear**

This is important because the product must support operational reconsideration, not just one-way approval.

---

## Code Structure Explained

### Backend Structure
```text
backend/app/
├── main_demo.py                 # Demo FastAPI app
├── main.py                      # Production app entry
├── agents/
│   ├── ingestion_agent.py       # SOW parsing and extraction
│   ├── monitoring_agent.py      # Compliance / risk logic
│   └── executive_agent.py       # Alerts and recommendations
├── api/
│   ├── sow.py                   # Upload/review/approval/execution APIs
│   └── integrations.py          # Per-SOW integration setup
├── core/
│   ├── config.py                # Environment-backed settings
│   └── cloudant_db.py           # Cloudant access layer
└── models/
    ├── sow_models.py            # SOW data helpers
    └── integration_config.py    # SOW integration models
```

### Frontend Structure
```text
frontend/src/
├── App.tsx                      # Main app routing and navigation
├── main.tsx                     # React entry point
├── pages/
│   ├── Dashboard.tsx            # Summary dashboard
│   ├── RiskReport.tsx           # Risk storytelling page
│   ├── IntegrationConfig.tsx    # SOW-scoped integration setup
│   ├── Settings.tsx             # Shared/global credentials
│   └── SOWManagement.tsx        # Upload/review/decide/execute flow
├── components/                  # Reusable UI components
├── services/                    # Future API service layer
├── store/                       # Future client-side state layer
├── types/                       # Future shared TS types
└── utils/                       # Utility functions
```

---

## Data Flow

### 1. Upload and Parse Flow
```text
User uploads SOW
  -> POST /api/v1/sow/upload
  -> temp file created
  -> IngestionAgent parses content
  -> risk summary generated
  -> alerts and action items created
  -> document saved to Cloudant
```

### 2. Review Retrieval Flow
```text
User opens saved SOW
  -> GET /api/v1/sow/{sow_id}
  -> persisted review package returned
  -> frontend shows alerts, actions, risk summary, and timeline
```

### 3. Review Decision Flow
```text
User chooses approved / rejected / clear
  -> POST /api/v1/sow/{sow_id}/approve
  -> review state updated
  -> approval history updated
  -> timeline updated
```

### 4. Execution Flow
```text
Approved actions
  -> POST /api/v1/sow/{sow_id}/execute
  -> workflow stage considered
  -> SOW-scoped integration config consulted
  -> execution status written back to SOW
```

### 5. Dashboard Flow
```text
Dashboard loads
  -> GET /api/v1/sow/dashboard/summary
  -> aggregates saved SOW state
  -> surfaces active risk and exposure
```

---

## Persisted SOW Shape

Conceptually, a saved SOW now contains fields such as:

```json
{
  "analysis_status": "completed",
  "review_status": "pending_approval",
  "risk_assessment": {
    "risk_score": 72,
    "risk_level": "high",
    "total_penalty_exposure": 25000
  },
  "agent_summary": {
    "ingestion_findings": {},
    "risk_findings": {},
    "executive_recommendations": {}
  },
  "alerts": [],
  "action_items": [],
  "scope_creep_items": [],
  "timeline_events": [],
  "approval_history": [],
  "integration_execution": {
    "pre_acceptance": {},
    "post_approval": {}
  }
}
```

---

## Important Current Realities

### watsonx Status
- watsonx configuration variables are present
- ingestion accepts that configuration
- current demo path still uses placeholder/mock parsing behavior in parts of the agent

### Monitoring Status
- review-time monitoring exists
- continuous monitoring for revenue leakage remains a future build area

### Integration Status
- operational routing is moving toward SOW-scoped execution
- global credentials still exist in settings
- execution behavior is increasingly stage-aware

### Frontend Status
- `SOWManagement` is the primary workflow page
- direct `fetch` usage is still embedded in components
- the workflow is demoable, but some validations remain manual

---

## How to Think About the Product

This project should be understood as a **governed contract-to-execution platform**.

The product story is:

1. understand the contract
2. identify operational and financial risk
3. generate concrete remediation work
4. preserve a defensible review record
5. require a human decision
6. execute only approved actions in the right systems

That is the correct conceptual model for future implementation.

---

## Readiness for Future Coding

When continuing development, prioritize work in this order:

1. harden backend upload / review / execute behavior
2. complete stage-aware frontend workflow polish
3. reduce demo logic in monitoring and execution paths
4. improve traceability of execution artifacts
5. wire real watsonx parsing
6. add stronger automated validation and tests

This file should be treated as the current high-level baseline for future implementation work.