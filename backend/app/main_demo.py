"""
SOW Sentinel - Demo Mode
AI-powered Statement of Work compliance and risk management
This version runs without IBM Cloud credentials for testing
"""
import os
import warnings
from dotenv import load_dotenv

# Suppress Pydantic V1/V2 mixing warnings from crewai
warnings.filterwarnings("ignore", message=".*Mixing V1 models and V2 models.*")

# Load environment variables from .env file so that Google Auth picks up GOOGLE_APPLICATION_CREDENTIALS
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Import API routers
from app.api.sow import router as sow_router
from app.api.integrations import router as integrations_router
from app.api.settings import router as settings_router
from app.api.contract_intelligence import router as contract_intelligence_router
from app.api.compliance import router as compliance_router
from app.api.events import router as events_router

app = FastAPI(
    title="SOW Sentinel - Demo Mode",
    description="AI-powered SOW compliance, risk management, and margin protection (Demo)",
    version="1.0.0"
)

# Include routers
app.include_router(sow_router, prefix="/api/v1/sow")
app.include_router(integrations_router)
app.include_router(settings_router)
app.include_router(contract_intelligence_router, prefix="/api/v1/contracts", tags=["Contract Intelligence"])
app.include_router(compliance_router, prefix="/api/v1/compliance", tags=["Compliance & Risk"])
app.include_router(events_router, tags=["Events & Webhooks"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    Automatically syncs existing GitHub issues on application start
    """
    import logging
    import asyncio
    from app.core.config import Settings
    
    logger = logging.getLogger(__name__)
    settings = Settings()
    
    # Only sync if GitHub is configured
    if settings.GITHUB_ACCESS_TOKEN and settings.GITHUB_REPO_NAME:
        logger.info("🔄 Syncing existing GitHub issues on startup...")
        
        try:
            from app.services.github_service import get_github_service
            from app.services.incident_service import get_incident_service
            
            github_service = get_github_service(
                access_token=settings.GITHUB_ACCESS_TOKEN,
                repo_name=settings.GITHUB_REPO_NAME
            )
            
            # Check if GitHub service is properly initialized
            if not github_service.repo:
                logger.warning("⚠️  GitHub repo not accessible. Please check:")
                logger.warning(f"   - GITHUB_REPO_NAME format: 'owner/repo' (current: {settings.GITHUB_REPO_NAME})")
                logger.warning(f"   - GITHUB_ACCESS_TOKEN has repo access permissions")
                logger.warning(f"   - Repository exists and is accessible")
                logger.info("ℹ️  Skipping existing issues sync. System will still work with webhooks.")
                return
            
            # Get all open issues
            issues = github_service.list_open_issues()
            
            incident_service = get_incident_service()
            
            synced_count = 0
            triggered_count = 0
            
            for issue in issues:
                # Check if it's an incident
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
                    # Trigger analysis in background
                    asyncio.create_task(trigger_analysis_background(
                        incident_id=incident.incident_id,
                        contract_id=settings.DEFAULT_CONTRACT_ID,
                        monthly_fee=100000.0
                    ))
            
            logger.info(f"✅ Synced {synced_count} existing incidents, triggered analysis for {triggered_count}")
            
        except Exception as e:
            logger.error(f"❌ Failed to sync existing issues: {e}")
    else:
        logger.info("⚠️  GitHub not configured, skipping existing issues sync")


async def trigger_analysis_background(incident_id: str, contract_id: str, monthly_fee: float):
    """Background task to trigger compliance analysis"""
    try:
        from app.crew.compliance_crew import get_compliance_crew
        from app.core.config import Settings
        
        settings = Settings()
        crew = get_compliance_crew(gemini_api_key=settings.GOOGLE_API_KEY)
        
        await crew.analyze_incident(
            incident_id=incident_id,
            contract_id=contract_id,
            monthly_fee=monthly_fee
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Background analysis failed for {incident_id}: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Autonomous Contract Risk Intelligence Platform",
        "tagline": "Event-driven compliance monitoring with AI agents",
        "version": "2.0.0",
        "status": "running",
        "mode": "demo",
        "features": [
            "Contract Intelligence Agent (SLA extraction)",
            "Real-time GitHub webhook integration",
            "Autonomous compliance analysis with CrewAI",
            "Live incident feed with reasoning stream",
            "Financial exposure tracking",
            "Liability exclusion matching",
            "AI War Room dashboard",
            "Auto-sync existing GitHub issues on startup"
        ],
        "endpoints": {
            "github_webhook": "/api/v1/events/github/webhook",
            "live_incidents": "/api/v1/events/incidents/live",
            "reasoning_stream": "/api/v1/events/reasoning/{incident_id}",
            "crew_status": "/api/v1/events/crew/{crew_execution_id}",
            "manual_trigger": "/api/v1/events/incidents/{incident_id}/analyze",
            "sync_existing": "/api/v1/events/github/sync-existing-issues"
        },
        "default_contract": "contract_6b65228aeb64",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mode": "demo",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/contracts")
async def get_contracts():
    """Get all contracts (demo data)"""
    return {
        "contracts": [
            {
                "id": "CTR-2024-001",
                "customer_name": "Acme Corporation",
                "contract_type": "service",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "status": "active",
                "value": 500000
            },
            {
                "id": "CTR-2024-002",
                "customer_name": "TechStart Inc",
                "contract_type": "license",
                "start_date": "2024-02-15",
                "end_date": "2025-02-14",
                "status": "active",
                "value": 250000
            }
        ],
        "total": 2
    }

@app.get("/api/v1/compliance/metrics")
async def get_compliance_metrics():
    """Get compliance metrics (demo data)"""
    return {
        "overall_compliance": 0.92,
        "active_contracts": 15,
        "compliant_contracts": 14,
        "at_risk_contracts": 1,
        "metrics": [
            {"name": "Response Time SLA", "compliance": 0.95, "status": "good"},
            {"name": "Uptime SLA", "compliance": 0.98, "status": "good"},
            {"name": "Support SLA", "compliance": 0.88, "status": "warning"}
        ]
    }

@app.get("/api/v1/risks")
async def get_risks():
    """Get risk assessments (demo data)"""
    return {
        "risks": [
            {
                "id": "RISK-001",
                "contract_id": "CTR-2024-001",
                "type": "compliance",
                "severity": "medium",
                "description": "Approaching SLA threshold for response time",
                "probability": 0.65,
                "impact": 0.70
            },
            {
                "id": "RISK-002",
                "contract_id": "CTR-2024-003",
                "type": "financial",
                "severity": "high",
                "description": "Contract renewal at risk due to performance issues",
                "probability": 0.80,
                "impact": 0.85
            }
        ],
        "total": 2
    }

@app.get("/api/v1/alerts")
async def get_alerts():
    """Get active alerts (demo data)"""
    return {
        "alerts": [
            {
                "id": "ALERT-001",
                "type": "sla_breach",
                "severity": "high",
                "message": "SLA breach detected for CTR-2024-005",
                "timestamp": "2024-05-01T10:30:00Z",
                "status": "active"
            },
            {
                "id": "ALERT-002",
                "type": "contract_expiry",
                "severity": "medium",
                "message": "Contract CTR-2024-008 expiring in 30 days",
                "timestamp": "2024-05-01T09:15:00Z",
                "status": "active"
            }
        ],
        "total": 2
    }

@app.get("/api/v1/analytics/dashboard")
async def get_dashboard_analytics():
    """Get dashboard analytics (demo data)"""
    return {
        "summary": {
            "total_contracts": 15,
            "active_contracts": 12,
            "total_value": 5250000,
            "compliance_rate": 0.92,
            "at_risk_count": 3
        },
        "compliance_trend": [
            {"date": "2024-01", "rate": 0.88},
            {"date": "2024-02", "rate": 0.90},
            {"date": "2024-03", "rate": 0.91},
            {"date": "2024-04", "rate": 0.92}
        ],
        "risk_distribution": {
            "low": 8,
            "medium": 4,
            "high": 2,
            "critical": 1
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
