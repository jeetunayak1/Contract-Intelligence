# IBM Cloud Setup Guide for SOW Sentinel

## Overview

SOW Sentinel requires **3 IBM Cloud services** to function in production mode:

1. **IBM watsonx.ai** - LLM for SOW document parsing and risk analysis
2. **IBM Cloudant** - NoSQL database for document storage
3. **IBM Watson Discovery** (Optional) - Enhanced document search and analysis

## Prerequisites

- IBM Cloud account (free tier available)
- IBM Cloud CLI installed
- Credit card for verification (free tier won't charge)

---

## Part 1: IBM watsonx.ai Setup

### What is watsonx.ai?
IBM's enterprise AI platform providing access to foundation models (LLMs) for text generation, analysis, and extraction. We use it to:
- Parse SOW documents (PDF/DOCX)
- Extract obligations, SLAs, and penalties
- Analyze vague clauses
- Generate risk assessments

### Step 1: Create watsonx.ai Project

1. **Login to IBM Cloud**
   ```
   https://cloud.ibm.com/
   ```

2. **Navigate to watsonx.ai**
   - Click "Catalog" in top menu
   - Search for "watsonx.ai"
   - Click "watsonx.ai" service
   - Click "Launch watsonx.ai"

3. **Create a New Project**
   - Click "Projects" in left sidebar
   - Click "New project"
   - Select "Create an empty project"
   - Enter project details:
     - Name: `SOW Sentinel`
     - Description: `AI-powered SOW compliance monitoring`
     - Storage: Select or create IBM Cloud Object Storage instance
   - Click "Create"

4. **Get Project ID**
   - Open your project
   - Click "Manage" tab
   - Copy the "Project ID" (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
   - Save this for later

### Step 2: Create API Key

1. **Navigate to API Keys**
   - Click your profile icon (top right)
   - Select "Profile and settings"
   - Click "API keys" in left sidebar
   - Click "Create an IBM Cloud API key"

2. **Create Key**
   - Name: `SOW Sentinel watsonx.ai Key`
   - Description: `API key for SOW Sentinel application`
   - Click "Create"
   - **IMPORTANT**: Copy and save the API key immediately (you won't see it again!)

3. **Save Credentials**
   ```
   WATSONX_API_KEY=<your-api-key>
   WATSONX_PROJECT_ID=<your-project-id>
   WATSONX_URL=https://us-south.ml.cloud.ibm.com
   ```

### Step 3: Select Foundation Model

We recommend using **IBM Granite** or **Meta Llama** models:

**Recommended Models:**
- `ibm/granite-13b-chat-v2` - Best for structured extraction
- `meta-llama/llama-2-70b-chat` - Best for complex analysis
- `ibm/granite-20b-multilingual` - Best for multi-language SOWs

**Model Selection in Code:**
```python
# In backend/app/agents/ingestion_agent.py
MODEL_ID = "ibm/granite-13b-chat-v2"  # Change this to your preferred model
```

### Step 4: Test watsonx.ai Connection

```bash
# Test API connection
curl -X POST "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29" \
  -H "Authorization: Bearer <your-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "ibm/granite-13b-chat-v2",
    "input": "Extract obligations from this SOW: The vendor shall deliver UAT sign-off by Friday.",
    "parameters": {
      "max_new_tokens": 500
    },
    "project_id": "<your-project-id>"
  }'
```

---

## Part 2: IBM Cloudant Setup

### What is Cloudant?
IBM's managed NoSQL database (based on Apache CouchDB). We use it to store:
- SOW documents
- Obligations and SLA terms
- Compliance events
- Alerts and notifications
- Scope creep detections

### Step 1: Create Cloudant Instance

1. **Navigate to Catalog**
   ```
   https://cloud.ibm.com/catalog
   ```

2. **Search for Cloudant**
   - Type "Cloudant" in search box
   - Click "Cloudant" service
   - Select plan:
     - **Lite Plan** (Free): 1GB storage, 20 lookups/sec
     - **Standard Plan**: Pay-as-you-go, better performance

3. **Configure Instance**
   - Service name: `sow-sentinel-db`
   - Region: `Dallas` (or closest to you)
   - Resource group: `Default`
   - Authentication: `IAM and legacy credentials`
   - Click "Create"

### Step 2: Create Database

1. **Open Cloudant Dashboard**
   - Go to "Resource list" → "Services and software"
   - Click your Cloudant instance
   - Click "Launch Dashboard"

2. **Create Database**
   - Click "Create Database" button
   - Database name: `sow-sentinel`
   - Partitioned: `No` (unpartitioned)
   - Click "Create"

### Step 3: Get Credentials

1. **Create Service Credentials**
   - In Cloudant instance page, click "Service credentials"
   - Click "New credential"
   - Name: `SOW Sentinel Credentials`
   - Role: `Manager` (full access)
   - Click "Add"

2. **View Credentials**
   - Click "View credentials" dropdown
   - Copy the JSON credentials
   - Extract these values:
     ```json
     {
       "apikey": "xxxxx",
       "host": "xxxxx.cloudantnosqldb.appdomain.cloud",
       "url": "https://xxxxx.cloudantnosqldb.appdomain.cloud"
     }
     ```

3. **Save Credentials**
   ```
   CLOUDANT_URL=https://xxxxx.cloudantnosqldb.appdomain.cloud
   CLOUDANT_API_KEY=xxxxx
   CLOUDANT_DB_NAME=sow-sentinel
   ```

### Step 4: Create Indexes (Optional but Recommended)

```bash
# Create index for SOW queries
curl -X POST "$CLOUDANT_URL/sow-sentinel/_index" \
  -H "Authorization: Bearer $CLOUDANT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "index": {
      "fields": ["type", "sow_number", "client_name"]
    },
    "name": "sow-lookup-index",
    "type": "json"
  }'

# Create index for obligations
curl -X POST "$CLOUDANT_URL/sow-sentinel/_index" \
  -H "Authorization: Bearer $CLOUDANT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "index": {
      "fields": ["type", "sow_id", "status", "risk_level"]
    },
    "name": "obligation-index",
    "type": "json"
  }'
```

---

## Part 3: IBM Watson Discovery Setup (Optional)

### What is Watson Discovery?
AI-powered search and text analytics service. Enhances SOW Sentinel with:
- Advanced document search
- Entity extraction
- Sentiment analysis
- Pattern detection

### Step 1: Create Discovery Instance

1. **Navigate to Catalog**
   - Search for "Watson Discovery"
   - Click "Watson Discovery"
   - Select "Plus" plan (free trial available)

2. **Configure Instance**
   - Service name: `sow-sentinel-discovery`
   - Region: `Dallas`
   - Click "Create"

### Step 2: Create Collection

1. **Launch Discovery**
   - Click "Launch Watson Discovery"
   - Click "Create a project"
   - Project name: `SOW Documents`
   - Project type: `Document Retrieval`

2. **Create Collection**
   - Click "Create collection"
   - Collection name: `SOW Archive`
   - Language: `English`
   - Click "Create"

### Step 3: Get Credentials

1. **Get API Key**
   - Go to Discovery instance page
   - Click "Service credentials"
   - Create new credential
   - Copy `apikey` and `url`

2. **Get Collection ID**
   - In Discovery dashboard
   - Click your collection
   - Copy Collection ID from URL or settings

3. **Save Credentials**
   ```
   DISCOVERY_API_KEY=xxxxx
   DISCOVERY_URL=https://api.us-south.discovery.watson.cloud.ibm.com
   DISCOVERY_COLLECTION_ID=xxxxx
   ```

---

## Part 4: Configure Backend

### Step 1: Update .env File

Create `backend/.env` file with all credentials:

```env
# ============================================
# IBM watsonx.ai Configuration
# ============================================
WATSONX_API_KEY=your_watsonx_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Model Selection
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2

# ============================================
# IBM Cloudant Configuration
# ============================================
CLOUDANT_URL=https://xxxxx.cloudantnosqldb.appdomain.cloud
CLOUDANT_API_KEY=your_cloudant_api_key_here
CLOUDANT_DB_NAME=sow-sentinel

# ============================================
# IBM Watson Discovery (Optional)
# ============================================
DISCOVERY_API_KEY=your_discovery_api_key_here
DISCOVERY_URL=https://api.us-south.discovery.watson.cloud.ibm.com
DISCOVERY_COLLECTION_ID=your_collection_id_here

# ============================================
# Application Configuration
# ============================================
USE_DEMO_MODE=false
SECRET_KEY=your_secret_key_here_generate_with_openssl

# ============================================
# External Integrations (Optional)
# ============================================
JIRA_API_KEY=your_jira_api_key
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@company.com

GITHUB_TOKEN=your_github_personal_access_token
GITHUB_ORG=your-github-org

GOOGLE_CALENDAR_API_KEY=your_google_calendar_api_key
GOOGLE_CALENDAR_ID=your_calendar_id

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# ============================================
# Redis Configuration (Optional)
# ============================================
REDIS_URL=redis://localhost:6379/0
```

### Step 2: Install Production Dependencies

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Test Connection

```bash
# Test watsonx.ai connection
python -c "
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
import os
from dotenv import load_dotenv

load_dotenv()

credentials = Credentials(
    url=os.getenv('WATSONX_URL'),
    api_key=os.getenv('WATSONX_API_KEY')
)

model = ModelInference(
    model_id='ibm/granite-13b-chat-v2',
    credentials=credentials,
    project_id=os.getenv('WATSONX_PROJECT_ID')
)

result = model.generate_text('Hello, watsonx!')
print('✅ watsonx.ai connection successful!')
print(f'Response: {result}')
"

# Test Cloudant connection
python -c "
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os
from dotenv import load_dotenv

load_dotenv()

authenticator = IAMAuthenticator(os.getenv('CLOUDANT_API_KEY'))
service = CloudantV1(authenticator=authenticator)
service.set_service_url(os.getenv('CLOUDANT_URL'))

response = service.get_all_dbs().get_result()
print('✅ Cloudant connection successful!')
print(f'Databases: {response}')
"
```

### Step 4: Switch to Production Mode

```bash
# Update .env
USE_DEMO_MODE=false

# Restart backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Part 5: Cost Estimation

### Free Tier Limits

**watsonx.ai (Free Trial)**
- Duration: 30 days
- Tokens: Limited (varies by model)
- After trial: Pay-as-you-go

**Cloudant (Lite Plan)**
- Storage: 1 GB
- Lookups: 20/sec
- Writes: 10/sec
- Free forever (with limits)

**Watson Discovery (Plus Trial)**
- Duration: 30 days
- Documents: 1,000
- Queries: 1,000/month
- After trial: $500/month

### Estimated Monthly Costs (Production)

**Scenario: 100 SOWs/month, 1000 compliance checks**

| Service | Usage | Cost |
|---------|-------|------|
| watsonx.ai | ~500K tokens | $10-20 |
| Cloudant Standard | 5GB storage, 100 req/sec | $25-50 |
| Watson Discovery | 100 documents, 500 queries | $500 (or skip) |
| **Total** | | **$35-70/month** (without Discovery) |

### Cost Optimization Tips

1. **Use Lite Plans for Demo**
   - Cloudant Lite: Free forever
   - watsonx.ai: 30-day trial sufficient for hackathon

2. **Batch Processing**
   - Process multiple SOWs together
   - Cache watsonx.ai responses

3. **Skip Watson Discovery**
   - Not required for core functionality
   - Use only if needed for advanced search

4. **Monitor Usage**
   - Set up billing alerts
   - Use IBM Cloud Cost Estimator

---

## Part 6: Verification Checklist

### ✅ watsonx.ai Setup
- [ ] Project created
- [ ] API key generated
- [ ] Project ID copied
- [ ] Model selected (granite-13b-chat-v2)
- [ ] Test connection successful

### ✅ Cloudant Setup
- [ ] Instance created
- [ ] Database created (sow-sentinel)
- [ ] Service credentials generated
- [ ] API key and URL copied
- [ ] Test connection successful

### ✅ Backend Configuration
- [ ] .env file created
- [ ] All credentials added
- [ ] USE_DEMO_MODE=false
- [ ] Production dependencies installed
- [ ] Backend starts without errors

### ✅ Integration Tests
- [ ] SOW upload works
- [ ] watsonx.ai parsing works
- [ ] Cloudant storage works
- [ ] Risk report generates
- [ ] Compliance monitoring runs

---

## Part 7: Troubleshooting

### Common Issues

**1. watsonx.ai Authentication Error**
```
Error: Invalid API key
```
**Solution:**
- Verify API key is correct
- Check Project ID matches
- Ensure API key has watsonx.ai access

**2. Cloudant Connection Timeout**
```
Error: Connection timeout
```
**Solution:**
- Check CLOUDANT_URL format (must include https://)
- Verify API key has Manager role
- Check network/firewall settings

**3. Model Not Found**
```
Error: Model 'xxx' not found
```
**Solution:**
- Use correct model ID: `ibm/granite-13b-chat-v2`
- Check model availability in your region
- Try alternative model: `meta-llama/llama-2-70b-chat`

**4. Rate Limit Exceeded**
```
Error: Rate limit exceeded
```
**Solution:**
- Implement exponential backoff
- Reduce request frequency
- Upgrade to paid tier

### Debug Commands

```bash
# Check environment variables
cd backend
source venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('WATSONX_API_KEY:', os.getenv('WATSONX_API_KEY')[:10] + '...')"

# Test watsonx.ai
python -c "from app.agents.ingestion_agent import IngestionAgent; agent = IngestionAgent(); print('Agent initialized successfully')"

# Test Cloudant
python -c "from app.core.cloudant_db import get_cloudant_client; client = get_cloudant_client(); print('Cloudant connected')"

# Check logs
tail -f logs/app.log
```

---

## Part 8: Quick Start Commands

### Setup Everything
```bash
# 1. Clone and setup
cd /Users/jeetendranayak/Hackathon
cd backend
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your IBM Cloud credentials

# 4. Test connections
python -c "from app.core.config import settings; print('Config loaded:', settings.USE_DEMO_MODE)"

# 5. Start backend (production mode)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. Start frontend (separate terminal)
cd ../frontend
npm run dev
```

### Switch Between Demo and Production
```bash
# Demo mode (no IBM Cloud needed)
echo "USE_DEMO_MODE=true" >> backend/.env
python -m uvicorn app.main_demo:app --reload --host 0.0.0.0 --port 8000

# Production mode (IBM Cloud required)
echo "USE_DEMO_MODE=false" >> backend/.env
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Part 9: Next Steps

After IBM Cloud setup is complete:

1. **Test SOW Upload**
   - Upload a sample SOW document
   - Verify watsonx.ai parsing
   - Check Cloudant storage

2. **Monitor Compliance**
   - Run monitoring agent
   - Verify compliance events
   - Check alert generation

3. **Test Integrations**
   - GitHub issue creation
   - Jira task creation
   - Slack notifications

4. **Prepare Demo**
   - Create compelling SOW examples
   - Test full workflow
   - Record demo video

5. **Document for Hackathon**
   - IBM Cloud usage
   - watsonx.ai prompts
   - Cost analysis
   - Performance metrics

---

## Support Resources

- **IBM Cloud Docs**: https://cloud.ibm.com/docs
- **watsonx.ai Docs**: https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-overview.html
- **Cloudant Docs**: https://cloud.ibm.com/docs/Cloudant
- **IBM Support**: https://www.ibm.com/support

---

## Summary

**Required IBM Cloud Services:**
1. ✅ **watsonx.ai** - LLM for SOW parsing ($10-20/month after trial)
2. ✅ **Cloudant** - NoSQL database (Free Lite plan available)
3. ⏳ **Watson Discovery** - Optional ($500/month, skip for hackathon)

**Total Setup Time:** 30-45 minutes
**Monthly Cost:** $35-70 (or $0 with free tiers for demo)
**Hackathon Ready:** Yes, free tier sufficient for demo!

Your SOW Sentinel will use IBM's AI to automatically parse SOW documents, detect compliance risks, and prevent revenue leakage - all powered by IBM Cloud! 🚀