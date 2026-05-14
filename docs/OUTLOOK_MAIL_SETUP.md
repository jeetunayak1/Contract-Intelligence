# Outlook Mail Integration Setup Guide

## Overview

The Outlook Mail integration enables SOW Sentinel to send email notifications for critical events such as SLA breaches, penalty warnings, milestone reminders, and weekly summaries using Microsoft Graph API.

## ⚠️ Important Prerequisites

**This integration requires an Azure AD (Entra ID) directory and cannot be used with personal Microsoft/Outlook accounts.**

### Account Requirements:
- ✅ **Microsoft 365 Business/Enterprise account** (with Azure AD)
- ✅ **Azure subscription** (free tier works)
- ❌ **Personal Outlook.com/Hotmail accounts** (not supported)

### If You Have a Personal Account:

You have three options:

1. **Get a Free Azure Account** (Recommended for testing)
   - Sign up at [azure.microsoft.com/free](https://azure.microsoft.com/free)
   - Includes $200 credit and 12 months of free services
   - Creates an Azure AD directory automatically

2. **Join M365 Developer Program** (Free for development)
   - Sign up at [developer.microsoft.com/microsoft-365/dev-program](https://developer.microsoft.com/microsoft-365/dev-program)
   - Get a free Microsoft 365 E5 developer subscription (90 days renewable)
   - Includes Azure AD and 25 user licenses

3. **Use Alternative Email Service**
   - For personal use, consider using SMTP with Gmail, SendGrid, or similar
   - These don't require Azure AD setup
   - See "Alternative: SMTP Configuration" section below

## Features

- **SLA Breach Alerts**: Immediate email notifications when SLAs are at risk
- **Penalty Warnings**: Alerts for high penalty exposure
- **Milestone Reminders**: Automated reminders for upcoming deliverables
- **Weekly Summaries**: Comprehensive SOW monitoring reports
- **HTML Email Templates**: Professional, branded email notifications
- **Test Connection**: Verify configuration before going live

## Prerequisites

- Microsoft 365 or Office 365 account
- Azure Active Directory access
- Admin permissions to register applications
- Valid email address for sending notifications

## Step 1: Register Azure AD Application

### 1.1 Access Azure Portal

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Sign in with your Microsoft 365 admin account
3. Go to **Azure Active Directory** > **App registrations**
4. Click **+ New registration**

### 1.2 Configure Application

**Application Details:**
- **Name**: `SOW Sentinel Notifications`
- **Supported account types**: `Accounts in this organizational directory only (Single tenant)`
- **Redirect URI**: Leave blank (not needed for daemon apps)

Click **Register**

### 1.3 Note Application IDs

After registration, copy these values from the **Overview** page:
- **Application (client) ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Directory (tenant) ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

## Step 2: Configure API Permissions

### 2.1 Add Microsoft Graph Permissions

1. In your app registration, go to **API permissions**
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Choose **Application permissions** (not Delegated)
5. Search and add these permissions:
   - `Mail.Send` - Send mail as any user
   - `User.Read.All` - Read all users' full profiles (optional, for validation)

### 2.2 Grant Admin Consent

1. Click **Grant admin consent for [Your Organization]**
2. Confirm by clicking **Yes**
3. Verify all permissions show "Granted for [Your Organization]"

**Important**: Admin consent is required for application permissions.

## Step 3: Create Client Secret

### 3.1 Generate Secret

1. Go to **Certificates & secrets**
2. Click **+ New client secret**
3. Add description: `SOW Sentinel Production`
4. Select expiration: `24 months` (recommended)
5. Click **Add**

### 3.2 Copy Secret Value

**IMPORTANT**: Copy the secret **Value** immediately - it won't be shown again!

- **Secret Value**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

Store this securely - you'll need it for configuration.

## Step 4: Configure Sender Mailbox

### 4.1 Choose Sender Email

Select an email address that will send notifications:
- Dedicated service account: `sow-notifications@yourdomain.com` (recommended)
- Shared mailbox: `alerts@yourdomain.com`
- User mailbox: `admin@yourdomain.com`

### 4.2 Verify Mailbox Permissions

Ensure the mailbox:
- Exists in your Microsoft 365 tenant
- Has a valid license (if using user mailbox)
- Can send external emails (check mail flow rules)

## Step 5: Configure SOW Sentinel

### 5.1 Access Settings Page

1. Open SOW Sentinel web interface
2. Navigate to **Settings** from the sidebar
3. Scroll to **Outlook Mail Integration** section

### 5.2 Enter Configuration

Fill in the following fields:

| Field | Value | Example |
|-------|-------|---------|
| **Microsoft Client ID** | Application (client) ID from Step 1.3 | `12345678-1234-1234-1234-123456789abc` |
| **Microsoft Client Secret** | Secret value from Step 3.2 | `abc123~DEF456.ghi789_JKL012` |
| **Microsoft Tenant ID** | Directory (tenant) ID from Step 1.3 | `87654321-4321-4321-4321-cba987654321` |
| **Sender Email Address** | Email that will send notifications | `sow-notifications@yourdomain.com` |

### 5.3 Save Configuration

1. Click **Save Settings**
2. Wait for success confirmation
3. Configuration is encrypted and stored securely

## Step 6: Test Connection

### 6.1 Send Test Email

1. Click **Test Outlook** button
2. Wait for the test to complete (5-10 seconds)
3. Check for success message

### 6.2 Verify Test Email

1. Check the sender email inbox
2. Look for email with subject: `✅ Test Email - SOW Sentinel`
3. Verify email formatting and content

**Expected Result:**
```
Subject: ✅ Test Email - SOW Sentinel
From: sow-notifications@yourdomain.com
To: sow-notifications@yourdomain.com

Test Email Successful
Outlook integration is working correctly! This is a test email from SOW Sentinel.

Status: ✅ Connected
API: Microsoft Graph API
Test Time: 2024-01-15 10:30:00 UTC
```

## Email Notification Types

### 1. SLA Breach Alerts

**Trigger**: When SLAs are at risk of breach

**Priority**: High

**Content**:
- SOW ID and name
- Number of at-risk SLAs
- Penalty exposure amount
- Immediate action required

**Example**:
```
Subject: 🚨 SLA Breach Alert: ACME Platform Migration
Priority: High

SOW SOW-2024-ACME-001 has 3 SLAs at risk of breach.

SOW ID: SOW-2024-ACME-001
At-Risk SLAs: 3
Penalty Exposure: $50,000
```

### 2. High Penalty Warnings

**Trigger**: Significant penalty exposure detected

**Priority**: High

**Content**:
- Total penalty exposure
- Immediate risk amount
- Recommended actions

**Example**:
```
Subject: ⚠️ High Penalty Exposure: ACME Platform Migration
Priority: High

SOW SOW-2024-ACME-001 has significant penalty exposure that requires attention.

Total Exposure: $150,000
Immediate Risk: $50,000
```

### 3. Milestone Reminders

**Trigger**: Upcoming milestone (7 days before due date)

**Priority**: Normal

**Content**:
- Milestone name and description
- Due date
- Days remaining
- Deliverables

**Example**:
```
Subject: 📅 Milestone Reminder: Phase 1 Completion
Priority: Normal

Reminder: Milestone 'Phase 1 Completion' is due in 7 days.

SOW ID: SOW-2024-ACME-001
Milestone: Phase 1 Completion
Due Date: 2024-01-22
Days Remaining: 7
```

### 4. Weekly Summaries

**Trigger**: Every Monday at 9:00 AM

**Priority**: Normal

**Content**:
- Total SOWs monitored
- SOWs at risk
- Total penalty exposure
- Critical items requiring attention

**Example**:
```
Subject: 📊 Weekly SOW Summary - 2024-01-15
Priority: Normal

Summary for week ending 2024-01-15

Total SOWs Monitored: 12
SOWs At Risk: 3
Total Penalty Exposure: $250,000

Critical Items:
• SOW-2024-ACME-001: 3 SLAs at risk
• SOW-2024-BETA-002: High penalty exposure
• SOW-2024-GAMMA-003: Milestone due in 2 days
```

## Email Template Customization

### HTML Email Structure

All emails use a consistent HTML template with:
- **Header**: Color-coded by severity (Red, Orange, Blue, Green)
- **Title**: Clear, actionable subject
- **Message**: Concise description
- **Fields Table**: Structured data
- **Footer**: Branding and timestamp

### Color Coding

| Color | Hex Code | Usage |
|-------|----------|-------|
| Red | `#f44336` | SLA breaches, critical alerts |
| Orange | `#ff9800` | Warnings, high priority |
| Blue | `#2196f3` | Reminders, informational |
| Green | `#4caf50` | Success, summaries |

## Troubleshooting

### Issue: "Failed to obtain access token"

**Possible Causes**:
- Incorrect Client ID or Client Secret
- Incorrect Tenant ID
- Client secret expired

**Solutions**:
1. Verify all IDs are correct (no extra spaces)
2. Check client secret hasn't expired
3. Generate new client secret if needed
4. Ensure tenant ID matches your organization

### Issue: "Failed to send email"

**Possible Causes**:
- Sender email doesn't exist
- Insufficient permissions
- Mailbox not licensed

**Solutions**:
1. Verify sender email exists in Microsoft 365
2. Check API permissions are granted
3. Ensure mailbox has valid license
4. Check mail flow rules aren't blocking

### Issue: "Test email not received"

**Possible Causes**:
- Email in spam/junk folder
- Mail flow delay
- Incorrect sender email

**Solutions**:
1. Check spam/junk folders
2. Wait 5-10 minutes for delivery
3. Verify sender email is correct
4. Check Microsoft 365 message trace

### Issue: "Permission denied"

**Possible Causes**:
- Admin consent not granted
- Wrong permission type (Delegated vs Application)

**Solutions**:
1. Grant admin consent in Azure AD
2. Verify using Application permissions (not Delegated)
3. Re-add permissions if needed

## Security Best Practices

### 1. Client Secret Management

- **Store securely**: Never commit secrets to version control
- **Rotate regularly**: Change secrets every 6-12 months
- **Use Azure Key Vault**: For production environments
- **Monitor usage**: Review sign-in logs regularly

### 2. Sender Account Security

- **Dedicated account**: Use service account, not personal
- **Strong password**: Enable MFA if possible
- **Limited permissions**: Only Mail.Send permission
- **Audit logs**: Monitor sent emails

### 3. Email Content Security

- **No sensitive data**: Don't include passwords or tokens
- **Sanitize inputs**: Prevent injection attacks
- **Rate limiting**: Prevent email flooding
- **Recipient validation**: Verify email addresses

### 4. Compliance

- **Data retention**: Follow organizational policies
- **Privacy**: Comply with GDPR/privacy laws
- **Audit trail**: Log all email notifications
- **Consent**: Ensure recipients opted in

## API Rate Limits

Microsoft Graph API has the following limits:

| Resource | Limit | Period |
|----------|-------|--------|
| Mail.Send | 30 requests | per minute |
| Mail.Send | 10,000 requests | per day |

**Recommendations**:
- Batch notifications when possible
- Implement retry logic with exponential backoff
- Monitor API usage in Azure portal

## Integration with SOW Monitoring

### Automatic Notifications

The system automatically sends emails for:

1. **Real-time Alerts** (immediate):
   - SLA breach detected
   - High penalty exposure
   - Critical compliance issues

2. **Scheduled Notifications**:
   - Milestone reminders (7 days before)
   - Weekly summaries (Monday 9 AM)
   - Monthly reports (1st of month)

### Manual Notifications

Administrators can trigger emails:
- From SOW detail pages
- Via API endpoints
- Through admin dashboard

## Advanced Configuration

### Custom Email Templates

To customize email templates, modify:
```python
# backend/app/services/outlook_notifications.py
def _build_html_email(self, title, message, fields, color):
    # Customize HTML structure here
    pass
```

### Notification Rules

Configure notification preferences per SOW:
```python
notification_preferences = {
    "sla_breach": True,
    "penalty_warning": True,
    "milestone_reminder": True,
    "weekly_summary": False
}
```

### Multiple Sender Accounts

For different notification types:
```python
# Configure in settings
senders = {
    "alerts": "alerts@yourdomain.com",
    "reports": "reports@yourdomain.com",
    "reminders": "reminders@yourdomain.com"
}
```

## Monitoring and Maintenance

### Health Checks

Monitor integration health:
- Test connection weekly
- Review sent email logs
- Check API usage metrics
- Monitor error rates

### Maintenance Tasks

Regular maintenance:
- Rotate client secrets (every 6-12 months)
- Review and update permissions
- Clean up old email logs
- Update email templates

### Logging

Email notifications are logged with:
- Timestamp
- Recipient(s)
- Subject
- Success/failure status
- Error messages (if any)

## Support and Resources

### Microsoft Documentation

- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/)
- [Mail API Reference](https://docs.microsoft.com/en-us/graph/api/user-sendmail)
- [App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

### SOW Sentinel Resources

- [Integration Configuration Guide](INTEGRATION_CONFIGURATION.md)
- [GitHub Issues Setup](GITHUB_ISSUES_SETUP.md)
- [Slack Integration Guide](REAL_TIME_INTEGRATION_GUIDE.md)

### Getting Help

For issues or questions:
1. Check troubleshooting section above
2. Review Microsoft Graph API documentation
3. Check Azure AD sign-in logs
4. Contact your system administrator

---

## Alternative: Quick Setup for Testing (Free Azure Account)

If you want to test the Outlook integration without a Microsoft 365 subscription, follow these steps:

### Step 1: Create Free Azure Account

1. Go to [azure.microsoft.com/free](https://azure.microsoft.com/free)
2. Click **Start free**
3. Sign in with your personal Microsoft account (sankalp.bhat@outlook.com)
4. Complete the registration:
   - Verify your identity (phone verification)
   - Add a credit card (for verification only - won't be charged)
   - Agree to terms
5. Wait for Azure subscription to be created (~2 minutes)

### Step 2: Access Azure Portal

1. Go to [portal.azure.com](https://portal.azure.com)
2. Sign in with your account
3. You now have an Azure AD (Entra ID) directory!

### Step 3: Register Application

Now follow the main setup guide from **Step 1: Register Azure AD Application** above.

Your Azure AD directory will be automatically created and you can:
- Register applications
- Create service principals
- Use Microsoft Graph API
- Send emails via your Outlook account

### What You Get (Free Tier)

- **Azure AD**: Unlimited app registrations
- **Microsoft Graph API**: 1000 requests/month free
- **Email Sending**: Via your personal Outlook account
- **No Cost**: Completely free for development/testing

### Limitations

- Uses your personal email as sender
- Limited to 1000 API calls/month (plenty for testing)
- Free tier expires after 12 months (but you can create new account)

---

## Alternative: SMTP Configuration (For Personal Use)

If you prefer not to use Azure, you can configure SMTP email sending instead:

### Option 1: Gmail SMTP

**Requirements:**
- Gmail account
- App-specific password (if 2FA enabled)

**Configuration:**
```python
# backend/app/services/smtp_notifications.py
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
```

**Setup Steps:**
1. Enable 2-Step Verification in Google Account
2. Generate App Password: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Use app password in configuration

### Option 2: SendGrid (Recommended for Production)

**Requirements:**
- Free SendGrid account (100 emails/day)

**Configuration:**
```python
SMTP_SERVER = "smtp.sendgrid.net"
SMTP_PORT = 587
SMTP_USERNAME = "apikey"
SMTP_PASSWORD = "your-sendgrid-api-key"
```

**Setup Steps:**
1. Sign up at [sendgrid.com](https://sendgrid.com)
2. Verify your sender email
3. Create API key
4. Use API key as password

### Option 3: Outlook.com SMTP (Personal Accounts)

**Requirements:**
- Personal Outlook.com account
- App password

**Configuration:**
```python
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@outlook.com"
SMTP_PASSWORD = "your-app-password"
```

**Setup Steps:**
1. Go to [account.microsoft.com/security](https://account.microsoft.com/security)
2. Enable 2-Step Verification
3. Generate App Password
4. Use app password in configuration

**Note:** This uses SMTP instead of Microsoft Graph API, so you won't need Azure AD setup.

---

## Comparison: Microsoft Graph API vs SMTP

| Feature | Microsoft Graph API | SMTP |
|---------|-------------------|------|
| **Setup Complexity** | High (Azure AD required) | Low (just credentials) |
| **Best For** | Enterprise/Business | Personal/Testing |
| **Cost** | Free (1000 calls/month) | Free (varies by provider) |
| **Email Limits** | 30/minute, 10,000/day | Varies (Gmail: 500/day) |
| **Features** | Rich API, calendar, etc. | Email only |
| **Authentication** | OAuth2 | Username/Password |
| **Recommended For** | Production deployment | Development/Testing |

---

## Recommendation for Your Use Case

Since you have a personal Outlook account (`sankalp.bhat@outlook.com`), I recommend:

### For Testing/Development:
**Option 1: Create Free Azure Account** (Best)
- Takes 10 minutes to setup
- Get full Microsoft Graph API access
- No ongoing costs
- Professional solution

**Option 2: Use Gmail SMTP** (Easiest)
- Takes 2 minutes to setup
- Works immediately
- Good for quick testing
- 500 emails/day limit

### For Production:
**Option 1: Microsoft 365 Business**
- Get proper business email
- Full Azure AD integration
- Professional email domain
- Recommended for enterprise

**Option 2: SendGrid**
- Professional email service
- 100 emails/day free
- Easy to scale
- Good deliverability


**Built with ❤️ using IBM Bob AI assistance**