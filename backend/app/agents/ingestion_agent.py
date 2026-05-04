"""
SOW Sentinel - Ingestion Agent
Parses Statement of Work documents and extracts obligations, SLAs, and penalties
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re
import logging
from pathlib import Path

from docx import Document
import pdfplumber
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import Credentials

from ..models.sow_models import (
    create_sow_document,
    create_obligation,
    create_sla_term,
    create_vague_clause,
    ObligationType,
    RiskLevel
)


logger = logging.getLogger(__name__)


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
    
    def __init__(
        self,
        watsonx_api_key: Optional[str] = None,
        watsonx_project_id: Optional[str] = None,
        watsonx_url: str = "https://us-south.ml.cloud.ibm.com",
        watsonx_model_id: str = "meta-llama/llama-3-1-70b-gptq"
    ):
        """
        Initialize the Ingestion Agent
        
        Args:
            watsonx_api_key: IBM watsonx.ai API key
            watsonx_project_id: IBM watsonx.ai project ID
        """
        self.watsonx_api_key = watsonx_api_key
        self.watsonx_project_id = watsonx_project_id
        self.watsonx_url = watsonx_url
        self.watsonx_model_id = watsonx_model_id
        self.model: Optional[ModelInference] = None
        
        if watsonx_api_key and watsonx_project_id:
            self._initialize_watsonx()
    
    def _initialize_watsonx(self):
        """Initialize watsonx.ai client."""
        try:
            credentials = Credentials(
                url=self.watsonx_url,
                api_key=self.watsonx_api_key
            )
            self.model = ModelInference(
                model_id=self.watsonx_model_id,
                credentials=credentials,
                project_id=self.watsonx_project_id,
                params={
                    GenParams.DECODING_METHOD: "greedy",
                    GenParams.MAX_NEW_TOKENS: 2048,
                    GenParams.MIN_NEW_TOKENS: 32,
                    GenParams.TEMPERATURE: 0,
                    GenParams.REPETITION_PENALTY: 1.0,
                },
            )
            logger.info("watsonx.ai model initialized for SOW ingestion")
        except Exception as exc:
            logger.exception("Failed to initialize watsonx.ai client: %s", exc)
            self.model = None
    
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
        Extract text from PDF, DOCX, DOC, or plain text file.
        """
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            extracted_pages: List[str] = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        extracted_pages.append(page_text)
            text_content = "\n\n".join(extracted_pages)
        elif suffix in {".docx", ".doc"}:
            document = Document(file_path)
            text_content = "\n".join(
                paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()
            )
        else:
            text_content = path.read_text(encoding="utf-8", errors="ignore")

        text_content = text_content.strip()
        if not text_content:
            raise ValueError(f"No text could be extracted from {path.name}")

        return text_content
    
    async def _parse_with_watsonx(self, text_content: str) -> Dict[str, Any]:
        """
        Use watsonx.ai to parse SOW text into structured data.
        Falls back to deterministic extraction if model invocation fails.
        """
        prompt = self._create_parsing_prompt(text_content)

        if self.model:
            try:
                response = self.model.generate_text(prompt=prompt)
                parsed = self._extract_json_from_response(response)
                return self._normalize_parsed_data(parsed)
            except Exception as exc:
                logger.exception("watsonx.ai parsing failed, falling back to heuristic extraction: %s", exc)

        logger.warning("Using heuristic parsing fallback because watsonx.ai output was unavailable")
        return self._heuristic_parse_text(text_content)
    
    def _create_parsing_prompt(self, text_content: str) -> str:
        """Create prompt for watsonx.ai to parse SOW."""
        return f"""
You are a senior contract risk analyst reviewing a Statement of Work for delivery, commercial, legal, and operational risk.

Return ONLY valid JSON. Do not add markdown, comments, or explanation text.

Use this exact JSON schema:
{{
  "start_date": "ISO date string or empty string",
  "end_date": "ISO date string or empty string",
  "total_value": 0,
  "currency": "USD",
  "description": "short project summary",
  "deliverables": [
    {{
      "name": "deliverable name",
      "deadline": "ISO date string or empty string",
      "description": "deliverable description",
      "penalty_amount": 0,
      "penalty_frequency": "per_day|per_hour|per_breach|one_time|unknown"
    }}
  ],
  "sla_metrics": [
    {{
      "metric_name": "metric",
      "target_value": 0,
      "unit": "hours|percentage|days|minutes|tickets|unknown",
      "measurement_period": "monthly|weekly|daily|per_incident|quarterly|unknown",
      "penalty_amount": 0
    }}
  ],
  "vague_clauses": [
    {{
      "clause": "original clause text",
      "risk": "why it is risky",
      "recommendation": "how to clarify it"
    }}
  ]
}}

Extraction requirements:
- Extract ALL meaningful vague, ambiguous, subjective, under-specified, one-sided, risky, or commercially dangerous clauses.
- Do not limit vague_clauses to style issues only. Include delivery risk, acceptance ambiguity, dependency ambiguity, resourcing ambiguity, support ambiguity, liability exposure, payment ambiguity, and change-request ambiguity.
- Capture clauses even if they are not explicitly labeled as risks.
- Prefer more coverage rather than fewer items when a clause may create delivery dispute, missed SLA, hidden scope, revenue leakage, or unbounded obligations.
- Preserve the original clause text as closely as possible.

Specifically look for clauses involving:
- reasonable efforts, best efforts, commercially reasonable efforts
- as needed, as required, where necessary, as appropriate, from time to time
- promptly, timely, without undue delay, soon as possible
- high quality, industry standard, best practice, acceptable, satisfactory
- support, assist, collaborate, coordinate, enable, maintain without measurable limits
- client dependencies, third-party dependencies, shared responsibilities, assumptions
- unclear acceptance criteria, unclear completion criteria, unclear sign-off criteria
- unlimited revisions, ongoing support, future enhancements, additional requests
- penalties, service credits, indemnities, liabilities, uncapped obligations
- terms that lack numeric thresholds, deadlines, owners, exclusions, or measurable outcomes

Rules:
- Infer dates into ISO format when possible.
- Extract numeric currency values without symbols or commas.
- If a value is missing, use empty string for strings and 0 for numbers.
- For vague_clauses, include every distinct risky clause you find, not just the top 3.
- If a clause contains measurable criteria and is not ambiguous, do not include it in vague_clauses.
- If there are 8-15 vague or risky clauses in the document, return all of them.

SOW TEXT:
{text_content}
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
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON object from model output."""
        if not response_text:
            raise ValueError("Empty response returned from watsonx.ai")

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

    def _normalize_parsed_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize model output to expected structure."""
        return {
            "start_date": parsed_data.get("start_date") or "",
            "end_date": parsed_data.get("end_date") or "",
            "total_value": self._to_number(parsed_data.get("total_value")),
            "currency": parsed_data.get("currency") or "USD",
            "description": parsed_data.get("description") or "",
            "deliverables": [
                {
                    "name": item.get("name", ""),
                    "deadline": item.get("deadline", ""),
                    "description": item.get("description", item.get("name", "")),
                    "penalty_amount": self._to_number(item.get("penalty_amount")),
                    "penalty_frequency": item.get("penalty_frequency", "unknown"),
                }
                for item in parsed_data.get("deliverables", [])
                if isinstance(item, dict)
            ],
            "sla_metrics": [
                {
                    "metric_name": item.get("metric_name", ""),
                    "target_value": self._to_number(item.get("target_value")),
                    "unit": item.get("unit", "unknown"),
                    "measurement_period": item.get("measurement_period", "unknown"),
                    "penalty_amount": self._to_number(item.get("penalty_amount")),
                }
                for item in parsed_data.get("sla_metrics", [])
                if isinstance(item, dict)
            ],
            "vague_clauses": [
                {
                    "clause": item.get("clause", ""),
                    "risk": item.get("risk", ""),
                    "recommendation": item.get("recommendation", ""),
                }
                for item in parsed_data.get("vague_clauses", [])
                if isinstance(item, dict)
            ],
        }

    def _heuristic_parse_text(self, text_content: str) -> Dict[str, Any]:
        """Fallback parser when model extraction is unavailable."""
        start_date = self._search_date(text_content, r"Start Date\s*:\s*(.+)")
        end_date = self._search_date(text_content, r"End Date\s*:\s*(.+)")
        total_value = self._search_money(text_content, r"Total Value\s*:\s*\$?([\d,]+(?:\.\d+)?)")
        description = self._search_text(text_content, r"Project\s*:\s*(.+)")
        currency = "USD"

        deliverables = []
        deliverable_pattern = re.compile(
            r"\d+\.\s*(?P<name>.+?)\n\s*Deadline:\s*(?P<deadline>.+?)\n\s*Description:\s*(?P<description>.+?)\n\s*Penalty:\s*\$?(?P<penalty>[\d,]+)(?:\s*per\s*(?P<frequency>\w+))?",
            re.IGNORECASE | re.MULTILINE,
        )
        for match in deliverable_pattern.finditer(text_content):
            deliverables.append(
                {
                    "name": match.group("name").strip(),
                    "deadline": self._coerce_date(match.group("deadline").strip()),
                    "description": match.group("description").strip(),
                    "penalty_amount": self._to_number(match.group("penalty")),
                    "penalty_frequency": f"per_{(match.group('frequency') or 'day').lower()}",
                }
            )

        sla_metrics = []
        sla_pattern = re.compile(
            r"\d+\.\s*(?P<metric>.+?):\s*(?P<target>[\d.]+)\s*(?P<unit>\w+)\n\s*Measurement:\s*(?P<period>.+?)\n\s*Penalty:\s*\$?(?P<penalty>[\d,]+)",
            re.IGNORECASE | re.MULTILINE,
        )
        for match in sla_pattern.finditer(text_content):
            sla_metrics.append(
                {
                    "metric_name": match.group("metric").strip(),
                    "target_value": self._to_number(match.group("target")),
                    "unit": match.group("unit").strip().lower(),
                    "measurement_period": match.group("period").strip().lower().replace(" ", "_"),
                    "penalty_amount": self._to_number(match.group("penalty")),
                }
            )

        vague_patterns = [
            (
                re.compile(r"\b(reasonable efforts|commercially reasonable efforts|best efforts)\b", re.IGNORECASE),
                "Subjective effort standard with no measurable baseline.",
                "Define concrete actions, timelines, and acceptance criteria instead of effort-based wording.",
            ),
            (
                re.compile(r"\b(as needed|as required|where necessary|as appropriate|from time to time)\b", re.IGNORECASE),
                "Open-ended obligation that can expand scope without clear limits.",
                "Specify exact triggers, ownership, limits, and quantity/frequency boundaries.",
            ),
            (
                re.compile(r"\b(promptly|timely|without undue delay|as soon as possible|soon)\b", re.IGNORECASE),
                "Timing commitment is vague and may create disputes over response obligations.",
                "Replace with a defined SLA or exact turnaround time.",
            ),
            (
                re.compile(r"\b(high quality|industry standard|best practice|acceptable|satisfactory)\b", re.IGNORECASE),
                "Quality standard is subjective and lacks measurable acceptance criteria.",
                "Define measurable quality metrics, review process, and sign-off standards.",
            ),
            (
                re.compile(r"\b(support|assist|collaborate|coordinate|enable|maintain)\b", re.IGNORECASE),
                "Responsibility may be too broad without defining scope, duration, or exclusions.",
                "Clarify the exact support scope, service window, owner, and exclusions.",
            ),
            (
                re.compile(r"\b(dependency|dependencies|assumption|assumptions|client to provide|provided by client|third[- ]party)\b", re.IGNORECASE),
                "Dependency or assumption risk may shift delivery responsibility without clear accountability.",
                "List each dependency, responsible party, due date, and impact if not met.",
            ),
            (
                re.compile(r"\b(acceptance|sign-?off|complete(?:d|ion)? criteria)\b", re.IGNORECASE),
                "Acceptance process may be unclear or missing objective completion standards.",
                "Define acceptance tests, reviewer, review period, and auto-acceptance conditions.",
            ),
            (
                re.compile(r"\b(unlimited|ongoing|future enhancements|additional requests|change request)\b", re.IGNORECASE),
                "Potential scope-creep language without commercial or delivery controls.",
                "Add change-control process, pricing guardrails, approval flow, and out-of-scope boundaries.",
            ),
            (
                re.compile(r"\b(indemnif|liab(?:ility)?|penalt(?:y|ies)|service credit)\b", re.IGNORECASE),
                "Commercial exposure may be one-sided or uncapped.",
                "Clarify caps, exclusions, triggering events, and aggregate liability limits.",
            ),
        ]

        vague_clauses = []
        seen_clauses = set()
        for raw_line in text_content.splitlines():
            normalized_line = re.sub(r"\s+", " ", raw_line).strip(" \t-•*")
            if len(normalized_line) < 20:
                continue

            for pattern, risk, recommendation in vague_patterns:
                if pattern.search(normalized_line):
                    dedupe_key = normalized_line.lower()
                    if dedupe_key in seen_clauses:
                        break
                    seen_clauses.add(dedupe_key)
                    vague_clauses.append(
                        {
                            "clause": normalized_line,
                            "risk": risk,
                            "recommendation": recommendation,
                        }
                    )
                    break

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_value": total_value,
            "currency": currency,
            "description": description,
            "deliverables": deliverables,
            "sla_metrics": sla_metrics,
            "vague_clauses": vague_clauses,
        }

    def _search_text(self, text_content: str, pattern: str) -> str:
        match = re.search(pattern, text_content, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _search_money(self, text_content: str, pattern: str) -> float:
        match = re.search(pattern, text_content, re.IGNORECASE)
        return self._to_number(match.group(1)) if match else 0

    def _search_date(self, text_content: str, pattern: str) -> str:
        match = re.search(pattern, text_content, re.IGNORECASE)
        return self._coerce_date(match.group(1).strip()) if match else ""

    def _coerce_date(self, raw_value: str) -> str:
        raw_value = raw_value.strip()
        for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(raw_value, fmt).date().isoformat()
            except ValueError:
                continue
        return raw_value

    def _to_number(self, value: Any) -> float:
        if value is None:
            return 0
        if isinstance(value, (int, float)):
            return float(value)
        cleaned = re.sub(r"[^\d.]", "", str(value))
        if not cleaned:
            return 0
        try:
            return float(cleaned)
        except ValueError:
            return 0

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