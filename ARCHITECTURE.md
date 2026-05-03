# SOW Sentinel - Agentic Compliance Framework

## 🎯 Project Vision

**SOW Sentinel** is an AI-powered governed execution system for service companies. It prevents revenue leakage, contract breaches, and SLA misses by turning long-form Statements of Work into reviewed, traceable, and executable operational work.

The platform does not stop at extraction. It connects:

**contract understanding** → **risk analysis** → **human review** → **approved execution**

This makes it especially suited for delivery teams that need both automation and control.

---

## 💡 The Core Problem

Service-based companies face the same pattern repeatedly:

1. **Revenue Leakage**  
   Teams perform work outside the SOW and fail to capture billable change requests.

2. **Financial Penalties**  
   Missing delivery milestones or SLA obligations triggers liquidated damages.

3. **Contract Breaches**  
   Vague language and hidden obligations create avoidable compliance failures.

4. **Margin Erosion**  
   Delivery commitments expand faster than tracked revenue.

5. **Execution Gaps**  
   Teams may understand the risk but still fail to operationalize corrective actions.

6. **Weak Auditability**  
   When issues occur, there is no clean trail showing what was identified, approved, or executed.

**Business reality**: winning the contract is not enough; teams must govern delivery against the contract continuously.

---

## 🏗️ System Architecture: Upload → Analyze → Review → Decide → Execute

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                              SOW Sentinel System                            │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  1. SOW Upload Layer                                                        │
│  - User uploads PDF / DOC / DOCX / TXT SOW                                  │
│  - Captures SOW number, client, project metadata                            │
│  - Hands file to backend workflow                                           │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  2. Ingestion Agent                                                         │
│  - Reads the SOW                                                            │
│  - Extracts obligations, SLA clauses, deadlines, vague terms                │
│  - Produces normalized contract structure                                   │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  3. Monitoring Agent                                                        │
│  - Computes compliance indicators                                           │
│  - Estimates penalty and delivery exposure                                  │
│  - Detects scope creep and revenue leakage signals                          │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  4. Executive Agent                                                         │
│  - Converts findings into alerts                                            │
│  - Generates business-friendly action items                                 │
│  - Separates pre-acceptance vs post-approval work                           │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  5. Persisted Review Package                                                │
│  Saved to Cloudant with:                                                    │
│  - analysis_status                                                          │
│  - review_status                                                            │
│  - risk_assessment                                                          │
│  - alerts                                                                   │
│  - action_items                                                             │
│  - scope_creep_items                                                        │
│  - approval_history                                                         │
│  - integration_execution                                                    │
│  - timeline_events                                                          │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  6. Human Review & Decision Layer                                           │
│  - Reviewer reopens saved SOW later                                         │
│  - Accepts, rejects, or clears the package                                  │
│  - Notes and decisions are persisted                                        │
│  - Timeline preserves auditability                                          │
└──────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  7. Execution Layer                                                         │
│  - Approved actions are operationalized                                     │
│  - Pre-acceptance tasks can go to review repos / meetings                   │
│  - Post-approval tasks can go to delivery repos / coordination workflows    │
│  - Execution artifacts are saved back to the SOW                            │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Agent Roles

### 1. Ingestion Agent - The Reader
**Responsibilities**
- parse uploaded SOW documents
- extract deliverables, milestones, obligations, and SLA terms
- flag vague or risky contractual language
- normalize results into structured JSON

**Current state**
- integrated into upload flow
- accepts watsonx-related configuration
- still contains demo/placeholder parsing behavior in parts of the path

---

### 2. Monitoring Agent - The Watchman
**Responsibilities**
- derive compliance risk indicators
- estimate penalty exposure
- identify margin leakage and scope creep patterns
- support future continuous monitoring over delivery signals

**Current state**
- used during review package generation
- supports review-time findings
- continuous recurring monitoring is still a pending enhancement

---

### 3. Executive Agent - The Actor
**Responsibilities**
- generate business-friendly alerts
- create recommended actions with ownership
- shape findings into human-reviewable operational packages
- support escalation logic for critical items

**Current state**
- contributes to alert and action generation
- downstream execution is approval-driven
- some execution behavior remains demo-oriented

---

### 4. Execution / Mapping Layer - The Bridge
**Responsibilities**
- route approved work into GitHub and scheduling systems
- maintain SOW-scoped operational isolation
- preserve SOW → action → execution traceability

**Current state**
- supports per-SOW integration modeling
- stage-aware execution behavior exists
- deeper real-world validation is still pending

---

## 🎨 Product Flows

### A. Upload and Analyze

```text
Upload SOW
  -> parse contract
  -> extract obligations / SLA terms / vague clauses
  -> score risk and exposure
  -> generate alerts and action items
  -> save review package
```

### B. Review Later

```text
Open saved SOW
  -> fetch persisted review package
  -> inspect risk, alerts, action items, timeline
  -> understand numeric exposure before deciding
```

### C. Review Decision

```text
Reviewer chooses one of:
  -> accept
  -> reject
  -> clear

Then:
  -> decision is persisted
  -> approval history is updated
  -> timeline event is added
  -> action states are adjusted
```

### D. Execute Approved Actions

```text
Approved actions
  -> check workflow stage
  -> use SOW-scoped integration configuration
  -> create GitHub issues or meeting actions
  -> save execution status and artifacts
  -> expose results back in UI and timeline
```

---

## 🔄 Stage-Aware Operating Model

### Pre-Acceptance Stage
This stage is for work that should happen **before the SOW is fully accepted or signed off for delivery**.

