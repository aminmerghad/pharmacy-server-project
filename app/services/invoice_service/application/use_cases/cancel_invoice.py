from typing import Optional
import logging
from uuid import UUID

from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.application.dtos.invoice_dto import InvoiceDTO
from app.services.invoice_service.application.dtos.converters import invoice_to_dto
from app.services.invoice_service.application.commands.cancel_invoice_command import CancelInvoiceCommand
from app.services.invoice_service.domain.exceptions.invoice_exceptions import (
    InvoiceNotFoundException,
    InvalidInvoiceStateException,
    InvoiceOperationException
)
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus
from app.services.invoice_service.infrastructure.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork

logger = logging.getLogger(__name__)

class CancelInvoiceUseCase:
    """
    Use case for cancelling invoices.
    Handles the cancellation flow, including validation and status updates.
    """
    
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow
        logger.info("CancelInvoiceUseCase initialized")
    
    def execute(self, command: CancelInvoiceCommand) -> InvoiceDTO:
        """
        Cancel an invoice.
        
        Args:
            command: The command containing the invoice ID and optional reason
            
        Returns:
            DTO of the cancelled invoice
            
        Raises:
            InvoiceNotFoundException: If the invoice does not exist
            InvalidInvoiceStateException: If the invoice is already paid and cannot be cancelled
        """
        invoice_id = command.id
        reason = command.reason
        
        logger.info(f"Cancelling invoice: {invoice_id}")
        
        try:
            # Get the invoice from the repository
            with self._uow:
                invoice = self._uow.invoices.get(invoice_id)
                
                if not invoice:
                    logger.error(f"Invoice not found: {invoice_id}")
                    raise InvoiceNotFoundException(f"Invoice with ID {invoice_id} not found")
                
                # Check if invoice can be cancelled (only pending and overdue invoices can be cancelled)
                if invoice.status == InvoiceStatus.CANCELLED:
                    logger.warning(f"Invoice {invoice_id} is already cancelled")
                    return invoice_to_dto(invoice)
                
                if invoice.status == InvoiceStatus.PAID:
                    logger.error(f"Cannot cancel paid invoice: {invoice_id}")
                    raise InvalidInvoiceStateException("Cannot cancel a paid invoice")
                
                # Cancel the invoice
                invoice.cancel(reason)
                
                # Save updated invoice
                invoice = self._uow.invoices.update(invoice)
                
                # Convert to DTO and return
                invoice_dto = invoice_to_dto(invoice)
                logger.info(f"Invoice cancelled successfully: {invoice.id}")
                return invoice_dto
                
        except (InvoiceNotFoundException, InvalidInvoiceStateException):
            raise
        except Exception as e:
            logger.error(f"Error cancelling invoice: {str(e)}", exc_info=True)
            raise InvoiceOperationException(f"Failed to cancel invoice: {str(e)}") 