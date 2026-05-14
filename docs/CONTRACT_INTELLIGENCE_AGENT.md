# Contract Intelligence Agent

## Overview

The Contract Intelligence Agent is a production-quality MVP system that automatically extracts SLA obligations, compliance rules, and liability terms from service contracts. It uses LangGraph and Google's Gemini AI to provide structured, machine-readable contract data.

## Architecture

```
backend/app/
├── agents/
│   └── contract_agent.py          # LangGraph-based extraction agent
├── api/
│   └── contracts.py                # FastAPI endpoints
├── models/
│   └── contract_models.py          # Pydantic data models
├── prompts/
│   └── contract_extraction_prompt.py  # Extraction prompts
├── services/
│   └── firestore_service.py        # Firestore database layer
└── utils/
    └── document_parser.py          # PDF/DOCX/TXT parsing
```

## Features

### Document Processing
- **Supported Formats**: PDF, DOCX, TXT
- **Multi-method Parsing**: Uses pdfplumber and PyPDF2 for PDFs
- **Text Extraction**: Handles tables, paragraphs, and complex layouts
- **Validation**: File size and format validation

### SLA Extraction
The agent extracts:
- **Incident SLAs**: Response times by priority (P1-P5)
- **Availability SLAs**: Uptime targets and downtime limits
- **Service Credits**: Financial penalties for breaches
- **Quality KPIs**: Performance metrics and targets
- **Liability Exclusions**: Force majeure and exclusions
- **Governance Rules**: Meeting requirements
- **Escalation Matrix**: Contact procedures

### Data Normalization
- Time values → minutes/hours
- Percentages → decimal numbers
- Priorities → P1/P2/P3/P4/P5 format
- All data is machine-readable JSON

### Storage
- **Database**: Google Firestore
- **Collection**: `contracts`
- **Document Structure**:
  - contract_id
  - filename
  - raw_text
  - extracted_data
  - uploaded_at
  - file_size_bytes
  - file_type

## API Endpoints

### POST /api/contracts/upload
Upload and extract contract data.

**Request:**
```bash
curl -X POST http://localhost:8000/api/contracts/upload \
  -F "file=@contract.pdf"
```

**Response:**
```json
{
  "success": true,
  "contract_id": "contract_abc123",
  "filename": "contract.pdf",
  "data": {
    "contract_metadata": {
      "contract_id": "contract_abc123",
      "client_name": "Acme Corp",
      "provider_name": "Tech Services Inc"
    },
    "incident_slas": [
      {
        "priority": "P1",
        "acknowledge_minutes": 15,
        "resolution_hours": 4,
        "availability_window": "24x7x365"
      }
    ],
    "availability_slas": [
      {
        "tier": "Production",
        "target_uptime_percent": 99.9,
        "max_downtime_minutes": 43.8
      }
    ],
    "service_credits": [
      {
        "breach_condition": "P1 resolution exceeds 4 hours",
        "credit_percent": 2,
        "monthly_cap_percent": 10
      }
    ],
    "liability_exclusions": [
      "client_infrastructure_failure",
      "third_party_cloud_outage"
    ]
  }
}
```

### GET /api/contracts
List all contracts.

**Request:**
```bash
curl http://localhost:8000/api/contracts?limit=10
```

**Response:**
```json
{
  "success": true,
  "count": 10,
  "contracts": [...]
}
```

### GET /api/contracts/{contract_id}
Get single contract by ID.

**Request:**
```bash
curl http://localhost:8000/api/contracts/contract_abc123
```

**Response:**
```json
{
  "success": true,
  "contract": {
    "contract_id": "contract_abc123",
    "filename": "contract.pdf",
    "extracted_data": {...}
  }
}
```

### GET /api/contracts/client/{client_name}
Get contracts for specific client.

### DELETE /api/contracts/{contract_id}
Delete contract by ID.

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```env
# Google Cloud / Gemini
GCP_PROJECT_ID=your-project-id
GOOGLE_API_KEY=your-gemini-api-key
GEMINI_MODEL_ID=gemini-1.5-pro

# Firestore
FIRESTORE_DB_NAME=(default)

# File Upload
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=.pdf,.docx,.doc,.txt
```

