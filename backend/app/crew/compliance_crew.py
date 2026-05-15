"""
Compliance Crew - Autonomous SLA Analysis
Orchestrates AI agents to analyze incidents against contract obligations
"""
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

try:
    from crewai import Agent, Crew, Process
    from langchain_google_genai import ChatGoogleGenerativeAI
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    logging.warning("CrewAI not installed. Using fallback compliance analysis.")

from app.crew.tasks import (
    create_compliance_analysis_task,
    create_liability_check_task,
    create_financial_impact_task,
    create_executive_summary_task,
    create_resolution_recommendation_task
)
from app.services.firebase_event_service import get_firebase_event_service
from app.services.incident_service import get_incident_service
from app.models.event_models import (
    CrewEvent, CrewEventType, ReasoningLog, ReasoningLogLevel,
    FinancialExposureSnapshot
)
from app.agents.compliance_agent import get_compliance_agent

logger = logging.getLogger(__name__)


class ComplianceCrew:
    """
    Autonomous compliance analysis crew
    Coordinates multiple AI agents to analyze SLA compliance
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize compliance crew"""
        self.event_service = get_firebase_event_service()
        self.incident_service = get_incident_service()
        self.gemini_api_key = gemini_api_key
        
        # Initialize LLM if CrewAI available
        self.llm = None
        if CREWAI_AVAILABLE and gemini_api_key:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=gemini_api_key,
                    temperature=0.3
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini LLM: {e}")
    
    async def analyze_incident(
        self,
        incident_id: str,
        contract_id: str,
        monthly_fee: float = 100000.0
    ) -> Dict[str, Any]:
        """
        Run autonomous compliance analysis on incident
        
        Args:
            incident_id: Incident to analyze
            contract_id: Contract with SLA obligations
            monthly_fee: Monthly contract fee for exposure calculation
            
        Returns:
            Complete compliance analysis results
        """
        crew_execution_id = f"crew_{uuid.uuid4().hex[:8]}"
        
        try:
            # Log crew start
            await self._log_crew_event(
                crew_execution_id=crew_execution_id,
                incident_id=incident_id,
                event_type=CrewEventType.CREW_STARTED,
                message="🚀 Starting autonomous compliance analysis crew"
            )
            
            await self._add_reasoning_log(
                incident_id=incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.INFO,
                message=f"🤖 Compliance Crew {crew_execution_id} activated for incident {incident_id}"
            )
            
            await self._add_reasoning_log(
                incident_id=incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.INFO,
                message=f"📋 Configuration: Contract={contract_id}, Monthly Fee=${monthly_fee:,.2f}"
            )
            
            # Update incident with crew execution ID
            try:
                await self.incident_service.start_sla_analysis(incident_id, crew_execution_id)
                await self._add_reasoning_log(
                    incident_id=incident_id,
                    crew_execution_id=crew_execution_id,
                    level=ReasoningLogLevel.INFO,
                    message="✅ Incident status updated to 'Analyzing'"
                )
            except Exception as e:
                await self._add_reasoning_log(
                    incident_id=incident_id,
                    crew_execution_id=crew_execution_id,
                    level=ReasoningLogLevel.WARNING,
                    message=f"⚠️  Failed to update incident status: {str(e)}"
                )
            
            # Get incident and contract data
            await self._add_reasoning_log(
                incident_id=incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.INFO,
                message="🔍 Fetching incident details..."
            )
            
            incident = await self.incident_service.get_incident(incident_id)
            if not incident:
                await self._add_reasoning_log(
                    incident_id=incident_id,
                    crew_execution_id=crew_execution_id,
                    level=ReasoningLogLevel.ERROR,
                    message=f"❌ Incident {incident_id} not found in database"
                )
                raise ValueError(f"Incident {incident_id} not found")
            
            await self._add_reasoning_log(
                incident_id=incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.INFO,
                message=f"✅ Incident loaded: {incident.title} (Priority: {incident.priority}, Service: {incident.service})"
            )
            
            await self._add_reasoning_log(
                incident_id=incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.INFO,
                message="🚀 Initiating 4-step compliance analysis pipeline..."
            )
            
            # For now, use existing compliance agent
            # In production, this would use CrewAI agents
            result = await self._run_analysis_with_existing_agent(
                incident=incident,
                contract_id=contract_id,
                monthly_fee=monthly_fee,
                crew_execution_id=crew_execution_id
            )
            
            # Log crew completion
            await self._log_crew_event(
                crew_execution_id=crew_execution_id,
                incident_id=incident_id,
                event_type=CrewEventType.CREW_COMPLETED,
                message="✅ Compliance analysis completed successfully"
            )
            
            await self._add_reasoning_log(
                incident_id=incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.SUCCESS,
                message=f"🎯 Analysis complete - Breach: {result.get('breach_detected', False)}"
            )
            
            # Update incident with results
            await self.incident_service.complete_sla_analysis(
                incident_id=incident_id,
                breach_detected=result.get('breach_detected', False),
                financial_exposure=result.get('financial_exposure', 0.0),
                penalty_waived=result.get('penalty_waived', False),
                waiver_reason=result.get('waiver_reason')
            )
            
            # Create financial snapshot
            await self._create_financial_snapshot(
                incident_id=incident_id,
                result=result
            )
            
            return {
                'success': True,
                'crew_execution_id': crew_execution_id,
                'incident_id': incident_id,
                'analysis': result
            }
            
        except ValueError as e:
            # Validation errors (incident not found, contract not found, etc.)
            logger.error(f"Validation error in crew execution: {e}", exc_info=True)
            
            await self._log_crew_event(
                crew_execution_id=crew_execution_id,
                incident_id=incident_id,
                event_type=CrewEventType.CREW_FAILED,
                message=f"❌ Validation Error: {str(e)}",
                error=f"ValueError: {str(e)}"
            )
            
            await self._add_reasoning_log(
                incident_id=incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.ERROR,
                message=f"💥 Validation Error: {str(e)}"
            )
            
            await self._add_reasoning_log(
                incident_id=incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.ERROR,
                message="🔧 Troubleshooting: Check that incident and contract exist in database"
            )
            
            return {
                'success': False,
                'crew_execution_id': crew_execution_id,
                'incident_id': incident_id,
                'error': str(e),
                'error_type': 'ValidationError'
            }
            
        except KeyError as e:
            # Missing data errors
            logger.error(f"Data structure error in crew execution: {e}", exc_info=True)
            
            await self._log_crew_event(
                crew_execution_id=crew_execution_id,
                incident_id=incident_id,
                event_type=CrewEventType.CREW_FAILED,
                message=f"❌ Data Structure Error: Missing key {str(e)}",
                error=f"KeyError: {str(e)}"
            )
            
            await self._add_reasoning_log(
                incident_id=incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.ERROR,
                message=f"💥 Data Structure Error: Missing required field {str(e)}"
            )
            
            await self._add_reasoning_log(
                incident_id=incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.ERROR,
                message="🔧 Troubleshooting: Contract data may be incomplete or malformed"
            )
            
            return {
                'success': False,
                'crew_execution_id': crew_execution_id,
                'incident_id': incident_id,
                'error': f"Missing required field: {str(e)}",
                'error_type': 'DataStructureError'
            }
            
        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error in crew execution: {e}", exc_info=True)
            
            await self._log_crew_event(
                crew_execution_id=crew_execution_id,
                incident_id=incident_id,
                event_type=CrewEventType.CREW_FAILED,
                message=f"❌ Unexpected Error: {str(e)}",
                error=f"{type(e).__name__}: {str(e)}"
            )
            
            await self._add_reasoning_log(
                incident_id=incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.ERROR,
                message=f"💥 Unexpected Error ({type(e).__name__}): {str(e)}"
            )
            
            await self._add_reasoning_log(
                incident_id=incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.ERROR,
                message="🔧 Troubleshooting: Check backend logs for full stack trace"
            )
            
            return {
                'success': False,
                'crew_execution_id': crew_execution_id,
                'incident_id': incident_id,
                'error': str(e)
            }
    
    async def _run_analysis_with_existing_agent(
        self,
        incident: Any,
        contract_id: str,
        monthly_fee: float,
        crew_execution_id: str
    ) -> Dict[str, Any]:
        """
        Run analysis using existing compliance agent
        This is a bridge until full CrewAI integration
        """
        # Step 1: Load Contract
        await self._add_reasoning_log(
            incident_id=incident.incident_id,
            crew_execution_id=crew_execution_id,
            level=ReasoningLogLevel.INFO,
            message="📊 [STEP 1/4] Loading contract SLA obligations...",
            agent="System",
            task="Contract Loading"
        )
        
        try:
            from app.services.contract_firestore import ContractFirestoreService
            contract_service = ContractFirestoreService()
            contract_doc = await contract_service.get_contract(contract_id)
            
            if not contract_doc:
                await self._add_reasoning_log(
                    incident_id=incident.incident_id,
                    crew_execution_id=crew_execution_id,
                    level=ReasoningLogLevel.ERROR,
                    message=f"❌ Contract {contract_id} not found in database",
                    agent="System",
                    task="Contract Loading"
                )
                raise ValueError(f"Contract {contract_id} not found")
            
            await self._add_reasoning_log(
                incident_id=incident.incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.INFO,
                message=f"✅ Contract loaded: {contract_doc.get('filename', 'Unknown')} ({len(contract_doc.get('extracted_data', {}).get('incident_slas', []))} SLA tiers)",
                agent="System",
                task="Contract Loading"
            )
        except Exception as e:
            await self._add_reasoning_log(
                incident_id=incident.incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.ERROR,
                message=f"❌ Failed to load contract: {str(e)}",
                agent="System",
                task="Contract Loading"
            )
            raise
        
        # Step 2: Parse Contract Data
        await self._add_reasoning_log(
            incident_id=incident.incident_id,
            crew_execution_id=crew_execution_id,
            level=ReasoningLogLevel.INFO,
            message="📋 [STEP 2/4] Parsing contract SLA obligations...",
            agent="System",
            task="Contract Parsing"
        )
        
        try:
            from app.models.contract_models import ExtractedContract
            contract = ExtractedContract(**contract_doc['extracted_data'])
            
            await self._add_reasoning_log(
                incident_id=incident.incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.INFO,
                message=f"✅ Parsed {len(contract.incident_slas)} incident SLAs, {len(contract.availability_slas)} availability SLAs",
                agent="System",
                task="Contract Parsing"
            )
        except Exception as e:
            await self._add_reasoning_log(
                incident_id=incident.incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.ERROR,
                message=f"❌ Failed to parse contract data: {str(e)}",
                agent="System",
                task="Contract Parsing"
            )
            raise
        
        # Step 3: Run Compliance Analysis
        await self._add_reasoning_log(
            incident_id=incident.incident_id,
            crew_execution_id=crew_execution_id,
            level=ReasoningLogLevel.INFO,
            message=f"🔍 [STEP 3/4] Running compliance analysis against {len(contract.incident_slas)} SLA tiers...",
            agent="Compliance Agent",
            task="SLA Breach Detection"
        )
        
        try:
            compliance_agent = get_compliance_agent()
            
            await self._add_reasoning_log(
                incident_id=incident.incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.INFO,
                message="🤖 Compliance Agent initialized, analyzing incident...",
                agent="Compliance Agent",
                task="SLA Breach Detection"
            )
            
            report = await compliance_agent.analyze_compliance(contract, monthly_fee)
            
            await self._add_reasoning_log(
                incident_id=incident.incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.INFO,
                message=f"✅ Compliance analysis complete - Analyzed {len(report.incident_analysis)} incidents",
                agent="Compliance Agent",
                task="SLA Breach Detection"
            )
        except Exception as e:
            await self._add_reasoning_log(
                incident_id=incident.incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.ERROR,
                message=f"❌ Compliance analysis failed: {str(e)}",
                agent="Compliance Agent",
                task="SLA Breach Detection"
            )
            raise
        
        # Step 4: Extract Incident Results
        await self._add_reasoning_log(
            incident_id=incident.incident_id,
            crew_execution_id=crew_execution_id,
            level=ReasoningLogLevel.INFO,
            message=f"💰 [STEP 4/4] Calculating financial impact and liability...",
            agent="Financial Impact Agent",
            task="Financial Exposure Calculation"
        )
        
        try:
            # Find analysis for this specific incident
            incident_analysis = None
            for analysis in report.incident_analysis:
                if analysis.incident_id == incident.incident_id:
                    incident_analysis = analysis
                    break
            
            if not incident_analysis:
                await self._add_reasoning_log(
                    incident_id=incident.incident_id,
                    crew_execution_id=crew_execution_id,
                    level=ReasoningLogLevel.WARNING,
                    message="⚠️  No specific analysis found for this incident, using default values",
                    agent="Financial Impact Agent",
                    task="Financial Exposure Calculation"
                )
                # Create synthetic analysis
                incident_analysis = {
                    'breach_detected': False,
                    'financial_exposure': 0.0,
                    'penalty_waived': False,
                    'waiver_reason': None
                }
            else:
                breach_status = "SLA BREACH DETECTED" if incident_analysis.breach_detected else "No breach"
                waiver_status = f" (WAIVED: {incident_analysis.exclusion_reason})" if incident_analysis.liability_exclusion_applied else ""
                
                await self._add_reasoning_log(
                    incident_id=incident.incident_id,
                    crew_execution_id=crew_execution_id,
                    level=ReasoningLogLevel.INFO if not incident_analysis.breach_detected else ReasoningLogLevel.WARNING,
                    message=f"📊 {breach_status}{waiver_status} - Financial exposure: ${incident_analysis.financial_exposure:,.2f}",
                    agent="Financial Impact Agent",
                    task="Financial Exposure Calculation"
                )
                
                incident_analysis = {
                    'breach_detected': incident_analysis.breach_detected,
                    'financial_exposure': incident_analysis.financial_exposure,
                    'penalty_waived': incident_analysis.liability_exclusion_applied,
                    'waiver_reason': incident_analysis.exclusion_reason if incident_analysis.liability_exclusion_applied else None
                }
            
            await self._add_reasoning_log(
                incident_id=incident.incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.INFO,
                message="✅ Financial impact analysis complete",
                agent="Financial Impact Agent",
                task="Financial Exposure Calculation"
            )
            
            return incident_analysis
            
        except Exception as e:
            await self._add_reasoning_log(
                incident_id=incident.incident_id,
                crew_execution_id=crew_execution_id,
                level=ReasoningLogLevel.ERROR,
                message=f"❌ Financial impact calculation failed: {str(e)}",
                agent="Financial Impact Agent",
                task="Financial Exposure Calculation"
            )
            raise
    
    async def _create_financial_snapshot(
        self,
        incident_id: str,
        result: Dict[str, Any]
    ):
        """Create financial exposure snapshot"""
        snapshot = FinancialExposureSnapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            total_exposure=result.get('financial_exposure', 0.0),
            waived_penalties=result.get('financial_exposure', 0.0) if result.get('penalty_waived') else 0.0,
            net_exposure=0.0 if result.get('penalty_waived') else result.get('financial_exposure', 0.0),
            sla_credits_applied=result.get('financial_exposure', 0.0),
            breach_count=1 if result.get('breach_detected') else 0,
            exposure_percentage=result.get('financial_exposure', 0.0) / 100000.0 * 100
        )
        
        await self.event_service.create_financial_snapshot(snapshot)
    
    async def _log_crew_event(
        self,
        crew_execution_id: str,
        incident_id: str,
        event_type: CrewEventType,
        message: str,
        agent_name: Optional[str] = None,
        task_name: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Log crew execution event"""
        event = CrewEvent(
            event_id=f"event_{uuid.uuid4().hex[:8]}",
            crew_execution_id=crew_execution_id,
            incident_id=incident_id,
            event_type=event_type,
            agent_name=agent_name,
            task_name=task_name,
            message=message,
            error=error
        )
        
        await self.event_service.add_crew_event(event)
    
    async def _add_reasoning_log(
        self,
        incident_id: str,
        crew_execution_id: str,
        level: ReasoningLogLevel,
        message: str,
        agent: Optional[str] = None,
        task: Optional[str] = None
    ):
        """Add reasoning log entry"""
        log = ReasoningLog(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            incident_id=incident_id,
            crew_execution_id=crew_execution_id,
            level=level,
            message=message,
            agent=agent,
            task=task
        )
        
        await self.event_service.add_reasoning_log(log)


# Singleton instance
_compliance_crew = None


def get_compliance_crew(gemini_api_key: Optional[str] = None) -> ComplianceCrew:
    """Get or create compliance crew singleton"""
    global _compliance_crew
    if _compliance_crew is None:
        _compliance_crew = ComplianceCrew(gemini_api_key)
    return _compliance_crew


# Made with Bob - Autonomous Compliance Crew