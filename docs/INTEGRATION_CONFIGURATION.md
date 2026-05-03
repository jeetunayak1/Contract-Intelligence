# AI-Powered Integration Configuration

## Overview

The Integration Configuration feature allows you to set up GitHub, Slack, and Outlook integrations for each SOW (Statement of Work) with AI assistance. The AI agent analyzes your team information and automatically configures optimal settings for tracking, notifications, and collaboration.

## Features

### 🤖 AI-Powered Configuration
- Analyzes team structure and project details
- Suggests optimal integration settings
- Creates custom labels, channels, and calendars
- Configures notification preferences automatically

### 🔧 GitHub Integration
- **Automatic Label Creation**: Creates 7 standard labels for SLA tracking
  - `sla-critical` - Critical SLA obligations
  - `sla-high` - High priority obligations
  - `sla-medium` - Medium priority obligations
  - `scope-creep` - Potential scope creep detection
  - `penalty-risk` - Risk of financial penalties
  - `milestone` - SOW milestone deliverables
  - `compliance` - Compliance requirements

- **Milestone Management**: Creates project milestones
- **Auto-Issue Creation**: Automatically creates GitHub issues for obligations

### 💬 Slack Integration
- **Channel Creation**: Creates dedicated alert channels
- **Notification Configuration**: Configures notification preferences
  - SLA breach alerts
  - Scope creep detection
  - Milestone due reminders
  - Daily summaries (optional)

### 📧 Outlook Integration
- **Team Member Management**: Adds team members with roles
- **Calendar Creation**: Creates shared project calendar
- **Auto-Scheduling**: Schedules milestone reviews automatically
- **Email Notifications**: Configures email alerts for key events

## How It Works

### Step 1: Provide Team Information

Navigate to **Integration Setup** from the sidebar and provide:

1. **SOW ID**: Your Statement of Work identifier
2. **Project Manager**: Name and email (format: `Name <email@example.com>`)
3. **Tech Lead**: Name and email
4. **Team Size**: Number of team members
5. **GitHub Repository**: Repository path (format: `owner/repository`)
6. **Slack Workspace**: Workspace identifier
7. **Key Stakeholders**: List of stakeholder emails

### Step 2: AI Generates Configuration

Click **"Generate AI Configuration"** and the AI agent will:

1. Analyze your team structure
2. Determine optimal integration settings
3. Suggest custom labels and channels
4. Configure notification preferences
5. Set up team member roles

The AI provides a detailed explanation of its configuration decisions.

### Step 3: Review Configuration

Review the suggested configuration for each integration:

#### GitHub Configuration
- Repository details
- Custom labels with colors
- Milestone name
- Auto-issue creation settings

#### Slack Configuration
- Workspace details
- Channel names and descriptions
- Alert channel designation
- Notification preferences

#### Outlook Configuration
- Team member list with roles
- Calendar name
- Auto-scheduling settings
- Email notification preferences

### Step 4: Apply Configuration

Click **"Apply Configuration"** to:

1. Create GitHub labels in your repository
2. Create Slack channels in your workspace
3. Set up Outlook calendar and team
4. Save configuration to database

The system provides real-time feedback on each integration's status.

## API Endpoints

### Generate AI Configuration

```http
POST /api/v1/integrations/configure
Content-Type: application/json

{
  "sow_id": "SOW-2024-ACME-001",
  "team_info": {
    "project_manager": "John Smith <john.smith@acme.com>",
    "tech_lead": "Jane Doe <jane.doe@acme.com>",
    "team_size": 5,
    "github_repo": "acme-corp/platform-migration",
    "slack_workspace": "acme-corp",
    "key_stakeholders": [
      "john.smith@acme.com",
      "jane.doe@acme.com"
    ]
  }
}
```

**Response:**
```json
{
  "sow_id": "SOW-2024-ACME-001",
  "suggested_config": {
    "github": {
      "repository_owner": "acme-corp",
      "repository_name": "platform-migration",
      "labels": [...],
      "milestone_name": "SOW-2024-ACME-001 Deliverables"
    },
    "slack": {
      "workspace_id": "acme-corp",
      "channels": [...],
      "alert_channel": "sow-2024-acme-001-alerts"
    },
    "outlook": {
      "team_members": [...],
      "calendar_name": "SOW-2024-ACME-001 - Project Calendar"
    }
  },
  "explanation": "AI explanation of configuration...",
  "next_steps": [...]
}
```

### Apply Configuration

```http
POST /api/v1/integrations/apply/{sow_id}
Content-Type: application/json

{
  "github": {...},
  "slack": {...},
  "outlook": {...}
}
```

**Response:**
```json
{
  "sow_id": "SOW-2024-ACME-001",
  "results": {
    "github": {
      "success": true,
      "message": "Created 7 labels, milestone created",
      "created_labels": ["sla-critical", "sla-high", ...]
    },
    "slack": {
      "success": true,
      "message": "Created 1 channels",
      "created_channels": ["sow-2024-acme-001-alerts"]
    },
    "outlook": {
      "success": true,
      "message": "Configuration validated for 2 team members"
    }
  },
  "overall_success": true
}
```

### Get Configuration

```http
GET /api/v1/integrations/{sow_id}
```

### Delete Configuration

```http
DELETE /api/v1/integrations/{sow_id}
```

## Configuration Requirements

### GitHub
- Personal Access Token with `repo` scope
- Repository admin access
- Environment variables:
  ```bash
  GITHUB_TOKEN=your_github_token
  GITHUB_OWNER=your_username_or_org
  GITHUB_REPO=your_repository
  ```

