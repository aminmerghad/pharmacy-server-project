import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.dataBase import db
from app.shared.database_types import UUID
from app.services.inventory_service.domain.enums.movement_type import MovementType


class StockMovementModel(db.Model):
    """
    Database model for tracking all movements of inventory stock.
    
    This model maintains a complete audit trail of all stock changes,
    enabling detailed reporting and analysis of inventory operations.
    """
    __tablename__ = 'stock_movements'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey('inventory.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    movement_type = Column(Enum(MovementType), nullable=False)
    reference_id = Column(UUID(as_uuid=True), nullable=True)  # Order ID, Transfer ID, etc.
    batch_number = Column(String(50), nullable=True)
    reason = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    inventory = relationship('InventoryModel', back_populates='movements')
    created_by_user = relationship('UserModel')
    
    def __repr__(self):
        return (f"<StockMovement(id={self.id}, inventory_id={self.inventory_id}, "
                f"quantity={self.quantity}, movement_type={self.movement_type})>") 