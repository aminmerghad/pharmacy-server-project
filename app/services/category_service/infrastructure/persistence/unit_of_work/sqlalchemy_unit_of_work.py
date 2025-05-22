from typing import Any
from sqlalchemy.orm import Session

from app.services.category_service.domain.interfaces.category_repository import CategoryRepository
from app.services.category_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.category_service.infrastructure.persistence.repositories.sqlalchemy_category_repository import SQLAlchemyCategoryRepository
from app.shared.acl.unified_acl import UnifiedACL
from app.shared.application.events.event_bus import EventBus

class SQLAlchemyUnitOfWork(UnitOfWork):
    """
    SQLAlchemy implementation of the UnitOfWork interface.
    """
    
    def __init__(self, session: Session, event_bus: EventBus, acl: UnifiedACL):
        self._session = session
        self._event_bus = event_bus
        self._acl = acl
        self._category_repository = SQLAlchemyCategoryRepository(session)
    
    @property
    def category_repository(self) -> CategoryRepository:
        return self._category_repository
    
    def commit(self) -> None:
        self._session.commit()
    
    def rollback(self) -> None:
        self._session.rollback()
    
    def publish(self, event: Any) -> None:
        self._event_bus.publish(event) 