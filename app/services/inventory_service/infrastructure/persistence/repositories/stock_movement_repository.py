from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services.inventory_service.domain.entities.stock_movement_entity import StockMovementEntity
from app.services.inventory_service.domain.enums.movement_type import MovementType
from app.services.inventory_service.infrastructure.persistence.models.stock_movement_model import StockMovementModel
from app.shared.infrastructure.persistence.repositories.repository import SQLAlchemyRepository


class StockMovementRepository(SQLAlchemyRepository):
    """
    Repository for managing stock movement data persistence.
    
    This repository handles the conversion between domain entities and database models,
    providing an abstraction layer over the database operations.
    """
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def add(self, movement: StockMovementEntity) -> StockMovementEntity:
        """
        Add a new stock movement to the database.
        
        Args:
            movement: The stock movement entity to persist
            
        Returns:
            The persisted stock movement entity with ID populated
            
        Raises:
            RepositoryError: If there's an error saving to the database
        """
        try:
            model = self._to_model(movement)
            self._session.add(model)
            self._session.flush()
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self._session.rollback()
            raise RepositoryError(f"Error adding stock movement: {str(e)}")
    
    def get_by_id(self, movement_id: UUID) -> Optional[StockMovementEntity]:
        """
        Get a stock movement by its ID.
        
        Args:
            movement_id: The UUID of the movement to retrieve
            
        Returns:
            The stock movement entity if found, None otherwise
        """
        model = self._session.query(StockMovementModel).filter(
            StockMovementModel.id == movement_id
        ).first()
        
        return self._to_entity(model) if model else None
    
    def get_by_inventory_id(self, inventory_id: UUID) -> List[StockMovementEntity]:
        """
        Get all movements for a specific inventory item.
        
        Args:
            inventory_id: The UUID of the inventory item
            
        Returns:
            A list of stock movement entities
        """
        models = self._session.query(StockMovementModel).filter(
            StockMovementModel.inventory_id == inventory_id
        ).order_by(StockMovementModel.created_at.desc()).all()
        
        return [self._to_entity(model) for model in models]
    
    def get_by_type(self, movement_type: MovementType) -> List[StockMovementEntity]:
        """
        Get all movements of a specific type.
        
        Args:
            movement_type: The type of movement to filter by
            
        Returns:
            A list of stock movement entities of the specified type
        """
        models = self._session.query(StockMovementModel).filter(
            StockMovementModel.movement_type == movement_type
        ).order_by(StockMovementModel.created_at.desc()).all()
        
        return [self._to_entity(model) for model in models]
    
    def get_by_reference_id(self, reference_id: UUID) -> List[StockMovementEntity]:
        """
        Get all movements associated with a specific reference (e.g., order).
        
        Args:
            reference_id: The UUID of the reference (order, transfer, etc.)
            
        Returns:
            A list of stock movement entities with the specified reference
        """
        models = self._session.query(StockMovementModel).filter(
            StockMovementModel.reference_id == reference_id
        ).order_by(StockMovementModel.created_at.desc()).all()
        
        return [self._to_entity(model) for model in models]
    
    def _to_model(self, entity: StockMovementEntity) -> StockMovementModel:
        """Convert a domain entity to a database model"""
        model = StockMovementModel(
            id=entity.id,
            inventory_id=entity.inventory_id,
            quantity=entity.quantity,
            movement_type=entity.movement_type,
            reference_id=entity.reference_id,
            batch_number=entity.batch_number,
            reason=entity.reason,
            created_by=entity.created_by,
            created_at=entity.created_at
        )
        return model
    
    def _to_entity(self, model: StockMovementModel) -> StockMovementEntity:
        """Convert a database model to a domain entity"""
        entity = StockMovementEntity(
            id=model.id,
            inventory_id=model.inventory_id,
            quantity=model.quantity,
            movement_type=model.movement_type,
            reference_id=model.reference_id,
            batch_number=model.batch_number,
            reason=model.reason,
            created_by=model.created_by,
            created_at=model.created_at
        )
        return entity


class RepositoryError(Exception):
    """Exception raised for repository-related errors"""
    pass 