"""
FastAPI endpoints for Contract Intelligence operations
Handles contract upload, extraction, and retrieval
"""
import logging
import uuid
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from fastapi.responses import JSONResponse

from app.models.contract_models import (
    ContractUploadResponse,
    ContractListResponse,
    ContractDetailResponse,
    ExtractedContract
)
from app.utils.document_parser import DocumentParser, DocumentParsingError
from app.agents.contract_agent_feature import get_contract_agent, reset_contract_agent, ContractAgentError
from app.services.firestore_service import get_firestore_service, FirestoreServiceError
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/upload", response_model=ContractUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_contract(
    file: UploadFile = File(..., description="Contract file (PDF, DOCX, or TXT)")
):
    """
    Upload and extract contract SLA obligations
    
    This endpoint:
    1. Validates the uploaded file
    2. Extracts text from the document
    3. Runs Contract Intelligence Agent to extract SLAs
    4. Stores results in Firestore
    5. Returns structured JSON
    
    Args:
        file: Uploaded contract file
        
    Returns:
        ContractUploadResponse with extracted data
        
    Raises:
        HTTPException: If upload or extraction fails
    """
    contract_id = None
    
    try:
        # Validate file extension
        DocumentParser.validate_file_extension(file.filename)
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        DocumentParser.validate_file_size(file_size, settings.MAX_UPLOAD_SIZE)
        
        logger.info(f"Processing contract upload: {file.filename} ({file_size} bytes)")
        
        # Parse document
        try:
            raw_text, file_type = DocumentParser.parse_file(file_content, file.filename)
        except DocumentParsingError as e:
            logger.error(f"Document parsing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse document: {str(e)}"
            )
        
        # Generate contract ID
        contract_id = f"contract_{uuid.uuid4().hex[:12]}"
        
        # Extract contract data using agent (force reload to get latest code)
        try:
            agent = get_contract_agent(force_reload=True)
            extracted_data = await agent.extract_contract(
                contract_text=raw_text,
                filename=file.filename,
                contract_id=contract_id
            )
        except ContractAgentError as e:
            logger.error(f"Contract extraction failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to extract contract data: {str(e)}"
            )
        
        # Save to Firestore
        try:
            firestore_service = get_firestore_service()
            await firestore_service.save_contract(
                contract_id=contract_id,
                filename=file.filename,
                raw_text=raw_text,
                extracted_data=extracted_data,
                file_size_bytes=file_size,
                file_type=file_type
            )
        except FirestoreServiceError as e:
            logger.error(f"Firestore save failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save contract: {str(e)}"
            )
        
        logger.info(f"Successfully processed contract {contract_id}")
        
        # Return response
        return ContractUploadResponse(
            success=True,
            contract_id=contract_id,
            filename=file.filename,
            data=extracted_data,
            message="Contract uploaded and processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing contract: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/", response_model=ContractListResponse)
async def list_contracts(
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of contracts to return"),
    order_by: str = Query("uploaded_at", description="Field to order by"),
    descending: bool = Query(True, description="Sort in descending order")
):
    """
    List all contracts
    
    Args:
        limit: Maximum number of contracts to return
        order_by: Field to order by (default: uploaded_at)
        descending: Sort in descending order (default: True)
        
    Returns:
        ContractListResponse with list of contracts
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        firestore_service = get_firestore_service()
        contracts = await firestore_service.get_all_contracts(
            limit=limit,
            order_by=order_by,
            descending=descending
        )
        
        logger.info(f"Retrieved {len(contracts)} contracts")
        
        return ContractListResponse(
            success=True,
            count=len(contracts),
            contracts=contracts
        )
        
    except FirestoreServiceError as e:
        logger.error(f"Failed to retrieve contracts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve contracts: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving contracts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/{contract_id}", response_model=ContractDetailResponse)
async def get_contract(contract_id: str):
    """
    Get contract by ID
    
    Args:
        contract_id: Contract identifier
        
    Returns:
        ContractDetailResponse with contract details
        
    Raises:
        HTTPException: If contract not found or retrieval fails
    """
    try:
        firestore_service = get_firestore_service()
        contract = await firestore_service.get_contract_by_id(contract_id)
        
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contract {contract_id} not found"
            )
        
        logger.info(f"Retrieved contract {contract_id}")
        
        return ContractDetailResponse(
            success=True,
            contract=contract,
            message="Contract retrieved successfully"
        )
        
    except HTTPException:
        raise
    except FirestoreServiceError as e:
        logger.error(f"Failed to retrieve contract: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve contract: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving contract: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/client/{client_name}")
async def get_contracts_by_client(client_name: str):
    """
    Get contracts for a specific client
    
    Args:
        client_name: Client organization name
        
    Returns:
        List of contracts for the client
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        firestore_service = get_firestore_service()
        contracts = await firestore_service.get_contracts_by_client(client_name)
        
        logger.info(f"Retrieved {len(contracts)} contracts for client {client_name}")
        
        return {
            "success": True,
            "client_name": client_name,
            "count": len(contracts),
            "contracts": contracts
        }
        
    except FirestoreServiceError as e:
        logger.error(f"Failed to retrieve contracts by client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve contracts: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving contracts by client: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.delete("/{contract_id}")
async def delete_contract(contract_id: str):
    """
    Delete contract by ID
    
    Args:
        contract_id: Contract identifier
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        firestore_service = get_firestore_service()
        
        # Check if contract exists
        contract = await firestore_service.get_contract_by_id(contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contract {contract_id} not found"
            )
        
        # Delete contract
        await firestore_service.delete_contract(contract_id)
        
        logger.info(f"Deleted contract {contract_id}")
        
        return {
            "success": True,
            "message": f"Contract {contract_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except FirestoreServiceError as e:
        logger.error(f"Failed to delete contract: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete contract: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting contract: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/agent/reset")
async def reset_agent():
    """
    Reset the contract agent singleton (useful after code updates)
    
    Returns:
        Success message
    """
    try:
        reset_contract_agent()
        logger.info("Contract agent reset successfully")
        return {
            "success": True,
            "message": "Contract agent reset successfully. Next upload will use updated code."
        }
    except Exception as e:
        logger.error(f"Failed to reset agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset agent: {str(e)}"
        )


# Health check for contracts service
@router.get("/health/status")
async def contracts_health():
    """
    Health check for contracts service
    
    Returns:
        Service health status
    """
    try:
        # Test Firestore connection
        firestore_service = get_firestore_service()
        
        # Test agent initialization
        agent = get_contract_agent()
        
        return {
            "status": "healthy",
            "service": "Contract Intelligence",
            "firestore": "connected",
            "agent": "initialized"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "Contract Intelligence",
                "error": str(e)
            }
        )


# Made with Bob