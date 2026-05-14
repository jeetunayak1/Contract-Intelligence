# Quick Start - Contract Intelligence Agent (No Firestore)

## Running Without Google Cloud Credentials

The Contract Intelligence Agent can run in **demo mode** using in-memory storage when Firestore credentials are not available.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create `backend/.env` file with minimal configuration:

```env
# Google AI API Key (required for LLM)
GOOGLE_API_KEY=your-gemini-api-key

# Optional - leave empty for in-memory storage
GCP_PROJECT_ID=
FIRESTORE_DB_NAME=(default)

# Model Configuration
GEMINI_MODEL_ID=gemini-1.5-pro

# File Upload
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=.pdf,.docx,.doc,.txt

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Important**: You only need `GOOGLE_API_KEY` for the LLM. Leave `GCP_PROJECT_ID` empty to use in-memory storage.

### 3. Start Server

```bash
cd backend
python -m uvicorn app.main_demo:app --reload --port 8000
```

Or use the original main.py (it will automatically fall back to in-memory storage):

```bash
python -m uvicorn app.main:app --reload --port 8000
```

## How It Works

### In-Memory Storage Mode

When Firestore credentials are not configured:
- ✅ All contract data is stored in memory
- ✅ Data persists during server runtime
- ✅ Data is lost when server restarts
- ✅ Perfect for testing and demos
- ✅ No Google Cloud setup required

### What You Get

- ✅ Full contract upload and extraction
- ✅ LLM-powered SLA extraction
- ✅ All API endpoints work
- ✅ List, get, delete operations
- ✅ Search functionality

### What's Different

- ⚠️ Data doesn't persist across restarts
- ⚠️ No distributed storage
- ⚠️ Single server instance only

## Testing

### 1. Upload Sample Contract

```bash
curl -X POST http://localhost:8000/api/contracts/upload \
  -F "file=@backend/tests/sample_contract.txt"
```

### 2. List Contracts

```bash
curl http://localhost:8000/api/contracts
```

### 3. Get Specific Contract

```bash
curl http://localhost:8000/api/contracts/{contract_id}
```

## Expected Logs

When starting without Firestore credentials, you'll see:

```
INFO:     Started server process
WARNING:  GCP credentials not configured. Firestore will use in-memory storage.
INFO:     Application startup complete
```

This is **normal** and expected. The system will work perfectly with in-memory storage.

## Get Google AI API Key

### Option 1: Google AI Studio (Free)

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Add to `.env`: `GOOGLE_API_KEY=your-key-here`

### Option 2: Google Cloud (Production)

1. Go to Google Cloud Console
2. Enable Vertex AI API
3. Create service account
4. Download credentials JSON
5. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
   ```

## Switching to Firestore Later

When ready to use Firestore:

1. Set up Google Cloud Project
2. Enable Firestore API
3. Update `.env`:
   ```env
   GCP_PROJECT_ID=your-project-id
   GOOGLE_API_KEY=your-api-key
   ```
4. Restart server

The system will automatically detect Firestore credentials and switch from in-memory to persistent storage.

## Troubleshooting

### Error: "Failed to initialize Firestore client"

**Solution**: This is expected without credentials. The system will automatically use in-memory storage. Look for:
```
WARNING: GCP credentials not configured. Firestore will use in-memory storage.
```

### Error: "GOOGLE_API_KEY not set"

**Solution**: You need a Gemini API key for LLM extraction:
1. Get key from https://makersuite.google.com/app/apikey
2. Add to `.env`: `GOOGLE_API_KEY=your-key`
3. Restart server

### Error: "Import google.cloud.firestore failed"

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

## Demo Mode Features

### What Works Without Firestore

✅ Contract upload (PDF, DOCX, TXT)  
✅ Document parsing  
✅ LLM extraction with LangGraph  
✅ SLA normalization  
✅ JSON validation  
✅ All API endpoints  
✅ Frontend integration  

### What Requires Firestore

❌ Persistent storage across restarts  
❌ Multi-server deployment  
❌ Production-scale storage  

## Production Deployment

For production, use Firestore:

1. **Better Performance**: Distributed database
2. **Persistence**: Data survives restarts
3. **Scalability**: Handle multiple servers
4. **Backup**: Automatic backups
5. **Security**: Fine-grained access control

## Summary

**For Testing/Demo**: Use in-memory storage (no Firestore setup needed)  
**For Production**: Use Firestore (requires Google Cloud setup)

Both modes provide full functionality for contract intelligence extraction!

---

Made with Bob