# IBM Cloudant Setup Guide

## Overview

This guide shows how to provision and connect to IBM Cloudant for your Contract Intelligence System hackathon project.

---

## Why Cloudant?

✅ **Native IBM Cloud service** - Shows IBM ecosystem usage  
✅ **Free Lite plan** - Perfect for hackathon  
✅ **JSON-native** - Ideal for contract documents  
✅ **Easy setup** - No SSL certificates needed  
✅ **Built-in replication** - High availability  
✅ **Flexible schema** - Adapt as you build  

---

## Step 1: Provision Cloudant on IBM Cloud

### Via IBM Cloud Console:

1. **Log in to IBM Cloud:**
   - Go to https://cloud.ibm.com
   - Use your hackathon team account

2. **Create Cloudant Instance:**
   - Navigate to **Catalog** → **Databases**
   - Select **Cloudant**
   - Configure:
     - **Service name:** `contract-intelligence-cloudant`
     - **Region:** Choose closest to your location (e.g., `us-south`)
     - **Plan:** **Lite** (FREE - perfect for hackathon!)
     - **Authentication:** IAM and legacy credentials

3. **Create the instance:**
   - Click **Create**
   - Wait 1-2 minutes for provisioning

### Via IBM Cloud CLI:

```bash
# Login to IBM Cloud
ibmcloud login --sso

# Target your resource group
ibmcloud target -g Default

# Create Cloudant instance (Lite plan - FREE)
ibmcloud resource service-instance-create contract-intelligence-cloudant \
  cloudantnosqldb \
  lite \
  us-south
```

---

## Step 2: Get Connection Credentials

### Via IBM Cloud Console:

1. **Navigate to your Cloudant instance:**
   - Go to **Resource List** → **Databases**
   - Click on `contract-intelligence-cloudant`

2. **Create Service Credentials:**
   - Click **Service Credentials** in left menu
   - Click **New Credential**
   - Name it: `hackathon-credentials`
   - Role: **Manager** (full access)
   - Click **Add**

3. **View credentials:**
   - Click **View credentials** dropdown
   - You'll see JSON like this:

```json
{
  "apikey": "your-api-key-here",
  "host": "your-account.cloudantnosqldb.appdomain.cloud",
  "iam_apikey_description": "Auto-generated for key...",
  "iam_apikey_name": "hackathon-credentials",
  "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Manager",
  "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::...",
  "url": "https://your-account.cloudantnosqldb.appdomain.cloud",
  "username": "your-username"
}
```

4. **Copy these values:**
   - `apikey` - Your API key for authentication
   - `url` - Your Cloudant URL

### Via IBM Cloud CLI:

```bash
# Create service credentials
ibmcloud resource service-key-create hackathon-credentials \
  Manager \
  --instance-name contract-intelligence-cloudant

# View credentials
ibmcloud resource service-key hackathon-credentials
```

---

## Step 3: Configure Your Application

### Update `.env` file:

```bash
# IBM Cloudant Database
CLOUDANT_URL=https://your-account.cloudantnosqldb.appdomain.cloud
CLOUDANT_API_KEY=your-api-key-here
CLOUDANT_DB_NAME=contract-intelligence
```

### Test Connection:

Create `backend/test_cloudant.py`:

```python
"""Test Cloudant connection"""
import asyncio
from app.core.cloudant_db import CloudantDatabase
from app.core.config import settings

async def test_connection():
    """Test IBM Cloudant connection"""
    try:
        db = CloudantDatabase()
        
        # Create database
        success = await db.create_database()
        if success:
            print("✅ Successfully connected to IBM Cloudant!")
            print(f"Database: {settings.CLOUDANT_DB_NAME}")
            print(f"URL: {settings.CLOUDANT_URL}")
            
            # Test document creation
            test_doc = {
                "type": "test",
                "message": "Hello from Contract Intelligence System!"
            }
            created = await db.create_document(test_doc)
            print(f"✅ Test document created: {created['_id']}")
            
            # Clean up test document
            await db.delete_document(created['_id'], created['_rev'])
            print("✅ Test document deleted")
            
            return True
        else:
            print("❌ Failed to create database")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
```

Run the test:

```bash
cd backend
python test_cloudant.py
```

---

## Step 4: Initialize Database

### Create Database and Indexes:

The application automatically creates the database and indexes on startup. You can also do it manually:

