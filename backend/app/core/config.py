"""
Configuration settings for the Contract Intelligence System
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "Contract Intelligence System"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:5173"]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # IBM Cloudant Database
    CLOUDANT_URL: str = ""
    CLOUDANT_API_KEY: str = ""
    CLOUDANT_DB_NAME: str = "contract-intelligence"
    
    # IBM watsonx.ai
    WATSONX_API_KEY: str = ""
    WATSONX_PROJECT_ID: str = ""
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    WATSONX_MODEL_ID: str = "meta-llama/llama-3-3-70b-instruct"
    
    # Watson Discovery
    DISCOVERY_API_KEY: str = ""
    DISCOVERY_URL: str = ""
    DISCOVERY_VERSION: str = "2023-03-31"
    DISCOVERY_COLLECTION_ID: str = ""
    
    # watsonx Orchestrate
    ORCHESTRATE_API_KEY: str = ""
    ORCHESTRATE_URL: str = ""
    ORCHESTRATE_INSTANCE_ID: str = ""
    
    # IBM Cloud Object Storage
    COS_API_KEY: str = ""
    COS_INSTANCE_ID: str = ""
    COS_ENDPOINT: str = ""
    COS_BUCKET_NAME: str = "contract-files"
    
    # GitHub Integration
    GITHUB_TOKEN: str = ""
    GITHUB_OWNER: str = ""
    GITHUB_REPO: str = ""
    
    # Slack Integration
    SLACK_BOT_TOKEN: str = ""
    SLACK_WORKSPACE_ID: str = ""
    
    # Microsoft Graph API (Outlook)
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT_ID: str = ""
    
    # IBM Event Streams (Kafka)
    KAFKA_BROKERS: str = ""
    KAFKA_API_KEY: str = ""
    KAFKA_TOPIC_COMPLIANCE: str = "compliance-metrics"
    KAFKA_TOPIC_ALERTS: str = "alerts"
    
    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: Union[List[str], str] = [".pdf", ".docx", ".doc"]
    
    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    # Agent Configuration
    CONTRACT_AGENT_ENABLED: bool = True
    COMPLIANCE_AGENT_ENABLED: bool = True
    RISK_AGENT_ENABLED: bool = True
    ALERT_AGENT_ENABLED: bool = True
    FORECAST_AGENT_ENABLED: bool = True
    
    # Compliance Monitoring
    COMPLIANCE_CHECK_INTERVAL: int = 300  # seconds (5 minutes)
    RISK_ASSESSMENT_INTERVAL: int = 3600  # seconds (1 hour)
    
    # Alert Thresholds
    ALERT_CRITICAL_THRESHOLD: float = 0.95  # 95% of SLA threshold
    ALERT_HIGH_THRESHOLD: float = 0.85  # 85% of SLA threshold
    ALERT_MEDIUM_THRESHOLD: float = 0.75  # 75% of SLA threshold
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    


# Create settings instance
settings = Settings()

# Made with Bob
