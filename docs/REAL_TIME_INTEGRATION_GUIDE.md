# Real-Time Integration Guide

## 🎯 Current State vs Real-Time

### What's Currently Working (Real Data)
✅ **SOW Document Data** - Pulled from your database (Firestore/Cloudant)
✅ **Obligations** - Extracted from actual SOW documents
✅ **Risk Assessments** - Calculated from real SOW data
✅ **Alerts** - Generated from actual contract analysis
✅ **Action Items** - Created from real SOW obligations
✅ **Scope Creep Items** - Detected from actual documents

### What's Currently Mocked (Demo Data)
⚠️ **GitHub Velocity** - Hardcoded demo values
⚠️ **Timesheet Hours** - Calculated as 75% of contract hours
⚠️ **Uptime Metrics** - Fixed at 99.2%
⚠️ **Response Times** - Fixed at 3.5 hours
⚠️ **Burn Rate** - Estimated at 40 hours/week

## 🔌 How to Make It Real-Time

### Phase 1: GitHub Integration (Live Velocity & Issues)

#### Step 1: Set Up GitHub API Access

1. **Get GitHub Personal Access Token**
   ```bash
   # Go to: https://github.com/settings/tokens
   # Create token with scopes: repo, read:org
   ```

2. **Update .env file**
   ```bash
   GITHUB_TOKEN=your_github_personal_access_token
   GITHUB_OWNER=your-github-username-or-org
   GITHUB_REPO=your-repository-name
   ```

#### Step 2: Implement Real GitHub Integration

**File**: `backend/app/integrations/github_live.py` (NEW)

```python
"""
Live GitHub Integration
"""
import httpx
from typing import Dict, Any
from datetime import datetime, timedelta

class GitHubLiveIntegration:
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def get_velocity_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get real commit velocity and issue metrics"""
        async with httpx.AsyncClient() as client:
            # Get commits
            since = (datetime.utcnow() - timedelta(days=days)).isoformat()
            commits_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/commits"
            commits_response = await client.get(
                commits_url,
                headers=self.headers,
                params={"since": since}
            )
            commits = commits_response.json() if commits_response.status_code == 200 else []
            
            # Get closed issues
            issues_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
            issues_response = await client.get(
                issues_url,
                headers=self.headers,
                params={"state": "closed", "since": since}
            )
            issues = issues_response.json() if issues_response.status_code == 200 else []
            
            # Get pull requests
            prs_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls"
            prs_response = await client.get(
                prs_url,
                headers=self.headers,
                params={"state": "closed"}
            )
            prs = prs_response.json() if prs_response.status_code == 200 else []
            
            # Calculate average PR merge time
            merge_times = []
            for pr in prs[:10]:  # Last 10 PRs
                if pr.get("merged_at"):
                    created = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
                    merged = datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))
                    hours = (merged - created).total_seconds() / 3600
                    merge_times.append(hours)
            
            avg_merge_time = sum(merge_times) / len(merge_times) if merge_times else 24
            
            return {
                "repo": f"{self.owner}/{self.repo}",
                "commits_last_week": len(commits),
                "issues_closed_last_week": len(issues),
                "pr_merge_time_avg_hours": round(avg_merge_time, 1),
                "velocity_trend": "stable",  # Can be calculated from historical data
                "sla_compliance": "on_track"
            }
```

#### Step 3: Update Compliance Agent

**File**: `backend/app/agents/compliance_agent.py`

```python
# Replace the mock implementation with:

from ..integrations.github_live import GitHubLiveIntegration
from ..core.config import settings

async def monitor_github_velocity(self, repo: str, sla_terms: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Track commit velocity vs SLA requirements - LIVE DATA"""
    try:
        github = GitHubLiveIntegration(
            token=settings.GITHUB_TOKEN,
            owner=settings.GITHUB_OWNER,
            repo=settings.GITHUB_REPO
        )
        return await github.get_velocity_metrics()
    except Exception as e:
        logger.error(f"GitHub API error: {e}")
        # Fallback to demo data if API fails
        return {
            "repo": repo,
            "commits_last_week": 0,
            "issues_closed_last_week": 0,
            "pr_merge_time_avg_hours": 0,
            "velocity_trend": "unknown",
            "sla_compliance": "unknown",
            "error": str(e)
        }
```

---

### Phase 2: Timesheet Integration (Live Hours Tracking)

#### Option A: Integrate with Harvest

```python
"""
Harvest Timesheet Integration
"""
import httpx

class HarvestIntegration:
    def __init__(self, account_id: str, token: str):
        self.account_id = account_id
        self.token = token
        self.base_url = "https://api.harvestapp.com/v2"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Harvest-Account-ID": account_id,
            "User-Agent": "SOW Sentinel"
        }
    
    async def get_project_hours(self, project_id: str, from_date: str, to_date: str) -> Dict[str, Any]:
        """Get real hours from Harvest"""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/time_entries"
            response = await client.get(
                url,
                headers=self.headers,
                params={
                    "project_id": project_id,
                    "from": from_date,
                    "to": to_date
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                total_hours = sum(entry["hours"] for entry in data.get("time_entries", []))
                return {
                    "project_id": project_id,
                    "total_hours": total_hours,
                    "entries_count": len(data.get("time_entries", [])),
                    "period": f"{from_date} to {to_date}"
                }
            
            return {"error": "Failed to fetch timesheet data"}
```

