from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class ProductItemContract(BaseModel):
    """Contract for individual product items"""
    id: UUID
    name: str
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    current_price: Optional[float] = None
    regular_price: Optional[float] = None
    discount_price: Optional[float] = None
    discount_start_date: Optional[datetime] = None
    discount_end_date: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProductListContract(BaseModel):
    """Contract for product list responses"""
    items: List[ProductItemContract]
    total_items: int
    page: int
    page_size: int
    total_pages: int

class GetProductRequestContract(BaseModel):
    """Contract for requesting a product by ID"""
    product_id: UUID

class GetProductsRequestContract(BaseModel):
    """Contract for listing products with pagination"""
    page: int = 1
    page_size: int = 20
    filters: Dict[str, Any] = {}

class SearchProductsRequestContract(BaseModel):
    """Contract for searching products"""
    search_term: str
    page: int = 1
    page_size: int = 20

class CategoryProductsRequestContract(BaseModel):
    """Contract for retrieving products by category"""
    category_id: UUID
    page: int = 1
    page_size: int = 20
