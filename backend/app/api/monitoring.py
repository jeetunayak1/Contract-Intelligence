"""
SOW Sentinel - Live Monitoring API Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

from ..agents.contract_agent import contract_agent
from ..agents.compliance_agent import compliance_agent
from ..agents.risk_agent import risk_agent
from ..agents.forecast_agent import forecast_agent
from ..core.cloudant_db import cloudant_db
from ..services.slack_notifications import slack_service

router = APIRouter(tags=["Live Monitoring"])


@router.get("/monitoring/live-dashboard/{sow_id}")
async def get_live_dashboard(sow_id: str):
    """
    Get comprehensive live monitoring dashboard data
    
    Args:
        sow_id: SOW ID
        
    Returns:
        Complete dashboard data from all agents
    """
    try:
        # Get SOW document
        doc = await cloudant_db.get_document(sow_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"SOW not found: {sow_id}")
        
        # Contract Agent Analysis
        sla_terms = contract_agent.analyze_sla_terms(doc)
        penalty_exposure = contract_agent.calculate_penalty_exposure(sla_terms)
        scope_boundaries = contract_agent.detect_scope_boundaries(doc)
        
        # Compliance Agent Analysis
        compliance_status = await compliance_agent.compare_sla_vs_operations(sow_id, doc)
        
        # Get contract hours from financial summary (populated by populate_sla_data)
        financial_summary = doc.get("financial_summary", {})
        contract_hours = financial_summary.get("contract_hours", 1000)  # Fallback to 1000 if not populated
        
        timesheet_burn = await compliance_agent.track_timesheet_burn(
            sow_id,
            contract_hours
        )
        
        # Risk Agent Analysis
        risk_exposure = risk_agent.calculate_penalty_exposure(compliance_status, doc)
        operational_data = {
            "uptime_percentage": 99.2,  # Demo data
            "avg_response_time_hours": 3.5
        }
        liability_events = risk_agent.detect_liability_events(operational_data)
        
        trends = {
            "velocity_trend": "stable"
        }
        breach_probability = risk_agent.estimate_breach_probability(trends, doc)
        
        # Forecast Agent Analysis
        forecast_breach = forecast_agent.predict_breach_probability(
            {}, trends, doc
        )
        
        # Get total value (revenue) from financial summary
        total_value = financial_summary.get("total_value", 150000)  # Fallback to $150k if not populated
        
        margin_forecast = forecast_agent.forecast_margin_impact(
            timesheet_burn,
            total_value,
            doc
        )
        
        scope_creep_items = doc.get("scope_creep_items", [])
        change_order = forecast_agent.generate_change_order_draft(scope_creep_items, doc)
        
        recommendations = forecast_agent.generate_recommendations(
            forecast_breach,
            margin_forecast,
            penalty_exposure
        )
        
        return {
            "success": True,
            "sow_id": sow_id,
            "sow_info": {
                "sow_number": doc.get("sow_number"),
                "client_name": doc.get("client_name"),
                "project_name": doc.get("project_name")
            },
            "agents": {
                "contract": contract_agent.get_agent_status(),
                "compliance": compliance_agent.get_agent_status(),
                "risk": risk_agent.get_agent_status(),
                "forecast": forecast_agent.get_agent_status()
            },
            "metrics": {
                "sla_health": {
                    "overall_score": compliance_status["overall_compliance_rate"],
                    "compliant": compliance_status["compliant"],
                    "at_risk": compliance_status["at_risk"],
                    "breached": compliance_status["breached"],
                    "total": compliance_status["total"]
                },
                "penalty_exposure": {
                    "total": penalty_exposure["total_exposure"],
                    "immediate": risk_exposure["immediate_exposure"],
                    "potential": risk_exposure["potential_exposure"],
                    "currency": "USD",
                    "trend": risk_exposure["trend"]
                },
                "scope_burn": {
                    "contract_hours": timesheet_burn["contract_hours"],
                    "hours_burned": timesheet_burn["hours_burned"],
                    "hours_remaining": timesheet_burn["hours_remaining"],
                    "burn_percentage": timesheet_burn["burn_percentage"],
                    "out_of_scope_items": scope_boundaries["out_of_scope_items"],
                    "out_of_scope_value": scope_boundaries["out_of_scope_value"]
                },
                "breach_risk": {
                    "probability": breach_probability["overall_breach_probability"],
                    "probability_percentage": breach_probability["probability_percentage"],
                    "risk_level": breach_probability["risk_level"],
                    "risk_factors": breach_probability["risk_factors"]
                },
                "margin_forecast": {
                    "current_margin": margin_forecast["current_margin"],
                    "projected_margin": margin_forecast["projected_margin"],
                    "margin_erosion": margin_forecast["margin_erosion"],
                    "current_margin_percentage": margin_forecast["current_margin_percentage"],
                    "projected_margin_percentage": margin_forecast["projected_margin_percentage"],
                    "at_risk": margin_forecast["at_risk"]
                }
            },
            "recommendations": recommendations,
            "change_order": change_order,
            "liability_events": liability_events,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Trigger Slack notifications based on thresholds
        try:
            sow_name = doc.get("project_name", doc.get("sow_number", sow_id))
            
            # Alert for high SLA breach risk (>3 at-risk SLAs)
            if compliance_status.get("at_risk", 0) >= 3:
                await slack_service.send_sla_breach_alert(
                    sow_id,
                    sow_name,
                    compliance_status["at_risk"],
                    penalty_exposure["total_exposure"]
                )
            
            # Alert for high penalty exposure (>$2k)
            if penalty_exposure["total_exposure"] > 2000:
                await slack_service.send_high_penalty_warning(
                    sow_id,
                    sow_name,
                    penalty_exposure["total_exposure"],
                    risk_exposure["immediate_exposure"]
                )
            
            # Alert for high breach probability (>50%)
            if breach_probability["overall_breach_probability"] > 0.5:
                await slack_service.send_breach_probability_alert(
                    sow_id,
                    sow_name,
                    breach_probability["overall_breach_probability"],
                    breach_probability["risk_level"]
                )
        except Exception as e:
            # Don't fail the request if Slack notifications fail
            logger.warning(f"Failed to send Slack notifications: {e}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")


@router.get("/monitoring/sla-health/{sow_id}")
async def get_sla_health(sow_id: str):
    """Get SLA health metrics"""
    try:
        doc = await cloudant_db.get_document(sow_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"SOW not found: {sow_id}")
        
        compliance_status = await compliance_agent.compare_sla_vs_operations(sow_id, doc)
        
        return {
            "success": True,
            "sow_id": sow_id,
            "overall_health": compliance_status["overall_compliance_rate"],
            "metrics": compliance_status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/penalty-exposure/{sow_id}")
async def get_penalty_exposure(sow_id: str):
    """Get penalty exposure metrics"""
    try:
        doc = await cloudant_db.get_document(sow_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"SOW not found: {sow_id}")
        
        sla_terms = contract_agent.analyze_sla_terms(doc)
        penalty_exposure = contract_agent.calculate_penalty_exposure(sla_terms)
        
        return {
            "success": True,
            "sow_id": sow_id,
            "exposure": penalty_exposure
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/scope-burn/{sow_id}")
async def get_scope_burn(sow_id: str):
    """Get scope burn metrics"""
    try:
        doc = await cloudant_db.get_document(sow_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"SOW not found: {sow_id}")
        
        timesheet_burn = await compliance_agent.track_timesheet_burn(sow_id, 1000)
        scope_boundaries = contract_agent.detect_scope_boundaries(doc)
        
        return {
            "success": True,
            "sow_id": sow_id,
            "burn_metrics": timesheet_burn,
            "scope_metrics": scope_boundaries
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/breach-risk/{sow_id}")
async def get_breach_risk(sow_id: str):
    """Get breach risk metrics"""
    try:
        doc = await cloudant_db.get_document(sow_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"SOW not found: {sow_id}")
        
        trends = {"velocity_trend": "stable"}
        breach_probability = risk_agent.estimate_breach_probability(trends, doc)
        
        return {
            "success": True,
            "sow_id": sow_id,
            "breach_risk": breach_probability
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
