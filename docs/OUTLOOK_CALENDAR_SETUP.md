# Outlook Calendar Integration Setup Guide

## Overview

SOW Sentinel integrates with Microsoft Outlook Calendar via Microsoft Graph API to automatically schedule compliance reviews, milestone checkpoints, and deadline reminders. This guide walks you through the complete setup process.

---

## Prerequisites

- Microsoft 365 account (Business or Personal)
- Azure account (free tier works)
- Admin access to create Azure AD applications
- Outlook Calendar access

---

## Step 1: Register Application in Azure Portal

### 1.1 Access Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Sign in with your Microsoft account
3. Search for **Azure Active Directory** in the top search bar

### 1.2 Register New Application

1. In Azure AD, click **App registrations** (left sidebar)
2. Click **+ New registration**
3. Fill in the details:
   - **Name**: `SOW Sentinel Calendar Integration`
   - **Supported account types**: 
     - Select **Accounts in this organizational directory only** (for business)
     - Or **Accounts in any organizational directory and personal Microsoft accounts** (for broader access)
   - **Redirect URI**: 
     - Platform: **Web**
     - URI: `http://localhost:8000/auth/callback`
4. Click **Register**

### 1.3 Note Application Details

After registration, copy these values (you'll need them later):

```
Application (client) ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Directory (tenant) ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## Step 2: Configure API Permissions

### 2.1 Add Microsoft Graph Permissions

1. In your app registration, click **API permissions** (left sidebar)
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Choose **Delegated permissions**

### 2.2 Select Required Permissions

Add these permissions:

```
✓ Calendars.ReadWrite (Read and write user calendars)
✓ Calendars.ReadWrite.Shared (Read and write shared calendars)
✓ User.Read (Sign in and read user profile)
✓ offline_access (Maintain access to data)
```

### 2.3 Grant Admin Consent

1. Click **Grant admin consent for [Your Organization]**
2. Click **Yes** to confirm
3. Verify all permissions show "Granted" status

---

## Step 3: Create Client Secret

### 3.1 Generate Secret

1. Click **Certificates & secrets** (left sidebar)
2. Click **+ New client secret**
3. Configure:
   - **Description**: `SOW Sentinel Production`
   - **Expires**: **180 days** (or based on your security policy)
4. Click **Add**

### 3.2 Copy Secret Value

**CRITICAL**: Copy the secret value immediately (you won't see it again)

```
Secret Value: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Step 4: Configure Environment Variables

### 4.1 Update `.env` File

Open `backend/.env` and add:

```bash
# Microsoft Graph API (Outlook Calendar)
MICROSOFT_CLIENT_ID=your-application-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret-value
MICROSOFT_TENANT_ID=your-directory-tenant-id
MICROSOFT_REDIRECT_URI=http://localhost:8000/auth/callback

# Optional: Specific calendar to use (leave empty for default)
MICROSOFT_CALENDAR_ID=
```

**Example**:
```bash
MICROSOFT_CLIENT_ID=12345678-1234-1234-1234-123456789abc
MICROSOFT_CLIENT_SECRET=abc~123456789abcdefghijklmnopqrstuvwxyz
MICROSOFT_TENANT_ID=87654321-4321-4321-4321-cba987654321
MICROSOFT_REDIRECT_URI=http://localhost:8000/auth/callback
```

### 4.2 Verify Configuration

Test the configuration:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -c "
from app.core.config import settings
print(f'Client ID: {settings.MICROSOFT_CLIENT_ID[:8]}...')
print(f'Tenant ID: {settings.MICROSOFT_TENANT_ID[:8]}...')
print(f'Secret configured: {bool(settings.MICROSOFT_CLIENT_SECRET)}')
"
```

---

## Step 5: Authenticate and Get Access Token

### 5.1 Start the Backend Server

```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main_demo:app --reload
```

### 5.2 Initiate OAuth Flow

1. Open browser and navigate to:
   ```
   http://localhost:8000/auth/microsoft/login
   ```

2. You'll be redirected to Microsoft login page
3. Sign in with your Microsoft account
4. Grant permissions when prompted
5. You'll be redirected back to the application

### 5.3 Verify Token Storage

The access token and refresh token are automatically stored. Verify:

```bash
curl http://localhost:8000/api/v1/auth/status
```

Expected response:
```json
{
  "authenticated": true,
  "user": "user@company.com",
  "token_expires": "2024-05-02T18:00:00Z"
}
```

---

## Step 6: Test Calendar Integration

### 6.1 Create Test Event

```bash
curl -X POST http://localhost:8000/api/v1/test/outlook-event \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test SOW Compliance Review",
    "start": "2024-05-10T14:00:00",
    "end": "2024-05-10T15:00:00",
    "attendees": ["colleague@company.com"]
  }'
