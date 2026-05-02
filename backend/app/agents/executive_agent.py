"""
SOW Sentinel - Executive Agent
Takes automated actions based on compliance events
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..models.sow_models import (
    create_alert_document,
    AlertSeverity
)


class ExecutiveAgent:
    """
    The Executive Agent (The Actor)
    
    Responsibilities:
    1. Create Jira tasks automatically
    2. Schedule Google Calendar events
    3. Send Slack/email notifications
    4. Generate status reports
    5. Block invoice release if needed
    """
    
    def __init__(
        self,
        jira_api_key: Optional[str] = None,
        calendar_api_key: Optional[str] = None,
        slack_webhook: Optional[str] = None
    ):
        """
        Initialize the Executive Agent
        
        Args:
            jira_api_key: Jira API key
            calendar_api_key: Google Calendar API key
            slack_webhook: Slack webhook URL
        """
        self.jira_api_key = jira_api_key
        self.calendar_api_key = calendar_api_key
        self.slack_webhook = slack_webhook
    
    async def handle_compliance_event(
        self,
        event: Dict[str, Any],
        sow: Dict[str, Any],
        obligation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle a compliance event by taking appropriate actions
        
        Args:
            event: Compliance event data
            sow: SOW document
            obligation: Obligation data
            
        Returns:
            Actions taken
        """
        actions_taken = []
        
        severity = event.get("severity")
        
        # Create alert
        alert = await self.create_alert(event, sow, obligation)
        actions_taken.append(f"Created alert: {alert['_id']}")
        
        # Take actions based on severity
        if severity == AlertSeverity.CRITICAL.value:
            # Critical: Immediate action
            jira_task = await self.create_urgent_jira_task(obligation)
            actions_taken.append(f"Created P0 Jira task: {jira_task['key']}")
            
            slack_msg = await self.send_slack_alert(alert, urgent=True)
            actions_taken.append(f"Sent urgent Slack alert")
            
            meeting = await self.schedule_emergency_meeting(obligation)
            actions_taken.append(f"Scheduled emergency meeting")
        
        elif severity == AlertSeverity.HIGH.value:
            # High: Urgent attention
            jira_task = await self.create_jira_task(obligation)
            actions_taken.append(f"Created Jira task: {jira_task['key']}")
            
            slack_msg = await self.send_slack_alert(alert)
            actions_taken.append(f"Sent Slack alert")
        
        elif severity == AlertSeverity.MEDIUM.value:
            # Medium: Monitor
            email = await self.send_email_notification(alert)
            actions_taken.append(f"Sent email notification")
        
        else:
            # Low: Informational
            calendar_event = await self.schedule_planning_session(obligation)
            actions_taken.append(f"Scheduled planning session")
        
        return {
            "alert_id": alert["_id"],
            "actions_taken": actions_taken,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def create_alert(
        self,
        event: Dict[str, Any],
        sow: Dict[str, Any],
        obligation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an alert document
        
        Args:
            event: Compliance event
            sow: SOW document
            obligation: Obligation data
            
        Returns:
            Alert document
        """
        severity = event.get("severity")
        days_remaining = event.get("days_remaining", 0)
        penalty_exposure = event.get("penalty_exposure", 0)
        
        # Generate alert message
        if severity == AlertSeverity.CRITICAL.value:
            title = f"URGENT: {obligation['description']} Due in {days_remaining} Days"
            message = f"If you don't deliver by the deadline, you lose ${penalty_exposure:,.0f}"
        elif severity == AlertSeverity.HIGH.value:
            title = f"WARNING: {obligation['description']} At Risk"
            message = f"Current velocity declining. Penalty exposure: ${penalty_exposure:,.0f}"
        else:
            title = f"NOTICE: {obligation['description']} Approaching"
            message = f"Deadline in {days_remaining} days. Current progress: {event.get('current_progress', 0)}%"
        
        # Generate recommended actions
        recommended_actions = self._generate_recommended_actions(
            obligation,
            event
        )
        
        alert = create_alert_document(
            sow_id=sow["_id"],
            obligation_id=obligation["id"],
            alert_type="deadline_warning",
            severity=severity,
            title=title,
            message=message,
            penalty_amount=obligation.get("penalty_amount"),
            days_until_penalty=days_remaining,
            recommended_actions=recommended_actions,
            notification_channels=["slack", "email"]
        )
        
        return alert
    
    def _generate_recommended_actions(
        self,
        obligation: Dict[str, Any],
        event: Dict[str, Any]
    ) -> List[str]:
        """Generate recommended actions based on situation"""
        actions = []
        
        severity = event.get("severity")
        progress = event.get("current_progress", 0)
        
        if severity == AlertSeverity.CRITICAL.value:
            actions.extend([
                "Schedule emergency review meeting",
                "Escalate to project manager and CEO",
                "Request deadline extension if possible",
                "Allocate additional resources immediately"
            ])
        elif severity == AlertSeverity.HIGH.value:
            actions.extend([
                "Review blockers and dependencies",
                "Increase team velocity",
                "Schedule daily standups",
                "Consider resource reallocation"
            ])
        elif progress < 50:
            actions.extend([
                "Identify and remove blockers",
                "Review task breakdown",
                "Ensure team has necessary resources"
            ])
        else:
            actions.extend([
                "Continue current pace",
                "Monitor progress weekly",
                "Prepare for delivery review"
            ])
        
        return actions
    
    async def create_jira_task(
        self,
        obligation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a Jira task for an obligation
        
        Args:
            obligation: Obligation data
            
        Returns:
            Jira task data
        """
        # TODO: Implement actual Jira API integration
        # For demo, return mock data
        return {
            "key": f"URGENT-{obligation['id'][-3:]}",
            "summary": f"Complete: {obligation['description']}",
            "description": f"SOW Obligation due: {obligation['deadline']}",
            "priority": "High",
            "due_date": obligation["deadline"],
            "url": f"https://jira.company.com/browse/URGENT-{obligation['id'][-3:]}"
        }
    
    async def create_urgent_jira_task(
        self,
        obligation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create P0 urgent Jira task"""
        task = await self.create_jira_task(obligation)
        task["priority"] = "P0 - Critical"
        return task
    
    async def schedule_emergency_meeting(
        self,
        obligation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Schedule emergency meeting
        
        Args:
            obligation: Obligation data
            
        Returns:
            Calendar event data
        """
        # TODO: Implement actual Google Calendar API
        # For demo, return mock data
        meeting_time = datetime.utcnow() + timedelta(hours=2)
        
        return {
            "event_id": f"MEETING-{obligation['id'][-3:]}",
            "title": f"URGENT: {obligation['description']} Review",
            "start_time": meeting_time.isoformat(),
            "duration": 60,
            "attendees": ["pm@company.com", "tech-lead@company.com", "ceo@company.com"],
            "url": "https://meet.google.com/abc-defg-hij"
        }
    
    async def schedule_planning_session(
        self,
        obligation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Schedule planning session"""
        deadline = datetime.fromisoformat(obligation["deadline"])
        meeting_time = deadline - timedelta(days=30)
        
        return {
            "event_id": f"PLAN-{obligation['id'][-3:]}",
            "title": f"Planning: {obligation['description']}",
            "start_time": meeting_time.isoformat(),
            "duration": 30,
            "attendees": ["pm@company.com", "tech-lead@company.com"],
            "url": "https://meet.google.com/xyz-uvwx-rst"
        }
    
    async def send_slack_alert(
        self,
        alert: Dict[str, Any],
        urgent: bool = False
    ) -> Dict[str, Any]:
        """
        Send Slack alert
        
        Args:
            alert: Alert data
            urgent: Whether this is urgent
            
        Returns:
            Slack response
        """
        # TODO: Implement actual Slack webhook
        # For demo, return mock data
        return {
            "ok": True,
            "channel": "#sow-alerts" if not urgent else "#urgent-alerts",
            "message": alert["message"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def send_email_notification(
        self,
        alert: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send email notification"""
        # TODO: Implement actual email sending
        return {
            "sent": True,
            "to": ["pm@company.com"],
            "subject": alert["title"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def generate_status_report(
        self,
        sow: Dict[str, Any],
        github_data: Optional[Dict[str, Any]] = None,
        jira_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate status report for SOW
        
        Args:
            sow: SOW document
            github_data: GitHub activity data
            jira_data: Jira progress data
            
        Returns:
            Formatted status report
        """
        report = f"""
# SOW Status Report
**Project**: {sow['project_name']}
**Client**: {sow['client_name']}
**Report Date**: {datetime.utcnow().strftime('%Y-%m-%d')}

## Overall Status
- Total Obligations: {len(sow.get('obligations', []))}
- Completed: {len([o for o in sow.get('obligations', []) if o.get('status') == 'completed'])}
- In Progress: {len([o for o in sow.get('obligations', []) if o.get('status') == 'in_progress'])}
- At Risk: {len([o for o in sow.get('obligations', []) if o.get('status') == 'at_risk'])}

## Financial Summary
- Total Contract Value: ${sow.get('total_value', 0):,.0f}
- Penalty Exposure: ${sow.get('financial_summary', {}).get('total_penalties_at_risk', 0):,.0f}
- Penalties Avoided: ${sow.get('financial_summary', {}).get('penalties_avoided', 0):,.0f}

## Key Milestones
"""
        
        for obligation in sow.get('obligations', []):
            status_emoji = "✅" if obligation.get('status') == 'completed' else "🔄" if obligation.get('status') == 'in_progress' else "🚨"
            report += f"\n{status_emoji} **{obligation['description']}**\n"
            report += f"   - Deadline: {obligation['deadline']}\n"
            report += f"   - Progress: {obligation.get('progress_percentage', 0)}%\n"
        
        return report


# Made with Bob - SOW Sentinel