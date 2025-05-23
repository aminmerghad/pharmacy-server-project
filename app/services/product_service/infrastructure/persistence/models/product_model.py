import uuid
from sqlalchemy import Column, Enum, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.dataBase import db
from app.shared.database_types import UUID
from app.services.product_service.domain.enums.product_status import ProductStatus

class ProductModel(db.Model):
    __tablename__ = 'products'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    category_id = Column(UUID(as_uuid=True), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    brand = Column(String(100), nullable=True)
    dosage_form = Column(String(50), nullable=True)
    strength = Column(String(50), nullable=True)
    package = Column(String(50), nullable=True)
    image_url = Column(String(255), nullable=True)
    status=Column(Enum(ProductStatus), nullable=False, default=ProductStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    inventory = relationship('InventoryModel', back_populates='product', uselist=False)

    def to_json(self):
        return {
            "id":self.id,
            "category_id":self.category_id,
            "name":self.name,
            "description":self.description ,
            "brand":self.brand, 
            "dosage_form": self.dosage_form,
            "strength" : self.strength,
            "package" : self.package,
            "image_url" : self.image_url,
            "created_at" : self.created_at,
            "updated_at" : self.updated_at

        }