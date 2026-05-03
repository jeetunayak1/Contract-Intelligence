"""
Initialize Cloudant database with schemas, indexes, and sample data
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.core.cloudant_db import cloudant_db
from app.models.sow_models import (
    create_sow_document,
    create_obligation,
    create_sla_term,
    create_vague_clause,
    create_compliance_event_document,
    create_scope_creep_document,
    create_alert_document,
    ObligationType,
    RiskLevel,
    ObligationStatus,
    EventType,
    AlertSeverity,
    ScopeCreepStatus
)


async def create_indexes():
    """Create necessary indexes for efficient querying"""
    print("\n📊 Creating Database Indexes...")
    
    indexes = [
        {
            "fields": ["type", "created_at"],
            "name": "type-created-index",
            "description": "Index for querying by document type and creation date"
        },
        {
            "fields": ["sow_number"],
            "name": "sow-number-index",
            "description": "Index for SOW number lookups"
        },
        {
            "fields": ["client_name"],
            "name": "client-name-index",
            "description": "Index for client name searches"
        },
        {
            "fields": ["status"],
            "name": "status-index",
            "description": "Index for status filtering"
        },
        {
            "fields": ["type", "sow_id"],
            "name": "type-sow-index",
            "description": "Index for querying documents by type and SOW ID"
        },
        {
            "fields": ["type", "severity"],
            "name": "type-severity-index",
            "description": "Index for querying alerts and events by severity"
        },
        {
            "fields": ["obligation_id"],
            "name": "obligation-id-index",
            "description": "Index for obligation lookups"
        }
    ]
    
    for idx in indexes:
        try:
            await cloudant_db.create_index(
                index_fields=idx["fields"],
                index_name=idx["name"]
            )
            print(f"   ✅ Created: {idx['name']} - {idx['description']}")
        except Exception as e:
            print(f"   ⚠️  {idx['name']}: {str(e)}")


async def create_sample_sow():
    """Create sample SOW document with obligations"""
    print("\n📄 Creating Sample SOW Document...")
    
    # Create main SOW document
    sow_doc = create_sow_document(
        sow_number="2024-ACME-001",
        client_name="Acme Corporation",
        project_name="Enterprise Platform Migration",
        start_date="2024-01-01",
        end_date="2024-12-31",
        total_value=500000,
        currency="USD",
        description="Migration of legacy systems to cloud-based platform with enhanced security and scalability",
        file_name="SOW-ACME-2024-001.pdf",
        file_size=2458624
    )
    
    # Add obligations
    obligations = [
        create_obligation(
            sow_id=sow_doc["_id"],
            obligation_type=ObligationType.MILESTONE.value,
            description="Phase 1: Database Migration Complete",
            deadline="2024-03-31",
            penalty_amount=5000,
            penalty_frequency="per_day",
            risk_level=RiskLevel.HIGH.value,
            status=ObligationStatus.COMPLETED.value,
            progress_percentage=100,
            mapped_to={
                "github_project": "acme-migration",
                "github_issue": 123
            }
        ),
        create_obligation(
            sow_id=sow_doc["_id"],
            obligation_type=ObligationType.DELIVERABLE.value,
            description="UAT Sign-off Documentation",
            deadline="2024-05-15",
            penalty_amount=1000,
            penalty_frequency="per_day",
            risk_level=RiskLevel.CRITICAL.value,
            status=ObligationStatus.IN_PROGRESS.value,
            progress_percentage=75,
            mapped_to={
                "github_issue": 456,
                "outlook_event_id": "AAMkAGI2..."
            },
            checklist=[
                "Complete UAT test cases",
                "Obtain client sign-off",
                "Document test results",
                "Archive test artifacts"
            ]
        ),
        create_obligation(
            sow_id=sow_doc["_id"],
            obligation_type=ObligationType.DELIVERABLE.value,
            description="Security Audit Report",
            deadline="2024-06-30",
            penalty_amount=2500,
            penalty_frequency="per_day",
            risk_level=RiskLevel.HIGH.value,
            status=ObligationStatus.NOT_STARTED.value,
            progress_percentage=0
        )
    ]
    
    # Add SLA terms
    sla_terms = [
        create_sla_term(
            sow_id=sow_doc["_id"],
            metric_name="Incident Response Time",
            target_value=4,
            unit="hours",
            measurement_period="monthly",
            penalty_amount=1000,
            current_value=3.2,
            compliance_percentage=95
        ),
        create_sla_term(
            sow_id=sow_doc["_id"],
            metric_name="System Uptime",
            target_value=99.9,
            unit="percentage",
            measurement_period="monthly",
            penalty_amount=5000,
            current_value=99.95,
            compliance_percentage=100
        )
    ]
    
    # Add vague clauses
    vague_clauses = [
        create_vague_clause(
            sow_id=sow_doc["_id"],
            clause_text="Reasonable efforts for performance optimization",
            risk_description="Undefined success criteria - no specific performance metrics",
            recommendation="Request specific metrics: e.g., 'Page load time < 2 seconds'",
            severity=RiskLevel.MEDIUM.value
        )
    ]
    
    sow_doc["obligations"] = obligations
    sow_doc["sla_terms"] = sla_terms
    sow_doc["vague_clauses"] = vague_clauses
    
    # Update financial summary
    sow_doc["financial_summary"] = {
        "total_value": 500000,
        "total_penalties": 8500,
        "penalties_avoided": 12000,
        "scope_creep_value": 15000,
        "margin_protected": 3.25
    }
    
    # Check if document already exists
    existing_sow = await cloudant_db.get_document(sow_doc["_id"])
    if existing_sow:
        print(f"   ℹ️  SOW already exists: {existing_sow['_id']}")
        print(f"      - Client: {existing_sow['client_name']}")
        print(f"      - Project: {existing_sow['project_name']}")
        return existing_sow
    
    created_sow = await cloudant_db.create_document(sow_doc)
    print(f"   ✅ Created SOW: {created_sow['_id']}")
    print(f"      - Client: {created_sow['client_name']}")
    print(f"      - Project: {created_sow['project_name']}")
    print(f"      - Obligations: {len(obligations)}")
    print(f"      - SLA Terms: {len(sla_terms)}")
    
    return created_sow


async def create_sample_events(sow_id: str, obligation_id: str):
    """Create sample compliance events"""
    print("\n⚡ Creating Sample Compliance Events...")
    
    events = [
        create_compliance_event_document(
            sow_id=sow_id,
            obligation_id=obligation_id,
            event_type=EventType.DEADLINE_WARNING.value,
            severity=AlertSeverity.HIGH.value,
            days_remaining=7,
            current_progress=75,
            required_progress=100,
            velocity_trend="declining",
            predicted_completion="2024-05-18",
            penalty_exposure=3000,
            actions_taken=[
                "Created GitHub Issue #456 (URGENT)",
                "Scheduled Outlook meeting for tomorrow",
                "Sent Slack alert to PM"
            ]
        ),
        create_compliance_event_document(
            sow_id=sow_id,
            obligation_id=obligation_id,
            event_type=EventType.VELOCITY_DECLINE.value,
            severity=AlertSeverity.MEDIUM.value,
            days_remaining=10,
            current_progress=70,
            required_progress=100,
            velocity_trend="declining",
            penalty_exposure=1000
        )
    ]
    
    for event in events:
        created_event = await cloudant_db.create_document(event)
        print(f"   ✅ Created Event: {created_event['event_type']} (Severity: {created_event['severity']})")
    
    return events


async def create_sample_scope_creep(sow_id: str):
    """Create sample scope creep detection"""
    print("\n🔍 Creating Sample Scope Creep Detection...")
    
    scope_creep = create_scope_creep_document(
        sow_id=sow_id,
        detected_work={
            "description": "Advanced Analytics Dashboard",
            "hours_spent": 40,
            "cost": 10000,
            "github_commits": ["abc123", "def456", "ghi789"],
            "github_issues": [789]
        },
        sow_match=None,
        recommendation="Create Change Request CR-2024-05",
        potential_revenue=15000,
        status=ScopeCreepStatus.DETECTED.value
    )
    
    created_scope = await cloudant_db.create_document(scope_creep)
    print(f"   ✅ Created Scope Creep: {created_scope['_id']}")
    print(f"      - Work: {created_scope['detected_work']['description']}")
    print(f"      - Cost: ${created_scope['detected_work']['cost']:,}")
    print(f"      - Potential Revenue: ${created_scope['potential_revenue']:,}")
    
    return created_scope


async def create_sample_alerts(sow_id: str, obligation_id: str):
    """Create sample alerts"""
    print("\n🚨 Creating Sample Alerts...")
    
    alerts = [
        create_alert_document(
            sow_id=sow_id,
            obligation_id=obligation_id,
            alert_type="deadline_warning",
            severity=AlertSeverity.CRITICAL.value,
            title="URGENT: UAT Sign-off Due in 48 Hours",
            message="If you don't deliver the UAT sign-off by Friday, you lose $1,000 per day",
            penalty_amount=1000,
            days_until_penalty=2,
            recommended_actions=[
                "Complete remaining UAT test cases",
                "Schedule emergency review meeting",
                "Prepare sign-off documentation"
            ],
            notified_users=["pm@company.com", "tech-lead@company.com"],
            notification_channels=["slack", "email"]
        ),
        create_alert_document(
            sow_id=sow_id,
            obligation_id=obligation_id,
            alert_type="scope_creep",
            severity=AlertSeverity.MEDIUM.value,
            title="Scope Creep Detected: Advanced Analytics Dashboard",
            message="Team spent 40 hours on out-of-scope work. Potential revenue: $15,000",
            recommended_actions=[
                "Create Change Request CR-2024-05",
                "Document additional work",
                "Negotiate billing with client"
            ],
            notified_users=["pm@company.com"],
            notification_channels=["email"]
        )
    ]
    
    for alert in alerts:
        created_alert = await cloudant_db.create_document(alert)
        print(f"   ✅ Created Alert: {created_alert['title']}")
        print(f"      - Severity: {created_alert['severity']}")
    
    return alerts


async def initialize_database():
    """Main initialization function"""
    print("=" * 70)
    print("SOW SENTINEL - DATABASE INITIALIZATION")
    print("=" * 70)
    
    try:
        # Step 1: Create database
        print("\n🗄️  Creating Database...")
        await cloudant_db.create_database()
        print("   ✅ Database ready")
        
        # Step 2: Create indexes
        await create_indexes()
        
        # Step 3: Create sample SOW
        sow = await create_sample_sow()
        
        # Step 4: Create sample events
        if sow["obligations"]:
            obligation_id = sow["obligations"][1]["id"]  # UAT obligation
            await create_sample_events(sow["_id"], obligation_id)
            await create_sample_alerts(sow["_id"], obligation_id)
        
        # Step 5: Create sample scope creep
        await create_sample_scope_creep(sow["_id"])
        
        print("\n" + "=" * 70)
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("=" * 70)
        print("\n📊 Summary:")
        print(f"   - Database: {cloudant_db.db_name}")
        print(f"   - Indexes: 7 created")
        print(f"   - Sample SOW: {sow['sow_number']}")
        print(f"   - Obligations: {len(sow['obligations'])}")
        print(f"   - Events: 2 created")
        print(f"   - Alerts: 2 created")
        print(f"   - Scope Creep: 1 detected")
        print("\n🚀 Ready to use! Access the API at http://localhost:8000/docs")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(initialize_database())
    sys.exit(0 if success else 1)

# Made with Bob
