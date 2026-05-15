"""
PagerDuty Service
Loads and manages incident data
"""
import json
import os
from typing import List, Dict, Any
from pathlib import Path
import logging

from ..models.compliance_models import PagerDutyIncident

logger = logging.getLogger(__name__)


class PagerDutyService:
    """Service for managing PagerDuty incidents"""
    
    def __init__(self):
        """Initialize PagerDuty service"""
        self.mock_data_path = Path(__file__).parent.parent / "mock_data" / "pagerduty_incidents.json"
        self._incidents_cache = None
    
    def load_incidents(self) -> List[PagerDutyIncident]:
        """
        Load incidents from mock data file
        
        Returns:
            List of PagerDuty incidents
        """
        try:
            if self._incidents_cache is not None:
                return self._incidents_cache
            
            if not self.mock_data_path.exists():
                logger.warning(f"Mock data file not found: {self.mock_data_path}")
                return []
            
            with open(self.mock_data_path, 'r') as f:
                data = json.load(f)
            
            incidents = [PagerDutyIncident(**incident) for incident in data]
            self._incidents_cache = incidents
            
            logger.info(f"Loaded {len(incidents)} PagerDuty incidents")
            return incidents
            
        except Exception as e:
            logger.error(f"Failed to load PagerDuty incidents: {e}")
            return []
    
    def get_incident_by_id(self, incident_id: str) -> PagerDutyIncident | None:
        """
        Get specific incident by ID
        
        Args:
            incident_id: Incident identifier
            
        Returns:
            Incident or None if not found
        """
        incidents = self.load_incidents()
        for incident in incidents:
            if incident.incident_id == incident_id:
                return incident
        return None
    
    def get_incidents_by_priority(self, priority: str) -> List[PagerDutyIncident]:
        """
        Get incidents filtered by priority
        
        Args:
            priority: Priority level (P1, P2, P3, P4, P5)
            
        Returns:
            List of incidents matching priority
        """
        incidents = self.load_incidents()
        return [inc for inc in incidents if inc.priority == priority]
    
    def get_incidents_by_service(self, service: str) -> List[PagerDutyIncident]:
        """
        Get incidents filtered by service
        
        Args:
            service: Service name
            
        Returns:
            List of incidents for service
        """
        incidents = self.load_incidents()
        return [inc for inc in incidents if inc.service == service]
    
    def get_incident_statistics(self) -> Dict[str, Any]:
        """
        Get incident statistics
        
        Returns:
            Dictionary with incident stats
        """
        incidents = self.load_incidents()
        
        if not incidents:
            return {
                "total_incidents": 0,
                "by_priority": {},
                "by_status": {},
                "total_affected_users": 0,
                "avg_resolution_hours": 0
            }
        
        by_priority = {}
        by_status = {}
        total_affected = 0
        total_duration = 0
        
        for incident in incidents:
            # Count by priority
            by_priority[incident.priority] = by_priority.get(incident.priority, 0) + 1
            
            # Count by status
            by_status[incident.status] = by_status.get(incident.status, 0) + 1
            
            # Sum affected users
            total_affected += incident.affected_users
            
            # Sum duration
            total_duration += incident.duration_hours
        
        return {
            "total_incidents": len(incidents),
            "by_priority": by_priority,
            "by_status": by_status,
            "total_affected_users": total_affected,
            "avg_resolution_hours": round(total_duration / len(incidents), 2)
        }
    
    def clear_cache(self):
        """Clear incidents cache"""
        self._incidents_cache = None


# Singleton instance
_pagerduty_service = None


def get_pagerduty_service() -> PagerDutyService:
    """Get or create PagerDuty service singleton"""
    global _pagerduty_service
    if _pagerduty_service is None:
        _pagerduty_service = PagerDutyService()
    return _pagerduty_service

# Made with Bob
