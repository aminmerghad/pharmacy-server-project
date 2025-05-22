from datetime import datetime
import uuid
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.dataBase import db
from app.services.order_service.domain.value_objects.order_status import OrderStatus
from datetime import UTC
class OrderModel(db.Model):
    __tablename__ = 'orders'

    id = Column(UUID(as_uuid=True),default=uuid.uuid4, primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    total_amount = Column(Numeric(10, 2), nullable=False)
    notes = Column(String)
    created_at = Column(DateTime(timezone=True  ), nullable=False, default=datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")


    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'total_amount': self.total_amount,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'completed_at': self.completed_at
        }

class OrderItemModel(db.Model):
    __tablename__ = 'order_items'

    id = Column(UUID(as_uuid=True),default=uuid.uuid4, primary_key=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    # name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(UTC))

    # Relationships
    order = relationship("OrderModel", back_populates="items") 