#### Option B: Integrate with Toggl

```python
"""
Toggl Timesheet Integration
"""
import httpx
import base64

class TogglIntegration:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.track.toggl.com/api/v9"
        auth_string = f"{api_token}:api_token"
        auth_bytes = base64.b64encode(auth_string.encode())
        self.headers = {
            "Authorization": f"Basic {auth_bytes.decode()}",
            "Content-Type": "application/json"
        }
    
    async def get_project_hours(self, workspace_id: str, project_id: str) -> Dict[str, Any]:
        """Get real hours from Toggl"""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/workspaces/{workspace_id}/projects/{project_id}/time_entries"
            response = await client.get(url, headers=self.headers)
            
            if response.status_code == 200:
                entries = response.json()
                total_seconds = sum(entry.get("duration", 0) for entry in entries)
                total_hours = total_seconds / 3600
                
                return {
                    "project_id": project_id,
                    "total_hours": round(total_hours, 2),
                    "entries_count": len(entries)
                }
            
            return {"error": "Failed to fetch Toggl data"}
```

#### Step 3: Update Compliance Agent

```python
async def track_timesheet_burn(self, project_id: str, contract_hours: int) -> Dict[str, Any]:
    """Monitor hours burned vs contract allocation - LIVE DATA"""
    try:
        # Choose your timesheet system
        if settings.TIMESHEET_PROVIDER == "harvest":
            timesheet = HarvestIntegration(
                account_id=settings.HARVEST_ACCOUNT_ID,
                token=settings.HARVEST_TOKEN
            )
            data = await timesheet.get_project_hours(
                project_id,
                from_date="2024-01-01",
                to_date=datetime.utcnow().strftime("%Y-%m-%d")
            )
            hours_burned = data.get("total_hours", 0)
        
        elif settings.TIMESHEET_PROVIDER == "toggl":
            timesheet = TogglIntegration(token=settings.TOGGL_API_TOKEN)
            data = await timesheet.get_project_hours(
                workspace_id=settings.TOGGL_WORKSPACE_ID,
                project_id=project_id
            )
            hours_burned = data.get("total_hours", 0)
        
        else:
            # Fallback to demo calculation
            hours_burned = int(contract_hours * 0.75)
        
        hours_remaining = contract_hours - hours_burned
        burn_rate_per_week = 40  # Can be calculated from historical data
        weeks_remaining = hours_remaining / burn_rate_per_week if burn_rate_per_week > 0 else 0
        
        return {
            "project_id": project_id,
            "contract_hours": contract_hours,
            "hours_burned": hours_burned,
            "hours_remaining": hours_remaining,
            "burn_rate_per_week": burn_rate_per_week,
            "weeks_remaining": round(weeks_remaining, 1),
            "burn_percentage": round((hours_burned / contract_hours * 100), 1),
            "status": "on_track" if hours_remaining > 0 else "overrun",
            "data_source": "live"
        }
    except Exception as e:
        logger.error(f"Timesheet integration error: {e}")
        # Fallback to demo data
        return {
            "project_id": project_id,
            "contract_hours": contract_hours,
            "hours_burned": int(contract_hours * 0.75),
            "data_source": "demo",
            "error": str(e)
        }
```

---

### Phase 3: PagerDuty Integration (Live Uptime & Incidents)

```python
"""
PagerDuty Integration
"""
import httpx

class PagerDutyIntegration:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.pagerduty.com"
        self.headers = {
            "Authorization": f"Token token={api_token}",
            "Accept": "application/vnd.pagerduty+json;version=2"
        }
    
    async def get_service_metrics(self, service_id: str, days: int = 30) -> Dict[str, Any]:
        """Get real uptime and incident metrics"""
        async with httpx.AsyncClient() as client:
            # Get incidents
            since = (datetime.utcnow() - timedelta(days=days)).isoformat()
            url = f"{self.base_url}/incidents"
            response = await client.get(
                url,
                headers=self.headers,
                params={
                    "service_ids[]": service_id,
                    "since": since
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                incidents = data.get("incidents", [])
                
                # Calculate uptime
                total_minutes = days * 24 * 60
                downtime_minutes = sum(
                    self._calculate_incident_duration(inc)
                    for inc in incidents
                )
                uptime_percentage = ((total_minutes - downtime_minutes) / total_minutes) * 100
                
                return {
                    "service_id": service_id,
                    "uptime_percentage": round(uptime_percentage, 2),
                    "incidents_count": len(incidents),
                    "total_downtime_minutes": downtime_minutes,
                    "period_days": days,
                    "data_source": "live"
                }
            
            return {"error": "Failed to fetch PagerDuty data"}
    
    def _calculate_incident_duration(self, incident: Dict) -> int:
        """Calculate incident duration in minutes"""
        if incident.get("resolved_at"):
            created = datetime.fromisoformat(incident["created_at"].replace("Z", "+00:00"))
            resolved = datetime.fromisoformat(incident["resolved_at"].replace("Z", "+00:00"))
            return int((resolved - created).total_seconds() / 60)
        return 0
```

