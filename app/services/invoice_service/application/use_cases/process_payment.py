from typing import Optional, Dict, Any
import logging
from datetime import datetime
from uuid import UUID
from contextlib import contextmanager

from app.services.invoice_service.domain.entities.invoice import Invoice
from app.services.invoice_service.application.commands.process_payment_command import ProcessPaymentCommand
from app.services.invoice_service.application.dtos.invoice_dto import InvoiceDTO
from app.services.invoice_service.application.dtos.converters import invoice_to_dto
from app.services.invoice_service.domain.value_objects.payment_details import PaymentDetails
from app.services.invoice_service.domain.exceptions.invoice_exceptions import (
    InvoiceNotFoundException,
    PaymentProcessingException,
    InvalidInvoiceStateException
)
from app.services.invoice_service.domain.enums.invoice_status import InvoiceStatus
from app.services.invoice_service.infrastructure.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
from app.services.invoice_service.infrastructure.adapters.payment_processor_adapter import PaymentProcessorAdapter

logger = logging.getLogger(__name__)

class ProcessPaymentUseCase:
    """
    Use case for processing payments for invoices.
    Handles the payment processing flow, including validation and status updates.
    """
    
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow
        self._payment_processor = PaymentProcessorAdapter()
        logger.info("ProcessPaymentUseCase initialized with PaymentProcessorAdapter")
    
    def execute(self, command: ProcessPaymentCommand) -> InvoiceDTO:
        """
        Process a payment for an invoice.
        
        Args:
            command: Process payment command containing invoice ID and payment details
            
        Returns:
            DTO of the updated invoice
            
        Raises:
            InvoiceNotFoundException: If the invoice does not exist
            InvalidInvoiceStateException: If the invoice is already paid or cancelled
            PaymentProcessingException: If the payment processing fails
        """
        logger.info(f"Processing payment for invoice: {command.id}")
        
        # Validate the command
        if not command.id:
            error_msg = "Invalid command: Missing invoice ID"
            logger.error(error_msg)
            raise PaymentProcessingException(str(command.id), error_msg)
            
        if not command.payment_details:
            error_msg = "Invalid command: Missing payment details"
            logger.error(error_msg)
            raise PaymentProcessingException(str(command.id), error_msg)
        
        try:
            # Get the invoice from the repository
            with self._uow:
                # Get invoice
                invoice = self._uow.invoices.get(command.id)
                
                if not invoice:
                    logger.error(f"Invoice not found: {command.id}")
                    raise InvoiceNotFoundException(f"Invoice with ID {command.id} not found")
                
                # Validate invoice state
                self._validate_invoice_state(invoice, command)
                
                # Process the payment
                payment_result = self._process_payment_with_processor(invoice, command)
                
                # Create payment details value object
                payment_details = self._create_payment_details(payment_result, command)
                
                # Update the invoice with payment details
                invoice.process_payment(payment_details)
                
                # Save updated invoice
                invoice = self._uow.invoices.update(invoice)
                self._uow.commit()
                
                # Convert to DTO and return
                invoice_dto = invoice_to_dto(invoice)
                
                # Log transaction details
                payment_reference = payment_details.payment_reference or "No payment URL"
                logger.info(f"Payment processed for invoice: {invoice.id}, transaction ID: {payment_details.transaction_id}, URL: {payment_reference}")
                
                return invoice_dto
                
        except (InvoiceNotFoundException, InvalidInvoiceStateException) as e:
            # Domain exceptions should be propagated as-is
            logger.error(str(e))
            self._uow.rollback()
            raise
        except PaymentProcessingException as e:
            # Payment processing failures
            logger.error(f"Payment processing failed: {str(e)}")
            self._uow.rollback()
            raise
        except Exception as e:
            # Unexpected errors
            error_msg = f"Unexpected error processing payment: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._uow.rollback()
            raise PaymentProcessingException(str(command.id), error_msg)
    
    def _validate_invoice_state(self, invoice: Invoice, command: ProcessPaymentCommand) -> None:
        """
        Validate that the invoice is in a valid state for payment.
        
        Args:
            invoice: The invoice to validate
            command: The payment command
            
        Raises:
            InvalidInvoiceStateException: If the invoice cannot be paid
        """
        # Check if invoice can be paid
        if invoice.status == InvoiceStatus.PAID:
            logger.warning(f"Invoice {command.id} is already paid")
            raise InvalidInvoiceStateException("Invoice is already paid")
        
        if invoice.status == InvoiceStatus.CANCELLED:
            logger.error(f"Cannot pay cancelled invoice: {command.id}")
            raise InvalidInvoiceStateException("Cannot pay a cancelled invoice")
        
        # Validate payment amount
        payment_amount = command.payment_details.amount
        if payment_amount < invoice.total_amount.amount:
            logger.error(f"Payment amount {payment_amount} is less than invoice total {invoice.total_amount.amount}")
            raise PaymentProcessingException(
                str(command.id),
                f"Payment amount {payment_amount} is less than invoice total {invoice.total_amount.amount}"
            )
    
    def _process_payment_with_processor(self, invoice: Invoice, command: ProcessPaymentCommand) -> PaymentDetails:
        """
        Process the payment through the payment processor.
        
        Args:
            invoice: The invoice to process payment for
            command: The payment command
            
        Returns:
            Payment details from the processor
            
        Raises:
            PaymentProcessingException: If payment processing fails
        """
        logger.info(f"Calling payment processor for invoice {command.id}")
        try:
            payment_result = self._payment_processor.process_payment(
                invoice_id=str(command.id),
                amount=command.payment_details.amount,
                payment_method=command.payment_details.payment_method,
                payment_info=command.payment_details.payment_info or {}
            )
            
            # Check if we got a valid result back
            if not payment_result or not payment_result.transaction_id:
                error_msg = f"Payment processor did not return valid transaction for invoice {command.id}"
                logger.error(error_msg)
                raise PaymentProcessingException(str(command.id), error_msg)
            
            # Log the payment URL if one was provided
            if payment_result.payment_reference:
                logger.info(f"Payment URL for invoice {command.id}: {payment_result.payment_reference}")
            
            return payment_result
        except Exception as e:
            if isinstance(e, PaymentProcessingException):
                raise
            error_msg = f"Error communicating with payment processor: {str(e)}"
            logger.error(error_msg)
            raise PaymentProcessingException(str(command.id), error_msg)
    
    def _create_payment_details(self, payment_result: PaymentDetails, command: ProcessPaymentCommand) -> PaymentDetails:
        """
        Create payment details value object from processor result and command.
        
        Args:
            payment_result: Result from the payment processor
            command: The payment command
            
        Returns:
            Payment details value object to associate with the invoice
        """
        return PaymentDetails(
            payment_method=command.payment_details.payment_method,
            transaction_id=payment_result.transaction_id,
            amount=command.payment_details.amount,
            payment_date=datetime.now(),
            payment_info=command.payment_details.payment_info or {},
            payment_reference=payment_result.payment_reference
        ) 