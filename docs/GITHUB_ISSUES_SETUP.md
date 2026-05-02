# GitHub Issues Integration Setup Guide

## Overview

SOW Sentinel integrates with GitHub Issues to automatically create, track, and manage compliance tasks based on SOW obligations. This guide walks you through setting up the integration.

---

## Prerequisites

- GitHub account with repository access
- Repository where issues will be created
- Admin or write permissions on the repository

---

## Step 1: Create a GitHub Personal Access Token

### 1.1 Navigate to GitHub Settings

1. Log in to GitHub
2. Click your profile picture (top-right) → **Settings**
3. Scroll down to **Developer settings** (bottom-left)
4. Click **Personal access tokens** → **Tokens (classic)**

### 1.2 Generate New Token

1. Click **Generate new token** → **Generate new token (classic)**
2. Give it a descriptive name: `SOW Sentinel Integration`
3. Set expiration: **90 days** (or custom based on your security policy)

### 1.3 Select Required Scopes

Check the following permissions:

```
✓ repo (Full control of private repositories)
  ✓ repo:status
  ✓ repo_deployment
  ✓ public_repo
  ✓ repo:invite
  ✓ security_events

✓ workflow (Update GitHub Action workflows)

✓ project (Full control of projects)
  ✓ read:project
```

### 1.4 Generate and Copy Token