---

### Phase 4: Auto-Refresh Dashboard (WebSockets)

#### Backend: Add WebSocket Support

```python
"""
WebSocket endpoint for real-time updates
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@router.websocket("/ws/monitoring/{sow_id}")
async def websocket_endpoint(websocket: WebSocket, sow_id: str):
    await manager.connect(websocket)
    try:
        while True:
            # Send updates every 30 seconds
            await asyncio.sleep(30)
            
            # Fetch fresh data
            dashboard_data = await get_live_dashboard_data(sow_id)
            
            # Broadcast to client
            await websocket.send_json({
                "type": "dashboard_update",
                "data": dashboard_data
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

#### Frontend: Connect to WebSocket

```typescript
// In LiveMonitoring.tsx

useEffect(() => {
  if (!selectedSowId) return;
  
  // Connect to WebSocket
  const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/monitoring/${selectedSowId}`);
  
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'dashboard_update') {
      setDashboardData(message.data);
      toast.info('Dashboard updated with live data');
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  return () => {
    ws.close();
  };
}, [selectedSowId]);
```

---

## 🔧 Configuration Steps

### 1. Update .env File

```bash
# GitHub Integration
GITHUB_TOKEN=ghp_your_token_here
GITHUB_OWNER=your-org
GITHUB_REPO=your-repo

# Timesheet Integration (Choose one)
TIMESHEET_PROVIDER=harvest  # or toggl
HARVEST_ACCOUNT_ID=your_account_id
HARVEST_TOKEN=your_harvest_token
# OR
TOGGL_API_TOKEN=your_toggl_token
TOGGL_WORKSPACE_ID=your_workspace_id

# PagerDuty Integration
PAGERDUTY_API_TOKEN=your_pagerduty_token
PAGERDUTY_SERVICE_ID=your_service_id

# Refresh Intervals (seconds)
MONITORING_REFRESH_INTERVAL=30
GITHUB_SYNC_INTERVAL=300
TIMESHEET_SYNC_INTERVAL=600
```

### 2. Install Additional Dependencies

```bash
cd backend
pip install websockets python-socketio
```

### 3. Update Frontend Dependencies

```bash
cd frontend
npm install socket.io-client
```

---

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     External Systems                        │
├─────────────────────────────────────────────────────────────┤
│  GitHub API  │  Harvest/Toggl  │  PagerDuty  │  Billing   │
└──────┬───────┴────────┬─────────┴──────┬──────┴────────┬────┘
       │                │                 │               │
       ▼                ▼                 ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│              Integration Layer (Python)                     │
│  • GitHub Live    • Timesheet Live    • PagerDuty Live     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Layer                               │
│  Contract │ Compliance │ Risk │ Forecast                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              WebSocket / REST API                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Frontend Dashboard                             │
│  • Real-time updates    • Live metrics    • Auto-refresh   │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Implementation Checklist

### Immediate (Week 1)
- [ ] Set up GitHub API token
- [ ] Implement GitHub live integration
- [ ] Test with real repository data
- [ ] Update compliance agent to use live data

### Short-term (Week 2-3)
- [ ] Choose timesheet provider (Harvest/Toggl)
- [ ] Set up timesheet API access
- [ ] Implement timesheet integration
- [ ] Test hours tracking with real data

### Medium-term (Week 4-6)
- [ ] Set up PagerDuty API access
- [ ] Implement uptime monitoring
- [ ] Add WebSocket support
- [ ] Implement auto-refresh

### Long-term (Week 7-8)
- [ ] Add billing system integration
- [ ] Implement historical data analysis
- [ ] Add predictive analytics
- [ ] Optimize refresh intervals

---

## 🎯 Testing Real-Time Data

### Test GitHub Integration
```bash
curl -X GET "http://localhost:8000/api/v1/monitoring/github-test" \
  -H "Authorization: Bearer your-token"
```

### Test Timesheet Integration
```bash
curl -X GET "http://localhost:8000/api/v1/monitoring/timesheet-test" \
  -H "Authorization: Bearer your-token"
```

### Monitor WebSocket Connection
```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/monitoring/SOW-001');
ws.onmessage = (e) => console.log('Update:', JSON.parse(e.data));
```

---

**Next Steps**: Start with GitHub integration (easiest) and progressively add other integrations based on your needs.