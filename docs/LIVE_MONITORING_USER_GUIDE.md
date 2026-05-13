# Live Monitoring Dashboard - User Guide

## 🎯 Overview

The Live Monitoring Dashboard is a real-time multi-agent analysis system that provides comprehensive insights into SOW compliance, risk exposure, and financial health.

## 🚀 How to Access

1. **Start the Application**
   - Backend should be running on `http://localhost:8000`
   - Frontend should be running on `http://localhost:3000`

2. **Navigate to Live Monitoring**
   - Click on the sidebar menu icon (☰) if sidebar is hidden
   - Click on **"Live Monitoring"** in the sidebar
   - Or navigate directly to: `http://localhost:3000/monitoring`

## 📊 Dashboard Components

### 1. Agent Status Bar
Located at the top of the dashboard, shows the status of all 4 agents:

- **Contract Agent** - SLAs, penalties, scope analysis
- **Compliance Agent** - Live SLA vs ops data
- **Risk Agent** - Penalty, liability detect
- **Forecast Agent** - Breach prob, margin

Each agent shows:
- ✅ Active status
- 🎯 Current capabilities
- 📈 Real-time processing

### 2. Main Metrics Grid (4 Key Metrics)

#### A. SLA Health
- **Overall Score**: 0-100% compliance rate
- **Visual Indicator**: Color-coded progress bar
  - Green (90%+): Healthy
  - Orange (70-89%): Warning
  - Red (<70%): Critical
- **Breakdown**:
  - Compliant SLAs (green)
  - At Risk SLAs (orange)
  - Breached SLAs (red)

**How to Use:**
- Monitor overall health score
- Click on individual SLAs for details
- Track trends over time

#### B. Penalty Exposure
- **Total Exposure**: Dollar amount at risk
- **Trend Indicator**: Increasing/Stable/Decreasing
- **Breakdown**:
  - Immediate exposure (breached SLAs)
  - Potential exposure (at-risk SLAs)

**How to Use:**
- Monitor total $ exposure
- Prioritize high-value penalties
- Track exposure trends

#### C. Scope Burn
- **Burn Percentage**: Hours used vs contract
- **Visual Progress**: Shows consumption rate
- **Out-of-Scope Detection**: Alerts for unbilled work

**How to Use:**
- Monitor hours consumption
- Identify out-of-scope work
- Plan resource allocation

#### D. Breach Risk
- **Probability**: 0-100% chance of SLA breach
- **Risk Level**: Low/Medium/High/Critical
- **Risk Factors**: Key contributors to risk

**How to Use:**
- Assess breach likelihood
- Review risk factors
- Take preventive action

### 3. AI Recommendation Panel

The most important section - provides actionable insights:

#### Recommendation Types:

**🔴 Critical Recommendations**
- Immediate action required
- High financial impact
- Example: "Convert $25K penalty risk to change order"

**🟡 High Priority Recommendations**
- Urgent attention needed
- Moderate financial impact
- Example: "Bill for 50 hours of out-of-scope work"

**🟢 Medium Priority Recommendations**
- Monitor and plan
- Lower financial impact
- Example: "Schedule capacity review"

#### Each Recommendation Includes:
- **Title**: Clear description of the issue
- **Description**: Detailed context
- **Priority Level**: Critical/High/Medium
- **Recommended Actions**: Step-by-step guidance
- **Financial Impact**: Dollar amounts (where applicable)

#### Change Order Drafts
When out-of-scope work is detected:
- Auto-generated change order draft
- Total value calculation
- Item-by-item breakdown
- One-click review access

**How to Use:**
1. Review recommendations by priority
2. Click "Review Draft" for change orders
3. Execute recommended actions
4. Track completion status

### 4. Margin Forecast

Three-panel view of financial health:

#### Current Margin
- Current margin percentage
- Current margin dollar amount
- Status: Healthy/At Risk

#### Projected Margin
- Forecasted margin percentage
- Projected margin dollar amount
- Trend indicator

#### Margin Erosion
- Dollar amount of erosion
- Risk status
- Recommendation for action

**How to Use:**
- Compare current vs projected
- Monitor erosion trends
- Take corrective action early

