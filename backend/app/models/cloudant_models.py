"""
Cloudant document models for Contract Intelligence System
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from enum import Enum
import uuid


class ContractStatus(str, Enum):
    """Contract status enumeration"""
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"
    TERMINATED = "terminated"
    RENEWED = "renewed"


class ContractType(str, Enum):
    """Contract type enumeration"""
    SERVICE = "service"
    MAINTENANCE = "maintenance"
    SUBSCRIPTION = "subscription"
    LICENSE = "license"
    SUPPORT = "support"


class MetricType(str, Enum):
    """SLA metric type enumeration"""
    UPTIME = "uptime"
    RESPONSE_TIME = "response_time"
    RESOLUTION_TIME = "resolution_time"
    AVAILABILITY = "availability"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"


class ComplianceStatus(str, Enum):
    """Compliance status enumeration"""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    BREACHED = "breached"


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertStatus(str, Enum):
    """Alert status enumeration"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


def create_contract_document(
    contract_number: str,
    customer_name: str,
    contract_type: str,
    start_date: str,
    end_date: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a contract document for Cloudant
    
    Args:
        contract_number: Unique contract number
        customer_name: Customer name
        contract_type: Type of contract
        start_date: Contract start date (ISO format)
        end_date: Contract end date (ISO format)
        **kwargs: Additional fields
        
    Returns:
        Contract document dictionary
    """
    doc = {
        "_id": kwargs.get("_id", str(uuid.uuid4())),
        "type": "contract",
        "contract_number": contract_number,
        "customer_name": customer_name,
        "contract_type": contract_type,
        "start_date": start_date,
        "end_date": end_date,
        "renewal_date": kwargs.get("renewal_date"),
        "status": kwargs.get("status", ContractStatus.ACTIVE.value),
        "file_url": kwargs.get("file_url"),
        "file_name": kwargs.get("file_name"),
        "file_size": kwargs.get("file_size"),
        "total_value": kwargs.get("total_value"),
        "currency": kwargs.get("currency", "USD"),
        "description": kwargs.get("description"),
        "tags": kwargs.get("tags", []),
        "sla_terms": kwargs.get("sla_terms", []),
        "created_at": kwargs.get("created_at", datetime.utcnow().isoformat()),
        "updated_at": kwargs.get("updated_at", datetime.utcnow().isoformat())
    }
    
    # Remove None values
    return {k: v for k, v in doc.items() if v is not None}


def create_sla_term(
    contract_id: str,
    metric_name: str,
    metric_type: str,
    threshold_value: float,
    threshold_unit: str,
    measurement_period: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create an SLA term subdocument
    
    Args:
        contract_id: Parent contract ID
        metric_name: Name of the metric
        metric_type: Type of metric
        threshold_value: Threshold value
        threshold_unit: Unit of measurement
        measurement_period: Measurement period
        **kwargs: Additional fields
        
    Returns:
        SLA term dictionary
    """
    return {
        "id": kwargs.get("id", str(uuid.uuid4())),
        "contract_id": contract_id,
        "metric_name": metric_name,
        "metric_type": metric_type,
        "metric_description": kwargs.get("metric_description"),
        "threshold_value": threshold_value,
        "threshold_unit": threshold_unit,
        "penalty_amount": kwargs.get("penalty_amount"),
        "penalty_currency": kwargs.get("penalty_currency", "USD"),
        "penalty_description": kwargs.get("penalty_description"),
        "measurement_period": measurement_period,
        "created_at": kwargs.get("created_at", datetime.utcnow().isoformat())
    }


def create_compliance_metric_document(
    contract_id: str,
    sla_term_id: str,
    measurement_date: str,
    actual_value: float,
    threshold_value: float,
    compliance_status: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a compliance metric document
    
    Args:
        contract_id: Contract ID
        sla_term_id: SLA term ID
        measurement_date: Date of measurement
        actual_value: Actual measured value
        threshold_value: Threshold value
        compliance_status: Compliance status
        **kwargs: Additional fields
        
    Returns:
        Compliance metric document
    """
    doc = {
        "_id": kwargs.get("_id", str(uuid.uuid4())),
        "type": "compliance_metric",
        "contract_id": contract_id,
        "sla_term_id": sla_term_id,
        "measurement_date": measurement_date,
        "actual_value": actual_value,
        "threshold_value": threshold_value,
        "compliance_status": compliance_status,
        "deviation_percentage": kwargs.get("deviation_percentage"),
        "created_at": kwargs.get("created_at", datetime.utcnow().isoformat())
    }
    
    return {k: v for k, v in doc.items() if v is not None}


def create_risk_assessment_document(
    contract_id: str,
    risk_type: str,
    risk_level: str,
    financial_impact: float,
    probability_score: float,
    description: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a risk assessment document
    
    Args:
        contract_id: Contract ID
        risk_type: Type of risk
        risk_level: Risk severity level
        financial_impact: Financial impact amount
        probability_score: Probability score (0-1)
        description: Risk description
        **kwargs: Additional fields
        
    Returns:
        Risk assessment document
    """
    doc = {
        "_id": kwargs.get("_id", str(uuid.uuid4())),
        "type": "risk_assessment",
        "contract_id": contract_id,
        "risk_type": risk_type,
        "risk_level": risk_level,
        "financial_impact": financial_impact,
        "probability_score": probability_score,
        "description": description,
        "recommendations": kwargs.get("recommendations"),
        "assessed_at": kwargs.get("assessed_at", datetime.utcnow().isoformat()),
        "created_at": kwargs.get("created_at", datetime.utcnow().isoformat())
    }
    
    return {k: v for k, v in doc.items() if v is not None}


def create_alert_document(
    contract_id: str,
    alert_type: str,
    severity: str,
    title: str,
    message: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create an alert document
    
    Args:
        contract_id: Contract ID
        alert_type: Type of alert
        severity: Alert severity
        title: Alert title
        message: Alert message
        **kwargs: Additional fields
        
    Returns:
        Alert document
    """
    doc = {
        "_id": kwargs.get("_id", str(uuid.uuid4())),
        "type": "alert",
        "contract_id": contract_id,
        "risk_assessment_id": kwargs.get("risk_assessment_id"),
        "alert_type": alert_type,
        "severity": severity,
        "title": title,
        "message": message,
        "status": kwargs.get("status", AlertStatus.NEW.value),
        "notified_users": kwargs.get("notified_users", []),
        "created_at": kwargs.get("created_at", datetime.utcnow().isoformat()),
        "acknowledged_at": kwargs.get("acknowledged_at"),
        "resolved_at": kwargs.get("resolved_at")
    }
    
    return {k: v for k, v in doc.items() if v is not None}


def validate_contract_document(doc: Dict[str, Any]) -> bool:
    """
    Validate a contract document
    
    Args:
        doc: Contract document
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        "type", "contract_number", "customer_name", 
        "contract_type", "start_date", "end_date"
    ]
    
    for field in required_fields:
        if field not in doc or doc[field] is None:
            return False
    
    return True


def validate_sla_term(term: Dict[str, Any]) -> bool:
    """
    Validate an SLA term
    
    Args:
        term: SLA term dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        "metric_name", "metric_type", "threshold_value",
        "threshold_unit", "measurement_period"
    ]
    
    for field in required_fields:
        if field not in term or term[field] is None:
            return False
    
    return True

# Made with Bob
