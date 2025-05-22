from typing import Dict, Any, Optional
import logging
from app.services.invoice_service.domain.interfaces.payment_processor import PaymentProcessor
from app.services.invoice_service.domain.value_objects.payment_details import PaymentDetails
from app.services.invoice_service.domain.enums.payment_method import PaymentMethod
from app.services.invoice_service.domain.exceptions.invoice_exceptions import PaymentProcessingException
from app.services.invoice_service.infrastructure.adapters.chargily_payment_processor import ChargilyPaymentProcessor

logger = logging.getLogger(__name__)

class PaymentProcessorAdapter():
    """
    Adapter that selects the appropriate payment processor based on configuration
    or payment method.
    """
    
    def __init__(self):
        """Initialize the payment processor adapter."""
        self.processors = {
            'chargily': ChargilyPaymentProcessor(""),  # Use proper name matching for consistency
            'default': ChargilyPaymentProcessor(""),
        }
        self.default_processor = self.processors['default']
        
        # Map payment methods to processors for auto-selection
        self.payment_method_map = {
            PaymentMethod.DEBIT_CARD: 'chargily',
            PaymentMethod.CREDIT_CARD: 'chargily',
        }
    
    def process_payment(self, invoice_id: str, amount: float, payment_method: str, 
                        payment_info: Dict[str, Any] = None) -> PaymentDetails:
        """
        Process a payment for an invoice using the appropriate processor.
        
        Args:
            invoice_id: The ID of the invoice to process payment for
            amount: The amount to be paid
            payment_method: The payment method to use (string representation)
            payment_info: Additional payment information
            
        Returns:
            Payment details with the transaction information
            
        Raises:
            PaymentProcessingException: If payment processing fails
        """
        payment_info = payment_info or {}
        
        # Get processor from explicit configuration or select based on payment method
        processor_name = payment_info.get('processor')
        
        # Convert string payment method to enum if needed
        payment_method_enum = payment_method
        if isinstance(payment_method, str):
            try:
                payment_method_enum = PaymentMethod(payment_method.upper())
            except ValueError:
                logger.warning(f"Unrecognized payment method: {payment_method}, using OTHER")
                payment_method_enum = PaymentMethod.OTHER
        
        # If no processor explicitly specified, try to select based on payment method
        if not processor_name and isinstance(payment_method_enum, PaymentMethod):
            processor_name = self.payment_method_map.get(payment_method_enum)
        
        # Fall back to default if no processor determined
        if not processor_name or processor_name not in self.processors:
            processor_name = 'default'
            
        processor = self.processors[processor_name]
        
        logger.info(f"Processing payment for invoice {invoice_id} using {processor_name} processor")
        
        try:
            return processor.process_payment(invoice_id, amount, payment_method_enum, payment_info)
        except Exception as e:
            error_message = f"Payment processing failed with {processor_name} processor: {str(e)}"
            logger.error(error_message)
            raise PaymentProcessingException(invoice_id, error_message)
    
    def verify_payment(self, transaction_id: str) -> bool:
        """
        Verify a payment transaction across all processors.
        
        Args:
            transaction_id: The ID of the transaction to verify
            
        Returns:
            True if payment is verified by any processor, False otherwise
        """
        if not transaction_id:
            logger.warning("Cannot verify payment: No transaction ID provided")
            return False
            
        for name, processor in self.processors.items():
            try:
                if processor.verify_payment(transaction_id):
                    logger.info(f"Payment {transaction_id} verified by {name} processor")
                    return True
            except Exception as e:
                logger.warning(f"Error verifying payment {transaction_id} with {name} processor: {str(e)}")
        
        logger.warning(f"Payment {transaction_id} could not be verified by any processor")
        return False
    
    def get_payment_url(self, payment_details: PaymentDetails) -> Optional[str]:
        """
        Get a payment URL if one is available for the given payment details.
        
        Args:
            payment_details: Payment details containing transaction information
            
        Returns:
            URL string if available, None otherwise
        """
        if not payment_details or not payment_details.transaction_id:
            return None
            
        # Try to determine which processor created this transaction
        processor_name = self._identify_processor_from_payment_details(payment_details)
        
        # If we can identify the processor, use it directly
        if processor_name and processor_name in self.processors:
            try:
                return self.processors[processor_name].get_payment_url(payment_details)
            except Exception as e:
                logger.debug(f"Error getting payment URL from {processor_name} processor: {str(e)}")
        
        # Try all processors as fallback
        for name, processor in self.processors.items():
            if name == processor_name:
                continue  # Skip if we already tried this one
                
            try:
                url = processor.get_payment_url(payment_details)
                if url:
                    return url
            except Exception as e:
                logger.debug(f"Error getting payment URL from {name} processor: {str(e)}")
        
        return None
        
    def handle_webhook(self, payload: Dict[str, Any], headers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a webhook from a payment processor.
        
        Args:
            payload: The webhook payload
            headers: The webhook headers
            
        Returns:
            Standardized webhook data
            
        Raises:
            ValueError: If no processor can handle the webhook
        """
        # Try to determine which processor the webhook is from based on headers
        processor_name = self._identify_processor_from_webhook(headers, payload)
        
        if processor_name and processor_name in self.processors:
            try:
                return self.processors[processor_name].handle_webhook(payload, headers)
            except Exception as e:
                logger.error(f"Error handling webhook with {processor_name} processor: {str(e)}")
                raise ValueError(f"Error handling webhook: {str(e)}")
        
        # If we can't determine the processor, try each one
        for name, processor in self.processors.items():
            if name == processor_name:
                continue  # Skip if we already tried this one
                
            try:
                result = processor.handle_webhook(payload, headers)
                if result:
                    logger.info(f"Webhook handled by {name} processor")
                    return result
            except Exception as e:
                logger.debug(f"Processor {name} failed to handle webhook: {str(e)}")
                
        raise ValueError("No processor could handle the webhook")
    
    def _identify_processor_from_payment_details(self, payment_details: PaymentDetails) -> Optional[str]:
        """
        Identify which processor was used based on payment details.
        
        Args:
            payment_details: The payment details to analyze
            
        Returns:
            Processor name or None if cannot determine
        """
        if not payment_details:
            return None
            
        # Check payment reference for processor hints
        if payment_details.payment_reference:
            reference = payment_details.payment_reference.lower()
            
            # Look for processor-specific URL patterns
            if "chargily" in reference or "pay.chargily.net" in reference:
                return "chargily"
        
        # Check payment info for processor hint
        if payment_details.payment_info and 'processor' in payment_details.payment_info:
            processor = payment_details.payment_info.get('processor')
            if processor in self.processors:
                return processor
        
        return None
    
    def _identify_processor_from_webhook(self, headers: Dict[str, Any], payload: Dict[str, Any]) -> Optional[str]:
        """
        Identify which processor a webhook is from based on headers and payload.
        
        Args:
            headers: The webhook headers
            payload: The webhook payload
            
        Returns:
            Processor name or None if cannot determine
        """
        # Check for Chargily-specific headers
        if 'Signature' in headers:
            return 'chargily'
            
        # Check payload for processor-specific fields
        if payload.get('processor') in self.processors:
            return payload.get('processor')
            
        # Check for processor identification in the event type
        event_type = payload.get('event') or payload.get('type') or payload.get('event_type')
        if event_type:
            event_type = str(event_type).lower()
            if 'chargily' in event_type:
                return 'chargily'
        
        return None 