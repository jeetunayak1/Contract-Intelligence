# Codebase Summary - SOW Sentinel

## Quick Reference

**Project**: IBM Hackathon - SOW Sentinel  
**Location**: `/Users/jeetendranayak/Hackathon`  
**Status**: Governed SOW workflow with persisted review, decisioning, and approved execution  
**Backend**: `http://localhost:8000`  
**Frontend**: Vite-based React app  
**Primary Demo Route**: `/sows`

---

## High-Level State

This codebase has evolved from a demo-style parser and risk dashboard into a **governed SOW-to-execution workflow**.

```text
Upload SOW
  -> Parse with agents
  -> Create review package
  -> Persist findings
  -> Reopen later
  -> Accept / Reject / Clear
  -> Execute approved actions
```

The current implementation already supports:
- persisted SOW records
- review packages
- decision tracking
- action execution entry points
- numeric risk and penalty visibility

---

## Top-Level Structure

```text
- backend/         FastAPI API, agents, persistence, models
- frontend/        React + TypeScript UI
- docs/            setup and product documentation
- .ai/             AI working context and summaries
- _archive/        legacy and reference material
```

---

## Critical Files to Know

### 1. Entry Points

| File | Purpose | Status |
|------|---------|--------|
| `backend/app/main_demo.py` | Demo FastAPI server | Active |
| `backend/app/main.py` | Production API entry | Secondary |
| `frontend/src/main.tsx` | React entry point | Active |
| `frontend/src/App.tsx` | App shell, nav, routes | Active |

### 2. Core Backend Files

| File | Purpose | Notes |
|------|---------|-------|
| `backend/app/api/sow.py` | Main SOW workflow API | Upload, list, detail, approve, execute |
| `backend/app/api/integrations.py` | Per-SOW integration generation and apply | GitHub / Slack / Outlook modeling |
| `backend/app/agents/ingestion_agent.py` | Parses SOWs and derives structure | Still partly demo-backed |
| `backend/app/agents/monitoring_agent.py` | Compliance / risk / scope creep logic | Key future hardening area |
| `backend/app/agents/executive_agent.py` | Alert and action recommendation logic | Some downstream behavior still demo-ish |
| `backend/app/core/cloudant_db.py` | Cloudant CRUD/query layer | Persistence backbone |
| `backend/app/core/config.py` | Environment-backed settings | Includes cloud and integration config |
| `backend/app/models/sow_models.py` | SOW document helpers | Core data helpers |
| `backend/app/models/integration_config.py` | SOW integration models | Supports workflow routing |

### 3. Core Frontend Files

| File | Purpose | Notes |
|------|---------|-------|
| `frontend/src/App.tsx` | Main routing/navigation | `/sows` is key route |
| `frontend/src/pages/SOWManagement.tsx` | Main governed workflow UI | Upload / review / decide / execute |
| `frontend/src/pages/Dashboard.tsx` | Summary dashboard | Uses live workflow-oriented data |
| `frontend/src/pages/RiskReport.tsx` | Risk showcase page | Strong for demo storytelling |
| `frontend/src/pages/IntegrationConfig.tsx` | Integration setup | Supports SOW-scoped routing |
| `frontend/src/pages/Settings.tsx` | Global/shared credentials | Not per-SOW operations |

### 4. Core Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main project and pitch document |
| `ARCHITECTURE.md` | End-to-end workflow and architecture story |
| `docs/UI_PREVIEW.md` | UI walkthrough and demo framing |
| `.ai/project-context.md` | AI-facing product and workflow context |
| `.ai/codebase-summary.md` | This file |
| `docs/SETUP_FROM_GIT.md` | Fresh checkout setup guide |

---

## Current Workflow in Code

### 1. Upload
The upload path is centered in [`upload_sow()`](backend/app/api/sow.py:228).

Responsibilities:
- accept file upload
- write temp file
- parse via [`IngestionAgent.parse_sow_document()`](backend/app/agents/ingestion_agent.py:67)
- derive quick risk and review content
- persist review package in Cloudant

### 2. Review Package Construction
The main workflow logic lives in [`backend/app/api/sow.py`](backend/app/api/sow.py), especially:
- [`_sanitize_for_response()`](backend/app/api/sow.py:33)
- [`_build_agent_summary()`](backend/app/api/sow.py:40)
- [`_build_action_items()`](backend/app/api/sow.py:68)
- [`_build_review_package()`](backend/app/api/sow.py:153)
- [`_save_sow_document()`](backend/app/api/sow.py:215)

