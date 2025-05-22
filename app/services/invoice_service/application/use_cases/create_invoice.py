from typing import Optional, Dict, Any
import logging
from datetime import datetime
from uuid import UUID, uuid4

from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.domain.entities.invoice_item import InvoiceItem
from app.services.invoice_service.application.commands.create_invoice_command import CreateInvoiceCommand
from app.services.invoice_service.application.dtos.invoice_dto import InvoiceDTO, InvoiceItemDTO
from app.services.invoice_service.application.dtos.converters import invoice_to_dto
from app.services.invoice_service.domain.exceptions.invoice_exceptions import InvoiceCreationException
from app.services.invoice_service.infrastructure.unit_of_work.unit_of_work import SQLAlchemyUnitOfWork

logger = logging.getLogger(__name__)

class CreateInvoiceUseCase:
    """
    Use case for creating a new invoice.
    Implements the business logic for invoice creation, including validation rules.
    """
    
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow
        logger.info("CreateInvoiceUseCase initialized")
    
    def execute(self, command: CreateInvoiceCommand) -> InvoiceDTO:
        """
        Create a new invoice.
        
        Args:
            command: Create invoice command containing all necessary data
            
        Returns:
            DTO of the created invoice
            
        Raises:
            InvoiceCreationException: If the invoice cannot be created due to validation errors
        """
        logger.info(f"Creating invoice for order {command.invoice_fields.order_id}")
        
        try:
            # Extract invoice fields from command
            invoice_fields = command.invoice_fields
            
            # Generate invoice ID if not provided
            invoice_id = uuid4() if not hasattr(invoice_fields, "id") else invoice_fields.id
            
            # Create invoice items
            invoice_items = []
            for item_dto in invoice_fields.items:
                invoice_items.append(
                    InvoiceItem(
                        product_id=item_dto.product_id,
                        description=item_dto.description,
                        quantity=item_dto.quantity,
                        unit_price=item_dto.unit_price
                    )
                )
            
            # Calculate total amount if not provided
            total_amount = invoice_fields.total_amount
            if total_amount is None or total_amount <= 0:
                # Sum up the subtotals of all items
                total_items_amount = sum(item.subtotal for item in invoice_items)
                # Apply tax and discount
                total_amount = (
                    total_items_amount 
                    + invoice_fields.tax_amount 
                    - invoice_fields.discount_amount
                )
            
            # Create invoice entity
            invoice = Invoice(
                id=invoice_id,
                order_id=invoice_fields.order_id,
                user_id=invoice_fields.user_id,
                items=invoice_items,
                total_amount=total_amount,
                tax_amount=invoice_fields.tax_amount,
                discount_amount=invoice_fields.discount_amount,
                due_date=invoice_fields.due_date,
                notes=invoice_fields.notes
            )
            
            # Validate invoice
            self._validate_invoice(invoice)
            
            # Save invoice
            with self._uow:
                self._uow.invoices.add(invoice)
                self._uow.commit()
                
                # Convert to DTO
                invoice_dto = invoice_to_dto(invoice)
                logger.info(f"Invoice created successfully with ID: {invoice.id}")
                return invoice_dto
                
        except InvoiceCreationException:
            logger.error("Invoice validation failed")
            raise
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}", exc_info=True)
            raise InvoiceCreationException(f"Failed to create invoice: {str(e)}")
    
    def _validate_invoice(self, invoice: Invoice) -> None:
        """
        Validate the invoice entity.
        
        Args:
            invoice: The invoice to validate
            
        Raises:
            InvoiceCreationException: If validation fails
        """
        errors = []
        
        # Check required fields
        if not invoice.order_id:
            errors.append("Order ID is required")
        
        if not invoice.user_id:
            errors.append("User ID is required")
        
        if not invoice.items or len(invoice.items) == 0:
            errors.append("Invoice must have at least one item")
        
        if not invoice.due_date:
            errors.append("Due date is required")
        
        # Check that total amount is positive
        if invoice.total_amount <= 0:
            errors.append("Total amount must be greater than zero")
        
        # Ensure tax and discount amounts are non-negative
        if invoice.tax_amount < 0:
            errors.append("Tax amount cannot be negative")
        
        if invoice.discount_amount < 0:
            errors.append("Discount amount cannot be negative")
        
        # If there are validation errors, raise exception
        if errors:
            raise InvoiceCreationException(f"Invoice validation failed: {'; '.join(errors)}") 