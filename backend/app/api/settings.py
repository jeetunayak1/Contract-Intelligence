"""
Settings API
Handles global application settings and API credentials
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from app.core.cloudant_db import cloudant_db

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


class SettingsRequest(BaseModel):
    """Settings save request"""
    github_token: str = None
    slack_webhook_url: str = None
    microsoft_client_id: str = None
    microsoft_client_secret: str = None
    microsoft_tenant_id: str = None
    microsoft_sender_email: str = None
    outlook_email: str = None
    outlook_password: str = None


@router.post("/save")
async def save_settings(settings: SettingsRequest):
    """
    Save global API settings to database
    """
    try:
        # Get existing settings document
        existing = await cloudant_db.get_document("global_api_settings")
        
        settings_dict = {
            "_id": "global_api_settings",
            "type": "global_settings"
        }
        
        # Add revision if document exists
        if existing and isinstance(existing, dict):
            settings_dict["_rev"] = existing.get("_rev")
        
        # Update with new values (only if provided)
        if settings.github_token:
            settings_dict["github_token"] = settings.github_token
        elif existing:
            settings_dict["github_token"] = existing.get("github_token")
            
        if settings.slack_webhook_url:
            settings_dict["slack_webhook_url"] = settings.slack_webhook_url
        elif existing:
            settings_dict["slack_webhook_url"] = existing.get("slack_webhook_url")
            
        if settings.microsoft_client_id:
            settings_dict["microsoft_client_id"] = settings.microsoft_client_id
        elif existing:
            settings_dict["microsoft_client_id"] = existing.get("microsoft_client_id")
            
        if settings.microsoft_client_secret:
            settings_dict["microsoft_client_secret"] = settings.microsoft_client_secret
        elif existing:
            settings_dict["microsoft_client_secret"] = existing.get("microsoft_client_secret")
            
        if settings.microsoft_tenant_id:
            settings_dict["microsoft_tenant_id"] = settings.microsoft_tenant_id
        elif existing:
            settings_dict["microsoft_tenant_id"] = existing.get("microsoft_tenant_id")
            
        if settings.microsoft_sender_email:
            settings_dict["microsoft_sender_email"] = settings.microsoft_sender_email
        elif existing:
            settings_dict["microsoft_sender_email"] = existing.get("microsoft_sender_email")
            
        if settings.outlook_email:
            settings_dict["outlook_email"] = settings.outlook_email
        elif existing:
            settings_dict["outlook_email"] = existing.get("outlook_email")
            
        if settings.outlook_password:
            settings_dict["outlook_password"] = settings.outlook_password
        elif existing:
            settings_dict["outlook_password"] = existing.get("outlook_password")
        
        # Save to database
        if existing:
            await cloudant_db.update_document("global_api_settings", settings_dict)
        else:
            await cloudant_db.create_document(settings_dict)
        
        return {
            "success": True,
            "message": "Settings saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(e)}")


@router.get("/get")
async def get_settings():
    """
    Get global API settings (tokens are masked for security)
    """
    try:
        settings = await cloudant_db.get_document("global_api_settings")
        
        if not settings or not isinstance(settings, dict):
            return {
                "github_token": None,
                "slack_webhook_url": None,
                "microsoft_client_id": None,
                "microsoft_client_secret": None,
                "microsoft_tenant_id": None,
                "microsoft_sender_email": None,
                "outlook_email": None,
                "outlook_password": None
            }
        
        # Mask sensitive tokens
        return {
            "github_token": "configured" if settings.get("github_token") else None,
            "slack_webhook_url": "configured" if settings.get("slack_webhook_url") else None,
            "microsoft_client_id": "configured" if settings.get("microsoft_client_id") else None,
            "microsoft_client_secret": "configured" if settings.get("microsoft_client_secret") else None,
            "microsoft_tenant_id": "configured" if settings.get("microsoft_tenant_id") else None,
            "microsoft_sender_email": settings.get("microsoft_sender_email") if settings.get("microsoft_sender_email") else None,
            "outlook_email": settings.get("outlook_email") if settings.get("outlook_email") else None,
            "outlook_password": "configured" if settings.get("outlook_password") else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")


@router.delete("/clear")
async def clear_settings():
    """
    Clear all global API settings
    """
    try:
        settings = await cloudant_db.get_document("global_api_settings")
        
        if settings and isinstance(settings, dict):
            doc_id = settings.get("_id")
            doc_rev = settings.get("_rev")
            if doc_id and doc_rev:
                await cloudant_db.delete_document(doc_id, doc_rev)
        
        return {
            "success": True,
            "message": "Settings cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear settings: {str(e)}")

@router.post("/test-slack")
async def test_slack_connection():
    """
    Test Slack webhook connection
    """
    try:
        from app.services.slack_notifications import slack_service
        result = await slack_service.test_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test Slack connection: {str(e)}")


@router.post("/test-outlook")
async def test_outlook_connection():
    """
    Test Outlook SMTP connection (for personal accounts)
    """
    try:
        from app.services.outlook_smtp import outlook_smtp_service
        result = await outlook_smtp_service.test_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test Outlook connection: {str(e)}")



# Made with Bob
