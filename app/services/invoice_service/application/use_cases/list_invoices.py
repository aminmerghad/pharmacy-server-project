import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID

from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.application.queries.list_invoices_query import ListInvoicesQuery
from app.services.invoice_service.application.dtos.invoice_dto import InvoiceDTO, InvoiceItemDTO, InvoiceListDTO
from app.services.invoice_service.application.dtos.converters import invoice_to_dto
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus
from app.services.invoice_service.infrastructure.unit_of_work.unit_of_work import SQLAlchemyUnitOfWork

logger = logging.getLogger(__name__)

class ListInvoicesUseCase:
    """
    Use case for listing invoices with pagination and filtering.
    """
    
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow
        logger.info("ListInvoicesUseCase initialized")
    
    def execute(self, query: ListInvoicesQuery) -> InvoiceListDTO:
        """
        List invoices with filtering and pagination.
        
        Args:
            query: The query parameters including filters, page, and page size
            
        Returns:
            DTO with list of invoices and pagination metadata
        """
        logger.info(f"Listing invoices with filters: {query.filters}")
        
        try:
            with self._uow:
                # Extract query parameters
                filters = query.filters or {}
                page = query.page or 1
                page_size = query.page_size or 20
                
                # Apply filters
                invoices = self._apply_filters(filters)
                
                # Get total count for pagination
                total_count = len(invoices)
                
                # Calculate pagination metadata
                total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
                start_index = (page - 1) * page_size
                end_index = min(start_index + page_size, total_count)
                
                # Get paginated results
                paginated_invoices = invoices[start_index:end_index] if total_count > 0 else []
                
                # Convert to DTOs
                invoice_dtos = [invoice_to_dto(invoice) for invoice in paginated_invoices]
                
                # Create list DTO with pagination metadata
                result = InvoiceListDTO(
                    items=invoice_dtos,
                    page=page,
                    page_size=page_size,
                    total_items=total_count,
                    total_pages=total_pages
                )
                
                logger.info(f"Found {total_count} invoices, returning page {page} of {total_pages}")
                return result
                
        except Exception as e:
            logger.error(f"Error listing invoices: {str(e)}", exc_info=True)
            # Return empty result on error rather than failing
            return InvoiceListDTO(
                items=[],
                page=query.page or 1,
                page_size=query.page_size or 20,
                total_items=0,
                total_pages=1
            )
    
    def _apply_filters(self, filters: Dict[str, Any]) -> List[Invoice]:
        """
        Apply filters to the invoice repository query.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List of filtered invoices
        """
        # Start with all invoices
        invoices = self._uow.invoices.get_all()
        
        # Apply specific filters
        if "user_id" in filters:
            user_id = filters["user_id"]
            invoices = [inv for inv in invoices if inv.user_id == user_id]
        
        if "order_id" in filters:
            order_id = filters["order_id"]
            invoices = [inv for inv in invoices if inv.order_id == order_id]
        
        if "status" in filters:
            status = filters["status"]
            invoices = [inv for inv in invoices if inv.status == status]
        
        if "due_date_before" in filters:
            date = filters["due_date_before"]
            invoices = [inv for inv in invoices if inv.due_date.date() <= date]
        
        if "due_date_after" in filters:
            date = filters["due_date_after"]
            invoices = [inv for inv in invoices if inv.due_date.date() >= date]
        
        if "created_at_after" in filters:
            date = filters["created_at_after"]
            invoices = [inv for inv in invoices if inv.created_at.date() >= date]
        
        if "search" in filters:
            search_term = filters["search"].lower()
            invoices = [
                inv for inv in invoices if (
                    search_term in str(inv.id).lower() or
                    search_term in str(inv.order_id).lower() or
                    search_term in str(inv.user_id).lower() or
                    (inv.notes and search_term in inv.notes.lower())
                )
            ]
        
        return invoices