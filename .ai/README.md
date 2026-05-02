# AI Assistant Quick Reference

This directory contains comprehensive context files to help AI assistants understand and work with this codebase.

## Files in This Directory

### 1. `project-context.md` (619 lines)
**Complete project overview** including:
- What the project does
- Current state and progress
- Architecture and data flow
- Code structure and patterns
- Development workflow
- Troubleshooting guide

**Use this when**: You need to understand the overall project, its goals, and how everything fits together.

### 2. `codebase-summary.md` (545 lines)
**Detailed codebase analysis** including:
- File inventory and statistics
- Critical files and their status
- Code patterns and examples
- Dependencies and configurations
- API endpoints and data models
- Next actions and priorities

**Use this when**: You need specific information about files, code structure, or implementation details.

## Root Level Context Files

### `.cursorrules` (346 lines)
**AI coding assistant rules** including:
- Project overview and tech stack
- File structure and patterns
- Development commands
- Common tasks and workflows
- IBM Cloud integration details

**Use this when**: You're actively coding and need quick reference for patterns, commands, or project structure.

## Quick Start for AI Assistants

### Understanding the Project (30 seconds)
1. Read the "What This Project Does" section in `project-context.md`
2. Check "Current Project State" to see what's working
3. Review "Architecture Overview" for system design

### Getting Context for Coding (1 minute)
1. Check `codebase-summary.md` for file locations
2. Review "Code Patterns Used" in `project-context.md`
3. Look at `.cursorrules` for development commands

### Understanding a Specific Feature (2 minutes)
1. Find the relevant section in `project-context.md`:
   - "Key Concepts" for business logic
   - "Code Structure Explained" for file organization
   - "Data Flow" for how data moves through the system
2. Check `codebase-summary.md` for implementation status
3. Review actual code files for details

## Key Information at a Glance

### Project Status
```
✅ Backend API running (demo mode)
✅ Python environment set up
✅ Node.js installed
🔄 Frontend npm install in progress
⏳ IBM Cloud integration pending
⏳ AI agents to be implemented
```

### Tech Stack
```
Backend:  Python 3.13, FastAPI, Pydantic
Frontend: React 18, TypeScript, Material-UI
Database: IBM Cloudant (NoSQL)
AI/ML:    IBM watsonx.ai, Watson Discovery
Deploy:   Podman/Docker, IBM Cloud
```

### Running Services
```
Backend:  http://localhost:8000 ✅
API Docs: http://localhost:8000/docs ✅
Frontend: http://localhost:3000 🔄
```

### Critical Files
```
Backend Entry:  backend/app/main_demo.py (running)
Frontend Entry: frontend/src/App.tsx (pending)
Config:         backend/.env (needs IBM Cloud credentials)
Database:       backend/app/core/cloudant_db.py
API Routes:     backend/app/api/*.py
```

### Common Commands
```bash
# Backend
cd backend && source venv/bin/activate
python -m uvicorn app.main_demo:app --reload

# Frontend
cd frontend && npm install && npm start

# Podman
./start-podman.sh
```

## How to Use These Files

### Scenario 1: "I need to add a new API endpoint"
1. Check `.cursorrules` → "Code Patterns" → "FastAPI Endpoint Pattern"
2. Look at `codebase-summary.md` → "API Endpoints Implemented"
3. Review `project-context.md` → "Common Tasks" → "Adding a New API Endpoint"
4. Examine existing files in `backend/app/api/`

### Scenario 2: "I need to implement an AI agent"
1. Read `project-context.md` → "Architecture Overview" → "Multi-Agent System"
2. Check `codebase-summary.md` → "AI Agent Files" for status
3. Review `project-context.md` → "Common Tasks" → "Implementing an AI Agent"
4. Look at `backend/app/agents/contract_agent.py` for skeleton

### Scenario 3: "I need to understand the data model"
1. Check `project-context.md` → "Database Schema (Cloudant)"
2. Review `codebase-summary.md` → "Data Models"
3. Examine `backend/app/models/cloudant_models.py`

### Scenario 4: "I need to set up IBM Cloud"
1. Read `project-context.md` → "IBM Cloud Integration"
2. Check root `docs/CLOUDANT_SETUP.md`
3. Review `backend/.env.example` for required variables

### Scenario 5: "I need to troubleshoot an issue"
1. Check `project-context.md` → "Troubleshooting Guide"
2. Review `codebase-summary.md` → "Known Issues"
3. Look at root `SETUP_GUIDE.md` for detailed troubleshooting

## File Relationships

```
.ai/README.md (this file)
    ↓
    ├─→ project-context.md (comprehensive overview)
    │   ├─→ What & Why
    │   ├─→ Architecture
    │   ├─→ Data Flow
    │   └─→ Development Guide
    │
    ├─→ codebase-summary.md (detailed analysis)
    │   ├─→ File Inventory
    │   ├─→ Code Statistics
    │   ├─→ Implementation Status
    │   └─→ Next Actions
    │
    └─→ ../.cursorrules (coding rules)
        ├─→ Quick Reference
        ├─→ Code Patterns
        └─→ Commands
```

## Context File Maintenance

### When to Update These Files

**Update `project-context.md` when**:
- Architecture changes
- New major features added
- Development workflow changes
- New IBM Cloud services integrated

**Update `codebase-summary.md` when**:
- File structure changes significantly
- Implementation status changes
- New dependencies added
- Code statistics need updating

**Update `.cursorrules` when**:
- Coding patterns change
- New commands added
- Project structure reorganized

### How to Keep Context Fresh

1. **After major milestones**: Update all three files
2. **Weekly**: Review and update status sections
3. **Before handoff**: Ensure all context is current
4. **After debugging**: Add to troubleshooting sections

## Tips for AI Assistants

### Do's ✅
- Read the relevant context file before making changes
- Check implementation status before suggesting code
- Follow the established code patterns
- Reference the correct file paths
- Use the documented commands

### Don'ts ❌
- Don't assume file locations without checking
- Don't ignore the current project state
- Don't suggest features that conflict with architecture
- Don't forget about IBM Cloud integration requirements
- Don't overlook the demo vs. production modes

## Quick Reference Links

### Documentation
- Main README: `../README.md`
- Architecture: `../ARCHITECTURE.md`
- Setup Guide: `../SETUP_GUIDE.md`
- Quick Start: `../QUICK_START_DEMO.md`
- Hackathon Plan: `../HACKATHON_GUIDE.md`

### Code
- Backend: `../backend/app/`
- Frontend: `../frontend/src/`
- API Docs: http://localhost:8000/docs

### Configuration
- Environment: `../backend/.env`
- Python Deps: `../backend/requirements.txt`
- Node Deps: `../frontend/package.json`
- Containers: `../podman-compose.yml`

## Summary

These context files provide **comprehensive information** about the Contract Intelligence System project. They're designed to help AI assistants quickly understand the codebase, make informed decisions, and provide accurate assistance.

**Start with**: `project-context.md` for overview  
**Dive into**: `codebase-summary.md` for details  
**Quick ref**: `.cursorrules` for coding  

All files are kept up-to-date and cross-referenced for easy navigation.