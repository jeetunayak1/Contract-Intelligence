"""
Contract Intelligence Agent using LangGraph
Extracts and categorizes SLA obligations into compliance, risk, and liability buckets
Supports multi-agent downstream processing (Compliance Agent, Risk Agent, Liability Agent)
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from app.core.config import settings
from app.models.contract_models import ExtractedContract, ContractMetadata
from app.prompts.contract_extraction_prompt import get_extraction_prompt

logger = logging.getLogger(__name__)


class ContractAgentError(Exception):
    """Custom exception for Contract Agent errors"""
    pass


class AgentState(TypedDict):
    """State for Contract Intelligence Agent"""
    contract_text: str
    contract_id: str
    filename: str
    extracted_json: Optional[str]
    parsed_data: Optional[Dict[str, Any]]
    error: Optional[str]
    retry_count: int


class ContractIntelligenceAgent:
    """
    LangGraph-based agent for contract intelligence extraction with categorized obligations.
    
    Extracts contract obligations into three categories:
    1. Compliance Obligations: Operational SLAs, KPIs, governance rules, escalation procedures
    2. Risk Obligations: Service credits, financial caps, commercial penalties, revenue controls
    3. Liability Obligations: Liability exclusions, client obligations, termination clauses, legal constraints
    
    This categorization enables downstream multi-agent processing:
    - Compliance Agent consumes compliance_obligations
    - Risk Agent consumes risk_obligations
    - Liability Agent consumes liability_obligations
    """
    
    def __init__(self):
        """Initialize the Contract Intelligence Agent"""
        try:
            # Initialize LLM
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL_ID,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.0,  # Deterministic for structured extraction
                max_output_tokens=8192,
                convert_system_message_to_human=True  # Required for Gemini API
            )
            
            # Build agent graph
            self.graph = self._build_graph()
            
            logger.info("Contract Intelligence Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Contract Intelligence Agent: {e}")
            raise ContractAgentError(f"Agent initialization failed: {str(e)}")
    
    def _build_graph(self) -> StateGraph:
        """
        Build LangGraph workflow for contract extraction
        
        Returns:
            Compiled StateGraph
        """
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("extract", self._extract_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("retry", self._retry_node)
        
        # Set entry point
        workflow.set_entry_point("extract")
        
        # Add edges
        workflow.add_conditional_edges(
            "extract",
            self._should_validate,
            {
                "validate": "validate",
                "retry": "retry",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "validate",
            self._should_retry,
            {
                "retry": "retry",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "retry",
            self._should_extract,
            {
                "extract": "extract",
                "end": END
            }
        )
        
        return workflow.compile()
    
    def _extract_node(self, state: AgentState) -> AgentState:
        """
        Extract structured data from contract text
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with extracted JSON
        """
        try:
            logger.info(f"Extracting data from contract {state['contract_id']}")
            
            # Get prompts
            system_prompt, user_prompt = get_extraction_prompt(state['contract_text'])
            
            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # Invoke LLM
            response = self.llm.invoke(messages)
            
            # Log raw response for debugging
            logger.info(f"LLM Response length: {len(response.content)} chars")
            logger.debug(f"LLM Raw response (first 500 chars): {response.content[:500]}")
            
            # Extract JSON from response
            extracted_json = self._extract_json_from_response(response.content)
            
            # Log extracted JSON for debugging
            logger.info(f"Extracted JSON length: {len(extracted_json)} chars")
            logger.debug(f"Extracted JSON (first 500 chars): {extracted_json[:500]}")
            
            state['extracted_json'] = extracted_json
            logger.info(f"Successfully extracted JSON for contract {state['contract_id']}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error in extract node: {e}")
            state['error'] = str(e)
            return state
    
    def _validate_node(self, state: AgentState) -> AgentState:
        """
        Validate and parse extracted JSON
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with parsed data
        """
        try:
            logger.info(f"Validating extracted data for contract {state['contract_id']}")
            
            if not state['extracted_json']:
                raise ValueError("No JSON data to validate")
            
            # Parse JSON
            parsed_data = json.loads(state['extracted_json'])
            
            # Validate with Pydantic model
            extracted_contract = ExtractedContract(**parsed_data)
            
            # Store validated data
            state['parsed_data'] = extracted_contract.model_dump()
            state['error'] = None
            
            logger.info(f"Successfully validated data for contract {state['contract_id']}")
            
            return state
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            state['error'] = f"Invalid JSON: {str(e)}"
            return state
        except Exception as e:
            logger.error(f"Validation error: {e}")
            state['error'] = f"Validation failed: {str(e)}"
            return state
    
    def _retry_node(self, state: AgentState) -> AgentState:
        """
        Handle retry logic
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with incremented retry count
        """
        state['retry_count'] += 1
        logger.warning(
            f"Retrying extraction for contract {state['contract_id']} "
            f"(attempt {state['retry_count']})"
        )
        return state
    
    def _should_validate(self, state: AgentState) -> str:
        """
        Determine if extraction was successful and should proceed to validation
        
        Args:
            state: Current agent state
            
        Returns:
            Next node name
        """
        if state.get('error'):
            if state['retry_count'] < 3:
                return "retry"
            return "end"
        
        if state.get('extracted_json'):
            return "validate"
        
        return "end"
    
    def _should_retry(self, state: AgentState) -> str:
        """
        Determine if validation failed and should retry
        
        Args:
            state: Current agent state
            
        Returns:
            Next node name
        """
        if state.get('error') and state['retry_count'] < 3:
            return "retry"
        return "end"
    
    def _should_extract(self, state: AgentState) -> str:
        """
        Determine if should retry extraction
        
        Args:
            state: Current agent state
            
        Returns:
            Next node name
        """
        if state['retry_count'] < 3:
            return "extract"
        return "end"
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """
        Extract JSON from LLM response, handling markdown code blocks
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Clean JSON string
        """
        # Remove markdown code blocks if present
        text = response_text.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        return text.strip()
    
    async def extract_contract(
        self,
        contract_text: str,
        filename: str,
        contract_id: Optional[str] = None
    ) -> ExtractedContract:
        """
        Extract structured data from contract text
        
        Args:
            contract_text: Raw contract text
            filename: Original filename
            contract_id: Optional contract ID (generated if not provided)
            
        Returns:
            ExtractedContract with all SLA data
            
        Raises:
            ContractAgentError: If extraction fails
        """
        try:
            # Generate contract ID if not provided
            if not contract_id:
                contract_id = f"contract_{uuid.uuid4().hex[:12]}"
            
            # Initialize state
            initial_state: AgentState = {
                "contract_text": contract_text,
                "contract_id": contract_id,
                "filename": filename,
                "extracted_json": None,
                "parsed_data": None,
                "error": None,
                "retry_count": 0
            }
            
            # Run agent graph
            final_state = self.graph.invoke(initial_state)
            
            # Check for errors
            if final_state.get('error'):
                raise ContractAgentError(
                    f"Extraction failed after {final_state['retry_count']} attempts: "
                    f"{final_state['error']}"
                )
            
            # Check for parsed data
            if not final_state.get('parsed_data'):
                raise ContractAgentError("No data extracted from contract")
            
            # Create ExtractedContract object
            extracted_contract = ExtractedContract(**final_state['parsed_data'])
            
            logger.info(f"Successfully extracted contract {contract_id}")
            return extracted_contract
            
        except Exception as e:
            logger.error(f"Contract extraction failed: {e}")
            raise ContractAgentError(f"Failed to extract contract: {str(e)}")


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
    """
    Reset the singleton agent instance.
    Call this after code updates to force reload.
    """
    global _contract_agent
    _contract_agent = None
    logger.info("Contract Intelligence Agent reset")


# Made with Bob