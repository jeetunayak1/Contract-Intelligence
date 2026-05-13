"""
Contract Agent - Enhanced SLA and Penalty Analysis
Responsibilities:
- Deep SLA parsing with penalty clauses
- Scope boundary detection
- Contract term extraction
- Penalty calculation logic
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


class ContractAgent:
    """
    The Contract Agent analyzes SOW documents for SLAs, penalties, and scope
    """
    
    def __init__(self):
        """Initialize the Contract Agent"""
        self.name = "Contract Agent"
        self.description = "SLAs, penalties, scope analysis"
    
    def analyze_sla_terms(self, sow_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and structure all SLA commitments
        
        Args:
            sow_doc: SOW document
            
        Returns:
            List of SLA terms with penalty clauses
        """
        obligations = sow_doc.get("obligations", [])
        sla_terms = []
        
        for obligation in obligations:
            if obligation.get("deadline"):
                sla_term = {
                    "id": obligation.get("id"),
                    "name": obligation.get("description", "")[:50],
                    "deadline": obligation.get("deadline"),
                    "status": obligation.get("status", "pending"),
                    "penalty_clause": self._extract_penalty_clause(obligation),
                    "penalty_amount": obligation.get("penalty_amount", 0),  # Use actual penalty from SLA data
                    "risk_level": obligation.get("risk_level", "medium")
                }
                sla_terms.append(sla_term)
        
        return sla_terms
    
    def _extract_penalty_clause(self, obligation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract penalty information from obligation"""
        # Demo logic - in production, this would use NLP to extract from text
        risk_level = obligation.get("risk_level", "medium")
        
        penalty_amounts = {
            "critical": 5000,
            "high": 2500,
            "medium": 1000,
            "low": 500
        }
        
        return {
            "has_penalty": risk_level in ["critical", "high"],
            "amount": penalty_amounts.get(risk_level, 0),
            "trigger": "missed_deadline",
            "grace_period_days": 0 if risk_level == "critical" else 2
        }
    
    def calculate_penalty_exposure(
        self, 
        sla_terms: List[Dict[str, Any]], 
        current_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate real-time penalty exposure
        
        Args:
            sla_terms: List of SLA terms
            current_date: Current date (defaults to now)
            
        Returns:
            Penalty exposure summary
        """
        if current_date is None:
            current_date = datetime.now(timezone.utc)
        
        total_exposure = 0
        at_risk_count = 0
        breakdown = []
        
        for sla in sla_terms:
            try:
                deadline = datetime.fromisoformat(sla["deadline"].replace("Z", "+00:00"))
                days_until = (deadline - current_date).days
                
                # Get actual penalty amount from SLA term (populated by populate_sla_data)
                # Fall back to penalty_clause if not available
                penalty_clause = sla.get("penalty_clause", {})
                exposure_amount = sla.get("penalty_amount", penalty_clause.get("amount", 0))
                
                # Skip if no penalty
                if exposure_amount == 0:
                    continue
                
                # Calculate exposure for at-risk SLAs (within 7 days or overdue)
                if days_until <= 7:
                    at_risk_count += 1
                    total_exposure += exposure_amount
                    
                    breakdown.append({
                        "sla_name": sla["name"],
                        "exposure_amount": exposure_amount,
                        "days_until_penalty": days_until,
                        "probability": self._calculate_breach_probability(days_until, sla["risk_level"])
                    })
            except (ValueError, KeyError) as e:
                logger.warning(f"Could not parse deadline for SLA: {e}")
                continue
        
        return {
            "total_exposure": total_exposure,
            "at_risk_count": at_risk_count,
            "breakdown": breakdown,
            "currency": "USD"
        }
    
    def _calculate_breach_probability(self, days_until: int, risk_level: str) -> float:
        """Calculate probability of SLA breach"""
        base_probability = {
            "critical": 0.8,
            "high": 0.6,
            "medium": 0.4,
            "low": 0.2
        }.get(risk_level, 0.3)
        
        # Increase probability as deadline approaches
        if days_until <= 0:
            return 0.95
        elif days_until <= 2:
            return min(base_probability + 0.3, 0.9)
        elif days_until <= 5:
            return min(base_probability + 0.15, 0.75)
        else:
            return base_probability
    
    def detect_scope_boundaries(self, sow_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify what's in/out of scope
        
        Args:
            sow_doc: SOW document
            
        Returns:
            Scope boundary analysis
        """
        obligations = sow_doc.get("obligations", [])
        scope_creep_items = sow_doc.get("scope_creep_items", [])
        
        in_scope_count = len(obligations)
        out_of_scope_count = len(scope_creep_items)
        
        out_of_scope_value = sum(
            item.get("financial_impact", 0) 
            for item in scope_creep_items
        )
        
        return {
            "in_scope_items": in_scope_count,
            "out_of_scope_items": out_of_scope_count,
            "out_of_scope_value": out_of_scope_value,
            "scope_creep_detected": out_of_scope_count > 0,
            "details": scope_creep_items
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status for UI display"""
        return {
            "name": self.name,
            "description": self.description,
            "status": "active",
            "capabilities": [
                "SLA term extraction",
                "Penalty calculation",
                "Scope boundary detection",
                "Risk assessment"
            ]
        }


# Global instance
contract_agent = ContractAgent()

# Made with Bob
