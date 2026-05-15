"""
SOW Sentinel - Cloudant document models for Statement of Work management
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import uuid


# ============================================================================
# ENUMERATIONS
# ============================================================================

class SOWStatus(str, Enum):
    """SOW status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PENDING = "pending"
    TERMINATED = "terminated"
    ON_HOLD = "on_hold"


class ObligationType(str, Enum):
    """Obligation type enumeration"""
    DELIVERABLE = "deliverable"
    MILESTONE = "milestone"
    SLA_METRIC = "sla_metric"
    RECURRING_TASK = "recurring_task"
    COMPLIANCE_REQUIREMENT = "compliance_requirement"


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ObligationStatus(str, Enum):
    """Obligation status enumeration"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    AT_RISK = "at_risk"
    COMPLETED = "completed"
    BREACHED = "breached"


class EventType(str, Enum):
    """Compliance event type enumeration"""
    DEADLINE_WARNING = "deadline_warning"
    VELOCITY_DECLINE = "velocity_decline"
    SCOPE_CREEP_DETECTED = "scope_creep_detected"
    MILESTONE_COMPLETED = "milestone_completed"
    PENALTY_TRIGGERED = "penalty_triggered"
    CHANGE_REQUEST = "change_request"


class AlertSeverity(str, Enum):
    """Alert severity enumeration"""
    CRITICAL = "critical"  # < 24 hours to penalty
    HIGH = "high"          # < 7 days, velocity declining
    MEDIUM = "medium"      # Scope creep detected
    LOW = "low"            # Informational


class ScopeCreepStatus(str, Enum):
    """Scope creep status enumeration"""
    DETECTED = "detected"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    BILLED = "billed"


# ============================================================================
# SOW DOCUMENT MODELS
# ============================================================================

def create_sow_document(
    sow_number: str,
    client_name: str,
    project_name: str,
    start_date: str,
    end_date: str,
    total_value: float,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a Statement of Work document for Cloudant
    
    Args:
        sow_number: Unique SOW identifier
        client_name: Client/customer name
        project_name: Project name
        start_date: SOW start date (ISO format)
        end_date: SOW end date (ISO format)
        total_value: Total contract value
        **kwargs: Additional fields
        
    Returns:
        SOW document dictionary
    """
    upload_suffix = kwargs.get("upload_id") or str(uuid.uuid4())[:8]
    doc = {
        "_id": kwargs.get("_id", f"SOW-{sow_number}-{upload_suffix}"),
        "type": "sow",
        "sow_number": sow_number,
        "client_name": client_name,
        "project_name": project_name,
        "start_date": start_date,
        "end_date": end_date,
        "total_value": total_value,
        "currency": kwargs.get("currency", "USD"),
        "status": kwargs.get("status", SOWStatus.ACTIVE.value),
        "file_url": kwargs.get("file_url"),
        "file_name": kwargs.get("file_name"),
        "file_size": kwargs.get("file_size"),
        "description": kwargs.get("description"),
        "obligations": kwargs.get("obligations", []),
        "sla_terms": kwargs.get("sla_terms", []),
        "vague_clauses": kwargs.get("vague_clauses", []),
        "financial_summary": kwargs.get("financial_summary", {
            "total_value": total_value,
            "total_penalties": 0,
            "penalties_avoided": 0,
            "scope_creep_value": 0,
            "margin_protected": 0
        }),
        "created_at": kwargs.get("created_at", datetime.utcnow().isoformat()),
        "updated_at": kwargs.get("updated_at", datetime.utcnow().isoformat()),
        "parsed_at": kwargs.get("parsed_at"),
        "parsed_by": kwargs.get("parsed_by", "ingestion_agent"),
        "active_agent": kwargs.get("active_agent")
    }
    
    return {k: v for k, v in doc.items() if v is not None}


