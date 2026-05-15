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


class FinancialCap(BaseModel):
    """Financial caps and aggregate limits"""
    cap_type: str = Field(..., description="Type of cap (e.g., Aggregate Monthly Service Credit Cap)")
    cap_percent: Optional[float] = Field(None, description="Cap as percentage")
    cap_amount: Optional[float] = Field(None, description="Cap as fixed amount")
    trigger_condition: Optional[str] = Field(None, description="Condition that triggers cap")
    
    @field_validator('cap_percent')
    @classmethod
    def validate_percent(cls, v):
        if v is not None and v < 0:
            raise ValueError('Percentage must be positive')
        return v


class CommercialPenalty(BaseModel):
    """Commercial penalties and consequences"""
    trigger: str = Field(..., description="What triggers this penalty")
    consequence: str = Field(..., description="Penalty consequence")
    penalty_percent: Optional[float] = Field(None, description="Penalty as percentage")
    penalty_amount: Optional[float] = Field(None, description="Penalty as fixed amount")
    
    @field_validator('penalty_percent')
    @classmethod
    def validate_percent(cls, v):
        if v is not None and v < 0:
            raise ValueError('Percentage must be positive')
        return v


class RevenueControl(BaseModel):
    """Revenue and billing controls"""
    control: str = Field(..., description="Control name")
    description: str = Field(..., description="Control description")
    enforcement: Optional[str] = Field(None, description="How control is enforced")


class ClientObligation(BaseModel):
    """Client responsibilities and obligations"""
    obligation: str = Field(..., description="Client obligation description")
    sla_days: Optional[int] = Field(None, description="SLA timeframe in days")
    consequence: Optional[str] = Field(None, description="Consequence of non-compliance")
    
    @field_validator('sla_days')
    @classmethod
    def validate_positive_int(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be positive')
        return v


class TerminationClause(BaseModel):
    """Contract termination clauses"""
    termination_type: str = Field(..., description="Type of termination")
    notice_period_days: Optional[int] = Field(None, description="Notice period in days")
    conditions: Optional[str] = Field(None, description="Termination conditions")
    
    @field_validator('notice_period_days')
    @classmethod
    def validate_positive_int(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be positive')
        return v


class LegalConstraint(BaseModel):
    """Legal constraints and limitations"""
    type: str = Field(..., description="Constraint type (e.g., Limitation of Liability)")
    details: str = Field(..., description="Constraint details")
    exclusions: Optional[List[str]] = Field(None, description="Exclusions from constraint")


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


class ComplianceObligations(BaseModel):
    """Compliance and operational obligations"""
    incident_slas: List[IncidentSLA] = Field(default_factory=list, description="Incident response SLAs")
    availability_slas: List[AvailabilitySLA] = Field(default_factory=list, description="Uptime and availability SLAs")
    quality_kpis: List[QualityKPI] = Field(default_factory=list, description="Quality and performance KPIs")
    governance_rules: List[GovernanceRule] = Field(default_factory=list, description="Governance and meeting requirements")
    escalation_rules: List[EscalationLevel] = Field(default_factory=list, description="Escalation matrix")


class RiskObligations(BaseModel):
    """Risk and financial obligations"""
    service_credits: List[ServiceCredit] = Field(default_factory=list, description="Service credit terms")
    financial_caps: List[FinancialCap] = Field(default_factory=list, description="Financial caps and limits")
    commercial_penalties: List[CommercialPenalty] = Field(default_factory=list, description="Commercial penalties")
    revenue_controls: List[RevenueControl] = Field(default_factory=list, description="Revenue and billing controls")


class LiabilityObligations(BaseModel):
    """Liability and legal obligations"""
    liability_exclusions: List[str] = Field(default_factory=list, description="Liability exclusions")
    client_obligations: List[ClientObligation] = Field(default_factory=list, description="Client responsibilities")
    termination_clauses: List[TerminationClause] = Field(default_factory=list, description="Termination terms")
    legal_constraints: List[LegalConstraint] = Field(default_factory=list, description="Legal constraints")


class ExtractedContract(BaseModel):
    """Complete extracted contract data structure with categorized obligations"""
    contract_metadata: ContractMetadata
    compliance_obligations: ComplianceObligations = Field(default_factory=ComplianceObligations)
    risk_obligations: RiskObligations = Field(default_factory=RiskObligations)
    liability_obligations: LiabilityObligations = Field(default_factory=LiabilityObligations)
    additional_terms: Optional[Dict[str, Any]] = Field(None, description="Any additional terms")
    
    # Backward compatibility properties (deprecated - use categorized obligations)
    @property
    def incident_slas(self) -> List[IncidentSLA]:
        """Backward compatibility: access incident_slas"""
        return self.compliance_obligations.incident_slas
    
    @property
    def availability_slas(self) -> List[AvailabilitySLA]:
        """Backward compatibility: access availability_slas"""
        return self.compliance_obligations.availability_slas
    
    @property
    def quality_kpis(self) -> List[QualityKPI]:
        """Backward compatibility: access quality_kpis"""
        return self.compliance_obligations.quality_kpis
    
    @property
    def service_credits(self) -> List[ServiceCredit]:
        """Backward compatibility: access service_credits"""
        return self.risk_obligations.service_credits
    
    @property
    def liability_exclusions(self) -> List[str]:
        """Backward compatibility: access liability_exclusions"""
        return self.liability_obligations.liability_exclusions
    
    @property
    def governance_rules(self) -> List[GovernanceRule]:
        """Backward compatibility: access governance_rules"""
        return self.compliance_obligations.governance_rules
    
    @property
    def escalation_matrix(self) -> List[EscalationLevel]:
        """Backward compatibility: access escalation_matrix"""
        return self.compliance_obligations.escalation_rules


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