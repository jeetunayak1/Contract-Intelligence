# IBM Cloud Quick Start - SOW Sentinel

## 🎯 What You Need from IBM Cloud

SOW Sentinel uses **2 IBM Cloud services** (1 optional):

| Service | Purpose | Cost | Required? |
|---------|---------|------|-----------|
| **watsonx.ai** | LLM for SOW parsing | Free 30-day trial | ✅ YES |
| **Cloudant** | NoSQL database | Free Lite plan | ✅ YES |
| Watson Discovery | Advanced search | $500/month | ❌ NO (skip for hackathon) |

---

## ⚡ 15-Minute Setup

### Step 1: watsonx.ai (5 minutes)

1. **Go to**: https://cloud.ibm.com/
2. **Search**: "watsonx.ai" → Click "Launch watsonx.ai"
3. **Create Project**:
   - Name: `SOW Sentinel`
   - Click "Create"
4. **Get Credentials**:
   - Copy **Project ID** from Manage tab
   - Create **API Key**: Profile → API keys → Create
5. **Save**:
   ```env
   WATSONX_API_KEY=your_key_here
   WATSONX_PROJECT_ID=your_project_id_here
   WATSONX_URL=https://us-south.ml.cloud.ibm.com
   ```

### Step 2: Cloudant (5 minutes)

1. **Go to**: https://cloud.ibm.com/catalog
2. **Search**: "Cloudant" → Select **Lite Plan** (FREE)
3. **Create**:
   - Name: `sow-sentinel-db`
   - Region: Dallas
   - Click "Create"
4. **Create Database**:
   - Click "Launch Dashboard"
   - Create database: `sow-sentinel`
5. **Get Credentials**:
   - Service credentials → New credential → Manager role
   - Copy `apikey` and `url`
6. **Save**:
   ```env
   CLOUDANT_URL=https://xxxxx.cloudantnosqldb.appdomain.cloud
   CLOUDANT_API_KEY=your_key_here
   CLOUDANT_DB_NAME=sow-sentinel
   ```

### Step 3: Configure Backend (5 minutes)

```bash
# 1. Create .env file
cd backend
cp .env.example .env

# 2. Edit .env with your credentials
nano .env  # or use VS Code

# 3. Add these lines:
WATSONX_API_KEY=your_watsonx_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

CLOUDANT_URL=your_cloudant_url
CLOUDANT_API_KEY=your_cloudant_key
CLOUDANT_DB_NAME=sow-sentinel

USE_DEMO_MODE=false

# 4. Install production dependencies
pip install -r requirements.txt

# 5. Test connection
python -c "from app.core.config import settings; print('✅ Config loaded')"

# 6. Start production server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔑 Your .env File Template

```env
# ============================================
# IBM watsonx.ai - LLM for SOW Parsing
# ============================================
WATSONX_API_KEY=paste_your_api_key_here
WATSONX_PROJECT_ID=paste_your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2

# ============================================
# IBM Cloudant - NoSQL Database
# ============================================
CLOUDANT_URL=https://xxxxx.cloudantnosqldb.appdomain.cloud
CLOUDANT_API_KEY=paste_your_cloudant_key_here
CLOUDANT_DB_NAME=sow-sentinel

# ============================================
# Application Mode
# ============================================
USE_DEMO_MODE=false
SECRET_KEY=generate_with_openssl_rand_hex_32

# ============================================
# Optional Integrations (Add Later)
# ============================================
# JIRA_API_KEY=
# GITHUB_TOKEN=
# SLACK_WEBHOOK_URL=
```

---

## 🧪 Test Your Setup

### Test 1: watsonx.ai Connection
```bash
cd backend
source venv/bin/activate

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

result = model.generate_text('Extract obligations from: Deliver UAT by Friday.')
print('✅ watsonx.ai working!')
print(f'Response: {result}')
"
```

### Test 2: Cloudant Connection
```bash
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
print('✅ Cloudant working!')
print(f'Databases: {response}')
"
```

### Test 3: Full Integration
```bash
# Start backend in production mode
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, test API
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "mode": "production", "services": {"watsonx": "connected", "cloudant": "connected"}}
```

---

## 💰 Cost Breakdown

### Free Tier (Perfect for Hackathon!)

**watsonx.ai Free Trial**
- ✅ 30 days free
- ✅ Sufficient for hackathon demo
- ✅ Process 100+ SOWs
- ⚠️ After trial: ~$10-20/month

**Cloudant Lite Plan**
- ✅ FREE FOREVER
- ✅ 1 GB storage
- ✅ 20 lookups/sec
- ✅ Perfect for demo and small production

**Total for Hackathon: $0** 🎉

### Production Costs (After Hackathon)

| Service | Monthly Usage | Cost |
|---------|---------------|------|
| watsonx.ai | 500K tokens | $10-20 |
| Cloudant Standard | 5GB, 100 req/sec | $25-50 |
| **Total** | | **$35-70/month** |

---

## 🚨 Common Issues & Fixes

### Issue 1: "Invalid API Key"
```
Error: Authentication failed
```
**Fix:**
- Double-check API key (no extra spaces)
- Verify Project ID is correct
- Ensure API key has watsonx.ai access

### Issue 2: "Database not found"
```
Error: Database 'sow-sentinel' does not exist
```
**Fix:**
```bash
# Create database manually
curl -X PUT "$CLOUDANT_URL/sow-sentinel" \
  -H "Authorization: Bearer $CLOUDANT_API_KEY"
