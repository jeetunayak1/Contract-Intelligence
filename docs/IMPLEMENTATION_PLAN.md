# SOW Sentinel Implementation Plan

## Goal

Complete the application so users can:

1. Upload a new SOW
2. Run agentic analysis on the uploaded SOW
3. Review extracted obligations, SLA terms, risks, alerts, and action points later
4. Approve recommended items
5. Persist all approved items to the database
6. Convert approved action items into GitHub actions after per-SOW GitHub configuration

## Target End-to-End Flow

```text
Upload SOW
  -> Ingestion Agent parses document
  -> Review package is created
  -> Monitoring Agent derives SLA risks and alert candidates
  -> Executive Agent derives action points and recommended actions
  -> Review package is saved in Cloudant
  -> User opens review later
  -> User approves/rejects alerts and action items
  -> Approved review is persisted
  -> If GitHub is configured for this SOW, approved action items are converted into GitHub issues/tasks
```

## Backend Changes

### 1. New persisted review state on SOW
Extend the SOW document to store:

- `analysis_status`
- `review_status`
- `agent_summary`
- `alerts`
- `action_items`
- `timeline_events`
- `approval_history`
- `integration_execution`

### 2. New API behavior in `backend/app/api/sow.py`
Add or upgrade endpoints:

- `POST /api/v1/sow/upload`
  - save uploaded file
  - parse SOW
  - generate review package
  - save to Cloudant
- `GET /api/v1/sow/list`
  - return real stored SOW documents
- `GET /api/v1/sow/{sow_id}`
  - return full persisted review state
- `POST /api/v1/sow/{sow_id}/approve`
  - approve selected alerts/action items
  - persist approval state
- `POST /api/v1/sow/{sow_id}/execute`
  - convert approved action items into GitHub tasks using per-SOW integration config
- `GET /api/v1/sow/{sow_id}/timeline`
  - review history and agent decisions

### 3. New orchestration service in SOW flow
Within upload flow:

- [`IngestionAgent.parse_sow_document()`](backend/app/agents/ingestion_agent.py:67)
- Monitoring-style risk derivation
- [`ExecutiveAgent.create_alert()`](backend/app/agents/executive_agent.py:105) style alert creation
- new action item generation helper
- database persistence using [`cloudant_db.create_document()`](backend/app/core/cloudant_db.py:59)

### 4. GitHub conversion
Use per-SOW integration config from [`backend/app/api/integrations.py`](backend/app/api/integrations.py) and stored config documents:

- map approved action items to GitHub issues
- write resulting issue metadata back to SOW document
- preserve traceability between:
  - SOW obligation
  - approved action item
  - GitHub issue

## Frontend Changes

### 1. Replace placeholder SOW Management
Current route in [`frontend/src/App.tsx`](frontend/src/App.tsx) points `/sows` to a placeholder.
Replace with full page supporting:

- upload new SOW
- list saved SOWs
- open SOW review
- approve/reject action items
- push approved actions to GitHub

### 2. New page behavior
New `SOW Management` page should show:

- upload form
- saved SOW table/cards
- review drawer or detail page
- obligations
- SLA terms
- vague clauses
- financial risk summary
- alert recommendations
- action points
- approval controls
- GitHub execution status

### 3. Dashboard updates
Update [`frontend/src/pages/Dashboard.tsx`](frontend/src/pages/Dashboard.tsx) to surface stored review state:

- recently uploaded SOWs
- pending approvals
- approved but not executed actions
- active alerts from persisted records

## Data Model Extensions

Extend models in [`backend/app/models/sow_models.py`](backend/app/models/sow_models.py) with helpers for:

- alert review entries
- actionable task entries
- approval records
- execution records
- agent summary blocks

Suggested objects:

```json
{
  "analysis_status": "completed",
  "review_status": "pending_approval",
  "agent_summary": {
    "ingestion_findings": [],
    "risk_findings": [],
    "executive_recommendations": []
  },
  "alerts": [],
  "action_items": [],
  "approval_history": [],
  "integration_execution": {
    "github": {
      "executed": false,
      "issues_created": []
    }
  }
}
```

## Documentation Updates Needed

Update these files to reflect the new complete story:

- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`.ai/project-context.md`](.ai/project-context.md)
- [`.ai/codebase-summary.md`](.ai/codebase-summary.md)
- [`README.md`](README.md)
- [`_archive/HACKATHON_GUIDE.md`](_archive/HACKATHON_GUIDE.md)

## Hackathon Selling Points

Emphasize:

1. Upload a real SOW and get immediate AI extraction
2. Get penalty, SLA, vague clause, and scope creep visibility
3. Review and approve AI recommendations instead of blind automation
4. Persist every review for auditability
5. Convert approved decisions into GitHub execution automatically
6. Keep each SOW isolated with its own team, alerts, actions, and integrations

## Delivery Order

1. Extend backend SOW models
2. Implement persisted upload/review APIs
3. Implement approval and execution APIs
4. Build SOW Management UI
5. Connect dashboard to stored review state
6. Update architecture and hackathon docs
7. Verify end-to-end flow