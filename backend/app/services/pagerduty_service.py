"""
PagerDuty Service
Loads and manages incident data
"""
import json
import os
from typing import List, Dict, Any, Optional
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
    
    def fetch_incident_metrics(self) -> List[Dict[str, Any]]:
        """
        Fetch operational metrics from PagerDuty incidents
        Converts PagerDuty incidents to standardized metric format
        
        Returns:
            List of incident metrics
        """
        incidents = self.load_incidents()
        
        metrics = []
        for incident in incidents:
            # Parse timestamps
            from datetime import datetime
            
            created_at = incident.created_at
            resolved_at = incident.resolved_at
            
            # Calculate durations
            resolution_hours = incident.duration_hours
            acknowledge_minutes = incident.acknowledged_minutes
            workaround_hours = incident.workaround_hours
            
            metrics.append({
                'incident_id': incident.incident_id,
                'priority': incident.priority,
                'service': incident.service,
                'title': incident.title,
                'created_at': created_at,
                'resolved_at': resolved_at,
                'acknowledged_at': None,  # Would need to calculate from acknowledged_minutes
                'workaround_at': None,  # Would need to calculate from workaround_hours
                'resolution_hours': resolution_hours,
                'acknowledge_minutes': acknowledge_minutes,
                'workaround_hours': workaround_hours,
                'affected_users': incident.affected_users,
                'downtime_minutes': resolution_hours * 60 if resolution_hours else None,
                'root_cause': incident.root_cause,
                'status': incident.status
            })
        
        logger.info(f"Fetched metrics for {len(metrics)} PagerDuty incidents")
        return metrics
    
    def get_uptime_metrics(self, service: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate uptime metrics from incidents
        
        Args:
            service: Filter by service name
            
        Returns:
            Uptime metrics
        """
        incidents = self.load_incidents()
        
        if service:
            incidents = [inc for inc in incidents if inc.service == service]
        
        # Calculate total downtime
        total_downtime_hours = sum(inc.duration_hours for inc in incidents)
        total_downtime_minutes = total_downtime_hours * 60
        
        # Assume 30-day period (43200 minutes)
        period_minutes = 43200
        uptime_minutes = period_minutes - total_downtime_minutes
        uptime_percent = (uptime_minutes / period_minutes) * 100
        
        return {
            'uptime_percent': round(uptime_percent, 2),
            'downtime_minutes': round(total_downtime_minutes, 2),
            'total_incidents': len(incidents),
            'period_days': 30,
            'service': service or 'all'
        }


# Singleton instance
_pagerduty_service = None


def get_pagerduty_service() -> PagerDutyService:
    """Get or create PagerDuty service singleton"""
    global _pagerduty_service
    if _pagerduty_service is None:
        _pagerduty_service = PagerDutyService()
    return _pagerduty_service

# Made with Bob
