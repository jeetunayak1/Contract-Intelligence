"""
Jira Service
Loads and manages operational metrics
"""
import json
import os
from typing import Dict, Any
from pathlib import Path
import logging

from ..models.compliance_models import JiraMetrics

logger = logging.getLogger(__name__)


class JiraService:
    """Service for managing Jira metrics"""
    
    def __init__(self):
        """Initialize Jira service"""
        self.mock_data_path = Path(__file__).parent.parent / "mock_data" / "jira_metrics.json"
        self._metrics_cache = None
    
    def load_metrics(self) -> JiraMetrics:
        """
        Load metrics from mock data file
        
        Returns:
            Jira metrics object
        """
        try:
            if self._metrics_cache is not None:
                return self._metrics_cache
            
            if not self.mock_data_path.exists():
                logger.warning(f"Mock data file not found: {self.mock_data_path}")
                return self._get_empty_metrics()
            
            with open(self.mock_data_path, 'r') as f:
                data = json.load(f)
            
            metrics = JiraMetrics(**data)
            self._metrics_cache = metrics
            
            logger.info("Loaded Jira metrics successfully")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to load Jira metrics: {e}")
            return self._get_empty_metrics()
    
    def _get_empty_metrics(self) -> JiraMetrics:
        """Return empty metrics structure"""
        return JiraMetrics(
            sprint_metrics={},
            quality_metrics={},
            performance_metrics={},
            delivery_metrics={},
            customer_satisfaction={},
            resource_utilization={},
            compliance_metrics={}
        )
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """
        Get quality-specific metrics
        
        Returns:
            Quality metrics dictionary
        """
        metrics = self.load_metrics()
        return metrics.quality_metrics
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance-specific metrics
        
        Returns:
            Performance metrics dictionary
        """
        metrics = self.load_metrics()
        return metrics.performance_metrics
    
    def get_sprint_metrics(self) -> Dict[str, Any]:
        """
        Get sprint-specific metrics
        
        Returns:
            Sprint metrics dictionary
        """
        metrics = self.load_metrics()
        return metrics.sprint_metrics
    
    def get_customer_satisfaction(self) -> Dict[str, Any]:
        """
        Get customer satisfaction metrics
        
        Returns:
            Customer satisfaction dictionary
        """
        metrics = self.load_metrics()
        return metrics.customer_satisfaction
    
    def get_metric_value(self, category: str, metric_name: str) -> Any:
        """
        Get specific metric value
        
        Args:
            category: Metric category (quality_metrics, performance_metrics, etc.)
            metric_name: Name of the metric
            
        Returns:
            Metric value or None if not found
        """
        metrics = self.load_metrics()
        category_data = getattr(metrics, category, {})
        return category_data.get(metric_name)
    
    def get_all_metrics_flat(self) -> Dict[str, Any]:
        """
        Get all metrics in a flat dictionary
        
        Returns:
            Flattened metrics dictionary
        """
        metrics = self.load_metrics()
        flat_metrics = {}
        
        for category in ['sprint_metrics', 'quality_metrics', 'performance_metrics',
                        'delivery_metrics', 'customer_satisfaction', 'resource_utilization',
                        'compliance_metrics']:
            category_data = getattr(metrics, category, {})
            for key, value in category_data.items():
                flat_metrics[f"{category}.{key}"] = value
        
        return flat_metrics
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of key metrics
        
        Returns:
            Summary dictionary
        """
        metrics = self.load_metrics()
        
        return {
            "quality": {
                "unit_test_coverage": metrics.quality_metrics.get("unit_test_coverage", 0),
                "code_review_coverage": metrics.quality_metrics.get("code_review_coverage", 0),
                "critical_bugs": metrics.quality_metrics.get("critical_bug_escape_count", 0),
                "security_vulnerabilities": metrics.quality_metrics.get("security_vulnerabilities_critical", 0)
            },
            "performance": {
                "availability_tier1": metrics.performance_metrics.get("availability_tier1", 0),
                "error_rate": metrics.performance_metrics.get("error_rate_percent", 0),
                "api_response_p95": metrics.performance_metrics.get("api_response_time_p95", 0)
            },
            "delivery": {
                "sprint_velocity": metrics.sprint_metrics.get("sprint_velocity", 0),
                "sprint_velocity_variance": metrics.sprint_metrics.get("sprint_velocity_variance", 0),
                "deployment_frequency": metrics.delivery_metrics.get("deployment_frequency", 0)
            },
            "customer": {
                "csat_score": metrics.customer_satisfaction.get("csat_score", 0),
                "nps_score": metrics.customer_satisfaction.get("nps_score", 0)
            }
        }
    
    def clear_cache(self):
        """Clear metrics cache"""
        self._metrics_cache = None


# Singleton instance
_jira_service = None


def get_jira_service() -> JiraService:
    """Get or create Jira service singleton"""
    global _jira_service
    if _jira_service is None:
        _jira_service = JiraService()
    return _jira_service

# Made with Bob
