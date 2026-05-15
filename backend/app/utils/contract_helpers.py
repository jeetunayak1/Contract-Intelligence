"""
Contract Helper Utilities
Helper functions for contract operations
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def get_first_available_contract_id() -> Optional[str]:
    """
    Get the first available contract ID from the database
    
    Returns:
        Contract ID or None if no contracts found
    """
    try:
        from app.services.contract_data_service import get_contract_data_service
        
        service = get_contract_data_service()
        contracts = await service.list_contracts(limit=1)
        
        if contracts and len(contracts) > 0:
            contract_id = contracts[0].get('contract_id')
            logger.info(f"Found contract: {contract_id}")
            return contract_id
        
        logger.warning("No contracts found in database")
        return None
        
    except Exception as e:
        logger.error(f"Failed to get first contract: {e}")
        return None


async def get_default_contract_id() -> Optional[str]:
    """
    Get default contract ID
    First tries to get from database, falls back to env variable
    
    Returns:
        Contract ID or None
    """
    import os
    
    # Try to get first available contract from DB
    contract_id = await get_first_available_contract_id()
    
    if contract_id:
        return contract_id
    
    # Fallback to env variable (but warn that it might not exist)
    env_contract_id = os.getenv('DEFAULT_CONTRACT_ID')
    if env_contract_id:
        logger.warning(f"Using DEFAULT_CONTRACT_ID from env: {env_contract_id} (may not exist in DB)")
        return env_contract_id
    
    logger.error("No contract ID available - please upload a contract first")
    return None


# Made with Bob