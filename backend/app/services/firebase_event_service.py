"""
Firebase Event Service
Handles realtime event storage and streaming for autonomous compliance monitoring
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.models.event_models import (
    Incident, ReasoningLog, CrewEvent, FinancialExposureSnapshot,
    Alert, IncidentStatus, CrewExecutionStatus
)

logger = logging.getLogger(__name__)


class FirebaseEventService:
    """
    Service for managing realtime events in Firestore
    Acts as the event bus for the autonomous compliance system
    """
    
    def __init__(self, firestore_client=None):
        """Initialize with optional Firestore client"""
        self.db = firestore_client
        self._in_memory_store = {
            'incidents': {},
            'reasoning_logs': {},
            'crew_events': {},
            'financial_snapshots': {},
            'alerts': {}
        }
    
    # ========================================================================
    # INCIDENT OPERATIONS
    # ========================================================================
    
    async def create_incident(self, incident: Incident) -> str:
        """
        Create new incident in Firestore
        Triggers realtime updates to connected clients
        """
        try:
            incident_dict = incident.model_dump(mode='json')
            incident_dict['created_at'] = datetime.utcnow().isoformat()
            incident_dict['updated_at'] = datetime.utcnow().isoformat()
            
            if self.db:
                doc_ref = self.db.collection('incidents').document(incident.incident_id)
                doc_ref.set(incident_dict)
                logger.info(f"Created incident in Firestore: {incident.incident_id}")
            else:
                self._in_memory_store['incidents'][incident.incident_id] = incident_dict
                logger.info(f"Created incident in memory: {incident.incident_id}")
            
            return incident.incident_id
            
        except Exception as e:
            logger.error(f"Failed to create incident: {e}")
            raise
    
    async def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> bool:
        """Update incident with new data"""
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            if self.db:
                doc_ref = self.db.collection('incidents').document(incident_id)
                doc_ref.update(updates)
                logger.info(f"Updated incident: {incident_id}")
            else:
                if incident_id in self._in_memory_store['incidents']:
                    self._in_memory_store['incidents'][incident_id].update(updates)
                    logger.info(f"Updated incident in memory: {incident_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update incident: {e}")
            return False
    
    async def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get incident by ID"""
        try:
            if self.db:
                doc_ref = self.db.collection('incidents').document(incident_id)
                doc = doc_ref.get()
                return doc.to_dict() if doc.exists else None
            else:
                return self._in_memory_store['incidents'].get(incident_id)
                
        except Exception as e:
            logger.error(f"Failed to get incident: {e}")
            return None
    
    async def get_active_incidents(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all active incidents"""
        try:
            if self.db:
                docs = self.db.collection('incidents')\
                    .where('status', 'in', ['OPEN', 'ACKNOWLEDGED', 'INVESTIGATING'])\
                    .order_by('created_at', direction='DESCENDING')\
                    .limit(limit)\
                    .stream()
                return [doc.to_dict() for doc in docs]
            else:
                incidents = list(self._in_memory_store['incidents'].values())
                active = [i for i in incidents if i.get('status') in ['OPEN', 'ACKNOWLEDGED', 'INVESTIGATING']]
                return sorted(active, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
                
        except Exception as e:
            logger.error(f"Failed to get active incidents: {e}")
            return []
    
    # ========================================================================
    # REASONING LOG OPERATIONS
    # ========================================================================
    
    async def add_reasoning_log(self, log: ReasoningLog) -> str:
        """
        Add reasoning log entry
        Streams to frontend in realtime
        """
        try:
            log_dict = log.model_dump(mode='json')
            log_dict['timestamp'] = datetime.utcnow().isoformat()
            
            if self.db:
                doc_ref = self.db.collection('reasoning_logs').document(log.log_id)
                doc_ref.set(log_dict)
                logger.debug(f"Added reasoning log: {log.log_id}")
            else:
                if log.incident_id not in self._in_memory_store['reasoning_logs']:
                    self._in_memory_store['reasoning_logs'][log.incident_id] = []
                self._in_memory_store['reasoning_logs'][log.incident_id].append(log_dict)
                logger.debug(f"Added reasoning log in memory: {log.log_id}")
            
            return log.log_id
            
        except Exception as e:
            logger.error(f"Failed to add reasoning log: {e}")
            raise
    
    async def get_reasoning_logs(self, incident_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get reasoning logs for incident"""
        try:
            if self.db:
                docs = self.db.collection('reasoning_logs')\
                    .where('incident_id', '==', incident_id)\
                    .order_by('timestamp', direction='ASCENDING')\
                    .limit(limit)\
                    .stream()
                return [doc.to_dict() for doc in docs]
            else:
                logs = self._in_memory_store['reasoning_logs'].get(incident_id, [])
                return sorted(logs, key=lambda x: x.get('timestamp', ''))[:limit]
                
        except Exception as e:
            logger.error(f"Failed to get reasoning logs: {e}")
            return []
    
    # ========================================================================
    # CREW EVENT OPERATIONS
    # ========================================================================
    
    async def add_crew_event(self, event: CrewEvent) -> str:
        """Add CrewAI execution event"""
        try:
            event_dict = event.model_dump(mode='json')
            event_dict['timestamp'] = datetime.utcnow().isoformat()
            
            if self.db:
                doc_ref = self.db.collection('crew_events').document(event.event_id)
                doc_ref.set(event_dict)
                logger.debug(f"Added crew event: {event.event_id}")
            else:
                if event.crew_execution_id not in self._in_memory_store['crew_events']:
                    self._in_memory_store['crew_events'][event.crew_execution_id] = []
                self._in_memory_store['crew_events'][event.crew_execution_id].append(event_dict)
                logger.debug(f"Added crew event in memory: {event.event_id}")
            
            return event.event_id
            
        except Exception as e:
            logger.error(f"Failed to add crew event: {e}")
            raise
    
    async def get_crew_events(self, crew_execution_id: str) -> List[Dict[str, Any]]:
        """Get all events for a crew execution"""
        try:
            if self.db:
                docs = self.db.collection('crew_events')\
                    .where('crew_execution_id', '==', crew_execution_id)\
                    .order_by('timestamp', direction='ASCENDING')\
                    .stream()
                return [doc.to_dict() for doc in docs]
            else:
                return self._in_memory_store['crew_events'].get(crew_execution_id, [])
                
        except Exception as e:
            logger.error(f"Failed to get crew events: {e}")
            return []
    
    # ========================================================================
    # FINANCIAL EXPOSURE OPERATIONS
    # ========================================================================
    
    async def create_financial_snapshot(self, snapshot: FinancialExposureSnapshot) -> str:
        """Create financial exposure snapshot"""
        try:
            snapshot_dict = snapshot.model_dump(mode='json')
            snapshot_dict['timestamp'] = datetime.utcnow().isoformat()
            
            if self.db:
                doc_ref = self.db.collection('financial_snapshots').document(snapshot.snapshot_id)
                doc_ref.set(snapshot_dict)
                logger.info(f"Created financial snapshot: {snapshot.snapshot_id}")
            else:
                if snapshot.incident_id not in self._in_memory_store['financial_snapshots']:
                    self._in_memory_store['financial_snapshots'][snapshot.incident_id] = []
                self._in_memory_store['financial_snapshots'][snapshot.incident_id].append(snapshot_dict)
                logger.info(f"Created financial snapshot in memory: {snapshot.snapshot_id}")
            
            return snapshot.snapshot_id
            
        except Exception as e:
            logger.error(f"Failed to create financial snapshot: {e}")
            raise
    
    async def get_latest_financial_snapshot(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get latest financial snapshot for incident"""
        try:
            if self.db:
                docs = self.db.collection('financial_snapshots')\
                    .where('incident_id', '==', incident_id)\
                    .order_by('timestamp', direction='DESCENDING')\
                    .limit(1)\
                    .stream()
                snapshots = [doc.to_dict() for doc in docs]
                return snapshots[0] if snapshots else None
            else:
                snapshots = self._in_memory_store['financial_snapshots'].get(incident_id, [])
                return snapshots[-1] if snapshots else None
                
        except Exception as e:
            logger.error(f"Failed to get financial snapshot: {e}")
            return None
    # ========================================================================
    # COMPLIANCE REPORT OPERATIONS
    # ========================================================================
    
    async def save_compliance_report(
        self, 
        incident_id: str, 
        report_data: Dict[str, Any]
    ) -> str:
        """
        Save full compliance report for an incident
        This stores the detailed analysis from the compliance agent
        """
        try:
            report_id = f"report_{uuid.uuid4().hex[:8]}"
            report_dict = {
                'report_id': report_id,
                'incident_id': incident_id,
                'report_data': report_data,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if self.db:
                doc_ref = self.db.collection('compliance_reports').document(incident_id)
                doc_ref.set(report_dict)
                logger.info(f"Saved compliance report for incident: {incident_id}")
            else:
                if 'compliance_reports' not in self._in_memory_store:
                    self._in_memory_store['compliance_reports'] = {}
                self._in_memory_store['compliance_reports'][incident_id] = report_dict
                logger.info(f"Saved compliance report in memory: {incident_id}")
            
            return report_id
            
        except Exception as e:
            logger.error(f"Failed to save compliance report: {e}")
            raise
    
    async def get_compliance_report(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get compliance report for an incident"""
        try:
            if self.db:
                doc_ref = self.db.collection('compliance_reports').document(incident_id)
                doc = doc_ref.get()
                return doc.to_dict() if doc.exists else None
            else:
                if 'compliance_reports' not in self._in_memory_store:
                    self._in_memory_store['compliance_reports'] = {}
                return self._in_memory_store['compliance_reports'].get(incident_id)
                
        except Exception as e:
            logger.error(f"Failed to get compliance report: {e}")
            return None

    
    # ========================================================================
    # ALERT OPERATIONS
    # ========================================================================
    
    async def create_alert(self, alert: Alert) -> str:
        """Create system alert"""
        try:
            alert_dict = alert.model_dump(mode='json')
            alert_dict['created_at'] = datetime.utcnow().isoformat()
            
            if self.db:
                doc_ref = self.db.collection('alerts').document(alert.alert_id)
                doc_ref.set(alert_dict)
                logger.info(f"Created alert: {alert.alert_id}")
            else:
                self._in_memory_store['alerts'][alert.alert_id] = alert_dict
                logger.info(f"Created alert in memory: {alert.alert_id}")
            
            return alert.alert_id
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            raise
    
    async def get_active_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get active unresolved alerts"""
        try:
            if self.db:
                docs = self.db.collection('alerts')\
                    .where('resolved', '==', False)\
                    .order_by('created_at', direction='DESCENDING')\
                    .limit(limit)\
                    .stream()
                return [doc.to_dict() for doc in docs]
            else:
                alerts = list(self._in_memory_store['alerts'].values())
                active = [a for a in alerts if not a.get('resolved', False)]
                return sorted(active, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
                
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def generate_id(self, prefix: str = "") -> str:
        """Generate unique ID"""
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{unique_id}" if prefix else unique_id


# Singleton instance
_firebase_event_service = None


def get_firebase_event_service(firestore_client=None) -> FirebaseEventService:
    """Get or create Firebase event service singleton"""
    global _firebase_event_service
    if _firebase_event_service is None:
        _firebase_event_service = FirebaseEventService(firestore_client)
    return _firebase_event_service


# Made with Bob - Realtime Event Bus