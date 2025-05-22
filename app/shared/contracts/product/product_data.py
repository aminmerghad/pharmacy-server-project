from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ProductContract(BaseModel):
    """
    Contract for product data shared between services.
    """
    id: str
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    category_id: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    package: Optional[str] = None
    image_url: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    is_prescription_required: bool = False
    tax_rate: Optional[float] = None
    is_active: bool = True
    package_size: Optional[str] = None
    manufacturer: Optional[str] = None
    status: str = "active"


class ProductListContract(BaseModel):
    """
    Contract for a list of products with pagination information.
    """
    items: List[ProductContract]
    total_items: int
    page: int
    page_size: int
    total_pages: int


class ProductSearchRequestContract(BaseModel):
    """
    Contract for product search requests.
    """
    search_term: Optional[str] = None
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    page: int = 1
    page_size: int = 20 