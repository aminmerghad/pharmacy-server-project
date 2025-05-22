from typing import Optional, Dict, Any
import logging
from datetime import datetime
from uuid import UUID

from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.application.commands.update_invoice_command import UpdateInvoiceCommand
from app.services.invoice_service.application.dtos.invoice_dto import InvoiceDTO, InvoiceItemDTO
from app.services.invoice_service.application.dtos.converters import invoice_to_dto
from app.services.invoice_service.domain.exceptions.invoice_exceptions import (
    InvoiceNotFoundException,
    InvoiceUpdateException,
    InvalidInvoiceStateException
)
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus
from app.services.invoice_service.infrastructure.unit_of_work.unit_of_work import SQLAlchemyUnitOfWork

logger = logging.getLogger(__name__)

class UpdateInvoiceUseCase:
    """
    Use case for updating an existing invoice.
    Implements the business logic for invoice updates, including validation rules and status transitions.
    """
    
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow
        logger.info("UpdateInvoiceUseCase initialized")
    
    def execute(self, command: UpdateInvoiceCommand) -> InvoiceDTO:
        """
        Update an existing invoice.
        
        Args:
            command: Update invoice command containing invoice ID and fields to update
            
        Returns:
            DTO of the updated invoice
            
        Raises:
            InvoiceNotFoundException: If the invoice does not exist
            InvoiceUpdateException: If the invoice cannot be updated due to validation errors
            InvalidInvoiceStateException: If the invoice is in a state that cannot be updated
        """
        logger.info(f"Updating invoice with ID: {command.id}")
        
        try:
            # Get the invoice from the repository
            with self._uow:
                invoice = self._uow.invoices.get(command.id)
                
                if not invoice:
                    logger.error(f"Invoice not found: {command.id}")
                    raise InvoiceNotFoundException(f"Invoice with ID {command.id} not found")
                
                # Check if invoice can be updated (only pending invoices can be updated)
                if invoice.status != InvoiceStatus.PENDING:
                    logger.error(f"Cannot update invoice in status: {invoice.status}")
                    raise InvalidInvoiceStateException(
                        f"Cannot update invoice in status: {invoice.status}. Only pending invoices can be updated."
                    )
                
                # Update fields from command
                self._update_invoice_fields(invoice, command.invoice_fields)
                
                # Save updated invoice
                self._uow.invoices.save(invoice)
                self._uow.commit()
                
                # Convert to DTO and return
                invoice_dto = invoice_to_dto(invoice)
                logger.info(f"Invoice updated successfully: {invoice.id}")
                return invoice_dto
                
        except (InvoiceNotFoundException, InvalidInvoiceStateException):
            raise
        except Exception as e:
            logger.error(f"Error updating invoice: {str(e)}", exc_info=True)
            raise InvoiceUpdateException(f"Failed to update invoice: {str(e)}")
    
    def mark_as_paid(self, invoice_id: UUID, payment_details: Dict[str, Any]) -> InvoiceDTO:
        """
        Mark an invoice as paid.
        
        Args:
            invoice_id: ID of the invoice to mark as paid
            payment_details: Details of the payment
            
        Returns:
            DTO of the updated invoice
            
        Raises:
            InvoiceNotFoundException: If the invoice does not exist
            InvalidInvoiceStateException: If the invoice is already paid or cancelled
        """
        logger.info(f"Marking invoice as paid: {invoice_id}")
        
        try:
            # Get the invoice from the repository
            with self._uow:
                invoice = self._uow.invoices.get(invoice_id)
                
                if not invoice:
                    logger.error(f"Invoice not found: {invoice_id}")
                    raise InvoiceNotFoundException(f"Invoice with ID {invoice_id} not found")
                
                # Check if invoice can be marked as paid
                if invoice.status == InvoiceStatus.PAID:
                    logger.warning(f"Invoice {invoice_id} is already paid")
                    return invoice_to_dto(invoice)
                
                if invoice.status == InvoiceStatus.CANCELLED:
                    logger.error(f"Cannot pay cancelled invoice: {invoice_id}")
                    raise InvalidInvoiceStateException("Cannot pay a cancelled invoice")
                
                # Mark invoice as paid
                invoice.mark_as_paid(payment_details)
                
                # Save updated invoice
                self._uow.invoices.save(invoice)
                self._uow.commit()
                
                # Convert to DTO and return
                invoice_dto = invoice_to_dto(invoice)
                logger.info(f"Invoice marked as paid: {invoice.id}")
                return invoice_dto
                
        except (InvoiceNotFoundException, InvalidInvoiceStateException):
            raise
        except Exception as e:
            logger.error(f"Error marking invoice as paid: {str(e)}", exc_info=True)
            raise InvoiceUpdateException(f"Failed to mark invoice as paid: {str(e)}")
    
    def mark_as_overdue(self, invoice_id: UUID) -> InvoiceDTO:
        """
        Mark an invoice as overdue.
        
        Args:
            invoice_id: ID of the invoice to mark as overdue
            
        Returns:
            DTO of the updated invoice
            
        Raises:
            InvoiceNotFoundException: If the invoice does not exist
            InvalidInvoiceStateException: If the invoice is not in a valid state to be marked overdue
        """
        logger.info(f"Marking invoice as overdue: {invoice_id}")
        
        try:
            # Get the invoice from the repository
            with self._uow:
                invoice = self._uow.invoices.get(invoice_id)
                
                if not invoice:
                    logger.error(f"Invoice not found: {invoice_id}")
                    raise InvoiceNotFoundException(f"Invoice with ID {invoice_id} not found")
                
                # Check if invoice can be marked as overdue
                if invoice.status != InvoiceStatus.PENDING:
                    logger.error(f"Cannot mark invoice as overdue in status: {invoice.status}")
                    raise InvalidInvoiceStateException(
                        f"Cannot mark invoice as overdue in status: {invoice.status}. Only pending invoices can be marked as overdue."
                    )
                
                # Check if due date is in the past
                if invoice.due_date > datetime.now():
                    logger.error(f"Cannot mark invoice as overdue: due date is in the future")
                    raise InvalidInvoiceStateException("Cannot mark invoice as overdue: due date is in the future")
                
                # Mark invoice as overdue
                invoice.mark_as_overdue()
                
                # Save updated invoice
                self._uow.invoices.save(invoice)
                self._uow.commit()
                
                # Convert to DTO and return
                invoice_dto = invoice_to_dto(invoice)
                logger.info(f"Invoice marked as overdue: {invoice.id}")
                return invoice_dto
                
        except (InvoiceNotFoundException, InvalidInvoiceStateException):
            raise
        except Exception as e:
            logger.error(f"Error marking invoice as overdue: {str(e)}", exc_info=True)
            raise InvoiceUpdateException(f"Failed to mark invoice as overdue: {str(e)}")
    
    def _update_invoice_fields(self, invoice: Invoice, fields: Dict[str, Any]) -> None:
        """
        Update invoice fields from the command.
        
        Args:
            invoice: The invoice entity to update
            fields: Dictionary of fields to update
        """
        # Update fields if provided
        if hasattr(fields, "due_date") and fields.due_date is not None:
            invoice.due_date = fields.due_date
        
        if hasattr(fields, "tax_amount") and fields.tax_amount is not None:
            invoice.tax_amount = fields.tax_amount
        
        if hasattr(fields, "discount_amount") and fields.discount_amount is not None:
            invoice.discount_amount = fields.discount_amount
        
        if hasattr(fields, "notes") and fields.notes is not None:
            invoice.notes = fields.notes
        
        # Recalculate total amount if tax or discount changed
        if hasattr(fields, "tax_amount") or hasattr(fields, "discount_amount"):
            # Sum up the subtotals of all items
            total_items_amount = sum(item.subtotal for item in invoice.items)
            # Apply tax and discount
            invoice.total_amount = (
                total_items_amount 
                + invoice.tax_amount 
                - invoice.discount_amount
            ) 