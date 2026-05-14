"""
Forecast Agent - Breach Probability and Margin Analysis
Responsibilities:
- Predict SLA breach likelihood
- Forecast margin erosion
- Recommend preventive actions
- Generate change order drafts
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ForecastAgent:
    """
    The Forecast Agent predicts future risks and recommends preventive actions
    """
    
    def __init__(self):
        """Initialize the Forecast Agent"""
        self.name = "Forecast Agent"
        self.description = "Breach prob, margin"
    
    def predict_breach_probability(
        self, 
        historical_data: Dict[str, Any], 
        current_trends: Dict[str, Any],
        sow_doc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict likelihood of SLA breach
        
        Args:
            historical_data: Historical performance data
            current_trends: Current trend indicators
            sow_doc: SOW document
            
        Returns:
            Breach prediction
        """
        risk_assessment = sow_doc.get("risk_assessment", {})
        risk_score = risk_assessment.get("risk_score", 50)
        
        # Calculate base probability
        base_prob = risk_score / 100
        
        # Adjust for velocity trends
        velocity_trend = current_trends.get("velocity_trend", "stable")
        if velocity_trend == "declining":
            base_prob += 0.20
        elif velocity_trend == "improving":
            base_prob -= 0.15
        
        # Adjust for scope creep
        scope_creep_count = len(sow_doc.get("scope_creep_items", []))
        if scope_creep_count > 0:
            base_prob += (scope_creep_count * 0.05)
        
        # Cap probability
        breach_prob = max(0.0, min(0.95, base_prob))
        
        return {
            "breach_probability": round(breach_prob, 2),
            "probability_percentage": round(breach_prob * 100, 1),
            "confidence_level": "medium",
            "prediction_horizon_days": 30,
            "key_indicators": {
                "velocity_trend": velocity_trend,
                "scope_creep_items": scope_creep_count,
                "risk_score": risk_score
            }
        }
    
    def forecast_margin_impact(
        self, 
        scope_burn: Dict[str, Any], 
        revenue: float,
        sow_doc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate margin erosion forecast
        
        Args:
            scope_burn: Scope burn data
            revenue: Total revenue
            sow_doc: SOW document
            
        Returns:
            Margin forecast
        """
        hours_burned = scope_burn.get("hours_burned", 0)
        contract_hours = scope_burn.get("contract_hours", 1)
        projected_overrun = scope_burn.get("projected_overrun", 0)
        
        # Calculate costs
        hourly_rate = 150  # Demo rate
        actual_cost = hours_burned * hourly_rate
        projected_total_cost = (hours_burned + projected_overrun) * hourly_rate
        
        # Calculate margins
        current_margin = revenue - actual_cost
        projected_margin = revenue - projected_total_cost
        margin_erosion = current_margin - projected_margin
        
        # Calculate percentages
        current_margin_pct = (current_margin / revenue * 100) if revenue > 0 else 0
        projected_margin_pct = (projected_margin / revenue * 100) if revenue > 0 else 0
        
        return {
            "revenue": revenue,
            "current_cost": actual_cost,
            "projected_cost": projected_total_cost,
            "current_margin": current_margin,
            "projected_margin": projected_margin,
            "margin_erosion": margin_erosion,
            "current_margin_percentage": round(current_margin_pct, 1),
            "projected_margin_percentage": round(projected_margin_pct, 1),
            "at_risk": projected_margin < (revenue * 0.15),  # Below 15% margin
            "recommendation": "Initiate change order" if margin_erosion > 10000 else "Monitor closely"
        }
    
    def generate_change_order_draft(
        self, 
        scope_creep_items: List[Dict[str, Any]],
        sow_doc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Auto-generate change order documentation
        
        Args:
            scope_creep_items: List of out-of-scope items
            sow_doc: SOW document
            
        Returns:
            Change order draft
        """
        if not scope_creep_items:
            return {
                "has_change_order": False,
                "message": "No out-of-scope work detected"
            }
        
        total_value = sum(item.get("financial_impact", 0) for item in scope_creep_items)
        
        # Generate change order text
        change_order_text = f"""
CHANGE ORDER DRAFT
==================

Project: {sow_doc.get('project_name', 'N/A')}
Client: {sow_doc.get('client_name', 'N/A')}
SOW Number: {sow_doc.get('sow_number', 'N/A')}
Date: {datetime.utcnow().strftime('%Y-%m-%d')}

SCOPE ADDITIONS
---------------

The following work items were identified as out-of-scope per the original SOW:

"""
        
        for idx, item in enumerate(scope_creep_items, 1):
            change_order_text += f"{idx}. {item.get('title', 'Unnamed item')}\n"
            change_order_text += f"   Description: {item.get('description', 'N/A')}\n"
            change_order_text += f"   Estimated Value: ${item.get('financial_impact', 0):,.2f}\n\n"
        
        change_order_text += f"""
FINANCIAL SUMMARY
-----------------
Total Additional Value: ${total_value:,.2f}

RECOMMENDATION
--------------
This change order should be reviewed and approved before proceeding with the additional work.
"""
        
        return {
            "has_change_order": True,
            "change_order_id": f"CO-{sow_doc.get('sow_number', 'XXX')}-{datetime.utcnow().strftime('%Y%m%d')}",
            "total_value": total_value,
            "item_count": len(scope_creep_items),
            "draft_text": change_order_text,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }
    
    def generate_recommendations(
        self,
        breach_prob: Dict[str, Any],
        margin_forecast: Dict[str, Any],
        penalty_exposure: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations
        
        Args:
            breach_prob: Breach probability data
            margin_forecast: Margin forecast data
            penalty_exposure: Penalty exposure data
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # High breach probability
        if breach_prob.get("breach_probability", 0) > 0.5:
            recommendations.append({
                "priority": "critical",
                "type": "breach_prevention",
                "title": "High SLA breach risk detected",
                "description": f"{breach_prob['probability_percentage']}% probability of breach",
                "actions": [
                    "Schedule emergency capacity review",
                    "Escalate to delivery leadership",
                    "Review resource allocation"
                ]
            })
        
        # Margin erosion
        if margin_forecast.get("at_risk", False):
            recommendations.append({
                "priority": "high",
                "type": "margin_protection",
                "title": "Margin erosion forecast",
                "description": f"Projected margin: {margin_forecast['projected_margin_percentage']}%",
                "actions": [
                    "Initiate change order process",
                    "Review scope boundaries",
                    "Optimize resource utilization"
                ]
            })
        
        # High penalty exposure
        if penalty_exposure.get("total_exposure", 0) > 20000:
            recommendations.append({
                "priority": "high",
                "type": "penalty_mitigation",
                "title": "Significant penalty exposure",
                "description": f"${penalty_exposure['total_exposure']:,.0f} at risk",
                "actions": [
                    "Convert penalty risk to change order",
                    "Negotiate SLA modifications",
                    "Implement risk mitigation plan"
                ]
            })
        
        return recommendations
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status for UI display"""
        return {
            "name": self.name,
            "description": self.description,
            "status": "active",
            "capabilities": [
                "Breach probability prediction",
                "Margin erosion forecasting",
                "Change order generation",
                "Preventive recommendations"
            ]
        }


# Global instance
forecast_agent = ForecastAgent()

# Made with Bob
