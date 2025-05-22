from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from app.services.order_service.domain.entities.order_item import OrderItem
from app.services.order_service.domain.value_objects.order_status import OrderStatus
from app.services.order_service.domain.value_objects.money import Money
from app.services.order_service.domain.exceptions.order_errors import (
    OrderValidationError,
    InvalidOrderStatusTransition
)

@dataclass
class OrderEntity:
    id: UUID = None
    user_id: UUID = None
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = None
    total_amount : Decimal = field(default_factory=Decimal(0))
    # total_amount: Money = field(default_factory=lambda: Money(Decimal("0")))
    notes: str = None    
    created_at: datetime = None
    updated_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        # self.total_amount = self.calculate_total()
        self._validate()

    def _validate(self) -> None:
        if not self.items:
            raise OrderValidationError("Order must have at least one item")
        if any(item.quantity <= 0 for item in self.items):
            raise OrderValidationError("Item quantity must be greater than 0")

    def calculate_total(self) -> Money:
        return Money(sum((item.price * item.quantity for item in self.items), Decimal("0")))

    def add_item(self, item: OrderItem) -> None:
        if self.status != OrderStatus.PENDING:
            raise OrderValidationError("Can only add items to pending orders")
        
        existing_item = next(
            (i for i in self.items if i.product_id == item.product_id), 
            None
        )
        
        if existing_item:
            existing_item.quantity += item.quantity
        else:
            self.items.append(item)
            
        self.total_amount = self.calculate_total()
        self.updated_at = datetime.now(UTC)

    def remove_item(self, product_id: UUID) -> None:
        if self.status != OrderStatus.PENDING:
            raise OrderValidationError("Can only remove items from pending orders")
            
        original_length = len(self.items)
        self.items = [item for item in self.items if item.product_id != product_id]
        
        if len(self.items) == original_length:
            raise OrderValidationError(f"Product {product_id} not found in order")
            
        self.total_amount = self.calculate_total()
        self.updated_at = datetime.now(UTC)

    def update_status(self, new_status: OrderStatus) -> None:
        if not OrderStatus.can_transition(self.status, new_status):
            raise InvalidOrderStatusTransition(
                message=f"Cannot transition from {self.status.value} to {new_status.value}"
            ) 
        self.status = new_status        
        if new_status == OrderStatus.COMPLETED:
            self.completed_at = datetime.now(UTC)

    def can_cancel(self) -> bool:
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]

    def cancel(self) -> None:
        if not self.can_cancel():
            raise OrderValidationError("Order cannot be cancelled in its current state")
        self.update_status(OrderStatus.CANCELLED)

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise OrderValidationError("Only pending orders can be confirmed")
        self.update_status(OrderStatus.CONFIRMED)

    def complete(self) -> None:
        if self.status != OrderStatus.CONFIRMED:
            raise OrderValidationError("Only confirmed orders can be completed")
        self.update_status(OrderStatus.COMPLETED)

    def update_quantities(self, product_quantities: dict[UUID, int]) -> None:
        if self.status != OrderStatus.PENDING:
            raise OrderValidationError("Can only update quantities of pending orders")
            
        for product_id, new_quantity in product_quantities.items():
            item = next((i for i in self.items if i.product_id == product_id), None)
            if item:
                if new_quantity <= 0:
                    self.remove_item(product_id)
                else:
                    item.quantity = new_quantity
            else:
                raise OrderValidationError(f"Product {product_id} not found in order")
                
        self.total_amount = self.calculate_total()
        self.updated_at = datetime.now(UTC)

    def calculate_total_amount(self):
        """Calculate the total amount of the order from all items"""
        total = sum(item.total_price.amount for item in self.items)
        self.total_amount = Money(amount=total, currency="USD")
        return self.total_amount
        
    def can_be_cancelled(self) -> bool:
        """Check if the order can be cancelled based on its current status"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]
        
    def can_be_modified_by(self, user_id: UUID) -> bool:
        """Check if the order can be modified by the given user"""
        
        return self.user_id == user_id

