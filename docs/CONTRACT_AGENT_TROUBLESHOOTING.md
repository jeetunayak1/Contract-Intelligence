# Contract Intelligence Agent - Troubleshooting Guide

## Issue: Empty Extraction Results

### Problem
When uploading contracts, the API returns empty arrays for all SLA fields:
```json
{
  "incident_slas": [],
  "availability_slas": [],
  "service_credits": []
}
```

### Root Causes

#### 1. Missing google-genai Package
**Symptom**: Agent falls back to heuristic extraction
**Solution**:
```bash
cd backend
pip install -r requirements-minimal.txt
```

#### 2. Missing or Invalid GOOGLE_API_KEY
**Symptom**: LLM extraction fails silently
**Check**:
```bash
# Verify .env file has valid API key
cat backend/.env | grep GOOGLE_API_KEY
```

**Solution**:
1. Get API key from https://aistudio.google.com/app/apikey
2. Add to `backend/.env`:
```
GOOGLE_API_KEY=your-actual-api-key-here
```

#### 3. Wrong Model ID
**Symptom**: API calls fail with model not found
**Check**:
```bash
cat backend/.env | grep GEMINI_MODEL_ID
```

**Valid Models**:
- `gemini-1.5-pro` (recommended)
- `gemini-1.5-flash`
- `gemini-2.0-flash-exp`

**Fix in .env**:
```
GEMINI_MODEL_ID=gemini-1.5-pro
```

#### 4. Firestore Not Configured
**Symptom**: Warning about Firestore, but extraction still works
**Solution**: System automatically falls back to in-memory storage

### Verification Steps

#### Step 1: Check Environment Variables
```bash
cd backend
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('GOOGLE_API_KEY:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'MISSING')
print('GEMINI_MODEL_ID:', os.getenv('GEMINI_MODEL_ID', 'gemini-1.5-pro'))
"
```

#### Step 2: Test Gemini API
```bash
cd backend
python3 -c "
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
response = client.models.generate_content(
    model='gemini-1.5-pro',
    contents='Say hello'
)
print('API Test:', 'SUCCESS' if response.text else 'FAILED')
print('Response:', response.text[:100])
"
```

#### Step 3: Check Backend Logs
When running the server, look for these log messages:

**Good**:
```
INFO: Gemini client initialized with model: gemini-1.5-pro
INFO: Successfully extracted contract data using Gemini
```

**Bad**:
```
WARNING: GOOGLE_API_KEY not set. Agent will use fallback extraction.
ERROR: Gemini extraction failed: ...
```

### Quick Fix Commands

```bash
# 1. Install dependencies
cd backend
pip3 install -r requirements-minimal.txt

# 2. Verify .env file exists
ls -la .env

# 3. Check API key is set
grep GOOGLE_API_KEY .env

# 4. Restart backend server
# Stop current server (Ctrl+C)
# Start again:
uvicorn app.main_demo:app --reload --port 8000
```

### Testing the Fix

Upload a test contract and check the response includes `llm_metadata`:

```json
{
  "success": true,
  "llm_metadata": {
    "model": "gemini-1.5-pro",
    "method": "gemini",
    "success": true,
    "response_length": 1234
  }
}
```

**If `method` is "failed" or "none"**: LLM is not working
**If `method` is "gemini" and `success` is true**: System is working correctly

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `No module named 'google'` | Package not installed | `pip install google-genai` |
| `GOOGLE_API_KEY not set` | Missing env variable | Add to `.env` file |
| `Empty response from Gemini` | Invalid API key | Check API key validity |
| `Model not found` | Wrong model ID | Use `gemini-1.5-pro` |
| `Rate limit exceeded` | Too many requests | Wait or upgrade API tier |

### Advanced Debugging

Enable detailed logging:

```python
# In backend/app/main_demo.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check extraction in real-time:
```bash
# Watch backend logs
tail -f backend/logs/app.log
```

### Still Not Working?

1. **Check Python version**: Should be 3.9+
   ```bash
   python3 --version
   ```

2. **Verify all packages installed**:
   ```bash
   pip3 list | grep -E "google-genai|langchain|pydantic"
   ```

3. **Test with minimal example**:
   ```bash
   cd backend
   python3 test_contract_extraction.py
   ```

4. **Check API quota**: Visit https://aistudio.google.com/app/apikey

### Expected Behavior

When working correctly:
1. Upload contract → API processes in 5-15 seconds
2. Response includes populated arrays for SLAs
3. `llm_metadata.success` is `true`
4. Backend logs show "Successfully extracted contract data using Gemini"

### Contact

If issues persist after following this guide, check:
- Backend logs for detailed error messages
- Network connectivity to Google APIs
- API key permissions and quotas