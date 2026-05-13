"""
Admin API - Demo Data Generation
Creates realistic GitHub issues for hackathon demonstrations
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import requests
import random
import json
import logging

from app.core.cloudant_db import cloudant_db
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class DemoDataRequest(BaseModel):
    """Demo data generation request"""
    sow_id: str
    num_critical_issues: int = 3
    num_high_issues: int = 5
    num_medium_issues: int = 7
    include_overdue: bool = True
    include_comments: bool = True
    include_commits: bool = False


class ClearDataRequest(BaseModel):
    """Clear demo data request"""
    sow_id: str


async def _get_global_settings_document() -> Dict[str, Any]:
    """Fetch globally saved credentials from Cloudant."""
    return await cloudant_db.get_document("global_api_settings") or {}


async def _resolve_github_token() -> str:
    """Resolve GitHub token from DB first, then environment fallback."""
    global_settings = await _get_global_settings_document()
    return (
        global_settings.get("github_token")
        or settings.GITHUB_TOKEN
        or ""
    )


async def _get_integration_config(sow_id: str) -> Dict[str, Any]:
    """Get integration configuration for SOW"""
    try:
        config = await cloudant_db.get_document(f"integration_config_{sow_id}")
        return config if config and isinstance(config, dict) else {}
    except:
        return {}


def _generate_issue_templates(sow_id: str, priority: str) -> List[Dict[str, Any]]:
    """Generate realistic issue templates based on priority"""
    
    critical_templates = [
        {
            "title": "Database Migration - Phase 1",
            "body": "**Critical SLA Obligation**\n\nComplete database migration to new infrastructure.\n\n**Deliverables:**\n- Schema migration scripts\n- Data validation reports\n- Rollback procedures\n\n**Penalty:** $5,000 per day after deadline\n**Status:** In Progress",
            "penalty": 5000
        },
        {
            "title": "Security Audit Completion",
            "body": "**Critical SLA Obligation**\n\nComplete comprehensive security audit and remediation.\n\n**Deliverables:**\n- Penetration test results\n- Vulnerability assessment\n- Remediation plan\n\n**Penalty:** $3,000 per day after deadline\n**Status:** At Risk",
            "penalty": 3000
        },
        {
            "title": "Production Deployment",
            "body": "**Critical SLA Obligation**\n\nDeploy application to production environment.\n\n**Deliverables:**\n- Deployment runbook\n- Smoke test results\n- Monitoring setup\n\n**Penalty:** $10,000 per day after deadline\n**Status:** Blocked",
            "penalty": 10000
        },
    ]
    
    high_templates = [
        {
            "title": "UAT Sign-off Document",
            "body": "**High Priority Deliverable**\n\nObtain UAT sign-off from client stakeholders.\n\n**Deliverables:**\n- UAT test cases\n- Test execution results\n- Sign-off documentation\n\n**Penalty:** $1,000 per day after deadline",
            "penalty": 1000
        },
        {
            "title": "API Integration Testing",
            "body": "**High Priority Deliverable**\n\nComplete integration testing with third-party APIs.\n\n**Deliverables:**\n- Integration test suite\n- Performance benchmarks\n- Error handling documentation\n\n**Penalty:** $2,000 per day after deadline",
            "penalty": 2000
        },
        {
            "title": "User Training Materials",
            "body": "**High Priority Deliverable**\n\nCreate comprehensive user training documentation.\n\n**Deliverables:**\n- Training manual\n- Video tutorials\n- Quick reference guides\n\n**Penalty:** $500 per day after deadline",
            "penalty": 500
        },
        {
            "title": "Performance Optimization",
            "body": "**High Priority Deliverable**\n\nOptimize application performance to meet SLA requirements.\n\n**Deliverables:**\n- Performance test results\n- Optimization report\n- Load testing documentation\n\n**Penalty:** $1,500 per day after deadline",
            "penalty": 1500
        },
        {
            "title": "Disaster Recovery Plan",
            "body": "**High Priority Deliverable**\n\nDocument and test disaster recovery procedures.\n\n**Deliverables:**\n- DR runbook\n- Backup procedures\n- Recovery time testing\n\n**Penalty:** $2,500 per day after deadline",
            "penalty": 2500
        },
    ]
    
    medium_templates = [
        {
            "title": "Code Documentation",
            "body": "**Medium Priority Task**\n\nComplete code documentation for all modules.\n\n**Deliverables:**\n- API documentation\n- Code comments\n- Architecture diagrams",
            "penalty": 0
        },
        {
            "title": "Unit Test Coverage",
            "body": "**Medium Priority Task**\n\nAchieve 80% unit test coverage.\n\n**Deliverables:**\n- Test suite\n- Coverage reports\n- CI/CD integration",
            "penalty": 0
        },
        {
            "title": "Accessibility Compliance",
            "body": "**Medium Priority Task**\n\nEnsure WCAG 2.1 AA compliance.\n\n**Deliverables:**\n- Accessibility audit\n- Remediation plan\n- Testing results",
            "penalty": 0
        },
        {
            "title": "Monitoring Dashboard",
            "body": "**Medium Priority Task**\n\nSet up application monitoring and alerting.\n\n**Deliverables:**\n- Dashboard configuration\n- Alert rules\n- Runbook documentation",
            "penalty": 0
        },
        {
            "title": "Data Backup Automation",
            "body": "**Medium Priority Task**\n\nAutomate daily data backup procedures.\n\n**Deliverables:**\n- Backup scripts\n- Verification procedures\n- Restore testing",
            "penalty": 0
        },
        {
            "title": "API Rate Limiting",
            "body": "**Medium Priority Task**\n\nImplement rate limiting for public APIs.\n\n**Deliverables:**\n- Rate limit configuration\n- Documentation\n- Testing results",
            "penalty": 0
        },
        {
            "title": "Error Logging Enhancement",
            "body": "**Medium Priority Task**\n\nEnhance error logging and tracking.\n\n**Deliverables:**\n- Logging framework\n- Error categorization\n- Alert integration",
            "penalty": 0
        },
    ]
    
    if priority == "critical":
        return critical_templates
    elif priority == "high":
        return high_templates
    else:
        return medium_templates


def _generate_comments() -> List[str]:
    """Generate realistic issue comments"""
    return [
        "Started work on this task. Initial analysis complete.",
        "Encountered some blockers with the third-party API. Working on resolution.",
        "Made good progress today. About 60% complete.",
        "Need clarification from the client on acceptance criteria.",
        "Updated the implementation based on code review feedback.",
        "Testing in progress. Found a few edge cases to handle.",
        "Ready for review. All acceptance criteria met.",
        "Deployed to staging environment for UAT.",
    ]


@router.post("/generate-demo-data")
async def generate_demo_data(request: DemoDataRequest):
    """
    Generate realistic demo data in GitHub for hackathon presentations
    """
    try:
        # Get GitHub token
        github_token = await _resolve_github_token()
        if not github_token:
            raise HTTPException(status_code=400, detail="GitHub token not configured. Please configure in Settings.")
        
        # Get integration config
        config = await _get_integration_config(request.sow_id)
        if not config or not config.get("github"):
            raise HTTPException(status_code=400, detail="GitHub not configured for this SOW. Please configure in GitHub Configuration page.")
        
        github_config = config["github"]
        repo_owner = github_config.get("repository_owner")
        repo_name = github_config.get("repository_name")
        
        if not repo_owner or not repo_name:
            raise HTTPException(status_code=400, detail="Repository not configured for this SOW.")
        
        # Ensure token is ASCII-safe (GitHub tokens should be ASCII, but handle edge cases)
        try:
            github_token_safe = github_token.encode('ascii').decode('ascii')
        except (UnicodeEncodeError, UnicodeDecodeError):
            # If token has non-ASCII characters, it's invalid
            raise HTTPException(status_code=400, detail="GitHub token contains invalid characters. Please check your token.")
        
        headers = {
            "Authorization": f"token {github_token_safe}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        
        # Get milestone
        milestone_number = None
        try:
            milestones_response = requests.get(f"{base_url}/milestones", headers=headers)
            if milestones_response.status_code == 200:
                milestones = milestones_response.json()
                for milestone in milestones:
                    if request.sow_id in milestone.get("title", ""):
                        milestone_number = milestone.get("number")
                        break
        except:
            pass
        
        # Get labels
        labels_map = {
            "critical": f"{request.sow_id.lower()}-sla-critical",
            "high": f"{request.sow_id.lower()}-sla-high",
            "medium": f"{request.sow_id.lower()}-sla-medium",
            "milestone": f"{request.sow_id.lower()}-milestone",
            "compliance": f"{request.sow_id.lower()}-compliance",
        }
        
        # Don't use assignees - they cause validation errors if user doesn't have repo access
        # Issues can be assigned manually after creation
        assignees = []
        
        issues_created = 0
        comments_created = 0
        created_issues = []
        
        # Generate critical issues
        critical_templates = _generate_issue_templates(request.sow_id, "critical")
        for i in range(request.num_critical_issues):
            # Cycle through templates if more issues requested than templates
            template = critical_templates[i % len(critical_templates)]
            
            # Calculate due date
            if request.include_overdue and i == 0:
                # First critical issue is overdue
                due_date = (datetime.utcnow() - timedelta(days=random.randint(1, 5))).isoformat() + "Z"
            else:
                # Others are due soon
                due_date = (datetime.utcnow() + timedelta(days=random.randint(3, 14))).isoformat() + "Z"
            
            # Add variation to title if using same template multiple times
            title_suffix = f" - Part {(i // len(critical_templates)) + 1}" if i >= len(critical_templates) else ""
            
            issue_data = {
                "title": f"[{request.sow_id}] {template['title']}{title_suffix}",
                "body": template["body"],
                "labels": [labels_map["critical"], labels_map["milestone"], labels_map["compliance"]],
            }
            
            if milestone_number:
                issue_data["milestone"] = milestone_number
            
            # Create issue with explicit UTF-8 encoding
            try:
                json_data = json.dumps(issue_data, ensure_ascii=False)
                logger.info(f"Creating issue with data: {json_data[:100]}...")
                response = requests.post(
                    f"{base_url}/issues",
                    headers={**headers, "Content-Type": "application/json; charset=utf-8"},
                    data=json_data.encode('utf-8')
                )
                logger.info(f"Response status: {response.status_code}")
            except Exception as e:
                logger.error(f"Error creating issue: {type(e).__name__}: {repr(e)}")
                raise
            if response.status_code in [200, 201]:
                issue = response.json()
                issues_created += 1
                created_issues.append(issue)
                
                # Add comments if requested
                if request.include_comments:
                    comments = random.sample(_generate_comments(), random.randint(2, 4))
                    for comment in comments:
                        comment_data = {"body": comment}
                        comment_response = requests.post(
                            issue["comments_url"],
                            headers={**headers, "Content-Type": "application/json; charset=utf-8"},
                            data=json.dumps(comment_data).encode('utf-8')
                        )
                        if comment_response.status_code in [200, 201]:
                            comments_created += 1
            else:
                # Log error but continue
                print(f"Failed to create critical issue {i+1}: {response.status_code} - {response.text}")
        
        # Generate high priority issues
        high_templates = _generate_issue_templates(request.sow_id, "high")
        for i in range(request.num_high_issues):
            # Cycle through templates if more issues requested than templates
            template = high_templates[i % len(high_templates)]
            
            # Calculate due date
            if request.include_overdue and i < 2:
                # Some high issues are overdue
                due_date = (datetime.utcnow() - timedelta(days=random.randint(1, 3))).isoformat() + "Z"
            else:
                # Others are upcoming
                due_date = (datetime.utcnow() + timedelta(days=random.randint(7, 21))).isoformat() + "Z"
            
            # Add variation to title if using same template multiple times
            title_suffix = f" - Part {(i // len(high_templates)) + 1}" if i >= len(high_templates) else ""
            
            issue_data = {
                "title": f"[{request.sow_id}] {template['title']}{title_suffix}",
                "body": template["body"],
                "labels": [labels_map["high"], labels_map["milestone"]],
            }
            
            if milestone_number:
                issue_data["milestone"] = milestone_number
            
            response = requests.post(
                f"{base_url}/issues",
                headers={**headers, "Content-Type": "application/json; charset=utf-8"},
                data=json.dumps(issue_data).encode('utf-8')
            )
            if response.status_code in [200, 201]:
                issue = response.json()
                issues_created += 1
                created_issues.append(issue)
                
                if request.include_comments and random.random() > 0.5:
                    comments = random.sample(_generate_comments(), random.randint(1, 3))
                    for comment in comments:
                        comment_data = {"body": comment}
                        comment_response = requests.post(
                            issue["comments_url"],
                            headers={**headers, "Content-Type": "application/json; charset=utf-8"},
                            data=json.dumps(comment_data).encode('utf-8')
                        )
                        if comment_response.status_code in [200, 201]:
                            comments_created += 1
            else:
                # Log error but continue
                print(f"Failed to create high priority issue {i+1}: {response.status_code} - {response.text}")
        
        # Generate medium priority issues
        medium_templates = _generate_issue_templates(request.sow_id, "medium")
        for i in range(request.num_medium_issues):
            # Cycle through templates if more issues requested than templates
            template = medium_templates[i % len(medium_templates)]
            
            # Medium issues have longer deadlines
            due_date = (datetime.utcnow() + timedelta(days=random.randint(14, 45))).isoformat() + "Z"
            
            # Add variation to title if using same template multiple times
            title_suffix = f" - Part {(i // len(medium_templates)) + 1}" if i >= len(medium_templates) else ""
            
            issue_data = {
                "title": f"[{request.sow_id}] {template['title']}{title_suffix}",
                "body": template["body"],
                "labels": [labels_map["medium"]],
            }
            
            response = requests.post(
                f"{base_url}/issues",
                headers={**headers, "Content-Type": "application/json; charset=utf-8"},
                data=json.dumps(issue_data).encode('utf-8')
            )
            if response.status_code in [200, 201]:
                issue = response.json()
                issues_created += 1
                created_issues.append(issue)
                
                if request.include_comments and random.random() > 0.7:
                    comments = random.sample(_generate_comments(), random.randint(1, 2))
                    for comment in comments:
                        comment_data = {"body": comment}
                        comment_response = requests.post(
                            issue["comments_url"],
                            headers={**headers, "Content-Type": "application/json; charset=utf-8"},
                            data=json.dumps(comment_data).encode('utf-8')
                        )
                        if comment_response.status_code in [200, 201]:
                            comments_created += 1
            else:
                # Log error but continue
                print(f"Failed to create medium priority issue {i+1}: {response.status_code} - {response.text}")
        
        return {
            "success": True,
            "issues_created": issues_created,
            "comments_created": comments_created,
            "commits_created": 0,
            "repository_url": f"https://github.com/{repo_owner}/{repo_name}/issues",
            "created_issues": [
                {
                    "number": issue["number"],
                    "title": issue["title"],
                    "url": issue["html_url"]
                }
                for issue in created_issues
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Handle encoding errors in exception message
        try:
            error_msg = str(e)
        except:
            error_msg = repr(e)
        raise HTTPException(status_code=500, detail=f"Failed to generate demo data: {error_msg}")


@router.post("/clear-demo-data")
async def clear_demo_data(request: ClearDataRequest):
    """
    Clear demo data from GitHub (closes all SOW-related issues)
    """
    try:
        # Get GitHub token
        github_token = await _resolve_github_token()
        if not github_token:
            raise HTTPException(status_code=400, detail="GitHub token not configured")
        
        # Get integration config
        config = await _get_integration_config(request.sow_id)
        if not config or not config.get("github"):
            raise HTTPException(status_code=400, detail="GitHub not configured for this SOW")
        
        github_config = config["github"]
        repo_owner = github_config.get("repository_owner")
        repo_name = github_config.get("repository_name")
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        
        # Get all open issues with SOW prefix
        issues_response = requests.get(
            f"{base_url}/issues",
            headers=headers,
            params={"state": "open", "per_page": 100}
        )
        
        if issues_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch issues from GitHub")
        
        issues = issues_response.json()
        issues_deleted = 0
        
        # Close issues that match the SOW ID
        for issue in issues:
            if f"[{request.sow_id}]" in issue.get("title", ""):
                # Close the issue
                close_response = requests.patch(
                    f"{base_url}/issues/{issue['number']}",
                    headers=headers,
                    json={"state": "closed"}
                )
                if close_response.status_code == 200:
                    issues_deleted += 1
        
        return {
            "success": True,
            "issues_deleted": issues_deleted
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear demo data: {str(e)}")

@router.post("/populate-sla-data")
async def populate_sla_data():
    """
    Populate SLA data for all SOW obligations
    Adds realistic deadlines and penalty amounts
    """
    try:
        sows = await cloudant_db.query_documents({"type": "sow"}, limit=100)
        
        if not sows:
            return {"success": False, "message": "No SOWs found"}
        
        updated_count = 0
        total_penalties = 0
        
        for sow in sows:
            sow_id = sow.get("_id")
            obligations = sow.get("obligations", [])
            
            if not obligations:
                continue
            
            updated = False
            for i, obligation in enumerate(obligations):
                # Skip if already has deadline and penalty
                if obligation.get("deadline") and obligation.get("penalty_amount"):
                    continue
                
                # Add realistic deadline
                if i == 0:
                    days_offset = random.randint(-5, 14)
                elif i == 1:
                    days_offset = random.randint(7, 30)
                else:
                    days_offset = random.randint(14, 60)
                
                deadline = (datetime.utcnow() + timedelta(days=days_offset)).isoformat() + "Z"
                
                # Add realistic penalty
                penalties = [1000, 2000, 3000, 5000, 10000]
                penalty_amount = random.choice(penalties)
                
                # Determine priority
                if penalty_amount >= 5000:
                    priority = "critical"
                    risk_level = "critical"
                elif penalty_amount >= 2000:
                    priority = "high"
                    risk_level = "high"
                else:
                    priority = "medium"
                    risk_level = "medium"
                
                # Update obligation
                obligation["deadline"] = deadline
                obligation["penalty_amount"] = float(penalty_amount)
                obligation["penalty_per_day"] = float(penalty_amount)
                obligation["priority"] = priority
                obligation["risk_level"] = risk_level
                obligation["status"] = "in_progress" if days_offset > 0 else "at_risk"
                
                updated = True
                total_penalties += penalty_amount
            
            if updated:
                # Calculate financial metrics
                sow_penalties = sum(o.get("penalty_amount", 0) for o in obligations)
                high_risk_count = sum(1 for o in obligations if o.get("risk_level") in ["critical", "high"])
                
                # Calculate realistic contract hours based on obligations
                # Assume 40-80 hours per obligation
                num_obligations = len(obligations)
                contract_hours = num_obligations * random.randint(40, 80)
                
                # Calculate realistic revenue based on penalties and hours
                # Typical project: $150-200 per hour, penalties are 5-10% of total value
                hourly_rate = random.randint(150, 200)
                base_revenue = contract_hours * hourly_rate
                # Add buffer for penalties (penalties should be ~5-10% of revenue)
                total_value = base_revenue + (sow_penalties * random.randint(10, 20))
                
                sow["financial_summary"] = {
                    "total_penalties_at_risk": sow_penalties,
                    "high_risk_obligations": high_risk_count,
                    "penalties_avoided": 0,
                    "margin_protected": 0,
                    "scope_creep_value": 0,
                    "contract_hours": contract_hours,
                    "total_value": total_value,
                    "hourly_rate": hourly_rate
                }
                
                # Save
                await cloudant_db.update_document(sow_id, sow)
                updated_count += 1
        
        return {
            "success": True,
            "sows_updated": updated_count,
            "total_penalty_exposure": total_penalties,
            "message": f"Updated {updated_count} SOWs with SLA data"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to populate SLA data: {str(e)}")



# Made with Bob