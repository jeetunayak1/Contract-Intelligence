# IBM Cloud PostgreSQL Setup Guide

## Overview

This guide shows how to provision and connect to IBM Cloud Databases for PostgreSQL for your hackathon project.

---

## Step 1: Provision PostgreSQL on IBM Cloud

### Via IBM Cloud Console:

1. **Log in to IBM Cloud:**
   - Go to https://cloud.ibm.com
   - Use your hackathon team account

2. **Create Database Instance:**
   - Navigate to **Catalog** → **Databases**
   - Select **Databases for PostgreSQL**
   - Configure:
     - **Service name:** `contract-intelligence-db`
     - **Region:** Choose closest to your location (e.g., `us-south`)
     - **Resource group:** Default or your team's resource group
     - **Plan:** Standard (recommended for hackathon)
     - **Initial disk allocation:** 20 GB (minimum)
     - **Initial RAM:** 1 GB per member (minimum)

3. **Create the instance:**
   - Click **Create**
   - Wait 5-10 minutes for provisioning

### Via IBM Cloud CLI:

```bash
# Install IBM Cloud CLI if not already installed
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh

# Login
ibmcloud login --sso

# Target your resource group
ibmcloud target -g Default

# Create PostgreSQL instance
ibmcloud resource service-instance-create contract-intelligence-db \
  databases-for-postgresql \
  standard \
  us-south \
  -p '{
    "members_memory_allocation_mb": "1024",
    "members_disk_allocation_mb": "20480"
  }'
```

---

## Step 2: Get Connection Credentials

### Via IBM Cloud Console:

1. **Navigate to your database:**
   - Go to **Resource List** → **Databases**
   - Click on `contract-intelligence-db`

2. **Get connection string:**
   - Click **Service Credentials** in left menu
   - Click **New Credential**
   - Name it: `hackathon-credentials`
   - Click **Add**
   - Click **View credentials** to see the JSON

3. **Extract connection details:**
   ```json
   {
     "connection": {
       "postgres": {
         "composed": [
           "postgresql://ibm_cloud_xxx:password@host:port/ibmclouddb?sslmode=verify-full"
         ],
         "hosts": [
           {
             "hostname": "xxx.databases.appdomain.cloud",
             "port": 32541
           }
         ],
         "authentication": {
           "username": "ibm_cloud_xxx",
           "password": "your-password"
         },
         "database": "ibmclouddb",
         "certificate": {
           "certificate_base64": "LS0tLS1CRUdJTi..."
         }
       }
     }
   }
   ```

### Via IBM Cloud CLI:

```bash
# Get service credentials
ibmcloud resource service-key contract-intelligence-db-credentials

# Or create new credentials
ibmcloud resource service-key-create hackathon-credentials \
  --instance-name contract-intelligence-db
```

---

## Step 3: Configure Your Application

### Option A: Using Connection String (Recommended)

1. **Save the SSL certificate:**

```bash
# Create certs directory
mkdir -p backend/certs

# Save certificate (from credentials JSON)
echo "-----BEGIN CERTIFICATE-----
[paste certificate_base64 content here]
-----END CERTIFICATE-----" > backend/certs/ibm-cloud-postgres.crt
```

2. **Update `.env` file:**

```bash
# IBM Cloud PostgreSQL Connection
DATABASE_URL=postgresql+asyncpg://ibm_cloud_xxx:password@xxx.databases.appdomain.cloud:32541/ibmclouddb?ssl=require

# SSL Certificate Path
DB_SSL_CERT_PATH=./certs/ibm-cloud-postgres.crt
```

### Option B: Using Individual Parameters

Update your `.env`:

```bash
DB_HOST=xxx.databases.appdomain.cloud
DB_PORT=32541
DB_NAME=ibmclouddb
DB_USER=ibm_cloud_xxx
DB_PASSWORD=your-password
DB_SSL_MODE=verify-full
DB_SSL_CERT_PATH=./certs/ibm-cloud-postgres.crt
```

---

## Step 4: Update Database Configuration

### Update `backend/app/core/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Database - IBM Cloud PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/contracts_db"
    
    # SSL Configuration for IBM Cloud
    DB_SSL_CERT_PATH: str | None = None
    DB_SSL_MODE: str = "require"  # Options: disable, allow, prefer, require, verify-ca, verify-full
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### Update `backend/app/core/database.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import logging
import ssl

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure SSL context for IBM Cloud
ssl_context = None
if settings.DB_SSL_CERT_PATH:
    ssl_context = ssl.create_default_context(cafile=settings.DB_SSL_CERT_PATH)
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED

# Create async engine with SSL support
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={
        "ssl": ssl_context,
        "server_settings": {
            "application_name": "contract-intelligence-system"
        }
    } if ssl_context else {}
)

