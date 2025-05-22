from typing import Dict, Any, Optional
from datetime import datetime
import logging
from uuid import UUID

from app.shared.application.events.event_bus import EventBus
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus

logger = logging.getLogger(__name__)

class InvoiceEventAdapter:
    """
    Adapter for converting domain events to application events and publishing them.
    Acts as a bridge between the domain layer and the application's event system.
    """
    
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        logger.info("Invoice event adapter initialized")
    
    def publish_invoice_created(
        self, 
        invoice_id: UUID,
        order_id: UUID,
        user_id: UUID,
        total_amount: float,
        due_date: datetime
    ) -> bool:
        """
        Publish an event when an invoice is created.
        
        Args:
            invoice_id: ID of the created invoice
            order_id: ID of the associated order
            user_id: ID of the user the invoice belongs to
            total_amount: Total amount of the invoice
            due_date: Due date of the invoice
            
        Returns:
            True if event was published successfully, False otherwise
        """
        logger.info(f"Publishing invoice.created event for invoice {invoice_id}")
        try:
            event_data = {
                "event_type": "invoice.created",
                "invoice_id": str(invoice_id),
                "order_id": str(order_id),
                "user_id": str(user_id),
                "total_amount": total_amount,
                "due_date": due_date.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
            self._event_bus.publish("invoice.created", event_data)
            logger.info(f"Published invoice.created event for invoice {invoice_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish invoice.created event: {str(e)}", exc_info=True)
            return False
    
    def publish_invoice_status_changed(
        self,
        invoice_id: UUID,
        order_id: UUID,
        user_id: UUID,
        previous_status: InvoiceStatus,
        new_status: InvoiceStatus
    ) -> bool:
        """
        Publish an event when an invoice's status changes.
        
        Args:
            invoice_id: ID of the invoice
            order_id: ID of the associated order
            user_id: ID of the user the invoice belongs to
            previous_status: Previous invoice status
            new_status: New invoice status
            
        Returns:
            True if event was published successfully, False otherwise
        """
        logger.info(f"Publishing invoice.status_changed event for invoice {invoice_id}")
        try:
            event_data = {
                "event_type": "invoice.status_changed",
                "invoice_id": str(invoice_id),
                "order_id": str(order_id),
                "user_id": str(user_id),
                "previous_status": previous_status.value,
                "new_status": new_status.value,
                "timestamp": datetime.now().isoformat()
            }
            
            self._event_bus.publish("invoice.status_changed", event_data)
            logger.info(f"Published invoice.status_changed event for invoice {invoice_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish invoice.status_changed event: {str(e)}", exc_info=True)
            return False
    
    def publish_invoice_paid(
        self,
        invoice_id: UUID,
        order_id: UUID,
        user_id: UUID,
        amount_paid: float,
        payment_method: str,
        transaction_id: Optional[str] = None
    ) -> bool:
        """
        Publish an event when an invoice is paid.
        
        Args:
            invoice_id: ID of the invoice
            order_id: ID of the associated order
            user_id: ID of the user the invoice belongs to
            amount_paid: Amount that was paid
            payment_method: Method of payment
            transaction_id: Optional transaction ID for the payment
            
        Returns:
            True if event was published successfully, False otherwise
        """
        logger.info(f"Publishing invoice.paid event for invoice {invoice_id}")
        try:
            event_data = {
                "event_type": "invoice.paid",
                "invoice_id": str(invoice_id),
                "order_id": str(order_id),
                "user_id": str(user_id),
                "amount_paid": amount_paid,
                "payment_method": payment_method,
                "transaction_id": transaction_id,
                "timestamp": datetime.now().isoformat()
            }
            
            self._event_bus.publish("invoice.paid", event_data)
            logger.info(f"Published invoice.paid event for invoice {invoice_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish invoice.paid event: {str(e)}", exc_info=True)
            return False
    
    def publish_invoice_cancelled(
        self,
        invoice_id: UUID,
        order_id: UUID,
        user_id: UUID,
        reason: Optional[str] = None
    ) -> bool:
        """
        Publish an event when an invoice is cancelled.
        
        Args:
            invoice_id: ID of the invoice
            order_id: ID of the associated order
            user_id: ID of the user the invoice belongs to
            reason: Optional reason for cancellation
            
        Returns:
            True if event was published successfully, False otherwise
        """
        logger.info(f"Publishing invoice.cancelled event for invoice {invoice_id}")
        try:
            event_data = {
                "event_type": "invoice.cancelled",
                "invoice_id": str(invoice_id),
                "order_id": str(order_id),
                "user_id": str(user_id),
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
            
            self._event_bus.publish("invoice.cancelled", event_data)
            logger.info(f"Published invoice.cancelled event for invoice {invoice_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish invoice.cancelled event: {str(e)}", exc_info=True)
            return False
    
    def publish_invoice_overdue(
        self,
        invoice_id: UUID,
        order_id: UUID,
        user_id: UUID,
        due_date: datetime,
        days_overdue: int
    ) -> bool:
        """
        Publish an event when an invoice becomes overdue.
        
        Args:
            invoice_id: ID of the invoice
            order_id: ID of the associated order
            user_id: ID of the user the invoice belongs to
            due_date: Original due date of the invoice
            days_overdue: Number of days the invoice is overdue
            
        Returns:
            True if event was published successfully, False otherwise
        """
        logger.info(f"Publishing invoice.overdue event for invoice {invoice_id}")
        try:
            event_data = {
                "event_type": "invoice.overdue",
                "invoice_id": str(invoice_id),
                "order_id": str(order_id),
                "user_id": str(user_id),
                "due_date": due_date.isoformat(),
                "days_overdue": days_overdue,
                "timestamp": datetime.now().isoformat()
            }
            
            self._event_bus.publish("invoice.overdue", event_data)
            logger.info(f"Published invoice.overdue event for invoice {invoice_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish invoice.overdue event: {str(e)}", exc_info=True)
            return False 