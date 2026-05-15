"""
Compliance API endpoints
SLA breach detection and financial exposure analysis
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ..agents.compliance_agent_feature import get_compliance_agent
from ..services.contract_firestore import get_contract_firestore
from ..services.pagerduty_service import get_pagerduty_service
from ..services.jira_service import get_jira_service
from ..models.contract_models import ExtractedContract
from ..models.compliance_models import ComplianceRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "compliance-agent",
        "version": "1.0.0"
    }


@router.post("/analyze")
async def run_compliance_analysis(
    contract_id: str = Query(..., description="Contract ID to analyze"),
    monthly_fee: float = Query(100000.0, description="Monthly contract value")
):
    """
    Run complete compliance analysis
    
    Analyzes PagerDuty incidents and Jira metrics against contract SLAs
    """
    try:
        logger.info(f"Starting compliance analysis for contract: {contract_id}")
        
        # Get contract data
        firestore = get_contract_firestore()
        contract_doc = await firestore.get_contract_by_id(contract_id)
        
        if not contract_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Contract not found: {contract_id}"
            )
        
        # Extract contract data
        extracted_data = contract_doc.get("extracted_data")
        if not extracted_data:
            raise HTTPException(
                status_code=400,
                detail="Contract has no extracted SLA data"
            )
        
        # Convert to ExtractedContract model
        contract = ExtractedContract(**extracted_data)
        
        # Run compliance analysis
        agent = get_compliance_agent()
        report = await agent.analyze_compliance(contract, monthly_fee)
        
        logger.info(f"Compliance analysis completed: {report.report_id}")
        
        return report.model_dump()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compliance analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run compliance analysis: {str(e)}"
        )


@router.get("/incidents")
async def get_incidents():
    """
    Get all PagerDuty incidents
    
    Returns list of incidents with operational data
    """
    try:
        service = get_pagerduty_service()
        incidents = service.load_incidents()
        
        return {
            "success": True,
            "count": len(incidents),
            "incidents": [inc.model_dump() for inc in incidents]
        }
        
    except Exception as e:
        logger.error(f"Failed to load incidents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load incidents: {str(e)}"
        )


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get specific incident by ID"""
    try:
        service = get_pagerduty_service()
        incident = service.get_incident_by_id(incident_id)
        
        if not incident:
            raise HTTPException(
                status_code=404,
                detail=f"Incident not found: {incident_id}"
            )
        
        return incident.model_dump()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get incident: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get incident: {str(e)}"
        )


@router.get("/incidents/stats")
async def get_incident_statistics():
    """Get incident statistics"""
    try:
        service = get_pagerduty_service()
        stats = service.get_incident_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/metrics")
async def get_jira_metrics():
    """
    Get Jira operational metrics
    
    Returns quality, performance, and delivery metrics
    """
    try:
        service = get_jira_service()
        metrics = service.load_metrics()
        
        return {
            "success": True,
            "metrics": metrics.model_dump()
        }
        
    except Exception as e:
        logger.error(f"Failed to load metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load metrics: {str(e)}"
        )


@router.get("/metrics/summary")
async def get_metrics_summary():
    """Get summary of key metrics"""
    try:
        service = get_jira_service()
        summary = service.get_metrics_summary()
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics summary: {str(e)}"
        )


@router.get("/dashboard")
async def get_dashboard_data(
    contract_id: str = Query(..., description="Contract ID"),
    monthly_fee: float = Query(100000.0, description="Monthly contract value")
):
    """
    Get complete dashboard data
    
    Returns compliance analysis, incidents, and metrics in one call
    """
    try:
        # Get contract
        firestore = get_contract_firestore()
        contract_doc = await firestore.get_contract_by_id(contract_id)
        
        if not contract_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Contract not found: {contract_id}"
            )
        
        extracted_data = contract_doc.get("extracted_data")
        if not extracted_data:
            raise HTTPException(
                status_code=400,
                detail="Contract has no extracted SLA data"
            )
        
        contract = ExtractedContract(**extracted_data)
        
        # Run compliance analysis
        agent = get_compliance_agent()
        compliance_report = await agent.analyze_compliance(contract, monthly_fee)
        
        # Get incidents
        pagerduty = get_pagerduty_service()
        incidents = pagerduty.load_incidents()
        incident_stats = pagerduty.get_incident_statistics()
        
        # Get metrics
        jira = get_jira_service()
        metrics = jira.load_metrics()
        metrics_summary = jira.get_metrics_summary()
        
        return {
            "success": True,
            "contract_id": contract_id,
            "compliance_report": compliance_report.model_dump(),
            "incidents": {
                "total": len(incidents),
                "statistics": incident_stats,
                "recent": [inc.model_dump() for inc in incidents[:5]]
            },
            "metrics": {
                "summary": metrics_summary,
                "full": metrics.model_dump()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard data: {str(e)}"
        )


@router.get("/contracts")
async def list_contracts():
    """List all contracts available for compliance analysis"""
    try:
        firestore = get_contract_firestore()
        contracts = await firestore.get_all_contracts()
        
        # Filter to only contracts with extracted data
        valid_contracts = []
        for contract in contracts:
            if contract.get("extracted_data"):
                valid_contracts.append({
                    "contract_id": contract.get("contract_id"),
                    "filename": contract.get("filename"),
                    "processed_at": contract.get("processed_at"),
                    "provider": contract.get("extracted_data", {}).get("contract_metadata", {}).get("provider_name")
                })
        
        return {
            "success": True,
            "count": len(valid_contracts),
            "contracts": valid_contracts
        }
        
    except Exception as e:
        logger.error(f"Failed to list contracts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list contracts: {str(e)}"
        )

# Made with Bob
