# 🔄 Backend Server Restart Required

## Issue
The Contract Agent uses a **singleton pattern** that caches the agent instance in memory. The old instance (without the Gemini API fix) is still being used.

## Solution
**RESTART YOUR BACKEND SERVER** to pick up the code changes.

## How to Restart

### Option 1: Using Docker/Podman
```bash
# Stop containers
docker-compose down
# or
./stop.sh

# Start containers
docker-compose up -d
# or
./start.sh
```

### Option 2: Using Python directly
```bash
# Stop the running backend (Ctrl+C if running in terminal)
# Then restart:
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Force Reload (Development Only)
If you can't restart, add this to force reload:

```python
# In your API endpoint or test script
import sys
if 'app.agents.contract_agent_feature' in sys.modules:
    del sys.modules['app.agents.contract_agent_feature']
    
# Then import fresh
from app.agents.contract_agent_feature import ContractIntelligenceAgent
agent = ContractIntelligenceAgent()  # Create fresh instance
```

## Verification

After restart, test with:

```bash
curl -X POST http://localhost:8000/api/contracts/upload \
  -F "file=@backend/tests/sample_contract.txt"
```

You should see populated arrays in the response:
- `compliance_obligations.incident_slas` - should have data
- `risk_obligations.service_credits` - should have data
- `liability_obligations.liability_exclusions` - should have data

## What Was Fixed

**File**: `backend/app/agents/contract_agent_feature.py`
**Line**: 53
**Change**: Added `convert_system_message_to_human=True` to ChatGoogleGenerativeAI

This fixes the Gemini API compatibility issue where SystemMessages are no longer supported.

## Test Results (After Restart)

✅ Fresh agent instance extracts data correctly:
- 2 incident SLAs extracted
- 2 service credits extracted  
- 3 liability exclusions extracted

The categorized extraction is working - you just need to restart to use the updated code!