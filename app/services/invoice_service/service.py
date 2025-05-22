from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from uuid import UUID

from app.dataBase import Database
from app.services.invoice_service.application.commands.create_invoice_command import CreateInvoiceCommand
from app.services.invoice_service.application.commands.update_invoice_command import UpdateInvoiceCommand
from app.services.invoice_service.application.commands.process_payment_command import ProcessPaymentCommand
from app.services.invoice_service.application.commands.cancel_invoice_command import CancelInvoiceCommand
from app.services.invoice_service.application.queries.get_invoice_query import GetInvoiceQuery
from app.services.invoice_service.application.queries.get_invoices_by_filter_query import GetInvoicesByFilterQuery
from app.services.invoice_service.application.use_cases.create_invoice import CreateInvoiceUseCase
from app.services.invoice_service.application.use_cases.update_invoice import UpdateInvoiceUseCase
from app.services.invoice_service.application.use_cases.process_payment import ProcessPaymentUseCase
from app.services.invoice_service.application.use_cases.cancel_invoice import CancelInvoiceUseCase
from app.services.invoice_service.application.use_cases.get_invoice import GetInvoiceUseCase
from app.services.invoice_service.application.use_cases.list_invoices import ListInvoicesUseCase
from app.services.invoice_service.application.dtos.invoice_dto import InvoiceDTO, InvoiceListDTO
from app.services.invoice_service.domain.value_objects.payment_details import PaymentDetails
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus
from app.services.invoice_service.domain.exceptions.invoice_exceptions import (
    InvoiceServiceException, 
    InvoiceNotFoundException, 
    PaymentProcessingException, 
    InvalidInvoiceStateException
)
from app.services.invoice_service.infrastructure.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
from app.services.invoice_service.infrastructure.query_services.invoice_query_service import InvoiceQueryService
from app.services.invoice_service.infrastructure.adapters.invoice_event_adapter import InvoiceEventAdapter
from app.shared.acl.unified_acl import UnifiedACL
from app.shared.application.events.event_bus import EventBus

# Configure logger
logger = logging.getLogger(__name__)

