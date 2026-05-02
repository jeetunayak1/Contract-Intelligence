"""
SOW Sentinel - Ingestion Agent
Parses Statement of Work documents and extracts obligations, SLAs, and penalties
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re
from pathlib import Path

# Placeholder for watsonx.ai integration
# from ibm_watsonx_ai import Credentials, APIClient
# from ibm_watsonx_ai.foundation_models import Model

from ..models.sow_models import (
    create_sow_document,
    create_obligation,
    create_sla_term,
    create_vague_clause,
    ObligationType,
    RiskLevel
)


class IngestionAgent:
    """
    The Ingestion Agent (The Reader)
    
    Responsibilities:
    1. Parse PDF/DOCX SOW documents
    2. Extract obligations (deliverables, milestones, SLAs)
    3. Identify financial penalties and liquidated damages
    4. Detect vague clauses that pose risks
    5. Score risk levels for each obligation
    """
    
    def __init__(self, watsonx_api_key: Optional[str] = None, watsonx_project_id: Optional[str] = None):
        """
        Initialize the Ingestion Agent
        
        Args:
            watsonx_api_key: IBM watsonx.ai API key
            watsonx_project_id: IBM watsonx.ai project ID
        """
        self.watsonx_api_key = watsonx_api_key
        self.watsonx_project_id = watsonx_project_id
        self.model = None
        
        # Initialize watsonx.ai client if credentials provided
        if watsonx_api_key and watsonx_project_id:
            self._initialize_watsonx()
    
    def _initialize_watsonx(self):
        """Initialize watsonx.ai client"""
        # TODO: Implement watsonx.ai initialization
        # credentials = Credentials(
        #     url="https://us-south.ml.cloud.ibm.com",
        #     api_key=self.watsonx_api_key
        # )
        # self.model = Model(
        #     model_id="ibm/granite-13b-chat-v2",
        #     credentials=credentials,
        #     project_id=self.watsonx_project_id
        # )
        pass
    
    async def parse_sow_document(
        self,
        file_path: str,
        sow_number: str,
        client_name: str,
        project_name: str
    ) -> Dict[str, Any]:
        """
        Parse a SOW document and extract all relevant information
        
        Args:
            file_path: Path to SOW file (PDF/DOCX)
            sow_number: Unique SOW identifier
            client_name: Client name
            project_name: Project name
            
        Returns:
            Parsed SOW document with obligations, SLAs, and risks
        """
        # Step 1: Extract text from document
        text_content = await self._extract_text(file_path)
        
        # Step 2: Use watsonx.ai to parse structured data
        parsed_data = await self._parse_with_watsonx(text_content)
        
        # Step 3: Extract obligations
        obligations = await self._extract_obligations(parsed_data, sow_number)
        
        # Step 4: Extract SLA terms
        sla_terms = await self._extract_sla_terms(parsed_data, sow_number)
        
        # Step 5: Detect vague clauses
        vague_clauses = await self._detect_vague_clauses(parsed_data, sow_number)
        
        # Step 6: Calculate financial summary
        financial_summary = self._calculate_financial_summary(obligations, sla_terms)
        
        # Step 7: Create SOW document
        sow_doc = create_sow_document(
            sow_number=sow_number,
            client_name=client_name,
            project_name=project_name,
            start_date=parsed_data.get("start_date", datetime.utcnow().isoformat()),
            end_date=parsed_data.get("end_date", datetime.utcnow().isoformat()),
            total_value=parsed_data.get("total_value", 0),
            currency=parsed_data.get("currency", "USD"),
            description=parsed_data.get("description"),
            obligations=obligations,
            sla_terms=sla_terms,
            vague_clauses=vague_clauses,
            financial_summary=financial_summary,
            file_url=file_path,
            file_name=Path(file_path).name,
            parsed_at=datetime.utcnow().isoformat()
        )
        
        return sow_doc
    
    async def _extract_text(self, file_path: str) -> str:
        """
        Extract text from PDF or DOCX file
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text content
        """
        # TODO: Implement PDF/DOCX text extraction
        # For now, return placeholder
        return """
        STATEMENT OF WORK
        
        Project: Enterprise Platform Migration
        Client: Acme Corporation
        Start Date: January 1, 2024
        End Date: December 31, 2024
        Total Value: $500,000
        
        DELIVERABLES:
        
        1. Phase 1: Database Migration
           Deadline: March 31, 2024
           Description: Migrate all legacy databases to cloud infrastructure
           Penalty: $5,000 per day after deadline
           
        2. Phase 2: Application Modernization
           Deadline: June 30, 2024
           Description: Refactor applications to microservices architecture
           Penalty: $3,000 per day after deadline
           
        3. UAT Sign-off Document
           Deadline: May 15, 2024
           Description: Complete User Acceptance Testing documentation
           Penalty: $1,000 per day after deadline
           
        SLA REQUIREMENTS:
        
        1. Incident Response Time: 4 hours
           Measurement: Monthly average
           Penalty: $1,000 per breach
           
        2. System Uptime: 99.9%
           Measurement: Monthly
           Penalty: $2,000 per 0.1% below target
           
        3. Resolution Time: 24 hours for critical issues
           Measurement: Per incident
           Penalty: $500 per hour over target
           
        SUPPORT:
        Reasonable efforts will be made to optimize performance.
        Best practices will be followed for security implementation.
        """
    
    async def _parse_with_watsonx(self, text_content: str) -> Dict[str, Any]:
        """
        Use watsonx.ai to parse SOW text into structured data
        
        Args:
            text_content: Raw text from SOW
            
        Returns:
            Structured data dictionary
        """
        if self.model:
            # TODO: Implement actual watsonx.ai parsing
            prompt = self._create_parsing_prompt(text_content)
            # response = self.model.generate(prompt)
            # return json.loads(response)
            pass
        
        # Demo mode: Return structured data
        return {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "total_value": 500000,
            "currency": "USD",
            "description": "Enterprise Platform Migration",
            "deliverables": [
                {
                    "name": "Phase 1: Database Migration",
                    "deadline": "2024-03-31",
                    "description": "Migrate all legacy databases to cloud infrastructure",
                    "penalty_amount": 5000,
                    "penalty_frequency": "per_day"
                },
                {
                    "name": "Phase 2: Application Modernization",
                    "deadline": "2024-06-30",
                    "description": "Refactor applications to microservices architecture",
                    "penalty_amount": 3000,
                    "penalty_frequency": "per_day"
                },
                {
                    "name": "UAT Sign-off Document",
                    "deadline": "2024-05-15",
                    "description": "Complete User Acceptance Testing documentation",
                    "penalty_amount": 1000,
                    "penalty_frequency": "per_day"
                }
            ],
            "sla_metrics": [
                {
                    "metric_name": "Incident Response Time",
                    "target_value": 4,
                    "unit": "hours",
                    "measurement_period": "monthly",
                    "penalty_amount": 1000
                },
                {
                    "metric_name": "System Uptime",
                    "target_value": 99.9,
                    "unit": "percentage",
                    "measurement_period": "monthly",
                    "penalty_amount": 2000
                },
                {
                    "metric_name": "Resolution Time",
                    "target_value": 24,
                    "unit": "hours",
                    "measurement_period": "per_incident",
                    "penalty_amount": 500
                }
            ],
            "vague_clauses": [
                {
                    "clause": "Reasonable efforts will be made to optimize performance",
                    "risk": "Undefined success criteria - no specific performance metrics",
                    "recommendation": "Request specific performance benchmarks (e.g., response time < 200ms)"
                },
                {
                    "clause": "Best practices will be followed for security implementation",
                    "risk": "Ambiguous security requirements",
                    "recommendation": "Define specific security standards (e.g., OWASP Top 10, SOC 2)"
                }
            ]
        }
    
    def _create_parsing_prompt(self, text_content: str) -> str:
        """Create prompt for watsonx.ai to parse SOW"""
        return f"""
        You are an expert contract analyst. Parse the following Statement of Work (SOW) and extract:
        
        1. Basic Information:
           - Start date
           - End date
           - Total contract value
           - Currency
           - Project description
        
        2. Deliverables and Milestones:
           - Name/description
           - Deadline
           - Penalty amount and frequency
           - Risk level (critical/high/medium/low)
        
        3. SLA Metrics:
           - Metric name
           - Target value
           - Unit of measurement
           - Measurement period
           - Penalty amount
        
        4. Vague Clauses:
           - Identify any ambiguous or undefined terms
           - Explain the risk
           - Provide recommendations
        
        Return the data as a JSON object.
        
        SOW TEXT:
        {text_content}
        
        JSON OUTPUT:
        """
    
    async def _extract_obligations(
        self,
        parsed_data: Dict[str, Any],
        sow_id: str
    ) -> List[Dict[str, Any]]:
        """Extract obligations from parsed data"""
        obligations = []
        
        for deliverable in parsed_data.get("deliverables", []):
            # Assess risk level based on penalty amount
            penalty = deliverable.get("penalty_amount", 0)
            if penalty >= 5000:
                risk_level = RiskLevel.CRITICAL.value
            elif penalty >= 3000:
                risk_level = RiskLevel.HIGH.value
            elif penalty >= 1000:
                risk_level = RiskLevel.MEDIUM.value
            else:
                risk_level = RiskLevel.LOW.value
            
            obligation = create_obligation(
                sow_id=sow_id,
                obligation_type=ObligationType.DELIVERABLE.value,
                description=deliverable.get("description", ""),
                deadline=deliverable.get("deadline", ""),
                penalty_amount=penalty,
                penalty_frequency=deliverable.get("penalty_frequency", "per_day"),
                risk_level=risk_level,
                status="not_started",
                progress_percentage=0
            )
            obligations.append(obligation)
        
        return obligations
    
    async def _extract_sla_terms(
        self,
        parsed_data: Dict[str, Any],
        sow_id: str
    ) -> List[Dict[str, Any]]:
        """Extract SLA terms from parsed data"""
        sla_terms = []
        
        for metric in parsed_data.get("sla_metrics", []):
            sla_term = create_sla_term(
                sow_id=sow_id,
                metric_name=metric.get("metric_name", ""),
                target_value=metric.get("target_value", 0),
                unit=metric.get("unit", ""),
                measurement_period=metric.get("measurement_period", ""),
                penalty_amount=metric.get("penalty_amount", 0)
            )
            sla_terms.append(sla_term)
        
        return sla_terms
    
    async def _detect_vague_clauses(
        self,
        parsed_data: Dict[str, Any],
        sow_id: str
    ) -> List[Dict[str, Any]]:
        """Detect and flag vague clauses"""
        vague_clauses = []
        
        for clause in parsed_data.get("vague_clauses", []):
            vague_clause = create_vague_clause(
                sow_id=sow_id,
                clause_text=clause.get("clause", ""),
                risk_description=clause.get("risk", ""),
                recommendation=clause.get("recommendation"),
                severity=RiskLevel.MEDIUM.value
            )
            vague_clauses.append(vague_clause)
        
        return vague_clauses
    
    def _calculate_financial_summary(
        self,
        obligations: List[Dict[str, Any]],
        sla_terms: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate financial summary"""
        total_penalties = sum(
            obl.get("penalty_amount", 0) for obl in obligations
        )
        total_penalties += sum(
            sla.get("penalty_amount", 0) for sla in sla_terms
        )
        
        return {
            "total_penalties_at_risk": total_penalties,
            "penalties_avoided": 0,
            "scope_creep_value": 0,
            "margin_protected": 0,
            "high_risk_obligations": len([
                o for o in obligations 
                if o.get("risk_level") in [RiskLevel.CRITICAL.value, RiskLevel.HIGH.value]
            ])
        }
    
    async def quick_risk_assessment(self, sow_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform quick risk assessment on parsed SOW
        
        Args:
            sow_doc: Parsed SOW document
            
        Returns:
            Risk assessment summary
        """
        obligations = sow_doc.get("obligations", [])
        financial_summary = sow_doc.get("financial_summary", {})
        
        # Calculate risk score (0-100)
        high_risk_count = financial_summary.get("high_risk_obligations", 0)
        total_penalties = financial_summary.get("total_penalties_at_risk", 0)
        
        risk_score = min(100, (high_risk_count * 20) + (total_penalties / 1000))
        
        return {
            "risk_score": risk_score,
            "risk_level": "critical" if risk_score >= 80 else "high" if risk_score >= 60 else "medium",
            "total_obligations": len(obligations),
            "high_risk_obligations": high_risk_count,
            "total_penalty_exposure": total_penalties,
            "vague_clauses_count": len(sow_doc.get("vague_clauses", [])),
            "recommendations": [
                "Schedule immediate review for high-risk obligations",
                "Clarify vague clauses with client",
                "Set up automated monitoring for all deadlines"
            ]
        }


# Made with Bob - SOW Sentinel