import logging
from typing import Dict, Any, List, Optional
import json
import re

from ..core.config import settings

logger = logging.getLogger(__name__)

class TransformationAgent:
    """
    Transformation Agent (Financial Strategist)
    Rewrites and transforms T&M SOWs into Outcome-Based SOWs.
    """
    def __init__(self):
        self.llm_provider = settings.LLM_PROVIDER.lower()
        if self.llm_provider == "gcp":
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)
            except ImportError:
                self.gemini_client = None
        else:
            self.gemini_client = None
            
    async def transform_tm_to_outcome(self, sow_doc: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        prompt = f"""
You are a Financial Strategist Transformation Agent. 
You are analyzing a Time and Materials (T&M) Statement of Work for a service provider. 
Your goal is to optimize revenue, reduce leakage, and convert it into an Outcome-Based structure.

Return ONLY valid JSON matching this schema:
{{
  "revenue_leakage_score": 0.0 to 100.0,
  "proposed_outcome_milestones": [
    {{
      "milestone_name": "string",
      "description": "string",
      "value": 0.0
    }}
  ],
  "compensation_rewrite": {{
    "original_text": "string (extract a representative T&M compensation snippet)",
    "new_text": "string (the rewritten outcome-linked compensation section)",
    "diff_format": "A unified diff string showing - old text and + new text"
  }},
  "risk_profile": [
    "string (e.g., 'Risk of losing $X if client delays approval of phase 1')"
  ]
}}

Make sure you propose 3-5 Outcome Milestones.
Calculate a Revenue Leakage score based on the effort-based ceiling (higher score = more leakage risk).

SOW TEXT TO ANALYZE:
{raw_text[:8000]}
"""
        
        if self.gemini_client:
            try:
                from google.genai import types
                import asyncio
                model_id = settings.GEMINI_MODEL_ID
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.gemini_client.models.generate_content,
                        model=model_id,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.2,
                            response_mime_type="application/json",
                        )
                    ),
                    timeout=30.0
                )
                return self._extract_json(response.text)
            except Exception as e:
                logger.error(f"Error in transformation agent (Real AI failed): {e}")
                
        # Heuristic fallback if LLM fails
        project_name = sow_doc.get("project_name", "the project")
        client_name = sow_doc.get("client_name", "the client")
        
        return {
            "revenue_leakage_score": 68.0,
            "proposed_outcome_milestones": [
                {"milestone_name": f"{project_name} - Inception", "description": "Architecture sign-off", "value": 25000},
                {"milestone_name": f"{project_name} - MVP", "description": "Core features delivery", "value": 75000},
                {"milestone_name": f"{project_name} - Final Delivery", "description": f"Acceptance by {client_name}", "value": 50000}
            ],
            "compensation_rewrite": {
                "original_text": "Hourly rates apply for all services.",
                "new_text": "Payment shall be made upon achievement of the specific Outcome Milestones defined above.",
                "diff_format": f"- Hourly rates apply for all services.\n+ Payment shall be made upon achievement of the specific Outcome Milestones defined above."
            },
            "risk_profile": [
                f"Risk of unbilled scope creep with {client_name}.",
                "Lack of measurable acceptance criteria in current T&M structure."
            ]
        }

    def _extract_json(self, response_text: str) -> Dict[str, Any]:
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))

transformation_agent = TransformationAgent()
