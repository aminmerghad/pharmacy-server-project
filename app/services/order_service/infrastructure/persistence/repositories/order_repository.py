from datetime import datetime
from typing import List, Optional, Set
from uuid import UUID, uuid4

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.services.order_service.domain.entities.order import OrderEntity
from app.services.order_service.domain.interfaces.order_repository import OrderRepository
from app.services.order_service.domain.value_objects.order_status import OrderStatus
from app.services.order_service.infrastructure.persistence.mappers.order_mapper import OrderMapper
from app.services.order_service.infrastructure.persistence.models.order import OrderItemModel, OrderModel

class SQLAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self._session = session
        self._mapper = OrderMapper()
        self._seen: Set[OrderEntity] = set()
    
    def get_all(self):
        orders_model= self._session.query(OrderModel).all()
        return orders_model 

    @property
    def seen(self) -> Set[OrderEntity]:
        return self._seen

    def add(self, order: OrderEntity) -> OrderEntity:
       
        # order_model = self._mapper.to_model(order)
        order_model = OrderModel(
            total_amount=order.total_amount,
            items=[OrderItemModel(
                quantity=item.quantity, 
                price=item.price.amount,
                product_id=item.product_id
            ) for item in order.items]
        )
        
        self._session.add(order_model)
        self._session.flush()
       
        order = self._mapper.to_entity(order_model)
        return order

    def get(self, order_id: UUID) -> Optional[OrderEntity]:
        order_model = self._session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).first()
        
        if not order_model:
            return None
            
        order = self._mapper.to_entity(order_model)
        # self._seen.add(order)
        return order

    def update(self, order: OrderEntity) -> OrderEntity:
        order_model = self._session.query(OrderModel).filter(
            OrderModel.id == order.id
        ).first()

        
        if not order_model:
            raise ValueError(f"Order {order.id} not found")
            
        # updated_model = self._mapper.to_model(order)
        order_model.status = order.status
        # for key, value in updated_model.__dict__.items():
        #     if not key.startswith('_'):
        #         setattr(order_model, key, value)
        self._session.flush()
        return self._mapper.to_entity(order_model)

    def delete(self, order_id: UUID) -> None:
        self._session.query(OrderModel).filter(
            OrderModel.id == order_id
        ).delete()
        self._session.flush()

    def get_by_user(
        self,
        user_id: UUID,
        status: Optional[OrderStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[OrderEntity]:
        query = self._session.query(OrderModel).filter(OrderModel.user_id == user_id)

        if status:
            query = query.filter(OrderModel.status == status)
        if start_date:
            query = query.filter(OrderModel.created_at >= start_date)
        if end_date:
            query = query.filter(OrderModel.created_at <= end_date)

        order_models = query.all()
        orders = [self._mapper.to_entity(model) for model in order_models]
        self._seen.update(orders)
        return orders

    def get_by_status(
        self,
        status: OrderStatus,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[OrderEntity]:
        query = self._session.query(OrderModel).filter(OrderModel.status == status)

        if start_date:
            query = query.filter(OrderModel.created_at >= start_date)
        if end_date:
            query = query.filter(OrderModel.created_at <= end_date)

        order_models = query.all()
        orders = [self._mapper.to_entity(model) for model in order_models]
        self._seen.update(orders)
        return orders

    def search(
        self,
        query: str,
        status: Optional[OrderStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[OrderEntity]:
        db_query = self._session.query(OrderModel).filter(
            or_(
                OrderModel.id.ilike(f"%{query}%"),
                OrderModel.user_id.ilike(f"%{query}%"),
                OrderModel.notes.ilike(f"%{query}%")
            )
        )

        if status:
            db_query = db_query.filter(OrderModel.status == status)
        if start_date:
            db_query = db_query.filter(OrderModel.created_at >= start_date)
        if end_date:
            db_query = db_query.filter(OrderModel.created_at <= end_date)

        order_models = db_query.all()
        orders = [self._mapper.to_entity(model) for model in order_models]
        self._seen.update(orders)
        return orders

    def exists(self, order_id: UUID) -> bool:
        return self._session.query(
            self._session.query(OrderModel).filter(
                OrderModel.id == order_id
            ).exists()
        ).scalar()