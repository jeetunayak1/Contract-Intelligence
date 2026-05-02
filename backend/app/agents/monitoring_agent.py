"""
SOW Sentinel - Monitoring Agent
Continuously monitors SOW compliance and detects risks
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from ..models.sow_models import (
    create_compliance_event_document,
    create_scope_creep_document,
    create_alert_document,
    EventType,
    AlertSeverity,
    ObligationStatus
)


class MonitoringAgent:
    """
    The Monitoring Agent (The Watchman)
    
    Responsibilities:
    1. Compare SOW deadlines vs. actual progress
    2. Monitor commit velocity in GitHub
    3. Detect scope creep (work not in SOW)
    4. Calculate penalty exposure
    5. Generate compliance events
    """
    
    def __init__(self):
        """Initialize the Monitoring Agent"""
        self.monitoring_interval = 14400  # 4 hours in seconds
        self.is_running = False
    
    async def start_monitoring(self, sow_id: str):
        """
        Start continuous monitoring for a SOW
        
        Args:
            sow_id: SOW ID to monitor
        """
        self.is_running = True
        
        while self.is_running:
            await self.check_compliance(sow_id)
            await asyncio.sleep(self.monitoring_interval)
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_running = False
    
    async def check_compliance(self, sow_id: str) -> List[Dict[str, Any]]:
        """
        Check compliance for all obligations in a SOW
        
        Args:
            sow_id: SOW ID
            
        Returns:
            List of compliance events
        """
        # TODO: Fetch SOW from database
        # For demo, use sample data
        obligations = self._get_demo_obligations(sow_id)
        
        events = []
        for obligation in obligations:
            event = await self._check_obligation_compliance(sow_id, obligation)
            if event:
                events.append(event)
        
        return events
    
    async def _check_obligation_compliance(
        self,
        sow_id: str,
        obligation: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Check compliance for a single obligation
        
        Args:
            sow_id: SOW ID
            obligation: Obligation data
            
        Returns:
            Compliance event if issue detected
        """
        deadline = datetime.fromisoformat(obligation["deadline"])
        now = datetime.utcnow()
        days_remaining = (deadline - now).days
        
        current_progress = obligation.get("progress_percentage", 0)
        required_progress = 100
        
        # Calculate velocity
        velocity_trend = self._calculate_velocity_trend(obligation)
        
        # Predict completion date
        predicted_completion = self._predict_completion(
            current_progress,
            velocity_trend,
            days_remaining
        )
        
        # Determine if at risk
        severity = self._determine_severity(
            days_remaining,
            current_progress,
            velocity_trend
        )
        
        if severity:
            # Calculate penalty exposure
            penalty_exposure = self._calculate_penalty_exposure(
                obligation,
                days_remaining,
                predicted_completion
            )
            
            # Create compliance event
            event = create_compliance_event_document(
                sow_id=sow_id,
                obligation_id=obligation["id"],
                event_type=EventType.DEADLINE_WARNING.value,
                severity=severity,
                days_remaining=days_remaining,
                current_progress=current_progress,
                required_progress=required_progress,
                velocity_trend=velocity_trend,
                predicted_completion=predicted_completion.isoformat() if predicted_completion else None,
                penalty_exposure=penalty_exposure
            )
            
            return event
        
        return None
    
    def _calculate_velocity_trend(self, obligation: Dict[str, Any]) -> str:
        """
        Calculate velocity trend (increasing/stable/declining)
        
        Args:
            obligation: Obligation data
            
        Returns:
            Velocity trend
        """
        # TODO: Implement actual velocity calculation from GitHub
        # For demo, return based on progress
        progress = obligation.get("progress_percentage", 0)
        
        if progress < 50:
            return "declining"
        elif progress < 80:
            return "stable"
        else:
            return "increasing"
    
    def _predict_completion(
        self,
        current_progress: float,
        velocity_trend: str,
        days_remaining: int
    ) -> Optional[datetime]:
        """
        Predict completion date based on current velocity
        
        Args:
            current_progress: Current progress percentage
            velocity_trend: Velocity trend
            days_remaining: Days until deadline
            
        Returns:
            Predicted completion date
        """
        if velocity_trend == "declining":
            # Predict will miss deadline
            extra_days = int((100 - current_progress) / 5)  # Rough estimate
            return datetime.utcnow() + timedelta(days=days_remaining + extra_days)
        elif velocity_trend == "stable":
            # On track
            return datetime.utcnow() + timedelta(days=days_remaining)
        else:
            # Ahead of schedule
            return datetime.utcnow() + timedelta(days=days_remaining - 2)
    
    def _determine_severity(
        self,
        days_remaining: int,
        current_progress: float,
        velocity_trend: str
    ) -> Optional[str]:
        """
        Determine alert severity
        
        Args:
            days_remaining: Days until deadline
            current_progress: Current progress percentage
            velocity_trend: Velocity trend
            
        Returns:
            Severity level or None if no alert needed
        """
        if days_remaining < 2:
            return AlertSeverity.CRITICAL.value
        elif days_remaining < 7 and velocity_trend == "declining":
            return AlertSeverity.HIGH.value
        elif days_remaining < 14 and current_progress < 50:
            return AlertSeverity.MEDIUM.value
        elif days_remaining < 30:
            return AlertSeverity.LOW.value
        
        return None
    
    def _calculate_penalty_exposure(
        self,
        obligation: Dict[str, Any],
        days_remaining: int,
        predicted_completion: Optional[datetime]
    ) -> float:
        """
        Calculate potential penalty exposure
        
        Args:
            obligation: Obligation data
            days_remaining: Days until deadline
            predicted_completion: Predicted completion date
            
        Returns:
            Penalty exposure amount
        """
        penalty_amount = obligation.get("penalty_amount", 0)
        penalty_frequency = obligation.get("penalty_frequency", "per_day")
        
        if not predicted_completion:
            return 0
        
        deadline = datetime.fromisoformat(obligation["deadline"])
        
        if predicted_completion > deadline:
            # Will miss deadline
            days_late = (predicted_completion - deadline).days
            
            if penalty_frequency == "per_day":
                return penalty_amount * days_late
            elif penalty_frequency == "one_time":
                return penalty_amount
        
        return 0
    
    async def detect_scope_creep(
        self,
        sow_id: str,
        github_data: Dict[str, Any],
        jira_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect work that's not in the SOW (scope creep)
        
        Args:
            sow_id: SOW ID
            github_data: GitHub activity data
            jira_data: Jira ticket data
            
        Returns:
            List of scope creep detections
        """
        scope_creep_items = []
        
        # TODO: Implement actual scope creep detection
        # For demo, return sample data
        demo_scope_creep = {
            "description": "Advanced Analytics Dashboard",
            "hours_spent": 40,
            "cost": 10000,
            "team_members": ["Developer A", "Developer B"],
            "github_commits": 45,
            "jira_tickets": ["ACME-789", "ACME-790"]
        }
        
        scope_creep_doc = create_scope_creep_document(
            sow_id=sow_id,
            detected_work=demo_scope_creep,
            sow_match=None,
            recommendation="Create Change Request CR-2024-05 for $15,000",
            potential_revenue=15000,
            status="detected"
        )
        
        scope_creep_items.append(scope_creep_doc)
        
        return scope_creep_items
    
    def _get_demo_obligations(self, sow_id: str) -> List[Dict[str, Any]]:
        """Get demo obligations for testing"""
        return [
            {
                "id": "OBL-001",
                "sow_id": sow_id,
                "type": "deliverable",
                "description": "Phase 1: Database Migration",
                "deadline": "2024-03-31T23:59:59Z",
                "penalty_amount": 5000,
                "penalty_frequency": "per_day",
                "risk_level": "critical",
                "status": "in_progress",
                "progress_percentage": 75
            },
            {
                "id": "OBL-002",
                "sow_id": sow_id,
                "type": "deliverable",
                "description": "UAT Sign-off Document",
                "deadline": "2024-05-15T23:59:59Z",
                "penalty_amount": 1000,
                "penalty_frequency": "per_day",
                "risk_level": "high",
                "status": "at_risk",
                "progress_percentage": 60
            }
        ]


# Made with Bob - SOW Sentinel