```

### Issue 3: "Connection timeout"
```
Error: Request timeout
```
**Fix:**
- Check internet connection
- Verify CLOUDANT_URL includes `https://`
- Check firewall settings

### Issue 4: "Rate limit exceeded"
```
Error: Too many requests
```
**Fix:**
- Wait 60 seconds
- Reduce request frequency
- Upgrade to paid tier

---

## 🎬 Demo Mode vs Production Mode

### Demo Mode (Current)
```env
USE_DEMO_MODE=true
```
- ✅ No IBM Cloud needed
- ✅ Works offline
- ✅ Instant responses
- ❌ Fake data only
- ❌ No real AI parsing

### Production Mode (After Setup)
```env
USE_DEMO_MODE=false
```
- ✅ Real AI parsing with watsonx.ai
- ✅ Persistent storage in Cloudant
- ✅ Real-time compliance monitoring
- ✅ Production-ready
- ⚠️ Requires IBM Cloud credentials

---

## 📊 What watsonx.ai Does for You

### SOW Document Parsing
```
Input: PDF/DOCX SOW document
       ↓
watsonx.ai (Granite model)
       ↓
Output: {
  "obligations": [
    {
      "description": "Deliver UAT sign-off",
      "deadline": "2024-12-15",
      "penalty": "$1,000/day"
    }
  ],
  "sla_terms": [...],
  "vague_clauses": [...],
  "risk_score": 85
}
```

### Risk Analysis
```
Input: Obligation + Current Progress
       ↓
watsonx.ai Analysis
       ↓
Output: {
  "risk_level": "critical",
  "days_remaining": 2,
  "penalty_exposure": "$9,000",
  "recommended_actions": [...]
}
```

---

## 📚 Recommended Models

### For SOW Parsing (Best)
```env
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2
```
- ✅ Best for structured extraction
- ✅ Fast response time
- ✅ Cost-effective

### For Complex Analysis
```env
WATSONX_MODEL_ID=meta-llama/llama-2-70b-chat
```
- ✅ Better reasoning
- ✅ More accurate risk assessment
- ⚠️ Slower, more expensive

### For Multi-Language SOWs
```env
WATSONX_MODEL_ID=ibm/granite-20b-multilingual
```
- ✅ Supports 100+ languages
- ✅ Good for international clients

---

## 🎯 Next Steps After Setup

1. **Test SOW Upload**
   ```bash
   # Upload a sample SOW
   curl -X POST http://localhost:8000/api/v1/sow/upload \
     -F "file=@sample_sow.pdf"
   ```

2. **Verify Parsing**
   ```bash
   # Check parsed obligations
   curl http://localhost:8000/api/v1/sow/SOW-2024-001
   ```

3. **Test Risk Report**
   ```bash
   # Get risk analysis
   curl http://localhost:8000/api/v1/sow/SOW-2024-001/risk-report
   ```

4. **Monitor Compliance**
   ```bash
   # Run monitoring agent
   curl -X POST http://localhost:8000/api/v1/sow/SOW-2024-001/check-compliance
   ```

---

## 🆘 Need Help?

### IBM Cloud Support
- **Docs**: https://cloud.ibm.com/docs
- **watsonx.ai**: https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-overview.html
- **Cloudant**: https://cloud.ibm.com/docs/Cloudant
- **Support**: https://www.ibm.com/support

### Project Support
- **Full Guide**: `docs/IBM_CLOUD_SETUP_COMPLETE.md`
- **Architecture**: `ARCHITECTURE.md`
- **README**: `README.md`

---

## ✅ Setup Checklist

- [ ] IBM Cloud account created
- [ ] watsonx.ai project created
- [ ] watsonx.ai API key generated
- [ ] Cloudant instance created (Lite plan)
- [ ] Cloudant database created (`sow-sentinel`)
- [ ] Cloudant credentials obtained
- [ ] `backend/.env` file created
- [ ] All credentials added to `.env`
- [ ] Production dependencies installed
- [ ] watsonx.ai connection tested
- [ ] Cloudant connection tested
- [ ] Backend starts in production mode
- [ ] API health check passes
- [ ] SOW upload works
- [ ] Risk report generates

---

## 🚀 You're Ready!

Once all checkboxes are complete, your SOW Sentinel is powered by IBM Cloud AI! 

**Demo Flow:**
1. Upload SOW → watsonx.ai parses it
2. View Risk Report → See critical alerts
3. Monitor Compliance → Auto-detect risks
4. Take Action → Automated responses

**Total Setup Time:** 15 minutes  
**Total Cost:** $0 (free tier)  
**Hackathon Ready:** ✅ YES!