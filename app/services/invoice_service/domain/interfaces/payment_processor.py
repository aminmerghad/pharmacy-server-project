from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from app.services.invoice_service.domain.value_objects.money import Money
from app.services.invoice_service.domain.value_objects.payment_details import PaymentDetails
from app.services.invoice_service.domain.enums.payment_method import PaymentMethod

class PaymentProcessor(ABC):
    """Interface for processing payments."""
    
    @abstractmethod
    def process_payment(
        self, 
        invoice_id: str, 
        amount: Money, 
        payment_method: PaymentMethod, 
        payment_info: Dict[str, Any]
    ) -> PaymentDetails:
        """
        Process a payment for an invoice.
        
        Args:
            invoice_id: The ID of the invoice to pay
            amount: The amount to pay
            payment_method: The method of payment
            payment_info: Additional payment information (card details, etc.)
            
        Returns:
            PaymentDetails with transaction information
            
        Raises:
            PaymentProcessingException: If payment processing fails
        """
        pass
    
    @abstractmethod
    def verify_payment(self, transaction_id: str) -> bool:
        """
        Verify that a payment was successful.
        
        Args:
            transaction_id: The ID of the transaction to verify
            
        Returns:
            True if payment is verified, False otherwise
        """
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id: str, amount: Optional[Money] = None) -> bool:
        """
        Refund a payment.
        
        Args:
            transaction_id: The ID of the transaction to refund
            amount: The amount to refund, or None for full refund
            
        Returns:
            True if refund is successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_payment_status(self, transaction_id: str) -> str:
        """
        Get the current status of a payment.
        
        Args:
            transaction_id: The ID of the transaction to check
            
        Returns:
            The status of the payment (e.g., "completed", "pending", "failed")
        """
        pass
    
    def get_payment_url(self, payment_details: PaymentDetails) -> Optional[str]:
        """
        Get the payment URL to redirect the user to complete payment.
        
        Args:
            payment_details: The payment details returned from process_payment
            
        Returns:
            The URL to redirect the user to, or None if not applicable
        """
        # Default implementation relies on payment_reference containing the URL
        return payment_details.payment_reference if payment_details else None 