## 🎮 Interactive Features

### SOW Selection
- **Chip-based selector** at the top
- Click any SOW to switch context
- Real-time data refresh
- Color-coded for active selection

### Real-Time Updates
- Dashboard refreshes on SOW selection
- All metrics update simultaneously
- Agent status shows live processing

### Navigation
- **Sidebar Toggle**: Click menu icon (☰) to hide/show
- **Quick Access**: Direct links to all sections
- **Breadcrumbs**: Track your location

## 📈 Use Cases

### Use Case 1: Daily Health Check
1. Navigate to Live Monitoring
2. Review SLA Health score
3. Check Penalty Exposure
4. Review AI Recommendations
5. Take action on critical items

### Use Case 2: Risk Assessment
1. Select SOW from dropdown
2. Check Breach Risk percentage
3. Review Risk Factors
4. Implement preventive measures
5. Monitor trend changes

### Use Case 3: Financial Planning
1. Review Scope Burn metrics
2. Check Margin Forecast
3. Identify out-of-scope work
4. Generate change orders
5. Protect margin

### Use Case 4: Executive Reporting
1. Capture dashboard screenshot
2. Export key metrics
3. Share AI recommendations
4. Present change order drafts
5. Track action items

## 🔔 Alert Interpretation

### Color Coding System

**Green (✅)**
- Healthy status
- Low risk
- On track
- Action: Monitor

**Orange (⚠️)**
- Warning status
- Medium risk
- Attention needed
- Action: Plan intervention

**Red (🔴)**
- Critical status
- High risk
- Immediate action required
- Action: Execute now

### Priority Levels

**Critical**
- Immediate financial impact
- SLA breach imminent
- Action: Within 24 hours

**High**
- Significant risk
- Preventable loss
- Action: Within 3 days

**Medium**
- Moderate concern
- Planning needed
- Action: Within 1 week

## 💡 Best Practices

### Daily Routine
1. **Morning**: Check SLA Health and Penalty Exposure
2. **Midday**: Review AI Recommendations
3. **Evening**: Update action items and track progress

### Weekly Review
1. Compare week-over-week trends
2. Review all change order drafts
3. Assess margin forecast accuracy
4. Update risk mitigation plans

### Monthly Analysis
1. Analyze breach probability trends
2. Review scope burn patterns
3. Assess agent effectiveness
4. Optimize monitoring thresholds

## 🛠️ Troubleshooting

### Dashboard Not Loading
- Check backend is running: `http://localhost:8000/health`
- Check frontend is running: `http://localhost:3000`
- Verify SOW data exists in database

### No Data Showing
- Ensure at least one SOW is uploaded
- Check SOW has been analyzed
- Verify API endpoints are accessible

### Metrics Not Updating
- Refresh the page
- Re-select the SOW
- Check browser console for errors

## 📞 Support

For issues or questions:
1. Check the implementation document: `docs/ENHANCED_ARCHITECTURE_IMPLEMENTATION.md`
2. Review API documentation: `http://localhost:8000/docs`
3. Check agent logs in backend terminal

## 🎯 Quick Reference

### Key Metrics Thresholds

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| SLA Health | >90% | 70-90% | <70% |
| Breach Risk | <30% | 30-60% | >60% |
| Margin | >20% | 10-20% | <10% |
| Scope Burn | <80% | 80-95% | >95% |

### API Endpoints

- Live Dashboard: `GET /api/v1/monitoring/live-dashboard/{sow_id}`
- SLA Health: `GET /api/v1/monitoring/sla-health/{sow_id}`
- Penalty Exposure: `GET /api/v1/monitoring/penalty-exposure/{sow_id}`
- Scope Burn: `GET /api/v1/monitoring/scope-burn/{sow_id}`
- Breach Risk: `GET /api/v1/monitoring/breach-risk/{sow_id}`

### Keyboard Shortcuts

- `Ctrl/Cmd + K`: Toggle sidebar
- `Ctrl/Cmd + R`: Refresh dashboard
- `Esc`: Close dialogs

---

**Version**: 1.0  
**Last Updated**: 2026-05-13  
**Status**: Production Ready