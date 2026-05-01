"""
Contract database models
"""
from sqlalchemy import Column, String, Date, DateTime, Text, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class ContractStatus(str, enum.Enum):
    """Contract status enumeration"""
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"
    TERMINATED = "terminated"
    RENEWED = "renewed"


class ContractType(str, enum.Enum):
    """Contract type enumeration"""
    SERVICE = "service"
    MAINTENANCE = "maintenance"
    SUBSCRIPTION = "subscription"
    LICENSE = "license"
    SUPPORT = "support"


class Contract(Base):
    """
    Contract model representing customer contracts
    """
    __tablename__ = "contracts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_number = Column(String(100), unique=True, nullable=False, index=True)
    customer_name = Column(String(255), nullable=False, index=True)
    contract_type = Column(SQLEnum(ContractType), nullable=False)
    
    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    renewal_date = Column(Date)
    
    # Status
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.ACTIVE, nullable=False)
    
    # File information
    file_url = Column(Text)
    file_name = Column(String(255))
    file_size = Column(Numeric)
    
    # Financial
    total_value = Column(Numeric(15, 2))
    currency = Column(String(10), default="USD")
    
    # Metadata
    description = Column(Text)
    tags = Column(ARRAY(String), default=[])
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    sla_terms = relationship("SLATerm", back_populates="contract", cascade="all, delete-orphan")
    compliance_metrics = relationship("ComplianceMetric", back_populates="contract", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="contract", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="contract", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Contract {self.contract_number} - {self.customer_name}>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "contract_number": self.contract_number,
            "customer_name": self.customer_name,
            "contract_type": self.contract_type.value,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "renewal_date": self.renewal_date.isoformat() if self.renewal_date else None,
            "status": self.status.value,
            "file_url": self.file_url,
            "file_name": self.file_name,
            "total_value": float(self.total_value) if self.total_value else None,
            "currency": self.currency,
            "description": self.description,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

# Made with Bob
