from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.services.inventory_service.domain.entities.inventory_entity import InventoryEntity
from app.services.inventory_service.infrastructure.persistence.models.inventory_model import InventoryModel
from app.shared.infrastructure.persistence.repositories.repository import SQLAlchemyRepository


class InventoryRepository(SQLAlchemyRepository):
    """SQLAlchemy implementation of inventory repository."""
    
    def __init__(self, session: Session):
        super().__init__(session)
        self._session = session

    def add(self, entity: InventoryEntity) -> InventoryEntity:
        """Add a new inventory entity to the database"""
        model = self._to_model(entity)
        self._session.add(model)
        
        self._session.flush()  # Ensure the model gets its ID
        
        return self._to_entity(model)
    
    def get_by_id(self, inventory_id: UUID) -> Optional[InventoryEntity]:
        """Get inventory by its ID"""
        model = self._session.query(InventoryModel).filter(InventoryModel.id == inventory_id).first()
        return self._to_entity(model) if model else None
    
    def get_by_product_id(self, product_id: UUID) -> Optional[InventoryEntity]:
        """Get inventory by product ID"""
        model = self._session.query(InventoryModel).filter(InventoryModel.product_id == product_id).first()
        return self._to_entity(model) if model else None
    
    def get_all(self) -> List[InventoryEntity]:
        """Get all inventory items"""
        models = self._session.query(InventoryModel).all()
        return [self._to_entity(model) for model in models]
    
    def get_by_location(self, location_code: str) -> List[InventoryEntity]:
        """Get all inventory items in a specific location"""
        models = self._session.query(InventoryModel).filter(
            InventoryModel.location_code == location_code
        ).all()
        return [self._to_entity(model) for model in models]
    
    def get_by_batch(self, batch_number: str) -> List[InventoryEntity]:
        """Get all inventory items with a specific batch number"""
        models = self._session.query(InventoryModel).filter(
            InventoryModel.batch_number == batch_number
        ).all()
        return [self._to_entity(model) for model in models]
    
    def get_expiring(self, days: int = 90) -> List[InventoryEntity]:
        """Get inventory items expiring within the specified number of days"""
        today = datetime.now(timezone.utc).date()
        expiry_date = today + timedelta(days=days)
        
        models = self._session.query(InventoryModel).filter(
            InventoryModel.expiry_date <= expiry_date,
            InventoryModel.expiry_date >= today,  # Not already expired
            InventoryModel.quantity > 0  # Has stock
        ).order_by(InventoryModel.expiry_date).all()
        
        return [self._to_entity(model) for model in models]
    
    def get_expired(self) -> List[InventoryEntity]:
        """Get already expired inventory items that still have stock"""
        today = datetime.now(timezone.utc).date()
        
        models = self._session.query(InventoryModel).filter(
            InventoryModel.expiry_date < today,
            InventoryModel.quantity > 0  # Has stock
        ).order_by(InventoryModel.expiry_date).all()
        
        return [self._to_entity(model) for model in models]
    
    def get_low_stock(self, threshold_percentage: float = 100) -> List[InventoryEntity]:
        """Get inventory items with stock at or below the minimum level"""
        models = self._session.query(InventoryModel).filter(
            InventoryModel.quantity <= InventoryModel.min_stock * threshold_percentage / 100
        ).all()
        
        return [self._to_entity(model) for model in models]
    
    def update(self, entity: InventoryEntity) -> InventoryEntity:
        # model = self._session.query(InventoryModel).filter(InventoryModel.id == entity.id).first()
        model = self._session.query(InventoryModel).filter(InventoryModel.product_id == entity.product_id).first()
        
        # Update all fields
        model.quantity = entity.quantity
        model.price = entity.price
        model.max_stock = entity.max_stock
        model.min_stock = entity.min_stock
        model.expiry_date = entity.expiry_date
        model.supplier_id = entity.supplier_id

        # model.batch_number = entity.batch_number
        # model.lot_number = entity.lot_number
        # model.manufacturer = entity.manufacturer
        # model.supplier_id = entity.supplier_id
        # model.location_code = entity.location_code
        # model.notes = entity.notes
        # model.reorder_point = entity.reorder_point
        # model.lead_time_days = entity.lead_time_days
        # model.last_restock_date = entity.last_restock_date
        # model.last_count_date = entity.last_count_date
        
        self._session.flush()
        return self._to_entity(model)
    
    # def delete(self, product_id: UUID) -> bool:
    #     """Delete an inventory item by its ID"""
    #     # model = self._session.query(InventoryModel).filter(InventoryModel.id == inventory_id).first()
        
    #     # if not model:
    #     #     return False
            
    #     # self._session.delete(model)
    #     # self._session.flush()
    #     model = self._session.query(InventoryModel).filter(InventoryModel.product_id == product_id).first()
    #     model.status = ProductStatus.INACTIVE
    #     self._session.flush()

    #     return True
    
    def _to_model(self, entity: InventoryEntity) -> InventoryModel:
        """Convert a domain entity to a database model"""
        model = InventoryModel(
            id=entity.id,
            product_id=entity.product_id,
            quantity=entity.quantity,
            price=entity.price,
            max_stock=entity.max_stock,
            min_stock=entity.min_stock,
            expiry_date=entity.expiry_date,
            supplier_id=entity.supplier_id,
            # batch_number=entity.batch_number,
            # lot_number=entity.lot_number,
            # manufacturer=entity.manufacturer,
            # supplier_id=entity.supplier_id,
            # location_code=entity.location_code,
            # notes=entity.notes,
            # reorder_point=entity.reorder_point,
            # lead_time_days=entity.lead_time_days,
            # last_restock_date=entity.last_restock_date,
            # last_count_date=entity.last_count_date
        )
        return model

    def _to_entity(self, model: InventoryModel) -> InventoryEntity:
        """Convert a database model to a domain entity"""
        if not model:
            return None
            
        return InventoryEntity(
            id=model.id,
            product_id=model.product_id,
            quantity=model.quantity,
            price=model.price,
            max_stock=model.max_stock,
            min_stock=model.min_stock,
            expiry_date=model.expiry_date,
            supplier_id=model.supplier_id,
            
            # batch_number=model.batch_number,
            # lot_number=model.lot_number,
            # manufacturer=model.manufacturer,
            # supplier_id=model.supplier_id,
            # location_code=model.location_code,
            # notes=model.notes,
            # reorder_point=model.reorder_point,
            # lead_time_days=model.lead_time_days,
            # last_restock_date=model.last_restock_date,
            # last_count_date=model.last_count_date
        )

