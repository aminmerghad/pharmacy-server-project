from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.services.product_service.domain.enums.product_status import ProductStatus
from app.shared.domain.exceptions.common_errors import ValidationError
from datetime import date

class ProductFieldsDto(BaseModel):
    
    name: str
    description: str    
    id: Optional[UUID] = None
    brand: Optional[str] = None
    category_id: Optional[UUID] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    package: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[ProductStatus] = None

    def validate(self) -> None:
        """Validate product fields"""
        if not self.name.strip():
            raise ValidationError("Name must not be empty.")
            
        if len(self.description) > 500:
            raise ValidationError("Description must not exceed 500 characters.")
                        
        if self.brand and len(self.brand) > 100:
            raise ValidationError("Brand must not exceed 100 characters.")
            
        if self.dosage_form and len(self.dosage_form) > 50:
            raise ValidationError("Dosage form must not exceed 50 characters.")
            
        if self.strength and len(self.strength) > 50:
            raise ValidationError("Strength must not exceed 50 characters.")
            
            
        if self.package and len(self.package) > 50:
            raise ValidationError("Package size must not exceed 50 characters.")
            
        if self.image_url and len(self.image_url) > 255:
            raise ValidationError("Image URL must not exceed 255 characters.")

class InventoryFieldsDto(BaseModel):
    price: float
    quantity: int
    max_stock: int
    min_stock: int        
    expiry_date:date    
    supplier_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    def validate(self):
        if self.price < 0 or self.quantity < 0 or self.max_stock < 0 or self.min_stock < 0:
            raise ValidationError('the price or quantity should be > 0')

