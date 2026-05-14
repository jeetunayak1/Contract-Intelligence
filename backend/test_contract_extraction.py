#!/usr/bin/env python3
"""
Test script to verify Contract Intelligence Agent setup
"""
import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_extraction():
    """Test contract extraction"""
    
    print("=" * 60)
    print("Contract Intelligence Agent - Setup Test")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. Checking Environment Variables:")
    print("-" * 60)
    
    google_api_key = os.getenv("GOOGLE_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL_ID", "gemini-1.5-pro")
    gcp_project = os.getenv("GCP_PROJECT_ID")
    
    print(f"GOOGLE_API_KEY: {'✓ Set' if google_api_key else '✗ NOT SET'}")
    print(f"GEMINI_MODEL_ID: {gemini_model}")
    print(f"GCP_PROJECT_ID: {gcp_project or 'Not set'}")
    
    if not google_api_key:
        print("\n❌ ERROR: GOOGLE_API_KEY not set in .env file")
        print("Please add: GOOGLE_API_KEY=your-api-key")
        return False
    
    # Test Gemini client
    print("\n2. Testing Gemini Client:")
    print("-" * 60)
    
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=google_api_key)
        print("✓ Gemini client initialized successfully")
        
        # Test simple generation
        print("\n3. Testing Gemini API Call:")
        print("-" * 60)
        
        test_prompt = "Return only this JSON: {\"test\": \"success\"}"
        
        response = client.models.generate_content(
            model=gemini_model,
            contents=test_prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
            )
        )
        
        response_text = getattr(response, "text", "")
        print(f"✓ API call successful")
        print(f"Response: {response_text[:200]}")
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Run: pip install google-genai")
        return False
    except Exception as e:
        print(f"✗ Gemini API error: {e}")
        return False
    
    # Test contract agent
    print("\n4. Testing Contract Intelligence Agent:")
    print("-" * 60)
    
    try:
        from app.agents.contract_intelligence_agent import get_contract_agent
        
        agent = get_contract_agent()
        print("✓ Contract agent initialized")
        
        # Test with sample text
        sample_contract = """
        SERVICE LEVEL AGREEMENT
        
        Client: Acme Corporation
        Provider: Tech Solutions Inc.
        
        Incident Response SLAs:
        - P1 (Critical): Acknowledge within 15 minutes, resolve within 4 hours
        - P2 (High): Acknowledge within 30 minutes, resolve within 8 hours
        
        Availability SLA:
        - Production: 99.9% uptime
        
        Service Credits:
        - P1 breach: 2% credit per incident, max 10% monthly
        """
        
        print("\n5. Testing Extraction:")
        print("-" * 60)
        
        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_contract)
            temp_path = f.name
        
        try:
            result = await agent.extract_contract(
                file_path=temp_path,
                filename="test_contract.txt"
            )
            
            print("✓ Extraction completed")
            print(f"\nExtraction Status: {result.get('extraction_status')}")
            print(f"LLM Metadata: {result.get('llm_metadata', {})}")
            
            extracted = result.get('extracted_data', {})
            print(f"\nExtracted Data Summary:")
            print(f"  - Incident SLAs: {len(extracted.get('incident_slas', []))}")
            print(f"  - Availability SLAs: {len(extracted.get('availability_slas', []))}")
            print(f"  - Service Credits: {len(extracted.get('service_credits', []))}")
            
            if len(extracted.get('incident_slas', [])) > 0:
                print("\n✓ SUCCESS: Contract extraction working!")
                return True
            else:
                print("\n⚠ WARNING: Extraction returned empty data")
                print(f"Full response: {extracted}")
                return False
                
        finally:
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"✗ Agent error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    # Load .env
    from dotenv import load_dotenv
    load_dotenv()
    
    success = asyncio.run(test_extraction())
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed! System is ready.")
    else:
        print("✗ Tests failed. Please fix the issues above.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

# Made with Bob
