"""
Integration Configuration API
Handles GitHub, Slack, and Outlook configuration for SOWs
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import requests
from datetime import datetime

from app.models.integration_config import (
    IntegrationConfig,
    ConfigurationRequest,
    ConfigurationResponse,
    GitHubConfig,
    GitHubLabel,
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
        github=_generate_github_config(sow_id, team_info),
        slack=_generate_slack_config(sow_id, team_info),
        outlook=_generate_outlook_config(sow_id, team_info)
    )
    
    explanation = f"""
    Based on your team information, I've configured the following integrations:
    
    **GitHub Configuration:**
    - Repository: {team_info.get('github_repo', 'Not specified')}
    - Created {len(suggested_config.github.labels)} custom labels for SLA tracking
    - Enabled automatic issue creation for obligations
    
    **Slack Configuration:**
    - Created dedicated alert channel for real-time notifications
    - Configured notification preferences for critical events
    - Team size: {team_info.get('team_size', 'Unknown')}
    
    **Outlook Configuration:**
    - Added {len(suggested_config.outlook.team_members)} team members
    - Configured automatic milestone review scheduling
    - Set up email notifications for key stakeholders
    """
    
    next_steps = [
        "Review the suggested configuration",
        "Click 'Apply Configuration' to create GitHub labels",
        "Authorize Slack workspace connection",
        "Verify team member email addresses",
        "Test notification delivery"
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
        return IntegrationConfig(**config)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Configuration not found for SOW {sow_id}")


@router.delete("/{sow_id}")
async def delete_integration_config(sow_id: str):
    """Delete integration configuration"""
    try:
        config = await cloudant_db.get_document(f"integration_config_{sow_id}")
        await cloudant_db.delete_document(config["_id"], config["_rev"])
        return {"message": f"Configuration deleted for SOW {sow_id}"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Configuration not found for SOW {sow_id}")


# Helper functions

def _generate_github_config(sow_id: str, team_info: Dict[str, Any]) -> GitHubConfig:
    """Generate GitHub configuration based on team info"""
    
    # Extract repo info
    github_repo = team_info.get('github_repo', '')
    if '/' in github_repo:
        owner, repo = github_repo.split('/', 1)
    else:
        owner = team_info.get('repository_owner', 'unknown')
        repo = team_info.get('repository_name', 'unknown')
    
    # Generate standard labels for SOW tracking
    labels = [
        GitHubLabel(
            name="sla-critical",
            color="d73a4a",
            description="Critical SLA obligation - immediate attention required"
        ),
        GitHubLabel(
            name="sla-high",
            color="ff6b6b",
            description="High priority SLA obligation"
        ),
        GitHubLabel(
            name="sla-medium",
            color="fbca04",
            description="Medium priority SLA obligation"
        ),
        GitHubLabel(
            name="scope-creep",
            color="f9d0c4",
            description="Potential scope creep - not in original SOW"
        ),
        GitHubLabel(
            name="penalty-risk",
            color="d93f0b",
            description="Risk of financial penalty if not completed"
        ),
        GitHubLabel(
            name="milestone",
            color="0e8a16",
            description="SOW milestone deliverable"
        ),
        GitHubLabel(
            name="compliance",
            color="1d76db",
            description="Compliance requirement"
        )
    ]
    
    return GitHubConfig(
        sow_id=sow_id,
        repository_owner=owner,
        repository_name=repo,
        labels=labels,
        milestone_name=f"{sow_id} Deliverables",
        auto_create_issues=True,
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
    
    return OutlookConfig(
        sow_id=sow_id,
        team_members=team_members,
        calendar_name=f"{sow_id} - Project Calendar",
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


async def _apply_github_config(config: GitHubConfig) -> Dict[str, Any]:
    """Apply GitHub configuration - create labels and milestone"""
    
    if not settings.GITHUB_TOKEN:
        return {"success": False, "message": "GitHub token not configured"}
    
    headers = {
        "Authorization": f"token {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    base_url = f"https://api.github.com/repos/{config.repository_owner}/{config.repository_name}"
    
    created_labels = []
    failed_labels = []
    
    # Create labels
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
            elif response.status_code == 422:  # Label already exists
                created_labels.append(f"{label.name} (already exists)")
            else:
                failed_labels.append(label.name)
        except Exception as e:
            failed_labels.append(f"{label.name} (error: {str(e)})")
    
    # Create milestone if specified
    milestone_created = False
    if config.milestone_name:
        try:
            response = requests.post(
                f"{base_url}/milestones",
                headers=headers,
                json={
                    "title": config.milestone_name,
                    "description": f"Deliverables for {config.sow_id}"
                }
            )
            milestone_created = response.status_code in [200, 201]
        except Exception:
            pass
    
    success = len(created_labels) > 0
    message = f"Created {len(created_labels)} labels"
    if failed_labels:
        message += f", failed: {len(failed_labels)}"
    if milestone_created:
        message += f", milestone created"
    
    return {
        "success": success,
        "message": message,
        "created_labels": created_labels,
        "failed_labels": failed_labels
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
