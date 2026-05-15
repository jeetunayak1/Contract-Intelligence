# Categorized Contract Obligation Extraction

## Overview

The Contract Intelligence Agent now extracts obligations into **three categorized buckets** to support multi-agent downstream processing:

1. **Compliance Obligations** - Operational and measurable commitments
2. **Risk Obligations** - Financial and commercial exposure
3. **Liability Obligations** - Legal attribution and constraints

## Architecture

```
UNSTRUCTURED CONTRACT
        ↓
   LLM EXTRACTION (Gemini)
        ↓
   NORMALIZED JSON
        ↓
CLASSIFIED OBLIGATIONS
        ↓
DOWNSTREAM AGENTS
```

## Categorization Logic

### Compliance Obligations
**Purpose**: Operational metrics and governance requirements

**Contains**:
- `incident_slas` - Incident response and resolution SLAs by priority (P1-P5)
- `availability_slas` - Uptime targets and downtime limits
- `quality_kpis` - Performance metrics and quality targets
- `governance_rules` - Meeting cadence and deliverables
- `escalation_rules` - Escalation matrix and procedures

**Examples**:
- "P1 incidents must be acknowledged within 15 minutes"
- "99.9% uptime target for production systems"
- "Monthly service review with executive summary"

**Consumed By**: Compliance Agent

---

### Risk Obligations
**Purpose**: Financial penalties and commercial controls

**Contains**:
- `service_credits` - SLA breach penalties and credit terms
- `financial_caps` - Aggregate limits and caps
- `commercial_penalties` - Non-SLA penalties (bug escapes, unauthorized changes)
- `revenue_controls` - Billing rules and approval requirements

**Examples**:
- "5% service credit for P1 SLA breach"
- "20% monthly service credit cap"
- "No-code-no-work rule for billable work"
- "Overtime requires prior approval"

**Consumed By**: Risk Agent

---

### Liability Obligations
**Purpose**: Legal attribution and termination rights

**Contains**:
- `liability_exclusions` - Force majeure, client-caused issues
- `client_obligations` - Client responsibilities with SLAs
- `termination_clauses` - Termination types and notice periods
- `legal_constraints` - Governing law, confidentiality, IP, indemnity

**Examples**:
- "Provider not liable for client-caused outages"
- "Client must provide access within 2 days"
- "90-day termination for convenience"
- "Liability capped at 12 months fees"

**Consumed By**: Liability Agent

---

## Data Model

### ExtractedContract Schema

```python
class ExtractedContract(BaseModel):
    contract_metadata: ContractMetadata
    compliance_obligations: ComplianceObligations
    risk_obligations: RiskObligations
    liability_obligations: LiabilityObligations
    additional_terms: Optional[Dict[str, Any]]
```

### Backward Compatibility

The model includes **property accessors** for backward compatibility:

```python
# Old way (still works)
contract.incident_slas
contract.service_credits
contract.liability_exclusions

# New way (recommended)
contract.compliance_obligations.incident_slas
contract.risk_obligations.service_credits
contract.liability_obligations.liability_exclusions
```

---

## Downstream Agent Consumption

### Compliance Agent
```python
# Access only compliance obligations
compliance_data = extracted_contract.compliance_obligations

# Process incident SLAs
for sla in compliance_data.incident_slas:
    monitor_sla_compliance(sla)

# Check governance requirements
for rule in compliance_data.governance_rules:
    schedule_meeting(rule)
```

### Risk Agent
```python
# Access only risk obligations
risk_data = extracted_contract.risk_obligations

# Calculate penalty exposure
total_exposure = 0
for credit in risk_data.service_credits:
    total_exposure += calculate_credit_risk(credit)

# Check financial caps
for cap in risk_data.financial_caps:
    enforce_cap_limit(cap)
```

### Liability Agent
```python
# Access only liability obligations
liability_data = extracted_contract.liability_obligations

# Review exclusions
for exclusion in liability_data.liability_exclusions:
    document_exclusion(exclusion)

# Track client obligations
for obligation in liability_data.client_obligations:
    monitor_client_compliance(obligation)
```

---

## Example Extraction

See `example_categorized_contract_extraction.json` for a complete example with:
- 3 incident SLA tiers (P1, P2, P3)
- 2 availability tiers (Production, Non-Production)
- 3 quality KPIs
- 2 governance meetings
- 4 escalation levels
- 3 service credit types
- 3 financial caps
- 3 commercial penalties
- 3 revenue controls
- 6 liability exclusions
- 4 client obligations
- 3 termination clauses
- 4 legal constraints

---

## Validation

All models use **Pydantic validation**:

✅ Time values normalized (minutes/hours)  
✅ Percentages as decimal numbers (99.9 not "99.9%")  
✅ Priorities normalized (P1/P2/P3/P4/P5)  
✅ Optional fields allowed as null  
✅ Strict typing enforced  

---

## LangGraph Workflow

The extraction workflow remains unchanged:

1. **Extract Node** - LLM extracts categorized JSON
2. **Validate Node** - Pydantic validates nested structure
3. **Retry Node** - Handles failures (max 3 attempts)

The validation automatically handles the nested categorized schema.

---

## Benefits

### For Multi-Agent Systems
- **Separation of Concerns**: Each agent processes only relevant obligations
- **Parallel Processing**: Agents can work independently
- **Reduced Complexity**: Agents don't need to filter irrelevant data

### For Contract Analysis
- **Better Organization**: Obligations grouped by purpose
- **Clearer Attribution**: Easy to identify who owns what
- **Risk Visibility**: Financial exposure clearly separated

### For Compliance
- **Audit Trail**: Clear categorization for compliance reporting
- **SLA Monitoring**: Operational metrics isolated from legal terms
- **Governance**: Meeting and review requirements clearly defined

---

## Migration Notes

### Existing Code
No breaking changes - backward compatibility maintained via properties.

### New Code
Use categorized structure for better organization:

```python
# Recommended approach
compliance = contract.compliance_obligations
risk = contract.risk_obligations
liability = contract.liability_obligations
```

### Database Storage
The nested structure serializes to JSON naturally:

```python
contract_doc = {
    "contract_id": "MSA-2024-001",
    "extracted_data": extracted_contract.model_dump()
}
```

---

## Future Enhancements

- [ ] Add obligation priority scoring
- [ ] Implement cross-category dependency tracking
- [ ] Add obligation change detection
- [ ] Support multi-contract obligation aggregation
- [ ] Add obligation conflict detection

---

## Made with Bob
Senior Python AI Systems Engineer