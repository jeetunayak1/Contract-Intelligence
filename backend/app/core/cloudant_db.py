"""
IBM Cloudant database configuration and connection management
"""
try:
    from ibmcloudant.cloudant_v1 import CloudantV1, Document
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
except ImportError:
    CloudantV1 = None
    Document = None
    IAMAuthenticator = None

# Google Firestore imports
try:
    from google.cloud import firestore
except ImportError:
    firestore = None

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class CloudantDatabase:
    """
    Cloudant database manager for Contract Intelligence System
    """
    
    def __init__(self):
        """Initialize database client"""
        self.db_provider = settings.DB_PROVIDER.lower()
        self.client = None
        self.firestore_client = None
        self.db_name = settings.CLOUDANT_DB_NAME if self.db_provider == "ibm" else "contract-intelligence"
        
        if self.db_provider == "ibm":
            self._initialize_ibm_client()
        elif self.db_provider == "gcp":
            self._initialize_gcp_client()
    
    def _initialize_ibm_client(self):
        """Initialize Cloudant client with IAM authentication"""
        try:
            authenticator = IAMAuthenticator(settings.CLOUDANT_API_KEY)
            self.client = CloudantV1(authenticator=authenticator)
            self.client.set_service_url(settings.CLOUDANT_URL)
            logger.info(f"Cloudant client initialized for database: {self.db_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Cloudant client: {str(e)}")
            raise
            
    def _initialize_gcp_client(self):
        """Initialize Firestore client"""
        try:
            self.firestore_client = firestore.AsyncClient(
                project=settings.GCP_PROJECT_ID,
                database=settings.FIRESTORE_DB_NAME
            )
            logger.info(f"Firestore client initialized for collection: {self.db_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {str(e)}")
            raise
    
    async def create_database(self, db_name: str = None) -> bool:
        """
        Create a new database if it doesn't exist
        
        Args:
            db_name: Database name (uses default if not provided)
            
        Returns:
            True if created or already exists
        """
        db_name = db_name or self.db_name
        
        if self.db_provider == "gcp":
            # Firestore collections are created implicitly
            logger.info(f"Firestore collection ready: {db_name}")
            return True
            
        try:
            response = self.client.put_database(db=db_name).get_result()
            logger.info(f"Database created: {db_name}")
            return True
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"Database already exists: {db_name}")
                return True
            logger.error(f"Failed to create database: {str(e)}")
            return False
    
    async def create_document(self, document: Dict[str, Any], db_name: str = None) -> Dict[str, Any]:
        """
        Create a new document in Cloudant
        
        Args:
            document: Document data
            db_name: Database name (uses default if not provided)
            
        Returns:
            Created document with _id and _rev
        """
        db_name = db_name or self.db_name
        try:
            # Add timestamp if not present
            if 'created_at' not in document:
                document['created_at'] = datetime.utcnow().isoformat()
            if 'updated_at' not in document:
                document['updated_at'] = datetime.utcnow().isoformat()
            
            if self.db_provider == "gcp":
                doc_ref = self.firestore_client.collection(db_name).document(document.get('_id'))
                if '_id' in document:
                    document.pop('_id')
                if '_rev' in document:
                    document.pop('_rev')
                await doc_ref.set(document)
                document['_id'] = doc_ref.id
                document['_rev'] = "1" # Firestore doesn't use revs
                logger.info(f"Document created in Firestore: {doc_ref.id}")
                return document
            
            response = self.client.post_document(
                db=db_name,
                document=Document(**document)
            ).get_result()
            
            document['_id'] = response['id']
            document['_rev'] = response['rev']
            
            logger.info(f"Document created: {response['id']}")
            return document
        except Exception as e:
            logger.error(f"Failed to create document: {str(e)}")
            raise
    
    async def get_document(self, doc_id: str, db_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID
        
        Args:
            doc_id: Document ID
            db_name: Database name (uses default if not provided)
            
        Returns:
            Document data or None if not found
        """
        db_name = db_name or self.db_name
        try:
            if self.db_provider == "gcp":
                doc_ref = self.firestore_client.collection(db_name).document(doc_id)
                doc = await doc_ref.get()
                if doc.exists:
                    data = doc.to_dict()
                    data['_id'] = doc.id
                    data['_rev'] = "1"
                    return data
                logger.info(f"Document not found in Firestore: {doc_id}")
                return None
                
            response = self.client.get_document(
                db=db_name,
                doc_id=doc_id
            ).get_result()
            return response
        except Exception as e:
            error_text = str(e).lower()
            if "not found" in error_text or "not_found" in error_text or "status code: 404" in error_text:
                logger.info(f"Document not found: {doc_id}")
                return None
            logger.error(f"Failed to get document: {str(e)}")
            raise
    
    async def update_document(self, doc_id: str, document: Dict[str, Any], db_name: str = None) -> Dict[str, Any]:
        """
        Update an existing document
        
        Args:
            doc_id: Document ID
            document: Updated document data (must include _rev)
            db_name: Database name (uses default if not provided)
            
        Returns:
            Updated document with new _rev
        """
        db_name = db_name or self.db_name
        try:
            # Update timestamp
            document['updated_at'] = datetime.utcnow().isoformat()
            
            if self.db_provider == "gcp":
                doc_ref = self.firestore_client.collection(db_name).document(doc_id)
                update_data = document.copy()
                if '_id' in update_data:
                    update_data.pop('_id')
                if '_rev' in update_data:
                    update_data.pop('_rev')
                await doc_ref.set(update_data, merge=True)
                document['_id'] = doc_id
                document['_rev'] = "1"
                logger.info(f"Document updated in Firestore: {doc_id}")
                return document
                
            response = self.client.put_document(
                db=db_name,
                doc_id=doc_id,
                document=Document(**document)
            ).get_result()
            
            document['_rev'] = response['rev']
            logger.info(f"Document updated: {doc_id}")
            return document
        except Exception as e:
            logger.error(f"Failed to update document: {str(e)}")
            raise
    
    async def delete_document(self, doc_id: str, rev: str, db_name: str = None) -> bool:
        """
        Delete a document
        
        Args:
            doc_id: Document ID
            rev: Document revision
            db_name: Database name (uses default if not provided)
            
        Returns:
            True if deleted successfully
        """
        db_name = db_name or self.db_name
        try:
            if self.db_provider == "gcp":
                doc_ref = self.firestore_client.collection(db_name).document(doc_id)
                await doc_ref.delete()
                logger.info(f"Document deleted from Firestore: {doc_id}")
                return True
                
            self.client.delete_document(
                db=db_name,
                doc_id=doc_id,
                rev=rev
            ).get_result()
            logger.info(f"Document deleted: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            return False
    
    async def query_documents(self, selector: Dict[str, Any], db_name: str = None, 
                            limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Query documents using Cloudant Query (Mango)
        
        Args:
            selector: Query selector (Mango query syntax)
            db_name: Database name (uses default if not provided)
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            
        Returns:
            List of matching documents
        """
        db_name = db_name or self.db_name
        try:
            if self.db_provider == "gcp":
                collection_ref = self.firestore_client.collection(db_name)
                query = collection_ref
                for key, value in selector.items():
                    # Simple equality translation
                    if isinstance(value, dict) and "$in" in value:
                        query = query.where(key, "in", value["$in"])
                    else:
                        query = query.where(key, "==", value)
                
                query = query.limit(limit).offset(skip)
                docs = []
                async for doc in query.stream():
                    data = doc.to_dict()
                    data['_id'] = doc.id
                    data['_rev'] = "1"
                    docs.append(data)
                return docs
                
            response = self.client.post_find(
                db=db_name,
                selector=selector,
                limit=limit,
                skip=skip
            ).get_result()
            
            return response.get('docs', [])
        except Exception as e:
            logger.error(f"Failed to query documents: {str(e)}")
            raise
    
    async def create_index(self, index_fields: List[str], index_name: str = None, 
                          db_name: str = None) -> bool:
        """
        Create an index for efficient querying
        
        Args:
            index_fields: List of fields to index
            index_name: Optional index name
            db_name: Database name (uses default if not provided)
            
        Returns:
            True if index created successfully
        """
        db_name = db_name or self.db_name
        
        if self.db_provider == "gcp":
            logger.info("Firestore handles single-field indexes automatically. Composite index might need manual setup via GCP console.")
            return True
            
        try:
            # Prepare index definition
            index_spec = {
                "fields": index_fields
            }
            
            # Call post_index with correct parameters
            self.client.post_index(
                db=db_name,
                index=index_spec,
                name=index_name,
                type="json"
            ).get_result()
            
            logger.info(f"Index created on fields: {index_fields}")
            return True
        except Exception as e:
            logger.error(f"Failed to create index: {str(e)}")
            return False
    
    async def bulk_create(self, documents: List[Dict[str, Any]], db_name: str = None) -> List[Dict[str, Any]]:
        """
        Create multiple documents in a single request
        
        Args:
            documents: List of documents to create
            db_name: Database name (uses default if not provided)
            
        Returns:
            List of created documents with _id and _rev
        """
        db_name = db_name or self.db_name
        try:
            # Add timestamps
            timestamp = datetime.utcnow().isoformat()
            for doc in documents:
                if 'created_at' not in doc:
                    doc['created_at'] = timestamp
                if 'updated_at' not in doc:
                    doc['updated_at'] = timestamp
            
            if self.db_provider == "gcp":
                batch = self.firestore_client.batch()
                collection_ref = self.firestore_client.collection(db_name)
                
                for doc in documents:
                    doc_copy = doc.copy()
                    doc_id = doc_copy.pop('_id', None)
                    doc_copy.pop('_rev', None)
                    
                    if doc_id:
                        doc_ref = collection_ref.document(doc_id)
                    else:
                        doc_ref = collection_ref.document()
                        
                    batch.set(doc_ref, doc_copy)
                    doc['_id'] = doc_ref.id
                    doc['_rev'] = "1"
                    
                await batch.commit()
                logger.info(f"Bulk created {len(documents)} documents in Firestore")
                return documents
                
            bulk_docs = [Document(**doc) for doc in documents]
            response = self.client.post_bulk_docs(
                db=db_name,
                bulk_docs={"docs": bulk_docs}
            ).get_result()
            
            # Update documents with _id and _rev
            for i, result in enumerate(response):
                if 'id' in result:
                    documents[i]['_id'] = result['id']
                    documents[i]['_rev'] = result['rev']
            
            logger.info(f"Bulk created {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Failed to bulk create documents: {str(e)}")
            raise
    
    async def get_all_documents(self, db_name: str = None, include_docs: bool = True,
                               limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all documents from database
        
        Args:
            db_name: Database name (uses default if not provided)
            include_docs: Include full document content
            limit: Maximum number of documents
            
        Returns:
            List of documents
        """
        db_name = db_name or self.db_name
        try:
            if self.db_provider == "gcp":
                collection_ref = self.firestore_client.collection(db_name)
                docs = []
                async for doc in collection_ref.limit(limit).stream():
                    if include_docs:
                        data = doc.to_dict()
                        data['_id'] = doc.id
                        data['_rev'] = "1"
                        docs.append(data)
                    else:
                        docs.append({"id": doc.id, "key": doc.id, "value": {"rev": "1"}})
                return docs
                
            response = self.client.post_all_docs(
                db=db_name,
                include_docs=include_docs,
                limit=limit
            ).get_result()
            
            if include_docs:
                return [row['doc'] for row in response.get('rows', [])]
            return response.get('rows', [])
        except Exception as e:
            logger.error(f"Failed to get all documents: {str(e)}")
            raise


# Global Cloudant instance
cloudant_db = CloudantDatabase()


async def get_cloudant() -> CloudantDatabase:
    """
    Dependency function to get Cloudant database instance
    
    Returns:
        CloudantDatabase instance
    """
    return cloudant_db


async def init_cloudant():
    """
    Initialize Cloudant databases and indexes
    """
    try:
        # Create main database
        await cloudant_db.create_database()
        
        # Create indexes for common queries
        await cloudant_db.create_index(
            index_fields=["type", "created_at"],
            index_name="type-created-index"
        )
        await cloudant_db.create_index(
            index_fields=["contract_number"],
            index_name="contract-number-index"
        )
        await cloudant_db.create_index(
            index_fields=["customer_name"],
            index_name="customer-name-index"
        )
        await cloudant_db.create_index(
            index_fields=["status"],
            index_name="status-index"
        )
        
        logger.info("Cloudant initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Cloudant: {str(e)}")
        raise

# Made with Bob


# Global instance
cloudant_db = CloudantDatabase()


def get_cloudant_db() -> CloudantDatabase:
    """Get the global Cloudant database instance"""
    return cloudant_db
