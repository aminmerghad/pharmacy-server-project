from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class ListCentersByFilterQuery:
    """Query for filtering health care centers"""
    # Search parameters
    search: Optional[str] = None
    
    # Pagination parameters
    page: int = 1
    page_size: int = 20
    
    # Filter parameters
    name: Optional[str] = None
    email: Optional[str] = None
    license_number: Optional[str] = None
    is_active: Optional[bool] = True
    
    # Sorting
    sort_by: Optional[str] = "name"
    sort_order: str = "asc"  # asc or desc
