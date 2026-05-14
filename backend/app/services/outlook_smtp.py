"""
Gmail SMTP Email Notifications Service
Sends alerts and notifications via Gmail SMTP (works with App Passwords)
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from app.core.cloudant_db import cloudant_db

logger = logging.getLogger(__name__)


class OutlookSMTPService:
    """Service for sending email notifications via Gmail SMTP"""
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    async def _get_credentials(self) -> Dict[str, Optional[str]]:
        """Get Gmail SMTP credentials from settings"""
        try:
            settings = await cloudant_db.get_document("global_api_settings")
            if settings and isinstance(settings, dict):
                return {
                    "email": settings.get("outlook_email"),
                    "password": settings.get("outlook_password")
                }
        except Exception as e:
            logger.error(f"Failed to get Gmail credentials: {e}")
        return {"email": None, "password": None}
    
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
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body_html: str,
        importance: str = "normal"
    ) -> bool:
        """
        Send an email via Gmail SMTP
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body_html: HTML body content
            importance: Email importance (low, normal, high)
            
        Returns:
            True if sent successfully
        """
        credentials = await self._get_credentials()
        email = credentials.get("email")
        password = credentials.get("password")
        
        if not email or not password:
            logger.warning("Gmail SMTP credentials not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Set importance
            if importance == "high":
                msg['X-Priority'] = '1'
                msg['Importance'] = 'high'
            
            # Attach HTML body
            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(email, password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully: {subject}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {str(e)}")
            logger.error("Please check your email and App Password. Make sure you're using a Gmail App Password, not your regular password.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {type(e).__name__}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {type(e).__name__}: {str(e)}")
            return False
    
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
        """Test Gmail SMTP connection"""
        credentials = await self._get_credentials()
        email = credentials.get("email")
        password = credentials.get("password")
        
        if not email or not password:
            return {
                "success": False,
                "message": "Gmail email and App Password not configured. Please enter your credentials in Settings."
            }
        
        # Send test email to self
        success = await self.send_email(
            to_emails=[email],
            subject="✅ Test Email - SOW Sentinel",
            body_html=self._build_html_email(
                title="Test Email Successful",
                message="Gmail SMTP integration is working correctly! This is a test email from SOW Sentinel.",
                fields=[
                    {"title": "Status", "value": "✅ Connected"},
                    {"title": "Method", "value": "Gmail SMTP"},
                    {"title": "Test Time", "value": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
                ],
                color="#4caf50"
            ),
            importance="normal"
        )
        
        if success:
            return {
                "success": True,
                "message": f"Test email sent successfully to {email}. Check your inbox!"
            }
        else:
            return {
                "success": False,
                "message": "Failed to send test email. Please check your Gmail address and App Password. Make sure you're using an App Password from Google Account settings, not your regular Gmail password."
            }


# Global instance
outlook_smtp_service = OutlookSMTPService()

# Made with Bob