### Slack
- Slack Bot Token with permissions:
  - `channels:manage` - Create channels
  - `channels:write` - Set channel topics
  - `chat:write` - Send messages
- Environment variables:
  ```bash
  SLACK_BOT_TOKEN=xoxb-your-bot-token
  SLACK_WORKSPACE_ID=your_workspace_id
  ```

### Outlook (Microsoft Graph API)
- Azure AD App Registration
- Microsoft Graph API permissions:
  - `Calendars.ReadWrite` - Manage calendars
  - `User.Read.All` - Read user profiles
- Environment variables:
  ```bash
  MICROSOFT_CLIENT_ID=your_client_id
  MICROSOFT_CLIENT_SECRET=your_client_secret
  MICROSOFT_TENANT_ID=your_tenant_id
  ```

## Label Descriptions

### SLA Labels

| Label | Color | Description | Use Case |
|-------|-------|-------------|----------|
| `sla-critical` | Red (#d73a4a) | Critical SLA obligation | Immediate attention required, penalty risk |
| `sla-high` | Light Red (#ff6b6b) | High priority SLA | Important but not immediate |
| `sla-medium` | Yellow (#fbca04) | Medium priority SLA | Standard tracking |

### Risk Labels

| Label | Color | Description | Use Case |
|-------|-------|-------------|----------|
| `scope-creep` | Peach (#f9d0c4) | Potential scope creep | Work not in original SOW |
| `penalty-risk` | Dark Orange (#d93f0b) | Financial penalty risk | Deadline approaching |

### Tracking Labels

| Label | Color | Description | Use Case |
|-------|-------|-------------|----------|
| `milestone` | Green (#0e8a16) | SOW milestone | Major deliverable |
| `compliance` | Blue (#1d76db) | Compliance requirement | Regulatory or contractual |

## Notification Preferences

### Slack Notifications

| Event | Default | Description |
|-------|---------|-------------|
| SLA Breach | ✅ Enabled | Alert when SLA is breached |
| Scope Creep | ✅ Enabled | Alert when scope creep detected |
| Milestone Due | ✅ Enabled | Reminder before milestone |
| Daily Summary | ❌ Disabled | Daily status summary |

### Outlook Notifications

| Event | Default | Description |
|-------|---------|-------------|
| Milestone Reminders | ✅ Enabled | Email before milestones |
| SLA Alerts | ✅ Enabled | Email for SLA issues |
| Weekly Summary | ✅ Enabled | Weekly status report |

## Team Member Roles

### Project Manager
- **Notifications**: All events (SLA breach, scope creep, milestones)
- **Responsibilities**: Overall project oversight
- **Calendar Access**: Full access to project calendar

### Tech Lead
- **Notifications**: SLA breach, milestones
- **Responsibilities**: Technical delivery
- **Calendar Access**: Full access to project calendar

### Stakeholder
- **Notifications**: Milestone due
- **Responsibilities**: Review and approval
- **Calendar Access**: Read-only access

## Best Practices

### 1. Complete Team Information
- Provide accurate email addresses
- Include all key stakeholders
- Specify correct GitHub repository

### 2. Review AI Suggestions
- Check label names and colors
- Verify channel names
- Confirm team member roles

### 3. Test Notifications
- Send test alerts after configuration
- Verify email delivery
- Check Slack channel access

### 4. Update Configuration
- Reconfigure when team changes
- Update stakeholder list regularly
- Adjust notification preferences as needed

### 5. Monitor Integration Health
- Check GitHub label usage
- Monitor Slack channel activity
- Review calendar event creation

## Troubleshooting

### GitHub Labels Not Created
- **Issue**: Labels already exist
- **Solution**: Labels are reused if they exist
- **Check**: Repository permissions

### Slack Channel Creation Failed
- **Issue**: Channel name already taken
- **Solution**: Use unique channel names
- **Check**: Bot token permissions

### Outlook Calendar Not Created
- **Issue**: OAuth not configured
- **Solution**: Complete Azure AD app registration
- **Check**: Microsoft Graph API permissions

### Configuration Not Saved
- **Issue**: Database connection error
- **Solution**: Check Cloudant credentials
- **Check**: Network connectivity

## Security Considerations

### API Tokens
- Store tokens in environment variables
- Never commit tokens to version control
- Rotate tokens regularly
- Use least privilege access

### Team Member Data
- Validate email addresses
- Respect privacy settings
- Comply with data protection regulations
- Audit access logs

### Integration Permissions
- Review bot permissions regularly
- Limit access to necessary scopes
- Monitor API usage
- Revoke unused tokens

## Future Enhancements

### Phase 1
- [ ] Support for multiple GitHub repositories
- [ ] Custom label templates
- [ ] Slack workflow automation
- [ ] Calendar event templates

### Phase 2
- [ ] Microsoft Teams integration
- [ ] Jira integration (optional)
- [ ] Custom notification rules
- [ ] Integration health dashboard

### Phase 3
- [ ] AI-powered notification optimization
- [ ] Predictive configuration suggestions
- [ ] Integration analytics
- [ ] Multi-SOW configuration

## Support

For issues or questions:
- Check the [GitHub Issues Setup Guide](GITHUB_ISSUES_SETUP.md)
- Review the [Outlook Calendar Setup Guide](OUTLOOK_CALENDAR_SETUP.md)
- Contact your system administrator
- Submit a support ticket

---

**Built with ❤️ using IBM Bob AI assistance**