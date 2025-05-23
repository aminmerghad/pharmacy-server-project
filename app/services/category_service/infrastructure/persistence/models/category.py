from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from app.dataBase import db
from app.shared.database_types import UUID

class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    parent_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), nullable=True)
    image_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Category {self.name}>" 