def create_obligation(
    sow_id: str,
    obligation_type: str,
    description: str,
    deadline: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create an obligation (deliverable/milestone) subdocument
    
    Args:
        sow_id: Parent SOW ID
        obligation_type: Type of obligation
        description: Obligation description
        deadline: Deadline date (ISO format)
        **kwargs: Additional fields
        
    Returns:
        Obligation dictionary
    """
    return {
        "id": kwargs.get("id", str(uuid.uuid4())),
        "sow_id": sow_id,
        "type": obligation_type,
        "description": description,
        "deadline": deadline,
        "penalty_amount": kwargs.get("penalty_amount", 0),
        "penalty_frequency": kwargs.get("penalty_frequency", "per_day"),
        "risk_level": kwargs.get("risk_level", RiskLevel.MEDIUM.value),
        "status": kwargs.get("status", ObligationStatus.NOT_STARTED.value),
        "progress_percentage": kwargs.get("progress_percentage", 0),
        "mapped_to": kwargs.get("mapped_to", {}),  # GitHub/Jira mappings
        "checklist": kwargs.get("checklist", []),
        "dependencies": kwargs.get("dependencies", []),
        "created_at": kwargs.get("created_at", datetime.utcnow().isoformat()),
        "updated_at": kwargs.get("updated_at", datetime.utcnow().isoformat())
    }


def create_sla_term(
    sow_id: str,
    metric_name: str,
    target_value: float,
    unit: str,
    measurement_period: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create an SLA term subdocument
    
    Args:
        sow_id: Parent SOW ID
        metric_name: Name of the SLA metric
        target_value: Target/threshold value
        unit: Unit of measurement
        measurement_period: Measurement period
        **kwargs: Additional fields
        
    Returns:
        SLA term dictionary
    """
    return {
        "id": kwargs.get("id", str(uuid.uuid4())),
        "sow_id": sow_id,
        "metric_name": metric_name,
        "target_value": target_value,
        "unit": unit,
        "measurement_period": measurement_period,
        "penalty_amount": kwargs.get("penalty_amount", 0),
        "penalty_currency": kwargs.get("penalty_currency", "USD"),
        "current_value": kwargs.get("current_value"),
        "compliance_percentage": kwargs.get("compliance_percentage"),
        "status": kwargs.get("status", "pending"),
        "created_at": kwargs.get("created_at", datetime.utcnow().isoformat())
    }


def create_vague_clause(
    sow_id: str,
    clause_text: str,
    risk_description: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a vague clause warning subdocument
    
    Args:
        sow_id: Parent SOW ID
        clause_text: The vague clause text
        risk_description: Description of the risk
        **kwargs: Additional fields
        
    Returns:
        Vague clause dictionary
    """
    return {
        "id": kwargs.get("id", str(uuid.uuid4())),
        "sow_id": sow_id,
        "clause_text": clause_text,
        "risk_description": risk_description,
        "recommendation": kwargs.get("recommendation"),
        "severity": kwargs.get("severity", RiskLevel.MEDIUM.value),
        "detected_at": kwargs.get("detected_at", datetime.utcnow().isoformat())
    }


# ============================================================================
# COMPLIANCE EVENT MODELS
# ============================================================================

def create_compliance_event_document(
    sow_id: str,
    obligation_id: str,
    event_type: str,
    severity: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a compliance event document
    
    Args:
        sow_id: SOW ID
        obligation_id: Obligation ID
        event_type: Type of event
        severity: Event severity
        **kwargs: Additional fields
        
    Returns:
        Compliance event document
    """
    doc = {
        "_id": kwargs.get("_id", f"EVENT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"),
        "type": "compliance_event",
        "sow_id": sow_id,
        "obligation_id": obligation_id,
        "event_type": event_type,
        "severity": severity,
        "days_remaining": kwargs.get("days_remaining"),
        "current_progress": kwargs.get("current_progress"),
        "required_progress": kwargs.get("required_progress"),
        "velocity_trend": kwargs.get("velocity_trend"),
        "predicted_completion": kwargs.get("predicted_completion"),
        "penalty_exposure": kwargs.get("penalty_exposure", 0),
        "actions_taken": kwargs.get("actions_taken", []),
        "timestamp": kwargs.get("timestamp", datetime.utcnow().isoformat()),
        "created_at": kwargs.get("created_at", datetime.utcnow().isoformat())
    }
    
    return {k: v for k, v in doc.items() if v is not None}


# ============================================================================
# SCOPE CREEP MODELS
# ============================================================================

def create_scope_creep_document(
    sow_id: str,
    detected_work: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Create a scope creep detection document
    
    Args:
        sow_id: SOW ID
        detected_work: Details of out-of-scope work
        **kwargs: Additional fields
        
    Returns:
        Scope creep document
    """
    doc = {
        "_id": kwargs.get("_id", f"SCOPE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"),
        "type": "scope_creep",
        "sow_id": sow_id,
        "detected_work": detected_work,
        "sow_match": kwargs.get("sow_match"),
        "recommendation": kwargs.get("recommendation"),
        "potential_revenue": kwargs.get("potential_revenue", 0),
        "status": kwargs.get("status", ScopeCreepStatus.DETECTED.value),
        "change_request_id": kwargs.get("change_request_id"),
        "detected_at": kwargs.get("detected_at", datetime.utcnow().isoformat()),
        "created_at": kwargs.get("created_at", datetime.utcnow().isoformat())
    }
    
    return {k: v for k, v in doc.items() if v is not None}


# ============================================================================
# INTEGRATION MAPPING MODELS
# ============================================================================

def create_integration_mapping(
    sow_id: str,
    obligation_id: str,
    integration_type: str,
    external_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create an integration mapping (SOW to GitHub/Jira/Calendar)
    
    Args:
        sow_id: SOW ID
        obligation_id: Obligation ID
        integration_type: Type of integration (github, jira, calendar)
        external_id: External system ID
        **kwargs: Additional fields
        
    Returns:
        Integration mapping dictionary
    """
    return {
        "id": kwargs.get("id", str(uuid.uuid4())),
        "sow_id": sow_id,
        "obligation_id": obligation_id,
        "integration_type": integration_type,
        "external_id": external_id,
        "external_url": kwargs.get("external_url"),
        "sync_status": kwargs.get("sync_status", "active"),
        "last_synced": kwargs.get("last_synced"),
        "metadata": kwargs.get("metadata", {}),
        "created_at": kwargs.get("created_at", datetime.utcnow().isoformat())
    }


# ============================================================================
# ALERT MODELS
# ============================================================================

def create_alert_document(
    sow_id: str,
    obligation_id: str,
    alert_type: str,
    severity: str,
    title: str,
    message: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create an alert document
    
    Args:
        sow_id: SOW ID
        obligation_id: Obligation ID
        alert_type: Type of alert
        severity: Alert severity
        title: Alert title
        message: Alert message
        **kwargs: Additional fields
        
    Returns:
        Alert document
    """
    doc = {
        "_id": kwargs.get("_id", f"ALERT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"),
        "type": "alert",
        "sow_id": sow_id,
        "obligation_id": obligation_id,
        "alert_type": alert_type,
        "severity": severity,
        "title": title,
        "message": message,
        "status": kwargs.get("status", "new"),
        "penalty_amount": kwargs.get("penalty_amount"),
        "days_until_penalty": kwargs.get("days_until_penalty"),
        "recommended_actions": kwargs.get("recommended_actions", []),
        "notified_users": kwargs.get("notified_users", []),
        "notification_channels": kwargs.get("notification_channels", []),
        "created_at": kwargs.get("created_at", datetime.utcnow().isoformat()),
        "acknowledged_at": kwargs.get("acknowledged_at"),
        "resolved_at": kwargs.get("resolved_at")
    }
    
    return {k: v for k, v in doc.items() if v is not None}


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_sow_document(doc: Dict[str, Any]) -> bool:
    """Validate a SOW document"""
    required_fields = [
        "type", "sow_number", "client_name", "project_name",
        "start_date", "end_date", "total_value"
    ]
    
    for field in required_fields:
        if field not in doc or doc[field] is None:
            return False
    
    return True


def validate_obligation(obligation: Dict[str, Any]) -> bool:
    """Validate an obligation"""
    required_fields = [
        "id", "sow_id", "type", "description", "deadline"
    ]
    
    for field in required_fields:
        if field not in obligation or obligation[field] is None:
            return False
    
    return True


def validate_compliance_event(event: Dict[str, Any]) -> bool:
    """Validate a compliance event"""
    required_fields = [
        "type", "sow_id", "obligation_id", "event_type", "severity"
    ]
    
    for field in required_fields:
        if field not in event or event[field] is None:
            return False
    
    return True


# Made with Bob - SOW Sentinel