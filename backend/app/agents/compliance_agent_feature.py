"""
Compliance Agent
Autonomous SLA breach detection and financial exposure calculation
"""
import os
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
import uuid

from google import genai
from google.genai import types

from ..models.contract_models import ExtractedContract, IncidentSLA, ServiceCredit, QualityKPI
from ..models.compliance_models import (
    ComplianceReport, IncidentAnalysis, KPIAnalysis, AvailabilityAnalysis,
    FinancialSummary, ReasoningStep, BreachSeverity, ComplianceStatus,
    PagerDutyIncident
)
from ..services.pagerduty_service import get_pagerduty_service
from ..services.jira_service import get_jira_service
from ..services.github_service import get_github_service
from ..services.compliance_engine import get_compliance_engine
from ..services.contract_data_service import get_contract_data_service
from ..models.breach_models import ComplianceBreachReport, IncidentMetrics
from ..core.config import Settings

logger = logging.getLogger(__name__)


class ComplianceAgent:
    """
    Autonomous Compliance Agent
    Detects SLA breaches, calculates financial exposure, applies liability exclusions
    """
    
    def __init__(self):
        """Initialize Compliance Agent"""
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.gemini_model_id = os.getenv("GEMINI_MODEL_ID", "gemini-1.5-pro")
        self.gemini_client = None
        
        if self.google_api_key:
            self._initialize_gemini()
        
        # Initialize services
        settings = Settings()
        self.pagerduty_service = get_pagerduty_service()
        self.jira_service = get_jira_service()
        self.github_service = get_github_service(
            access_token=settings.GITHUB_ACCESS_TOKEN,
            repo_name=settings.GITHUB_REPO_NAME
        )
        self.compliance_engine = get_compliance_engine()
        self.contract_service = get_contract_data_service()
        
        self.reasoning_stream: List[ReasoningStep] = []
    
    def _initialize_gemini(self):
        """Initialize Google GenAI client"""
        try:
            self.gemini_client = genai.Client(api_key=self.google_api_key)
            logger.info(f"Gemini client initialized for compliance reasoning")
        except Exception as exc:
            logger.exception(f"Failed to initialize Gemini client: {exc}")
            self.gemini_client = None
    
    def _add_reasoning(self, message: str, level: str = "INFO", metadata: Dict[str, Any] = None):
        """Add reasoning step to stream"""
        step = ReasoningStep(
            timestamp=datetime.utcnow().isoformat(),
            message=message,
            level=level,
            metadata=metadata or {}
        )
        self.reasoning_stream.append(step)
        logger.info(f"[REASONING] {message}")
    
    async def analyze_single_incident(
        self,
        incident_data: Dict[str, Any],
        contract_data: ExtractedContract,
        monthly_fee: float = 100000.0
    ) -> ComplianceReport:
        """
        Analyze a single incident against contract SLAs
        
        Args:
            incident_data: Single incident to analyze (from GitHub/PagerDuty)
            contract_data: Extracted contract with SLA obligations
            monthly_fee: Monthly contract value for financial calculations
            
        Returns:
            Compliance report for the single incident
        """
        self.reasoning_stream = []
        report_id = f"compliance_{uuid.uuid4().hex[:12]}"
        
        self._add_reasoning("🚀 Starting Single Incident Compliance Analysis")
        self._add_reasoning(f"Incident: {incident_data.get('title', 'Unknown')}")
        self._add_reasoning(f"Priority: {incident_data.get('priority', 'Unknown')}")
        self._add_reasoning(f"Contract Provider: {contract_data.contract_metadata.provider_name}")
        self._add_reasoning(f"Monthly Fee Basis: ${monthly_fee:,.2f}")
        
        # Convert incident data to PagerDutyIncident format for analysis
        from datetime import datetime, timedelta
        
        # Calculate duration (assume incident just started if no duration provided)
        duration_hours = incident_data.get('duration_hours', 0.5)  # Default 30 minutes
        
        pagerduty_incident = PagerDutyIncident(
            incident_id=incident_data.get('incident_id', 'unknown'),
            title=incident_data.get('title', 'Unknown Incident'),
            priority=incident_data.get('priority', 'P3'),
            service=incident_data.get('service', 'unknown-service'),
            status=incident_data.get('status', 'OPEN'),
            created_at=incident_data.get('created_at', datetime.utcnow().isoformat()),
            resolved_at=incident_data.get('resolved_at', ''),
            duration_hours=duration_hours,
            acknowledged_minutes=None,  # Not yet acknowledged
            workaround_hours=None,  # No workaround yet
            affected_users=incident_data.get('affected_users', 0),
            root_cause=incident_data.get('root_cause', 'under_investigation'),
            description=incident_data.get('description', '')
        )
        
        self._add_reasoning(f"📊 Analyzing incident: {pagerduty_incident.incident_id}")
        
        # Analyze the single incident
        incident_analyses = []
        analysis = await self._analyze_incident(
            pagerduty_incident,
            contract_data.incident_slas,
            contract_data.service_credits,
            contract_data.liability_exclusions,
            monthly_fee
        )
        incident_analyses.append(analysis)
        
        total_incident_exposure = analysis.financial_exposure if analysis.breach_detected else 0.0
        total_waived = analysis.waived_amount if analysis.liability_exclusion_applied else 0.0
        breached_count = 1 if analysis.breach_detected else 0
        waived_count = 1 if analysis.liability_exclusion_applied else 0
        
        # For single incident, skip KPI and availability analysis
        kpi_analyses = []
        availability_analyses = []
        availability_exposure = 0.0
        
        # Calculate financial summary
        total_exposure = total_incident_exposure + availability_exposure
        net_exposure = total_exposure - total_waived
        
        financial_summary = FinancialSummary(
            total_estimated_exposure=total_exposure,
            total_waived_penalties=total_waived,
            net_exposure=net_exposure,
            monthly_fee_basis=monthly_fee,
            exposure_percentage=round((net_exposure / monthly_fee) * 100, 2) if monthly_fee > 0 else 0.0,
            incidents_with_exposure=breached_count,
            incidents_waived=waived_count,
            availability_penalties=availability_exposure,
            incident_penalties=total_incident_exposure
        )
        
        # Determine overall status and severity
        if breached_count > 0 and waived_count == 0:
            overall_status = ComplianceStatus.BREACH
            breach_severity = BreachSeverity.HIGH if total_incident_exposure > monthly_fee * 0.05 else BreachSeverity.MEDIUM
        elif breached_count > 0 and waived_count > 0:
            overall_status = ComplianceStatus.WAIVED
            breach_severity = BreachSeverity.LOW
        else:
            overall_status = ComplianceStatus.COMPLIANT
            breach_severity = BreachSeverity.NONE
        
        self._add_reasoning(f"✅ Analysis Complete - Status: {overall_status.value}")
        self._add_reasoning(f"💰 Financial Exposure: ${net_exposure:,.2f}")
        
        return ComplianceReport(
            report_id=report_id,
            contract_id=contract_data.contract_metadata.contract_id or "unknown",
            generated_at=datetime.utcnow().isoformat(),
            incident_analysis=incident_analyses,
            kpi_analysis=kpi_analyses,
            availability_analysis=availability_analyses,
            financial_summary=financial_summary,
            overall_status=overall_status,
            breach_severity=breach_severity,
            reasoning_stream=self.reasoning_stream,
            total_incidents=1,
            breached_incidents=breached_count,
            waived_incidents=waived_count,
            breached_kpis=0,
            total_kpis=0
        )
    
    async def analyze_compliance(
        self,
        contract_data: ExtractedContract,
        monthly_fee: float = 100000.0
    ) -> ComplianceReport:
        """
        Run complete compliance analysis (all incidents)
        
        Args:
            contract_data: Extracted contract with SLA obligations
            monthly_fee: Monthly contract value for financial calculations
            
        Returns:
            Complete compliance report
        """
        self.reasoning_stream = []
        report_id = f"compliance_{uuid.uuid4().hex[:12]}"
        
        self._add_reasoning("🚀 Starting Autonomous Compliance Analysis")
        self._add_reasoning(f"Contract Provider: {contract_data.contract_metadata.provider_name}")
        self._add_reasoning(f"Monthly Fee Basis: ${monthly_fee:,.2f}")
        
        # Load operational data
        incidents = self.pagerduty_service.load_incidents()
        metrics = self.jira_service.load_metrics()
        
        self._add_reasoning(f"📊 Loaded {len(incidents)} PagerDuty incidents")
        self._add_reasoning(f"📈 Loaded Jira operational metrics")
        
        # Analyze incidents
        incident_analyses = []
        total_incident_exposure = 0.0
        total_waived = 0.0
        breached_count = 0
        waived_count = 0
        
        for incident in incidents:
            analysis = await self._analyze_incident(
                incident,
                contract_data.incident_slas,
                contract_data.service_credits,
                contract_data.liability_exclusions,
                monthly_fee
            )
            incident_analyses.append(analysis)
            
            if analysis.breach_detected:
                breached_count += 1
                total_incident_exposure += analysis.financial_exposure
                
                if analysis.liability_exclusion_applied:
                    waived_count += 1
                    total_waived += analysis.waived_amount
        
        # Analyze KPIs
        kpi_analyses = await self._analyze_kpis(
            contract_data.quality_kpis,
            metrics.quality_metrics
        )
        
        breached_kpis = sum(1 for kpi in kpi_analyses if kpi.breach_detected)
        
        # Analyze availability
        availability_analyses = await self._analyze_availability(
            contract_data.availability_slas,
            metrics.performance_metrics,
            contract_data.service_credits,
            monthly_fee
        )
        
        availability_exposure = sum(a.financial_exposure for a in availability_analyses)
        
        # Calculate financial summary
        total_exposure = total_incident_exposure + availability_exposure
        net_exposure = total_exposure - total_waived
        
        financial_summary = FinancialSummary(
            total_estimated_exposure=total_exposure,
            total_waived_penalties=total_waived,
            net_exposure=net_exposure,
            monthly_fee_basis=monthly_fee,
            exposure_percentage=round((net_exposure / monthly_fee) * 100, 2),
            incidents_with_exposure=breached_count,
            incidents_waived=waived_count,
            availability_penalties=availability_exposure,
            incident_penalties=total_incident_exposure
        )
        
        # Determine overall status
        overall_status, breach_severity = self._determine_overall_status(
            breached_count,
            waived_count,
            breached_kpis,
            net_exposure,
            monthly_fee
        )
        
        self._add_reasoning(f"💰 Total Financial Exposure: ${total_exposure:,.2f}")
        self._add_reasoning(f"✅ Waived Penalties: ${total_waived:,.2f}")
        self._add_reasoning(f"⚠️  Net Exposure: ${net_exposure:,.2f} ({financial_summary.exposure_percentage}%)")
        self._add_reasoning(f"📋 Overall Status: {overall_status.value}")
        
        # Generate AI reasoning summary
        if self.gemini_client:
            await self._generate_ai_summary(
                incident_analyses,
                kpi_analyses,
                financial_summary
            )
        
        return ComplianceReport(
            report_id=report_id,
            generated_at=datetime.utcnow().isoformat(),
            contract_id=contract_data.contract_metadata.contract_id or "unknown",
            overall_status=overall_status,
            breach_severity=breach_severity,
            incident_analysis=incident_analyses,
            kpi_analysis=kpi_analyses,
            availability_analysis=availability_analyses,
            financial_summary=financial_summary,
            reasoning_stream=self.reasoning_stream,
            total_incidents=len(incidents),
            breached_incidents=breached_count,
            waived_incidents=waived_count,
            breached_kpis=breached_kpis,
            total_kpis=len(kpi_analyses)
        )
    
    async def _analyze_incident(
        self,
        incident: PagerDutyIncident,
        slas: List[IncidentSLA],
        service_credits: List[ServiceCredit],
        liability_exclusions: List[str],
        monthly_fee: float
    ) -> IncidentAnalysis:
        """Analyze single incident against SLA"""
        
        self._add_reasoning(f"🔍 Analyzing Incident: {incident.incident_id} ({incident.priority})")
        
        # Find matching SLA
        matching_sla = None
        for sla in slas:
            if sla.priority == incident.priority:
                matching_sla = sla
                break
        
        if not matching_sla:
            self._add_reasoning(f"⚠️  No SLA found for priority {incident.priority}", "WARNING")
            return self._create_no_sla_analysis(incident)
        
        # Check for breach
        breach_detected = False
        breach_type = None
        
        if matching_sla.resolution_hours and incident.duration_hours > matching_sla.resolution_hours:
            breach_detected = True
            breach_type = "resolution"
            self._add_reasoning(
                f"🚨 SLA BREACH: Resolution time {incident.duration_hours}h exceeds target {matching_sla.resolution_hours}h",
                "ERROR"
            )
        
        # Check liability exclusions
        liability_exclusion_applied = False
        exclusion_reason = None
        
        if breach_detected:
            self._add_reasoning("🔎 Checking liability exclusions...")
            
            for exclusion in liability_exclusions:
                if self._matches_exclusion(incident.root_cause, exclusion):
                    liability_exclusion_applied = True
                    exclusion_reason = exclusion
                    self._add_reasoning(
                        f"✅ Liability exclusion applied: {exclusion}",
                        "INFO"
                    )
                    break
            
            if not liability_exclusion_applied:
                self._add_reasoning("❌ No liability exclusion applies", "WARNING")
        
        # Calculate financial exposure
        financial_exposure = 0.0
        waived_amount = 0.0
        
        if breach_detected:
            # Find matching service credit
            for credit in service_credits:
                if credit.priority == incident.priority and "Resolution" in credit.breach_condition:
                    financial_exposure = monthly_fee * (credit.credit_percent / 100)
                    
                    if liability_exclusion_applied:
                        waived_amount = financial_exposure
                        financial_exposure = 0.0
                    
                    break
        
        # Determine severity
        severity = self._calculate_breach_severity(
            breach_detected,
            incident.priority,
            incident.affected_users,
            financial_exposure
        )
        
        # Generate reasoning
        reasoning = self._generate_incident_reasoning(
            incident,
            matching_sla,
            breach_detected,
            liability_exclusion_applied,
            exclusion_reason,
            financial_exposure,
            waived_amount
        )
        
        return IncidentAnalysis(
            incident_id=incident.incident_id,
            priority=incident.priority,
            service=incident.service,
            title=incident.title,
            breach_detected=breach_detected,
            sla_target_hours=matching_sla.resolution_hours,
            actual_resolution_hours=incident.duration_hours,
            acknowledge_target_minutes=matching_sla.acknowledge_minutes,
            actual_acknowledge_minutes=incident.acknowledged_minutes,
            workaround_target_hours=matching_sla.workaround_hours,
            actual_workaround_hours=incident.workaround_hours,
            root_cause=incident.root_cause,
            liability_exclusion_applied=liability_exclusion_applied,
            exclusion_reason=exclusion_reason,
            financial_exposure=financial_exposure,
            waived_amount=waived_amount,
            breach_severity=severity,
            reasoning=reasoning,
            affected_users=incident.affected_users
        )
    
    def _matches_exclusion(self, root_cause: str, exclusion: str) -> bool:
        """Check if root cause matches liability exclusion"""
        # Normalize strings
        root_cause_normalized = root_cause.lower().replace("_", " ").replace("-", " ")
        exclusion_normalized = exclusion.lower().replace("_", " ").replace("-", " ")
        
        # Check for keyword matches
        root_cause_words = set(root_cause_normalized.split())
        exclusion_words = set(exclusion_normalized.split())
        
        # If significant overlap, consider it a match
        overlap = root_cause_words & exclusion_words
        return len(overlap) >= 2
    
    async def _analyze_kpis(
        self,
        contract_kpis: List[QualityKPI],
        actual_metrics: Dict[str, Any]
    ) -> List[KPIAnalysis]:
        """Analyze KPIs against contract thresholds"""
        
        self._add_reasoning("📊 Analyzing Quality KPIs")
        
        analyses = []
        
        for kpi in contract_kpis:
            # Map contract KPI to actual metric
            actual_value = self._get_actual_kpi_value(kpi.metric, actual_metrics)
            
            if actual_value is None:
                continue
            
            target = kpi.target_percent or kpi.target_value
            if target is None:
                continue
            
            # Check for breach
            breach_detected = False
            variance = 0.0
            
            if kpi.target_percent:
                variance = actual_value - target
                breach_detected = actual_value < target
            
            severity = BreachSeverity.NONE
            if breach_detected:
                if abs(variance) > 20:
                    severity = BreachSeverity.CRITICAL
                elif abs(variance) > 10:
                    severity = BreachSeverity.HIGH
                elif abs(variance) > 5:
                    severity = BreachSeverity.MEDIUM
                else:
                    severity = BreachSeverity.LOW
            
            reasoning = f"Target: {target}%, Actual: {actual_value}%, Variance: {variance:+.1f}%"
            
            if breach_detected:
                self._add_reasoning(f"⚠️  KPI Breach: {kpi.metric} - {reasoning}", "WARNING")
            
            analyses.append(KPIAnalysis(
                metric=kpi.metric,
                target=target,
                actual=actual_value,
                breach_detected=breach_detected,
                variance_percent=variance,
                severity=severity,
                reasoning=reasoning
            ))
        
        return analyses
    
    def _get_actual_kpi_value(self, metric_name: str, metrics: Dict[str, Any]) -> float | None:
        """Map contract KPI name to actual metric value"""
        metric_map = {
            "Unit Test Coverage": "unit_test_coverage",
            "Code Review Coverage": "code_review_coverage",
            "Critical/High Security Vulnerabilities": "security_vulnerabilities_critical",
            "Documentation Completeness (ADRs/API)": "documentation_completeness",
            "Sprint Velocity Variance": "sprint_velocity_variance"
        }
        
        metric_key = metric_map.get(metric_name)
        if metric_key:
            return metrics.get(metric_key)
        return None
    
    async def _analyze_availability(
        self,
        availability_slas: List,
        performance_metrics: Dict[str, Any],
        service_credits: List[ServiceCredit],
        monthly_fee: float
    ) -> List[AvailabilityAnalysis]:
        """Analyze availability against SLA targets"""
        
        self._add_reasoning("🌐 Analyzing Availability SLAs")
        
        analyses = []
        
        tier_map = {
            "Tier 1 - Production": "availability_tier1",
            "Tier 2 - Staging/UAT": "availability_tier2",
            "Tier 3 - Dev/Test": "availability_tier3"
        }
        
        for sla in availability_slas:
            metric_key = tier_map.get(sla.tier)
            if not metric_key:
                continue
            
            actual_uptime = performance_metrics.get(metric_key, 100.0)
            target_uptime = sla.target_uptime_percent or 99.9
            
            breach_detected = actual_uptime < target_uptime
            
            # Calculate downtime
            downtime_minutes = ((100 - actual_uptime) / 100) * 43800  # minutes in month
            max_downtime = sla.max_downtime_minutes or 43.8
            
            # Calculate financial exposure
            financial_exposure = 0.0
            if breach_detected:
                # Find matching service credit
                for credit in service_credits:
                    if "Availability" in credit.breach_condition and sla.tier.startswith(credit.priority):
                        financial_exposure = monthly_fee * (credit.credit_percent / 100)
                        break
            
            severity = BreachSeverity.NONE
            if breach_detected:
                diff = target_uptime - actual_uptime
                if diff > 1.0:
                    severity = BreachSeverity.CRITICAL
                elif diff > 0.5:
                    severity = BreachSeverity.HIGH
                elif diff > 0.1:
                    severity = BreachSeverity.MEDIUM
                else:
                    severity = BreachSeverity.LOW
            
            if breach_detected:
                self._add_reasoning(
                    f"⚠️  Availability Breach: {sla.tier} - {actual_uptime}% < {target_uptime}%",
                    "WARNING"
                )
            
            analyses.append(AvailabilityAnalysis(
                tier=sla.tier,
                target_uptime_percent=target_uptime,
                actual_uptime_percent=actual_uptime,
                breach_detected=breach_detected,
                downtime_minutes=downtime_minutes,
                max_allowed_downtime_minutes=max_downtime,
                financial_exposure=financial_exposure,
                breach_severity=severity
            ))
        
        return analyses
    
    def _calculate_breach_severity(
        self,
        breach_detected: bool,
        priority: str,
        affected_users: int,
        financial_exposure: float
    ) -> BreachSeverity:
        """Calculate breach severity"""
        if not breach_detected:
            return BreachSeverity.NONE
        
        if priority == "P1" or affected_users > 10000 or financial_exposure > 5000:
            return BreachSeverity.CRITICAL
        elif priority == "P2" or affected_users > 5000 or financial_exposure > 2000:
            return BreachSeverity.HIGH
        elif priority == "P3" or affected_users > 1000:
            return BreachSeverity.MEDIUM
        else:
            return BreachSeverity.LOW
    
    def _determine_overall_status(
        self,
        breached_incidents: int,
        waived_incidents: int,
        breached_kpis: int,
        net_exposure: float,
        monthly_fee: float
    ) -> Tuple[ComplianceStatus, BreachSeverity]:
        """Determine overall compliance status"""
        
        exposure_percent = (net_exposure / monthly_fee) * 100
        
        if breached_incidents == 0 and breached_kpis == 0:
            return ComplianceStatus.COMPLIANT, BreachSeverity.NONE
        
        if breached_incidents > 0 and breached_incidents == waived_incidents:
            return ComplianceStatus.WAIVED, BreachSeverity.LOW
        
        if exposure_percent > 10 or breached_incidents > 3:
            return ComplianceStatus.BREACH, BreachSeverity.CRITICAL
        elif exposure_percent > 5 or breached_incidents > 1:
            return ComplianceStatus.BREACH, BreachSeverity.HIGH
        elif breached_kpis > 2:
            return ComplianceStatus.WARNING, BreachSeverity.MEDIUM
        else:
            return ComplianceStatus.WARNING, BreachSeverity.LOW
    
    def _generate_incident_reasoning(
        self,
        incident: PagerDutyIncident,
        sla: IncidentSLA,
        breach_detected: bool,
        exclusion_applied: bool,
        exclusion_reason: str | None,
        exposure: float,
        waived: float
    ) -> str:
        """Generate human-readable reasoning for incident"""
        
        parts = []
        parts.append(f"Incident {incident.incident_id} ({incident.priority})")
        parts.append(f"Target: {sla.resolution_hours}h, Actual: {incident.duration_hours}h")
        
        if breach_detected:
            parts.append("SLA BREACH DETECTED")
            parts.append(f"Root cause: {incident.root_cause}")
            
            if exclusion_applied:
                parts.append(f"Liability exclusion applied: {exclusion_reason}")
                parts.append(f"Penalty waived: ${waived:,.2f}")
            else:
                parts.append(f"Financial exposure: ${exposure:,.2f}")
        else:
            parts.append("SLA COMPLIANT")
        
        return " | ".join(parts)
    
    def _create_no_sla_analysis(self, incident: PagerDutyIncident) -> IncidentAnalysis:
        """Create analysis for incident with no matching SLA"""
        return IncidentAnalysis(
            incident_id=incident.incident_id,
            priority=incident.priority,
            service=incident.service,
            title=incident.title,
            breach_detected=False,
            sla_target_hours=None,
            actual_resolution_hours=incident.duration_hours,
            acknowledge_target_minutes=None,
            actual_acknowledge_minutes=incident.acknowledged_minutes,
            workaround_target_hours=None,
            actual_workaround_hours=incident.workaround_hours,
            root_cause=incident.root_cause,
            liability_exclusion_applied=False,
            exclusion_reason=None,
            financial_exposure=0.0,
            waived_amount=0.0,
            breach_severity=BreachSeverity.NONE,
            reasoning="No matching SLA found for this priority level",
            affected_users=incident.affected_users
        )
    
    async def _generate_ai_summary(
        self,
        incident_analyses: List[IncidentAnalysis],
        kpi_analyses: List[KPIAnalysis],
        financial_summary: FinancialSummary
    ):
        """Generate AI-powered executive summary"""
        
        self._add_reasoning("🤖 Generating AI Executive Summary")
        
        try:
            prompt = f"""You are an AI compliance analyst. Provide a brief executive summary of this compliance analysis.

Incidents Analyzed: {len(incident_analyses)}
Breached: {sum(1 for i in incident_analyses if i.breach_detected)}
Waived: {sum(1 for i in incident_analyses if i.liability_exclusion_applied)}

KPIs Analyzed: {len(kpi_analyses)}
Breached: {sum(1 for k in kpi_analyses if k.breach_detected)}

Financial Exposure: ${financial_summary.total_estimated_exposure:,.2f}
Waived Penalties: ${financial_summary.total_waived_penalties:,.2f}
Net Exposure: ${financial_summary.net_exposure:,.2f}

Provide a 2-3 sentence executive summary focusing on key risks and liability exclusions."""

            import asyncio
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.gemini_client.models.generate_content,
                    model=self.gemini_model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.3)
                ),
                timeout=30.0
            )
            
            summary = getattr(response, "text", "")
            if summary:
                self._add_reasoning(f"📝 Executive Summary: {summary}")
        
        except Exception as e:
            logger.error(f"Failed to generate AI summary: {e}")
    
    async def analyze_with_engine(
        self,
        contract_id: str,
        monthly_fee: float = 100000.0
    ) -> ComplianceBreachReport:
        """
        Run deterministic compliance analysis using Compliance Engine
        NO AI reasoning - pure mechanical SLA comparison
        
        Args:
            contract_id: Contract identifier
            monthly_fee: Monthly contract value (for context only, not used in engine)
            
        Returns:
            Standardized breach report
        """
        logger.info(f"🔧 Starting deterministic compliance analysis for contract {contract_id}")
        
        # 1. Fetch contract obligations
        contract = await self.contract_service.get_extracted_contract(contract_id)
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")
        
        logger.info(f"✅ Contract loaded: {contract.contract_metadata.client_name}")
        logger.info(f"📊 SLAs: {len(contract.compliance_obligations.incident_slas)} incident, "
                   f"{len(contract.compliance_obligations.availability_slas)} availability, "
                   f"{len(contract.compliance_obligations.quality_kpis)} KPIs")
        
        # 2. Fetch operational metrics from GitHub (real data)
        logger.info("📊 Fetching incident metrics from GitHub...")
        incident_data = self.github_service.fetch_issue_metrics()
        incidents = [IncidentMetrics(**inc) for inc in incident_data]
        
        logger.info(f"📈 Loaded {len(incidents)} incidents from GitHub")
        
        # 3. Get uptime metrics from GitHub deployment data
        try:
            deployment_metrics = self.github_service.fetch_deployment_metrics()
            # Calculate uptime from deployment success rate
            total_deployments = deployment_metrics.get('total_deployments', 0)
            successful_deployments = deployment_metrics.get('successful_deployments', 0)
            uptime_percent = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 100.0
            logger.info(f"🌐 Calculated uptime from deployments: {uptime_percent:.2f}%")
        except Exception as e:
            logger.warning(f"Failed to calculate uptime from GitHub: {e}, using default 99.0%")
            uptime_percent = 99.0
        
        # 4. Get KPI metrics from Jira
        kpi_metrics = {}
        try:
            jira_metrics = self.jira_service.load_metrics()
            kpi_metrics = {
                'unit_test_coverage': jira_metrics.quality_metrics.get('unit_test_coverage', 0),
                'code_review_coverage': jira_metrics.quality_metrics.get('code_review_coverage', 0)
            }
            logger.info(f"📊 KPI Metrics: {kpi_metrics}")
        except Exception as e:
            logger.warning(f"Failed to load Jira metrics: {e}")
        
        # 5. Run deterministic breach detection
        logger.info("🔍 Running deterministic breach detection...")
        report = self.compliance_engine.detect_breaches(
            contract=contract,
            incidents=incidents,
            uptime_percent=uptime_percent,
            kpi_metrics=kpi_metrics
        )
        
        logger.info(f"✅ Analysis complete: {report.overall_status}")
        logger.info(f"📊 Total breaches: {report.breach_summary.total_breaches}")
        logger.info(f"🚨 Critical: {report.breach_summary.critical_breaches}, "
                   f"High: {report.breach_summary.high_breaches}, "
                   f"Medium: {report.breach_summary.medium_breaches}")
        
        return report


# Singleton instance
_compliance_agent = None


def get_compliance_agent() -> ComplianceAgent:
    """Get or create Compliance Agent singleton"""
    global _compliance_agent
    if _compliance_agent is None:
        _compliance_agent = ComplianceAgent()
    return _compliance_agent

# Made with Bob