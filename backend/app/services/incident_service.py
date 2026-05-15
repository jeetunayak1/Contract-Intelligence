"""
Incident Service
Manages incident lifecycle and detection logic
"""
import logging
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from app.models.event_models import (
    Incident, IncidentCreate, IncidentPriority, IncidentStatus,
    EventSource, ReasoningLog, ReasoningLogLevel
)
from app.services.firebase_event_service import get_firebase_event_service

logger = logging.getLogger(__name__)


class IncidentService:
    """
    Service for managing incidents
    Handles detection, creation, and lifecycle management
    """
    
    def __init__(self):
        self.event_service = get_firebase_event_service()
        
        # Priority patterns for detection
        self.priority_patterns = {
            r'\[P1\]': 'P1',
            r'\[P2\]': 'P2',
            r'\[P3\]': 'P3',
            r'\[P4\]': 'P4',
            r'\[SEV1\]': 'SEV1',
            r'\[CRITICAL\]': 'CRITICAL',
            r'(?i)critical': 'CRITICAL',
            r'(?i)sev1': 'SEV1',
        }
        
        # Priorities that trigger automatic compliance analysis
        self.auto_trigger_priorities = {'P1', 'P2', 'SEV1', 'CRITICAL'}
    
    # ========================================================================
    # INCIDENT DETECTION
    # ========================================================================
    
    def detect_priority(self, title: str) -> Optional[str]:
        """
        Detect incident priority from title
        Returns priority string or None
        """
        for pattern, priority in self.priority_patterns.items():
            if re.search(pattern, title):
                return priority
        return None
    
    def extract_service_name(self, title: str, body: Optional[str] = None) -> str:
        """
        Extract service name from title or body
        Uses heuristics to identify service
        """
        # Common service patterns
        service_patterns = [
            r'(?i)(payment|auth|database|api|order|notification|integration)[-_]?(\w+)?',
            r'(?i)(\w+)[-_](service|api|gateway|system)',
        ]
        
        text = f"{title} {body or ''}"
        
        for pattern in service_patterns:
            match = re.search(pattern, text)
            if match:
                service = match.group(0).lower().replace(' ', '-')
                return service
        
        return "unknown-service"
    
    def should_trigger_analysis(self, priority: str) -> bool:
        """
        Determine if incident should trigger automatic compliance analysis
        """
        return priority in self.auto_trigger_priorities
    
    # ========================================================================
    # INCIDENT CREATION
    # ========================================================================
    
    async def create_incident_from_github(
        self,
        issue_number: int,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        **kwargs
    ) -> Incident:
        """
        Create incident from GitHub issue
        Automatically detects priority and service
        """
        # Detect priority
        priority = self.detect_priority(title)
        if not priority:
            priority = 'P3'  # Default priority
        
        # Extract service
        service = self.extract_service_name(title, body)
        
        # Determine severity
        severity = self._map_priority_to_severity(priority)
        
        # Generate incident ID
        incident_id = f"INC-{issue_number}"
        
        # Create incident
        incident = Incident(
            incident_id=incident_id,
            source=EventSource.GITHUB,
            priority=priority,
            severity=severity,
            service=service,
            title=title,
            description=body,
            status=IncidentStatus.OPEN,
            github_issue_number=issue_number,
            labels=labels or [],
            affected_users=kwargs.get('affected_users', 0),
            estimated_revenue_impact=kwargs.get('estimated_revenue_impact', 0.0),
            created_at=datetime.utcnow()
        )
        
        # Store in Firestore
        await self.event_service.create_incident(incident)
        
        # Log creation
        await self._log_incident_creation(incident)
        
        logger.info(f"Created incident {incident_id} from GitHub issue #{issue_number}")
        
        return incident
    
    async def create_incident_from_pagerduty(
        self,
        pd_incident_id: str,
        title: str,
        priority: str,
        service: str,
        **kwargs
    ) -> Incident:
        """Create incident from PagerDuty event"""
        incident_id = f"INC-PD-{pd_incident_id}"
        
        incident = Incident(
            incident_id=incident_id,
            source=EventSource.PAGERDUTY,
            priority=priority,
            severity=self._map_priority_to_severity(priority),
            service=service,
            title=title,
            description=kwargs.get('description'),
            status=IncidentStatus.OPEN,
            affected_users=kwargs.get('affected_users', 0),
            estimated_revenue_impact=kwargs.get('estimated_revenue_impact', 0.0),
            created_at=datetime.utcnow()
        )
        
        await self.event_service.create_incident(incident)
        await self._log_incident_creation(incident)
        
        logger.info(f"Created incident {incident_id} from PagerDuty")
        
        return incident
    
    # ========================================================================
    # INCIDENT UPDATES
    # ========================================================================
    
    async def start_sla_analysis(self, incident_id: str, crew_execution_id: str) -> bool:
        """Mark incident as having SLA analysis started"""
        updates = {
            'sla_analysis_started': True,
            'crew_execution_id': crew_execution_id,
            'crew_status': 'RUNNING'
        }
        
        success = await self.event_service.update_incident(incident_id, updates)
        
        if success:
            await self._add_reasoning_log(
                incident_id=incident_id,
                level=ReasoningLogLevel.INFO,
                message=f"🚀 Starting autonomous compliance analysis (Crew: {crew_execution_id})"
            )
        
        return success
    
    async def complete_sla_analysis(
        self,
        incident_id: str,
        breach_detected: bool,
        financial_exposure: float,
        penalty_waived: bool,
        waiver_reason: Optional[str] = None
    ) -> bool:
        """Mark incident SLA analysis as complete"""
        updates = {
            'sla_analysis_completed': True,
            'crew_status': 'COMPLETED',
            'breach_detected': breach_detected,
            'financial_exposure': financial_exposure,
            'penalty_waived': penalty_waived,
            'waiver_reason': waiver_reason
        }
        
        success = await self.event_service.update_incident(incident_id, updates)
        
        if success:
            if breach_detected and not penalty_waived:
                message = f"⚠️ SLA BREACH DETECTED - Financial exposure: ${financial_exposure:,.2f}"
                level = ReasoningLogLevel.ERROR
            elif breach_detected and penalty_waived:
                message = f"✅ SLA breach detected but penalty WAIVED - Reason: {waiver_reason}"
                level = ReasoningLogLevel.SUCCESS
            else:
                message = "✅ No SLA breach detected - Incident within compliance"
                level = ReasoningLogLevel.SUCCESS
            
            await self._add_reasoning_log(
                incident_id=incident_id,
                level=level,
                message=message
            )
        
        return success
    
    async def update_incident_status(self, incident_id: str, status: IncidentStatus) -> bool:
        """Update incident status"""
        updates = {'status': status.value}
        
        if status == IncidentStatus.RESOLVED:
            updates['resolution_completed_at'] = datetime.utcnow().isoformat()
        
        success = await self.event_service.update_incident(incident_id, updates)
        
        if success:
            await self._add_reasoning_log(
                incident_id=incident_id,
                level=ReasoningLogLevel.INFO,
                message=f"📊 Incident status updated: {status.value}"
            )
        
        return success
    
    # ========================================================================
    # INCIDENT RETRIEVAL
    # ========================================================================
    
    async def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID"""
        incident_dict = await self.event_service.get_incident(incident_id)
        if incident_dict:
            return Incident(**incident_dict)
        return None
    
    async def get_active_incidents(self, limit: int = 50) -> List[Incident]:
        """Get all active incidents"""
        incidents_dict = await self.event_service.get_active_incidents(limit)
        return [Incident(**i) for i in incidents_dict]
    
    # ========================================================================
    # REASONING LOGS
    # ========================================================================
    
    async def _add_reasoning_log(
        self,
        incident_id: str,
        level: ReasoningLogLevel,
        message: str,
        agent: Optional[str] = None,
        task: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add reasoning log for incident"""
        log = ReasoningLog(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            level=level,
            message=message,
            agent=agent,
            task=task,
            metadata=metadata,
            timestamp=datetime.utcnow()
        )
        
        await self.event_service.add_reasoning_log(log)
    
    async def _log_incident_creation(self, incident: Incident):
        """Log incident creation"""
        await self._add_reasoning_log(
            incident_id=incident.incident_id,
            level=ReasoningLogLevel.INFO,
            message=f"🔔 New {incident.priority} incident detected: {incident.title}",
            metadata={
                'source': incident.source.value,
                'service': incident.service,
                'priority': incident.priority
            }
        )
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _map_priority_to_severity(self, priority: str) -> str:
        """Map priority to severity level"""
        severity_map = {
            'P1': 'CRITICAL',
            'SEV1': 'CRITICAL',
            'CRITICAL': 'CRITICAL',
            'P2': 'HIGH',
            'P3': 'MEDIUM',
            'P4': 'LOW'
        }
        return severity_map.get(priority, 'MEDIUM')


# Singleton instance
_incident_service = None


def get_incident_service() -> IncidentService:
    """Get or create incident service singleton"""
    global _incident_service
    if _incident_service is None:
        _incident_service = IncidentService()
    return _incident_service


# Made with Bob - Incident Lifecycle Management