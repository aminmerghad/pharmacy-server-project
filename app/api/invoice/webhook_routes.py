from flask import request, jsonify, Blueprint, current_app
import logging
from app.extensions import container
from app.services.invoice_service.domain.value_objects.payment_details import PaymentDetails
from app.services.invoice_service.domain.enums.payment_method import PaymentMethod
from typing import Dict, Any, Optional
import hmac
import hashlib

# Create Blueprint for webhooks
webhook_bp = Blueprint('webhooks', 'webhooks', url_prefix='/webhooks')

logger = logging.getLogger(__name__)

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify webhook signature using HMAC-SHA256.
    
    Args:
        payload: Raw request payload bytes
        signature: Signature header from request
        secret: Webhook secret key
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not payload or not signature or not secret:
        return False
        
    computed_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_signature, signature)

@webhook_bp.route('/chargily', methods=['POST'])
def chargily_webhook() -> tuple[Dict[str, Any], int]:
    """
    Handle webhooks from Chargily payment gateway.
    Updates invoice status when payment is completed.
    
    Chargily verifies webhooks using HMAC-SHA256 signatures:
    1. The raw payload is extracted
    2. HMAC-SHA256 signature is computed using the shared API secret
    3. The computed signature is compared with the value in the Signature header
    
    Returns:
        JSON response and HTTP status code
    """
    # Get the raw payload
    raw_payload = request.get_data()
    
    try:
        # Check if payload exists
        payload = request.json
        if not payload:
            logger.error("Empty webhook payload received")
            return jsonify({"status": "error", "message": "Empty payload"}), 400
        
        # Extract request headers
        headers = dict(request.headers)
        signature = headers.get('Signature')
        
        logger.info(f"Received Chargily webhook: {payload.get('id')}, status: {payload.get('status')}")
        
        # Get services from container
        invoice_service = container.get('invoice_service')
        payment_processor = invoice_service.payment_processor
        
        # Verify signature if configured
        webhook_secret = current_app.config.get('CHARGILY_WEBHOOK_SECRET')
        if webhook_secret and signature:
            if not verify_signature(raw_payload, signature, webhook_secret):
                logger.error("Webhook signature verification failed")
                return jsonify({"status": "error", "message": "Invalid signature"}), 401
        
        # Process the webhook
        try:
            webhook_data = payment_processor.handle_webhook(payload, headers)
        except ValueError as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 401
        
        # Check if this is a payment status update
        if webhook_data.get("status") != "paid":
            logger.info(f"Ignoring non-payment webhook: {webhook_data.get('status')}")
            return jsonify({"status": "success", "message": "Webhook received"}), 200
        
        # Get the invoice ID from metadata
        invoice_id = webhook_data.get("invoice_id")
        if not invoice_id:
            logger.error("Invoice ID not found in webhook metadata")
            return jsonify({"status": "error", "message": "Invoice ID not found"}), 400
        
        transaction_id = webhook_data.get("transaction_id")
        payment_method_str = webhook_data.get("payment_method", "OTHER")
        
        # Map Chargily payment method to our PaymentMethod enum
        payment_method_mapping = {
            "credit_card": PaymentMethod.CREDIT_CARD,
            "debit_card": PaymentMethod.DEBIT_CARD,
            "bank_transfer": PaymentMethod.BANK_TRANSFER,
            "edahabia": PaymentMethod.DEBIT_CARD,  # Map edahabia to debit card
            "cib": PaymentMethod.CREDIT_CARD,      # Map CIB to credit card
        }
        
        payment_method = payment_method_mapping.get(
            payment_method_str.lower(), 
            PaymentMethod.OTHER
        )
        
        # Create payment details
        payment_details = PaymentDetails(
            payment_method=payment_method,
            transaction_id=transaction_id,
            payment_date=webhook_data.get("created_at"),
            payment_reference=f"Chargily: {transaction_id}"
        )
        
        # Process the payment for the invoice
        try:
            invoice = invoice_service.update_payment_status(
                invoice_id=invoice_id,
                payment_details=payment_details
            )
            
            logger.info(f"Successfully processed payment for invoice {invoice_id}, amount: {invoice.total_amount}")
            return jsonify({
                "status": "success", 
                "message": "Payment processed",
                "invoice_id": invoice_id,
                "transaction_id": transaction_id
            }), 200
            
        except Exception as e:
            logger.error(f"Failed to update invoice payment status: {str(e)}")
            return jsonify({"status": "error", "message": f"Payment processing failed: {str(e)}"}), 500
        
    except Exception as e:
        logger.exception(f"Error processing Chargily webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500 