

from jsonschema import ValidationError
from marshmallow import Schema, fields, validate, validates_schema


class PaymentProcessSchema(Schema):
    """Schema for processing payments."""
    
    payment_method = fields.Str(required=True, 
                                validate=validate.OneOf(["credit_card", "debit_card", "cash", "bank_transfer", "edahabia", "cib"]),
                                description="Payment method")
    amount = fields.Float(required=True, description="Payment amount")
    currency = fields.Str(required=False, default="dzd", description="Currency code (default: DZD)")
    
    # Required for Chargily
    success_url = fields.Str(required=True, description="URL to redirect after successful payment")
    failure_url = fields.Str(required=True, description="URL to redirect after failed payment")
    
    # Optional parameters
    webhook_endpoint = fields.Str(required=False, description="Webhook URL for payment notifications")
    locale = fields.Str(required=False, default="en", description="Locale for payment page")
    description = fields.Str(required=False, description="Payment description")
    customer_id = fields.Str(required=False, description="Existing customer ID in payment gateway")
    
    # Auto-create customer if not provided
    user_data = fields.Dict(required=False, description="User data for creating a customer in payment gateway")
    
    # Additional payment information
    metadata = fields.Dict(required=False, description="Additional metadata to include with payment")
    
    # Validation to ensure required fields are present
    @validates_schema
    def validate_required_fields(self, data, **kwargs):
        """Validate that required fields are present based on payment method."""
        payment_method = data.get('payment_method')
        
        if payment_method in ['edahabia', 'cib']:
            # For Chargily payments, success_url and failure_url are required
            if not data.get('success_url'):
                raise ValidationError("success_url is required for Chargily payments")
            if not data.get('failure_url'):
                raise ValidationError("failure_url is required for Chargily payments")
                
            # Validate user_data structure if provided
            user_data = data.get('user_data')
            if user_data and not isinstance(user_data, dict):
                raise ValidationError("user_data must be a dictionary")
                
            if user_data and 'address' in user_data and not isinstance(user_data['address'], dict):
                raise ValidationError("user_data.address must be a dictionary")

class PaymentStatusSchema(Schema):
    """Schema for payment status responses."""
    
    status = fields.Str(required=True, description="Status of the payment")
    transaction_id = fields.Str(required=False, description="Transaction ID")
    payment_url = fields.Str(required=False, description="Payment URL for redirect")
    payment_details = fields.Dict(required=False, description="Additional payment details")
    message = fields.Str(required=False, description="Status message") 