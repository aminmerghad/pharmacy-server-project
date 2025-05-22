from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from app.services.product_service.domain.enums.product_status import ProductStatus


class ProductEntity(BaseModel):
    name: str
    description: str
    id: Optional[UUID] = None
    brand: Optional[str] = None
    category_id: Optional[UUID] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    package: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: ProductStatus
    
    
    # def get_effective_price(self) -> Optional[float]:
    #     """
    #     Get the current effective price of the product, taking into account
    #     any active discounts.
        
    #     Returns:
    #         The effective price (discount_price if applicable, otherwise current_price)
    #     """
    #     if not self.current_price:
    #         return None
            
    #     now = datetime.now()
    #     if (self.discount_price and self.discount_start_date and self.discount_end_date and
    #             self.discount_start_date <= now <= self.discount_end_date):
    #         return self.discount_price
            
    #     return self.current_price