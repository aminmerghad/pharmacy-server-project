import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.services.invoice_service.domain.interfaces.invoice_repository import InvoiceRepository
from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus
from app.shared.application.events.event_bus import EventBus

logger = logging.getLogger(__name__)

class SQLAlchemyInvoiceRepository(InvoiceRepository):
    """SQLAlchemy implementation of the invoice repository."""
    
    def __init__(self, session: Session):
        self._session = session
        self._collected_events = []
        logger.info("SQLAlchemy invoice repository initialized")
    
    def add(self, invoice: Invoice) -> Invoice:
        """
        Add a new invoice to the database.
        
        Args:
            invoice: The invoice to add
            
        Returns:
            The added invoice with generated ID
        """
        logger.debug(f"Adding invoice: {invoice}")
        try:
            self._session.add(invoice)
            self._session.flush()
            
            # Collect domain events from the entity
            self._collect_events(invoice)
            
            logger.debug(f"Invoice added with ID: {invoice.id}")
            return invoice
        except Exception as e:
            logger.error(f"Error adding invoice: {str(e)}", exc_info=True)
            raise
    
    def get(self, invoice_id: UUID) -> Optional[Invoice]:
        """
        Get an invoice by its ID.
        
        Args:
            invoice_id: The ID of the invoice to retrieve
            
        Returns:
            The invoice if found, None otherwise
        """
        logger.debug(f"Getting invoice with ID: {invoice_id}")
        try:
            invoice = self._session.query(Invoice).filter(Invoice.id == invoice_id).first()
            
            if invoice:
                logger.debug(f"Invoice found: {invoice_id}")
            else:
                logger.debug(f"Invoice not found: {invoice_id}")
                
            return invoice
        except Exception as e:
            logger.error(f"Error getting invoice: {str(e)}", exc_info=True)
            raise
    
    def update(self, invoice: Invoice) -> Invoice:
        """
        Update an existing invoice.
        
        Args:
            invoice: The invoice to update
            
        Returns:
            The updated invoice
        """
        logger.debug(f"Updating invoice: {invoice.id}")
        try:
            self._session.merge(invoice)
            self._session.flush()
            
            # Collect domain events from the entity
            self._collect_events(invoice)
            
            logger.debug(f"Invoice updated: {invoice.id}")
            return invoice
        except Exception as e:
            logger.error(f"Error updating invoice: {str(e)}", exc_info=True)
            raise
    
    def delete(self, invoice_id: UUID) -> bool:
        """
        Delete an invoice by its ID.
        
        Args:
            invoice_id: The ID of the invoice to delete
            
        Returns:
            True if the invoice was deleted, False otherwise
        """
        logger.debug(f"Deleting invoice: {invoice_id}")
        try:
            invoice = self.get(invoice_id)
            if not invoice:
                logger.debug(f"Invoice not found for deletion: {invoice_id}")
                return False
                
            self._session.delete(invoice)
            self._session.flush()
            
            logger.debug(f"Invoice deleted: {invoice_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting invoice: {str(e)}", exc_info=True)
            raise
    
    def get_all(self, limit: Optional[int] = None) -> List[Invoice]:
        """
        Get all invoices.
        
        Args:
            limit: Optional maximum number of invoices to return
            
        Returns:
            List of invoices
        """
        logger.debug("Getting all invoices")
        try:
            query = self._session.query(Invoice)
            
            if limit:
                query = query.limit(limit)
                
            invoices = query.all()
            logger.debug(f"Retrieved {len(invoices)} invoices")
            return invoices
        except Exception as e:
            logger.error(f"Error getting all invoices: {str(e)}", exc_info=True)
            raise
    
    def find_by_order_id(self, order_id: UUID) -> Optional[Invoice]:
        """
        Find an invoice by its associated order ID.
        
        Args:
            order_id: The order ID to find the invoice for
            
        Returns:
            The invoice if found, None otherwise
        """
        logger.debug(f"Finding invoice by order ID: {order_id}")
        try:
            invoice = self._session.query(Invoice).filter(Invoice.order_id == order_id).first()
            
            if invoice:
                logger.debug(f"Invoice found for order: {order_id}")
            else:
                logger.debug(f"No invoice found for order: {order_id}")
                
            return invoice
        except Exception as e:
            logger.error(f"Error finding invoice by order ID: {str(e)}", exc_info=True)
            raise
    
    def get_by_user_id(self, user_id: str) -> List[Invoice]:
        """
        Get all invoices for a specific user.
        
        Args:
            user_id: User ID to filter by
            
        Returns:
            List of invoices for the specified user
        """
        logger.debug(f"Getting invoices for user: {user_id}")
        try:
            invoices = self._session.query(Invoice).filter(Invoice.user_id == user_id).all()
            logger.debug(f"Found {len(invoices)} invoices for user {user_id}")
            return invoices
        except Exception as e:
            logger.error(f"Error getting invoices by user ID: {str(e)}", exc_info=True)
            raise
    
    def get_by_status(self, status: InvoiceStatus) -> List[Invoice]:
        """
        Get all invoices with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of invoices with the specified status
        """
        logger.debug(f"Getting invoices with status: {status}")
        try:
            invoices = self._session.query(Invoice).filter(Invoice.status == status).all()
            logger.debug(f"Found {len(invoices)} invoices with status {status}")
            return invoices
        except Exception as e:
            logger.error(f"Error getting invoices by status: {str(e)}", exc_info=True)
            raise
    
    def get_overdue_invoices(self) -> List[Invoice]:
        """
        Get all overdue invoices (pending invoices with due date in the past).
        
        Returns:
            List of overdue invoices
        """
        logger.debug("Getting overdue invoices")
        try:
            current_date = datetime.now().date()
            invoices = self._session.query(Invoice).filter(
                and_(
                    Invoice.status == InvoiceStatus.PENDING,
                    Invoice.due_date < current_date
                )
            ).all()
            logger.debug(f"Found {len(invoices)} overdue invoices")
            return invoices
        except Exception as e:
            logger.error(f"Error getting overdue invoices: {str(e)}", exc_info=True)
            raise
    
    def get_invoices_due_soon(self, days: int) -> List[Invoice]:
        """
        Get all invoices due within a certain number of days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of invoices due within the specified days
        """
        logger.debug(f"Getting invoices due within {days} days")
        try:
            current_date = datetime.now().date()
            due_date = current_date + timedelta(days=days)
            
            invoices = self._session.query(Invoice).filter(
                and_(
                    Invoice.status == InvoiceStatus.PENDING,
                    Invoice.due_date >= current_date,
                    Invoice.due_date <= due_date
                )
            ).all()
            
            logger.debug(f"Found {len(invoices)} invoices due within {days} days")
            return invoices
        except Exception as e:
            logger.error(f"Error getting invoices due soon: {str(e)}", exc_info=True)
            raise
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Invoice]:
        """
        Get all invoices created within a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            
        Returns:
            List of invoices created within the specified date range
        """
        logger.debug(f"Getting invoices created between {start_date} and {end_date}")
        try:
            # Convert to date if datetime objects were provided
            start = start_date.date() if isinstance(start_date, datetime) else start_date
            end = end_date.date() if isinstance(end_date, datetime) else end_date
            
            invoices = self._session.query(Invoice).filter(
                and_(
                    Invoice.created_at >= start,
                    Invoice.created_at <= end
                )
            ).all()
            
            logger.debug(f"Found {len(invoices)} invoices in date range")
            return invoices
        except Exception as e:
            logger.error(f"Error getting invoices by date range: {str(e)}", exc_info=True)
            raise
    
    def _collect_events(self, entity: Invoice) -> None:
        """
        Collect domain events from an entity.
        
        Args:
            entity: The entity to collect events from
        """
        if hasattr(entity, 'domain_events'):
            self._collected_events.extend(entity.domain_events)
            entity.clear_events()
    
    def publish_events(self, event_bus: EventBus) -> None:
        """
        Publish collected domain events to the event bus.
        
        Args:
            event_bus: The event bus to publish events to
        """
        for event in self._collected_events:
            event_type = event.__class__.__name__
            event_bus.publish(event_type, event.to_dict())
        
        self._collected_events.clear() 