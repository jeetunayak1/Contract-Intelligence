"""
Compliance Engine - Deterministic SLA Breach Detection
Pure mechanical comparison of operational metrics against SLA thresholds
NO AI reasoning, NO financial calculations, NO liability interpretation
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.models.breach_models import (
    Breach, BreachType, BreachSeverity, BreachMetrics, BreachDelta,
    BreachSummary, ComplianceBreachReport, IncidentMetrics
)
from app.models.contract_models import (
    ExtractedContract, IncidentSLA, AvailabilitySLA, QualityKPI
)

logger = logging.getLogger(__name__)


class ComplianceEngine:
    """
    Deterministic SLA breach detection engine
    Performs pure mechanical comparison without AI reasoning
    """
    
    def __init__(self):
        """Initialize compliance engine"""
        self.name = "Compliance Engine"
    
    def detect_breaches(
        self,
        contract: ExtractedContract,
        incidents: List[IncidentMetrics],
        uptime_percent: Optional[float] = None,
        kpi_metrics: Optional[Dict[str, float]] = None
    ) -> ComplianceBreachReport:
        """
        Detect all SLA breaches mechanically
        
        Args:
            contract: Extracted contract with compliance obligations
            incidents: List of incident metrics
            uptime_percent: Actual uptime percentage
            kpi_metrics: Actual KPI values
            
        Returns:
            Complete breach report
        """
        start_time = datetime.utcnow()
        breaches: List[Breach] = []
        
        # Check incident SLA breaches
        incident_breaches = self._check_incident_slas(
            contract.compliance_obligations.incident_slas,
            incidents
        )
        breaches.extend(incident_breaches)
        
        # Check availability SLA breaches
        if uptime_percent is not None:
            availability_breaches = self._check_availability_slas(
                contract.compliance_obligations.availability_slas,
                uptime_percent
            )
            breaches.extend(availability_breaches)
        
        # Check KPI breaches
        if kpi_metrics:
            kpi_breaches = self._check_kpi_slas(
                contract.compliance_obligations.quality_kpis,
                kpi_metrics
            )
            breaches.extend(kpi_breaches)
        
        # Calculate summary
        breach_summary = self._calculate_breach_summary(breaches)
        
        # Determine overall status
        overall_status = "BREACH" if breaches else "COMPLIANT"
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        return ComplianceBreachReport(
            contract_id=contract.contract_metadata.client_name or "UNKNOWN",
            overall_status=overall_status,
            breach_summary=breach_summary,
            breaches=breaches,
            total_slas_checked=(
                len(contract.compliance_obligations.incident_slas) +
                len(contract.compliance_obligations.availability_slas) +
                len(contract.compliance_obligations.quality_kpis)
            ),
            total_incidents_analyzed=len(incidents),
            analysis_duration_seconds=duration
        )
    
    def _check_incident_slas(
        self,
        slas: List[IncidentSLA],
        incidents: List[IncidentMetrics]
    ) -> List[Breach]:
        """
        Check incident resolution times against SLA thresholds
        Pure deterministic comparison
        """
        breaches: List[Breach] = []
        
        for incident in incidents:
            # Find matching SLA tier by priority
            matching_sla = None
            for sla in slas:
                if sla.priority == incident.priority:
                    matching_sla = sla
                    break
            
            if not matching_sla:
                logger.warning(f"No SLA found for priority {incident.priority}")
                continue
            
            # Check resolution time breach
            if incident.resolution_hours and matching_sla.resolution_hours:
                if incident.resolution_hours > matching_sla.resolution_hours:
                    delta_hours = incident.resolution_hours - matching_sla.resolution_hours
                    
                    breach = Breach(
                        obligation_id=f"OBL-{incident.priority}-RESOLUTION",
                        sla_id=f"SLA-{incident.priority}-001",
                        breach_type=BreachType.INCIDENT_BREACH,
                        severity=self._map_priority_to_severity(incident.priority),
                        pagerduty_incidents=[incident.incident_id],
                        metrics=BreachMetrics(
                            resolution_actual_hours=incident.resolution_hours,
                            resolution_required_hours=matching_sla.resolution_hours
                        ),
                        delta=BreachDelta(
                            resolution_delta_hours=round(delta_hours, 2)
                        ),
                        summary=f"{incident.priority} resolution exceeded SLA target by {delta_hours:.1f} hours",
                        priority=incident.priority,
                        service=incident.service,
                        affected_users=incident.affected_users
                    )
                    breaches.append(breach)
            
            # Check acknowledgment time breach
            if incident.acknowledge_minutes and matching_sla.acknowledge_minutes:
                if incident.acknowledge_minutes > matching_sla.acknowledge_minutes:
                    delta_minutes = incident.acknowledge_minutes - matching_sla.acknowledge_minutes
                    
                    breach = Breach(
                        obligation_id=f"OBL-{incident.priority}-ACKNOWLEDGE",
                        sla_id=f"SLA-{incident.priority}-ACK",
                        breach_type=BreachType.INCIDENT_BREACH,
                        severity=self._map_priority_to_severity(incident.priority),
                        pagerduty_incidents=[incident.incident_id],
                        metrics=BreachMetrics(
                            acknowledge_actual_minutes=incident.acknowledge_minutes,
                            acknowledge_required_minutes=matching_sla.acknowledge_minutes
                        ),
                        delta=BreachDelta(
                            acknowledge_delta_minutes=delta_minutes
                        ),
                        summary=f"{incident.priority} acknowledgment exceeded SLA target by {delta_minutes} minutes",
                        priority=incident.priority,
                        service=incident.service,
                        affected_users=incident.affected_users
                    )
                    breaches.append(breach)
            
            # Check workaround time breach
            if incident.workaround_hours and matching_sla.workaround_hours:
                if incident.workaround_hours > matching_sla.workaround_hours:
                    delta_hours = incident.workaround_hours - matching_sla.workaround_hours
                    
                    breach = Breach(
                        obligation_id=f"OBL-{incident.priority}-WORKAROUND",
                        sla_id=f"SLA-{incident.priority}-WA",
                        breach_type=BreachType.INCIDENT_BREACH,
                        severity=self._map_priority_to_severity(incident.priority),
                        pagerduty_incidents=[incident.incident_id],
                        metrics=BreachMetrics(
                            workaround_actual_hours=incident.workaround_hours,
                            workaround_required_hours=matching_sla.workaround_hours
                        ),
                        delta=BreachDelta(
                            workaround_delta_hours=round(delta_hours, 2)
                        ),
                        summary=f"{incident.priority} workaround exceeded SLA target by {delta_hours:.1f} hours",
                        priority=incident.priority,
                        service=incident.service,
                        affected_users=incident.affected_users
                    )
                    breaches.append(breach)
        
        return breaches
    
    def _check_availability_slas(
        self,
        slas: List[AvailabilitySLA],
        actual_uptime: float
    ) -> List[Breach]:
        """
        Check uptime against availability SLA thresholds
        Pure deterministic comparison
        """
        breaches: List[Breach] = []
        
        for sla in slas:
            if sla.target_uptime_percent and actual_uptime < sla.target_uptime_percent:
                delta_percent = sla.target_uptime_percent - actual_uptime
                
                # Calculate downtime
                downtime_minutes = (100 - actual_uptime) * 43200 / 100  # 30 days in minutes
                
                breach = Breach(
                    obligation_id=f"OBL-UPTIME-{sla.tier}",
                    sla_id=f"SLA-UPTIME-{sla.tier}",
                    breach_type=BreachType.UPTIME_BREACH,
                    severity=BreachSeverity.HIGH if delta_percent > 0.5 else BreachSeverity.MEDIUM,
                    metrics=BreachMetrics(
                        uptime_actual=actual_uptime,
                        uptime_required=sla.target_uptime_percent,
                        downtime_minutes=downtime_minutes
                    ),
                    delta=BreachDelta(
                        uptime_delta_percent=round(delta_percent, 2)
                    ),
                    summary=f"Uptime fell below SLA threshold by {delta_percent:.2f}%",
                    service=sla.tier
                )
                breaches.append(breach)
        
        return breaches
    
    def _check_kpi_slas(
        self,
        kpis: List[QualityKPI],
        actual_metrics: Dict[str, float]
    ) -> List[Breach]:
        """
        Check KPIs against contract thresholds
        Pure deterministic comparison
        """
        breaches: List[Breach] = []
        
        for kpi in kpis:
            metric_name = kpi.metric.lower().replace(" ", "_")
            actual_value = actual_metrics.get(metric_name)
            
            if actual_value is None:
                continue
            
            # Check if below threshold
            if kpi.target_percent and actual_value < kpi.target_percent:
                delta_percent = kpi.target_percent - actual_value
                
                breach = Breach(
                    obligation_id=f"OBL-KPI-{metric_name.upper()}",
                    sla_id=f"SLA-KPI-{metric_name.upper()}",
                    breach_type=BreachType.KPI_BREACH,
                    severity=BreachSeverity.MEDIUM if delta_percent > 10 else BreachSeverity.LOW,
                    metrics=BreachMetrics(
                        kpi_actual=actual_value,
                        kpi_required=kpi.target_percent
                    ),
                    delta=BreachDelta(
                        kpi_delta_percent=round(delta_percent, 2)
                    ),
                    summary=f"{kpi.metric} below target by {delta_percent:.1f}%"
                )
                breaches.append(breach)
        
        return breaches
    
    def _map_priority_to_severity(self, priority: str) -> BreachSeverity:
        """Map incident priority to breach severity"""
        priority_map = {
            "P1": BreachSeverity.CRITICAL,
            "P2": BreachSeverity.HIGH,
            "P3": BreachSeverity.MEDIUM,
            "P4": BreachSeverity.LOW,
            "P5": BreachSeverity.LOW
        }
        return priority_map.get(priority, BreachSeverity.MEDIUM)
    
    def _calculate_breach_summary(self, breaches: List[Breach]) -> BreachSummary:
        """Calculate breach summary statistics"""
        critical = sum(1 for b in breaches if b.severity == BreachSeverity.CRITICAL)
        high = sum(1 for b in breaches if b.severity == BreachSeverity.HIGH)
        medium = sum(1 for b in breaches if b.severity == BreachSeverity.MEDIUM)
        low = sum(1 for b in breaches if b.severity == BreachSeverity.LOW)
        
        return BreachSummary(
            total_breaches=len(breaches),
            critical_breaches=critical,
            high_breaches=high,
            medium_breaches=medium,
            low_breaches=low
        )


# Singleton instance
_compliance_engine = None


def get_compliance_engine() -> ComplianceEngine:
    """Get or create compliance engine singleton"""
    global _compliance_engine
    if _compliance_engine is None:
        _compliance_engine = ComplianceEngine()
    return _compliance_engine


# Made with Bob - Deterministic Compliance Engine