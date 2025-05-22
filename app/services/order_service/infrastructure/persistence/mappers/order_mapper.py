from decimal import Decimal
from uuid import UUID, uuid4

from app.services.order_service.domain.entities.order import OrderEntity
from app.services.order_service.domain.entities.order_item import OrderItem
from app.services.order_service.domain.value_objects.money import Money
from app.services.order_service.domain.value_objects.order_status import OrderStatus
from app.services.order_service.infrastructure.persistence.models.order import OrderModel, OrderItemModel

class OrderMapper:
    def to_entity(self, model: OrderModel) -> OrderEntity:
        """Convert OrderModel to Order entity"""
        return OrderEntity(
            id=model.id,
            user_id=model.user_id,
            items=[self._item_to_entity(item) for item in model.items],
            status=model.status,
            total_amount=Money(model.total_amount),
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at
        )

    def to_model(self, entity: OrderEntity) -> OrderModel:
        """Convert Order entity to OrderModel"""
       
        return OrderModel(
            user_id=uuid4(),
            # user_id=entity.user_id,
            status=entity.status,
            total_amount=0,
            # total_amount=entity.total_amount.amount,
            notes=entity.notes,
            completed_at=entity.completed_at,
            items=[self._item_to_model(item, entity.id) for item in entity.items]
        )

    def _item_to_entity(self, model: OrderItemModel) -> OrderItem:
        """Convert OrderItemModel to OrderItem entity"""
        
        return OrderItem(
            product_id=model.product_id,
            quantity=model.quantity,
            price=Money(model.price)
        )

    def _item_to_model(self, entity: OrderItem, order_id: str) -> OrderItemModel:
        """Convert OrderItem entity to OrderItemModel"""
        return OrderItemModel(
            id=entity.id,
            order_id=order_id,
            product_id=entity.product_id,
            # name=entity.name,
            quantity=entity.quantity,
            price=entity.price.amount
        ) 