"""
Risk Agent - Penalty and Liability Detection
Responsibilities:
- Real-time penalty exposure calculation
- Liability event detection
- Risk scoring and prioritization
- Breach probability estimation
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RiskAgent:
    """
    The Risk Agent detects and quantifies penalty and liability risks
    """
    
    def __init__(self):
        """Initialize the Risk Agent"""
        self.name = "Risk Agent"
        self.description = "Penalty, liability detect"
    
    def calculate_penalty_exposure(
        self, 
        sla_status: Dict[str, Any],
        sow_doc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate current penalty exposure in $
        
        Args:
            sla_status: SLA compliance status
            sow_doc: SOW document
            
        Returns:
            Penalty exposure calculation
        """
        risk_assessment = sow_doc.get("risk_assessment", {})
        total_exposure = risk_assessment.get("total_penalty_exposure", 0)
        
        # Calculate immediate vs potential exposure
        at_risk_count = sla_status.get("at_risk", 0)
        breached_count = sla_status.get("breached", 0)
        
        immediate_exposure = breached_count * 5000  # Breached SLAs
        potential_exposure = at_risk_count * 2500   # At-risk SLAs
        
        return {
            "total_exposure": total_exposure,
            "immediate_exposure": immediate_exposure,
            "potential_exposure": potential_exposure,
            "currency": "USD",
            "breakdown": {
                "breached_slas": breached_count,
                "at_risk_slas": at_risk_count,
                "immediate_penalty": immediate_exposure,
                "potential_penalty": potential_exposure
            },
            "trend": "increasing" if at_risk_count > 0 else "stable"
        }
    
    def detect_liability_events(
        self, 
        operational_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect events that trigger liability
        
        Args:
            operational_data: Operational metrics
            
        Returns:
            List of liability events
        """
        liability_events = []
        
        # Check for uptime issues
        uptime = operational_data.get("uptime_percentage", 100)
        if uptime < 99.9:
            liability_events.append({
                "type": "uptime_breach",
                "severity": "high",
                "description": f"Uptime at {uptime}%, below 99.9% SLA",
                "financial_impact": 10000,
                "detected_at": datetime.utcnow().isoformat()
            })
        
        # Check for response time issues
        response_time = operational_data.get("avg_response_time_hours", 0)
        if response_time > 4:
            liability_events.append({
                "type": "response_time_breach",
                "severity": "medium",
                "description": f"Response time at {response_time}h, exceeds 4h SLA",
                "financial_impact": 5000,
                "detected_at": datetime.utcnow().isoformat()
            })
        
        return liability_events
    
    def estimate_breach_probability(
        self, 
        trends: Dict[str, Any],
        sow_doc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate % probability of SLA breach
        
        Args:
            trends: Historical trend data
            sow_doc: SOW document
            
        Returns:
            Breach probability estimation
        """
        risk_assessment = sow_doc.get("risk_assessment", {})
        risk_score = risk_assessment.get("risk_score", 50)
        risk_level = risk_assessment.get("risk_level", "medium")
        
        # Base probability from risk score
        base_probability = risk_score / 100
        
        # Adjust based on trends
        velocity_trend = trends.get("velocity_trend", "stable")
        if velocity_trend == "declining":
            base_probability += 0.15
        elif velocity_trend == "improving":
            base_probability -= 0.10
        
        # Cap between 0 and 1
        breach_probability = max(0.0, min(1.0, base_probability))
        
        # Calculate risk factors
        risk_factors = []
        
        if risk_level in ["critical", "high"]:
            risk_factors.append({
                "factor": "High risk classification",
                "impact": "high",
                "contribution": 0.25
            })
        
        if velocity_trend == "declining":
            risk_factors.append({
                "factor": "Declining delivery velocity",
                "impact": "medium",
                "contribution": 0.15
            })
        
        scope_creep = len(sow_doc.get("scope_creep_items", []))
        if scope_creep > 0:
            risk_factors.append({
                "factor": f"Scope creep detected ({scope_creep} items)",
                "impact": "medium",
                "contribution": 0.12
            })
        
        return {
            "overall_breach_probability": round(breach_probability, 2),
            "probability_percentage": round(breach_probability * 100, 1),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "confidence": "medium"
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status for UI display"""
        return {
            "name": self.name,
            "description": self.description,
            "status": "active",
            "capabilities": [
                "Penalty exposure calculation",
                "Liability event detection",
                "Risk scoring",
                "Breach probability estimation"
            ]
        }


# Global instance
risk_agent = RiskAgent()

# Made with Bob
