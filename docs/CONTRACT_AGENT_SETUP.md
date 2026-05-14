# Contract Intelligence Agent - Setup Guide

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Google Cloud Project with Firestore enabled
- Google AI API Key (Gemini)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `backend/.env`:

```env
# Google Cloud / Gemini
GCP_PROJECT_ID=your-project-id
GOOGLE_API_KEY=your-gemini-api-key
GEMINI_MODEL_ID=gemini-1.5-pro

# Firestore
FIRESTORE_DB_NAME=(default)

# File Upload
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=.pdf,.docx,.doc,.txt

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Provider Selection
DB_PROVIDER=gcp
LLM_PROVIDER=gcp
```

### 3. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Server will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## Testing the System

### Test 1: Upload Sample Contract

```bash
# Using cURL
curl -X POST http://localhost:8000/api/contracts/upload \
  -F "file=@backend/tests/sample_contract.txt"
```

Expected response:
```json
{
  "success": true,
  "contract_id": "contract_...",
  "filename": "sample_contract.txt",
  "data": {
    "contract_metadata": {...},
    "incident_slas": [...],
    "availability_slas": [...]
  }
}
```

### Test 2: List All Contracts

```bash
curl http://localhost:8000/api/contracts
```

### Test 3: Get Specific Contract

```bash
curl http://localhost:8000/api/contracts/{contract_id}
```

### Test 4: Health Check

```bash
curl http://localhost:8000/api/contracts/health/status
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Contract Intelligence",
  "firestore": "connected",
  "agent": "initialized"
}
```

## Frontend Testing

1. Open http://localhost:5173
2. Navigate to Contract Upload page
3. Select `backend/tests/sample_contract.txt`
4. Click "Upload & Extract"
5. View extracted SLAs and contract data

## Verification Checklist

- [ ] Backend server starts without errors
- [ ] API documentation accessible at /docs
- [ ] Health check returns "healthy"
- [ ] Sample contract uploads successfully
- [ ] Extracted data contains incident SLAs
- [ ] Extracted data contains availability SLAs
- [ ] Extracted data contains service credits
- [ ] Extracted data contains liability exclusions
- [ ] Data stored in Firestore
- [ ] Frontend displays extracted data correctly

## Common Issues

### Issue: Firestore Connection Failed

**Solution:**
1. Verify GCP_PROJECT_ID is correct
2. Ensure Firestore API is enabled in Google Cloud Console
3. Check Google Cloud credentials are configured
4. For local development, set GOOGLE_APPLICATION_CREDENTIALS environment variable

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### Issue: Gemini API Error

**Solution:**
1. Verify GOOGLE_API_KEY is valid
2. Check API quota limits
3. Ensure Gemini API is enabled in Google Cloud Console
4. Try using a different model (e.g., gemini-1.5-flash)

### Issue: PDF Parsing Fails

**Solution:**
1. Ensure PDF contains selectable text (not scanned images)
2. Try converting to DOCX or TXT format
3. Check file is not corrupted
4. Verify file size is under 10MB

### Issue: Import Errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Verify installations
python -c "import langchain; print('LangChain OK')"
python -c "import langgraph; print('LangGraph OK')"
python -c "from google.cloud import firestore; print('Firestore OK')"
```

## Architecture Verification

### Check File Structure

```bash
backend/app/
├── agents/
│   └── contract_agent.py          ✓ LangGraph agent
├── api/
│   └── contracts.py                ✓ FastAPI endpoints
├── models/
│   └── contract_models.py          ✓ Pydantic models
├── prompts/
│   └── contract_extraction_prompt.py  ✓ Extraction prompts
├── services/
│   └── firestore_service.py        ✓ Database layer
└── utils/
    └── document_parser.py          ✓ Document parsing
```

### Verify Dependencies

```bash
pip list | grep -E "langchain|langgraph|google|fastapi|pydantic"
```

Expected output:
```
fastapi                 0.109.0
google-cloud-firestore  2.14.0
google-genai            0.3.0
langchain               0.1.0
langchain-community     0.0.10
langchain-core          0.1.10
langchain-google-genai  0.0.6
langgraph               0.0.20
pydantic                2.5.3
pydantic-settings       2.1.0
```

## Performance Testing

### Test Contract Processing Time

```python
import time
import requests

start = time.time()

with open('backend/tests/sample_contract.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/contracts/upload',
        files={'file': f}
    )

end = time.time()
print(f"Processing time: {end - start:.2f} seconds")
```

Expected: < 60 seconds for typical contract

### Test Concurrent Uploads

```python
import concurrent.futures
import requests

def upload_contract(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/api/contracts/upload',
            files={'file': f}
        )
    return response.status_code

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(upload_contract, 'backend/tests/sample_contract.txt')
        for _ in range(5)
    ]
    results = [f.result() for f in futures]
    print(f"Success rate: {results.count(201)}/{len(results)}")
```

## Production Deployment

### Environment Variables for Production

```env
DEBUG=False
LOG_LEVEL=INFO

# Use production Firestore
GCP_PROJECT_ID=your-production-project
FIRESTORE_DB_NAME=production

# Increase limits
MAX_UPLOAD_SIZE=20971520  # 20MB

# Security
SECRET_KEY=your-strong-random-secret-key
CORS_ORIGINS=https://your-production-domain.com

# Monitoring
SENTRY_DSN=your-sentry-dsn  # Optional
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t contract-intelligence .
docker run -p 8000:8000 --env-file .env contract-intelligence
```

### Health Monitoring

Set up monitoring for:
- `/health` endpoint
- `/api/contracts/health/status` endpoint
- Firestore connection status
- LLM API availability

### Logging

Logs are written to:
- Console (stdout/stderr)
- Application logs include:
  - Contract upload events
  - Extraction success/failures
  - Database operations
  - API requests

## Next Steps

1. **Test with Real Contracts**: Upload actual SOW contracts
2. **Validate Extraction Quality**: Review extracted SLAs for accuracy
3. **Integrate with Compliance Agent**: Use extracted data for compliance monitoring
4. **Set Up Monitoring**: Configure alerts for failures
5. **Performance Tuning**: Optimize for your contract sizes

## Support

For issues or questions:
1. Check logs: `backend/logs/`
2. Review API documentation: http://localhost:8000/docs
3. Test with sample contract first
4. Verify all environment variables are set

---

Made with Bob