"""
SLA Term database models
"""
from sqlalchemy import Column, String, DateTime, Numeric, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class MetricType(str, enum.Enum):
    """SLA metric type enumeration"""
    UPTIME = "uptime"
    RESPONSE_TIME = "response_time"
    RESOLUTION_TIME = "resolution_time"
    AVAILABILITY = "availability"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"


class ThresholdUnit(str, enum.Enum):
    """Threshold unit enumeration"""
    PERCENTAGE = "percentage"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    REQUESTS_PER_SECOND = "requests_per_second"
    COUNT = "count"


class MeasurementPeriod(str, enum.Enum):
    """Measurement period enumeration"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class SLATerm(Base):
    """
    SLA Term model representing service level agreement terms
    """
    __tablename__ = "sla_terms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Metric details
    metric_name = Column(String(100), nullable=False)
    metric_type = Column(SQLEnum(MetricType), nullable=False)
    metric_description = Column(String(500))
    
    # Threshold
    threshold_value = Column(Numeric(10, 4), nullable=False)
    threshold_unit = Column(SQLEnum(ThresholdUnit), nullable=False)
    
    # Penalty
    penalty_amount = Column(Numeric(15, 2))
    penalty_currency = Column(String(10), default="USD")
    penalty_description = Column(String(500))
    
    # Measurement
    measurement_period = Column(SQLEnum(MeasurementPeriod), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    contract = relationship("Contract", back_populates="sla_terms")
    compliance_metrics = relationship("ComplianceMetric", back_populates="sla_term", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SLATerm {self.metric_name} - {self.metric_type.value}>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "contract_id": str(self.contract_id),
            "metric_name": self.metric_name,
            "metric_type": self.metric_type.value,
            "metric_description": self.metric_description,
            "threshold_value": float(self.threshold_value),
            "threshold_unit": self.threshold_unit.value,
            "penalty_amount": float(self.penalty_amount) if self.penalty_amount else None,
            "penalty_currency": self.penalty_currency,
            "penalty_description": self.penalty_description,
            "measurement_period": self.measurement_period.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

# Made with Bob