These functions define the product’s most important behavior.

### 3. Review Decisioning
The decision path supports:
- approval
- rejection
- clearing/resetting the review state

This is handled through the approval endpoint in [`backend/app/api/sow.py`](backend/app/api/sow.py).

### 4. Action Execution
Approved actions are executed via the SOW execution endpoint in [`backend/app/api/sow.py`](backend/app/api/sow.py).

Current design supports:
- stage-aware execution
- GitHub issue generation
- scheduling-related execution metadata
- execution artifacts written back to the SOW

### 5. Frontend Operation Surface
[`frontend/src/pages/SOWManagement.tsx`](frontend/src/pages/SOWManagement.tsx) is now the most important user-facing page.

It provides:
- upload form
- saved SOW list
- selected SOW detail
- risk summary
- alerts
- action items
- review notes
- accept/reject/clear actions
- execution triggers
- timeline view

---

## API Endpoints

### Core App / Infra
```text
GET  /
GET  /health
```

### SOW Workflow
```text
POST /api/v1/sow/upload
GET  /api/v1/sow/list
GET  /api/v1/sow/{sow_id}
GET  /api/v1/sow/{sow_id}/timeline
GET  /api/v1/sow/{sow_id}/risk-report
GET  /api/v1/sow/{sow_id}/penalty-countdown
GET  /api/v1/sow/dashboard/summary
POST /api/v1/sow/{sow_id}/approve
POST /api/v1/sow/{sow_id}/execute
```

### Integration Workflow
```text
POST   /api/v1/integrations/configure
POST   /api/v1/integrations/apply/{sow_id}
GET    /api/v1/integrations/{sow_id}
DELETE /api/v1/integrations/{sow_id}
```

---

## Data Model Concepts

### SOW Document
The persisted SOW now carries workflow state such as:
- `analysis_status`
- `review_status`
- `risk_assessment`
- `agent_summary`
- `alerts`
- `action_items`
- `scope_creep_items`
- `timeline_events`
- `approval_history`
- `integration_execution`

### Action Item
Operational work derived from contract findings, usually containing:
- `id`
- `title`
- `description`
- `priority`
- `recommended_owner`
- `approval_state`
- `execution_state`
- `workflow_stage`
- `execution_targets`
- `sla_reference`

### Integration Execution
Tracks downstream actioning such as:
- GitHub issues created
- scheduling metadata
- stage-specific execution state
- timestamps and traceability

---

## Current Product/Engineering Reality

### Working Well
- upload and persisted SOW workflow
- saved review package retrieval
- timeline retrieval
- dashboard summary
- review decision controls
- action execution entry points
- numeric risk visibility in UI
- browser-accessible demo flow

### Caveats
- ingestion still includes placeholder/demo parsing behavior
- monitoring still contains demo assumptions in places
- downstream execution needs more real-world validation
- direct `fetch` calls remain embedded in page components
- automated end-to-end verification is still limited

---

## Known Gaps

1. **Full watsonx-backed parsing**
   - config exists
   - true inference path needs completion

2. **Continuous revenue leakage monitoring**
   - review-time detection exists
   - continuous Git/delivery monitoring is still pending

3. **Execution hardening**
   - real repo/calendar behavior needs deeper verification

4. **Frontend service normalization**
   - API calls should move into shared services

5. **Automated validation**
   - stronger tests are still needed

---

## Best Files to Open First

If continuing implementation, start here:

1. [`backend/app/api/sow.py`](backend/app/api/sow.py)
2. [`frontend/src/pages/SOWManagement.tsx`](frontend/src/pages/SOWManagement.tsx)
3. [`backend/app/api/integrations.py`](backend/app/api/integrations.py)
4. [`frontend/src/pages/IntegrationConfig.tsx`](frontend/src/pages/IntegrationConfig.tsx)
5. [`ARCHITECTURE.md`](ARCHITECTURE.md)
6. [`README.md`](README.md)

---

## Recommended Next Priorities

1. complete backend hardening for stage-aware execution
2. finish frontend UX polish for staged decisions and actions
3. reduce demo logic in monitoring and execution agents
4. add continuous revenue-leakage monitoring capabilities
5. verify full upload → review → decide → execute flows
6. push finalized repo state to git

---

## Summary

The most important mental model for this repository is:

**This is a governed SOW-to-execution workflow system.**

Not just:
- a parser
- a dashboard
- a risk report

But:
- upload
- analyze
- persist
- review
- accept / reject / clear
- execute approved actions

That is the correct frame for future development, documentation, and hackathon pitching.