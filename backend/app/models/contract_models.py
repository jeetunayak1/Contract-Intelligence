"""
Pydantic models for Contract Intelligence Agent
Strict schemas for SLA extraction and validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class PriorityLevel(str, Enum):
    """Incident priority levels"""
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"


class AvailabilityWindow(str, Enum):
    """Service availability windows"""
    BUSINESS_HOURS = "Business Hours"
    EXTENDED_HOURS = "Extended Hours"
    TWENTY_FOUR_SEVEN = "24x7x365"
    CUSTOM = "Custom"


class IncidentSLA(BaseModel):
    """Incident response and resolution SLA"""
    priority: PriorityLevel
    acknowledge_minutes: Optional[int] = Field(None, description="Time to acknowledge incident in minutes")
    workaround_hours: Optional[float] = Field(None, description="Time to provide workaround in hours")
    resolution_hours: Optional[float] = Field(None, description="Time to resolve incident in hours")
    rca_deadline_hours: Optional[int] = Field(None, description="Root cause analysis deadline in hours")
    availability_window: Optional[str] = Field(None, description="When SLA applies (e.g., 24x7x365)")
    
    @field_validator('acknowledge_minutes', 'rca_deadline_hours')
    @classmethod
    def validate_positive_int(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be positive')
        return v
    
    @field_validator('workaround_hours', 'resolution_hours')
    @classmethod
    def validate_positive_float(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be positive')
        return v


class AvailabilitySLA(BaseModel):
    """System availability and uptime SLA"""
    tier: str = Field(..., description="Service tier (e.g., Tier 1, Production)")
    target_uptime_percent: Optional[float] = Field(None, description="Target uptime percentage (e.g., 99.9)")
    max_downtime_minutes: Optional[float] = Field(None, description="Maximum allowed downtime per month")
    measurement_tool: Optional[str] = Field(None, description="Tool used to measure uptime")
    measurement_period: Optional[str] = Field(None, description="Measurement period (e.g., Monthly)")
    
    @field_validator('target_uptime_percent')
    @classmethod
    def validate_uptime(cls, v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError('Uptime must be between 0 and 100')
        return v


class QualityKPI(BaseModel):
    """Quality and performance KPI"""
    metric: str = Field(..., description="KPI metric name")
    target_percent: Optional[float] = Field(None, description="Target percentage")
    target_value: Optional[str] = Field(None, description="Target value (if not percentage)")
    measurement_frequency: Optional[str] = Field(None, description="How often measured")
    
    @field_validator('target_percent')
    @classmethod
    def validate_percent(cls, v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError('Percentage must be between 0 and 100')
        return v
    
    @field_validator('target_value', mode='before')
    @classmethod
    def validate_target_value(cls, v):
        # Convert int/float to string if needed
        if v is not None and not isinstance(v, str):
            return str(v)
        return v


class ServiceCredit(BaseModel):
    """Service credit for SLA breach"""
    priority: Optional[str] = Field(None, description="Incident priority or tier if applicable")
    breach_condition: str = Field(..., description="Condition that triggers credit")
    credit_percent: float = Field(..., description="Credit percentage of monthly fee")
    monthly_cap_percent: Optional[float] = Field(None, description="Maximum credit per month")
    calculation_method: Optional[str] = Field(None, description="How credit is calculated")
    
    @field_validator('credit_percent', 'monthly_cap_percent')
    @classmethod
    def validate_percent(cls, v):
        if v is not None and v < 0:
            raise ValueError('Percentage must be positive')
        return v


class GovernanceRule(BaseModel):
    """Governance and meeting requirements"""
    meeting: str = Field(..., description="Meeting name")
    frequency: str = Field(..., description="Meeting frequency")
    participants: Optional[List[str]] = Field(None, description="Required participants")
    deliverables: Optional[List[str]] = Field(None, description="Meeting deliverables")


class EscalationLevel(BaseModel):
    """Escalation matrix entry"""
    level: str = Field(..., description="Escalation level (e.g., L1, L2)")
    trigger: str = Field(..., description="What triggers this escalation")
    response_sla: Optional[str] = Field(None, description="Response time for this level")
    contact_role: Optional[str] = Field(None, description="Who to contact")


class ContractMetadata(BaseModel):
    """Contract metadata and basic information"""
    contract_id: Optional[str] = Field(None, description="Unique contract identifier")
    client_name: Optional[str] = Field(None, description="Client organization name")
    provider_name: Optional[str] = Field(None, description="Service provider name")
    effective_date: Optional[str] = Field(None, description="Contract effective date")
    end_date: Optional[str] = Field(None, description="Contract end date")
    contract_period_years: Optional[int] = Field(None, description="Contract duration in years")
    contract_value: Optional[float] = Field(None, description="Total contract value")
    currency: Optional[str] = Field("USD", description="Currency (e.g., USD)")


class ExtractedContract(BaseModel):
    """Complete extracted contract data structure"""
    contract_metadata: ContractMetadata
    incident_slas: List[IncidentSLA] = Field(default_factory=list)
    availability_slas: List[AvailabilitySLA] = Field(default_factory=list)
    quality_kpis: List[QualityKPI] = Field(default_factory=list)
    service_credits: List[ServiceCredit] = Field(default_factory=list)
    liability_exclusions: List[str] = Field(default_factory=list)
    governance_rules: List[GovernanceRule] = Field(default_factory=list)
    escalation_matrix: List[EscalationLevel] = Field(default_factory=list)
    additional_terms: Optional[Dict[str, Any]] = Field(None, description="Any additional terms")


class ContractDocument(BaseModel):
    """Contract document stored in database"""
    contract_id: str
    filename: str
    raw_text: str
    extracted_data: ExtractedContract
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    file_size_bytes: Optional[int] = None
    file_type: Optional[str] = None
    extraction_status: str = Field(default="pending")  # pending, processing, completed, failed
    error_message: Optional[str] = None


class ContractUploadResponse(BaseModel):
    """Response for contract upload endpoint"""
    success: bool
    contract_id: str
    filename: str
    data: ExtractedContract
    message: Optional[str] = None


class ContractListResponse(BaseModel):
    """Response for listing contracts"""
    success: bool
    count: int
    contracts: List[Dict[str, Any]]


class ContractDetailResponse(BaseModel):
    """Response for single contract detail"""
    success: bool
    contract: Optional[ContractDocument] = None
    message: Optional[str] = None


# Made with Bob