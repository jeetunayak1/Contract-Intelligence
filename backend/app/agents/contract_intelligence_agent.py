"""
Contract Intelligence Agent
Extracts SLA obligations and compliance rules from SOW contracts
"""
import os
import json
import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from google import genai
from google.genai import types

from ..utils.document_parser import DocumentParser
from ..models.contract_models import ExtractedContract

logger = logging.getLogger(__name__)


class ContractIntelligenceAgent:
    """
    Contract Intelligence Agent for extracting SLA obligations
    """
    
    def __init__(self):
        """Initialize the Contract Intelligence Agent"""
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.gemini_model_id = os.getenv("GEMINI_MODEL_ID", "gemini-1.5-pro")
        self.gemini_client = None
        
        if self.google_api_key:
            self._initialize_gemini()
        else:
            logger.warning("GOOGLE_API_KEY not set. Agent will use fallback extraction.")
    
    def _initialize_gemini(self):
        """Initialize Google GenAI client"""
        try:
            self.gemini_client = genai.Client(api_key=self.google_api_key)
            logger.info(f"Gemini client initialized with model: {self.gemini_model_id}")
        except Exception as exc:
            logger.exception(f"Failed to initialize Gemini client: {exc}")
            self.gemini_client = None
    
    async def extract_contract(
        self,
        file_path: str,
        filename: str,
        contract_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract contract SLA obligations from document
        
        Args:
            file_path: Path to contract file
            filename: Original filename
            contract_id: Optional contract ID
            
        Returns:
            Extracted contract data with metadata
        """
        if not contract_id:
            contract_id = f"contract_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"Starting extraction for contract: {filename}")
        
        # Extract text from document
        file_content = open(file_path, 'rb').read()
        raw_text, file_type = DocumentParser.parse_file(file_content, filename)
        
        logger.info(f"Extracted {len(raw_text)} characters from {file_type} file")
        
        # Extract structured data using LLM
        extracted_data, llm_metadata = await self._extract_with_llm(raw_text)
        
        logger.info(f"LLM extraction completed. Method: {llm_metadata.get('method', 'unknown')}")
        
        # Validate and create response
        try:
            validated_contract = ExtractedContract(**extracted_data)
            
            return {
                "contract_id": contract_id,
                "filename": filename,
                "raw_text": raw_text,
                "extracted_data": validated_contract.model_dump(),
                "file_type": file_type,
                "file_size_bytes": len(file_content),
                "processed_at": datetime.utcnow().isoformat(),
                "extraction_status": "completed",
                "llm_metadata": llm_metadata
            }
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            return {
                "contract_id": contract_id,
                "filename": filename,
                "raw_text": raw_text,
                "extracted_data": extracted_data,
                "file_type": file_type,
                "file_size_bytes": len(file_content),
                "processed_at": datetime.utcnow().isoformat(),
                "extraction_status": "completed_with_warnings",
                "error_message": str(e),
                "llm_metadata": llm_metadata
            }
    
    async def _extract_with_llm(self, contract_text: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Extract structured data using Gemini LLM
        
        Returns:
            Tuple of (extracted_data, llm_metadata)
        """
        
        llm_metadata = {
            "model": self.gemini_model_id,
            "method": "unknown",
            "success": False,
            "error": None
        }
        
        if not self.gemini_client:
            logger.error("Gemini client not initialized. Check GOOGLE_API_KEY.")
            llm_metadata["method"] = "none"
            llm_metadata["error"] = "GOOGLE_API_KEY not set"
            raise Exception("LLM not available. Please set GOOGLE_API_KEY in .env file")
        
        prompt = self._create_extraction_prompt(contract_text)
        
        try:
            logger.info(f"Calling Gemini API with model: {self.gemini_model_id}")
            logger.info(f"Contract text length: {len(contract_text)} characters")
            
            import asyncio
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.gemini_client.models.generate_content,
                    model=self.gemini_model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0,
                        response_mime_type="application/json",
                    )
                ),
                timeout=300.0  # Increased to 300 seconds for large documents
            )
            
            response_text = getattr(response, "text", "") or ""
            
            logger.info(f"Received response from Gemini: {len(response_text)} characters")
            logger.debug(f"Response preview: {response_text[:500]}")
            
            if not response_text:
                raise Exception("Empty response from Gemini")
            
            parsed = self._extract_json_from_response(response_text)
            
            llm_metadata["method"] = "gemini"
            llm_metadata["success"] = True
            llm_metadata["response_length"] = len(response_text)
            
            logger.info("Successfully extracted contract data using Gemini")
            return parsed, llm_metadata
            
        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}", exc_info=True)
            llm_metadata["method"] = "failed"
            llm_metadata["error"] = str(e)
            raise Exception(f"LLM extraction failed: {str(e)}")
    
    def _create_extraction_prompt(self, contract_text: str) -> str:
        """Create extraction prompt for LLM"""
        return f"""You are a Contract Intelligence Agent. Your task is to extract EVERY SINGLE SLA obligation, service credit, and compliance rule from the contract.

CRITICAL: Extract ALL priorities (P1, P2, P3, P4, P5), ALL tiers, ALL service credits, ALL availability targets.
Do NOT skip any data. If a table has 4 rows, extract all 4 rows. If there are service credits for P1-P4, extract all 4.

Return ONLY valid JSON. No markdown, no explanations, no summaries.

Extract into this exact schema:

{{
  "contract_metadata": {{
    "contract_id": null,
    "client_name": "extract from contract",
    "provider_name": "extract from contract",
    "effective_date": "YYYY-MM-DD or null",
    "end_date": "YYYY-MM-DD or null",
    "contract_period_years": null,
    "contract_value": null,
    "currency": "USD"
  }},
  "incident_slas": [
    {{
      "priority": "P1|P2|P3|P4|P5",
      "acknowledge_minutes": 15,
      "workaround_hours": 2.0,
      "resolution_hours": 4.0,
      "rca_deadline_hours": 24,
      "availability_window": "24x7x365"
    }}
    // EXTRACT ALL PRIORITIES - if contract has P1, P2, P3, P4, create 4 entries
  ],
  "availability_slas": [
    {{
      "tier": "Tier 1 - Mission Critical",
      "target_uptime_percent": 99.9,
      "max_downtime_minutes": 43.8,
      "measurement_tool": "Datadog",
      "measurement_period": "Monthly"
    }}
    // EXTRACT ALL TIERS - if contract has Tier 1, Tier 2, Tier 3, create 3 entries
  ],
  "quality_kpis": [
    {{
      "metric": "Unit Test Coverage",
      "target_percent": 80.0,
      "target_value": null,
      "measurement_frequency": "Per Sprint"
    }}
    // EXTRACT ALL KPIs from tables
  ],
  "service_credits": [
    {{
      "priority": "P1",
      "breach_condition": "Resolution time exceeds 4 hours",
      "credit_percent": 2.0,
      "monthly_cap_percent": 10.0,
      "calculation_method": "Per incident"
    }}
    // EXTRACT ALL SERVICE CREDITS - if table shows P1, P2, P3, P4 credits, create 4 entries
    // Look for "Service Credit Schedule" tables
  ],
  "liability_exclusions": [
    "extract_all_exclusions_from_contract"
    // Extract from "Out of Scope" or "Exclusions" sections
  ],
  "governance_rules": [
    {{
      "meeting": "Weekly Operations Review",
      "frequency": "Weekly",
      "participants": ["Client PM", "Provider PM"],
      "deliverables": ["Status Report"]
    }}
    // EXTRACT ALL governance meetings
  ],
  "escalation_matrix": [
    {{
      "level": "L1",
      "trigger": "Issue not resolved within SLA",
      "response_sla": "Same Business Day",
      "contact_role": "Operations Manager"
    }}
    // EXTRACT ALL escalation levels
  ]
}}

EXTRACTION INSTRUCTIONS:

1. INCIDENT SLAs:
   - Look for "Response & Resolution Time SLAs" or "Incident Priority Definitions" tables
   - Extract EVERY priority level (P1, P2, P3, P4, P5)
   - Include acknowledge time, workaround time, resolution time, RCA deadline
   - Convert "Business Hours" to hours, "Business Days" to hours (8 hours/day)

2. AVAILABILITY SLAs:
   - Look for "System Availability SLAs" or "Uptime Targets" tables
   - Extract ALL tiers (Tier 1, Tier 2, Tier 3, Production, Non-Production, etc.)
   - Include target percentage, max downtime, measurement tools
   - If percentage is missing but tier exists, set target_uptime_percent to null

3. SERVICE CREDITS:
   - Look for "Service Credit Schedule" or "SLA Breach" tables
   - Extract EVERY row from the table
   - Include priority, breach condition, credit percentage, monthly cap
   - Look for both Incident SLA breaches AND Availability SLA breaches

4. QUALITY KPIs:
   - Look for "Quality Gate KPIs" or "Development Tower" metrics
   - Extract ALL metrics from tables
   - Include metric name, target percentage/value, measurement frequency

5. LIABILITY EXCLUSIONS:
   - Look for "Out of Scope", "Exclusions", "Not Included" sections
   - Extract ALL items as a list of strings
   - Use snake_case format (e.g., "third_party_software_procurement")

NORMALIZATION RULES:
- Time: "15 minutes" → 15, "2 hours" → 2.0, "4 Business Hours" → 4, "5 Business Days" → 40
- Percentages: "99.9%" → 99.9, "80%" → 80.0
- Priorities: "Critical" → "P1", "High" → "P2", "Medium" → "P3", "Low" → "P4"
- Missing data: Use null, not empty string

CRITICAL: Do NOT summarize or skip rows. If a table has 10 rows, extract all 10 rows.

CONTRACT TEXT:
{contract_text[:12000]}
"""
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        cleaned = response_text.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find JSON object in response
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise
    


# Singleton instance
_contract_agent: Optional[ContractIntelligenceAgent] = None


def get_contract_agent() -> ContractIntelligenceAgent:
    """Get or create Contract Intelligence Agent singleton"""
    global _contract_agent
    if _contract_agent is None:
        _contract_agent = ContractIntelligenceAgent()
    return _contract_agent


# Made with Bob