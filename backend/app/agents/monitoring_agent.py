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
from ..core.cloudant_db import cloudant_db
from ..core.config import settings
import requests
import logging

logger = logging.getLogger(__name__)


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
        doc = await cloudant_db.get_document(sow_id)
        if not doc:
            logger.error(f"SOW {sow_id} not found for monitoring")
            return []
            
        obligations = doc.get("obligations", [])
        
        events = []
        for obligation in obligations:
            event = await self._check_obligation_compliance(sow_id, obligation)
            if event:
                events.append(event)
                # Ensure the new alerts are saved to the SOW document
                doc.setdefault("alerts", []).append(event)
                
        if events:
            await cloudant_db.update_document(sow_id, doc)
            
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
        deadline_raw = obligation.get("deadline")
        if not deadline_raw:
            return None

        try:
            deadline = datetime.fromisoformat(deadline_raw.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            try:
                deadline = datetime.fromisoformat(f"{deadline_raw}T00:00:00+00:00")
            except (TypeError, ValueError):
                return None

        # Fetch GitHub issue if mapped
        mapping = obligation.get("mapped_to", {})
        issue_number = mapping.get("external_id")
        
        is_closed = False
        if issue_number and mapping.get("integration_type") == "github":
            global_settings = await cloudant_db.get_document("global_api_settings") or {}
            token = global_settings.get("github_token") or settings.GITHUB_TOKEN
            owner = global_settings.get("github_owner") or settings.GITHUB_OWNER
            repo = global_settings.get("github_repo") or settings.GITHUB_REPO
            
            if token and owner and repo:
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                }
                resp = requests.get(f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}", headers=headers)
                if resp.status_code == 200:
                    issue_data = resp.json()
                    is_closed = issue_data.get("state") == "closed"
                    # Update progress based on issue state
                    if is_closed:
                        obligation["progress_percentage"] = 100
                        obligation["status"] = ObligationStatus.COMPLETED.value

        if is_closed:
            return None # No alert needed if it's closed

        now = datetime.utcnow().astimezone(deadline.tzinfo)
        total_time = (deadline - datetime.fromisoformat(obligation.get("created_at", now.isoformat()).replace("Z", "+00:00"))).total_seconds()
        if total_time <= 0:
            total_time = 86400 * 30 # fallback to 30 days
            
        time_remaining = (deadline - now).total_seconds()
        days_remaining = time_remaining / 86400.0
        
        current_progress = obligation.get("progress_percentage", 0)
        required_progress = 100
        
        # Calculate velocity
        velocity_trend = self._calculate_velocity_trend(obligation)
        
        # Predict completion date
        predicted_completion = self._predict_completion(
            current_progress,
            velocity_trend,
            int(days_remaining)
        )
        
        # ALERTER LOGIC: Check if within 20% of SLA deadline
        time_ratio = time_remaining / total_time
        severity = None
        
        if time_remaining < 0:
            severity = AlertSeverity.CRITICAL.value
            event_type = EventType.PENALTY_TRIGGERED.value
        elif time_ratio <= 0.20:
            severity = AlertSeverity.HIGH.value
            event_type = EventType.DEADLINE_WARNING.value
            logger.warning(f"ALERT: Issue {issue_number} is within 20% of SLA but not closed!")
        else:
            severity = self._determine_severity(int(days_remaining), current_progress, velocity_trend)
            event_type = EventType.DEADLINE_WARNING.value
            
        if severity:
            penalty_exposure = self._calculate_penalty_exposure(obligation, int(days_remaining), predicted_completion)
            
            # Create alert document instead of just compliance event to show in UI
            alert_doc = create_alert_document(
                sow_id=sow_id,
                obligation_id=obligation["id"],
                alert_type=event_type,
                severity=severity,
                title=f"SLA Warning: {obligation.get('description')}",
                message=f"Ticket is within 20% of SLA deadline but not closed. Days remaining: {int(days_remaining)}",
                days_until_penalty=int(days_remaining),
                penalty_amount=penalty_exposure
            )
            return alert_doc
            
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

        github_commits = github_data.get("commit_count", 0) or len(github_data.get("commits", []))
        jira_ticket_count = jira_data.get("ticket_count", 0) or len(jira_data.get("tickets", []))
        extra_hours = github_data.get("hours_spent", 0) or jira_data.get("hours_spent", 0) or 0
        detected_work = github_data.get("detected_work") or jira_data.get("detected_work") or ""

        if not any([github_commits, jira_ticket_count, extra_hours, detected_work]):
            return []

        revenue_estimate = float(
            github_data.get("potential_revenue")
            or jira_data.get("potential_revenue")
            or github_data.get("cost")
            or jira_data.get("cost")
            or extra_hours * 250
            or 0
        )

        summary_description = detected_work or "Additional delivery work detected outside baseline SOW scope"

        scope_creep_doc = create_scope_creep_document(
            sow_id=sow_id,
            detected_work={
                "description": summary_description,
                "hours_spent": extra_hours,
                "cost": github_data.get("cost") or jira_data.get("cost") or revenue_estimate,
                "team_members": github_data.get("team_members", []) or jira_data.get("team_members", []),
                "github_commits": github_commits,
                "jira_tickets": jira_data.get("tickets", []),
            },
            sow_match=None,
            recommendation=f"Validate scope change and consider recovery of ${revenue_estimate:,.0f}" if revenue_estimate else "Validate scope change and assess commercial recovery",
            potential_revenue=revenue_estimate,
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