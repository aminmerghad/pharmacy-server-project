import logging
from uuid import UUID
from typing import Optional

from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.application.dtos.invoice_dto import InvoiceDTO, InvoiceItemDTO
from app.services.invoice_service.application.dtos.converters import invoice_to_dto
from app.services.invoice_service.domain.exceptions.invoice_exceptions import InvoiceNotFoundException
from app.services.invoice_service.infrastructure.unit_of_work.unit_of_work import SQLAlchemyUnitOfWork

logger = logging.getLogger(__name__)

class GetInvoiceUseCase:
    """
    Use case for retrieving an invoice by ID.
    """
    
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow
        logger.info("GetInvoiceUseCase initialized")
    
    def execute(self, invoice_id: UUID) -> InvoiceDTO:
        """
        Get an invoice by its ID.
        
        Args:
            invoice_id: ID of the invoice to retrieve
            
        Returns:
            DTO of the invoice
            
        Raises:
            InvoiceNotFoundException: If the invoice is not found
        """
        logger.info(f"Getting invoice with ID: {invoice_id}")
        
        try:
            # Get the invoice from the repository
            with self._uow:
                invoice = self._uow.invoices.get(invoice_id)
                
                if not invoice:
                    logger.error(f"Invoice not found: {invoice_id}")
                    raise InvoiceNotFoundException(f"Invoice with ID {invoice_id} not found")
                
                # Convert to DTO and return
                invoice_dto = invoice_to_dto(invoice)
                logger.info(f"Invoice found: {invoice.id}")
                return invoice_dto
                
        except InvoiceNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error getting invoice: {str(e)}", exc_info=True)
            raise InvoiceNotFoundException(f"Failed to get invoice: {str(e)}")
    
    def get_by_order_id(self, order_id: UUID) -> Optional[InvoiceDTO]:
        """
        Get an invoice by its order ID.
        
        Args:
            order_id: Order ID to search for
            
        Returns:
            DTO of the invoice if found, None otherwise
        """
        logger.info(f"Getting invoice for order ID: {order_id}")
        
        try:
            # Get the invoice from the repository
            with self._uow:
                invoice = self._uow.invoices.find_by_order_id(order_id)
                
                if not invoice:
                    logger.info(f"No invoice found for order: {order_id}")
                    return None
                
                # Convert to DTO and return
                invoice_dto = invoice_to_dto(invoice)
                logger.info(f"Invoice found for order: {order_id}")
                return invoice_dto
                
        except Exception as e:
            logger.error(f"Error getting invoice by order ID: {str(e)}", exc_info=True)
            return None 