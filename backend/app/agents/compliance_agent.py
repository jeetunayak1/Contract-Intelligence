"""
Compliance Agent - Live SLA vs Operational Data
Responsibilities:
- Compare SLA commitments vs actual delivery
- Monitor GitHub velocity vs commitments
- Track timesheet hours vs contract limits
- Detect compliance drift
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ComplianceAgent:
    """
    The Compliance Agent monitors live operational data against SLA commitments
    """
    
    def __init__(self):
        """Initialize the Compliance Agent"""
        self.name = "Compliance Agent"
        self.description = "Live SLA vs ops data"
    
    async def compare_sla_vs_operations(self, sow_id: str, sow_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare SLA terms against live operational data
        
        Args:
            sow_id: SOW ID
            sow_doc: SOW document
            
        Returns:
            Compliance comparison results
        """
        obligations = sow_doc.get("obligations", [])
        
        compliant_count = 0
        at_risk_count = 0
        breached_count = 0
        
        compliance_details = []
        
        for obligation in obligations:
            status = obligation.get("status", "pending")
            risk_level = obligation.get("risk_level", "medium")
            
            if status == "completed":
                compliant_count += 1
                compliance_status = "compliant"
            elif status == "at_risk" or risk_level in ["critical", "high"]:
                at_risk_count += 1
                compliance_status = "at_risk"
            elif status == "breached":
                breached_count += 1
                compliance_status = "breached"
            else:
                compliance_status = "pending"
            
            compliance_details.append({
                "obligation_id": obligation.get("id"),
                "name": obligation.get("description", "")[:50],
                "status": compliance_status,
                "risk_level": risk_level
            })
        
        total = len(obligations)
        compliance_rate = (compliant_count / total * 100) if total > 0 else 0
        
        return {
            "sow_id": sow_id,
            "overall_compliance_rate": round(compliance_rate, 1),
            "compliant": compliant_count,
            "at_risk": at_risk_count,
            "breached": breached_count,
            "total": total,
            "details": compliance_details
        }
    
    async def monitor_github_velocity(
        self, 
        repo: str, 
        sla_terms: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Track commit velocity vs SLA requirements
        
        Args:
            repo: GitHub repository
            sla_terms: SLA terms to monitor
            
        Returns:
            Velocity monitoring results
        """
        # Demo implementation - in production, this would call GitHub API
        return {
            "repo": repo,
            "commits_last_week": 42,
            "issues_closed_last_week": 8,
            "pr_merge_time_avg_hours": 18.5,
            "velocity_trend": "stable",
            "sla_compliance": "on_track"
        }
    
    async def track_timesheet_burn(
        self, 
        project_id: str, 
        contract_hours: int
    ) -> Dict[str, Any]:
        """
        Monitor hours burned vs contract allocation
        
        Args:
            project_id: Project ID
            contract_hours: Total contract hours
            
        Returns:
            Timesheet burn analysis
        """
        # Demo implementation - in production, this would integrate with timesheet system
        hours_burned = int(contract_hours * 0.75)  # 75% burned
        hours_remaining = contract_hours - hours_burned
        burn_rate_per_week = 40
        weeks_remaining = hours_remaining / burn_rate_per_week if burn_rate_per_week > 0 else 0
        
        return {
            "project_id": project_id,
            "contract_hours": contract_hours,
            "hours_burned": hours_burned,
            "hours_remaining": hours_remaining,
            "burn_rate_per_week": burn_rate_per_week,
            "weeks_remaining": round(weeks_remaining, 1),
            "burn_percentage": round((hours_burned / contract_hours * 100), 1),
            "status": "on_track" if hours_remaining > 0 else "overrun"
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status for UI display"""
        return {
            "name": self.name,
            "description": self.description,
            "status": "active",
            "capabilities": [
                "SLA compliance monitoring",
                "GitHub velocity tracking",
                "Timesheet burn analysis",
                "Compliance drift detection"
            ]
        }


# Global instance
compliance_agent = ComplianceAgent()

# Made with Bob
