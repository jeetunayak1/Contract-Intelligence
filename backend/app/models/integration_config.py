"""
Integration Configuration Models
Manages GitHub, Slack, and Outlook configurations for SOWs
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class GitHubLabel(BaseModel):
    """GitHub label configuration"""
    name: str = Field(..., description="Label name")
    color: str = Field(..., description="Label color (hex without #)")
    description: str = Field(..., description="Label description")


class GitHubIssueTemplate(BaseModel):
    """Per-SOW GitHub issue template configuration"""
    title_prefix: str = Field(..., description="Prefix applied to generated issue titles")
    body_intro: str = Field(..., description="Introductory text for generated issue bodies")
    default_labels: List[str] = Field(default_factory=list, description="Default labels for all generated issues")
    assignees: List[str] = Field(default_factory=list, description="Default assignees for generated issues")


class GitHubRepositoryTarget(BaseModel):
    """Repository target used by a workflow stage"""
    repository_owner: str = Field(..., description="GitHub repository owner")
    repository_name: str = Field(..., description="GitHub repository name")
    purpose: str = Field(..., description="Why this repository is used in the workflow stage")
    stage: str = Field(..., description="Workflow stage, such as pre_acceptance or post_approval")


class GitHubAutomationSettings(BaseModel):
    """Automation settings for GitHub resources created per SOW"""
    create_labels: bool = Field(True, description="Create or sync SOW labels")
    create_milestone: bool = Field(True, description="Create milestone for the SOW")
    create_issue_templates: bool = Field(True, description="Generate issue templates or issue content per SOW")
    auto_create_obligation_issues: bool = Field(True, description="Automatically create issues for SOW obligations")
    auto_create_review_issue: bool = Field(True, description="Automatically create pre-delivery review issues")


class GitHubGeneratedIssue(BaseModel):
    """Issue definition generated for a specific SOW obligation"""
    obligation_id: str = Field(..., description="Associated SOW obligation ID")
    title: str = Field(..., description="Generated GitHub issue title")
    body: str = Field(..., description="Generated GitHub issue body")
    labels: List[str] = Field(default_factory=list, description="Labels to apply to the issue")
    assignees: List[str] = Field(default_factory=list, description="Assignees for the issue")
    issue_number: Optional[int] = Field(None, description="GitHub issue number if created")
    issue_url: Optional[str] = Field(None, description="GitHub issue URL if created")
    issue_type: str = Field("obligation", description="Type of generated issue")
    created: bool = Field(False, description="Whether the issue was created successfully")


class GitHubConfig(BaseModel):
    """GitHub repository configuration for SOW"""
    sow_id: str = Field(..., description="SOW identifier")
    repository_owner: str = Field(..., description="Default GitHub repository owner")
    repository_name: str = Field(..., description="Default GitHub repository name")
    labels: List[GitHubLabel] = Field(default_factory=list, description="Custom labels for this SOW")
    milestone_name: Optional[str] = Field(None, description="GitHub milestone name")
    project_board_name: Optional[str] = Field(None, description="GitHub project board name")
    issue_template: Optional[GitHubIssueTemplate] = Field(None, description="Issue generation template for this SOW")
    automation: GitHubAutomationSettings = Field(default_factory=GitHubAutomationSettings, description="Per-SOW GitHub automation settings")
    generated_issues: List[GitHubGeneratedIssue] = Field(default_factory=list, description="Issues generated for this SOW")
    pre_acceptance_repo: Optional[GitHubRepositoryTarget] = Field(None, description="Repository used before SOW acceptance for negotiation and review actions")
    delivery_repo: Optional[GitHubRepositoryTarget] = Field(None, description="Repository used after SOW approval for delivery execution items")
    configured: bool = Field(False, description="Configuration completed")
    configured_at: Optional[datetime] = None


class SlackChannel(BaseModel):
    """Slack channel configuration"""
    name: str = Field(..., description="Channel name (without #)")
    description: str = Field(..., description="Channel description")
    is_private: bool = Field(False, description="Private channel")
    members: List[str] = Field(default_factory=list, description="Slack user IDs to add")


class SlackConfig(BaseModel):
    """Slack workspace configuration for SOW"""
    sow_id: str = Field(..., description="SOW identifier")
    workspace_id: str = Field(..., description="Slack workspace ID")
    channels: List[SlackChannel] = Field(default_factory=list, description="Channels for this SOW")
    alert_channel: Optional[str] = Field(None, description="Primary alert channel name")
    notification_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {
            "sla_breach": True,
            "scope_creep": True,
            "milestone_due": True,
            "daily_summary": False
        },
        description="Notification preferences"
    )
    configured: bool = Field(False, description="Configuration completed")
    configured_at: Optional[datetime] = None


class TeamMember(BaseModel):
    """Team member configuration"""
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    role: str = Field(..., description="Role (PM, Tech Lead, Developer, etc.)")
    notify_on: List[str] = Field(
        default_factory=list,
        description="Notification types (sla_breach, scope_creep, milestone_due)"
    )


class OutlookConfig(BaseModel):
    """Outlook/Microsoft 365 configuration for SOW"""
    sow_id: str = Field(..., description="SOW identifier")
    team_members: List[TeamMember] = Field(default_factory=list, description="Team members")
    calendar_name: str = Field(..., description="Shared calendar name")
    pre_acceptance_calendar_name: Optional[str] = Field(None, description="Calendar used before SOW acceptance for legal/commercial clarification meetings")
    delivery_calendar_name: Optional[str] = Field(None, description="Calendar used after approval for delivery governance meetings")
    auto_schedule_reviews: bool = Field(True, description="Auto-schedule milestone reviews")
    review_lead_time_days: int = Field(7, description="Days before milestone to schedule review")
    notification_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {
            "milestone_reminders": True,
            "sla_alerts": True,
            "weekly_summary": True
        },
        description="Email notification preferences"
    )
    configured: bool = Field(False, description="Configuration completed")
    configured_at: Optional[datetime] = None


class IntegrationConfig(BaseModel):
    """Complete integration configuration for an SOW"""
    sow_id: str = Field(..., description="SOW identifier")
    team_info: Dict[str, Any] = Field(default_factory=dict, description="Per-SOW team and stakeholder context")
    github: Optional[GitHubConfig] = None
    slack: Optional[SlackConfig] = None
    outlook: Optional[OutlookConfig] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "sow_id": "SOW-2024-ACME-001",
                "team_info": {
                    "project_manager": "John Smith <john.smith@acme.com>",
                    "tech_lead": "Jane Doe <jane.doe@acme.com>",
                    "team_size": 5,
                    "github_repo": "acme-corp/platform-migration",
                    "slack_workspace": "acme-corp",
                    "key_stakeholders": ["john.smith@acme.com", "jane.doe@acme.com"]
                },
                "github": {
                    "sow_id": "SOW-2024-ACME-001",
                    "repository_owner": "acme-corp",
                    "repository_name": "platform-migration",
                    "labels": [
                        {
                            "name": "sla-critical",
                            "color": "d73a4a",
                            "description": "Critical SLA obligation"
                        },
                        {
                            "name": "scope-creep",
                            "color": "fbca04",
                            "description": "Potential scope creep"
                        }
                    ],
                    "issue_template": {
                        "title_prefix": "[SOW-2024-ACME-001]",
                        "body_intro": "Auto-generated from SOW Sentinel for this SOW.",
                        "default_labels": ["compliance", "milestone"],
                        "assignees": []
                    },
                    "automation": {
                        "create_labels": True,
                        "create_milestone": True,
                        "create_issue_templates": True,
                        "auto_create_obligation_issues": True,
                        "auto_create_review_issue": True
                    },
                    "generated_issues": [],
                    "configured": True
                },
                "slack": {
                    "sow_id": "SOW-2024-ACME-001",
                    "workspace_id": "T1234567890",
                    "channels": [
                        {
                            "name": "acme-platform-alerts",
                            "description": "SLA and compliance alerts",
                            "is_private": False
                        }
                    ],
                    "alert_channel": "acme-platform-alerts",
                    "configured": True
                },
                "outlook": {
                    "sow_id": "SOW-2024-ACME-001",
                    "team_members": [
                        {
                            "name": "John Smith",
                            "email": "john.smith@acme.com",
                            "role": "Project Manager",
                            "notify_on": ["sla_breach", "milestone_due"]
                        }
                    ],
                    "calendar_name": "ACME Platform Migration",
                    "configured": True
                }
            }
        }


class ConfigurationRequest(BaseModel):
    """Request to configure integrations with AI assistance"""
    sow_id: str = Field(..., description="SOW identifier")
    team_info: Dict[str, Any] = Field(
        ...,
        description="Team information for AI to process",
        json_schema_extra={
            "example": {
                "project_manager": "John Smith <john.smith@acme.com>",
                "tech_lead": "Jane Doe <jane.doe@acme.com>",
                "team_size": 5,
                "github_repo": "acme-corp/platform-migration",
                "slack_workspace": "acme-corp",
                "key_stakeholders": ["john.smith@acme.com", "jane.doe@acme.com"]
            }
        }
    )


class ConfigurationResponse(BaseModel):
    """AI-generated configuration response"""
    sow_id: str
    suggested_config: IntegrationConfig
    explanation: str = Field(..., description="AI explanation of the configuration")
    next_steps: List[str] = Field(..., description="Steps to complete the configuration")

# Made with Bob
