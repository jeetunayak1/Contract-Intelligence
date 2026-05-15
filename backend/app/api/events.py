"""
Events API - Real GitHub Webhooks and Live Incident Feed
Handles incoming GitHub webhooks and provides realtime incident data
"""
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks, Query
from fastapi.responses import JSONResponse

from app.models.event_models import (
    GitHubWebhookPayload, WebhookResponse, LiveIncidentsFeed,
    LiveReasoningStream, CrewStatusResponse, Incident
)
from app.integrations.github_webhook import get_github_webhook_handler
from app.services.incident_service import get_incident_service
from app.services.firebase_event_service import get_firebase_event_service
from app.crew.compliance_crew import get_compliance_crew
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/events", tags=["events"])


# ============================================================================
# GITHUB WEBHOOK ENDPOINTS
# ============================================================================

@router.post("/github/webhook", response_model=WebhookResponse)
async def github_webhook(
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    """
    GitHub webhook endpoint
    Receives issue events and triggers autonomous compliance analysis
    
    Headers:
    - X-GitHub-Event: Event type (issues, issue_comment, etc.)
    - X-Hub-Signature-256: Webhook signature for verification
    """
    try:
        logger.info(f"Received GitHub webhook: {x_github_event}")
        
        # Get webhook handler
        webhook_handler = get_github_webhook_handler(
            webhook_secret=settings.GITHUB_WEBHOOK_SECRET
        )
        
        # Verify signature (if configured)
        # Note: In production, you'd verify the signature here
        # For now, we'll skip verification for development
        
        # Handle different event types
        if x_github_event == "issues":
            # Parse payload
            github_payload = GitHubWebhookPayload(**payload)
            
            # Handle issue event
            response = await webhook_handler.handle_issues_event(github_payload)
            
            # If analysis should be triggered, run it in background
            if response.triggered_analysis and response.incident_id:
                background_tasks.add_task(
                    trigger_compliance_analysis,
                    incident_id=response.incident_id,
                    contract_id=settings.DEFAULT_CONTRACT_ID or "contract_default",
                    monthly_fee=100000.0
                )
            
            return response
            
        elif x_github_event == "issue_comment":
            # Handle comment event
            response = await webhook_handler.handle_issue_comment_event(payload)
            return response
            
        else:
            return WebhookResponse(
                success=True,
                message=f"Event type '{x_github_event}' acknowledged but not processed",
                triggered_analysis=False
            )
            
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def trigger_compliance_analysis(
    incident_id: str,
    contract_id: str,
    monthly_fee: float
):
    """
    Background task to trigger compliance analysis
    Runs asynchronously to avoid blocking webhook response
    """
    # If contract_id is default/empty, try to get first available contract
    if not contract_id or contract_id == "contract_default":
        try:
            from app.services.contract_firestore import ContractFirestoreService
            from app.models.event_models import ReasoningLog, ReasoningLogLevel
            import uuid
            
            contract_service = ContractFirestoreService()
            contracts = await contract_service.get_all_contracts()
            if contracts:
                contract_id = contracts[0]['contract_id']
                logger.info(f"Using first available contract: {contract_id}")
            else:
                logger.error("No contracts found in database. Please upload a contract first.")
                # Log error to incident
                event_service = get_firebase_event_service()
                error_log = ReasoningLog(
                    log_id=f"log_{uuid.uuid4().hex[:8]}",
                    incident_id=incident_id,
                    crew_execution_id=None,
                    level=ReasoningLogLevel.ERROR,
                    message="❌ No contracts found. Please upload a contract via Contract Intelligence page first.",
                    agent=None,
                    task=None
                )
                await event_service.add_reasoning_log(error_log)
                return
        except Exception as e:
            logger.error(f"Failed to get contracts: {e}")
            return
    try:
        logger.info(f"Triggering compliance analysis for incident {incident_id}")
        
        crew = get_compliance_crew(gemini_api_key=settings.GOOGLE_API_KEY)
        result = await crew.analyze_incident(
            incident_id=incident_id,
            contract_id=contract_id,
            monthly_fee=monthly_fee
        )
        
        if result['success']:
            logger.info(f"Compliance analysis completed: {result['crew_execution_id']}")
        else:
            logger.error(f"Compliance analysis failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"Background analysis failed: {e}", exc_info=True)


# ============================================================================
# LIVE INCIDENT FEED ENDPOINTS
# ============================================================================

@router.get("/incidents/live", response_model=LiveIncidentsFeed)
async def get_live_incidents(
    limit: int = Query(50, ge=1, le=100),
    status: str = Query(None, description="Filter by status: OPEN, ACKNOWLEDGED, etc.")
):
    """
    Get live incident feed
    Returns active incidents with realtime updates
    """
    try:
        incident_service = get_incident_service()
        
        # Get active incidents
        incidents = await incident_service.get_active_incidents(limit=limit)
        
        # Filter by status if provided
        if status:
            incidents = [i for i in incidents if i.status.value == status]
        
        return LiveIncidentsFeed(
            total_incidents=len(incidents),
            active_incidents=len([i for i in incidents if i.status.value in ['OPEN', 'ACKNOWLEDGED', 'INVESTIGATING']]),
            incidents=incidents
        )
        
    except Exception as e:
        logger.error(f"Failed to get live incidents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get single incident by ID"""
    try:
        incident_service = get_incident_service()
        incident = await incident_service.get_incident(incident_id)
        
        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
        
        return incident
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get incident: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# REASONING STREAM ENDPOINTS
# ============================================================================

@router.get("/reasoning/{incident_id}", response_model=LiveReasoningStream)
async def get_reasoning_logs(
    incident_id: str,
    limit: int = Query(100, ge=1, le=500)
):
    """
    Get reasoning logs for incident
    Returns AI reasoning stream in chronological order
    """
    try:
        event_service = get_firebase_event_service()
        logs = await event_service.get_reasoning_logs(incident_id, limit=limit)
        
        # Convert to ReasoningLog objects
        from app.models.event_models import ReasoningLog
        reasoning_logs = [ReasoningLog(**log) for log in logs]
        
        return LiveReasoningStream(
            incident_id=incident_id,
            logs=reasoning_logs,
            total_logs=len(reasoning_logs)
        )
        
    except Exception as e:
        logger.error(f"Failed to get reasoning logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CREW STATUS ENDPOINTS
# ============================================================================

@router.get("/crew/{crew_execution_id}", response_model=CrewStatusResponse)
async def get_crew_status(crew_execution_id: str):
    """
    Get crew execution status
    Returns current state of autonomous analysis
    """
    try:
        event_service = get_firebase_event_service()
        
        # Get crew events
        events_data = await event_service.get_crew_events(crew_execution_id)
        
        if not events_data:
            raise HTTPException(
                status_code=404,
                detail=f"Crew execution {crew_execution_id} not found"
            )
        
        # Convert to CrewEvent objects
        from app.models.event_models import CrewEvent, CrewExecutionStatus
        events = [CrewEvent(**e) for e in events_data]
        
        # Determine status
        status = CrewExecutionStatus.RUNNING
        completed_at = None
        
        for event in events:
            if event.event_type.value == "CREW_COMPLETED":
                status = CrewExecutionStatus.COMPLETED
                completed_at = event.timestamp
            elif event.event_type.value == "CREW_FAILED":
                status = CrewExecutionStatus.FAILED
                completed_at = event.timestamp
        
        # Extract active agents and completed tasks
        active_agents = []
        completed_tasks = []
        
        for event in events:
            if event.agent_name and event.event_type.value == "AGENT_STARTED":
                if event.agent_name not in active_agents:
                    active_agents.append(event.agent_name)
            if event.task_name and event.event_type.value == "TASK_COMPLETED":
                if event.task_name not in completed_tasks:
                    completed_tasks.append(event.task_name)
        
        from datetime import datetime
        
        return CrewStatusResponse(
            crew_execution_id=crew_execution_id,
            incident_id=events[0].incident_id if events else "",
            status=status,
            started_at=events[0].timestamp if events else datetime.utcnow(),
            completed_at=completed_at,
            active_agents=active_agents,
            completed_tasks=completed_tasks,
            events=events
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get crew status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MANUAL TRIGGER ENDPOINTS
# ============================================================================

@router.post("/incidents/{incident_id}/analyze")
async def trigger_manual_analysis(
    incident_id: str,
    background_tasks: BackgroundTasks,
    contract_id: str = Query(..., description="Contract ID to analyze against"),
    monthly_fee: float = Query(100000.0, description="Monthly contract fee")
):
    """
    Manually trigger compliance analysis for an incident
    Useful for re-analysis or testing
    """
    try:
        # Verify incident exists
        incident_service = get_incident_service()
        incident = await incident_service.get_incident(incident_id)
        
        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
        
        # Trigger analysis in background
        background_tasks.add_task(
            trigger_compliance_analysis,
            incident_id=incident_id,
            contract_id=contract_id,
            monthly_fee=monthly_fee
        )
        
        return {
            "success": True,
            "message": f"Compliance analysis triggered for incident {incident_id}",
            "incident_id": incident_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/incidents/{incident_id}/compliance-report")
async def get_incident_compliance_report(incident_id: str):
    """
    Get full compliance report for an incident
    Returns detailed SLA analysis, breach detection, and financial exposure
    """
    try:
        event_service = get_firebase_event_service()
        report = await event_service.get_compliance_report(incident_id)
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail=f"Compliance report not found for incident {incident_id}"
            )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get compliance report: {e}", exc_info=True)

@router.get("/github/raw-issues")
async def get_raw_github_issues():
    """
    Get raw GitHub issues without analysis
    Used for "All Incidents" tab to show unprocessed issues
    """
    try:
        from app.services.github_service import get_github_service
        
        github_service = get_github_service()
        issues = github_service.list_open_issues()
        
        # Convert to simple format
        raw_issues = []
        for issue in issues:
            raw_issues.append({
                'issue_number': issue.get('number'),
                'title': issue.get('title'),
                'body': issue.get('body', ''),
                'labels': issue.get('labels', []),
                'state': issue.get('state', 'open'),
                'created_at': issue.get('created_at'),
                'updated_at': issue.get('updated_at'),
                'html_url': issue.get('html_url')
            })
        
        return {
            'success': True,
            'total': len(raw_issues),
            'issues': raw_issues
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch raw GitHub issues: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

        raise HTTPException(status_code=500, detail=str(e))



@router.post("/github/sync-existing-issues")
async def sync_existing_github_issues(background_tasks: BackgroundTasks):
    """
    Sync existing GitHub issues and trigger analysis for P1/P2 incidents
    This allows analyzing issues that existed before webhook was set up
    """
    try:
        from app.services.github_service import get_github_service
        
        github_service = get_github_service(
            access_token=settings.GITHUB_ACCESS_TOKEN,
            repo_name=settings.GITHUB_REPO_NAME
        )
        
        # Get all open issues
        issues = github_service.list_open_issues()
        
        incident_service = get_incident_service()
        
        synced_count = 0
        triggered_count = 0
        
        for issue in issues:
            # Check if it's an incident (has priority or incident label)
            priority = incident_service.detect_priority(issue.get('title', ''))
            labels = issue.get('labels', [])  # Already a list of strings from GitHub service
            
            is_incident = (
                'incident' in labels or
                priority is not None
            )
            
            if not is_incident:
                continue
            
            # Create incident
            incident = await incident_service.create_incident_from_github(
                issue_number=issue['number'],
                title=issue['title'],
                body=issue.get('body'),
                labels=labels
            )
            
            synced_count += 1
            
            # Check if should trigger analysis
            should_trigger = incident_service.should_trigger_analysis(incident.priority)
            
            if should_trigger:
                triggered_count += 1
                background_tasks.add_task(
                    trigger_compliance_analysis,
                    incident_id=incident.incident_id,
                    contract_id=settings.DEFAULT_CONTRACT_ID,
                    monthly_fee=100000.0
                )
        
        return {
            "success": True,
            "message": f"Synced {synced_count} existing incidents, triggered analysis for {triggered_count}",
            "synced_incidents": synced_count,
            "triggered_analysis": triggered_count
        }
        
    except Exception as e:
        logger.error(f"Failed to sync existing issues: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Made with Bob - Event-Driven API Endpoints