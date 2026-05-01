# Secret Detection Setup Guide

## Overview

This project uses **detect-secrets** and **pre-commit hooks** to prevent accidentally committing sensitive information like API keys, passwords, and tokens to the repository.

---

## Quick Setup

### One-Command Setup:

```bash
./setup-git-hooks.sh
```

This will:
- Install pre-commit and detect-secrets
- Set up git hooks
- Scan existing files for secrets
- Create baseline configuration

---

## Manual Setup

### Step 1: Install Tools

```bash
# Install pre-commit and detect-secrets
pip3 install pre-commit detect-secrets
```

### Step 2: Install Git Hooks

```bash
# Install pre-commit hooks
pre-commit install
```

### Step 3: Create Secrets Baseline

```bash
# Scan and create baseline
detect-secrets scan --baseline .secrets.baseline
```

---

## What Gets Detected

The system automatically detects:

### **API Keys & Tokens:**
- ✅ AWS Access Keys
- ✅ IBM Cloud API Keys
- ✅ GitHub Tokens
- ✅ Slack Tokens
- ✅ Stripe Keys
- ✅ SendGrid Keys
- ✅ JWT Tokens

### **Credentials:**
- ✅ Passwords in code
- ✅ Basic Auth credentials
- ✅ Database connection strings
- ✅ Private SSH keys

### **High Entropy Strings:**
- ✅ Base64 encoded secrets
- ✅ Hex encoded secrets
- ✅ Random strings that look like secrets

### **Cloud Services:**
- ✅ IBM Cloudant credentials
- ✅ Azure Storage Keys
- ✅ Google Cloud credentials

---

## How It Works

### **Pre-Commit Hook:**

When you run `git commit`, the hook automatically:

1. **Scans** all staged files for secrets
2. **Blocks** the commit if secrets are found
3. **Shows** which files contain secrets
4. **Prevents** accidental exposure

### **Example:**

```bash
$ git commit -m "Add configuration"

Detect secrets...................................................Failed
- hook id: detect-secrets
- exit code: 1

ERROR: Potential secrets detected!
File: backend/.env
Line 3: CLOUDANT_API_KEY=abc123...

Please remove secrets before committing.
```

---

## Configuration Files

### `.pre-commit-config.yaml`

Defines all pre-commit hooks:
- Secret detection
- Large file detection
- Private key detection
- Code formatting (Black for Python, Prettier for JS)
- YAML/JSON validation

### `.secrets.baseline`

Baseline file that tracks:
- Known false positives
- Approved secrets (like example values)
- Plugin configuration

---

## Common Workflows

### **1. Committing Code (Normal Flow)**

```bash
# Stage your changes
git add .

# Commit (hooks run automatically)
git commit -m "Your message"

# If secrets detected, fix them and try again
```

### **2. If Secrets Are Detected**

```bash
# Option 1: Remove the secret
# Edit the file and remove/replace the secret

# Option 2: Add to .gitignore
echo "file-with-secret.txt" >> .gitignore

# Option 3: Mark as false positive (if it's not a real secret)
detect-secrets scan --baseline .secrets.baseline --update
```

### **3. Bypass Hooks (Emergency Only)**

```bash
# NOT RECOMMENDED - Only for emergencies
git commit --no-verify -m "Emergency fix"
```

### **4. Run Checks Manually**

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run only secret detection
detect-secrets scan
```

### **5. Update Baseline**

```bash
# After adding legitimate test data or examples
detect-secrets scan --baseline .secrets.baseline --update
```

---

## Best Practices

### **1. Use Environment Variables**

❌ **Bad:**
```python
api_key = "abc123xyz789"
```

✅ **Good:**
```python
import os
api_key = os.getenv("CLOUDANT_API_KEY")
```

### **2. Use .env Files (Never Commit Them)**

❌ **Bad:**
```bash
git add .env
```

✅ **Good:**
```bash
# .env is in .gitignore
# Only commit .env.example with placeholder values
git add .env.example
```

### **3. Use Example Files**

Create `.env.example` with placeholders:
```bash
CLOUDANT_URL=https://your-account.cloudantnosqldb.appdomain.cloud
CLOUDANT_API_KEY=your-api-key-here
CLOUDANT_DB_NAME=contract-intelligence
```

### **4. Document Required Secrets**

In README or documentation:
```markdown
## Required Environment Variables

