from sqlalchemy.orm import Session
import logging
from typing import Optional

from app.shared.acl.unified_acl import UnifiedACL
from app.shared.application.events.event_bus import EventBus
from app.services.invoice_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.invoice_service.infrastructure.repositories.invoice_repository import SQLAlchemyInvoiceRepository

logger = logging.getLogger(__name__)

class SQLAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of the Unit of Work pattern"""
    
    def __init__(self, session: Session, event_bus: EventBus, acl: UnifiedACL):
        self._session = session
        self._event_bus = event_bus
        self._acl = acl
        self.invoices = None

    def __enter__(self):
        logger.debug("Entering unit of work")
        self.invoices = SQLAlchemyInvoiceRepository(self._session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug(f"Exiting unit of work: {exc_type}")
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        logger.debug("Committing unit of work")
        self._session.commit()
        
        # Process and publish domain events
        self._publish_events()

    def rollback(self):
        logger.debug("Rolling back unit of work")
        self._session.rollback()
        
    def _publish_events(self):
        """Publish all collected domain events to the event bus"""
        if hasattr(self.invoices, 'publish_events'):
            self.invoices.publish_events(self._event_bus) 