import logging
from typing import Dict, Any

from app.services.invoice_service.application.events.invoice_events import (
    InvoiceCreatedEvent,
    InvoiceStatusChangedEvent,
    InvoicePaidEvent,
    InvoiceCancelledEvent,
    InvoiceOverdueEvent
)

logger = logging.getLogger(__name__)

class InvoiceEventHandlers:
    """
    Handlers for invoice-related events that are generated within the service.
    These handlers are registered with the event dispatcher.
    """
    
    def __init__(self, event_publisher=None):
        """
        Initialize the invoice event handlers.
        
        Args:
            event_publisher: A service that can publish events to external systems
        """
        self.event_publisher = event_publisher
    
    def handle_invoice_created(self, event: InvoiceCreatedEvent) -> None:
        """
        Handle an invoice.created event.
        
        Args:
            event: Event data containing invoice creation information
        """
        logger.info(f"Invoice created: {event.invoice_id} for order {event.order_id}")
        
        # Publish the event to external systems if available
        if self.event_publisher:
            self.event_publisher.publish("invoice.created", event.to_dict())
    
    def handle_invoice_status_changed(self, event: InvoiceStatusChangedEvent) -> None:
        """
        Handle an invoice.status_changed event.
        
        Args:
            event: Event data containing invoice status change information
        """
        logger.info(f"Invoice {event.invoice_id} status changed from {event.previous_status} to {event.new_status}")
        
        # Publish the event to external systems if available
        if self.event_publisher:
            self.event_publisher.publish("invoice.status_changed", event.to_dict())
    
    def handle_invoice_paid(self, event: InvoicePaidEvent) -> None:
        """
        Handle an invoice.paid event.
        
        Args:
            event: Event data containing invoice payment information
        """
        logger.info(f"Invoice {event.invoice_id} paid: {event.amount_paid} via {event.payment_method}")
        
        # Publish the event to external systems if available
        if self.event_publisher:
            self.event_publisher.publish("invoice.paid", event.to_dict())
    
    def handle_invoice_cancelled(self, event: InvoiceCancelledEvent) -> None:
        """
        Handle an invoice.cancelled event.
        
        Args:
            event: Event data containing invoice cancellation information
        """
        logger.info(f"Invoice {event.invoice_id} cancelled" + (f": {event.reason}" if event.reason else ""))
        
        # Publish the event to external systems if available
        if self.event_publisher:
            self.event_publisher.publish("invoice.cancelled", event.to_dict())
    
    def handle_invoice_overdue(self, event: InvoiceOverdueEvent) -> None:
        """
        Handle an invoice.overdue event.
        
        Args:
            event: Event data containing invoice overdue information
        """
        logger.info(f"Invoice {event.invoice_id} is overdue by {event.days_overdue} days")
        
        # Publish the event to external systems if available
        if self.event_publisher:
            self.event_publisher.publish("invoice.overdue", event.to_dict()) 