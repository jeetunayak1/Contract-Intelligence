"""
CrewAI Tasks for Autonomous Compliance Monitoring
Defines tasks for compliance analysis, resolution, and reporting
"""
from typing import Dict, Any
from crewai import Task


def create_compliance_analysis_task(
    incident_data: Dict[str, Any],
    contract_data: Dict[str, Any]
) -> Task:
    """
    Task: Analyze incident against SLA obligations
    
    Evaluates:
    - Resolution time vs SLA target
    - Acknowledge time vs SLA target
    - Workaround time vs SLA target
    - Availability impact
    - Financial exposure
    """
    return Task(
        description=f"""
        Analyze incident {incident_data.get('incident_id')} for SLA compliance.
        
        Incident Details:
        - Priority: {incident_data.get('priority')}
        - Service: {incident_data.get('service')}
        - Title: {incident_data.get('title')}
        - Status: {incident_data.get('status')}
        
        Contract SLA Obligations:
        - Incident SLAs: {len(contract_data.get('incident_slas', []))} defined
        - Availability SLAs: {len(contract_data.get('availability_slas', []))} defined
        - Service Credits: {len(contract_data.get('service_credits', []))} defined
        
        Your Task:
        1. Match incident priority to contract SLA obligations
        2. Calculate time elapsed since incident creation
        3. Determine if SLA breach has occurred or is imminent
        4. Calculate potential financial exposure
        5. Check for liability exclusions
        6. Generate detailed reasoning for each decision
        
        Output Format:
        {{
            "breach_detected": boolean,
            "breach_type": "resolution_time|acknowledge_time|workaround_time",
            "sla_target_hours": float,
            "actual_hours": float,
            "financial_exposure": float,
            "reasoning": "detailed explanation"
        }}
        """,
        expected_output="JSON object with compliance analysis results",
        agent=None  # Will be set by crew
    )


def create_liability_check_task(
    incident_data: Dict[str, Any],
    contract_data: Dict[str, Any],
    breach_analysis: Dict[str, Any]
) -> Task:
    """
    Task: Check if liability exclusions apply
    
    Evaluates:
    - Root cause analysis
    - Exclusion clause matching
    - Penalty waiver eligibility
    """
    return Task(
        description=f"""
        Check liability exclusions for incident {incident_data.get('incident_id')}.
        
        Breach Analysis:
        - Breach Detected: {breach_analysis.get('breach_detected')}
        - Financial Exposure: ${breach_analysis.get('financial_exposure', 0):,.2f}
        
        Contract Liability Exclusions:
        {contract_data.get('liability_exclusions', [])}
        
        Your Task:
        1. Analyze incident root cause
        2. Match root cause against liability exclusions
        3. Determine if penalty waiver applies
        4. Calculate adjusted financial exposure
        5. Generate reasoning for waiver decision
        
        Output Format:
        {{
            "exclusion_applies": boolean,
            "matched_exclusion": "exclusion_name",
            "waiver_reason": "detailed explanation",
            "adjusted_exposure": float,
            "confidence": float
        }}
        """,
        expected_output="JSON object with liability analysis results",
        agent=None
    )


def create_financial_impact_task(
    incident_data: Dict[str, Any],
    contract_data: Dict[str, Any],
    compliance_result: Dict[str, Any],
    liability_result: Dict[str, Any]
) -> Task:
    """
    Task: Calculate comprehensive financial impact
    
    Calculates:
    - Service credits
    - Penalty amounts
    - Monthly exposure
    - Cumulative risk
    """
    return Task(
        description=f"""
        Calculate financial impact for incident {incident_data.get('incident_id')}.
        
        Compliance Analysis:
        - Breach: {compliance_result.get('breach_detected')}
        - Exposure: ${compliance_result.get('financial_exposure', 0):,.2f}
        
        Liability Analysis:
        - Waiver: {liability_result.get('exclusion_applies')}
        - Adjusted: ${liability_result.get('adjusted_exposure', 0):,.2f}
        
        Your Task:
        1. Calculate service credit percentage
        2. Apply monthly cap limits
        3. Calculate net financial exposure
        4. Estimate cumulative monthly risk
        5. Generate financial summary
        
        Output Format:
        {{
            "service_credit_percent": float,
            "credit_amount": float,
            "penalty_amount": float,
            "net_exposure": float,
            "monthly_cap_reached": boolean,
            "exposure_percentage": float
        }}
        """,
        expected_output="JSON object with financial impact analysis",
        agent=None
    )


def create_executive_summary_task(
    incident_data: Dict[str, Any],
    compliance_result: Dict[str, Any],
    liability_result: Dict[str, Any],
    financial_result: Dict[str, Any]
) -> Task:
    """
    Task: Generate executive summary
    
    Creates:
    - High-level incident summary
    - Key findings
    - Recommendations
    - Action items
    """
    return Task(
        description=f"""
        Generate executive summary for incident {incident_data.get('incident_id')}.
        
        Key Findings:
        - SLA Breach: {compliance_result.get('breach_detected')}
        - Liability Waiver: {liability_result.get('exclusion_applies')}
        - Net Exposure: ${financial_result.get('net_exposure', 0):,.2f}
        
        Your Task:
        1. Summarize incident in 2-3 sentences
        2. Highlight critical findings
        3. Explain financial impact in business terms
        4. Provide actionable recommendations
        5. Identify escalation needs
        
        Output Format:
        {{
            "summary": "brief incident summary",
            "key_findings": ["finding1", "finding2", "finding3"],
            "financial_impact": "business-friendly explanation",
            "recommendations": ["action1", "action2"],
            "escalation_required": boolean,
            "severity_assessment": "CRITICAL|HIGH|MEDIUM|LOW"
        }}
        """,
        expected_output="JSON object with executive summary",
        agent=None
    )


def create_resolution_recommendation_task(
    incident_data: Dict[str, Any],
    compliance_result: Dict[str, Any]
) -> Task:
    """
    Task: Generate resolution recommendations
    
    Provides:
    - Immediate actions
    - Mitigation steps
    - Prevention measures
    """
    return Task(
        description=f"""
        Generate resolution recommendations for incident {incident_data.get('incident_id')}.
        
        Incident Context:
        - Priority: {incident_data.get('priority')}
        - Service: {incident_data.get('service')}
        - Breach Status: {compliance_result.get('breach_detected')}
        
        Your Task:
        1. Identify immediate actions to resolve incident
        2. Suggest mitigation steps to prevent SLA breach
        3. Recommend long-term prevention measures
        4. Prioritize actions by urgency
        5. Estimate time to resolution
        
        Output Format:
        {{
            "immediate_actions": ["action1", "action2"],
            "mitigation_steps": ["step1", "step2"],
            "prevention_measures": ["measure1", "measure2"],
            "estimated_resolution_time": "X hours",
            "priority_level": "URGENT|HIGH|NORMAL"
        }}
        """,
        expected_output="JSON object with resolution recommendations",
        agent=None
    )


# Made with Bob - CrewAI Task Definitions