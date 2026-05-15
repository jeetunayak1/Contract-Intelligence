"""
Pydantic models for Compliance Agent
SLA breach detection and financial exposure calculation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class BreachSeverity(str, Enum):
    """Breach severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


class ComplianceStatus(str, Enum):
    """Overall compliance status"""
    COMPLIANT = "COMPLIANT"
    BREACH = "BREACH"
    WARNING = "WARNING"
    WAIVED = "WAIVED"


class ReasoningStep(BaseModel):
    """AI reasoning step"""
    timestamp: str = Field(..., description="Timestamp of reasoning step")
    message: str = Field(..., description="Reasoning message")
    level: str = Field(default="INFO", description="Log level (INFO, WARNING, ERROR)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class IncidentAnalysis(BaseModel):
    """Analysis of a single incident against SLA"""
    incident_id: str
    priority: str
    service: str
    title: str
    breach_detected: bool
    sla_target_hours: Optional[float]
    actual_resolution_hours: float
    acknowledge_target_minutes: Optional[int]
    actual_acknowledge_minutes: Optional[int]
    workaround_target_hours: Optional[float]
    actual_workaround_hours: Optional[float]
    root_cause: str
    liability_exclusion_applied: bool
    exclusion_reason: Optional[str]
    financial_exposure: float
    waived_amount: float
    breach_severity: BreachSeverity
    reasoning: str
    affected_users: int


class KPIAnalysis(BaseModel):
    """Analysis of KPI against contract threshold"""
    metric: str
    target: Optional[float]
    actual: float
    breach_detected: bool
    variance_percent: float
    severity: BreachSeverity
    reasoning: str


class AvailabilityAnalysis(BaseModel):
    """Analysis of system availability against SLA"""
    tier: str
    target_uptime_percent: float
    actual_uptime_percent: float
    breach_detected: bool
    downtime_minutes: float
    max_allowed_downtime_minutes: float
    financial_exposure: float
    breach_severity: BreachSeverity


class FinancialSummary(BaseModel):
    """Financial exposure summary"""
    total_estimated_exposure: float = Field(..., description="Total potential penalties")
    total_waived_penalties: float = Field(..., description="Penalties waived due to exclusions")
    net_exposure: float = Field(..., description="Actual financial exposure")
    monthly_fee_basis: float = Field(default=100000.0, description="Monthly fee for calculations")
    exposure_percentage: float = Field(..., description="Exposure as % of monthly fee")
    incidents_with_exposure: int
    incidents_waived: int
    availability_penalties: float
    incident_penalties: float


class ComplianceReport(BaseModel):
    """Complete compliance analysis report"""
    report_id: str
    generated_at: str
    contract_id: str
    overall_status: ComplianceStatus
    breach_severity: BreachSeverity
    
    # Analysis sections
    incident_analysis: List[IncidentAnalysis] = Field(default_factory=list)
    kpi_analysis: List[KPIAnalysis] = Field(default_factory=list)
    availability_analysis: List[AvailabilityAnalysis] = Field(default_factory=list)
    
    # Financial summary
    financial_summary: FinancialSummary
    
    # AI reasoning
    reasoning_stream: List[ReasoningStep] = Field(default_factory=list)
    
    # Summary statistics
    total_incidents: int
    breached_incidents: int
    waived_incidents: int
    breached_kpis: int
    total_kpis: int


class PagerDutyIncident(BaseModel):
    """PagerDuty incident model"""
    incident_id: str
    priority: str
    service: str
    title: str
    duration_hours: float
    acknowledged_minutes: Optional[int]
    workaround_hours: Optional[float]
    root_cause: str
    affected_users: int
    status: str
    created_at: str
    resolved_at: str
    description: str


class JiraMetrics(BaseModel):
    """Jira operational metrics"""
    sprint_metrics: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    delivery_metrics: Dict[str, Any]
    customer_satisfaction: Dict[str, Any]
    resource_utilization: Dict[str, Any]
    compliance_metrics: Dict[str, Any]


class ComplianceRequest(BaseModel):
    """Request to run compliance analysis"""
    contract_id: str
    include_reasoning: bool = Field(default=True, description="Include AI reasoning stream")
    monthly_fee: float = Field(default=100000.0, description="Monthly contract value for calculations")


class LiveIncidentUpdate(BaseModel):
    """Real-time incident update for dashboard"""
    incident_id: str
    status: str
    breach_detected: bool
    financial_impact: float
    timestamp: str
    message: str

# Made with Bob
