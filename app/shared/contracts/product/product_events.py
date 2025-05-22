from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class ProductCreatedEvent(BaseModel):
    """
    Event contract for product creation.
    """
    id: str
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    category_id: Optional[str] = None
    status: str
    timestamp: str


class ProductUpdatedEvent(BaseModel):
    """
    Event contract for product update.
    """
    id: str
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    category_id: Optional[str] = None
    status: str
    timestamp: str


class ProductDeletedEvent(BaseModel):
    """
    Event contract for product deletion.
    """
    id: str
    name: str
    timestamp: str


class ProductStatusChangedEvent(BaseModel):
    """
    Event contract for product status change.
    """
    id: str
    name: str
    old_status: str
    new_status: str
    timestamp: str 