# Cloud Providers Setup (IBM & GCP)

SOW Sentinel supports dual cloud providers for its core infrastructure: **IBM Cloud** (default) and **Google Cloud Platform (GCP)**. You can easily switch between them using environment variables.

## 1. Supported Services

| Feature | IBM Cloud (Default) | Google Cloud Platform (GCP) |
| :--- | :--- | :--- |
| **NoSQL Database** | IBM Cloudant | Google Cloud Firestore |
| **LLM / Generative AI** | IBM watsonx.ai | Google GenAI (Gemini) |

## 2. Switching Providers

The application allows you to mix and match providers using environment variables in your `backend/.env` file.

- **`DB_PROVIDER`**: Controls the database. Set to `ibm` (Cloudant) or `gcp` (Firestore).
- **`LLM_PROVIDER`**: Controls the AI models. Set to `ibm` (watsonx.ai) or `gcp` (Gemini).

Example of mixing providers:
```env
DB_PROVIDER=ibm
LLM_PROVIDER=gcp
```

---

## 3. IBM Cloud Setup

To use the IBM stack, ensure your `backend/.env` contains the IBM provider configurations:

```env
DB_PROVIDER=ibm
LLM_PROVIDER=ibm

# IBM Cloudant
CLOUDANT_URL=https://<your-cloudant-url>.cloudantnosqldb.appdomain.cloud
CLOUDANT_API_KEY=your_cloudant_api_key
CLOUDANT_DB_NAME=contract-intelligence

# IBM watsonx.ai
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID=your_watsonx_project_id
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_MODEL_ID=meta-llama/llama-3-3-70b-instruct
```

For more details on IBM setup, see the [IBM Cloud Setup Guide](IBM_CLOUD_SETUP_COMPLETE.md).

---

## 4. Google Cloud Platform Setup

To use the GCP stack, you will need a Google Cloud Project with **Firestore** (in Native mode) and **Vertex AI** / **Gemini API** enabled.

Ensure your `backend/.env` contains the GCP provider configurations:

```env
DB_PROVIDER=gcp
LLM_PROVIDER=gcp

# GCP Configuration
GCP_PROJECT_ID=your-google-cloud-project-id
FIRESTORE_DB_NAME=(default)
GEMINI_MODEL_ID=gemini-1.5-pro-002
```

### Authentication for GCP

To use Google Cloud services, you need to authenticate your application. The recommended approach for servers is using a Service Account JSON key.

#### How to get a GCP Service Account JSON Key:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Select your project from the top dropdown.
3. Navigate to **IAM & Admin** > **Service Accounts**.
4. Click **+ CREATE SERVICE ACCOUNT**.
5. Give it a name (e.g., `sow-sentinel-sa`) and click **Create and Continue**.
6. Grant it the necessary roles:
   - **Cloud Datastore User** (for Firestore)
   - **Vertex AI User** (for Gemini)
7. Click **Done**.
8. Find the newly created Service Account in the list and click on it.
9. Go to the **Keys** tab.
10. Click **Add Key** > **Create new key**.
11. Select **JSON** and click **Create**. The key will automatically download to your computer.

Once downloaded, you must set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to this JSON file:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/gcp-service-account-key.json"
```

Alternatively, if you are running locally and have the Google Cloud SDK installed, you can authenticate using:

```bash
gcloud auth application-default login
```

### Handling GCP Credentials in Deployment

When moving to production, how you manage the `GOOGLE_APPLICATION_CREDENTIALS` depends on where you deploy the application:

#### 1. Deploying on Google Cloud (Cloud Run, GKE, Compute Engine)
**You do not need a JSON key file!** 
Instead, you attach the Service Account directly to the compute resource (e.g., assigning the Service Account to your Cloud Run service). The Google Cloud SDK will automatically detect the permissions without needing the `GOOGLE_APPLICATION_CREDENTIALS` variable.

#### 2. Deploying on External Platforms (Vercel, Heroku, AWS, Render)
External platforms cannot use Google's native Workload Identity directly. You must securely provide the JSON key:

**Option A (Base64 Environment Variable):**
1. Encode your JSON file to base64: `base64 -i gcp-key.json`
2. Add the base64 string as a Secret/Environment Variable in your hosting provider (e.g., `GCP_SA_KEY_BASE64`).
3. Modify your deployment startup script (`start.sh` or `Dockerfile`) to decode it back into a file:
   ```bash
   echo $GCP_SA_KEY_BASE64 | base64 --decode > /app/gcp-key.json
   export GOOGLE_APPLICATION_CREDENTIALS="/app/gcp-key.json"
   ```

**Option B (Secret Mounts):**
If your platform supports Secret Files (like Docker Swarm, Kubernetes Secrets, or Render Secret Files), you upload the raw JSON file to the platform's secret manager. The platform will securely mount the file into the container at runtime. You then set `GOOGLE_APPLICATION_CREDENTIALS` to that mount path.

### Firestore Configuration
- The app will automatically create collections equivalent to the `CLOUDANT_DB_NAME` (e.g., `contract-intelligence`).
- Firestore creates single-field indexes automatically. If you need complex querying, GCP might prompt you to create a composite index via the Firebase/GCP Console.

### Gemini Configuration

You can use the Gemini models either through Vertex AI (Enterprise) or Google AI Studio (Free Tier). The `GEMINI_MODEL_ID` is fully configurable in the `.env` file (e.g., `gemini-1.5-pro`, `gemini-1.5-flash`).

#### Option 1: Free Tier via Google AI Studio
If you do not want to set up a full GCP project or billing, you can use the free Google AI Studio:
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **Get API key** in the left sidebar.
4. Click **Create API key** and copy the generated key.
5. In your `backend/.env` file, add:
   ```env
   GOOGLE_API_KEY="your-free-gemini-api-key"
   ```
*(Note: If `GOOGLE_API_KEY` is present, the GenAI SDK will automatically use it instead of looking for Vertex AI credentials.)*

#### Option 2: Enterprise via Vertex AI
If you are using Vertex AI on Google Cloud, the SDK will authenticate using the `GOOGLE_APPLICATION_CREDENTIALS` JSON file or Workload Identity as described in the authentication section above.

---

## 5. Installing Dependencies

Make sure to install the required dependencies for both providers:

```bash
cd backend
pip install -r requirements.txt
```

*(Note: `google-cloud-firestore` and `google-genai` must be present in the `requirements.txt` file)*