### 3. Initialize Firestore

The system automatically creates the `contracts` collection on first use.

### 4. Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

## Usage

### Backend API

```python
import requests

# Upload contract
with open('contract.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/contracts/upload',
        files={'file': f}
    )
    
result = response.json()
print(f"Contract ID: {result['contract_id']}")
print(f"Incident SLAs: {len(result['data']['incident_slas'])}")
```

### Frontend Component

```typescript
import ContractUpload from './pages/ContractUpload';

function App() {
  return <ContractUpload />;
}
```

## Data Schema

### ExtractedContract

```typescript
{
  contract_metadata: {
    contract_id: string;
    client_name: string;
    provider_name: string;
    effective_date?: string;
    contract_period_years?: number;
  };
  
  incident_slas: Array<{
    priority: "P1" | "P2" | "P3" | "P4" | "P5";
    acknowledge_minutes?: number;
    workaround_hours?: number;
    resolution_hours?: number;
    rca_deadline_hours?: number;
    availability_window?: string;
  }>;
  
  availability_slas: Array<{
    tier: string;
    target_uptime_percent: number;
    max_downtime_minutes?: number;
    measurement_tool?: string;
  }>;
  
  service_credits: Array<{
    breach_condition: string;
    credit_percent: number;
    monthly_cap_percent?: number;
  }>;
  
  liability_exclusions: string[];
  quality_kpis: Array<any>;
  governance_rules: Array<any>;
  escalation_matrix: Array<any>;
}
```

## Future Integration

The extracted data is designed for integration with:

### Compliance Agent
```python
# Compare incident against SLA
if incident.duration_hours > sla.resolution_hours:
    if incident.root_cause not in contract.liability_exclusions:
        trigger_service_credit()
```

### Risk Agent
```python
# Calculate financial exposure
total_exposure = sum(
    credit.credit_percent * monthly_fee
    for credit in contract.service_credits
)
```

### PagerDuty Integration
```python
# Validate incident response
incident = pagerduty.get_incident(incident_id)
sla = contract.get_sla_for_priority(incident.priority)

if incident.acknowledged_at > sla.acknowledge_minutes:
    alert_sla_breach()
```

## Error Handling

The system includes comprehensive error handling:

- **File Validation**: Size and format checks
- **Parsing Errors**: Fallback methods for PDFs
- **Extraction Failures**: Retry logic with LangGraph
- **JSON Validation**: Pydantic model validation
- **Database Errors**: Firestore exception handling

## Testing

### Test Contract Upload

```bash
# Test with sample contract
curl -X POST http://localhost:8000/api/contracts/upload \
  -F "file=@test_contract.pdf"
```

### Test Extraction Quality

```python
from app.agents.contract_agent import get_contract_agent

agent = get_contract_agent()
result = await agent.extract_contract(
    contract_text="...",
    filename="test.pdf"
)

assert len(result.incident_slas) > 0
assert result.contract_metadata.client_name is not None
```

## Performance

- **Document Parsing**: < 5 seconds for 10MB PDF
- **LLM Extraction**: 10-30 seconds depending on contract size
- **Total Processing**: < 60 seconds for typical contract
- **Firestore Storage**: < 1 second

## Limitations

- Maximum file size: 10MB (configurable)
- Supported formats: PDF, DOCX, TXT only
- Requires readable text (no scanned images without OCR)
- LLM extraction accuracy depends on contract clarity

## Troubleshooting

### PDF Parsing Fails
- Ensure PDF contains selectable text
- Try converting to DOCX or TXT
- Check file is not corrupted

### Extraction Returns Empty Data
- Verify contract contains SLA information
- Check Gemini API key is valid
- Review extraction logs for errors

### Firestore Connection Fails
- Verify GCP_PROJECT_ID is correct
- Check Google Cloud credentials
- Ensure Firestore API is enabled

## License

Made with Bob for Hackathon Project

---

For questions or issues, check the logs at `backend/logs/` or contact the development team.