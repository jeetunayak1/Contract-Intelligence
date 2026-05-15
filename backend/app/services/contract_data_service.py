"""
Contract Data Service
Fetches extracted contract obligations from Firebase/Firestore
"""
import logging
from typing import Optional, Dict, Any

from app.services.contract_firestore import ContractFirestoreService
from app.models.contract_models import ExtractedContract, ComplianceObligations

logger = logging.getLogger(__name__)


class ContractDataService:
    """
    Service for fetching contract data and compliance obligations
    """
    
    def __init__(self):
        """Initialize contract data service"""
        self.firestore_service = ContractFirestoreService()
    
    async def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete contract document
        
        Args:
            contract_id: Contract identifier
            
        Returns:
            Contract document or None if not found
        """
        try:
            contract_doc = await self.firestore_service.get_contract(contract_id)
            if not contract_doc:
                logger.warning(f"Contract {contract_id} not found")
                return None
            
            return contract_doc
            
        except Exception as e:
            logger.error(f"Failed to fetch contract {contract_id}: {e}")
            return None
    
    async def get_extracted_contract(self, contract_id: str) -> Optional[ExtractedContract]:
        """
        Get parsed and validated extracted contract
        
        Args:
            contract_id: Contract identifier
            
        Returns:
            ExtractedContract model or None if not found
        """
        try:
            contract_doc = await self.get_contract(contract_id)
            if not contract_doc:
                return None
            
            extracted_data = contract_doc.get('extracted_data')
            if not extracted_data:
                logger.warning(f"Contract {contract_id} has no extracted_data")
                return None
            
            # Parse and validate
            contract = ExtractedContract(**extracted_data)
            return contract
            
        except Exception as e:
            logger.error(f"Failed to parse contract {contract_id}: {e}")
            return None
    
    async def get_compliance_obligations(self, contract_id: str) -> Optional[ComplianceObligations]:
        """
        Get only compliance obligations from contract
        
        Args:
            contract_id: Contract identifier
            
        Returns:
            ComplianceObligations or None if not found
        """
        try:
            contract = await self.get_extracted_contract(contract_id)
            if not contract:
                return None
            
            return contract.compliance_obligations
            
        except Exception as e:
            logger.error(f"Failed to fetch compliance obligations for {contract_id}: {e}")
            return None
    
    async def list_contracts(self, limit: int = 50) -> list[Dict[str, Any]]:
        """
        List all contracts
        
        Args:
            limit: Maximum number of contracts to return
            
        Returns:
            List of contract documents
        """
        try:
            contracts = await self.firestore_service.list_contracts(limit=limit)
            return contracts
            
        except Exception as e:
            logger.error(f"Failed to list contracts: {e}")
            return []
    
    def get_contract_metadata(self, contract: ExtractedContract) -> Dict[str, Any]:
        """
        Extract metadata from contract for reporting
        
        Args:
            contract: Extracted contract
            
        Returns:
            Metadata dictionary
        """
        return {
            'client_name': contract.contract_metadata.client_name,
            'provider_name': contract.contract_metadata.provider_name,
            'effective_date': contract.contract_metadata.effective_date,
            'contract_period_years': contract.contract_metadata.contract_period_years,
            'total_incident_slas': len(contract.compliance_obligations.incident_slas),
            'total_availability_slas': len(contract.compliance_obligations.availability_slas),
            'total_quality_kpis': len(contract.compliance_obligations.quality_kpis)
        }


# Singleton instance
_contract_data_service = None


def get_contract_data_service() -> ContractDataService:
    """Get or create contract data service singleton"""
    global _contract_data_service
    if _contract_data_service is None:
        _contract_data_service = ContractDataService()
    return _contract_data_service


# Made with Bob - Contract Data Service