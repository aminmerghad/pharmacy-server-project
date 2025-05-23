import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime
from app.shared.database_types import UUID
from app.dataBase import db

class HealthCareCenterModel(db.Model):
    __tablename__ = 'health_care_centers'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    license_number = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    users = db.relationship('UserModel', back_populates='health_care_center')

    def __repr__(self):
        return f"<HealthCareCenter {self.name}>" 