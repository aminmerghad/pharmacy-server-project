from dataclasses import dataclass
from typing import Optional

@dataclass
class ListAccessCodesQuery:
    """Query for listing access codes with optional filtering"""
    # Search parameters
    search: Optional[str] = None
    
    # Filter parameters
    email: Optional[str] = None
    is_used: Optional[bool] = None
    is_active: Optional[bool] = True
    role: Optional[str] = None
    
    # Pagination parameters
    page: int = 1
    page_size: int = 20
    
    # Sorting
    sort_by: Optional[str] = "created_at"
    sort_order: str = "desc"  # asc or desc
