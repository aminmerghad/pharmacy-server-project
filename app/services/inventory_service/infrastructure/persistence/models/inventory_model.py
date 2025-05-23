from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Float, String, Text
from sqlalchemy.orm import relationship
from app.shared.database_types import UUID
from app.dataBase import db

class InventoryModel(db.Model):
    __tablename__ = 'inventory'
    
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'))
    quantity = Column(Integer)
    price = Column(Float)
    max_stock = Column(Integer)
    min_stock = Column(Integer)
    last_updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expiry_date = Column(DateTime(timezone=True))
    supplier_id = Column(UUID(as_uuid=True), nullable=True)
    
    # New fields for enhanced inventory tracking
    # batch_number = Column(String(50), nullable=True)
    # lot_number = Column(String(50), nullable=True)
    # manufacturer = Column(String(100), nullable=True)
    # supplier_id = Column(UUID(as_uuid=True), nullable=True)
    # location_code = Column(String(50), nullable=True)
    # notes = Column(Text, nullable=True)
    # reorder_point = Column(Integer, nullable=True)
    # lead_time_days = Column(Integer, nullable=True)
    # last_restock_date = Column(DateTime(timezone=True), nullable=True)
    # last_count_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    product = db.relationship('ProductModel', back_populates='inventory')
    movements = db.relationship('StockMovementModel', back_populates='inventory', cascade="all, delete-orphan")
    # batches = db.relationship('BatchModel', back_populates='inventory', cascade="all, delete-orphan")
    
    def __repr__(self):
        return (f"<Inventory(id={self.id}, product_id={self.product_id}, "
                f"quantity={self.quantity})>")
    
    def to_json(self):
        return{
            "id":self.id,
            "product_id":self.product_id,
            "quantity":self.quantity,
            "price":self.price,
            "max_stock":self.max_stock,
            "min_stock":self.min_stock,
            # "last_updated_at":self.last_updated_at,
            "expiry_date":self.expiry_date,
            "supplier_id":self.supplier_id

        }