- `CLOUDANT_URL` - Your Cloudant instance URL
- `CLOUDANT_API_KEY` - API key from IBM Cloud
- `WATSONX_API_KEY` - watsonx.ai API key
```

---

## Handling False Positives

### **Example: UUID in Code**

If detect-secrets flags a UUID as a secret:

```bash
# Add to baseline as false positive
detect-secrets scan --baseline .secrets.baseline --update

# Or add inline comment
api_key = "00000000-0000-0000-0000-000000000000"  # pragma: allowlist secret
```

### **Example: Test Data**

For test files with fake credentials:

```python
# test_auth.py
def test_login():
    # pragma: allowlist secret
    test_password = "test123"
```

---

## Troubleshooting

### **Issue: Hook Not Running**

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### **Issue: Too Many False Positives**

```bash
# Update baseline to include current state
detect-secrets scan --baseline .secrets.baseline --update

# Commit the updated baseline
git add .secrets.baseline
git commit -m "Update secrets baseline"
```

### **Issue: Hook Fails on Large Files**

```bash
# Increase size limit in .pre-commit-config.yaml
# Change --maxkb=1000 to higher value
```

### **Issue: Need to Commit Urgently**

```bash
# Bypass hooks (use sparingly!)
git commit --no-verify -m "Urgent fix"

# Then fix secrets and commit properly
```

---

## For Hackathon Teams

### **Initial Setup (Team Lead):**

```bash
# 1. Run setup script
./setup-git-hooks.sh

# 2. Commit hook configuration
git add .pre-commit-config.yaml .secrets.baseline
git commit -m "Add secret detection"
git push
```

### **Team Members:**

```bash
# 1. Pull latest code
git pull

# 2. Install hooks
./setup-git-hooks.sh

# 3. Start coding safely!
```

### **Before Submission:**

```bash
# Run full scan
pre-commit run --all-files

# Check for any secrets
detect-secrets scan

# Verify .env is not committed
git ls-files | grep "\.env$"
# Should return nothing
```

---

## Additional Security Tools

### **GitHub Secret Scanning**

GitHub automatically scans for secrets. Enable it:
1. Go to repository Settings
2. Security & analysis
3. Enable "Secret scanning"

### **GitGuardian**

For additional protection:
```bash
# Install GitGuardian
pip install ggshield

# Scan repository
ggshield secret scan repo .
```

---

## What's Protected

### **Files Always Scanned:**
- ✅ Python files (`.py`)
- ✅ JavaScript/TypeScript (`.js`, `.ts`, `.tsx`)
- ✅ Configuration files (`.yaml`, `.json`, `.toml`)
- ✅ Environment files (`.env`, `.env.local`)
- ✅ Shell scripts (`.sh`, `.bash`)

### **Files Excluded:**
- ❌ `node_modules/`
- ❌ `venv/`, `env/`
- ❌ `.git/`
- ❌ `package-lock.json`
- ❌ Binary files

---

## Monitoring & Auditing

### **Check Commit History:**

```bash
# Scan git history for secrets
detect-secrets-hook --baseline .secrets.baseline $(git ls-files)
```

### **Audit Logs:**

```bash
# View pre-commit hook runs
cat .git/hooks/pre-commit

# View recent commits
git log --oneline -10
```

---

## Emergency: Secret Was Committed

If you accidentally committed a secret:

### **1. Remove from Latest Commit:**

```bash
# Edit the file to remove secret
nano file-with-secret.py

# Amend the commit
git add file-with-secret.py
git commit --amend --no-edit

# Force push (if already pushed)
git push --force
```

### **2. Remove from History:**

```bash
# Use BFG Repo-Cleaner
brew install bfg  # or download from bfg.io

# Remove secret from all history
bfg --replace-text secrets.txt

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push --force
```

### **3. Rotate the Secret:**

1. **Immediately** revoke the exposed secret in IBM Cloud
2. Generate a new API key
3. Update your `.env` file
4. Never reuse the exposed secret

---

## Quick Reference

### **Setup:**
```bash
./setup-git-hooks.sh
```

### **Manual Check:**
```bash
pre-commit run --all-files
```

### **Update Baseline:**
```bash
detect-secrets scan --baseline .secrets.baseline --update
```

### **Bypass (Emergency):**
```bash
git commit --no-verify
```

### **Uninstall:**
```bash
pre-commit uninstall
```

---

## Resources

- **detect-secrets:** https://github.com/Yelp/detect-secrets
- **pre-commit:** https://pre-commit.com/
- **GitHub Secret Scanning:** https://docs.github.com/en/code-security/secret-scanning

---

**Your secrets are now protected!** 🔒