1. Click **Generate token**
2. **IMPORTANT**: Copy the token immediately (you won't see it again)
3. Store it securely (we'll add it to `.env` next)

---

## Step 2: Configure Environment Variables

### 2.1 Update `.env` File

Open `backend/.env` and add:

```bash
# GitHub Integration
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_OWNER=your-github-username-or-org
GITHUB_REPO=your-repository-name
```

**Example**:
```bash
GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz
GITHUB_OWNER=acme-corp
GITHUB_REPO=sow-sentinel
```

### 2.2 Verify Configuration

Test the connection:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -c "
from app.core.config import settings
print(f'GitHub Owner: {settings.GITHUB_OWNER}')
print(f'GitHub Repo: {settings.GITHUB_REPO}')
print(f'Token configured: {bool(settings.GITHUB_TOKEN)}')
"
```

---

## Step 3: Set Up Repository Labels

### 3.1 Create SOW-Specific Labels

SOW Sentinel uses custom labels to categorize issues. Create these in your repository:

1. Go to your repository → **Issues** → **Labels**
2. Click **New label** and create:

| Label Name | Color | Description |
|------------|-------|-------------|
| `sow-compliance` | `#0052CC` | SOW obligation tracking |
| `risk-critical` | `#D73A4A` | Critical financial risk |
| `risk-high` | `#FF6B6B` | High financial risk |
| `risk-medium` | `#FFA500` | Medium financial risk |
| `risk-low` | `#28A745` | Low financial risk |
| `penalty-exposure` | `#B60205` | Liquidated damages risk |
| `scope-creep` | `#FBCA04` | Out-of-scope work detected |
| `review-required` | `#5319E7` | Pre-delivery review needed |

### 3.2 Automated Label Creation (Optional)

Run this script to create labels automatically:

```bash
cd backend
python scripts/setup_github_labels.py
```

---

## Step 4: Configure Issue Templates

### 4.1 Create Issue Template Directory

```bash
mkdir -p .github/ISSUE_TEMPLATE
```

### 4.2 Create SOW Compliance Template

Create `.github/ISSUE_TEMPLATE/sow-compliance.md`:

```markdown
---
name: SOW Compliance Task
about: Track SOW obligation or deliverable
title: '[SOW] '
labels: sow-compliance
assignees: ''
---

## SOW Reference
**Obligation ID**: OBL-XXX
**SOW Section**: X.X
**Deadline**: YYYY-MM-DD
**Penalty**: $X,XXX per day

## Description
<!-- Describe the SOW obligation -->

## Definition of Done
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Financial Impact
**Penalty Exposure**: $X,XXX
**Risk Level**: Critical/High/Medium/Low

## Related Links
- SOW Document: [Link]
- Project Board: [Link]
```

---

## Step 5: Set Up GitHub Projects (Optional)

### 5.1 Create SOW Tracking Project

1. Go to your repository → **Projects** → **New project**
2. Name: `SOW Compliance Tracker`
3. Template: **Board**

### 5.2 Add Custom Fields

Add these custom fields to track SOW metrics:

| Field Name | Type | Options |
|------------|------|---------|
| `SOW Reference` | Text | - |
| `Deadline` | Date | - |
| `Penalty Amount` | Number | - |
| `Risk Level` | Single Select | Critical, High, Medium, Low |
| `Days Remaining` | Number | - |

---

## Step 6: Test the Integration

### 6.1 Manual Test

Run the test script:

```bash
cd backend
python -m pytest tests/test_github_integration.py -v
```

### 6.2 Create Test Issue

Test issue creation via API:

```bash
curl -X POST http://localhost:8000/api/v1/test/github-issue \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test SOW Compliance Issue",
    "body": "Testing GitHub integration",
    "labels": ["sow-compliance", "risk-low"]
  }'
```

### 6.3 Verify in GitHub

1. Go to your repository → **Issues**
2. You should see the test issue created
3. Verify labels are applied correctly

---

## Step 7: Configure Webhooks (Optional)

### 7.1 Set Up Webhook for Real-Time Updates

1. Go to repository → **Settings** → **Webhooks**
2. Click **Add webhook**
3. Configure:
   - **Payload URL**: `https://your-domain.com/api/v1/webhooks/github`
   - **Content type**: `application/json`
   - **Secret**: Generate a random secret and add to `.env`
   - **Events**: Select `Issues`, `Issue comments`, `Pull requests`

### 7.2 Add Webhook Secret to `.env`

```bash
GITHUB_WEBHOOK_SECRET=your-random-secret-here
```

---

## Usage Examples

### Create Issue from SOW Obligation

```python
from app.services.github_service import GitHubService

github = GitHubService()

# Create compliance issue
issue = github.create_compliance_issue(
    title="SOW: Complete UAT Documentation",
    obligation_id="OBL-001",
    deadline="2024-05-15",
    penalty_amount=5000,
    risk_level="critical",
    description="Complete UAT sign-off documentation per SOW Section 4.2"
)

print(f"Created issue #{issue.number}")
```

### Update Issue Status

```python
# Update issue when milestone is reached
github.update_issue_status(
    issue_number=123,
    status="completed",
    comment="UAT documentation completed and signed off"
)
```

### Query SOW Issues

```python
# Get all critical SOW issues
critical_issues = github.get_sow_issues(
    labels=["sow-compliance", "risk-critical"],
    state="open"
)

for issue in critical_issues:
    print(f"#{issue.number}: {issue.title} - Due: {issue.deadline}")
```

---

## Troubleshooting

### Issue: "Bad credentials" Error

**Solution**: Verify your GitHub token:
1. Check token hasn't expired
2. Ensure token has correct scopes
3. Regenerate token if needed

### Issue: "Resource not accessible by integration"

**Solution**: Check repository permissions:
1. Verify you have write access to the repository
2. Ensure token has `repo` scope
3. Check if repository is private (requires full `repo` scope)

### Issue: Labels Not Applied

**Solution**: Create labels first:
1. Run label setup script
2. Or manually create labels in GitHub
3. Verify label names match exactly (case-sensitive)

---

## Security Best Practices

1. **Token Storage**: Never commit tokens to git
2. **Token Rotation**: Rotate tokens every 90 days
3. **Least Privilege**: Only grant required scopes
4. **Webhook Secrets**: Always use webhook secrets for validation
5. **Environment Variables**: Use `.env` files (not committed)

---

## API Rate Limits

GitHub API has rate limits:
- **Authenticated**: 5,000 requests/hour
- **Unauthenticated**: 60 requests/hour

SOW Sentinel handles rate limiting automatically with exponential backoff.

---

## Support

For issues or questions:
- GitHub Issues: [Repository Issues](https://github.com/your-org/sow-sentinel/issues)
- Documentation: [ARCHITECTURE.md](../ARCHITECTURE.md)
- API Reference: http://localhost:8000/docs

---

**Next Steps**: [Set up Outlook Calendar Integration](OUTLOOK_CALENDAR_SETUP.md)