Typical goals:
- validate risky SLA commitments
- challenge vague or ambiguous clauses
- create review items in GitHub
- schedule executive or PM review meetings
- force visibility into exposure before acceptance

### Post-Approval Stage
This stage is for work that should happen **after the SOW is approved for operational delivery**.

Typical goals:
- launch delivery-governance tasks
- create implementation-tracking items in delivery repositories
- coordinate follow-up execution work
- preserve SLA references and ownership throughout delivery

This staged separation is important because it prevents the system from creating implementation work too early.

---

## 📊 Key Features

### 1. Persisted Review Package
Every uploaded SOW becomes a durable review object containing:
- obligations
- vague clauses
- SLA terms
- risk assessment
- alerts
- action items
- timeline
- approval history
- execution history

### 2. Human-in-the-Loop Governance
The system does not blindly automate high-impact actions. It:
- recommends
- waits for human decision
- executes only approved work

### 3. Numeric Financial Risk
The system can surface:
- risk scores
- total penalty exposure
- per-alert or per-action exposure
- days/hours until penalty conditions
- potential revenue at risk

### 4. SOW-Scoped Execution
Each SOW can be routed independently to:
- a GitHub review destination
- a delivery destination
- scheduling / coordination targets
- SOW-specific labels and references

### 5. Auditability
Timeline and history allow users to see:
- when the SOW was uploaded
- when analysis completed
- when it was accepted, rejected, or cleared
- when downstream work was executed

---

## 📦 Persisted Data Model

### SOW Document (Conceptual)

```json
{
  "_id": "SOW-2024-ACME-001",
  "type": "sow",
  "sow_number": "2024-ACME-001",
  "client_name": "Acme Corp",
  "project_name": "Enterprise Platform Migration",
  "analysis_status": "completed",
  "review_status": "pending_approval",
  "risk_assessment": {
    "risk_score": 72,
    "risk_level": "high",
    "total_penalty_exposure": 25000
  },
  "alerts": [],
  "action_items": [],
  "scope_creep_items": [],
  "approval_history": [],
  "timeline_events": [],
  "integration_execution": {
    "pre_acceptance": {},
    "post_approval": {}
  }
}
```

### Action Item (Conceptual)

```json
{
  "id": "ACTION-OBL-001",
  "title": "Validate SLA response commitment before acceptance",
  "description": "Review the contractual response-time commitment and confirm delivery feasibility.",
  "priority": "high",
  "recommended_owner": "project_manager",
  "approval_state": "pending",
  "execution_state": "not_started",
  "workflow_stage": "pre_acceptance",
  "sla_reference": "UAT sign-off within 5 business days"
}
```

### Approval Record (Conceptual)

```json
{
  "decided_at": "2026-05-03T10:15:00Z",
  "decision": "approved",
  "notes": "Proceed with review repo items and risk meeting.",
  "approved_alert_ids": ["ALERT-001"],
  "approved_action_ids": ["ACTION-OBL-001"]
}
```

---

## 🔌 Integration Architecture

### Global Credentials vs SOW-Scoped Operations

The system distinguishes between:
- **global credentials** used to authenticate external systems
- **SOW-scoped operational routing** used to decide where approved work should go

This allows shared secret storage while still keeping execution isolated by project/SOW.

### GitHub
Used for:
- pre-acceptance review tasks
- post-approval delivery tasks
- labels and metadata traceability
- recording execution links back onto the SOW

### Outlook / Calendar-Oriented Scheduling
Used for:
- executive review meetings
- delivery coordination meetings
- stage-aware scheduling metadata

### Slack / Collaboration
Modeled for:
- alerts
- SOW-specific stakeholder routing
- coordination workflows

---

## 🖥️ Frontend Architecture

### Main User Surfaces
- Dashboard
- Risk Report
- Integration Setup
- API Settings
- SOW Management

### SOW Management Responsibilities
The SOW Management page is the primary working surface for the product:
- upload new SOWs
- review saved packages
- inspect alerts and action items
- see numeric risk
- add review notes
- accept / reject / clear
- execute approved work
- inspect timeline and downstream results

---

## 🏆 Hackathon Story

The strongest demo sequence is:

1. Upload a real or sample SOW
2. Show AI-derived obligations, alerts, and SLA risk
3. Highlight financial exposure
4. Reopen the saved review package
5. Accept or reject the review package
6. Execute approved actions into downstream systems
7. Show the timeline and traceability

This demonstrates:
- AI document understanding
- contract-aware governance
- human-controlled execution
- operational traceability
- measurable business value

---

## 🚧 Current Gaps / Pending Work

1. **Live watsonx inference**
   - config exists
   - parsing path is still partly demo-backed

2. **Continuous monitoring**
   - review-time monitoring exists
   - continuous ticket/revenue-leakage monitoring remains pending

3. **Execution hardening**
   - stage-aware execution exists
   - needs more real-world validation

4. **Frontend service layer**
   - direct fetch calls remain embedded in components
   - should migrate to dedicated services

5. **Automated validation**
   - end-to-end automated tests remain limited

6. **Documentation alignment**
   - product, architecture, and setup docs need to stay aligned as staged workflow evolves

---

## ✅ Architecture Summary

SOW Sentinel should be understood as a **governed contract-to-execution system**.

Its core flow is:

**Upload** → **Analyze** → **Persist** → **Review** → **Accept / Reject / Clear** → **Execute Approved Actions**

That is the architectural foundation for future implementation and the core hackathon message.