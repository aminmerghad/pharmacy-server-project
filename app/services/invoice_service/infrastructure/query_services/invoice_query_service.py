from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from uuid import UUID
import logging
from datetime import datetime

from app.services.invoice_service.application.queries.get_invoice_query import GetInvoiceQuery
from app.services.invoice_service.application.queries.get_invoices_by_filter_query import GetInvoicesByFilterQuery
from app.services.invoice_service.application.dtos.invoice_dto import InvoiceDTO, InvoiceListDTO
from app.services.invoice_service.application.dtos.converters import invoice_to_dto
from app.services.invoice_service.domain.exceptions.invoice_exceptions import InvoiceNotFoundException
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus
from app.services.invoice_service.infrastructure.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork

logger = logging.getLogger(__name__)

class InvoiceQueryService:
    """
    Service for querying invoice data from the database.
    Implements specialized query methods to fetch invoice data in various ways.
    """
    
    def __init__(self, db_session: Session, uow: SQLAlchemyUnitOfWork):
        self._db_session = db_session
        self._uow = uow
        logger.info("Invoice query service initialized")
    
    def get_by_id(self, query: GetInvoiceQuery) -> Optional[InvoiceDTO]:
        """
        Get an invoice by its ID.
        
        Args:
            query: The query containing the invoice ID to retrieve
            
        Returns:
            InvoiceDTO if found, None otherwise
        """
        invoice_id = query.id
        logger.info(f"Querying invoice with ID: {invoice_id}")
        try:
            with self._uow:
                invoice = self._uow.invoices.get(invoice_id)
                if not invoice:
                    logger.warning(f"Invoice not found: {invoice_id}")
                    return None
                
                result = invoice_to_dto(invoice)
                logger.info(f"Invoice found: {invoice_id}")
                return result
        except InvoiceNotFoundException as e:
            logger.warning(f"Invoice not found: {invoice_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting invoice by ID: {str(e)}", exc_info=True)
            raise
    
    def get_by_order_id(self, order_id: UUID) -> Optional[InvoiceDTO]:
        """
        Get an invoice by its associated order ID.
        
        Args:
            order_id: The order ID to find the invoice for
            
        Returns:
            InvoiceDTO if found, None otherwise
        """
        logger.info(f"Querying invoice for order ID: {order_id}")
        try:
            with self._uow:
                invoice = self._uow.invoices.find_by_order_id(order_id)
                if not invoice:
                    logger.info(f"No invoice found for order: {order_id}")
                    return None
                
                result = invoice_to_dto(invoice)
                logger.info(f"Invoice found for order: {order_id}")
                return result
        except Exception as e:
            logger.error(f"Error getting invoice by order ID: {str(e)}", exc_info=True)
            return None
    
    def list(self, query: GetInvoicesByFilterQuery) -> InvoiceListDTO:
        """
        List invoices with filters and pagination.
        
        Args:
            query: List invoices query object containing filters and pagination settings
            
        Returns:
            InvoiceListDTO containing paginated results and total count
        """
        filters = query.filters or {}
        
        # If specific filters are set in the query, add them to the filters dict
        if query.user_id:
            filters["user_id"] = query.user_id
        if query.order_id:
            filters["order_id"] = query.order_id
        if query.status:
            filters["status"] = query.status
        if query.created_at_after:
            filters["created_at_after"] = query.created_at_after
        if query.created_at_before:
            filters["created_at_before"] = query.created_at_before
        if query.due_date_after:
            filters["due_date_after"] = query.due_date_after
        if query.due_date_before:
            filters["due_date_before"] = query.due_date_before
        if query.min_amount:
            filters["min_amount"] = query.min_amount
        if query.max_amount:
            filters["max_amount"] = query.max_amount
        if query.search:
            filters["search"] = query.search
        
        logger.info(f"Listing invoices with filters: {filters}")
        try:
            with self._uow:
                # Apply filters
                invoices = self._apply_filters(filters)
                
                # Apply sorting
                invoices = self._apply_sorting(invoices, query.sort_by, query.sort_direction)
                
                # Get total count for pagination
                total_count = len(invoices)
                
                # Calculate pagination metadata
                total_pages = max(1, (total_count + query.page_size - 1) // query.page_size)
                start_index = (query.page - 1) * query.page_size
                end_index = min(start_index + query.page_size, total_count)
                
                # Get paginated results
                paginated_invoices = invoices[start_index:end_index] if total_count > 0 else []
                
                # Convert to DTOs
                invoice_dtos = [invoice_to_dto(invoice) for invoice in paginated_invoices]
                
                # Create list DTO with pagination metadata
                result = InvoiceListDTO(
                    items=invoice_dtos,
                    page=query.page,
                    page_size=query.page_size,
                    total_items=total_count,
                    total_pages=total_pages
                )
                
                logger.info(f"Found {len(result.items)} invoices")
                return result
        except Exception as e:
            logger.error(f"Error listing invoices: {str(e)}", exc_info=True)
            raise
            
    def _apply_filters(self, filters: Dict[str, Any]) -> List:
        """
        Apply filters to the invoice repository query.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List of filtered invoices
        """
        # Start with all invoices
        invoices = self._uow.invoices.get_all()
        
        # Apply basic filters
        if "user_id" in filters:
            user_id = filters["user_id"]
            invoices = [inv for inv in invoices if inv.user_id == user_id]
        
        if "order_id" in filters:
            order_id = filters["order_id"]
            invoices = [inv for inv in invoices if inv.order_id == order_id]
        
        if "status" in filters:
            status = filters["status"]
            invoices = [inv for inv in invoices if inv.status == status]
        
        # Date filters
        if "due_date_before" in filters:
            due_date = filters["due_date_before"]
            invoices = [inv for inv in invoices if inv.due_date.date() <= due_date]
            
        if "due_date_after" in filters:
            due_date = filters["due_date_after"]
            invoices = [inv for inv in invoices if inv.due_date.date() >= due_date]
            
        if "created_at_before" in filters:
            created_date = filters["created_at_before"]
            invoices = [inv for inv in invoices if inv.created_at.date() <= created_date]
            
        if "created_at_after" in filters:
            created_date = filters["created_at_after"]
            invoices = [inv for inv in invoices if inv.created_at.date() >= created_date]
        
        # Amount filters
        if "min_amount" in filters:
            min_amount = filters["min_amount"]
            invoices = [inv for inv in invoices if inv.total_amount >= min_amount]
            
        if "max_amount" in filters:
            max_amount = filters["max_amount"]
            invoices = [inv for inv in invoices if inv.total_amount <= max_amount]
        
        # Search filter
        if "search" in filters and filters["search"]:
            search_term = filters["search"].lower()
            filtered_invoices = []
            for inv in invoices:
                # Search in various fields
                if (str(inv.id).lower().find(search_term) >= 0 or
                    str(inv.order_id).lower().find(search_term) >= 0 or
                    str(inv.user_id).lower().find(search_term) >= 0 or
                    (inv.notes and inv.notes.lower().find(search_term) >= 0)):
                    filtered_invoices.append(inv)
            invoices = filtered_invoices
            
        return invoices
    
    def _apply_sorting(self, invoices: List, sort_by: str, sort_direction: str) -> List:
        """
        Apply sorting to the list of invoices.
        
        Args:
            invoices: List of invoices to sort
            sort_by: Field to sort by
            sort_direction: Direction of sort (asc or desc)
            
        Returns:
            Sorted list of invoices
        """
        reverse = sort_direction.lower() == "desc"
        
        if sort_by == "id":
            return sorted(invoices, key=lambda inv: inv.id, reverse=reverse)
        elif sort_by == "order_id":
            return sorted(invoices, key=lambda inv: inv.order_id, reverse=reverse)
        elif sort_by == "user_id":
            return sorted(invoices, key=lambda inv: inv.user_id, reverse=reverse)
        elif sort_by == "total_amount":
            return sorted(invoices, key=lambda inv: inv.total_amount, reverse=reverse)
        elif sort_by == "due_date":
            return sorted(invoices, key=lambda inv: inv.due_date, reverse=reverse)
        elif sort_by == "status":
            return sorted(invoices, key=lambda inv: inv.status.value, reverse=reverse)
        elif sort_by == "created_at":
            return sorted(invoices, key=lambda inv: inv.created_at, reverse=reverse)
        else:
            # Default to sorting by created_at
            return sorted(invoices, key=lambda inv: inv.created_at, reverse=reverse) 