
import os
import sys
from google import genai
from google.genai import types

# Set current directory to backend to pick up .env
os.chdir('/Users/jeetendranayak/Documents/crewai/SOW-Hackathon/Contract-Intelligence/backend')

# Add backend to path
sys.path.append('/Users/jeetendranayak/Documents/crewai/SOW-Hackathon/Contract-Intelligence/backend')
from app.core.config import settings

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./gcp-key.json"

def test_gemini():
    try:
        print(f"LLM_PROVIDER: {settings.LLM_PROVIDER}")
        print(f"GCP_PROJECT_ID: {settings.GCP_PROJECT_ID}")
        print(f"GEMINI_MODEL_ID: {settings.GEMINI_MODEL_ID}")
        
        client = genai.Client(
            vertexai=True,
            project=settings.GCP_PROJECT_ID,
            location=settings.GCP_LOCATION
        )
        print(f"Connected to Vertex AI project: {settings.GCP_PROJECT_ID}")
        
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL_ID,
            contents="Say 'AI is working'"
        )
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini()