```

### 6.2 Verify in Outlook

1. Open Outlook Calendar (web or desktop)
2. Check for the test event on May 10th at 2:00 PM
3. Verify attendees are invited

### 6.3 Run Integration Tests

```bash
cd backend
python -m pytest tests/test_outlook_integration.py -v
```

---

## Step 7: Configure Calendar Event Templates

### 7.1 Pre-Delivery Review Template

SOW Sentinel uses templates for different event types. Configure in `backend/app/config/calendar_templates.py`:

```python
PRE_DELIVERY_REVIEW = {
    "subject": "SOW Compliance Review: {obligation_description}",
    "body": {
        "contentType": "HTML",
        "content": """
        <h2>Pre-Delivery Review</h2>
        <p><strong>SOW Reference:</strong> {obligation_id}</p>
        <p><strong>Deadline:</strong> {deadline}</p>
        <p><strong>Penalty:</strong> ${penalty_amount}/{penalty_frequency}</p>
        
        <h3>Review Checklist</h3>
        <ul>
            <li>Verify all deliverables are complete</li>
            <li>Review quality standards</li>
            <li>Confirm client sign-off process</li>
            <li>Check for scope creep</li>
        </ul>
        
        <p><strong>Risk Level:</strong> {risk_level}</p>
        """
    },
    "isReminderOn": True,
    "reminderMinutesBeforeStart": 60,
    "categories": ["SOW Compliance", "High Priority"]
}
```

---

## Step 8: Set Up Recurring Events

### 8.1 Weekly Progress Sync

Configure recurring meetings for ongoing SOW tracking:

```python
from app.services.outlook_service import OutlookService

outlook = OutlookService()

# Create weekly progress sync
event = outlook.create_recurring_event(
    subject="SOW Progress Review: Acme Project",
    start_date="2024-05-01T10:00:00",
    duration_minutes=30,
    recurrence={
        "pattern": {
            "type": "weekly",
            "interval": 1,
            "daysOfWeek": ["monday"]
        },
        "range": {
            "type": "endDate",
            "startDate": "2024-05-01",
            "endDate": "2024-12-31"
        }
    },
    attendees=["pm@company.com", "tech-lead@company.com"]
)
```

---

## Step 9: Configure Notifications and Reminders

### 9.1 Set Default Reminder Times

Update `backend/app/config/calendar_config.py`:

```python
REMINDER_SETTINGS = {
    "critical": {
        "minutes_before": 60,  # 1 hour
        "additional_reminders": [1440, 2880]  # 1 day, 2 days
    },
    "high": {
        "minutes_before": 120,  # 2 hours
        "additional_reminders": [1440]  # 1 day
    },
    "medium": {
        "minutes_before": 240,  # 4 hours
        "additional_reminders": []
    },
    "low": {
        "minutes_before": 480,  # 8 hours
        "additional_reminders": []
    }
}
```

### 9.2 Enable Email Notifications

Configure in Azure AD app:
1. Go to **API permissions**
2. Add **Mail.Send** permission
3. Grant admin consent

Update `.env`:
```bash
MICROSOFT_ENABLE_EMAIL_NOTIFICATIONS=true
```

---

## Usage Examples

### Create Compliance Review Meeting

```python
from app.services.outlook_service import OutlookService
from datetime import datetime, timedelta

outlook = OutlookService()

# Schedule pre-delivery review 48 hours before deadline
deadline = datetime(2024, 5, 15, 17, 0, 0)
review_time = deadline - timedelta(hours=48)

