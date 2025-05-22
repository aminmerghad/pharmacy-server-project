from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.services.order_service.domain.value_objects.money import Money
from app.services.order_service.domain.exceptions.order_errors import OrderValidationError

@dataclass
class OrderItem:
    product_id: UUID
    quantity: int
    price: Money
    # name: str
    id: UUID = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if self.quantity <= 0:
            raise OrderValidationError("Quantity must be greater than 0")
        if self.price.amount <= 0:
            raise OrderValidationError("Price must be greater than 0")

    @property
    def total_price(self) -> Money:
        return Money(self.price.amount * self.quantity)

    def update_quantity(self, new_quantity: int) -> None:
        if new_quantity <= 0:
            raise OrderValidationError("Quantity must be greater than 0")
        self.quantity = new_quantity
        self.updated_at = datetime.utcnow()

    def update_price(self, new_price: Decimal) -> None:
        if new_price <= 0:
            raise OrderValidationError("Price must be greater than 0")
        self.price = Money(new_price)
        self.updated_at = datetime.utcnow()

    @classmethod
    def create(
        cls,
        product_id: UUID,
        # name: str,
        quantity: int,
        price: Decimal
    ) -> 'OrderItem':
        return cls(
            product_id=product_id,
            # name=name,
            quantity=quantity,
            price=Money(price)
        )

