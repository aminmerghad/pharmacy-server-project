import logging
import requests
import hmac
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.services.invoice_service.domain.interfaces.payment_processor import PaymentProcessor
from app.services.invoice_service.domain.value_objects.money import Money
from app.services.invoice_service.domain.value_objects.payment_details import PaymentDetails
from app.services.invoice_service.domain.enums.payment_method import PaymentMethod
from app.services.invoice_service.domain.exceptions.invoice_exceptions import PaymentProcessingException

logger = logging.getLogger(__name__)

class ChargilyPaymentProcessor(PaymentProcessor):
    """Implementation of PaymentProcessor using Chargily payment gateway."""
    
    def __init__(self, api_key: str, api_base_url: str = "https://pay.chargily.net/test/api/v2", webhook_secret: Optional[str] = None):
        """
        Initialize the Chargily payment processor.
        
        Args:
            api_key: Chargily API key
            api_base_url: Base URL for Chargily API (test or production)
            webhook_secret: Secret for verifying webhook signatures (if used)
        """
        # Use provided values or fallback to environment/defaults
        self.api_key = api_key or "test_sk_x1AnPnf603gYvLlUikKYeCQ7TZ6kRn5d8nZUBnSY"
        self.api_base_url = api_base_url or "https://pay.chargily.net/test/api/v2"
        self.webhook_secret = webhook_secret
        self.checkouts_url = f"{self.api_base_url}/checkouts"
        
        logger.info(f"Initialized Chargily payment processor with API URL: {self.api_base_url}")
        if not self.api_key:
            logger.warning("No API key provided for Chargily payment processor")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_customer(self, user_id: str, name: str = None, email: str = None, phone: str = None, address: Dict[str, str] = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a customer in Chargily.
        
        Args:
            user_id: User ID for tracking
            name: Customer name
            email: Customer email
            phone: Customer phone number
            address: Dictionary with country, state, and address fields
            metadata: Additional data to associate with the customer
            
        Returns:
            Dictionary with customer data including customer_id if successful
            
        Raises:
            PaymentProcessingException: If customer creation fails
        """
        try:
            logger.info(f"Creating customer in Chargily for user {user_id}")
            
            # Prepare customer data
            customer_data = {
                "name": name or f"User-{user_id}",
                "metadata": metadata or {}
            }
            
            # Add optional fields if provided
            if email:
                customer_data["email"] = email
                
            if phone:
                customer_data["phone"] = phone
                
            if address:
                customer_data["address"] = {
                    "country": address.get("country", "DZ"),
                    "state": address.get("state", ""),
                    "address": address.get("address", "")
                }
            
            # Include user_id in metadata for tracking
            if "metadata" not in customer_data:
                customer_data["metadata"] = {}
                
            customer_data["metadata"]["user_id"] = user_id
            
            logger.debug(f"Sending customer data to Chargily: {customer_data}")
            
            # Make API call to create customer
            response = requests.post(
                f"{self.api_base_url}/customers",
                json=customer_data,
                headers=self._get_headers()
            )
            
            # Check for errors
            if response.status_code not in (200, 201):
                error_msg = f"Failed to create customer: HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = f"Chargily error: {error_data.get('message', error_msg)}"
                except:
                    pass
                    
                logger.error(error_msg)
                raise PaymentProcessingException(user_id, error_msg)
                
            # Parse response
            customer_resp = response.json()
            customer_id = customer_resp.get("id")
            
            if not customer_id:
                error_msg = "Customer ID missing from Chargily response"
                logger.error(error_msg)
                raise PaymentProcessingException(user_id, error_msg)
                
            logger.info(f"Customer created in Chargily with ID: {customer_id}")
            return {
                "customer_id": customer_id,
                "customer_data": customer_resp
            }
            
        except requests.RequestException as e:
            error_msg = f"Error creating customer: {str(e)}"
            logger.error(error_msg)
            raise PaymentProcessingException(user_id, error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error creating customer: {str(e)}"
            logger.error(error_msg)
            raise PaymentProcessingException(user_id, error_msg)
    
    def process_payment(
        self, 
        invoice_id: str, 
        amount: Money, 
        payment_method: PaymentMethod, 
        payment_info: Dict[str, Any]
    ) -> PaymentDetails:
        """
        Process a payment using Chargily.
        
        For Chargily, this creates a checkout session and returns payment details
        with the checkout URL. The actual payment processing happens when the user
        completes the payment on Chargily's platform.
        
        Args:
            invoice_id: The ID of the invoice to pay
            amount: The amount to pay
            payment_method: The method of payment
            payment_info: Additional payment information including:
                - success_url: URL to redirect after successful payment
                - failure_url: URL to redirect after failed payment
                - webhook_endpoint: URL for Chargily to send payment notifications
                - customer_id: Optional customer ID in Chargily
                - locale: Optional locale (en, fr, ar)
                - description: Optional payment description
                - items: Optional array of items with price and quantity
                - metadata: Optional metadata to include with the payment
                - user_data: Optional user data for creating a customer (name, email, phone, address)
        
        Returns:
            PaymentDetails with transaction information including checkout URL
            
        Raises:
            PaymentProcessingException: If payment processing fails
        """
        try:
            logger.info(f"Processing payment for invoice {invoice_id} with Chargily")
            
            # Extract amount and currency
            if hasattr(amount, 'amount'):
                amount_value = int(float(amount.amount))
                currency = amount.currency.lower()
            else:
                amount_value = int(float(amount))
                currency = payment_info.get('currency', 'dzd').lower()
            
            # Validate required fields
            success_url = payment_info.get('success_url')
            failure_url = payment_info.get('failure_url')
            
            if not success_url:
                raise PaymentProcessingException(invoice_id, "success_url is required")
            
            if not failure_url:
                raise PaymentProcessingException(invoice_id, "failure_url is required")
                
            # Map payment method to Chargily format
            chargily_payment_method = "edahabia"  # Default
            if payment_method == PaymentMethod.CREDIT_CARD or payment_method == "cib":
                chargily_payment_method = "cib"
            elif payment_method == PaymentMethod.DEBIT_CARD or payment_method == "edahabia":
                chargily_payment_method = "edahabia"
            
            # Step 1: Create or get customer ID
            customer_id = payment_info.get("customer_id")
            if not customer_id and payment_info.get("user_data"):
                user_data = payment_info.get("user_data", {})
                user_id = user_data.get("user_id") or payment_info.get("user_id", "unknown")
                
                # Create customer in Chargily
                customer_result = self.create_customer(
                    user_id=user_id,
                    name=user_data.get("name"),
                    email=user_data.get("email"),
                    phone=user_data.get("phone"),
                    address=user_data.get("address"),
                    metadata=user_data.get("metadata")
                )
                
                customer_id = customer_result["customer_id"]
                logger.info(f"Created customer with ID {customer_id} for invoice {invoice_id}")
                
            # Build request payload
            payload = {
                "amount": amount_value,
                "currency": currency,
                "payment_method": chargily_payment_method,
                "success_url": success_url,
                "failure_url": failure_url,
                "description": payment_info.get("description", f"Payment for invoice {invoice_id}"),
                "locale": payment_info.get("locale", "en"),
                "metadata": {
                    "invoice_id": invoice_id
                }
            }
            
            # Add customer_id if available
            if customer_id:
                payload["customer_id"] = customer_id
                
            # Add webhook endpoint if provided
            if webhook_endpoint := payment_info.get("webhook_endpoint"):
                payload["webhook_endpoint"] = webhook_endpoint
                
            # Add items if provided
            items = payment_info.get("items")
            if items:
                payload["items"] = items
                
            logger.debug(f"Sending Chargily payment request: {payload}")
            
            # Send request to Chargily
            response = requests.post(
                self.checkouts_url, 
                json=payload, 
                headers=self._get_headers()
            )
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = f"Chargily API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = f"Chargily error: {error_data.get('message', error_msg)}"
                except:
                    pass
                logger.error(error_msg)
                raise PaymentProcessingException(invoice_id, error_msg)
                
            # Parse response
            checkout_data = response.json()
            
            transaction_id = checkout_data.get("id")
            payment_reference = checkout_data.get("checkout_url")
            
            if not payment_reference:
                logger.error(f"No checkout URL returned from Chargily for invoice {invoice_id}")
                raise PaymentProcessingException(invoice_id, "No checkout URL returned from Chargily")
                
            logger.info(f"Created Chargily checkout for invoice {invoice_id}: {transaction_id}, URL: {payment_reference}")
            
            # Return payment details (not completed yet, user needs to complete the checkout)
            return PaymentDetails(
                payment_method=payment_method,
                amount=float(amount_value) / 100 if amount_value > 100 else float(amount_value),
                transaction_id=transaction_id,
                payment_reference=payment_reference,
                payment_info={
                    "checkout_id": transaction_id,
                    "payment_url": payment_reference,
                    "status": checkout_data.get("status", "pending")
                }
            )
            
        except requests.RequestException as e:
            error_msg = f"Chargily payment processing failed: {str(e)}"
            if hasattr(e, 'response') and e.response:
                try:
                    error_data = e.response.json()
                    error_msg = f"Chargily error: {error_data.get('message', str(e))}"
                except:
                    pass
            logger.error(error_msg)
            raise PaymentProcessingException(invoice_id, error_msg)
            
        except Exception as e:
            error_msg = f"Error processing payment: {str(e)}"
            logger.error(error_msg)
            raise PaymentProcessingException(invoice_id, error_msg)
    
    def verify_payment(self, transaction_id: str) -> bool:
        """
        Verify that a payment was successful.
        
        Args:
            transaction_id: The ID of the Chargily checkout to verify
            
        Returns:
            True if payment is verified, False otherwise
        """
        try:
            # Get checkout details from Chargily
            response = requests.get(
                f"{self.checkouts_url}/{transaction_id}",
                headers=self._get_headers()
            )
            
            response.raise_for_status()
            checkout_data = response.json()
            
            # Check if payment is completed
            return checkout_data.get("status") == "paid"
            
        except Exception as e:
            logger.error(f"Error verifying Chargily payment {transaction_id}: {str(e)}")
            return False
    
    def refund_payment(self, transaction_id: str, amount: Optional[Money] = None) -> bool:
        """
        Refund a payment.
        
        Note: This implementation assumes Chargily has a refund API endpoint.
        The actual endpoint and parameters may need to be adjusted based on
        Chargily's actual API documentation.
        
        Args:
            transaction_id: The ID of the transaction to refund
            amount: The amount to refund, or None for full refund
            
        Returns:
            True if refund is successful, False otherwise
        """
        try:
            # Build refund payload
            payload = {"checkout_id": transaction_id}
            
            if amount:
                payload["amount"] = int(float(amount.amount) * 100)  # Convert to smallest currency unit
            
            # Send refund request to Chargily
            # Note: This endpoint may need to be adjusted based on actual Chargily API
            response = requests.post(
                f"{self.api_base_url}/refunds",
                json=payload,
                headers=self._get_headers()
            )
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Error refunding Chargily payment {transaction_id}: {str(e)}")
            return False
    
    def get_payment_status(self, transaction_id: str) -> str:
        """
        Get the current status of a payment.
        
        Args:
            transaction_id: The ID of the Chargily checkout to check
            
        Returns:
            The status of the payment (e.g., "pending", "paid", "failed")
        """
        try:
            # Get checkout details from Chargily
            response = requests.get(
                f"{self.checkouts_url}/{transaction_id}",
                headers=self._get_headers()
            )
            
            response.raise_for_status()
            checkout_data = response.json()
            
            # Return the status
            return checkout_data.get("status", "unknown")
            
        except Exception as e:
            logger.error(f"Error getting Chargily payment status for {transaction_id}: {str(e)}")
            return "unknown"
    
    def handle_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Handle a webhook notification from Chargily.
        
        Args:
            payload: The webhook payload
            headers: The webhook headers, may include signature
            
        Returns:
            Processed webhook data with standardized information
            
        Raises:
            ValueError: If webhook validation fails
        """
        # Verify webhook signature if webhook_secret is configured
        if self.webhook_secret:
            # Get the signature from the headers
            signature = headers.get("Signature")
            if not signature:
                logger.warning("Missing Signature header in Chargily webhook")
                raise ValueError("Missing Signature header")
                
            if not self._verify_webhook_signature(payload, signature):
                logger.warning("Invalid webhook signature from Chargily")
                raise ValueError("Invalid webhook signature")
        
        # Extract relevant information from the webhook
        checkout_id = payload.get("id")
        status = payload.get("status")
        metadata = payload.get("metadata", {})
        invoice_id = metadata.get("invoice_id")
        
        # Parse timestamps
        created_timestamp = payload.get("created_at")
        created_at = datetime.fromtimestamp(created_timestamp) if created_timestamp else None
        
        # Return standardized webhook data
        return {
            "transaction_id": checkout_id,
            "status": status,
            "invoice_id": invoice_id,
            "amount": payload.get("amount", 0) / 100,  # Convert from smallest unit to decimal
            "currency": payload.get("currency", "").upper(),
            "created_at": created_at,
            "metadata": metadata,
            "payment_method": payload.get("payment_method", "unknown"),
            "raw_payload": payload
        }
    
    def _verify_webhook_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """
        Verify the webhook signature from Chargily using HMAC-SHA256.
        
        Args:
            payload: The webhook payload
            signature: The signature from the webhook headers
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.webhook_secret:
            logger.warning("Cannot verify webhook signature: webhook_secret not configured")
            return False
        
        try:
            # Convert payload to a JSON string
            payload_string = json.dumps(payload, separators=(',', ':'))
            
            # Compute HMAC-SHA256 signature
            computed_signature = hmac.new(
                key=self.webhook_secret.encode('utf-8'),
                msg=payload_string.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # Compare computed signature with provided signature
            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(computed_signature, signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False
            
    def get_payment_url(self, payment_details: PaymentDetails) -> Optional[str]:
        """
        Get the payment URL to redirect the user to complete payment.
        
        For Chargily, the payment_reference field contains the checkout URL.
        
        Args:
            payment_details: The payment details returned from process_payment
            
        Returns:
            The URL to redirect the user to, or None if not available
        """
        if not payment_details or not payment_details.payment_reference:
            return None
            
        # For Chargily, the payment_reference contains the checkout URL
        checkout_url = payment_details.payment_reference
        logger.info(f"Returning Chargily checkout URL for redirect: {checkout_url}")
        return checkout_url 