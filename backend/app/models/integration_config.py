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


class GitHubConfig(BaseModel):
    """GitHub repository configuration for SOW"""
    sow_id: str = Field(..., description="SOW identifier")
    repository_owner: str = Field(..., description="GitHub repository owner")
    repository_name: str = Field(..., description="GitHub repository name")
    labels: List[GitHubLabel] = Field(default_factory=list, description="Custom labels for this SOW")
    milestone_name: Optional[str] = Field(None, description="GitHub milestone name")
    project_board_name: Optional[str] = Field(None, description="GitHub project board name")
    auto_create_issues: bool = Field(True, description="Automatically create issues for obligations")
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
