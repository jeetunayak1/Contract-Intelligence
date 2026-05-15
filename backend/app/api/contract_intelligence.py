"""
Contract Intelligence API endpoints
Follows SOW API pattern with simplified architecture
"""
import os
import logging
import tempfile
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse

from ..agents.contract_intelligence_agent import get_contract_agent
from ..services.contract_firestore import get_contract_firestore

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_contract(
    file: UploadFile = File(..., description="Contract file (PDF, DOCX, TXT)")
):
    """
    Upload and extract contract SLA obligations
    
    Returns structured JSON with all SLA data
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Extract contract data (force reload to get latest code)
            agent = get_contract_agent(force_reload=True)
            result = await agent.extract_contract(
                file_path=tmp_file_path,
                filename=file.filename
            )
            
            # Save to Firestore
            firestore = get_contract_firestore()
            await firestore.save_contract(result)
            
            logger.info(f"Successfully processed contract: {result['contract_id']}")
            logger.info(f"LLM metadata: {result.get('llm_metadata', {})}")
            
            return {
                "success": True,
                "contract_id": result["contract_id"],
                "filename": result["filename"],
                "data": result["extracted_data"],
                "llm_metadata": result.get("llm_metadata", {}),
                "extraction_status": result.get("extraction_status", "unknown"),
                "message": "Contract uploaded and processed successfully"
            }
            
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Contract upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process contract: {str(e)}"
        )


@router.get("/list")
async def list_contracts(
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum contracts to return")
):
    """List all contracts"""
    try:
        firestore = get_contract_firestore()
        contracts = await firestore.list_contracts(limit=limit)
        
        return {
            "success": True,
            "count": len(contracts),
            "contracts": contracts
        }
    except Exception as e:
        logger.error(f"Failed to list contracts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    """Get contract by ID"""
    try:
        firestore = get_contract_firestore()
        contract = await firestore.get_contract(contract_id)
        
        if not contract:
            raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
        
        return {
            "success": True,
            "contract": contract
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{contract_id}")
async def delete_contract(contract_id: str):
    """Delete contract by ID"""
    try:
        firestore = get_contract_firestore()
        
        # Check if exists
        contract = await firestore.get_contract(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
        
        # Delete
        await firestore.delete_contract(contract_id)
        
        return {
            "success": True,
            "message": f"Contract {contract_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete contract: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/status")
async def health_check():
    """Health check for contract intelligence service"""
    try:
        agent = get_contract_agent()
        firestore = get_contract_firestore()
        
        return {
            "status": "healthy",
            "service": "Contract Intelligence",
            "gemini_configured": agent.gemini_client is not None,
            "firestore_configured": firestore.db is not None,
            "storage_mode": "firestore" if firestore.db else "in-memory"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# Made with Bob