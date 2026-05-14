# Example API Responses

## Contract Upload Response

### Request
```bash
POST /api/contracts/upload
Content-Type: multipart/form-data

file: contract.pdf
```

### Response (Success)
```json
{
  "success": true,
  "contract_id": "contract_a1b2c3d4e5f6",
  "filename": "acme_corp_sow_2024.pdf",
  "message": "Contract uploaded and processed successfully",
  "data": {
    "contract_metadata": {
      "contract_id": "contract_a1b2c3d4e5f6",
      "client_name": "Acme Corporation",
      "provider_name": "TechServices Inc",
      "effective_date": "2024-01-01",
      "end_date": "2026-12-31",
      "contract_period_years": 3,
      "contract_value": 1200000.0,
      "currency": "USD"
    },
    "incident_slas": [
      {
        "priority": "P1",
        "acknowledge_minutes": 15,
        "workaround_hours": 2.0,
        "resolution_hours": 4.0,
        "rca_deadline_hours": 24,
        "availability_window": "24x7x365"
      },
      {
        "priority": "P2",
        "acknowledge_minutes": 30,
        "workaround_hours": 4.0,
        "resolution_hours": 8.0,
        "rca_deadline_hours": 48,
        "availability_window": "24x7x365"
      },
      {
        "priority": "P3",
        "acknowledge_minutes": 60,
        "workaround_hours": 8.0,
        "resolution_hours": 24.0,
        "rca_deadline_hours": 72,
        "availability_window": "Business Hours"
      },
      {
        "priority": "P4",
        "acknowledge_minutes": 240,
        "workaround_hours": null,
        "resolution_hours": 72.0,
        "rca_deadline_hours": null,
        "availability_window": "Business Hours"
      }
    ],
    "availability_slas": [
      {
        "tier": "Production",
        "target_uptime_percent": 99.9,
        "max_downtime_minutes": 43.8,
        "measurement_tool": "Datadog",
        "measurement_period": "Monthly"
      },
      {
        "tier": "Staging",
        "target_uptime_percent": 99.5,
        "max_downtime_minutes": 219.0,
        "measurement_tool": "Datadog",
        "measurement_period": "Monthly"
      }
    ],
    "quality_kpis": [
      {
        "metric": "Unit Test Coverage",
        "target_percent": 80.0,
        "target_value": null,
        "measurement_frequency": "Per Sprint"
      },
      {
        "metric": "Code Review Completion",
        "target_percent": 100.0,
        "target_value": null,
        "measurement_frequency": "Per PR"
      },
      {
        "metric": "Security Scan Pass Rate",
        "target_percent": 100.0,
        "target_value": null,
        "measurement_frequency": "Per Deployment"
      }
    ],
    "service_credits": [
      {
        "priority": "P1",
        "breach_condition": "Resolution time exceeds 4 hours",
        "credit_percent": 2.0,
        "monthly_cap_percent": 10.0,
        "calculation_method": "Per incident"
      },
      {
        "priority": "P2",
        "breach_condition": "Resolution time exceeds 8 hours",
        "credit_percent": 1.0,
        "monthly_cap_percent": 10.0,
        "calculation_method": "Per incident"
      },
      {
        "priority": null,
        "breach_condition": "Monthly uptime below 99.9%",
        "credit_percent": 5.0,
        "monthly_cap_percent": 10.0,
        "calculation_method": "Per percentage point below target"
      }
    ],
    "liability_exclusions": [
      "client_infrastructure_failure",
      "third_party_cloud_provider_outage",
      "force_majeure_events",
      "client_provided_code_defects",
      "unauthorized_system_modifications",
      "ddos_attacks_exceeding_100gbps"
    ],
    "governance_rules": [
      {
        "meeting": "Weekly Operations Review",
        "frequency": "Weekly",
        "participants": ["Client PM", "Provider PM", "Tech Lead"],
        "deliverables": ["Status Report", "Risk Register"]
      },
      {
        "meeting": "Monthly Business Review",
        "frequency": "Monthly",
        "participants": ["Client Director", "Provider Director"],
        "deliverables": ["Performance Dashboard", "Financial Summary"]
      },
      {
        "meeting": "Quarterly Strategic Review",
        "frequency": "Quarterly",
        "participants": ["Executive Sponsors"],
        "deliverables": ["Strategic Roadmap", "Budget Review"]
      }
    ],
    "escalation_matrix": [
      {
        "level": "L1",
        "trigger": "Operational issue not resolved within SLA",
        "response_sla": "Same Business Day",
        "contact_role": "Operations Manager"
      },
      {
        "level": "L2",
        "trigger": "L1 escalation not resolved within 24 hours",
        "response_sla": "4 hours",
        "contact_role": "Service Delivery Manager"
      },
      {
        "level": "L3",
        "trigger": "Critical business impact or L2 unresolved",
        "response_sla": "2 hours",
        "contact_role": "VP of Operations"
      },
      {
        "level": "L4",
        "trigger": "Executive escalation required",
        "response_sla": "1 hour",
        "contact_role": "C-Level Executive"
      }
    ],
    "additional_terms": {
      "payment_terms": "Net 30",
      "invoice_frequency": "Monthly",
      "renewal_notice_days": 90,
      "termination_notice_days": 180
    }
  }
}
```

### Response (Error - Invalid File)
```json
{
  "detail": "Failed to parse document: Unsupported file type: .xlsx. Supported types: .pdf, .docx, .doc, .txt"
}
```

### Response (Error - File Too Large)
```json
{
  "detail": "Failed to parse document: File size (15.23MB) exceeds maximum allowed size (10.00MB)"
}
```

