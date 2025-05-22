from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.dataBase import db

class AccessCodeModel(db.Model):
    """Database model for access codes"""
    __tablename__ = "access_codes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String, nullable=False, unique=True, index=True)
    health_care_center_id = Column(UUID(as_uuid=True), ForeignKey("health_care_centers.id"), nullable=True)
    is_used = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationship with health care center
    health_care_center = relationship("HealthCareCenterModel")
    
    
 

    