```python
# backend/init_cloudant.py
import asyncio
from app.core.cloudant_db import init_cloudant

async def main():
    """Initialize Cloudant database"""
    await init_cloudant()
    print("✅ Cloudant initialized successfully!")

if __name__ == "__main__":
    asyncio.run(main())
```

Run initialization:

```bash
cd backend
python init_cloudant.py
```

---

## Step 5: Document Structure

### Contract Document:

```json
{
  "_id": "uuid-here",
  "_rev": "1-revision-hash",
  "type": "contract",
  "contract_number": "CTR-2024-001",
  "customer_name": "Acme Corporation",
  "contract_type": "service",
  "start_date": "2024-01-01",
  "end_date": "2025-12-31",
  "renewal_date": "2025-11-01",
  "status": "active",
  "file_url": "https://...",
  "total_value": 100000.00,
  "currency": "USD",
  "sla_terms": [
    {
      "id": "sla-uuid",
      "metric_name": "System Uptime",
      "metric_type": "uptime",
      "threshold_value": 99.9,
      "threshold_unit": "percentage",
      "penalty_amount": 5000.00,
      "measurement_period": "monthly"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Compliance Metric Document:

```json
{
  "_id": "uuid-here",
  "type": "compliance_metric",
  "contract_id": "contract-uuid",
  "sla_term_id": "sla-uuid",
  "measurement_date": "2024-01-15",
  "actual_value": 99.95,
  "threshold_value": 99.9,
  "compliance_status": "compliant",
  "deviation_percentage": 0.05,
  "created_at": "2024-01-15T00:00:00Z"
}
```

### Risk Assessment Document:

```json
{
  "_id": "uuid-here",
  "type": "risk_assessment",
  "contract_id": "contract-uuid",
  "risk_type": "sla_breach",
  "risk_level": "high",
  "financial_impact": 5000.00,
  "probability_score": 0.75,
  "description": "Potential SLA breach detected",
  "recommendations": "Increase monitoring frequency",
  "assessed_at": "2024-01-15T00:00:00Z"
}
```

### Alert Document:

```json
{
  "_id": "uuid-here",
  "type": "alert",
  "contract_id": "contract-uuid",
  "risk_assessment_id": "risk-uuid",
  "alert_type": "sla_warning",
  "severity": "high",
  "title": "SLA Threshold Approaching",
  "message": "System uptime is approaching SLA threshold",
  "status": "new",
  "notified_users": ["user1@example.com"],
  "created_at": "2024-01-15T00:00:00Z"
}
```

---

## Step 6: Common Operations

### Create a Contract:

```python
from app.core.cloudant_db import cloudant_db
from app.models.cloudant_models import create_contract_document

# Create contract document
contract = create_contract_document(
    contract_number="CTR-2024-001",
    customer_name="Acme Corporation",
    contract_type="service",
    start_date="2024-01-01",
    end_date="2025-12-31",
    total_value=100000.00
)

# Save to Cloudant
created = await cloudant_db.create_document(contract)
print(f"Contract created: {created['_id']}")
```

### Query Contracts:

```python
# Find all active contracts
selector = {
    "type": "contract",
    "status": "active"
}

contracts = await cloudant_db.query_documents(selector, limit=100)
print(f"Found {len(contracts)} active contracts")
```

### Update a Contract:

```python
# Get contract
contract = await cloudant_db.get_document("contract-id")

# Update fields
contract['status'] = 'renewed'
contract['renewal_date'] = '2026-01-01'

# Save changes
updated = await cloudant_db.update_document(contract['_id'], contract)
print(f"Contract updated: {updated['_id']}")
```

### Delete a Contract:

```python
# Get contract
contract = await cloudant_db.get_document("contract-id")

