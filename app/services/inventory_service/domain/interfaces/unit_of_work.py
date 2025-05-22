from sqlalchemy.orm import Session
from app.services.inventory_service.infrastructure.adapters.incoming.stock_check_adapter import StockCheckPort
from app.shared.application.events.event_bus import EventBus
from app.services.inventory_service.infrastructure.persistence.repositories.inventory_repository import InventoryRepository

class UnitOfWork:
    def __init__(self, session: Session, event_bus: EventBus):
        pass
    
    inventory_repository: InventoryRepository
    stockCheckPort: StockCheckPort
        
    def commit(self):
        pass
    
    def publish(self, event: any):
        pass
    
    def rollback(self):
        pass