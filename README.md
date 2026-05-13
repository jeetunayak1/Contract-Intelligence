# SOW Sentinel 🛡️

**AI-Powered Statement of Work Governance, Compliance & Margin Protection**

> Prevent revenue leakage before it becomes lost margin, missed SLA penalties, or unmanaged delivery work.

[![IBM Hackathon](https://img.shields.io/badge/IBM-Hackathon-blue)](https://ibm.com)
[![watsonx.ai](https://img.shields.io/badge/watsonx.ai-Powered-purple)](https://www.ibm.com/watsonx)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 🎯 Hackathon Pitch

**"SOW Sentinel turns signed contracts into governed execution."**

Service teams usually lose money after the deal is won, not before:
- delivery obligations get buried in long SOWs
- SLA penalties are noticed too late
- vague clauses create dispute risk
- teams do work that never gets billed
- action items stay in email instead of execution systems

**SOW Sentinel** solves that by combining AI extraction, human review, and controlled execution:
1. Upload a new SOW
2. Let agents extract obligations, SLAs, vague clauses, and financial risk
3. Review a saved risk package later
4. Accept, reject, or clear the review decision
5. Execute approved actions into GitHub, Outlook-caliber meeting flows, and post-approval coordination

This is not just document parsing. It is a **contract-to-execution control plane** for service delivery.

---

## 💥 The Problem

Service companies lose millions annually through:
- **Revenue Leakage**: Teams work on out-of-scope tasks without raising a change request
- **Financial Penalties**: Missing SLA deadlines triggers liquidated damages
- **Contract Breaches**: Vague SOW clauses create dispute exposure
- **Margin Erosion**: Untracked delivery commitments silently erode profitability
- **Execution Gaps**: Teams know the risk, but approved actions never get operationalized
- **Manual Governance**: PMs and delivery leads track high-risk commitments in spreadsheets and email

**Real Impact**: A single missed milestone can cost thousands per day in penalties and much more in downstream client trust.

---

## 💡 The Solution

**SOW Sentinel** is an agentic workflow that:
1. **Reads** complex SOWs and extracts obligations, SLA terms, vague clauses, and penalty signals
2. **Analyzes** contract risk and generates business-friendly alerts and action items
3. **Persists** a reusable review package so a human can come back later
4. **Separates** pre-acceptance and post-approval actions
5. **Requires** human approval before downstream execution
6. **Executes** approved work into GitHub and scheduling workflows with traceability

### The Demo "Wow" Moment

```text
🚨 CRITICAL SLA ALERT
"If UAT sign-off is not completed by Friday, penalties begin immediately."

⏰ 48 hours remaining
💰 Exposure: $5,000/day
📊 Agent risk score: 82
📌 Recommended actions:
   • Create GitHub review issue in pre-acceptance repo
   • Schedule executive risk review meeting
   • Escalate ownership before sign-off
```

---

## 🏗️ Product Workflow

### Governed SOW-to-Execution Flow

```text
Upload SOW
  -> Ingestion Agent parses contract
  -> Monitoring Agent derives risk and compliance findings
  -> Executive Agent creates alerts and action items
  -> Persist review package in Cloudant
  -> User reviews saved SOW later
  -> User accepts / rejects / clears review
  -> Execute approved actions in downstream tools
```

### Staged Operational Model

**Pre-Acceptance Stage**
- validate risky clauses before signing off
- create review items in the selected GitHub repo
- schedule review meetings
- surface SLA exposure clearly

**Post-Approval Stage**
- create delivery-governance tasks
- route work into delivery repositories
- prepare coordination metadata for Teams/channel setup
- maintain execution traceability back to the SOW

---

## 🎨 Key Features

### Contract Intelligence
- Upload PDF, DOC, DOCX, or TXT SOWs
- Extract obligations, SLA terms, deadlines, and vague clauses
- Build a persisted review package for later analysis

### Risk Governance
- Numeric risk scoring
- Penalty exposure summaries
- SLA-aware alerts
- Margin leakage and scope creep indicators

### Human-in-the-Loop Control
- Accept SOW review
- Reject SOW review
- Clear review decisions to re-evaluate
- Execute only approved actions

### Operational Execution
- GitHub issue creation for approved actions
- Calendar/scheduling execution metadata
- Stage-aware action routing
- Audit trail and timeline history

### Demo-Ready UI
- Dashboard summary
- Risk Report
- SOW Management workflow
- Integration setup
- Settings for shared credentials

---

## 🧱 Architecture at a Glance

### 4 Core Agent Roles

```text
1. Ingestion Agent
   -> reads SOW files and extracts obligations, SLAs, vague clauses

2. Monitoring Agent
   -> scores compliance risk, scope creep, penalty exposure

3. Executive Agent
   -> converts findings into alerts and action plans

4. Execution Layer
   -> operationalizes approved work in GitHub / scheduling tools
```

Full architecture details: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🛠️ Technology Stack

### Backend
- FastAPI
- Python 3.11+
- Databases: IBM Cloudant or Google Cloud Firestore
- AI/LLMs: IBM watsonx.ai or Google GenAI (Gemini)
- Pydantic / pydantic-settings

### Frontend
- React 18
- TypeScript
- Material UI
- Vite
- react-router-dom
- react-toastify

### Integrations
- GitHub
- Microsoft / Outlook-style calendar flows
- Slack configuration model
- IBM Cloud services documentation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm
- IBM Cloud account for full cloud-backed configuration
- Optional GitHub, Slack, and Microsoft/Outlook credentials

### Local Run

```bash
git clone <your-repo-url>
cd Hackathon

# backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# edit backend/.env with your Cloudant / watsonx / integration values

python -m uvicorn app.main_demo:app --reload --host 0.0.0.0 --port 8000
```

In another terminal:

```bash
cd Hackathon/frontend
npm install
npm run dev -- --host 0.0.0.0
```

### Application URLs
- Frontend: `http://localhost:5173` or the Vite URL shown in terminal
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### Full Pull-and-Run Guide
See [docs/SETUP_FROM_GIT.md](docs/SETUP_FROM_GIT.md)

### Cloud Provider Setup
See [docs/GCP_AND_IBM_SETUP.md](docs/GCP_AND_IBM_SETUP.md) for instructions on switching between IBM and GCP.

---

## 🎬 Recommended Demo Flow

1. Open the SOW Management page
2. Upload a new SOW
3. Show extracted obligations, alerts, and action items
4. Highlight numeric SLA exposure and risk score
5. Accept the SOW review package
6. Execute approved actions
7. Show saved timeline and execution traceability
8. Explain how rejected or cleared reviews support governed operations

---

## 📊 Current Product State

### Working
- SOW upload and analysis flow
- Saved SOW list and detail review
- Timeline retrieval
- Dashboard summary
- Approval decisions:
  - accept
  - reject
  - clear
- Execution of approved actions
- Per-SOW integration modeling
- Numeric risk and penalty visibility in UI

### In Progress
- hardening stage-aware execution behavior
- improving frontend workflow validation
- reducing remaining demo logic in monitoring
- aligning documentation with staged workflow

### Pending / Next Priorities
- real watsonx-backed parsing path
- continuous monitoring for revenue leakage across delivery work
- stronger automated testing
- deeper real-repo execution verification
- documentation and pitch polish for hackathon judging

---

## 🗺️ Pending Tasks

Current high-priority pending work:
1. Complete backend hardening for staged pre-acceptance and post-approval actions
2. Complete frontend UX for stage-aware action execution
3. Replace remaining demo monitoring logic for scope creep and revenue leakage
4. Update architecture and AI context docs fully for staged workflow
5. Verify end-to-end upload → approve/reject/clear → execute flows
6. Push all finalized changes to git

---

## 📡 Key API Endpoints

### SOW Workflow
```text
POST /api/v1/sow/upload
GET  /api/v1/sow/list
GET  /api/v1/sow/{id}
GET  /api/v1/sow/{id}/timeline
GET  /api/v1/sow/dashboard/summary
POST /api/v1/sow/{id}/approve
POST /api/v1/sow/{id}/execute
```

### Integration Workflow
```text
POST   /api/v1/integrations/configure
POST   /api/v1/integrations/apply/{sow_id}
GET    /api/v1/integrations/{sow_id}
DELETE /api/v1/integrations/{sow_id}
```

---

## 📁 Important Files

- [README.md](README.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [.ai/project-context.md](.ai/project-context.md)
- [.ai/codebase-summary.md](.ai/codebase-summary.md)
- [docs/INTEGRATION_CONFIGURATION.md](docs/INTEGRATION_CONFIGURATION.md)
- [docs/SETUP_FROM_GIT.md](docs/SETUP_FROM_GIT.md)
- [docs/GCP_AND_IBM_SETUP.md](docs/GCP_AND_IBM_SETUP.md)

---

## 🏆 IBM Hackathon Fit

This project showcases:
- AI-assisted document understanding
- governed agentic workflows
- human-in-the-loop execution
- contract-aware delivery operations
- business value through revenue protection and risk reduction

**Pitch summary**:  
SOW Sentinel helps service companies stop losing money on contracts they have already won by turning SOW obligations into reviewed, trackable, and executable operational work.

---

## 📞 Support

- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Setup: [docs/SETUP_FROM_GIT.md](docs/SETUP_FROM_GIT.md)
- UI preview: [docs/UI_PREVIEW.md](docs/UI_PREVIEW.md)
- API docs: `http://localhost:8000/docs`

---

## 📄 License

This project is licensed under the MIT License.

---

## 🌟 Demo Note

The current repository contains a mix of production-intent architecture and hackathon/demo-safe logic. The strongest story is the governed workflow:

**Upload** → **Analyze** → **Persist** → **Review** → **Accept/Reject/Clear** → **Execute Approved Actions**