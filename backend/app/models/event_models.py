"""
Event models for autonomous compliance monitoring
Handles GitHub webhooks, incidents, and realtime events
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class IncidentPriority(str, Enum):
    """Incident priority levels"""
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    SEV1 = "SEV1"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    """Incident lifecycle status"""
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class EventSource(str, Enum):
    """Source of the incident event"""
    GITHUB = "github"
    PAGERDUTY = "pagerduty"
    JIRA = "jira"
    MANUAL = "manual"


class CrewExecutionStatus(str, Enum):
    """CrewAI execution status"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ============================================================================
# GITHUB WEBHOOK MODELS
# ============================================================================

class GitHubIssue(BaseModel):
    """GitHub issue from webhook"""
    number: int
    title: str
    body: Optional[str] = None
    state: str
    labels: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str
    updated_at: str
    html_url: Optional[str] = None


class GitHubWebhookPayload(BaseModel):
    """GitHub webhook payload"""
    action: str  # opened, edited, closed, etc.
    issue: GitHubIssue
    repository: Optional[Dict[str, Any]] = None
    sender: Optional[Dict[str, Any]] = None


# ============================================================================
# INCIDENT MODELS
# ============================================================================

class IncidentCreate(BaseModel):
    """Create new incident from event"""
    incident_id: str
    source: EventSource
    priority: str
    severity: str
    service: str
    title: str
    description: Optional[str] = None
    status: IncidentStatus = IncidentStatus.OPEN
    github_issue_number: Optional[int] = None
    affected_users: Optional[int] = None
    estimated_revenue_impact: Optional[float] = None
    labels: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Incident(IncidentCreate):
    """Full incident with analysis metadata"""
    sla_analysis_started: bool = False
    sla_analysis_completed: bool = False
    crew_execution_id: Optional[str] = None
    crew_status: Optional[CrewExecutionStatus] = None
    breach_detected: bool = False
    financial_exposure: float = 0.0
    penalty_waived: bool = False
    waiver_reason: Optional[str] = None
    resolution_started_at: Optional[datetime] = None
    resolution_completed_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# REASONING LOG MODELS
# ============================================================================

class ReasoningLogLevel(str, Enum):
    """Log level for reasoning stream"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    DEBUG = "DEBUG"


class ReasoningLog(BaseModel):
    """Single reasoning log entry"""
    log_id: str
    incident_id: str
    crew_execution_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: ReasoningLogLevel
    message: str
    agent: Optional[str] = None
    task: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# CREW EVENT MODELS
# ============================================================================

class CrewEventType(str, Enum):
    """Types of crew events"""
    CREW_STARTED = "CREW_STARTED"
    CREW_COMPLETED = "CREW_COMPLETED"
    CREW_FAILED = "CREW_FAILED"
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    AGENT_STARTED = "AGENT_STARTED"
    AGENT_COMPLETED = "AGENT_COMPLETED"
    AGENT_FAILED = "AGENT_FAILED"


class CrewEvent(BaseModel):
    """CrewAI execution event"""
    event_id: str
    crew_execution_id: str
    incident_id: str
    event_type: CrewEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_name: Optional[str] = None
    task_name: Optional[str] = None
    message: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============================================================================
# FINANCIAL EXPOSURE MODELS
# ============================================================================

class FinancialExposureSnapshot(BaseModel):
    """Point-in-time financial exposure"""
    snapshot_id: str
    incident_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_exposure: float
    waived_penalties: float
    net_exposure: float
    sla_credits_applied: float
    breach_count: int
    exposure_percentage: float  # % of monthly fee


# ============================================================================
# ALERT MODELS
# ============================================================================

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Alert(BaseModel):
    """System alert"""
    alert_id: str
    incident_id: Optional[str] = None
    severity: AlertSeverity
    title: str
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None


# ============================================================================
# REALTIME STREAM MODELS
# ============================================================================

class RealtimeEvent(BaseModel):
    """Generic realtime event for frontend streaming"""
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class IncidentStreamEvent(BaseModel):
    """Incident update for realtime stream"""
    incident_id: str
    event_type: Literal["created", "updated", "resolved"]
    incident: Incident
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# API RESPONSE MODELS
# ============================================================================

class WebhookResponse(BaseModel):
    """Response from webhook endpoint"""
    success: bool
    message: str
    incident_id: Optional[str] = None
    crew_execution_id: Optional[str] = None
    triggered_analysis: bool = False


class LiveIncidentsFeed(BaseModel):
    """Live incidents feed response"""
    total_incidents: int
    active_incidents: int
    incidents: List[Incident]
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class LiveReasoningStream(BaseModel):
    """Live reasoning logs response"""
    incident_id: str
    logs: List[ReasoningLog]
    total_logs: int
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class CrewStatusResponse(BaseModel):
    """Crew execution status"""
    crew_execution_id: str
    incident_id: str
    status: CrewExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    active_agents: List[str] = Field(default_factory=list)
    completed_tasks: List[str] = Field(default_factory=list)
    events: List[CrewEvent] = Field(default_factory=list)


# Made with Bob - Event-Driven Autonomous Compliance System