event = outlook.create_compliance_review(
    obligation_id="OBL-001",
    description="UAT Sign-off Documentation",
    review_time=review_time,
    deadline=deadline,
    penalty_amount=5000,
    attendees=[
        "pm@company.com",
        "tech-lead@company.com",
        "qa-lead@company.com"
    ],
    risk_level="critical"
)

print(f"Created event: {event['webLink']}")
```

### Update Event When Status Changes

```python
# Update event when milestone is completed
outlook.update_event_status(
    event_id=event['id'],
    status="completed",
    add_note="UAT documentation completed ahead of schedule"
)
```

### Cancel Event if Obligation is Waived

```python
# Cancel event with notification
outlook.cancel_event(
    event_id=event['id'],
    cancellation_message="SOW obligation waived per client request"
)
```

### Query Upcoming SOW Events

```python
# Get all SOW-related events in next 30 days
events = outlook.get_sow_events(
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=30),
    categories=["SOW Compliance"]
)

for event in events:
    print(f"{event['subject']} - {event['start']['dateTime']}")
```

---

## Troubleshooting

### Issue: "Invalid client secret"

**Solution**: 
1. Verify secret hasn't expired
2. Check for extra spaces in `.env` file
3. Regenerate secret in Azure Portal if needed

### Issue: "Insufficient privileges"

**Solution**:
1. Verify API permissions are granted
2. Ensure admin consent is provided
3. Check user has calendar access

### Issue: "Token expired"

**Solution**: SOW Sentinel automatically refreshes tokens, but if issues persist:
1. Re-authenticate via `/auth/microsoft/login`
2. Check refresh token is stored correctly
3. Verify `offline_access` permission is granted

### Issue: Events not appearing in calendar

**Solution**:
1. Check calendar ID (use default if not specified)
2. Verify time zone settings
3. Check user has write permissions to calendar

---

## Advanced Configuration

### Use Shared Calendar

To create events in a shared calendar:

1. Get the calendar ID:
```bash
curl http://localhost:8000/api/v1/outlook/calendars
```

2. Update `.env`:
```bash
MICROSOFT_CALENDAR_ID=AAMkAGI2T...
```

### Configure Time Zones

Set default time zone in `.env`:
```bash
MICROSOFT_DEFAULT_TIMEZONE=Asia/Calcutta
```

### Enable Teams Meeting Integration

Add Teams meeting to calendar events:

```python
event = outlook.create_event(
    subject="SOW Review",
    start="2024-05-10T14:00:00",
    end="2024-05-10T15:00:00",
    is_online_meeting=True,
    online_meeting_provider="teamsForBusiness"
)
```

---

## Security Best Practices

1. **Secret Rotation**: Rotate client secrets every 180 days
2. **Least Privilege**: Only request required permissions
3. **Token Storage**: Store tokens securely (encrypted at rest)
4. **HTTPS Only**: Use HTTPS in production (update redirect URI)
5. **Audit Logs**: Enable Azure AD audit logs for monitoring

---

## Production Deployment

### Update Redirect URI

1. In Azure Portal, update redirect URI to production URL:
   ```
   https://your-domain.com/auth/callback
   ```

2. Update `.env`:
   ```bash
   MICROSOFT_REDIRECT_URI=https://your-domain.com/auth/callback
   ```

### Enable Multi-User Support

For multi-tenant applications:
1. Change account type to "Multitenant"
2. Implement user-specific token storage
3. Add user consent flow

---

## API Rate Limits

Microsoft Graph API limits:
- **Per app**: 10,000 requests per 10 minutes
- **Per user**: 2,000 requests per 10 minutes

SOW Sentinel implements automatic throttling and retry logic.

---

## Support

For issues or questions:
- Microsoft Graph Documentation: [docs.microsoft.com/graph](https://docs.microsoft.com/graph)
- Azure Support: [Azure Portal](https://portal.azure.com)
- SOW Sentinel Issues: [GitHub Issues](https://github.com/your-org/sow-sentinel/issues)

---

**Next Steps**: 
- [Complete Integration Testing](INTEGRATION_TESTING.md)
- [Deploy to Production](DEPLOYMENT.md)
- [Monitor and Maintain](MONITORING.md)