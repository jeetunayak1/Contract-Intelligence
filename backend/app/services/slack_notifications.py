"""
Slack Notifications Service
Sends alerts and notifications to Slack channels via webhooks
"""
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from app.core.cloudant_db import cloudant_db

logger = logging.getLogger(__name__)


class SlackNotificationService:
    """Service for sending Slack notifications"""
    
    def __init__(self):
        self.webhook_url = None
    
    async def _get_webhook_url(self) -> Optional[str]:
        """Get Slack webhook URL from settings"""
        try:
            settings = await cloudant_db.get_document("global_api_settings")
            if settings and isinstance(settings, dict):
                return settings.get("slack_webhook_url")
        except Exception as e:
            logger.error(f"Failed to get Slack webhook URL: {e}")
        return None
    
    async def send_notification(
        self,
        title: str,
        message: str,
        color: str = "#36a64f",
        fields: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Send a notification to Slack
        
        Args:
            title: Notification title
            message: Notification message
            color: Color bar (good=#36a64f, warning=#ff9800, danger=#f44336)
            fields: Additional fields to display
            
        Returns:
            True if sent successfully
        """
        webhook_url = await self._get_webhook_url()
        
        if not webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False
        
        try:
            payload = {
                "attachments": [{
                    "color": color,
                    "title": title,
                    "text": message,
                    "fields": fields or [],
                    "footer": "SOW Sentinel",
                    "ts": int(datetime.utcnow().timestamp())
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"Slack notification sent: {title}")
                return True
            else:
                logger.error(f"Slack notification failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    async def send_sla_breach_alert(
        self,
        sow_id: str,
        sow_name: str,
        at_risk_count: int,
        penalty_exposure: float
    ) -> bool:
        """Send alert for SLA breach risk"""
        return await self.send_notification(
            title=f"🚨 SLA Breach Alert: {sow_name}",
            message=f"SOW {sow_id} has {at_risk_count} SLAs at risk",
            color="#f44336",  # Red
            fields=[
                {
                    "title": "At-Risk SLAs",
                    "value": str(at_risk_count),
                    "short": True
                },
                {
                    "title": "Penalty Exposure",
                    "value": f"${penalty_exposure:,.0f}",
                    "short": True
                }
            ]
        )
    
    async def send_high_penalty_warning(
        self,
        sow_id: str,
        sow_name: str,
        total_exposure: float,
        immediate_exposure: float
    ) -> bool:
        """Send warning for high penalty exposure"""
        return await self.send_notification(
            title=f"⚠️ High Penalty Exposure: {sow_name}",
            message=f"SOW {sow_id} has significant penalty exposure",
            color="#ff9800",  # Orange
            fields=[
                {
                    "title": "Total Exposure",
                    "value": f"${total_exposure:,.0f}",
                    "short": True
                },
                {
                    "title": "Immediate Risk",
                    "value": f"${immediate_exposure:,.0f}",
                    "short": True
                }
            ]
        )
    
    async def send_breach_probability_alert(
        self,
        sow_id: str,
        sow_name: str,
        probability: float,
        risk_level: str
    ) -> bool:
        """Send alert for high breach probability"""
        color = "#f44336" if probability > 0.7 else "#ff9800"
        
        return await self.send_notification(
            title=f"📊 Breach Probability Alert: {sow_name}",
            message=f"SOW {sow_id} has {probability*100:.1f}% breach probability",
            color=color,
            fields=[
                {
                    "title": "Breach Probability",
                    "value": f"{probability*100:.1f}%",
                    "short": True
                },
                {
                    "title": "Risk Level",
                    "value": risk_level.upper(),
                    "short": True
                }
            ]
        )
    
    async def send_daily_summary(
        self,
        total_sows: int,
        at_risk_sows: int,
        total_exposure: float,
        critical_items: List[str]
    ) -> bool:
        """Send daily summary notification"""
        fields = [
            {
                "title": "Total SOWs Monitored",
                "value": str(total_sows),
                "short": True
            },
            {
                "title": "SOWs At Risk",
                "value": str(at_risk_sows),
                "short": True
            },
            {
                "title": "Total Penalty Exposure",
                "value": f"${total_exposure:,.0f}",
                "short": True
            }
        ]
        
        if critical_items:
            fields.append({
                "title": "Critical Items",
                "value": "\n".join(f"• {item}" for item in critical_items[:5]),
                "short": False
            })
        
        return await self.send_notification(
            title="📈 Daily SOW Monitoring Summary",
            message=f"Summary for {datetime.utcnow().strftime('%Y-%m-%d')}",
            color="#36a64f",  # Green
            fields=fields
        )
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Slack webhook connection"""
        webhook_url = await self._get_webhook_url()
        
        if not webhook_url:
            return {
                "success": False,
                "message": "Slack webhook URL not configured"
            }
        
        success = await self.send_notification(
            title="✅ Test Notification",
            message="Slack integration is working correctly!",
            color="#36a64f"
        )
        
        return {
            "success": success,
            "message": "Test notification sent successfully" if success else "Failed to send test notification"
        }


# Global instance
slack_service = SlackNotificationService()

# Made with Bob