### Response (Error - Extraction Failed)
```json
{
  "detail": "Failed to extract contract data: Extraction failed after 3 attempts: Invalid JSON: Expecting property name enclosed in double quotes"
}
```

## List Contracts Response

### Request
```bash
GET /api/contracts?limit=5&order_by=uploaded_at&descending=true
```

### Response
```json
{
  "success": true,
  "count": 5,
  "contracts": [
    {
      "contract_id": "contract_a1b2c3d4e5f6",
      "filename": "acme_corp_sow_2024.pdf",
      "uploaded_at": "2024-01-15T10:30:00Z",
      "processed_at": "2024-01-15T10:30:45Z",
      "file_size_bytes": 2458624,
      "file_type": "pdf",
      "extraction_status": "completed",
      "extracted_data": {
        "contract_metadata": {
          "client_name": "Acme Corporation",
          "provider_name": "TechServices Inc"
        }
      }
    },
    {
      "contract_id": "contract_f6e5d4c3b2a1",
      "filename": "globex_agreement.docx",
      "uploaded_at": "2024-01-14T15:20:00Z",
      "processed_at": "2024-01-14T15:20:30Z",
      "file_size_bytes": 1245678,
      "file_type": "docx",
      "extraction_status": "completed",
      "extracted_data": {
        "contract_metadata": {
          "client_name": "Globex Corporation",
          "provider_name": "TechServices Inc"
        }
      }
    }
  ]
}
```

## Get Single Contract Response

### Request
```bash
GET /api/contracts/contract_a1b2c3d4e5f6
```

### Response
```json
{
  "success": true,
  "message": "Contract retrieved successfully",
  "contract": {
    "contract_id": "contract_a1b2c3d4e5f6",
    "filename": "acme_corp_sow_2024.pdf",
    "raw_text": "SERVICE LEVEL AGREEMENT\n\nThis Service Level Agreement...",
    "uploaded_at": "2024-01-15T10:30:00Z",
    "processed_at": "2024-01-15T10:30:45Z",
    "file_size_bytes": 2458624,
    "file_type": "pdf",
    "extraction_status": "completed",
    "error_message": null,
    "extracted_data": {
      "contract_metadata": {
        "contract_id": "contract_a1b2c3d4e5f6",
        "client_name": "Acme Corporation",
        "provider_name": "TechServices Inc"
      },
      "incident_slas": [...],
      "availability_slas": [...],
      "service_credits": [...],
      "liability_exclusions": [...]
    }
  }
}
```

### Response (Not Found)
```json
{
  "detail": "Contract contract_xyz123 not found"
}
```

## Get Contracts by Client Response

### Request
```bash
GET /api/contracts/client/Acme%20Corporation
```

### Response
```json
{
  "success": true,
  "client_name": "Acme Corporation",
  "count": 3,
  "contracts": [
    {
      "contract_id": "contract_a1b2c3d4e5f6",
      "filename": "acme_corp_sow_2024.pdf",
      "uploaded_at": "2024-01-15T10:30:00Z"
    },
    {
      "contract_id": "contract_b2c3d4e5f6a1",
      "filename": "acme_corp_amendment_1.pdf",
      "uploaded_at": "2024-02-01T14:20:00Z"
    },
    {
      "contract_id": "contract_c3d4e5f6a1b2",
      "filename": "acme_corp_renewal_2025.pdf",
      "uploaded_at": "2024-03-15T09:15:00Z"
    }
  ]
}
```

## Delete Contract Response

### Request
```bash
DELETE /api/contracts/contract_a1b2c3d4e5f6
```

### Response (Success)
```json
{
  "success": true,
  "message": "Contract contract_a1b2c3d4e5f6 deleted successfully"
}
```

### Response (Not Found)
```json
{
  "detail": "Contract contract_xyz123 not found"
}
```

## Health Check Response

### Request
```bash
GET /api/contracts/health/status
```

### Response (Healthy)
```json
{
  "status": "healthy",
  "service": "Contract Intelligence",
  "firestore": "connected",
  "agent": "initialized"
}
```

### Response (Unhealthy)
```json
{
  "status": "unhealthy",
  "service": "Contract Intelligence",
  "error": "Failed to initialize Firestore client: Invalid credentials"
}
```

## Integration Examples

### Python Client
```python
import requests

# Upload contract
with open('contract.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/contracts/upload',
        files={'file': f}
    )
    
if response.status_code == 201:
    data = response.json()
    contract_id = data['contract_id']
    
    # Get contract details
    contract = requests.get(
        f'http://localhost:8000/api/contracts/{contract_id}'
    ).json()
    
    # Check P1 SLA
    p1_sla = next(
        sla for sla in contract['contract']['extracted_data']['incident_slas']
        if sla['priority'] == 'P1'
    )
    print(f"P1 Resolution SLA: {p1_sla['resolution_hours']} hours")
```

### JavaScript/TypeScript Client
```typescript
// Upload contract
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/api/contracts/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();

// Display incident SLAs
data.data.incident_slas.forEach(sla => {
  console.log(`${sla.priority}: ${sla.resolution_hours}h resolution`);
});
```

### cURL Examples
```bash
# Upload contract
curl -X POST http://localhost:8000/api/contracts/upload \
  -F "file=@contract.pdf"

# List contracts
curl http://localhost:8000/api/contracts?limit=10

# Get specific contract
curl http://localhost:8000/api/contracts/contract_a1b2c3d4e5f6

# Get contracts by client
curl http://localhost:8000/api/contracts/client/Acme%20Corporation

# Delete contract
curl -X DELETE http://localhost:8000/api/contracts/contract_a1b2c3d4e5f6

# Health check
curl http://localhost:8000/api/contracts/health/status
```

---

Made with Bob