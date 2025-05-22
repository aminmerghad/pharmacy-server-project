from sqlalchemy.orm import Session
from app.shared.application.events.event_bus import EventBus
from app.services.inventory_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.inventory_service.infrastructure.persistence.repositories.inventory_repository import InventoryRepository
from app.services.inventory_service.infrastructure.persistence.repositories.stock_movement_repository import StockMovementRepository

class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: Session, event_bus: EventBus = None):
        self.db_session = session
        self.event_bus = event_bus
        self._inventory = None
        self._stock_movement = None
        self._batch = None

    
    @property
    def inventory_repository(self):
        if not self._inventory:
            self._inventory = InventoryRepository(self.db_session)
        return self._inventory

        
    @property
    def stock_movement_repository(self):
        if not self._stock_movement:
            self._stock_movement = StockMovementRepository(self.db_session)
        return self._stock_movement
        
    
    def commit(self):
        self.db_session.commit()

    def publish(self, event: any):
        self.event_bus.publish(event)

    def rollback(self):
        self.db_session.rollback()