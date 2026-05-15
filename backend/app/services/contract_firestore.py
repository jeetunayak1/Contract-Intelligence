"""
Firestore service for Contract Intelligence
Uses environment variables directly (no config.py)
"""
import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

try:
    from google.cloud import firestore
    from google.cloud.firestore_v1.base_query import FieldFilter
except ImportError:
    firestore = None
    FieldFilter = None

logger = logging.getLogger(__name__)


class ContractFirestoreService:
    """Firestore service for contract storage"""
    
    def __init__(self):
        """Initialize Firestore client"""
        self.gcp_project_id = os.getenv("GCP_PROJECT_ID")
        self.firestore_db_name = os.getenv("FIRESTORE_DB_NAME", "(default)")
        self.db = None
        self._in_memory_storage = {}
        
        if self.gcp_project_id and firestore:
            try:
                self.db = firestore.Client(
                    project=self.gcp_project_id,
                    database=self.firestore_db_name
                )
                logger.info(f"Firestore initialized for project: {self.gcp_project_id}")
            except Exception as e:
                logger.warning(f"Firestore init failed: {e}. Using in-memory storage.")
                self.db = None
        else:
            logger.info("Using in-memory storage (Firestore not configured)")
    
    async def save_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save contract to Firestore or in-memory"""
        contract_id = contract_data.get("contract_id")
        
        if self.db:
            try:
                doc_ref = self.db.collection("contracts").document(contract_id)
                doc_ref.set(contract_data)
                logger.info(f"Saved contract {contract_id} to Firestore")
                return contract_data
            except Exception as e:
                logger.error(f"Firestore save failed: {e}")
        
        # Fallback to in-memory
        self._in_memory_storage[contract_id] = contract_data
        logger.info(f"Saved contract {contract_id} to in-memory storage")
        return contract_data
    
    async def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get contract by ID"""
        if self.db:
            try:
                doc_ref = self.db.collection("contracts").document(contract_id)
                doc = doc_ref.get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                logger.error(f"Firestore get failed: {e}")
        
        # Fallback to in-memory
        return self._in_memory_storage.get(contract_id)
    
    async def list_contracts(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all contracts"""
        if self.db:
            try:
                query = self.db.collection("contracts").order_by("processed_at", direction=firestore.Query.DESCENDING)
                if limit:
                    query = query.limit(limit)
                docs = query.stream()
                return [doc.to_dict() for doc in docs]
            except Exception as e:
                logger.error(f"Firestore list failed: {e}")
        
        # Fallback to in-memory
        contracts = list(self._in_memory_storage.values())
        contracts.sort(key=lambda x: x.get("processed_at", ""), reverse=True)
        if limit:
            contracts = contracts[:limit]
        return contracts
    
    async def get_contract_by_id(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get contract by ID (alias for get_contract)"""
        return await self.get_contract(contract_id)
    
    async def get_all_contracts(self) -> List[Dict[str, Any]]:
        """Get all contracts (alias for list_contracts)"""
        return await self.list_contracts()
    
    async def delete_contract(self, contract_id: str) -> bool:
        """Delete contract"""
        if self.db:
            try:
                self.db.collection("contracts").document(contract_id).delete()
                logger.info(f"Deleted contract {contract_id} from Firestore")
                return True
            except Exception as e:
                logger.error(f"Firestore delete failed: {e}")
        
        # Fallback to in-memory
        if contract_id in self._in_memory_storage:
            del self._in_memory_storage[contract_id]
            logger.info(f"Deleted contract {contract_id} from in-memory storage")
            return True
        return False


# Singleton
_service: Optional[ContractFirestoreService] = None


def get_contract_firestore() -> ContractFirestoreService:
    """Get or create Firestore service singleton"""
    global _service
    if _service is None:
        _service = ContractFirestoreService()
    return _service


# Made with Bob