# ... rest of the file remains the same ...
```

---

## Step 5: Test Connection

### Create a test script `backend/test_db_connection.py`:

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
import ssl

async def test_connection():
    """Test IBM Cloud PostgreSQL connection"""
    
    # Configure SSL if needed
    ssl_context = None
    if settings.DB_SSL_CERT_PATH:
        ssl_context = ssl.create_default_context(cafile=settings.DB_SSL_CERT_PATH)
    
    # Create engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        connect_args={"ssl": ssl_context} if ssl_context else {}
    )
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute("SELECT version()")
            version = result.scalar()
            print(f"✅ Successfully connected to IBM Cloud PostgreSQL!")
            print(f"PostgreSQL version: {version}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_connection())
```

### Run the test:

```bash
cd backend
python test_db_connection.py
```

---

## Step 6: Initialize Database Schema

### Run migrations:

```bash
cd backend

# Create tables
python -c "
import asyncio
from app.core.database import init_db
asyncio.run(init_db())
"
```

### Or use Alembic for migrations:

```bash
# Install alembic
pip install alembic

# Initialize alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

---

## Step 7: Update Docker Compose (Optional)

If you want to use IBM Cloud PostgreSQL with Docker Compose, update `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # Remove local postgres service
  # postgres:
  #   ...

  # Backend API - connects to IBM Cloud PostgreSQL
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: contract-intelligence-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - DB_SSL_CERT_PATH=/app/certs/ibm-cloud-postgres.crt
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
      - ./backend/certs:/app/certs:ro
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # ... rest of services ...
```

---

## Security Best Practices

### 1. Secure Credentials:

```bash
# Never commit credentials to Git
echo "backend/certs/" >> .gitignore
echo ".env" >> .gitignore

# Use environment variables
export DATABASE_URL="postgresql+asyncpg://..."
```

### 2. Use IBM Cloud Secrets Manager (Optional):

```bash
# Store credentials in Secrets Manager
ibmcloud secrets-manager secret-create \
  --secret-type arbitrary \
  --name contract-db-credentials \
  --secret-data '{"connection_string": "postgresql://..."}'
```

### 3. Rotate Credentials Regularly:

```bash
# Generate new credentials
ibmcloud resource service-key-create new-credentials \
  --instance-name contract-intelligence-db

# Update application
# Delete old credentials
ibmcloud resource service-key-delete old-credentials
```

---

## Monitoring & Management

### View Database Metrics:

1. Go to IBM Cloud Console
2. Navigate to your database instance
3. Click **Monitoring** tab
4. View:
   - CPU usage
   - Memory usage
   - Disk I/O
   - Connection count

### Database Backups:

IBM Cloud automatically backs up your database:
- **Continuous backup:** Every 24 hours
- **Point-in-time recovery:** Up to 7 days
- **Manual backup:** Available in console

### Scaling:

```bash
# Scale memory
ibmcloud resource service-instance-update contract-intelligence-db \
  --service-plan-id standard \
  -p '{"members_memory_allocation_mb": "2048"}'

# Scale disk
ibmcloud resource service-instance-update contract-intelligence-db \
  -p '{"members_disk_allocation_mb": "40960"}'
```

---

## Troubleshooting

### Connection Timeout:

```bash
# Check firewall rules
# Ensure your IP is whitelisted in IBM Cloud

# Test connection
psql "postgresql://user:pass@host:port/dbname?sslmode=require"
```

### SSL Certificate Issues:

```bash
# Download certificate again
# Verify certificate format
openssl x509 -in backend/certs/ibm-cloud-postgres.crt -text -noout

# Test SSL connection
openssl s_client -connect host:port -CAfile backend/certs/ibm-cloud-postgres.crt
```

### Performance Issues:

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

---

## Cost Optimization for Hackathon

### Free Tier / Lite Plan:
- IBM Cloud offers a **Lite plan** for PostgreSQL
- Limited resources but sufficient for hackathon
- No credit card required

### Standard Plan Costs:
- ~$30-50 for hackathon duration (3-4 days)
- Can be deleted after submission
- Team account should cover costs

### Tips:
1. Use minimum resources during development
2. Scale up only for demo
3. Delete instance after hackathon
4. Use local PostgreSQL for initial development

---

## Quick Reference

### Connection String Format:
```
postgresql+asyncpg://username:password@hostname:port/database?ssl=require
```

### Common Commands:
```bash
# List databases
ibmcloud resource service-instances --service-name databases-for-postgresql

# Get credentials
ibmcloud resource service-keys --instance-name contract-intelligence-db

# Delete instance (after hackathon)
ibmcloud resource service-instance-delete contract-intelligence-db
```

---

## Support

- **IBM Cloud Docs:** https://cloud.ibm.com/docs/databases-for-postgresql
- **Hackathon Mentors:** Available in Slack
- **IBM Cloud Support:** Available in console

---

**Ready to connect!** Follow these steps and you'll have your application connected to IBM Cloud PostgreSQL in minutes.