class InvoiceService:
    """
    Service for managing invoices in the pharmacy system.
    Provides high-level API for invoice creation, management, and payment processing.
    """
    
    def __init__(self, db: Database, event_bus: EventBus, acl: UnifiedACL):
        """
        Initialize the invoice service.
        
        Args:
            db: Database connection 
            event_bus: Event bus for publishing events
            acl: Access control layer for authorization
        """
        self._db_session = db.get_session()
        self._acl = acl
        self._event_bus = event_bus
        self._init_resources()
        logger.info("Invoice service initialized")
        
    def _init_resources(self) -> None:
        """Initialize required resources and dependencies."""
        self._uow = SQLAlchemyUnitOfWork(
            self._db_session, 
            self._event_bus, 
            self._acl
        )
        self._query_service = InvoiceQueryService(self._db_session, self._uow)
        self._event_adapter = InvoiceEventAdapter(self._event_bus)
        self._create_invoice_use_case = CreateInvoiceUseCase(self._uow)
        self._update_invoice_use_case = UpdateInvoiceUseCase(self._uow)
        self._process_payment_use_case = ProcessPaymentUseCase(self._uow)
        self._cancel_invoice_use_case = CancelInvoiceUseCase(self._uow)
        self._list_invoices_use_case = ListInvoicesUseCase(self._uow)
    
    def create_invoice(self, command: CreateInvoiceCommand) -> InvoiceDTO:
        """
        Create a new invoice.
        
        Args:
            command: Command containing invoice creation data
            
        Returns:
            DTO of the created invoice
            
        Raises:
            InvoiceServiceException: If invoice creation fails
        """
        logger.info(f"Creating invoice for order: {command.invoice_fields.order_id}")
        try:
            result = self._create_invoice_use_case.execute(command)
            
            # Publish event
            try:
                self._event_adapter.publish_invoice_created(
                    invoice_id=result.id,
                    order_id=result.order_id,
                    user_id=result.user_id,
                    total_amount=result.total_amount,
                    due_date=result.due_date
                )
            except Exception as e:
                # Log but continue if event publishing fails
                logger.error(f"Failed to publish invoice.created event: {str(e)}")
            
            logger.info(f"Invoice created successfully with ID: {result.id}")
            return result
        except Exception as e:
            self._uow.rollback()
            logger.error(f"Failed to create invoice: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to create invoice: {str(e)}")
    
    def update_invoice(self, command: UpdateInvoiceCommand) -> InvoiceDTO:
        """
        Update an existing invoice.
        
        Args:
            command: Command containing invoice update data
            
        Returns:
            DTO of the updated invoice
            
        Raises:
            InvoiceNotFoundException: If invoice doesn't exist
            InvoiceServiceException: If update fails
        """
        logger.info(f"Updating invoice with ID: {command.id}")
        try:
            # Get current invoice to track status changes
            current_invoice = self._query_service.get_by_id(GetInvoiceQuery(id=command.id))
            if not current_invoice:
                logger.error(f"Invoice not found: {command.id}")
                raise InvoiceNotFoundException(f"Invoice not found: {command.id}")
                
            result = self._update_invoice_use_case.execute(command)
            
            # Check if status changed and publish event if it did
            if current_invoice.status != result.status:
                try:
                    self._event_adapter.publish_invoice_status_changed(
                        invoice_id=result.id,
                        order_id=result.order_id,
                        user_id=result.user_id,
                        previous_status=current_invoice.status,
                        new_status=result.status
                    )
                except Exception as e:
                    # Log but continue if event publishing fails
                    logger.error(f"Failed to publish invoice.status_changed event: {str(e)}")
            
            logger.info(f"Invoice updated successfully: {result.id}")
            return result
        except InvoiceNotFoundException:
            logger.error(f"Invoice not found: {command.id}")
            raise
        except Exception as e:
            self._uow.rollback()
            logger.error(f"Error updating invoice: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to update invoice: {str(e)}")
    
    def process_payment(self, command: ProcessPaymentCommand) -> InvoiceDTO:        
        """
        Process a payment for an invoice.
        
        Args:
            command: Command containing invoice ID and payment details
            
        Returns:
            DTO of the updated invoice with payment details
            
        Raises:
            InvoiceNotFoundException: If invoice doesn't exist
            PaymentProcessingException: If payment processing fails
            InvalidInvoiceStateException: If invoice is in invalid state for payment
        """
        logger.info(f"Processing payment for invoice with ID: {command.id}")
        
        try:
            # Call the use case to process the payment
            result = self._process_payment_use_case.execute(command)
            
            # Publish paid event if payment is complete
            if result.status == InvoiceStatus.PAID:
                try:
                    self._event_adapter.publish_invoice_paid(
                        invoice_id=result.id,
                        order_id=result.order_id,
                        user_id=result.user_id,
                        amount_paid=result.total_amount,
                        payment_method=result.payment_details.payment_method,
                        transaction_id=result.payment_details.transaction_id
                    )
                    logger.info(f"Payment completed for invoice: {command.id}")
                except Exception as e:
                    # If event publishing fails, log but don't fail the request
                    logger.error(f"Error publishing payment event: {str(e)}")
            else:
                # If payment is not complete, log the payment URL for the client
                payment_url = None
                if result.payment_details and result.payment_details.payment_reference:
                    payment_url = result.payment_details.payment_reference
                    logger.info(f"Payment requires customer action. URL: {payment_url}")
            
            return result
            
        except (InvoiceNotFoundException, PaymentProcessingException, InvalidInvoiceStateException) as e:
            # Domain-specific exceptions are logged and re-raised
            logger.error(f"Payment processing error: {str(e)}")
            raise
        except Exception as e:
            # Unexpected errors are wrapped in a PaymentProcessingException
            error_msg = f"Unexpected error processing payment: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise PaymentProcessingException(str(command.id), error_msg)
    
    def cancel_invoice(self, command: CancelInvoiceCommand) -> InvoiceDTO:
        """
        Cancel an invoice.
        
        Args:
            command: Command containing invoice ID and cancellation reason
            
        Returns:
            DTO of the cancelled invoice
            
        Raises:
            InvoiceNotFoundException: If invoice doesn't exist
            InvoiceServiceException: If cancellation fails
        """
        logger.info(f"Cancelling invoice with ID: {command.id}")
        try:
            # Get invoice before cancellation to access its data
            invoice = self._query_service.get_by_id(GetInvoiceQuery(id=command.id))
            if not invoice:
                logger.error(f"Invoice not found: {command.id}")
                raise InvoiceNotFoundException(f"Invoice not found: {command.id}")
                
            result = self._cancel_invoice_use_case.execute(command)
            
            # Publish cancelled event
            try:
                self._event_adapter.publish_invoice_cancelled(
                    invoice_id=result.id,
                    order_id=result.order_id,
                    user_id=result.user_id,
                    reason=command.reason
                )
            except Exception as e:
                # Log but continue if event publishing fails
                logger.error(f"Failed to publish invoice.cancelled event: {str(e)}")
            
            logger.info(f"Invoice cancelled successfully: {command.id}")
            return result
        except InvoiceNotFoundException:
            raise
        except Exception as e:
            self._uow.rollback()
            logger.error(f"Error cancelling invoice: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to cancel invoice: {str(e)}")
    
    def get_invoice(self, query: GetInvoiceQuery) -> InvoiceDTO:
        """
        Get an invoice by ID.
        
        Args:
            query: Query containing the invoice ID
            
        Returns:
            DTO of the invoice
            
        Raises:
            InvoiceNotFoundException: If invoice doesn't exist
            InvoiceServiceException: If retrieval fails
        """
        invoice_id = query.id
        logger.info(f"Getting invoice with ID: {invoice_id}")
        try:
            result = self._query_service.get_by_id(query)
            if result:
                logger.info(f"Invoice found: {invoice_id}")
                return result
            else:
                logger.info(f"Invoice not found: {invoice_id}")
                raise InvoiceNotFoundException(f"Invoice with ID {invoice_id} not found")
        except InvoiceNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error getting invoice: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to get invoice: {str(e)}")
    
    def list_invoices(self, query: GetInvoicesByFilterQuery) -> InvoiceListDTO:
        """
        List invoices based on filter criteria.
        
        Args:
            query: Query containing filter criteria
            
        Returns:
            DTO containing list of invoices with pagination information
            
        Raises:
            InvoiceServiceException: If listing fails
        """
        logger.info("Listing invoices")
        try:
            result = self._query_service.list(query)
            logger.info(f"Found {result.total_items} invoices matching criteria")
            return result
        except Exception as e:
            logger.error(f"Error listing invoices: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to list invoices: {str(e)}")
    
    def get_invoices_by_user(self, user_id: UUID, page: int = 1, page_size: int = 20) -> InvoiceListDTO:
        """
        Get invoices for a specific user.
        
        Args:
            user_id: ID of the user
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Invoice list DTO with pagination information
            
        Raises:
            InvoiceServiceException: If retrieval fails
        """
        logger.info(f"Getting invoices for user: {user_id}")
        try:
            # Create a query with user filter
            filters = {"user_id": user_id}
            query = GetInvoicesByFilterQuery(
                filters=filters,
                page=page,
                page_size=page_size
            )
            
            # Delegate to list invoices use case
            result = self._list_invoices_use_case.execute(query)
            logger.info(f"Found {result.total_items} invoices for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting invoices for user: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to get invoices for user: {str(e)}")
    
    def get_invoices_by_status(self, status: InvoiceStatus, page: int = 1, page_size: int = 20) -> InvoiceListDTO:
        """
        Get invoices with a specific status.
        
        Args:
            status: Invoice status to filter by
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Invoice list DTO with pagination information
            
        Raises:
            InvoiceServiceException: If retrieval fails
        """
        logger.info(f"Getting invoices with status: {status}")
        try:
            # Create a query with status filter
            filters = {"status": status}
            query = GetInvoicesByFilterQuery(
                filters=filters,
                page=page,
                page_size=page_size
            )
            
            # Delegate to list invoices use case
            result = self._list_invoices_use_case.execute(query)
            logger.info(f"Found {result.total_items} invoices with status {status}")
            return result
        except Exception as e:
            logger.error(f"Error getting invoices by status: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to get invoices by status: {str(e)}")
    
    def get_overdue_invoices(self, page: int = 1, page_size: int = 20) -> InvoiceListDTO:
        """
        Get all overdue invoices.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Invoice list DTO with pagination information
            
        Raises:
            InvoiceServiceException: If retrieval fails
        """
        logger.info("Getting overdue invoices")
        try:
            # Get current date for comparison
            current_date = datetime.now().date()
            
            # Create a query with overdue filter
            filters = {
                "status": InvoiceStatus.PENDING,
                "due_date_before": current_date
            }
            query = GetInvoicesByFilterQuery(
                filters=filters,
                page=page,
                page_size=page_size
            )
            
            # Delegate to list invoices use case
            result = self._list_invoices_use_case.execute(query)
            logger.info(f"Found {result.total_items} overdue invoices")
            return result
        except Exception as e:
            logger.error(f"Error getting overdue invoices: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to get overdue invoices: {str(e)}")
    
    def check_and_update_overdue_invoices(self) -> int:
        """
        Check for overdue invoices and update their status.
        
        Returns:
            Number of invoices updated
            
        Raises:
            InvoiceServiceException: If update fails
        """
        logger.info("Checking for overdue invoices")
        try:
            current_date = datetime.now().date()
            
            # Get pending invoices with due dates in the past
            filters = {
                "status": InvoiceStatus.PENDING,
                "due_date_before": current_date
            }
            
            query = GetInvoicesByFilterQuery(filters=filters)
            overdue_invoices = self._query_service.list(query)
            
            update_count = 0
            update_errors = 0
            
            for invoice in overdue_invoices.items:
                try:
                    # Update to overdue status
                    update_command = UpdateInvoiceCommand(
                        id=invoice.id,
                        invoice_fields={"status": InvoiceStatus.OVERDUE}
                    )
                    
                    self.update_invoice(update_command)
                    update_count += 1
                except Exception as e:
                    # Log error but continue with other invoices
                    logger.error(f"Error updating invoice {invoice.id} to overdue: {str(e)}")
                    update_errors += 1
                
            logger.info(f"Updated {update_count} invoices to overdue status. Failed: {update_errors}")
            return update_count
        except Exception as e:
            logger.error(f"Error checking overdue invoices: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to check and update overdue invoices: {str(e)}")
    
    def handle_order_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Handle order-related events from the Order service.
        
        Args:
            event_type: Type of the event (e.g., order.created, order.cancelled)
            event_data: Data associated with the event
            
        Returns:
            True if the event was handled successfully, False otherwise
        """
        logger.info(f"Handling order event: {event_type}")
        try:
            # Validate required fields
            if event_type not in ["order.created", "order.cancelled"]:
                logger.warning(f"Unhandled order event type: {event_type}")
                return False
                
            if "order_id" not in event_data:
                logger.error(f"Missing required field 'order_id' in event data")
                return False
                
            if event_type == "order.created":
                # Validate required fields for order creation
                if "user_id" not in event_data:
                    logger.error(f"Missing required field 'user_id' in order.created event")
                    return False
                    
                # Create a new invoice for the order
                order_id = UUID(event_data["order_id"])
                user_id = UUID(event_data["user_id"])
                
                # Create due date (30 days from now by default)
                due_date = datetime.now() + timedelta(days=30)
                
                # Create invoice command
                command = CreateInvoiceCommand(
                    order_id=order_id,
                    user_id=user_id,
                    due_date=due_date,
                    items=event_data.get("items", []),
                    tax_amount=event_data.get("tax_amount", 0),
                    discount_amount=event_data.get("discount_amount", 0)
                )
                
                self.create_invoice(command)
                logger.info(f"Invoice created for order: {order_id}")
                return True
                
            elif event_type == "order.cancelled":
                # Cancel any pending invoices for this order
                order_id = UUID(event_data["order_id"])
                invoice = self._query_service.get_by_order_id(order_id)
                
                if invoice and invoice.status in [InvoiceStatus.PENDING, InvoiceStatus.OVERDUE]:
                    reason = "Order was cancelled"
                    self.cancel_invoice(CancelInvoiceCommand(id=invoice.id, reason=reason))
                    logger.info(f"Invoice {invoice.id} cancelled due to order cancellation")
                    return True
                    
                logger.info(f"No pending invoice found for cancelled order: {order_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error handling order event {event_type}: {str(e)}", exc_info=True)
            return False
    
    # Enhanced search methods
    
    def search_invoices(self, search_term: str, page: int = 1, page_size: int = 20) -> InvoiceListDTO:
        """
        Search for invoices by various criteria.
        
        Args:
            search_term: The search term to look for
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Invoice list with pagination information
            
        Raises:
            InvoiceServiceException: If search fails
        """
        logger.info(f"Searching invoices with term: {search_term}")
        try:
            # Create a query with search filter
            filters = {"search": search_term}
            query = GetInvoicesByFilterQuery(
                filters=filters,
                page=page,
                page_size=page_size
            )
            
            result = self._query_service.list(query)
            logger.info(f"Found {result.total_items} invoices matching '{search_term}'")
            return result
        except Exception as e:
            logger.error(f"Error searching invoices: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to search invoices: {str(e)}")
    
    def get_invoices_by_date_range(self, start_date: datetime, end_date: datetime, 
                                page: int = 1, page_size: int = 20) -> InvoiceListDTO:
        """
        Get invoices created within a specific date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Invoice list DTO with pagination information
            
        Raises:
            InvoiceServiceException: If retrieval fails
        """
        logger.info(f"Getting invoices from {start_date} to {end_date}")
        try:
            # Validate date range
            if end_date < start_date:
                raise ValueError("End date must be after start date")
                
            filters = {
                "created_at_after": start_date.date(),
                "created_at_before": end_date.date()
            }
            query = GetInvoicesByFilterQuery(
                filters=filters,
                page=page,
                page_size=page_size
            )
            
            result = self._list_invoices_use_case.execute(query)
            logger.info(f"Found {result.total_items} invoices in date range")
            return result
        except ValueError as e:
            logger.error(f"Invalid date range: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting invoices by date range: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to get invoices by date range: {str(e)}")
    
    def get_invoices_by_amount_range(self, min_amount: float, max_amount: float,
                                   page: int = 1, page_size: int = 20) -> InvoiceListDTO:
        """
        Get invoices with total amount within a specific range.
        
        Args:
            min_amount: Minimum total amount
            max_amount: Maximum total amount
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Invoice list DTO with pagination information
            
        Raises:
            InvoiceServiceException: If retrieval fails
        """
        logger.info(f"Getting invoices with amount between {min_amount} and {max_amount}")
        try:
            # Validate amount range
            if min_amount < 0 or max_amount < 0:
                raise ValueError("Amount values cannot be negative")
                
            if max_amount < min_amount:
                raise ValueError("Maximum amount must be greater than minimum amount")
                
            filters = {
                "min_amount": min_amount,
                "max_amount": max_amount
            }
            query = GetInvoicesByFilterQuery(
                filters=filters,
                page=page,
                page_size=page_size
            )
            
            result = self._list_invoices_use_case.execute(query)
            logger.info(f"Found {result.total_items} invoices in amount range")
            return result
        except ValueError as e:
            logger.error(f"Invalid amount range: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting invoices by amount range: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to get invoices by amount range: {str(e)}")
    
    def get_upcoming_due_invoices(self, days: int = 7, page: int = 1, page_size: int = 20) -> InvoiceListDTO:
        """
        Get invoices that are due within a specific number of days.
        
        Args:
            days: Number of days from now
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Invoice list DTO with pagination information
            
        Raises:
            InvoiceServiceException: If retrieval fails
        """
        logger.info(f"Getting invoices due within {days} days")
        try:
            # Validate days parameter
            if days < 1:
                raise ValueError("Days parameter must be positive")
                
            today = datetime.now().date()
            due_date = today + timedelta(days=days)
            
            filters = {
                "status": InvoiceStatus.PENDING,
                "due_date_after": today,
                "due_date_before": due_date
            }
            query = GetInvoicesByFilterQuery(
                filters=filters,
                page=page,
                page_size=page_size
            )
            
            result = self._list_invoices_use_case.execute(query)
            logger.info(f"Found {result.total_items} invoices due within {days} days")
            return result
        except ValueError as e:
            logger.error(f"Invalid days parameter: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting upcoming due invoices: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to get upcoming due invoices: {str(e)}")
    
    def get_invoice_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about invoices in the system.
        
        Returns:
            Dictionary containing various statistics about invoices
            
        Raises:
            InvoiceServiceException: If retrieval fails
        """
        logger.info("Getting invoice statistics")
        try:
            # Get counts by status - use pagination to limit memory usage while still getting all records
            pending_invoices = self.get_invoices_by_status(InvoiceStatus.PENDING, page_size=1000)
            paid_invoices = self.get_invoices_by_status(InvoiceStatus.PAID, page_size=1000)
            overdue_invoices = self.get_invoices_by_status(InvoiceStatus.OVERDUE, page_size=1000)
            cancelled_invoices = self.get_invoices_by_status(InvoiceStatus.CANCELLED, page_size=1000)
            
            pending_count = pending_invoices.total_items
            paid_count = paid_invoices.total_items
            overdue_count = overdue_invoices.total_items
            cancelled_count = cancelled_invoices.total_items
            total_count = pending_count + paid_count + overdue_count + cancelled_count
            
            # Calculate amounts
            pending_amount = sum(invoice.total_amount for invoice in pending_invoices.items)
            paid_amount = sum(invoice.total_amount for invoice in paid_invoices.items)
            overdue_amount = sum(invoice.total_amount for invoice in overdue_invoices.items)
            total_amount = pending_amount + paid_amount + overdue_amount
            
            return {
                "total_invoices": total_count,
                "status_counts": {
                    "pending": pending_count,
                    "paid": paid_count,
                    "overdue": overdue_count,
                    "cancelled": cancelled_count
                },
                "amounts": {
                    "total": total_amount,
                    "paid": paid_amount,
                    "pending": pending_amount,
                    "overdue": overdue_amount
                },
                "overdue_percentage": (overdue_count / total_count * 100) if total_count else 0,
                "paid_percentage": (paid_count / total_count * 100) if total_count else 0
            }
        except Exception as e:
            logger.error(f"Error getting invoice statistics: {str(e)}", exc_info=True)
            raise InvoiceServiceException(f"Failed to get invoice statistics: {str(e)}")