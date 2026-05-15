"""
Breach Models - Standardized SLA Breach Detection Schema
Pure deterministic breach detection without AI reasoning
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class BreachType(str, Enum):
    """Types of SLA breaches"""
    SLA_VIOLATION = "sla_violation"
    UPTIME_BREACH = "uptime_breach"
    INCIDENT_BREACH = "incident_breach"
    KPI_BREACH = "kpi_breach"
    GOVERNANCE_BREACH = "governance_breach"


class BreachSeverity(str, Enum):
    """Breach severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BreachMetrics(BaseModel):
    """Actual vs required metrics for a breach"""
    # Resolution metrics
    resolution_actual_hours: Optional[float] = None
    resolution_required_hours: Optional[float] = None
    
    # Acknowledgment metrics
    acknowledge_actual_minutes: Optional[int] = None
    acknowledge_required_minutes: Optional[int] = None
    
    # Workaround metrics
    workaround_actual_hours: Optional[float] = None
    workaround_required_hours: Optional[float] = None
    
    # Uptime metrics
    uptime_actual: Optional[float] = None
    uptime_required: Optional[float] = None
    downtime_minutes: Optional[float] = None
    
    # KPI metrics
    kpi_actual: Optional[float] = None
    kpi_required: Optional[float] = None
    
    # Custom metrics
    custom_metrics: Optional[Dict[str, Any]] = None


class BreachDelta(BaseModel):
    """Computed deltas from SLA thresholds"""
    resolution_delta_hours: Optional[float] = None
    acknowledge_delta_minutes: Optional[int] = None
    workaround_delta_hours: Optional[float] = None
    uptime_delta_percent: Optional[float] = None
    kpi_delta_percent: Optional[float] = None
    custom_deltas: Optional[Dict[str, float]] = None


class Breach(BaseModel):
    """Standardized breach record"""
    breach_id: str = Field(default_factory=lambda: f"BREACH-{uuid.uuid4().hex[:8].upper()}")
    obligation_id: str = Field(..., description="Maps to extracted contract obligation")
    sla_id: str = Field(..., description="Normalized SLA identifier")
    breach_type: BreachType
    breach_date: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    severity: BreachSeverity
    
    # Related incidents/issues
    github_issues: List[str] = Field(default_factory=list)
    pagerduty_incidents: List[str] = Field(default_factory=list)
    
    # Metrics
    metrics: BreachMetrics
    delta: BreachDelta
    
    # Factual summary (NO AI reasoning)
    summary: str = Field(..., description="Short factual statement of breach")
    
    # Optional context
    priority: Optional[str] = None
    service: Optional[str] = None
    affected_users: Optional[int] = None


class BreachSummary(BaseModel):
    """Summary of all breaches"""
    total_breaches: int
    critical_breaches: int
    high_breaches: int
    medium_breaches: int
    low_breaches: int


class ComplianceBreachReport(BaseModel):
    """Complete breach detection report"""
    report_id: str = Field(default_factory=lambda: f"REPORT-{uuid.uuid4().hex[:8].upper()}")
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    contract_id: str
    
    # Overall status
    overall_status: str = Field(..., description="COMPLIANT or BREACH")
    
    # Breach summary
    breach_summary: BreachSummary
    
    # All detected breaches
    breaches: List[Breach] = Field(default_factory=list)
    
    # Metadata
    total_slas_checked: int
    total_incidents_analyzed: int
    analysis_duration_seconds: Optional[float] = None


class IncidentMetrics(BaseModel):
    """Operational metrics for an incident"""
    incident_id: str
    priority: str
    service: str
    created_at: str
    resolved_at: Optional[str] = None
    acknowledged_at: Optional[str] = None
    workaround_at: Optional[str] = None
    
    # Computed durations
    resolution_hours: Optional[float] = None
    acknowledge_minutes: Optional[int] = None
    workaround_hours: Optional[float] = None
    
    # Impact
    affected_users: int = 0
    downtime_minutes: Optional[float] = None


class GitHubMetrics(BaseModel):
    """GitHub operational metrics"""
    issue_id: str
    created_at: str
    closed_at: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    
    # Computed metrics
    resolution_hours: Optional[float] = None
    is_bug: bool = False
    is_incident: bool = False
    priority: Optional[str] = None


class OperationalMetrics(BaseModel):
    """Combined operational metrics from all sources"""
    incidents: List[IncidentMetrics] = Field(default_factory=list)
    github_issues: List[GitHubMetrics] = Field(default_factory=list)
    
    # Uptime metrics
    uptime_percent: Optional[float] = None
    downtime_minutes: Optional[float] = None
    
    # Quality metrics
    unit_test_coverage: Optional[float] = None
    code_review_coverage: Optional[float] = None
    deployment_frequency: Optional[int] = None


# Made with Bob - Deterministic Breach Detection