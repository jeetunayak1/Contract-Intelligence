# Quick Start Guide

## 🚀 Run the Application in 3 Steps

### Step 1: Configure IBM Cloud Credentials

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit with your credentials
nano backend/.env  # or use any text editor
```

Update these values in `backend/.env`:
```bash
CLOUDANT_URL=https://your-account.cloudantnosqldb.appdomain.cloud
CLOUDANT_API_KEY=your-api-key-here
```

See [`docs/CLOUDANT_SETUP.md`](docs/CLOUDANT_SETUP.md) for how to get these credentials.

---

### Step 2: Run the Application

**On macOS/Linux:**
```bash
./start.sh
```

**On Windows:**
```bash
start.bat
```

The script will:
- ✅ Check prerequisites (Python, Node.js)
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Start backend API (port 8000)
- ✅ Start frontend UI (port 3000)

---

### Step 3: Access the Application

Open your browser:
- **Frontend Dashboard:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

---

## 🛑 Stop the Application

**On macOS/Linux:**
```bash
./stop.sh
```

**On Windows:**
```bash
stop.bat
```

---

## 📋 What the Scripts Do

### `start.sh` / `start.bat`
1. Checks if Python 3 and Node.js are installed
2. Creates `.env` file if missing
3. Sets up Python virtual environment
4. Installs Python dependencies
5. Installs Node.js dependencies
6. Starts backend API server
7. Starts frontend development server
8. Shows access URLs and log locations

### `stop.sh` / `stop.bat`
1. Stops backend API server
2. Stops frontend development server
3. Cleans up processes

---

## 📝 Logs

Logs are saved in the `logs/` directory:
- `logs/backend.log` - Backend API logs
- `logs/frontend.log` - Frontend development server logs

View logs in real-time:
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Both logs
tail -f logs/*.log
```

---

## 🔧 Manual Setup (Alternative)

If you prefer to run services manually:

### Backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## ⚠️ Troubleshooting

### Port Already in Use

**Backend (port 8000):**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

**Frontend (port 3000):**
```bash
# Find process using port 3000
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Python Virtual Environment Issues

```bash
# Remove and recreate
rm -rf backend/venv
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node Modules Issues

```bash
# Remove and reinstall
rm -rf frontend/node_modules
cd frontend
npm install
```

### Cloudant Connection Error

1. Check your `.env` file has correct credentials
2. Verify Cloudant instance is running in IBM Cloud
3. Test connection:
```bash
cd backend
source venv/bin/activate
python test_cloudant.py
```

---

## 📚 Next Steps

1. **Set up Cloudant:** Follow [`docs/CLOUDANT_SETUP.md`](docs/CLOUDANT_SETUP.md)
2. **Review Architecture:** See [`ARCHITECTURE.md`](ARCHITECTURE.md)
3. **Hackathon Guide:** Check [`HACKATHON_GUIDE.md`](HACKATHON_GUIDE.md)
4. **UI Preview:** View [`docs/UI_PREVIEW.md`](docs/UI_PREVIEW.md)

---

## 🎯 For Hackathon

### First Time Setup (5 minutes):
1. Provision Cloudant on IBM Cloud (2 min)
2. Copy credentials to `.env` (1 min)
3. Run `./start.sh` (2 min)
4. Access http://localhost:3000

### Daily Development:
```bash
# Start
./start.sh

# Develop...

# Stop
./stop.sh
```

---

## 💡 Tips

- **Keep scripts running:** Services run in background, you can close terminal
- **Check logs:** Use `tail -f logs/*.log` to monitor
- **Restart services:** Run `./stop.sh` then `./start.sh`
- **Update dependencies:** Delete `venv/` and `node_modules/`, then run `./start.sh`

---

**Ready to build!** 🚀