"""
Firestore service layer for Contract Intelligence Agent
Handles all database operations for contract storage and retrieval
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.api_core import exceptions as gcp_exceptions

from app.core.config import settings
from app.models.contract_models import ContractDocument, ExtractedContract

logger = logging.getLogger(__name__)


class FirestoreServiceError(Exception):
    """Custom exception for Firestore service errors"""
    pass


class FirestoreService:
    """
    Service layer for Firestore operations
    """
    
    def __init__(self):
        """Initialize Firestore client"""
        try:
            # Check if GCP credentials are available
            if not settings.GCP_PROJECT_ID or not settings.GOOGLE_API_KEY:
                logger.warning("GCP credentials not configured. Firestore will use in-memory storage.")
                self.db = None
                self.collection_name = "contracts"
                self._in_memory_storage = {}
                return
            
            # Initialize Firestore client
            self.db = firestore.Client(
                project=settings.GCP_PROJECT_ID,
                database=settings.FIRESTORE_DB_NAME
            )
            self.collection_name = "contracts"
            self._in_memory_storage = None
            logger.info(f"Firestore client initialized for project: {settings.GCP_PROJECT_ID}")
        except Exception as e:
            logger.warning(f"Failed to initialize Firestore client: {e}. Using in-memory storage.")
            self.db = None
            self.collection_name = "contracts"
            self._in_memory_storage = {}
    
    async def save_contract(
        self,
        contract_id: str,
        filename: str,
        raw_text: str,
        extracted_data: ExtractedContract,
        file_size_bytes: int,
        file_type: str
    ) -> Dict[str, Any]:
        """
        Save contract document to Firestore
        
        Args:
            contract_id: Unique contract identifier
            filename: Original filename
            raw_text: Raw extracted text
            extracted_data: Structured extracted data
            file_size_bytes: File size in bytes
            file_type: File type (pdf, docx, txt)
            
        Returns:
            Saved document data
            
        Raises:
            FirestoreServiceError: If save operation fails
        """
        try:
            # Create contract document
            contract_doc = ContractDocument(
                contract_id=contract_id,
                filename=filename,
                raw_text=raw_text,
                extracted_data=extracted_data,
                uploaded_at=datetime.utcnow(),
                processed_at=datetime.utcnow(),
                file_size_bytes=file_size_bytes,
                file_type=file_type,
                extraction_status="completed"
            )
            
            # Convert to dict for storage
            doc_dict = contract_doc.model_dump(mode='json')
            
            # Use in-memory storage if Firestore not available
            if self.db is None:
                self._in_memory_storage[contract_id] = doc_dict
                logger.info(f"Successfully saved contract {contract_id} to in-memory storage")
                return doc_dict
            
            # Save to Firestore
            doc_ref = self.db.collection(self.collection_name).document(contract_id)
            doc_ref.set(doc_dict)
            
            logger.info(f"Successfully saved contract {contract_id} to Firestore")
            return doc_dict
            
        except Exception as e:
            logger.error(f"Error saving contract: {e}")
            raise FirestoreServiceError(f"Failed to save contract: {str(e)}")
    
    async def get_contract_by_id(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve contract by ID
        
        Args:
            contract_id: Contract identifier
            
        Returns:
            Contract document or None if not found
            
        Raises:
            FirestoreServiceError: If retrieval fails
        """
        try:
            # Use in-memory storage if Firestore not available
            if self.db is None:
                contract = self._in_memory_storage.get(contract_id)
                if contract:
                    logger.info(f"Retrieved contract {contract_id} from in-memory storage")
                else:
                    logger.warning(f"Contract {contract_id} not found in in-memory storage")
                return contract
            
            doc_ref = self.db.collection(self.collection_name).document(contract_id)
            doc = doc_ref.get()
            
            if doc.exists:
                logger.info(f"Retrieved contract {contract_id} from Firestore")
                return doc.to_dict()
            else:
                logger.warning(f"Contract {contract_id} not found in Firestore")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving contract: {e}")
            raise FirestoreServiceError(f"Failed to retrieve contract: {str(e)}")
    
    async def get_all_contracts(
        self,
        limit: Optional[int] = None,
        order_by: str = "uploaded_at",
        descending: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all contracts
        
        Args:
            limit: Maximum number of contracts to return
            order_by: Field to order by
            descending: Sort in descending order
            
        Returns:
            List of contract documents
            
        Raises:
            FirestoreServiceError: If retrieval fails
        """
        try:
            # Use in-memory storage if Firestore not available
            if self.db is None:
                contracts = list(self._in_memory_storage.values())
                # Sort by order_by field
                if order_by in ['uploaded_at', 'processed_at']:
                    contracts.sort(
                        key=lambda x: x.get(order_by, ''),
                        reverse=descending
                    )
                # Apply limit
                if limit:
                    contracts = contracts[:limit]
                logger.info(f"Retrieved {len(contracts)} contracts from in-memory storage")
                return contracts
            
            # Build query
            query = self.db.collection(self.collection_name)
            
            # Add ordering
            direction = firestore.Query.DESCENDING if descending else firestore.Query.ASCENDING
            query = query.order_by(order_by, direction=direction)
            
            # Add limit if specified
            if limit:
                query = query.limit(limit)
            
            # Execute query
            docs = query.stream()
            
            contracts = []
            for doc in docs:
                contract_data = doc.to_dict()
                contracts.append(contract_data)
            
            logger.info(f"Retrieved {len(contracts)} contracts from Firestore")
            return contracts
            
        except Exception as e:
            logger.error(f"Error retrieving contracts: {e}")
            raise FirestoreServiceError(f"Failed to retrieve contracts: {str(e)}")
    
    async def get_contracts_by_client(self, client_name: str) -> List[Dict[str, Any]]:
        """
        Retrieve contracts for a specific client
        
        Args:
            client_name: Client organization name
            
        Returns:
            List of contract documents
            
        Raises:
            FirestoreServiceError: If retrieval fails
        """
        try:
            # Use in-memory storage if Firestore not available
            if self.db is None:
                contracts = [
                    contract for contract in self._in_memory_storage.values()
                    if contract.get('extracted_data', {}).get('contract_metadata', {}).get('client_name') == client_name
                ]
                logger.info(f"Retrieved {len(contracts)} contracts for client {client_name} from in-memory storage")
                return contracts
            
            query = self.db.collection(self.collection_name).where(
                filter=FieldFilter("extracted_data.contract_metadata.client_name", "==", client_name)
            )
            
            docs = query.stream()
            contracts = [doc.to_dict() for doc in docs]
            
            logger.info(f"Retrieved {len(contracts)} contracts for client {client_name}")
            return contracts
            
        except Exception as e:
            logger.error(f"Error retrieving contracts by client: {e}")
            raise FirestoreServiceError(f"Failed to retrieve contracts by client: {str(e)}")
    
    async def update_contract_status(
        self,
        contract_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update contract extraction status
        
        Args:
            contract_id: Contract identifier
            status: New status (pending, processing, completed, failed)
            error_message: Error message if status is failed
            
        Returns:
            True if update successful
            
        Raises:
            FirestoreServiceError: If update fails
        """
        try:
            # Use in-memory storage if Firestore not available
            if self.db is None:
                if contract_id in self._in_memory_storage:
                    self._in_memory_storage[contract_id]["extraction_status"] = status
                    self._in_memory_storage[contract_id]["processed_at"] = datetime.utcnow()
                    if error_message:
                        self._in_memory_storage[contract_id]["error_message"] = error_message
                    logger.info(f"Updated contract {contract_id} status to {status} in in-memory storage")
                    return True
                return False
            
            doc_ref = self.db.collection(self.collection_name).document(contract_id)
            
            update_data = {
                "extraction_status": status,
                "processed_at": datetime.utcnow()
            }
            
            if error_message:
                update_data["error_message"] = error_message
            
            doc_ref.update(update_data)
            
            logger.info(f"Updated contract {contract_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating contract status: {e}")
            raise FirestoreServiceError(f"Failed to update contract status: {str(e)}")
    
    async def delete_contract(self, contract_id: str) -> bool:
        """
        Delete contract from storage
        
        Args:
            contract_id: Contract identifier
            
        Returns:
            True if deletion successful
            
        Raises:
            FirestoreServiceError: If deletion fails
        """
        try:
            # Use in-memory storage if Firestore not available
            if self.db is None:
                if contract_id in self._in_memory_storage:
                    del self._in_memory_storage[contract_id]
                    logger.info(f"Deleted contract {contract_id} from in-memory storage")
                    return True
                return False
            
            doc_ref = self.db.collection(self.collection_name).document(contract_id)
            doc_ref.delete()
            
            logger.info(f"Deleted contract {contract_id} from Firestore")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting contract: {e}")
            raise FirestoreServiceError(f"Failed to delete contract: {str(e)}")
    
    async def search_contracts(
        self,
        search_field: str,
        search_value: Any,
        operator: str = "=="
    ) -> List[Dict[str, Any]]:
        """
        Search contracts by field value
        
        Args:
            search_field: Field to search
            search_value: Value to search for
            operator: Comparison operator (==, !=, <, <=, >, >=)
            
        Returns:
            List of matching contracts
            
        Raises:
            FirestoreServiceError: If search fails
        """
        try:
            # Use in-memory storage if Firestore not available
            if self.db is None:
                contracts = []
                for contract in self._in_memory_storage.values():
                    # Simple field access for nested fields
                    field_parts = search_field.split('.')
                    value = contract
                    for part in field_parts:
                        value = value.get(part, {}) if isinstance(value, dict) else None
                        if value is None:
                            break
                    
                    # Apply operator
                    if operator == "==" and value == search_value:
                        contracts.append(contract)
                    elif operator == "!=" and value != search_value:
                        contracts.append(contract)
                
                logger.info(f"Found {len(contracts)} contracts matching search criteria in in-memory storage")
                return contracts
            
            query = self.db.collection(self.collection_name).where(
                filter=FieldFilter(search_field, operator, search_value)
            )
            
            docs = query.stream()
            contracts = [doc.to_dict() for doc in docs]
            
            logger.info(f"Found {len(contracts)} contracts matching search criteria")
            return contracts
            
        except Exception as e:
            logger.error(f"Error searching contracts: {e}")
            raise FirestoreServiceError(f"Failed to search contracts: {str(e)}")


# Singleton instance
_firestore_service: Optional[FirestoreService] = None


def get_firestore_service() -> FirestoreService:
    """
    Get or create Firestore service singleton
    
    Returns:
        FirestoreService instance
    """
    global _firestore_service
    if _firestore_service is None:
        _firestore_service = FirestoreService()
    return _firestore_service


# Made with Bob