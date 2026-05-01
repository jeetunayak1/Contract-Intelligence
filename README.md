# Contract Intelligence & SLA Compliance System

> An agentic AI system for automated contract management, SLA monitoring, and proactive risk detection

[![IBM Cloud](https://img.shields.io/badge/IBM%20Cloud-Powered-blue)](https://cloud.ibm.com)
[![watsonx.ai](https://img.shields.io/badge/watsonx.ai-Enabled-purple)](https://www.ibm.com/watsonx)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-blue)](https://reactjs.org/)

## 🎯 Problem Statement

Organizations struggle with manual contract management, leading to:
- **Missed SLA breaches** causing customer dissatisfaction
- **Revenue leakage** from underutilized services and missed billing
- **Financial penalties** due to compliance failures
- **Lack of visibility** across multiple contracts and commitments

## 💡 Solution

An intelligent multi-agent system that:
1. **Automatically parses** contracts to extract critical business terms
2. **Monitors SLA compliance** in real-time against operational data
3. **Proactively identifies** financial and compliance risks
4. **Alerts stakeholders** with actionable recommendations
5. **Forecasts future risks** before breaches occur

## 🏗️ Architecture

### Multi-Agent System

```
┌─────────────────┐
│ Contract Agent  │ → Extracts pricing, SLAs, penalties, renewal terms
└─────────────────┘
         ↓
┌─────────────────┐
│ Compliance Agent│ → Compares obligations with operational data
└─────────────────┘
         ↓
┌─────────────────┐
│   Risk Agent    │ → Detects violations, revenue leakage, penalties
└─────────────────┘
         ↓
┌─────────────────┐
│   Alert Agent   │ → Notifies stakeholders with recommendations
└─────────────────┘
         ↓
┌─────────────────┐
│ Forecast Agent  │ → Predicts future compliance risks
└─────────────────┘
```

### Technology Stack

**Frontend:**
- React 18+ with TypeScript
- Material-UI for components
- Recharts for data visualization
- Redux Toolkit for state management

**Backend:**
- Python 3.11+ with FastAPI
- LangChain for agent orchestration
- Celery for background tasks

**IBM Cloud Services:**
- **watsonx.ai** - LLM for contract parsing and risk analysis
- **watsonx Orchestrate** - Agent workflow automation (optional)
- **Watson Discovery** - Document intelligence
- **Cloudant** - NoSQL database (JSON document storage)
- **Event Streams (Kafka)** - Real-time data processing (optional)
- **Cloud Functions** - Serverless event handling (optional)
- **Cloud Object Storage** - Contract file storage

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- IBM Cloud account with watsonx access
- Git

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-team/contract-intelligence-system.git
cd contract-intelligence-system
```

2. **Set up environment variables:**
```bash
cp backend/.env.example backend/.env
# Edit .env with your IBM Cloud Cloudant credentials
```

3. **Set up Cloudant:**
- Follow [`docs/CLOUDANT_SETUP.md`](docs/CLOUDANT_SETUP.md) to provision Cloudant
- Update `.env` with your Cloudant URL and API key

4. **Run locally:**

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python test_cloudant.py  # Test connection
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

5. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
contract-intelligence-system/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── contract_agent.py
│   │   │   ├── compliance_agent.py
│   │   │   ├── risk_agent.py
│   │   │   ├── alert_agent.py
│   │   │   └── forecast_agent.py
│   │   ├── api/
│   │   │   ├── contracts.py
│   │   │   ├── compliance.py
│   │   │   ├── risks.py
│   │   │   └── alerts.py
│   │   ├── models/
│   │   │   ├── contract.py
│   │   │   ├── sla_term.py
│   │   │   └── risk.py
│   │   ├── services/
│   │   │   ├── watsonx_service.py
│   │   │   ├── discovery_service.py
│   │   │   └── orchestrate_service.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   ├── ContractUpload/
│   │   │   ├── ComplianceMonitor/
│   │   │   ├── RiskHeatmap/
│   │   │   └── AlertPanel/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── store/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── scripts/
│   ├── setup_ibm_cloud.sh
│   └── seed_data.py
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔑 Key Features

### 1. Contract Parsing
- Upload PDF/DOCX contracts
- Automatic extraction of:
  - Pricing and payment terms
  - SLA commitments (uptime, response times)
  - Penalty clauses
  - Renewal dates
  - Service scope

### 2. Real-Time Compliance Monitoring
- Track system uptime vs. contracted uptime
- Monitor incident response times
- Measure resolution times
- Calculate compliance scores
- Identify deviations and trends

### 3. Risk Detection
- Identify potential SLA breaches
- Calculate financial exposure
- Detect revenue leakage opportunities
- Risk scoring and prioritization
- Pattern recognition for recurring issues

### 4. Proactive Alerting
- Multi-channel notifications (email, Slack, dashboard)
- Severity-based routing
- Actionable recommendations
- Alert aggregation
- Escalation workflows

### 5. Predictive Forecasting
- Time-series forecasting of SLA metrics
- Predict future compliance risks
- Capacity planning recommendations
- What-if scenario modeling

## 📊 Dashboard Features

- **Contract Overview:** All active contracts at a glance
- **Compliance Dashboard:** Real-time SLA compliance metrics
- **Risk Heatmap:** Visual representation of risk exposure
- **Alert Center:** Active alerts and notifications
- **Analytics:** Historical trends and forecasts
- **Financial Impact:** Revenue leakage and penalty tracking

## 🔧 Configuration

### IBM Cloud Services Setup

1. **watsonx.ai:**
```python
# backend/app/core/config.py
WATSONX_API_KEY = "your-api-key"
WATSONX_PROJECT_ID = "your-project-id"
WATSONX_URL = "https://us-south.ml.cloud.ibm.com"
```

2. **Watson Discovery:**
```python
DISCOVERY_API_KEY = "your-api-key"
DISCOVERY_URL = "your-discovery-url"
DISCOVERY_COLLECTION_ID = "your-collection-id"
```

3. **watsonx Orchestrate:**
```python
ORCHESTRATE_API_KEY = "your-api-key"
ORCHESTRATE_URL = "your-orchestrate-url"
```

### Database Configuration

**PostgreSQL:**
```python
DATABASE_URL = "postgresql://user:password@localhost:5432/contracts_db"
```

**Cloudant:**
```python
CLOUDANT_URL = "your-cloudant-url"
CLOUDANT_API_KEY = "your-api-key"
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📈 API Documentation

Full API documentation is available at `/docs` when running the backend server.

### Key Endpoints

**Contracts:**
- `POST /api/contracts/upload` - Upload and parse contract
- `GET /api/contracts` - List all contracts
- `GET /api/contracts/{id}` - Get contract details

**Compliance:**
- `GET /api/compliance/dashboard` - Compliance overview
- `GET /api/compliance/contracts/{id}` - Contract compliance

**Risks:**
- `GET /api/risks` - List all active risks
- `POST /api/risks/assess` - Trigger risk assessment

**Alerts:**
- `GET /api/alerts` - List all alerts
- `PUT /api/alerts/{id}/acknowledge` - Acknowledge alert

See [API.md](docs/API.md) for complete documentation.

## 🚢 Deployment

### IBM Cloud Deployment

1. **Build and push Docker images:**
```bash
docker build -t us.icr.io/your-namespace/contract-backend:latest ./backend
docker build -t us.icr.io/your-namespace/contract-frontend:latest ./frontend
docker push us.icr.io/your-namespace/contract-backend:latest
docker push us.icr.io/your-namespace/contract-frontend:latest
```

2. **Deploy to Kubernetes:**
```bash
kubectl apply -f k8s/
```

3. **Configure services:**
```bash
./scripts/setup_ibm_cloud.sh
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

## 🎥 Demo

Watch our 3-minute demo video: [Link to video]

The demo showcases:
1. Contract upload and automatic parsing
2. Real-time SLA compliance monitoring
3. Risk detection and alerting
4. Predictive forecasting capabilities

## 📝 IBM Bob Usage

This project was built with assistance from IBM Bob:

1. **Architecture Design:** Bob helped design the multi-agent system architecture
2. **Code Generation:** Generated boilerplate code for agents and API endpoints
3. **IBM Cloud Integration:** Assisted with watsonx.ai and Watson Discovery integration
4. **Code Review:** Identified security issues and performance optimizations
5. **Documentation:** Helped create comprehensive documentation

**Bob Report:** See [bob-report.md](bob-report.md) for the exported Bob session report.

## 🏆 Hackathon Deliverables

- ✅ Video demonstration (3 minutes)
- ✅ Problem and solution statement
- ✅ IBM Bob and watsonx usage documentation
- ✅ GitHub repository with code
- ✅ Exported IBM Bob report
- ✅ Architecture documentation
- ✅ Setup and deployment instructions

## 👥 Team

- **Backend Developer:** [Name] - Python, FastAPI, IBM Cloud integration
- **Frontend Developer:** [Name] - React, TypeScript, UI/UX
- **AI/ML Specialist:** [Name] - watsonx.ai, agent design, forecasting
- **DevOps Engineer:** [Name] - Kubernetes, CI/CD, monitoring

## 📄 License

This project was created for the IBM Hackathon 2026.

## 🙏 Acknowledgments

- IBM watsonx team for AI capabilities
- IBM Cloud for infrastructure
- Hackathon mentors for guidance
- Open source community for tools and libraries

## 📞 Support

For questions or issues:
- Create an issue in this repository
- Contact the team via Slack: #contract-intelligence-team
- Email: team@example.com

---

**Built with ❤️ using IBM watsonx and IBM Cloud**