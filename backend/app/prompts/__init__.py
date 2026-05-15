"""
Prompt templates for Contract Intelligence System
"""
from app.prompts.contract_extraction_prompt import (
    CONTRACT_EXTRACTION_SYSTEM_PROMPT,
    CONTRACT_EXTRACTION_USER_PROMPT,
    get_extraction_prompt
)

__all__ = [
    "CONTRACT_EXTRACTION_SYSTEM_PROMPT",
    "CONTRACT_EXTRACTION_USER_PROMPT",
    "get_extraction_prompt"
]

# Made with Bob