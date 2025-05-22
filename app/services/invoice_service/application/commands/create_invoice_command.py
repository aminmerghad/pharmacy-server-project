from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.services.invoice_service.domain.interfaces.invoice_repository import InvoiceRepository
from app.services.invoice_service.domain.interfaces.order_service import OrderService
from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.domain.entities.invoice_item import InvoiceItem
from app.services.invoice_service.domain.value_objects.money import Money
from app.services.invoice_service.application.dtos.invoice_dto import CreateInvoiceDTO, InvoiceDTO

class CreateInvoiceCommand:
    """Command for creating a new invoice."""
    
    def __init__(self, invoice_repository: InvoiceRepository, 
                #  order_service: OrderService
                 ):
        self.invoice_repository = invoice_repository
        # self.order_service = order_service
    
    def execute(self, data: CreateInvoiceDTO) -> InvoiceDTO:
        """
        Execute the command to create a new invoice.
        
        Args:
            data: Data for creating the invoice
            
        Returns:
            A DTO representation of the created invoice
            
        Raises:
            ValueError: If the order does not exist or is in an invalid state
        """
        # Validate the order exists and is in a valid state
        # if not self.order_service.validate_order(data.order_id):
        #     raise ValueError(f"Order {data.order_id} does not exist or is in an invalid state")
        
        # Create the invoice entity
        
        invoice = data.to_entity()
        
        # Save to repository
        saved_invoice = self.invoice_repository.save(invoice)
        
        # Return as DTO
        return InvoiceDTO.from_entity(saved_invoice)
    
    def create_from_order(self, order_id: str, due_date_days: int = 30) -> InvoiceDTO:
        """
        Create an invoice directly from an order without needing to specify items.
        
        Args:
            order_id: ID of the order to create an invoice for
            due_date_days: Number of days until the invoice is due
            
        Returns:
            A DTO representation of the created invoice
            
        Raises:
            ValueError: If the order does not exist or is in an invalid state
        """
        # Validate the order exists and is in a valid state
        if not self.order_service.validate_order(order_id):
            raise ValueError(f"Order {order_id} does not exist or is in an invalid state")
        
        # Get order details
        order = self.order_service.get_order(order_id)
        order_items = self.order_service.get_order_items(order_id)
        
        # Create invoice items from order items
        invoice_items = []
        for item in order_items:
            invoice_items.append(InvoiceItem(
                product_id=item['product_id'],
                description=item.get('name', 'Product'),
                quantity=item['quantity'],
                unit_price=Money(Decimal(str(item['price'])))
            ))
        
        # Calculate due date
        due_date = datetime.now() + timedelta(days=due_date_days)
        
        # Create invoice
        invoice = Invoice(
            order_id=order_id,
            user_id=order['user_id'],
            items=invoice_items,
            due_date=due_date
        )
        
        # Save to repository
        saved_invoice = self.invoice_repository.save(invoice)
        
        # Return as DTO
        return InvoiceDTO.from_entity(saved_invoice) 