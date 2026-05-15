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
        """Create extraction prompt for LLM with CATEGORIZED schema"""
        # Import the prompt from the centralized location
        from app.prompts.contract_extraction_prompt import get_extraction_prompt
        system_prompt, user_prompt = get_extraction_prompt(contract_text)
        # Combine for this agent's format
        return f"{system_prompt}\n\n{user_prompt}"
    
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


def get_contract_agent(force_reload: bool = False) -> ContractIntelligenceAgent:
    """
    Get or create Contract Intelligence Agent singleton
    
    Args:
        force_reload: Force creation of new agent instance (useful after code updates)
    
    Returns:
        ContractIntelligenceAgent instance
    """
    global _contract_agent
    if _contract_agent is None or force_reload:
        _contract_agent = ContractIntelligenceAgent()
        logger.info("Contract Intelligence Agent initialized/reloaded")
    return _contract_agent


def reset_contract_agent():
    """Reset the singleton agent instance"""
    global _contract_agent
    _contract_agent = None
    logger.info("Contract Intelligence Agent reset")


# Made with Bob