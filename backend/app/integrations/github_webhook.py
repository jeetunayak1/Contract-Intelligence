"""
GitHub Webhook Integration
Handles incoming GitHub issue webhooks and triggers autonomous compliance analysis
"""
import logging
import hmac
import hashlib
from typing import Optional, Dict, Any

from app.models.event_models import GitHubWebhookPayload, WebhookResponse
from app.services.incident_service import get_incident_service

logger = logging.getLogger(__name__)


class GitHubWebhookHandler:
    """
    Handles GitHub webhook events
    Automatically creates incidents and triggers compliance analysis
    """
    
    def __init__(self, webhook_secret: Optional[str] = None):
        self.webhook_secret = webhook_secret
        self.incident_service = get_incident_service()
        
        # Events that trigger incident creation
        self.trigger_actions = {'opened', 'reopened'}
    
    def verify_signature(
        self,
        payload_body: bytes,
        signature_header: str
    ) -> bool:
        """
        Verify GitHub webhook signature
        Returns True if signature is valid
        """
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured, skipping signature verification")
            return True
        
        if not signature_header:
            return False
        
        hash_algorithm, github_signature = signature_header.split('=')
        
        if hash_algorithm != 'sha256':
            return False
        
        mac = hmac.new(
            self.webhook_secret.encode(),
            msg=payload_body,
            digestmod=hashlib.sha256
        )
        
        return hmac.compare_digest(mac.hexdigest(), github_signature)
    
    async def handle_issues_event(
        self,
        payload: GitHubWebhookPayload
    ) -> WebhookResponse:
        """
        Handle GitHub issues webhook event
        Creates incident and triggers compliance analysis if needed
        """
        try:
            action = payload.action
            issue = payload.issue
            
            logger.info(f"Received GitHub issue event: action={action}, issue=#{issue.number}")
            
            # Only process certain actions
            if action not in self.trigger_actions:
                return WebhookResponse(
                    success=True,
                    message=f"Action '{action}' does not trigger incident creation",
                    triggered_analysis=False
                )
            
            # Extract labels
            labels = [label.get('name', '') for label in issue.labels]
            
            # Check if this is an incident (has incident label or priority in title)
            is_incident = (
                'incident' in labels or
                self.incident_service.detect_priority(issue.title) is not None
            )
            
            if not is_incident:
                return WebhookResponse(
                    success=True,
                    message="Issue does not appear to be an incident",
                    triggered_analysis=False
                )
            
            # Create incident
            incident = await self.incident_service.create_incident_from_github(
                issue_number=issue.number,
                title=issue.title,
                body=issue.body,
                labels=labels
            )
            
            # Check if should trigger automatic analysis
            should_trigger = self.incident_service.should_trigger_analysis(incident.priority)
            
            response = WebhookResponse(
                success=True,
                message=f"Incident {incident.incident_id} created from GitHub issue #{issue.number}",
                incident_id=incident.incident_id,
                triggered_analysis=should_trigger
            )
            
            if should_trigger:
                logger.info(f"Incident {incident.incident_id} will trigger automatic compliance analysis")
                # Note: Actual crew triggering will be done by the API endpoint
                # to avoid blocking the webhook response
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to handle GitHub webhook: {e}", exc_info=True)
            raise Exception(f"Failed to process webhook: {str(e)}")
    
    async def handle_issue_comment_event(
        self,
        payload: Dict[str, Any]
    ) -> WebhookResponse:
        """
        Handle GitHub issue comment webhook event
        Can be used for incident updates or commands
        """
        try:
            action = payload.get('action')
            issue = payload.get('issue', {})
            comment = payload.get('comment', {})
            
            logger.info(f"Received GitHub comment event: action={action}, issue=#{issue.get('number')}")
            
            # For now, just acknowledge the event
            # Future: Could parse commands like "/resolve" or "/escalate"
            
            return WebhookResponse(
                success=True,
                message="Comment event received",
                triggered_analysis=False
            )
            
        except Exception as e:
            logger.error(f"Failed to handle comment webhook: {e}", exc_info=True)
            raise Exception(f"Failed to process webhook: {str(e)}")


# Singleton instance
_github_webhook_handler = None


def get_github_webhook_handler(webhook_secret: Optional[str] = None) -> GitHubWebhookHandler:
    """Get or create GitHub webhook handler singleton"""
    global _github_webhook_handler
    if _github_webhook_handler is None:
        _github_webhook_handler = GitHubWebhookHandler(webhook_secret)
    return _github_webhook_handler


# Made with Bob - GitHub Webhook Integration