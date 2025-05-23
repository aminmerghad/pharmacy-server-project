from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from app.dataBase import db
from app.shared.database_types import UUID

class UserModel(db.Model):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True,default=uuid4)  # Generate UUID in Python
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=lambda:datetime.now(timezone.utc))
    health_care_center_id = Column(UUID(as_uuid=True),  ForeignKey('health_care_centers.id'),nullable=True)
    health_care_center = db.relationship('HealthCareCenterModel', back_populates='users')
    

    def __repr__(self):
        return f"<User {self.username}>"

