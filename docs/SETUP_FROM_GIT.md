# Setup Guide - Run SOW Sentinel After Pulling from Git

This guide explains how to take a fresh checkout of the repository and run the project locally.

---

## 1. What You Need

Install these first:

- **Git**
- **Python 3.11+**
- **Node.js 18+**
- **npm**
- Optional cloud/integration credentials for:
  - IBM Cloud / Cloudant
  - watsonx.ai
  - GitHub
  - Slack
  - Microsoft / Outlook

---

## 2. Clone the Repository

```bash
git clone <your-repository-url>
cd Hackathon
```

If your target directory is named differently, use that directory instead of `Hackathon`.

---

## 3. Project Structure

Important folders:

```text
backend/   FastAPI API, agents, Cloudant access, models
frontend/  React + TypeScript UI
docs/      Setup and project documentation
.ai/       AI project context and codebase summaries
```

---

## 4. Backend Setup

From the project root:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If you are on Windows PowerShell:

```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you are on Windows Command Prompt:

```bat
cd backend
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Then edit `backend/.env`.

### Minimum Recommended Variables
Configure the values that are relevant for your environment, especially:
- Cloudant connection details
- watsonx configuration
- GitHub credentials
- Slack credentials
- Microsoft / Outlook credentials

If you are only validating the local demo flow, some integrations can remain unconfigured, but Cloudant-backed behavior is important for persisted SOW workflows.

---

## 6. Start the Backend

From `backend/`:

```bash
python -m uvicorn app.main_demo:app --reload --host 0.0.0.0 --port 8000
```

You should then have:
- API base: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### Notes
- The repo currently uses [`app.main_demo`](backend/app/main_demo.py) as the most practical local dev entrypoint.
- If you want the non-demo entrypoint, inspect [`backend/app/main.py`](backend/app/main.py) first.

---

## 7. Frontend Setup

Open a new terminal from the project root:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Vite will print the local URL in the terminal. Commonly it will be:
- `http://localhost:5173`

In some local runs, you may also see:
- `http://127.0.0.1:4173`
- another Vite-assigned port

---

## 8. Open the App

Main URLs:
- Frontend: Vite URL shown in terminal
- Backend API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

### Best Page to Start With
Open the SOW workflow page:
- `/sows`

Example:
- `http://localhost:5173/sows`

---

## 9. Recommended Local Demo Flow

Once both services are running:

1. Open the frontend
2. Navigate to **SOW Management**
3. Upload a sample SOW file
4. Review generated alerts and action items
5. Add review notes
6. Accept, reject, or clear the review
7. Execute approved actions
8. Inspect the timeline and persisted state

This is the strongest way to validate the current product workflow.

---

## 10. If You Want to Run the Existing Helper Scripts

The repository also includes helper scripts at the root:
- `start.sh`
- `stop.sh`
- `start.bat`
- `stop.bat`
- `start-local.sh`
- `docker-compose.yml`
- `podman-compose.yml`

Before relying on them, review the script contents and ensure your local environment matches the expected setup.

---

## 11. Common Issues

### A. Backend starts but list/upload fails
Possible causes:
- Cloudant not configured correctly
- network connectivity issue to Cloudant
- invalid values in `backend/.env`

Check:
- [`backend/app/core/config.py`](backend/app/core/config.py)
- [`backend/app/core/cloudant_db.py`](backend/app/core/cloudant_db.py)

### B. Frontend runs on a different port than expected
This is normal with Vite. Use the URL shown in terminal.

### C. CORS issues between frontend and backend
The demo backend allows common localhost/127.0.0.1 frontend origins. If you change ports, check:
- [`backend/app/main_demo.py`](backend/app/main_demo.py)

### D. Upload works but parsing looks demo-like
This is expected in the current repository state. The ingestion path still includes placeholder/demo behavior and is not yet a full production-grade watsonx parsing implementation.

### E. Execution actions do not create real external artifacts
The project includes execution flow logic, but full production verification of GitHub / Outlook / collaboration execution still depends on real credentials and further hardening.

---

## 12. Important Files to Read After Setup

To understand the workflow quickly, start with:

- [`README.md`](README.md)
- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`backend/app/api/sow.py`](backend/app/api/sow.py)
- [`frontend/src/pages/SOWManagement.tsx`](frontend/src/pages/SOWManagement.tsx)
- [`backend/app/api/integrations.py`](backend/app/api/integrations.py)
- [`docs/UI_PREVIEW.md`](docs/UI_PREVIEW.md)

---

## 13. What Is Already Working

Current repo capabilities include:
- uploading SOWs
- persisting saved SOW review packages
- listing and reopening prior SOWs
- reviewing alerts and action items
- numeric risk and penalty display
- decision workflow:
  - approve
  - reject
  - clear
- execution of approved actions
- timeline-based audit history

---

## 14. What Is Still In Progress

You should expect ongoing work in these areas:
- staged pre-acceptance vs post-approval execution hardening
- continuous revenue leakage monitoring
- real watsonx-backed parsing
- stronger automated tests
- full production-grade integration validation

---

## 15. Suggested Git Workflow

After you pull and run successfully:

```bash
git checkout -b your-feature-branch
```

Make changes, test locally, then:

```bash
git status
git add .
git commit -m "Describe your change"
git push origin your-feature-branch
```

---

## 16. Summary

The most important thing to understand after pulling the repo is this:

**SOW Sentinel is a governed SOW-to-execution workflow.**

The key lifecycle is:

**Upload** → **Analyze** → **Persist** → **Review** → **Accept/Reject/Clear** → **Execute Approved Actions**

If you can run backend + frontend and reach the [`/sows`](frontend/src/pages/SOWManagement.tsx:1) flow, you are set up correctly.