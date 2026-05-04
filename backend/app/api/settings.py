from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.core.cloudant_db import cloudant_db
from app.core.config import settings

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


def _settings_doc_id() -> str:
    return "global_api_settings"


def _mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


def _build_settings_response(document: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "github_token": document.get("github_token", ""),
        "github_token_masked": _mask_secret(document.get("github_token", "")),
        "github_owner": document.get("github_owner", ""),
        "github_repo": document.get("github_repo", ""),
        "slack_bot_token": document.get("slack_bot_token", ""),
        "slack_bot_token_masked": _mask_secret(document.get("slack_bot_token", "")),
        "slack_workspace_id": document.get("slack_workspace_id", ""),
        "microsoft_client_id": document.get("microsoft_client_id", ""),
        "microsoft_client_secret": document.get("microsoft_client_secret", ""),
        "microsoft_client_secret_masked": _mask_secret(document.get("microsoft_client_secret", "")),
        "microsoft_tenant_id": document.get("microsoft_tenant_id", ""),
        "updated_at": document.get("updated_at"),
    }


@router.get("")
async def get_global_settings():
    try:
        stored = await cloudant_db.get_document(_settings_doc_id())
        if stored:
            return {
                "success": True,
                "settings": _build_settings_response(stored),
            }

        fallback_document = {
            "github_token": settings.GITHUB_TOKEN,
            "github_owner": settings.GITHUB_OWNER,
            "github_repo": settings.GITHUB_REPO,
            "slack_bot_token": settings.SLACK_BOT_TOKEN,
            "slack_workspace_id": settings.SLACK_WORKSPACE_ID,
            "microsoft_client_id": settings.MICROSOFT_CLIENT_ID,
            "microsoft_client_secret": settings.MICROSOFT_CLIENT_SECRET,
            "microsoft_tenant_id": settings.MICROSOFT_TENANT_ID,
            "updated_at": None,
        }
        return {
            "success": True,
            "settings": _build_settings_response(fallback_document),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load settings: {str(exc)}")


@router.post("")
async def save_global_settings(payload: Dict[str, Any]):
    try:
        existing = await cloudant_db.get_document(_settings_doc_id())
        timestamp = datetime.utcnow().isoformat()

        document = {
            "_id": _settings_doc_id(),
            "type": "global_settings",
            "github_token": payload.get("github_token", ""),
            "github_owner": payload.get("github_owner", ""),
            "github_repo": payload.get("github_repo", ""),
            "slack_bot_token": payload.get("slack_bot_token", ""),
            "slack_workspace_id": payload.get("slack_workspace_id", ""),
            "microsoft_client_id": payload.get("microsoft_client_id", ""),
            "microsoft_client_secret": payload.get("microsoft_client_secret", ""),
            "microsoft_tenant_id": payload.get("microsoft_tenant_id", ""),
            "updated_at": timestamp,
        }

        if existing:
            document["_rev"] = existing["_rev"]
            saved = await cloudant_db.update_document(_settings_doc_id(), document)
        else:
            document["created_at"] = timestamp
            saved = await cloudant_db.create_document(document)

        return {
            "success": True,
            "message": "Global settings saved successfully",
            "settings": _build_settings_response(saved),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(exc)}")

# Made with Bob
