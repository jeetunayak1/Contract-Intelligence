# UI Preview - SOW Sentinel

## Overview

The current UI is designed as a contract-governance workspace for delivery teams. Instead of a generic compliance dashboard, the product now centers on **SOW review, numeric risk visibility, human decisioning, and approved action execution**.

The interface uses Material UI and is intended to support a clean hackathon demo story:
- upload a SOW
- review AI findings
- inspect financial and SLA exposure
- accept, reject, or clear the review
- execute approved actions

---

## Main Layout

### Top Bar
- Product title: **SOW Sentinel**
- Supporting tagline: **Preventing Revenue Leakage**
- Primary blue app bar for a clean enterprise look

### Left Navigation
Current navigation includes:
1. Dashboard
2. Risk Report
3. Integration Setup
4. API Settings
5. SOW Management
6. Compliance
7. Scope Creep
8. Alerts
9. Analytics

The navigation is optimized to make **SOW Management** the operational center of the product.

---

## Primary Working Screen: SOW Management

This is the main demo page and the most important UI in the project.

### Header Area
Shows:
- page title: **SOW Management**
- workflow description focused on upload, review, risk, approval, and execution

### Summary Cards
At the top of the page, the user sees key metrics such as:
- active SOWs
- at-risk obligations
- critical alerts
- total penalty exposure

These metrics make the business impact visible immediately.

---

## Tab 1: Upload New SOW

### Upload Form
The upload flow includes:
- SOW number
- client name
- project name
- document picker for PDF / DOC / DOCX / TXT

### Upload Action
The user can trigger **Upload & Analyze**, which starts the backend workflow:
- parse SOW
- derive risks
- create alerts
- create action items
- persist review package

### Upload UX Goal
This section should feel like the start of a governed business workflow rather than a file-import utility.

---

## Tab 2: Review Saved SOWs

### Saved SOW List
The left panel shows saved SOW cards with:
- project name
- client and SOW number
- risk chip
- review status chip

This lets the user reopen previously analyzed SOWs later.

### Selected SOW Detail
The right panel displays the saved review package:
- project identity
- risk score
- penalty exposure
- alert count
- action item count

This makes the system feel persistent and audit-ready.

---

## Agent Summary Section

The Agent Summary provides three grouped views:

### Ingestion Findings
Summarizes:
- obligations count
- SLA terms count
- vague clauses count

### Risk Findings
Summarizes:
- overall risk level
- total penalty exposure
- high-risk obligations

### Executive Recommendations
Summarizes:
- alerts generated
- action items generated
- scope creep indicators

This section helps explain the value of the agent pipeline during the pitch.

---

## Alerts Section

The Alerts area is designed to showcase urgency and business value.

Typical information shown:
- alert title
- business-readable message
- severity
- penalty exposure
- time remaining
- recommended actions

This is one of the best places to demonstrate:
- SLA awareness
- financial risk visibility
- proactive warning before breach

---

## Action Items Section

The Action Items section is where the product shifts from insight to execution.

Each action item can show:
- title
- description
- severity / priority
- approval state
- execution state
- recommended owner
- workflow stage
- action type
- execution targets
- SLA reference
- numeric risk chips

### Numeric Risk Display
Users may see values such as:
- penalty amount
- days remaining
- hours until penalty
- revenue at stake
- total exposure
- risk score

### Execution Controls
Action items can expose buttons to:
- create GitHub items
- schedule meetings
- execute stage-aware operational tasks

This is critical to the hackathon story because it proves the system goes beyond passive reporting.

---

## Timeline Section

The Timeline shows event history for a saved SOW:
- upload completed
- analysis completed
- review decision saved
- actions executed

This supports auditability and demonstrates that the platform preserves decision history over time.

---

## Review Decision & Actions Section

This is the most important business-governance control in the UI.

The user can:
- add review notes
- **Accept SOW**
- **Reject SOW**
- **Clear Review**
- **Take Actions / Execute Approved Actions**

### Why this matters
This section communicates the core product philosophy:
- AI recommends
- humans decide
- systems execute only after approval

That makes the workflow safer and more enterprise-ready.

---

## Risk Report Page

The Risk Report page supports the visual storytelling side of the demo.

It is useful for:
- surfacing critical issues quickly
- highlighting penalty exposure
- showing a “wow moment” around SLA risk
- framing why the SOW workflow matters operationally

Use this page when you want to open the demo with urgency, then move into SOW Management to show control and execution.

---

## Dashboard

The Dashboard is intended to summarize the overall health of the SOW portfolio.

Expected themes:
- active delivery risk
- number of critical alerts
- penalty exposure
- trend toward revenue protection

This works best as the executive entry point before drilling into individual SOWs.

---

## Integration Setup

The Integration Setup area supports SOW-scoped operational configuration.

It is where the user can frame how approved work should be routed:
- GitHub targets
- calendar / Outlook-style scheduling details
- other collaboration system mappings

This is important because the system is not just identifying work; it is preparing where that work should go.

---

## Design Language

### Colors
- **Primary Blue**: app identity and navigation emphasis
- **Error Red**: critical financial or SLA risk
- **Warning Orange**: at-risk items and pending deadlines
- **Info Blue**: medium-priority indicators
- **Success Green**: approved / healthy states

### Typography
- bold headings for key business sections
- readable body text for contract and alert summaries
- large numeric cards for risk and exposure metrics

### Card-Driven Layout
The UI uses cards heavily to:
- isolate business concepts
- keep the interface scannable
- make the product demo-friendly

---

## Responsive Intent

The UI is designed to adapt across:
- desktop
- tablet
- mobile

### Desktop
Best experience for full demo:
- persistent sidebar
- multi-column review layout
- card-based analytics view

### Tablet / Smaller Screens
- stacked content
- reduced horizontal density
- preserved access to core decision actions

---

## Demo Walkthrough Recommendation

For the strongest demo:

1. Open **Risk Report** to establish urgency
2. Move to **SOW Management**
3. Upload a sample SOW
4. Open the saved SOW review package
5. Highlight alerts and penalty exposure
6. Show action items with SLA references and risk chips
7. Accept or reject the review package
8. Execute approved actions
9. Show the timeline for auditability

This sequence lands both the technical and business story.

---

## Current Reality

The current UI has moved beyond a mock dashboard. It now reflects a more realistic governed workflow:
- persisted SOWs
- live review packages
- numeric risk
- approval controls
- execution triggers

Some screens still retain demo-friendly assumptions, but the main interaction model is now aligned with the product vision.

---

## Run Locally

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Then open the Vite URL shown in the terminal, commonly:
- `http://localhost:5173`

Backend should also be running:
- `http://localhost:8000`

---

## UI Summary

SOW Sentinel’s UI is designed to answer five questions quickly:

1. What risk exists in this SOW?
2. How much money is exposed?
3. What actions should be taken?
4. Has a human approved those actions?
5. What has already been executed?

That makes the interface not just attractive for a hackathon demo, but meaningful for real delivery governance.