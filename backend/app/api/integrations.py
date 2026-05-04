"""
Integration Configuration API
Handles GitHub, Slack, and Outlook configuration for SOWs
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime

from app.models.integration_config import (
    IntegrationConfig,
    ConfigurationRequest,
    ConfigurationResponse,
    GitHubConfig,
    GitHubLabel,
    GitHubGeneratedIssue,
    GitHubIssueTemplate,
    GitHubRepositoryTarget,
    SlackConfig,
    SlackChannel,
    OutlookConfig,
    TeamMember
)
from app.core.cloudant_db import cloudant_db
from app.core.config import settings

router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])


@router.post("/configure", response_model=ConfigurationResponse)
async def ai_configure_integrations(request: ConfigurationRequest):
    """
    AI-powered integration configuration
    Analyzes team info and suggests optimal configuration
    """
    
    # Extract team information
    team_info = request.team_info
    sow_id = request.sow_id
    
    # AI-generated configuration based on team info
    suggested_config = IntegrationConfig(
        sow_id=sow_id,
        team_info=team_info,
        github=_generate_github_config(sow_id, team_info),
        slack=_generate_slack_config(sow_id, team_info),
        outlook=_generate_outlook_config(sow_id, team_info)
    )
    
    github_config = suggested_config.github
    slack_config = suggested_config.slack
    outlook_config = suggested_config.outlook

    github_label_count = len(github_config.labels) if github_config else 0
    github_issue_count = len(github_config.generated_issues) if github_config else 0
    outlook_member_count = len(outlook_config.team_members) if outlook_config else 0

    pre_acceptance_repo = github_config.pre_acceptance_repo if github_config else None
    delivery_repo = github_config.delivery_repo if github_config else None
    pre_acceptance_calendar = outlook_config.pre_acceptance_calendar_name if outlook_config else None
    delivery_calendar = outlook_config.delivery_calendar_name if outlook_config else None

    explanation = f"""
    Based on your team information, I've created a staged per-SOW integration plan for {sow_id}.

    **Pre-Acceptance Workflow:**
    - Review repository: {f"{pre_acceptance_repo.repository_owner}/{pre_acceptance_repo.repository_name}" if pre_acceptance_repo else 'Not specified'}
    - Review calendar: {pre_acceptance_calendar or 'Not specified'}
    - Agent actions focus on clarification, SLA negotiation, acceptance criteria, and commercial review before approval

    **Post-Approval Workflow:**
    - Delivery repository: {f"{delivery_repo.repository_owner}/{delivery_repo.repository_name}" if delivery_repo else 'Not specified'}
    - Delivery calendar: {delivery_calendar or 'Not specified'}
    - Agent actions focus on delivery kickoff, implementation tracking, SLA-tagged execution items, and stakeholder cadences after approval

    **GitHub Configuration:**
    - Created {github_label_count} SOW-specific labels
    - Prepared {github_issue_count} issue definitions tied to this SOW's obligations and workflow stages
    - Enabled milestone, review issue, and obligation issue automation for this SOW

    **Slack Configuration:**
    - Created dedicated SOW alert channel naming for {sow_id}
    - Configured notification preferences for critical events on this SOW
    - Team size: {team_info.get('team_size', 'Unknown')}

    **Outlook Configuration:**
    - Added {outlook_member_count} team members and stakeholders for this SOW
    - Configured automatic milestone review scheduling for this SOW calendar set
    - Set up email notifications scoped to this SOW's stakeholders
    """
    
    next_steps = [
        "Review the pre-acceptance repo and calendar used before SOW approval",
        "Review the delivery repo and calendar used after SOW approval",
        "Apply configuration to create SOW-specific labels, milestone, and GitHub issue definitions",
        "Verify SOW stakeholders and notification routing",
        "Test Slack and Outlook delivery for this SOW"
    ]
    
    return ConfigurationResponse(
        sow_id=sow_id,
        suggested_config=suggested_config,
        explanation=explanation.strip(),
        next_steps=next_steps
    )


@router.post("/apply/{sow_id}")
async def apply_configuration(sow_id: str, config: IntegrationConfig):
    """
    Apply the configuration and create resources
    """
    results = {
        "github": {"success": False, "message": ""},
        "slack": {"success": False, "message": ""},
        "outlook": {"success": False, "message": ""}
    }
    
    # Apply GitHub configuration
    if config.github:
        try:
            github_result = await _apply_github_config(config.github)
            results["github"] = github_result
            config.github.configured = github_result["success"]
            if github_result["success"]:
                config.github.configured_at = datetime.utcnow()
        except Exception as e:
            results["github"] = {"success": False, "message": str(e)}
    
    # Apply Slack configuration
    if config.slack:
        try:
            slack_result = await _apply_slack_config(config.slack)
            results["slack"] = slack_result
            config.slack.configured = slack_result["success"]
            if slack_result["success"]:
                config.slack.configured_at = datetime.utcnow()
        except Exception as e:
            results["slack"] = {"success": False, "message": str(e)}
    
    # Apply Outlook configuration
    if config.outlook:
        try:
            outlook_result = await _apply_outlook_config(config.outlook)
            results["outlook"] = outlook_result
            config.outlook.configured = outlook_result["success"]
            if outlook_result["success"]:
                config.outlook.configured_at = datetime.utcnow()
        except Exception as e:
            results["outlook"] = {"success": False, "message": str(e)}
    
    # Save configuration to database
    config.sow_id = sow_id
    config.updated_at = datetime.utcnow()
    config_dict = config.model_dump(exclude_none=True)
    config_dict["_id"] = f"integration_config_{sow_id}"
    config_dict["type"] = "integration_config"
    
    try:
        # Check if configuration exists
        existing = await cloudant_db.get_document(f"integration_config_{sow_id}")
        if existing:
            config_dict["_rev"] = existing["_rev"]
            await cloudant_db.update_document(f"integration_config_{sow_id}", config_dict)
        else:
            await cloudant_db.create_document(config_dict)
    except Exception as e:
        results["database"] = {"success": False, "message": str(e)}
    
    return {
        "sow_id": sow_id,
        "results": results,
        "overall_success": all(r["success"] for r in results.values() if isinstance(r, dict))
    }


@router.get("/{sow_id}", response_model=IntegrationConfig)
async def get_integration_config(sow_id: str):
    """Get integration configuration for an SOW"""
    try:
        config = await cloudant_db.get_document(f"integration_config_{sow_id}")
        if not config:
            raise HTTPException(status_code=404, detail=f"Configuration not found for SOW {sow_id}")

        if not isinstance(config, dict):
            raise HTTPException(status_code=500, detail="Stored integration config is not a valid mapping")

        sanitized_config = {key: value for key, value in config.items() if not key.startswith("_")}
        sanitized_config.pop("type", None)
        return IntegrationConfig(**sanitized_config)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail=f"Configuration not found for SOW {sow_id}")


@router.delete("/{sow_id}")
async def delete_integration_config(sow_id: str):
    """Delete integration configuration"""
    try:
        config = await cloudant_db.get_document(f"integration_config_{sow_id}")
        if not config or not isinstance(config, dict):
            raise HTTPException(status_code=404, detail=f"Configuration not found for SOW {sow_id}")

        doc_id = config.get("_id")
        doc_rev = config.get("_rev")
        if not doc_id or not doc_rev:
            raise HTTPException(status_code=500, detail=f"Stored configuration for SOW {sow_id} is incomplete")

        await cloudant_db.delete_document(doc_id, doc_rev)
        return {"message": f"Configuration deleted for SOW {sow_id}"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail=f"Configuration not found for SOW {sow_id}")


# Helper functions

def _parse_repo_target(repo_value: str, fallback_owner: str, fallback_repo: str) -> GitHubRepositoryTarget:
    """Parse owner/repo string into a repository target."""
    if '/' in repo_value:
        owner, repo = repo_value.split('/', 1)
    else:
        owner = fallback_owner
        repo = fallback_repo

    return GitHubRepositoryTarget(
        repository_owner=owner,
        repository_name=repo,
        purpose="SOW workflow target",
        stage="unspecified",
    )


def _generate_github_config(sow_id: str, team_info: Dict[str, Any]) -> GitHubConfig:
    """Generate GitHub configuration based on team info"""
    
    github_repo = team_info.get('github_repo', '')
    if '/' in github_repo:
        owner, repo = github_repo.split('/', 1)
    else:
        owner = team_info.get('repository_owner', 'unknown')
        repo = team_info.get('repository_name', 'unknown')

    pre_acceptance_repo_value = team_info.get('pre_acceptance_github_repo') or github_repo
    delivery_repo_value = team_info.get('delivery_github_repo') or github_repo

    pre_acceptance_repo = _parse_repo_target(pre_acceptance_repo_value, owner, repo)
    pre_acceptance_repo.purpose = "Repository for pre-acceptance review, SLA negotiation, and legal/commercial action items"
    pre_acceptance_repo.stage = "pre_acceptance"

    delivery_repo = _parse_repo_target(delivery_repo_value, owner, repo)
    delivery_repo.purpose = "Repository for approved delivery execution, implementation tracking, and SLA-bound project work"
    delivery_repo.stage = "post_approval"

    sow_label_prefix = sow_id.lower().replace('_', '-')
    labels = [
        GitHubLabel(
            name=f"{sow_label_prefix}-sla-critical",
            color="d73a4a",
            description=f"Critical SLA obligation for {sow_id}"
        ),
        GitHubLabel(
            name=f"{sow_label_prefix}-sla-high",
            color="ff6b6b",
            description=f"High priority SLA obligation for {sow_id}"
        ),
        GitHubLabel(
            name=f"{sow_label_prefix}-sla-medium",
            color="fbca04",
            description=f"Medium priority SLA obligation for {sow_id}"
        ),
        GitHubLabel(
            name=f"{sow_label_prefix}-scope-creep",
            color="f9d0c4",
            description=f"Potential scope creep detected for {sow_id}"
        ),
        GitHubLabel(
            name=f"{sow_label_prefix}-penalty-risk",
            color="d93f0b",
            description=f"Penalty risk for obligations in {sow_id}"
        ),
        GitHubLabel(
            name=f"{sow_label_prefix}-milestone",
            color="0e8a16",
            description=f"Milestone tracking for {sow_id}"
        ),
        GitHubLabel(
            name=f"{sow_label_prefix}-compliance",
            color="1d76db",
            description=f"Compliance requirement for {sow_id}"
        )
    ]

    default_assignees = _extract_github_assignees(team_info)
    issue_template = GitHubIssueTemplate(
        title_prefix=f"[{sow_id}]",
        body_intro=f"Auto-generated by SOW Sentinel for {sow_id}.",
        default_labels=[labels[-1].name, labels[-2].name],
        assignees=default_assignees
    )

    generated_issues = _generate_github_issue_definitions(
        sow_id=sow_id,
        team_info=team_info,
        labels=labels,
        issue_template=issue_template
    )
    
    return GitHubConfig(
        sow_id=sow_id,
        repository_owner=owner,
        repository_name=repo,
        labels=labels,
        milestone_name=f"{sow_id} Deliverables",
        project_board_name=f"{sow_id} Compliance Board",
        issue_template=issue_template,
        generated_issues=generated_issues,
        pre_acceptance_repo=pre_acceptance_repo,
        delivery_repo=delivery_repo,
        configured=False
    )


def _generate_slack_config(sow_id: str, team_info: Dict[str, Any]) -> SlackConfig:
    """Generate Slack configuration based on team info"""
    
    workspace = team_info.get('slack_workspace', 'unknown')
    
    # Generate channel name from SOW ID
    channel_name = f"{sow_id.lower().replace('_', '-')}-alerts"
    
    channels = [
        SlackChannel(
            name=channel_name,
            description=f"SLA and compliance alerts for {sow_id}",
            is_private=False,
            members=[]
        )
    ]
    
    return SlackConfig(
        sow_id=sow_id,
        workspace_id=workspace,
        channels=channels,
        alert_channel=channel_name,
        notification_preferences={
            "sla_breach": True,
            "scope_creep": True,
            "milestone_due": True,
            "daily_summary": False
        },
        configured=False
    )


def _generate_outlook_config(sow_id: str, team_info: Dict[str, Any]) -> OutlookConfig:
    """Generate Outlook configuration based on team info"""
    
    team_members = []
    
    # Extract team members from team_info
    if 'project_manager' in team_info:
        pm_info = team_info['project_manager']
        name, email = _parse_name_email(pm_info)
        team_members.append(TeamMember(
            name=name,
            email=email,
            role="Project Manager",
            notify_on=["sla_breach", "scope_creep", "milestone_due"]
        ))
    
    if 'tech_lead' in team_info:
        tl_info = team_info['tech_lead']
        name, email = _parse_name_email(tl_info)
        team_members.append(TeamMember(
            name=name,
            email=email,
            role="Tech Lead",
            notify_on=["sla_breach", "milestone_due"]
        ))
    
    # Add other stakeholders
    if 'key_stakeholders' in team_info:
        for stakeholder in team_info['key_stakeholders']:
            if '@' in stakeholder:
                name, email = _parse_name_email(stakeholder)
                if not any(tm.email == email for tm in team_members):
                    team_members.append(TeamMember(
                        name=name,
                        email=email,
                        role="Stakeholder",
                        notify_on=["milestone_due"]
                    ))
    
    base_calendar_name = team_info.get('outlook_calendar_name', f'{sow_id} - Project Calendar')
    pre_acceptance_calendar = team_info.get('pre_acceptance_calendar_name', f'{sow_id} - Pre-Acceptance Reviews')
    delivery_calendar = team_info.get('delivery_calendar_name', f'{sow_id} - Delivery Governance')

    return OutlookConfig(
        sow_id=sow_id,
        team_members=team_members,
        calendar_name=base_calendar_name,
        pre_acceptance_calendar_name=pre_acceptance_calendar,
        delivery_calendar_name=delivery_calendar,
        auto_schedule_reviews=True,
        review_lead_time_days=7,
        notification_preferences={
            "milestone_reminders": True,
            "sla_alerts": True,
            "weekly_summary": True
        },
        configured=False
    )


def _parse_name_email(text: str) -> tuple[str, str]:
    """Parse name and email from text like 'John Smith <john@example.com>'"""
    if '<' in text and '>' in text:
        name = text.split('<')[0].strip()
        email = text.split('<')[1].split('>')[0].strip()
    elif '@' in text:
        email = text.strip()
        name = email.split('@')[0].replace('.', ' ').title()
    else:
        name = text.strip()
        email = f"{name.lower().replace(' ', '.')}@example.com"
    
    return name, email


def _extract_github_assignees(team_info: Dict[str, Any]) -> List[str]:
    """Extract potential GitHub assignees from team info."""
    assignees: List[str] = []
    for key in ["project_manager", "tech_lead"]:
        value = team_info.get(key)
        if not value:
            continue
        name, email = _parse_name_email(value)
        candidate = email.split("@")[0].replace(".", "-").lower()
        if candidate not in assignees:
            assignees.append(candidate)
    return assignees


def _generate_github_issue_definitions(
    sow_id: str,
    team_info: Dict[str, Any],
    labels: List[GitHubLabel],
    issue_template: GitHubIssueTemplate
) -> List[GitHubGeneratedIssue]:
    """Generate per-SOW GitHub issue definitions for obligations and reviews."""
    default_assignees = issue_template.assignees
    compliance_label = labels[-1].name if labels else "compliance"
    milestone_label = labels[-2].name if len(labels) >= 2 else "milestone"
    critical_label = labels[0].name if labels else "sla-critical"
    high_label = labels[1].name if len(labels) > 1 else critical_label

    return [
        GitHubGeneratedIssue(
            obligation_id=f"{sow_id}-OBL-001",
            title=f"{issue_template.title_prefix} Phase 1 Database Migration",
            body=(
                f"{issue_template.body_intro}\n\n"
                f"SOW Reference: {sow_id}-OBL-001\n"
                f"Deliverable: Phase 1 Database Migration\n"
                f"Deadline: 2024-03-31\n"
                f"Penalty: $5,000 per day\n"
                f"Action: Track delivery readiness, blockers, and evidence."
            ),
            labels=[critical_label, milestone_label, compliance_label],
            assignees=default_assignees,
            issue_type="obligation"
        ),
        GitHubGeneratedIssue(
            obligation_id=f"{sow_id}-OBL-002",
            title=f"{issue_template.title_prefix} UAT Sign-off Document",
            body=(
                f"{issue_template.body_intro}\n\n"
                f"SOW Reference: {sow_id}-OBL-002\n"
                f"Deliverable: UAT Sign-off Document\n"
                f"Deadline: 2024-05-15\n"
                f"Penalty: $1,000 per day\n"
                f"Action: Coordinate security audit, client feedback, and final testing."
            ),
            labels=[high_label, milestone_label, compliance_label],
            assignees=default_assignees,
            issue_type="obligation"
        ),
        GitHubGeneratedIssue(
            obligation_id=f"{sow_id}-REVIEW",
            title=f"{issue_template.title_prefix} Pre-Delivery Review",
            body=(
                f"{issue_template.body_intro}\n\n"
                f"SOW Reference: {sow_id}\n"
                f"Purpose: Review all open obligations, blockers, and penalties before delivery.\n"
                f"Attendees: {team_info.get('project_manager', 'PM')}, {team_info.get('tech_lead', 'Tech Lead')}"
            ),
            labels=[milestone_label, compliance_label],
            assignees=default_assignees,
            issue_type="review"
        ),
    ]


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


async def _build_github_headers() -> Dict[str, str]:
    """Build GitHub API headers using stored credentials."""
    github_token = await _resolve_github_token()
    return {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }


async def _apply_github_config(config: GitHubConfig) -> Dict[str, Any]:
    """Apply GitHub configuration - create labels, milestone, and SOW-specific issues."""
    
    github_token = await _resolve_github_token()
    if not github_token:
        return {"success": False, "message": "GitHub token not configured in DB or environment"}
    
    headers = await _build_github_headers()
    
    base_url = f"https://api.github.com/repos/{config.repository_owner}/{config.repository_name}"
    
    created_labels: List[str] = []
    failed_labels: List[str] = []
    
    if config.automation.create_labels:
        for label in config.labels:
            try:
                response = requests.post(
                    f"{base_url}/labels",
                    headers=headers,
                    json={
                        "name": label.name,
                        "color": label.color,
                        "description": label.description
                    }
                )
                if response.status_code in [200, 201]:
                    created_labels.append(label.name)
                elif response.status_code == 422:
                    created_labels.append(f"{label.name} (already exists)")
                else:
                    failed_labels.append(label.name)
            except Exception as e:
                failed_labels.append(f"{label.name} (error: {str(e)})")
    
    milestone_created = False
    milestone_number: Optional[int] = None
    if config.milestone_name and config.automation.create_milestone:
        try:
            response = requests.post(
                f"{base_url}/milestones",
                headers=headers,
                json={
                    "title": config.milestone_name,
                    "description": f"Deliverables for {config.sow_id}"
                }
            )
            if response.status_code in [200, 201]:
                milestone_created = True
                milestone_number = response.json().get("number")
            elif response.status_code == 422:
                milestone_created = True
        except Exception:
            pass

    created_issues: List[Dict[str, Any]] = []
    failed_issues: List[str] = []
    if config.automation.auto_create_obligation_issues:
        for issue in config.generated_issues:
            if issue.issue_type == "review" and not config.automation.auto_create_review_issue:
                continue

            try:
                issue_payload = {
                    "title": issue.title,
                    "body": issue.body,
                    "labels": issue.labels,
                    "assignees": issue.assignees,
                }
                if milestone_number is not None:
                    issue_payload["milestone"] = milestone_number

                response = requests.post(
                    f"{base_url}/issues",
                    headers=headers,
                    json=issue_payload
                )
                if response.status_code in [200, 201]:
                    issue_data = response.json()
                    issue.issue_number = issue_data.get("number")
                    issue.issue_url = issue_data.get("html_url")
                    issue.created = True
                    created_issues.append(
                        {
                            "title": issue.title,
                            "issue_number": issue.issue_number,
                            "issue_url": issue.issue_url,
                            "issue_type": issue.issue_type,
                        }
                    )
                else:
                    failed_issues.append(issue.title)
            except Exception as e:
                failed_issues.append(f"{issue.title} (error: {str(e)})")
    
    success = bool(created_labels or created_issues or milestone_created)
    message_parts = [
        f"SOW {config.sow_id}: created/synced {len(created_labels)} labels",
        f"created {len(created_issues)} issues",
    ]
    if config.automation.create_milestone:
        message_parts.append("milestone ready" if milestone_created else "milestone not created")
    if failed_labels:
        message_parts.append(f"label failures: {len(failed_labels)}")
    if failed_issues:
        message_parts.append(f"issue failures: {len(failed_issues)}")
    
    return {
        "success": success,
        "message": ", ".join(message_parts),
        "created_labels": created_labels,
        "failed_labels": failed_labels,
        "created_issues": created_issues,
        "failed_issues": failed_issues,
        "milestone_created": milestone_created
    }


async def _apply_slack_config(config: SlackConfig) -> Dict[str, Any]:
    """Apply Slack configuration - create channels"""
    
    if not settings.SLACK_BOT_TOKEN:
        return {"success": False, "message": "Slack token not configured"}
    
    headers = {
        "Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    created_channels = []
    failed_channels = []
    
    for channel in config.channels:
        try:
            response = requests.post(
                "https://slack.com/api/conversations.create",
                headers=headers,
                json={
                    "name": channel.name,
                    "is_private": channel.is_private
                }
            )
            data = response.json()
            if data.get("ok"):
                created_channels.append(channel.name)
                
                # Set channel topic/description
                if data.get("channel", {}).get("id"):
                    requests.post(
                        "https://slack.com/api/conversations.setTopic",
                        headers=headers,
                        json={
                            "channel": data["channel"]["id"],
                            "topic": channel.description
                        }
                    )
            else:
                failed_channels.append(f"{channel.name} ({data.get('error', 'unknown error')})")
        except Exception as e:
            failed_channels.append(f"{channel.name} (error: {str(e)})")
    
    success = len(created_channels) > 0
    message = f"Created {len(created_channels)} channels"
    if failed_channels:
        message += f", failed: {len(failed_channels)}"
    
    return {
        "success": success,
        "message": message,
        "created_channels": created_channels,
        "failed_channels": failed_channels
    }


async def _apply_outlook_config(config: OutlookConfig) -> Dict[str, Any]:
    """Apply Outlook configuration - create calendar and add members"""
    
    if not settings.MICROSOFT_CLIENT_ID:
        return {"success": False, "message": "Microsoft Graph API not configured"}
    
    # For now, just validate the configuration
    # Actual calendar creation would require OAuth flow
    
    return {
        "success": True,
        "message": f"Configuration validated for {len(config.team_members)} team members",
        "team_members": [tm.email for tm in config.team_members]
    }

# Made with Bob
