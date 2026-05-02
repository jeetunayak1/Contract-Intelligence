"""
SOW Sentinel - SOW Management API Endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ..agents.ingestion_agent import IngestionAgent
from ..models.sow_models import (
    create_sow_document,
    create_compliance_event_document,
    create_scope_creep_document,
    create_alert_document,
    validate_sow_document,
    SOWStatus,
    ObligationStatus,
    AlertSeverity
)

router = APIRouter(prefix="/api/v1/sow", tags=["SOW Management"])

# Initialize Ingestion Agent
ingestion_agent = IngestionAgent()


# ============================================================================
# SOW CRUD OPERATIONS
# ============================================================================

@router.post("/upload")
async def upload_sow(
    file: UploadFile = File(...),
    sow_number: str = Form(...),
    client_name: str = Form(...),
    project_name: str = Form(...)
):
    """
    Upload and parse a Statement of Work document
    
    This endpoint:
    1. Accepts PDF/DOCX file
    2. Parses with Ingestion Agent
    3. Extracts obligations, SLAs, penalties
    4. Returns structured SOW data
    """
    try:
        # Save uploaded file temporarily
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse SOW with Ingestion Agent
        sow_doc = await ingestion_agent.parse_sow_document(
            file_path=file_path,
            sow_number=sow_number,
            client_name=client_name,
            project_name=project_name
        )
        
        # Perform quick risk assessment
        risk_assessment = await ingestion_agent.quick_risk_assessment(sow_doc)
        
        # TODO: Save to Cloudant database
        # db.create_document(sow_doc)
        
        return {
            "success": True,
            "message": "SOW parsed successfully",
            "sow": sow_doc,
            "risk_assessment": risk_assessment
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse SOW: {str(e)}")


@router.get("/list")
async def list_sows(
    status: Optional[str] = None,
    client_name: Optional[str] = None,
    limit: int = 50
):
    """
    List all SOWs with optional filtering
    """
    # Demo data
    demo_sows = [
        {
            "_id": "SOW-2024-ACME-001",
            "sow_number": "2024-ACME-001",
            "client_name": "Acme Corporation",
            "project_name": "Enterprise Platform Migration",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "total_value": 500000,
            "status": "active",
            "obligations_count": 3,
            "high_risk_count": 2,
            "total_penalty_exposure": 9000,
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "_id": "SOW-2024-TECHCO-002",
            "sow_number": "2024-TECHCO-002",
            "client_name": "TechCo Industries",
            "project_name": "Cloud Infrastructure Setup",
            "start_date": "2024-02-01",
            "end_date": "2024-08-31",
            "total_value": 300000,
            "status": "active",
            "obligations_count": 5,
            "high_risk_count": 1,
            "total_penalty_exposure": 5000,
            "created_at": "2024-02-01T00:00:00Z"
        }
    ]
    
    return {
        "success": True,
        "count": len(demo_sows),
        "sows": demo_sows
    }


@router.get("/{sow_id}")
async def get_sow(sow_id: str):
    """
    Get detailed SOW information including all obligations and SLAs
    """
    # Demo data - full SOW document
    demo_sow = {
        "_id": sow_id,
        "type": "sow",
        "sow_number": "2024-ACME-001",
        "client_name": "Acme Corporation",
        "project_name": "Enterprise Platform Migration",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "total_value": 500000,
        "currency": "USD",
        "status": "active",
        "obligations": [
            {
                "id": "OBL-001",
                "type": "deliverable",
                "description": "Phase 1: Database Migration",
                "deadline": "2024-03-31",
                "penalty_amount": 5000,
                "penalty_frequency": "per_day",
                "risk_level": "critical",
                "status": "in_progress",
                "progress_percentage": 75,
                "mapped_to": {
                    "github_project": "acme-migration",
                    "jira_epic": "ACME-123"
                }
            },
            {
                "id": "OBL-002",
                "type": "deliverable",
                "description": "UAT Sign-off Document",
                "deadline": "2024-05-15",
                "penalty_amount": 1000,
                "penalty_frequency": "per_day",
                "risk_level": "high",
                "status": "at_risk",
                "progress_percentage": 60,
                "mapped_to": {}
            }
        ],
        "sla_terms": [
            {
                "id": "SLA-001",
                "metric_name": "Incident Response Time",
                "target_value": 4,
                "unit": "hours",
                "measurement_period": "monthly",
                "penalty_amount": 1000,
                "current_value": 3.5,
                "compliance_percentage": 95,
                "status": "compliant"
            }
        ],
        "vague_clauses": [
            {
                "id": "VC-001",
                "clause_text": "Reasonable efforts for performance optimization",
                "risk_description": "Undefined success criteria",
                "recommendation": "Request specific performance benchmarks",
                "severity": "medium"
            }
        ],
        "financial_summary": {
            "total_penalties_at_risk": 9000,
            "penalties_avoided": 2000,
            "scope_creep_value": 15000,
            "margin_protected": 17000,
            "high_risk_obligations": 2
        }
    }
    
    return {
        "success": True,
        "sow": demo_sow
    }


# ============================================================================
# RISK & COMPLIANCE ENDPOINTS
# ============================================================================

@router.get("/{sow_id}/risk-report")
async def get_risk_report(sow_id: str):
    """
    Get comprehensive risk report for a SOW
    
    This is the DEMO STARTER - the "wow" moment!
    Shows penalties, deadlines, and financial exposure
    """
    # Demo data - Risk Report
    risk_report = {
        "sow_id": sow_id,
        "sow_number": "2024-ACME-001",
        "client_name": "Acme Corporation",
        "project_name": "Enterprise Platform Migration",
        "overall_risk_score": 75,
        "overall_risk_level": "high",
        "critical_alerts": [
            {
                "id": "ALERT-001",
                "title": "UAT Sign-off Due in 48 Hours",
                "message": "If you don't deliver the UAT sign-off by Friday, you lose $1,000 per day",
                "severity": "critical",
                "penalty_amount": 1000,
                "days_until_penalty": 2,
                "hours_until_penalty": 48,
                "obligation": {
                    "id": "OBL-002",
                    "description": "UAT Sign-off Document",
                    "deadline": "2024-05-15",
                    "current_progress": 60,
                    "blockers": [
                        "Security audit pending",
                        "Client feedback not received",
                        "Final testing incomplete"
                    ]
                },
                "recommended_actions": [
                    "Schedule emergency review meeting",
                    "Escalate to project manager",
                    "Request deadline extension",
                    "Allocate additional resources"
                ]
            }
        ],
        "high_risk_obligations": [
            {
                "id": "OBL-001",
                "description": "Phase 1: Database Migration",
                "deadline": "2024-03-31",
                "days_remaining": 15,
                "penalty_amount": 5000,
                "current_progress": 75,
                "velocity_trend": "declining",
                "predicted_completion": "2024-04-05",
                "risk_level": "high"
            }
        ],
        "scope_creep_detected": [
            {
                "id": "SCOPE-001",
                "description": "Advanced Analytics Dashboard",
                "hours_spent": 40,
                "cost": 10000,
                "sow_match": None,
                "recommendation": "Create Change Request CR-2024-05",
                "potential_revenue": 15000
            }
        ],
        "financial_summary": {
            "total_penalty_exposure": 9000,
            "immediate_risk": 1000,
            "penalties_avoided_ytd": 2000,
            "scope_creep_value": 15000,
            "potential_recovery": 15000
        },
        "sla_status": {
            "compliant": 2,
            "at_risk": 1,
            "breached": 0,
            "compliance_rate": 95
        }
    }
    
    return {
        "success": True,
        "risk_report": risk_report,
        "generated_at": datetime.utcnow().isoformat()
    }


@router.get("/{sow_id}/penalty-countdown")
async def get_penalty_countdown(sow_id: str):
    """
    Get real-time penalty countdown for all obligations
    """
    countdowns = [
        {
            "obligation_id": "OBL-002",
            "description": "UAT Sign-off Document",
            "deadline": "2024-05-15T23:59:59Z",
            "days_remaining": 2,
            "hours_remaining": 48,
            "minutes_remaining": 2880,
            "penalty_amount": 1000,
            "penalty_frequency": "per_day",
            "status": "critical",
            "message": "48 hours until $1,000/day penalty"
        },
        {
            "obligation_id": "OBL-001",
            "description": "Phase 1: Database Migration",
            "deadline": "2024-03-31T23:59:59Z",
            "days_remaining": 15,
            "hours_remaining": 360,
            "minutes_remaining": 21600,
            "penalty_amount": 5000,
            "penalty_frequency": "per_day",
            "status": "warning",
            "message": "15 days until $5,000/day penalty"
        }
    ]
    
    return {
        "success": True,
        "countdowns": countdowns
    }


@router.get("/{sow_id}/margin-leakage")
async def get_margin_leakage(sow_id: str):
    """
    Detect and report scope creep / margin leakage
    """
    leakage_report = {
        "sow_id": sow_id,
        "total_unbilled_hours": 65,
        "total_unbilled_value": 16250,
        "scope_creep_items": [
            {
                "id": "SCOPE-001",
                "description": "Advanced Analytics Dashboard",
                "hours_spent": 40,
                "cost": 10000,
                "team_members": ["Developer A", "Developer B"],
                "github_commits": 45,
                "jira_tickets": ["ACME-789", "ACME-790"],
                "detected_date": "2024-04-15",
                "status": "detected",
                "recommendation": "Create Change Request for $15,000"
            },
            {
                "id": "SCOPE-002",
                "description": "Additional Security Features",
                "hours_spent": 25,
                "cost": 6250,
                "team_members": ["Security Engineer"],
                "github_commits": 18,
                "jira_tickets": ["ACME-800"],
                "detected_date": "2024-04-20",
                "status": "detected",
                "recommendation": "Bill as additional security enhancement"
            }
        ],
        "potential_recovery": 16250,
        "margin_impact": -3.25  # percentage
    }
    
    return {
        "success": True,
        "leakage_report": leakage_report
    }


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/dashboard/summary")
async def get_dashboard_summary():
    """
    Get summary data for Loss Prevention Dashboard
    """
    summary = {
        "active_sows": 5,
        "total_obligations": 23,
        "at_risk_obligations": 4,
        "critical_alerts": 2,
        "total_penalty_exposure": 45000,
        "immediate_risk": 6000,
        "penalties_avoided_ytd": 12000,
        "scope_creep_detected": 3,
        "potential_revenue_recovery": 35000,
        "overall_compliance_rate": 92,
        "sla_status": {
            "compliant": 18,
            "at_risk": 3,
            "breached": 2
        }
    }
    
    return {
        "success": True,
        "summary": summary,
        "generated_at": datetime.utcnow().isoformat()
    }


# Made with Bob - SOW Sentinel