# Delete
success = await cloudant_db.delete_document(contract['_id'], contract['_rev'])
print(f"Contract deleted: {success}")
```

---

## Step 7: Cloudant Dashboard

### Access Cloudant Dashboard:

1. Go to your Cloudant instance in IBM Cloud
2. Click **Launch Dashboard**
3. You'll see:
   - **Databases** - List of all databases
   - **Documents** - View/edit documents
   - **Query** - Run Mango queries
   - **Replication** - Set up replication
   - **Monitoring** - View metrics

### Useful Dashboard Features:

**View Documents:**
- Click on database name
- See all documents
- Click document to view/edit JSON

**Run Queries:**
- Click **Query** tab
- Write Mango queries
- Test selectors

**Create Indexes:**
- Click **Design Documents**
- Create indexes for faster queries

---

## Step 8: Querying with Mango

### Basic Query:

```json
{
  "selector": {
    "type": "contract",
    "status": "active"
  },
  "limit": 10
}
```

### Complex Query:

```json
{
  "selector": {
    "type": "contract",
    "status": "active",
    "total_value": {
      "$gt": 50000
    },
    "end_date": {
      "$gte": "2024-01-01"
    }
  },
  "sort": [
    {"total_value": "desc"}
  ],
  "limit": 20
}
```

### Query with OR:

```json
{
  "selector": {
    "type": "alert",
    "$or": [
      {"severity": "critical"},
      {"severity": "high"}
    ],
    "status": "new"
  }
}
```

---

## Step 9: Best Practices

### 1. Document Design:

✅ **Include type field** - Easy filtering  
✅ **Use ISO dates** - Consistent formatting  
✅ **Embed related data** - Reduce queries  
✅ **Keep documents < 1MB** - Performance  

### 2. Indexing:

```python
# Create indexes for common queries
await cloudant_db.create_index(
    index_fields=["type", "status"],
    index_name="type-status-index"
)

await cloudant_db.create_index(
    index_fields=["contract_number"],
    index_name="contract-number-index"
)
```

### 3. Error Handling:

```python
try:
    doc = await cloudant_db.get_document(doc_id)
except Exception as e:
    if "not found" in str(e).lower():
        # Handle not found
        return None
    else:
        # Handle other errors
        raise
```

### 4. Bulk Operations:

```python
# Create multiple documents at once
documents = [
    create_contract_document(...),
    create_contract_document(...),
    create_contract_document(...)
]

created = await cloudant_db.bulk_create(documents)
```

---

## Step 10: Monitoring & Limits

### Lite Plan Limits:

- **Storage:** 1 GB
- **Throughput:** 20 reads/sec, 10 writes/sec
- **Perfect for hackathon!**

### Monitor Usage:

1. Go to Cloudant instance in IBM Cloud
2. Click **Monitoring** tab
3. View:
   - Storage usage
   - Request rate
   - Document count

### Upgrade if Needed:

```bash
# Upgrade to Standard plan (if needed)
ibmcloud resource service-instance-update contract-intelligence-cloudant \
  --service-plan-id standard
```

---

## Troubleshooting

### Connection Issues:

```python
# Test connection
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

authenticator = IAMAuthenticator('your-api-key')
client = CloudantV1(authenticator=authenticator)
client.set_service_url('your-cloudant-url')

# Test
info = client.get_server_information().get_result()
print(f"Connected to: {info['couchdb']}")
```

### Document Conflicts:

```python
# Handle revision conflicts
try:
    await cloudant_db.update_document(doc_id, document)
except Exception as e:
    if "conflict" in str(e).lower():
        # Get latest version
        latest = await cloudant_db.get_document(doc_id)
        # Merge changes
        # Retry update
```

### Query Performance:

```python
# Create indexes for slow queries
await cloudant_db.create_index(
    index_fields=["field1", "field2"],
    index_name="custom-index"
)
```

---

## Cost Management

### For Hackathon:

✅ **Use Lite plan** - FREE  
✅ **1 GB storage** - Plenty for hackathon  
✅ **Delete after submission** - No ongoing costs  

### After Hackathon:

```bash
# Delete instance to avoid charges
ibmcloud resource service-instance-delete contract-intelligence-cloudant
```

---

## Quick Reference

### Connection String:
```
URL: https://your-account.cloudantnosqldb.appdomain.cloud
API Key: your-api-key
Database: contract-intelligence
```

### Common Commands:

```bash
# List databases
ibmcloud resource service-instances --service-name cloudantnosqldb

# Get credentials
ibmcloud resource service-keys --instance-name contract-intelligence-cloudant

# Delete instance
ibmcloud resource service-instance-delete contract-intelligence-cloudant
```

---

## Support

- **IBM Cloud Docs:** https://cloud.ibm.com/docs/Cloudant
- **Cloudant API Docs:** https://cloud.ibm.com/apidocs/cloudant
- **Hackathon Mentors:** Available in Slack

---

**Ready to use Cloudant!** 🚀

Your Contract Intelligence System is now configured to use IBM Cloudant - a native IBM Cloud NoSQL database perfect for your hackathon project.