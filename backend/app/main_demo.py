"""
SOW Sentinel - Demo Mode
AI-powered Statement of Work compliance and risk management
This version runs without IBM Cloud credentials for testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Import API routers
from app.api.sow import router as sow_router
from app.api.integrations import router as integrations_router

app = FastAPI(
    title="SOW Sentinel - Demo Mode",
    description="AI-powered SOW compliance, risk management, and margin protection (Demo)",
    version="1.0.0"
)

# Include routers
app.include_router(sow_router)
app.include_router(integrations_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SOW Sentinel API - Demo Mode",
        "tagline": "Preventing revenue leakage and contract breaches",
        "version": "1.0.0",
        "status": "running",
        "mode": "demo",
        "features": [
            "SOW parsing with AI",
            "Real-time penalty countdown",
            "Scope creep detection",
            "Margin leakage alerts",
            "Risk assessment"
        ],
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
