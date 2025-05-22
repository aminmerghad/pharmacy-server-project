from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.services.invoice_service.domain.interfaces.invoice_repository import InvoiceRepository
from app.services.invoice_service.domain.exceptions.invoice_exceptions import (
    InvoiceNotFoundException,
    InvoiceAlreadyPaidException,
    InvoiceAlreadyCancelledException
)
from app.services.invoice_service.domain.value_objects.money import Money
from app.services.invoice_service.application.dtos.invoice_dto import InvoiceDTO, UpdateInvoiceDTO

class UpdateInvoiceCommand:
    """Command for updating an existing invoice."""
    
    def __init__(self, invoice_repository: InvoiceRepository):
        self.invoice_repository = invoice_repository
    
    def execute(self, invoice_id: str, data: UpdateInvoiceDTO) -> InvoiceDTO:
        """
        Execute the command to update an invoice.
        
        Args:
            invoice_id: ID of the invoice to update
            data: Data for updating the invoice
            
        Returns:
            A DTO representation of the updated invoice
            
        Raises:
            InvoiceNotFoundException: If the invoice is not found
            InvoiceAlreadyPaidException: If the invoice is already paid
            InvoiceAlreadyCancelledException: If the invoice is cancelled
        """
        # Get the invoice
        invoice = self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundException(invoice_id)
        
        # Check if the invoice can be modified
        if invoice.is_paid:
            raise InvoiceAlreadyPaidException(invoice_id)
        
        if invoice.is_cancelled:
            raise InvoiceAlreadyCancelledException(invoice_id)
        
        # Update the invoice fields
        if data.due_date is not None:
            days_extension = (data.due_date - invoice.due_date).days
            if days_extension > 0:
                invoice.extend_due_date(days_extension)
        
        if data.tax_amount is not None:
            invoice.apply_tax(Money(Decimal(str(data.tax_amount))))
        
        if data.discount_amount is not None:
            invoice.apply_discount(Money(Decimal(str(data.discount_amount))))
        
        if data.notes is not None and data.notes:
            invoice.add_notes(data.notes)
        
        # Save the updated invoice
        updated_invoice = self.invoice_repository.save(invoice)
        
        # Return as DTO
        return InvoiceDTO.from_entity(updated_invoice)

    def mark_as_overdue(self, invoice_id: str) -> InvoiceDTO:
        """
        Mark an invoice as overdue.
        
        Args:
            invoice_id: ID of the invoice to mark as overdue
            
        Returns:
            A DTO representation of the updated invoice
            
        Raises:
            InvoiceNotFoundException: If the invoice is not found
            ValueError: If the invoice cannot be marked as overdue
        """
        # Get the invoice
        invoice = self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundException(invoice_id)
        
        # Mark as overdue
        invoice.mark_as_overdue()
        
        # Save the updated invoice
        updated_invoice = self.invoice_repository.save(invoice)
        
        # Return as DTO
        return InvoiceDTO.from_entity(updated_invoice)
    
    def cancel_invoice(self, invoice_id: str) -> InvoiceDTO:
        """
        Cancel an invoice.
        
        Args:
            invoice_id: ID of the invoice to cancel
            
        Returns:
            A DTO representation of the updated invoice
            
        Raises:
            InvoiceNotFoundException: If the invoice is not found
            ValueError: If the invoice cannot be cancelled
        """
        # Get the invoice
        invoice = self.invoice_repository.get_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundException(invoice_id)
        
        # Cancel the invoice
        invoice.cancel()
        
        # Save the updated invoice
        updated_invoice = self.invoice_repository.save(invoice)
        
        # Return as DTO
        return InvoiceDTO.from_entity(updated_invoice) 