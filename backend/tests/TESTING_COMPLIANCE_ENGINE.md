# Testing the Deterministic Compliance Engine

## Problem

The error shows: `Contract contract_6b65228aeb64 not found in database`

This means you need to upload a contract first before testing compliance analysis.

## Step-by-Step Testing Guide

### Step 1: Upload a Contract

1. Go to **Contract Intelligence** page in the UI
2. Click **Upload Contract** button
3. Upload a contract PDF/DOCX file (e.g., `backend/tests/sample_contract.txt`)
4. Wait for extraction to complete
5. **Note the contract_id** from the response (e.g., `contract_abc123`)

### Step 2: Test Deterministic Breach Detection

#### Option A: Using the API directly

```bash
# Replace CONTRACT_ID with your actual contract ID
curl -X POST "http://localhost:8000/api/compliance/analyze/breaches?contract_id=CONTRACT_ID&monthly_fee=100000"
```

#### Option B: Using Python

```python
import requests

# Replace with your actual contract ID
contract_id = "contract_abc123"

response = requests.post(
    f"http://localhost:8000/api/compliance/analyze/breaches",
    params={
        "contract_id": contract_id,
        "monthly_fee": 100000.0
    }
)

report = response.json()
print(f"Status: {report['overall_status']}")
print(f"Total Breaches: {report['breach_summary']['total_breaches']}")
print(f"Critical: {report['breach_summary']['critical_breaches']}")

for breach in report['breaches']:
    print(f"\n- {breach['summary']}")
    print(f"  Severity: {breach['severity']}")
    print(f"  Type: {breach['breach_type']}")
```

#### Option C: Using the War Room (Current Flow)

The War Room is currently using the OLD compliance flow. To use the NEW deterministic engine:

1. **First, upload a contract** via Contract Intelligence page
2. **Get the contract_id** from the uploaded contract
3. **Update the War Room** to use the new endpoint

### Step 3: Verify the Output

The deterministic engine should return:

```json
{
  "report_id": "REPORT-XXXXXXXX",
  "generated_at": "2026-05-15T19:00:00.000Z",
  "contract_id": "your_contract_id",
  "overall_status": "BREACH" or "COMPLIANT",
  "breach_summary": {
    "total_breaches": 5,
    "critical_breaches": 1,
    "high_breaches": 2,
    "medium_breaches": 2,
    "low_breaches": 0
  },
  "breaches": [
    {
      "breach_id": "BREACH-XXXXXXXX",
      "obligation_id": "OBL-P1-RESOLUTION",
      "sla_id": "SLA-P1-001",
      "breach_type": "incident_breach",
      "severity": "critical",
      "metrics": {
        "resolution_actual_hours": 5.5,
        "resolution_required_hours": 4.0
      },
      "delta": {
        "resolution_delta_hours": 1.5
      },
      "summary": "P1 resolution exceeded SLA target by 1.5 hours"
    }
  ],
  "total_slas_checked": 12,
  "total_incidents_analyzed": 8
}
```

## Quick Test Script

Create `backend/test_compliance_engine.py`:

```python
import asyncio
import sys
sys.path.insert(0, '/Users/shubhamkumar/Documents/Contract-Intelligence/backend')

from app.agents.compliance_agent_feature import get_compliance_agent

async def test_compliance_engine():
    # Replace with your actual contract ID
    contract_id = "contract_abc123"  # GET THIS FROM UPLOADED CONTRACT
    
    print(f"Testing compliance engine for contract: {contract_id}")
    
    agent = get_compliance_agent()
    report = await agent.analyze_with_engine(
        contract_id=contract_id,
        monthly_fee=100000.0
    )
    
    print(f"\n✅ Analysis Complete!")
    print(f"Status: {report.overall_status}")
    print(f"Total Breaches: {report.breach_summary.total_breaches}")
    print(f"Critical: {report.breach_summary.critical_breaches}")
    print(f"High: {report.breach_summary.high_breaches}")
    print(f"Medium: {report.breach_summary.medium_breaches}")
    
    print(f"\n📊 Breaches:")
    for breach in report.breaches:
        print(f"\n- {breach.summary}")
        print(f"  ID: {breach.breach_id}")
        print(f"  Severity: {breach.severity}")
        print(f"  Type: {breach.breach_type}")
        if breach.delta.resolution_delta_hours:
            print(f"  Delta: {breach.delta.resolution_delta_hours} hours")

if __name__ == "__main__":
    asyncio.run(test_compliance_engine())
```

Run it:
```bash
cd backend
python test_compliance_engine.py
```

## Expected Output

```
Testing compliance engine for contract: contract_abc123

✅ Analysis Complete!
Status: BREACH
Total Breaches: 5
Critical: 1
High: 2
Medium: 2

📊 Breaches:

- P1 resolution exceeded SLA target by 1.5 hours
  ID: BREACH-001A2B3C
  Severity: critical
  Type: incident_breach
  Delta: 1.5 hours

- P2 acknowledgment exceeded SLA target by 5 minutes
  ID: BREACH-002D4E5F
  Severity: high
  Type: incident_breach

- Uptime fell below SLA threshold by 0.20%
  ID: BREACH-003G6H7I
  Severity: high
  Type: uptime_breach

- Unit Test Coverage below target by 8.0%
  ID: BREACH-004J8K9L
  Severity: medium
  Type: kpi_breach

- Code Review Coverage below target by 3.0%
  ID: BREACH-005M0N1O
  Severity: medium
  Type: kpi_breach
```

## Troubleshooting

### Error: "Contract not found"
- **Solution**: Upload a contract first via Contract Intelligence page
- Get the contract_id from the response
- Use that contract_id in your test

### Error: "No incidents found"
- **Solution**: The system uses mock PagerDuty data from `backend/app/mock_data/pagerduty_incidents.json`
- Make sure this file exists and has incident data

### Error: "No SLAs found"
- **Solution**: Make sure your uploaded contract has extracted SLAs
- Check the contract extraction was successful
- Verify `compliance_obligations.incident_slas` is not empty

## Differences: Old vs New

### OLD Compliance Flow (AI-Based)
- Uses `analyze_compliance()` method
- AI reasoning with Gemini
- Financial exposure calculations
- Liability exclusion interpretation
- Returns `ComplianceReport` model

### NEW Compliance Flow (Deterministic)
- Uses `analyze_with_engine()` method
- Pure mechanical comparison
- NO AI reasoning
- NO financial calculations
- Returns `ComplianceBreachReport` model

## Next Steps

1. Upload a contract to get a valid contract_id
2. Run the test script with your contract_id
3. Verify the breach report output
4. Optionally: Update War Room to use new endpoint

Made with Bob 🚀