from typing import Dict, Any
import logging
from datetime import datetime, timedelta

from app.services.invoice_service.application.commands.create_invoice_command import CreateInvoiceCommand
from app.services.invoice_service.application.commands.update_invoice_command import UpdateInvoiceCommand
from app.services.invoice_service.domain.interfaces.invoice_repository import InvoiceRepository
from app.services.invoice_service.domain.interfaces.order_service import OrderService
from app.services.invoice_service.domain.exceptions.invoice_exceptions import InvoiceNotFoundException

logger = logging.getLogger(__name__)

class OrderEventHandlers:
    """
    Handlers for order-related events that the invoice service needs to listen to.
    These handlers are registered with an event listener system outside the domain.
    """
    
    def __init__(
        self, 
        invoice_repository: InvoiceRepository,
        order_service: OrderService,
        create_invoice_command: CreateInvoiceCommand,
        update_invoice_command: UpdateInvoiceCommand
    ):
        self.invoice_repository = invoice_repository
        self.order_service = order_service
        self.create_invoice_command = create_invoice_command
        self.update_invoice_command = update_invoice_command
    
    def handle_order_created(self, event: Dict[str, Any]) -> None:
        """
        Handle an order.created event.
        Creates a new invoice for the order.
        
        Args:
            event: Event data containing order information
        """
        try:
            order_id = event.get('order_id')
            if not order_id:
                logger.error("Order created event missing order_id")
                return
                
            # Check if invoice already exists for this order (idempotence)
            existing_invoice = self.invoice_repository.get_by_order_id(order_id)
            if existing_invoice:
                logger.info(f"Invoice already exists for order {order_id}, skipping creation")
                return
            
            # Create a new invoice from the order
            self.create_invoice_command.create_from_order(order_id)
            logger.info(f"Created invoice for order {order_id}")
            
        except Exception as e:
            logger.error(f"Error handling order created event: {str(e)}")
    
    def handle_order_updated(self, event: Dict[str, Any]) -> None:
        """
        Handle an order.updated event.
        Updates the corresponding invoice if needed.
        
        Args:
            event: Event data containing order update information
        """
        try:
            order_id = event.get('order_id')
            if not order_id:
                logger.error("Order updated event missing order_id")
                return
                
            # Find the invoice for this order
            invoice = self.invoice_repository.get_by_order_id(order_id)
            if not invoice:
                logger.warning(f"No invoice found for updated order {order_id}")
                return
                
            # If the invoice is already paid or cancelled, no updates are needed
            if invoice.is_paid or invoice.is_cancelled:
                logger.info(f"Invoice for order {order_id} is already {invoice.status.value}, no updates needed")
                return
                
            # TODO: Implement logic to update the invoice based on order changes
            # This would typically involve recalculating totals, updating items, etc.
            
            logger.info(f"Updated invoice for order {order_id}")
            
        except Exception as e:
            logger.error(f"Error handling order updated event: {str(e)}")
    
    def handle_order_cancelled(self, event: Dict[str, Any]) -> None:
        """
        Handle an order.cancelled event.
        Cancels the corresponding invoice.
        
        Args:
            event: Event data containing order cancellation information
        """
        try:
            order_id = event.get('order_id')
            if not order_id:
                logger.error("Order cancelled event missing order_id")
                return
                
            # Find the invoice for this order
            invoice = self.invoice_repository.get_by_order_id(order_id)
            if not invoice:
                logger.warning(f"No invoice found for cancelled order {order_id}")
                return
                
            # If the invoice is already paid, we can't cancel it
            if invoice.is_paid:
                logger.warning(f"Cannot cancel invoice for order {order_id} as it is already paid")
                return
                
            # Cancel the invoice
            self.update_invoice_command.cancel_invoice(invoice.invoice_id)
            logger.info(f"Cancelled invoice for order {order_id}")
            
        except InvoiceNotFoundException:
            logger.warning(f"No invoice found for cancelled order {order_id}")
        except Exception as e:
            logger.error(f"Error handling order cancelled event: {str(e)}") 