
import os
import sys
import logging
from google import genai
from google.genai import types

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Set current directory to backend to pick up .env
backend_dir = '/Users/jeetendranayak/Documents/crewai/SOW-Hackathon/Contract-Intelligence/backend'
os.chdir(backend_dir)
sys.path.append(backend_dir)

from app.core.config import settings

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./gcp-key.json"

def test_gemini():
    print(f"Project ID: {settings.GCP_PROJECT_ID}")
    print(f"Location: {settings.GCP_LOCATION}")
    print(f"Model ID: {settings.GEMINI_MODEL_ID}")
    
    try:
        client = genai.Client(
            vertexai=True,
            project=settings.GCP_PROJECT_ID,
            location=settings.GCP_LOCATION
        )
        print("Client initialized")
        
        print("Calling generate_content...")
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL_ID,
            contents="Hello, are you there?"
        )
        print(f"Response received: {response.text}")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini()
