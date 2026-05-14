"""
Outlook Email Notifications Service
Sends alerts and notifications via Microsoft Graph API (Outlook/Office 365)
"""
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from app.core.cloudant_db import cloudant_db

logger = logging.getLogger(__name__)


class OutlookNotificationService:
    """Service for sending Outlook email notifications via Microsoft Graph API"""
    
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.tenant_id = None
        self.access_token = None
        self.token_expiry = None
    
    async def _get_credentials(self) -> Dict[str, Optional[str]]:
        """Get Outlook/Microsoft credentials from settings"""
        try:
            settings = await cloudant_db.get_document("global_api_settings")
            if settings and isinstance(settings, dict):
                return {
                    "client_id": settings.get("microsoft_client_id"),
                    "client_secret": settings.get("microsoft_client_secret"),
                    "tenant_id": settings.get("microsoft_tenant_id"),
                    "sender_email": settings.get("microsoft_sender_email")
                }
        except Exception as e:
            logger.error(f"Failed to get Outlook credentials: {e}")
        return {
            "client_id": None,
            "client_secret": None,
            "tenant_id": None,
            "sender_email": None
        }
    
    async def _get_access_token(self) -> Optional[str]:
        """Get Microsoft Graph API access token using client credentials flow"""
        # Check if we have a valid cached token
        if self.access_token and self.token_expiry:
            if datetime.utcnow() < self.token_expiry:
                return self.access_token
        
        credentials = await self._get_credentials()
        client_id = credentials.get("client_id")
        client_secret = credentials.get("client_secret")
        tenant_id = credentials.get("tenant_id")
        
        if not all([client_id, client_secret, tenant_id]):
            logger.warning("Outlook credentials not fully configured")
            return None
        
        try:
            # Microsoft OAuth2 token endpoint
            token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
            
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials"
            }
            
            response = requests.post(token_url, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                # Set expiry to 5 minutes before actual expiry for safety
                expires_in = token_data.get("expires_in", 3600)
                from datetime import timedelta
                self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 300)
                logger.info("Successfully obtained Microsoft Graph API access token")
                return self.access_token
            else:
                logger.error(f"Failed to get access token: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get access token (Request Error): {type(e).__name__}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Failed to get access token (Unexpected Error): {type(e).__name__}: {str(e)}")
            return None
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        importance: str = "normal"
    ) -> bool:
        """
        Send an email via Microsoft Graph API
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body_html: HTML body content
            body_text: Plain text body (optional, defaults to HTML)
            cc_emails: List of CC email addresses (optional)
            importance: Email importance (low, normal, high)
            
        Returns:
            True if sent successfully
        """
        access_token = await self._get_access_token()
        
        if not access_token:
            logger.warning("Outlook access token not available")
            return False
        
        credentials = await self._get_credentials()
        sender_email = credentials.get("sender_email")
        
        if not sender_email:
            logger.warning("Sender email not configured")
            return False
        
        try:
            # Microsoft Graph API endpoint for sending mail
            send_mail_url = f"https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail"
            
            # Build recipients list
            to_recipients = [{"emailAddress": {"address": email}} for email in to_emails]
            cc_recipients = [{"emailAddress": {"address": email}} for email in (cc_emails or [])]
            
            # Build email message
            message = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "HTML",
                        "content": body_html
                    },
                    "toRecipients": to_recipients,
                    "importance": importance
                },
                "saveToSentItems": "true"
            }
            
            if cc_recipients:
                message["message"]["ccRecipients"] = cc_recipients
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(send_mail_url, json=message, headers=headers, timeout=10)
            
            if response.status_code == 202:  # Accepted
                logger.info(f"Email sent successfully: {subject}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send email (Request Error): {type(e).__name__}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email (Unexpected Error): {type(e).__name__}: {str(e)}")
            return False
    
    def _build_html_email(
        self,
        title: str,
        message: str,
        fields: Optional[List[Dict[str, Any]]] = None,
        color: str = "#4caf50"
    ) -> str:
        """Build HTML email content"""
        fields_html = ""
        if fields:
            fields_html = "<table style='width: 100%; margin-top: 20px; border-collapse: collapse;'>"
            for field in fields:
                fields_html += f"""
                <tr>
                    <td style='padding: 8px; border-bottom: 1px solid #e0e0e0; font-weight: bold; width: 40%;'>
                        {field.get('title', '')}
                    </td>
                    <td style='padding: 8px; border-bottom: 1px solid #e0e0e0;'>
                        {field.get('value', '')}
                    </td>
                </tr>
                """
            fields_html += "</table>"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="border-left: 4px solid {color}; padding-left: 20px; margin-bottom: 20px;">
                <h2 style="color: {color}; margin: 0 0 10px 0;">{title}</h2>
                <p style="margin: 0; color: #666;">{message}</p>
            </div>
            {fields_html}
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; color: #999; font-size: 12px;">
                <p style="margin: 0;">SOW Sentinel - Contract Intelligence Platform</p>
                <p style="margin: 5px 0 0 0;">Sent on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            </div>
        </body>
        </html>
        """
        return html
    
    async def send_sla_breach_alert(
        self,
        to_emails: List[str],
        sow_id: str,
        sow_name: str,
        at_risk_count: int,
        penalty_exposure: float
    ) -> bool:
        """Send alert for SLA breach risk"""
        subject = f"🚨 SLA Breach Alert: {sow_name}"
        
        html_body = self._build_html_email(
            title=f"SLA Breach Alert: {sow_name}",
            message=f"SOW {sow_id} has {at_risk_count} SLAs at risk of breach.",
            fields=[
                {"title": "SOW ID", "value": sow_id},
                {"title": "At-Risk SLAs", "value": str(at_risk_count)},
                {"title": "Penalty Exposure", "value": f"${penalty_exposure:,.0f}"}
            ],
            color="#f44336"  # Red
        )
        
        return await self.send_email(
            to_emails=to_emails,
            subject=subject,
            body_html=html_body,
            importance="high"
        )
    
    async def send_high_penalty_warning(
        self,
        to_emails: List[str],
        sow_id: str,
        sow_name: str,
        total_exposure: float,
        immediate_exposure: float
    ) -> bool:
        """Send warning for high penalty exposure"""
        subject = f"⚠️ High Penalty Exposure: {sow_name}"
        
        html_body = self._build_html_email(
            title=f"High Penalty Exposure Warning: {sow_name}",
            message=f"SOW {sow_id} has significant penalty exposure that requires attention.",
            fields=[
                {"title": "SOW ID", "value": sow_id},
                {"title": "Total Exposure", "value": f"${total_exposure:,.0f}"},
                {"title": "Immediate Risk", "value": f"${immediate_exposure:,.0f}"}
            ],
            color="#ff9800"  # Orange
        )
        
        return await self.send_email(
            to_emails=to_emails,
            subject=subject,
            body_html=html_body,
            importance="high"
        )
    
    async def send_milestone_reminder(
        self,
        to_emails: List[str],
        sow_id: str,
        sow_name: str,
        milestone_name: str,
        due_date: str,
        days_remaining: int
    ) -> bool:
        """Send reminder for upcoming milestone"""
        subject = f"📅 Milestone Reminder: {milestone_name}"
        
        html_body = self._build_html_email(
            title=f"Milestone Reminder: {milestone_name}",
            message=f"Reminder: Milestone '{milestone_name}' is due in {days_remaining} days.",
            fields=[
                {"title": "SOW ID", "value": sow_id},
                {"title": "SOW Name", "value": sow_name},
                {"title": "Milestone", "value": milestone_name},
                {"title": "Due Date", "value": due_date},
                {"title": "Days Remaining", "value": str(days_remaining)}
            ],
            color="#2196f3"  # Blue
        )
        
        return await self.send_email(
            to_emails=to_emails,
            subject=subject,
            body_html=html_body,
            importance="normal"
        )
    
    async def send_weekly_summary(
        self,
        to_emails: List[str],
        total_sows: int,
        at_risk_sows: int,
        total_exposure: float,
        critical_items: List[str]
    ) -> bool:
        """Send weekly summary email"""
        subject = f"📊 Weekly SOW Summary - {datetime.utcnow().strftime('%Y-%m-%d')}"
        
        critical_items_html = ""
        if critical_items:
            critical_items_html = "<ul style='margin: 10px 0; padding-left: 20px;'>"
            for item in critical_items[:5]:
                critical_items_html += f"<li>{item}</li>"
            critical_items_html += "</ul>"
        
        fields = [
            {"title": "Total SOWs Monitored", "value": str(total_sows)},
            {"title": "SOWs At Risk", "value": str(at_risk_sows)},
            {"title": "Total Penalty Exposure", "value": f"${total_exposure:,.0f}"}
        ]
        
        if critical_items:
            fields.append({"title": "Critical Items", "value": critical_items_html})
        
        html_body = self._build_html_email(
            title="Weekly SOW Monitoring Summary",
            message=f"Summary for week ending {datetime.utcnow().strftime('%Y-%m-%d')}",
            fields=fields,
            color="#4caf50"  # Green
        )
        
        return await self.send_email(
            to_emails=to_emails,
            subject=subject,
            body_html=html_body,
            importance="normal"
        )
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Outlook/Microsoft Graph API connection"""
        credentials = await self._get_credentials()
        
        if not all([credentials.get("client_id"), credentials.get("client_secret"), 
                   credentials.get("tenant_id"), credentials.get("sender_email")]):
            return {
                "success": False,
                "message": "Outlook credentials not fully configured. Please provide Client ID, Client Secret, Tenant ID, and Sender Email."
            }
        
        # Try to get access token
        access_token = await self._get_access_token()
        
        if not access_token:
            return {
                "success": False,
                "message": "Failed to obtain access token. Please check your credentials."
            }
        
        # Send test email to sender (self)
        sender_email = credentials.get("sender_email")
        if not sender_email:
            return {
                "success": False,
                "message": "Sender email not configured"
            }
        
        success = await self.send_email(
            to_emails=[sender_email],
            subject="✅ Test Email - SOW Sentinel",
            body_html=self._build_html_email(
                title="Test Email Successful",
                message="Outlook integration is working correctly! This is a test email from SOW Sentinel.",
                fields=[
                    {"title": "Status", "value": "✅ Connected"},
                    {"title": "API", "value": "Microsoft Graph API"},
                    {"title": "Test Time", "value": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
                ],
                color="#4caf50"
            ),
            importance="normal"
        )
        
        return {
            "success": success,
            "message": f"Test email sent successfully to {sender_email}" if success else "Failed to send test email"
        }


# Global instance
outlook_service = OutlookNotificationService()

# Made with Bob