from flask import request, jsonify
from flask_smorest import Blueprint, abort
from datetime import datetime
import logging
from app.extensions import container
from marshmallow import Schema, fields, validate, ValidationError
from typing import Dict, List, Optional, Any, Union
from http import HTTPStatus
from app.api.base_routes import BaseRoute
from flask.views import MethodView
import json
from app.services.invoice_service.application.queries.get_invoice_query import GetInvoiceQuery

# Create Blueprint
invoice_bp = Blueprint('invoice', __name__, url_prefix='/invoice', description='Invoice API')

logger = logging.getLogger(__name__)

# Schema definitions
class InvoiceItemSchema(Schema):
    product_id = fields.String(required=True)
    description = fields.String(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    unit_price = fields.Float(required=True, validate=validate.Range(min=0.01))
    item_id = fields.String(dump_only=True)
    subtotal = fields.Float(dump_only=True)

class PaymentDetailsSchema(Schema):
    payment_method = fields.String(required=True)
    transaction_id = fields.String(dump_only=True)
    payment_date = fields.DateTime(dump_only=True)
    payer_name = fields.String()
    payment_reference = fields.String()

class InvoiceSchema(Schema):
    invoice_id = fields.String(dump_only=True)
    order_id = fields.String(required=True)
    user_id = fields.String(required=True)
    status = fields.String(dump_only=True)
    items = fields.List(fields.Nested(InvoiceItemSchema), required=True)
    total_amount = fields.Float(dump_only=True)
    subtotal = fields.Float(dump_only=True)
    tax_amount = fields.Float()
    discount_amount = fields.Float()
    due_date = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    paid_at = fields.DateTime(dump_only=True)
    payment_details = fields.Nested(PaymentDetailsSchema, dump_only=True)
    notes = fields.String()

class InvoiceUpdateSchema(Schema):
    due_date = fields.DateTime()
    tax_amount = fields.Float(validate=validate.Range(min=0))
    discount_amount = fields.Float(validate=validate.Range(min=0))
    notes = fields.String()

class PaymentProcessSchema(Schema):
    payment_method = fields.String(required=True, validate=validate.OneOf(
        ["CREDIT_CARD", "DEBIT_CARD", "BANK_TRANSFER", "CASH", "INSURANCE", "OTHER", "edahabia", "cib"]
    ))
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    currency = fields.String(load_default="DZD")
    payment_info = fields.Dict(load_default=dict)
    success_url = fields.String(required=True)
    failure_url = fields.String(required=True)
    webhook_endpoint = fields.String(load_default=None)
    description = fields.String(load_default=None)
    locale = fields.String(load_default="en", validate=validate.OneOf(["ar", "en", "fr"]))
    items = fields.List(fields.Dict, load_default=None)

class InvoiceQuerySchema(Schema):
    status = fields.String()
    user_id = fields.String()
    from_date = fields.DateTime()
    to_date = fields.DateTime()
    order_id = fields.String()
    page = fields.Integer(load_default=1)
    per_page = fields.Integer(load_default=20, validate=validate.Range(min=1, max=100))

class ErrorResponseSchema(Schema):
    status = fields.String(dump_default="error")
    message = fields.String(required=True)
    error_details = fields.Dict()

class SuccessResponseSchema(Schema):
    status = fields.String(dump_default="success")
    message = fields.String()
    data = fields.Dict()

class PaymentResponseSchema(Schema):
    status = fields.String(dump_default="success")
    message = fields.String()
    invoice_id = fields.String()
    payment_url = fields.String()
    transaction_id = fields.String()
    redirect_user = fields.Boolean()
    invoice = fields.Nested(InvoiceSchema)

class PaginatedResponseSchema(Schema):
    """Schema for paginated responses"""
    items = fields.List(fields.Nested(InvoiceSchema))
    page = fields.Int()
    per_page = fields.Int()
    total = fields.Int()
    pages = fields.Int()

# Helper functions
def get_invoice_service():
    """Get the invoice service from container"""
    try:
        # Try different methods of accessing the service based on container implementation
        if hasattr(container, 'invoice_service') and callable(getattr(container, 'invoice_service', None)):
            return container.invoice_service()
        elif hasattr(container, 'get'):
            return container.get('invoice_service')
        else:
            raise ValueError("Unable to access invoice service from container")
    except Exception as e:
        logger.error(f"Failed to get invoice service: {str(e)}")
        abort(500, message="Service unavailable")

# Route definitions with class-based views
@invoice_bp.route('/invoices')
class Invoices(BaseRoute):
    @invoice_bp.arguments(InvoiceSchema)
    
    # @invoice_bp.response(400, ErrorResponseSchema)
    # @invoice_bp.response(500, ErrorResponseSchema)
    # @invoice_bp.response(201, InvoiceSchema)
    def post(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new invoice"""
        try:
            invoice_service = get_invoice_service()
            
            result = invoice_service.create_invoice(invoice_data)
            return self._success_response(
                data=result,
                message="Invoice created successfully",
                status_code=HTTPStatus.CREATED
            )
        except ValueError as e:
                logger.warning(f"Invalid invoice data: {str(e)}")
                return self._error_response(
                    message=str(e),
                    status_code=HTTPStatus.BAD_REQUEST
                )
        except Exception as e:
                logger.error(f"Error creating invoice: {str(e)}")
                return self._error_response(
                    message="Failed to create invoice",
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    errors=str(e)
                )
    
#     @invoice_bp.arguments(InvoiceQuerySchema, location="query")
#     @invoice_bp.response(200, PaginatedResponseSchema)
#     @invoice_bp.alt_response(400, ErrorResponseSchema)
#     @invoice_bp.alt_response(500, ErrorResponseSchema)
#     def get(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
#         """List invoices with optional filtering and pagination"""
#         try:
#             invoice_service = get_invoice_service()
            
#             # Extract pagination parameters
#             page = query_params.pop('page', 1)
#             per_page = query_params.pop('per_page', 20)
            
#             # Handle different query parameters
#             if 'user_id' in query_params:
#                 invoices = invoice_service.get_user_invoices(query_params['user_id'])
#             elif 'status' in query_params:
#                 invoices = invoice_service.get_invoices_by_status(query_params['status'])
#             elif 'order_id' in query_params:
#                 invoice = invoice_service.get_invoice_by_order(query_params['order_id'])
#                 invoices = [invoice] if invoice else []
#             else:
#                 invoices = invoice_service.get_all_invoices()
            
#             # Apply date range filtering if specified
#             if 'from_date' in query_params or 'to_date' in query_params:
#                 from_date = query_params.get('from_date')
#                 to_date = query_params.get('to_date')
#                 invoices = [
#                     inv for inv in invoices 
#                     if (not from_date or inv.created_at >= from_date) and
#                        (not to_date or inv.created_at <= to_date)
#                 ]
            
#             # Manual pagination
#             total = len(invoices)
#             start_idx = (page - 1) * per_page
#             end_idx = min(start_idx + per_page, total)
            
#             return self._success_response(
#                 data={
#                     "items": invoices[start_idx:end_idx],
#                     "total": total,
#                     "page": page,
#                     "per_page": per_page,
#                     "pages": (total + per_page - 1) // per_page
#                 },
#                 message="Invoices retrieved successfully",
#                 status_code=HTTPStatus.OK
#             )
#         except ValueError as e:
#             return self._error_response(
#                 message=str(e),
#                 status_code=HTTPStatus.BAD_REQUEST
#             )
#         except Exception as e:
#             logger.error(f"Error listing invoices: {str(e)}")
#             return self._error_response(
#                 message="Failed to list invoices",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
#                 errors=str(e)
#             )


# @invoice_bp.route('/invoices/<invoice_id>')
# class InvoiceDetail(BaseRoute):
#     @invoice_bp.response(200, InvoiceSchema)
#     @invoice_bp.alt_response(404, ErrorResponseSchema)
#     @invoice_bp.alt_response(500, ErrorResponseSchema)
#     def get(self, invoice_id: str) -> Dict[str, Any]:
#         """Get invoice details by ID"""
#         try:
#             invoice_service = get_invoice_service()
#             invoice = invoice_service.get_invoice(invoice_id)
#             return self._success_response(
#                 data=invoice,
#                 message="Invoice retrieved successfully",
#                 status_code=HTTPStatus.OK
#             )
#         except ValueError as e:
#             return self._error_response(
#                 message=str(e),
#                 status_code=HTTPStatus.NOT_FOUND
#             )
#         except Exception as e:
#             logger.error(f"Error getting invoice {invoice_id}: {str(e)}")
#             return self._error_response(
#                 message=f"Failed to retrieve invoice",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
#                 errors=str(e)
#             )
    
#     @invoice_bp.arguments(InvoiceUpdateSchema)
#     @invoice_bp.response(200, InvoiceSchema)
#     @invoice_bp.alt_response(400, ErrorResponseSchema)
#     @invoice_bp.alt_response(404, ErrorResponseSchema)
#     @invoice_bp.alt_response(500, ErrorResponseSchema)
#     def put(self, invoice_data: Dict[str, Any], invoice_id: str) -> Dict[str, Any]:
#         """Update an existing invoice"""
#         try:
#             invoice_service = get_invoice_service()
#             invoice = invoice_service.update_invoice(invoice_id, invoice_data)
#             return self._success_response(
#                 data=invoice,
#                 message="Invoice updated successfully",
#                 status_code=HTTPStatus.OK
#             )
#         except ValueError as e:
#             return self._error_response(
#                 message=str(e),
#                 status_code=HTTPStatus.BAD_REQUEST
#             )
#         except Exception as e:
#             logger.error(f"Error updating invoice {invoice_id}: {str(e)}")
#             return self._error_response(
#                 message=f"Failed to update invoice",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
#                 errors=str(e)
#             )
    
#     @invoice_bp.response(200, InvoiceSchema)
#     @invoice_bp.alt_response(404, ErrorResponseSchema)
#     @invoice_bp.alt_response(500, ErrorResponseSchema)
#     def delete(self, invoice_id: str) -> Dict[str, Any]:
#         """Cancel an invoice"""
#         try:
#             invoice_service = get_invoice_service()
#             reason = request.args.get('reason')
#             invoice = invoice_service.cancel_invoice(invoice_id, reason)
#             return self._success_response(
#                 data=invoice,
#                 message="Invoice cancelled successfully",
#                 status_code=HTTPStatus.OK
#             )
#         except ValueError as e:
#             return self._error_response(
#                 message=str(e),
#                 status_code=HTTPStatus.NOT_FOUND
#             )
#         except Exception as e:
#             logger.error(f"Error cancelling invoice {invoice_id}: {str(e)}")
#             return self._error_response(
#                 message=f"Failed to cancel invoice",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
#                 errors=str(e)
#             )


@invoice_bp.route('/invoices/<invoice_id>/pay')
class InvoicePayment(BaseRoute):
    @invoice_bp.arguments(PaymentProcessSchema)
    # @invoice_bp.response(200, PaymentResponseSchema)
    # @invoice_bp.response(400, ErrorResponseSchema)
    # @invoice_bp.response(404, ErrorResponseSchema)
    # @invoice_bp.response(500, ErrorResponseSchema)
    def post(self, payment_data: Dict[str, Any], invoice_id: str) -> Dict[str, Any]:
        """Process payment for an invoice using Chargily payment gateway"""
        try:
            # Get invoice service
            invoice_service = get_invoice_service()
            
            # Validate request parameters
            payment_method = payment_data.get('payment_method')
            amount = payment_data.get('amount')
            
            if not payment_method or not amount:
                return self._error_response(
                    message="Payment method and amount are required",
                    status_code=HTTPStatus.BAD_REQUEST
                )
            
            # Create success and failure URLs if not provided
            base_url = request.host_url.rstrip('/')
            success_url = payment_data.get('success_url', f"{base_url}/invoice/payment/success")
            failure_url = payment_data.get('failure_url', f"{base_url}/invoice/payment/failure")
            
            # Create webhook URL if not provided
            webhook_endpoint = payment_data.get('webhook_endpoint', f"{base_url}/webhooks/chargily")
            
            # Prepare payment processing command
            from app.services.invoice_service.application.commands.process_payment_command import ProcessPaymentCommand
            
            # Create payment_info dictionary with all the parameters needed for Chargily
            payment_info = {
                'success_url': success_url,
                'failure_url': failure_url,
                'webhook_endpoint': webhook_endpoint,
                'description': payment_data.get('description', f"Payment for invoice {invoice_id}"),
                'locale': payment_data.get('locale', 'en'),
                'currency': payment_data.get('currency', 'dzd'),
            }
            
            # Add items if provided
            if items := payment_data.get('items'):
                payment_info['items'] = items
                
            # Create the payment processing command
            command = ProcessPaymentCommand(
                id=invoice_id,
                payment_method=payment_method,
                amount=amount,
                payment_info=payment_info
            )
            
            # Process the payment
            result = invoice_service.process_payment(command)
            
            # Extract payment URL from result
            payment_url = None
            if result.payment_details and result.payment_details.payment_reference:
                payment_url = result.payment_details.payment_reference
            
            # Return response with payment URL for client to redirect user
            return self._success_response(
                data={
                    "status": "success",
                    "message": "Payment initiated successfully",
                    "invoice_id": result.id,
                    "payment_url": payment_url,
                    "transaction_id": result.payment_details.transaction_id if result.payment_details else None,
                    "redirect_user": payment_url is not None,
                    "invoice": result
                },
                message="Payment initiated successfully",
                status_code=HTTPStatus.OK
            )
        except ValueError as e:
            return self._error_response(
                message=str(e),
                status_code=HTTPStatus.BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error processing payment for invoice {invoice_id}: {str(e)}")
            return self._error_response(
                message=f"Failed to process payment: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                errors=str(e)
            )


# @invoice_bp.route('/invoices/<invoice_id>/overdue')
# class InvoiceOverdue(BaseRoute):
#     @invoice_bp.response(200, InvoiceSchema)
#     @invoice_bp.alt_response(404, ErrorResponseSchema)
#     @invoice_bp.alt_response(500, ErrorResponseSchema)
#     def post(self, invoice_id: str) -> Dict[str, Any]:
#         """Mark an invoice as overdue"""
#         try:
#             invoice_service = get_invoice_service()
#             invoice = invoice_service.mark_invoice_as_overdue(invoice_id)
#             return self._success_response(
#                 data=invoice,
#                 message="Invoice marked as overdue",
#                 status_code=HTTPStatus.OK
#             )
#         except ValueError as e:
#             return self._error_response(
#                 message=str(e),
#                 status_code=HTTPStatus.NOT_FOUND
#             )
#         except Exception as e:
#             logger.error(f"Error marking invoice {invoice_id} as overdue: {str(e)}")
#             return self._error_response(
#                 message=f"Failed to mark invoice as overdue",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
#                 errors=str(e)
#             )


# @invoice_bp.route('/order/<order_id>/invoice')
# class OrderInvoice(BaseRoute):
#     @invoice_bp.response(200, InvoiceSchema)
#     @invoice_bp.alt_response(404, ErrorResponseSchema)
#     @invoice_bp.alt_response(500, ErrorResponseSchema)
#     def get(self, order_id: str) -> Dict[str, Any]:
#         """Get invoice by order ID"""
#         try:
#             invoice_service = get_invoice_service()
#             invoice = invoice_service.get_invoice_by_order(order_id)
#             if not invoice:
#                 return self._error_response(
#                     message="No invoice found for this order",
#                     status_code=HTTPStatus.NOT_FOUND
#                 )
#             return self._success_response(
#                 data=invoice,
#                 message="Invoice retrieved successfully",
#                 status_code=HTTPStatus.OK
#             )
#         except Exception as e:
#             logger.error(f"Error getting invoice for order {order_id}: {str(e)}")
#             return self._error_response(
#                 message=f"Failed to get invoice",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
#                 errors=str(e)
#             )
    
#     @invoice_bp.response(201, InvoiceSchema)
#     @invoice_bp.alt_response(400, ErrorResponseSchema)
#     @invoice_bp.alt_response(500, ErrorResponseSchema)
#     def post(self, order_id: str) -> Dict[str, Any]:
#         """Create an invoice from an existing order"""
#         try:
#             due_date_days = request.args.get('due_date_days', 30, type=int)
#             invoice_service = get_invoice_service()
#             invoice = invoice_service.create_invoice_from_order(order_id, due_date_days)
#             return self._success_response(
#                 data=invoice,
#                 message="Invoice created successfully from order",
#                 status_code=HTTPStatus.CREATED
#             )
#         except ValueError as e:
#             return self._error_response(
#                 message=str(e),
#                 status_code=HTTPStatus.BAD_REQUEST
#             )
#         except Exception as e:
#             logger.error(f"Error creating invoice from order {order_id}: {str(e)}")
#             return self._error_response(
#                 message=f"Failed to create invoice",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
#                 errors=str(e)
#             )


# @invoice_bp.route('/user/invoices')
# class UserInvoices(BaseRoute):
#     @invoice_bp.arguments(InvoiceQuerySchema, location="query")
#     @invoice_bp.response(200, PaginatedResponseSchema)
#     @invoice_bp.alt_response(400, ErrorResponseSchema)
#     @invoice_bp.alt_response(500, ErrorResponseSchema)
#     def get(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
#         """Get invoices for the current user with pagination"""
#         try:
#             # In a real application, get the user ID from the authentication system
#             # For this example, we'll use a query parameter
#             user_id = query_params.get('user_id')
#             if not user_id:
#                 return self._error_response(
#                     message="User ID is required",
#                     status_code=HTTPStatus.BAD_REQUEST
#                 )
                
#             invoice_service = get_invoice_service()
#             invoices = invoice_service.get_user_invoices(user_id)
            
#             # Extract pagination parameters
#             page = query_params.get('page', 1)
#             per_page = query_params.get('per_page', 20)
            
#             # Apply date range filtering if specified
#             if 'from_date' in query_params or 'to_date' in query_params:
#                 from_date = query_params.get('from_date')
#                 to_date = query_params.get('to_date')
#                 invoices = [
#                     inv for inv in invoices 
#                     if (not from_date or inv.created_at >= from_date) and
#                        (not to_date or inv.created_at <= to_date)
#                 ]
            
#             # Manual pagination
#             total = len(invoices)
#             start_idx = (page - 1) * per_page
#             end_idx = min(start_idx + per_page, total)
            
#             return self._success_response(
#                 data={
#                     "items": invoices[start_idx:end_idx],
#                     "total": total,
#                     "page": page,
#                     "per_page": per_page,
#                     "pages": (total + per_page - 1) // per_page
#                 },
#                 message="User invoices retrieved successfully",
#                 status_code=HTTPStatus.OK
#             )
#         except Exception as e:
#             logger.error(f"Error getting user invoices: {str(e)}")
#             return self._error_response(
#                 message=f"Failed to get invoices",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
#                 errors=str(e)
#             )


# @invoice_bp.route('/invoices/overdue')
# class OverdueInvoices(BaseRoute):
#     @invoice_bp.arguments(InvoiceQuerySchema, location="query")
#     @invoice_bp.response(200, PaginatedResponseSchema)
#     @invoice_bp.alt_response(500, ErrorResponseSchema)
#     def get(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
#         """Get all overdue invoices with pagination"""
#         try:
#             invoice_service = get_invoice_service()
#             invoices = invoice_service.get_overdue_invoices()
            
#             # Extract pagination parameters
#             page = query_params.get('page', 1)
#             per_page = query_params.get('per_page', 20)
            
#             # Manual pagination
#             total = len(invoices)
#             start_idx = (page - 1) * per_page
#             end_idx = min(start_idx + per_page, total)
            
#             return self._success_response(
#                 data={
#                     "items": invoices[start_idx:end_idx],
#                     "total": total,
#                     "page": page,
#                     "per_page": per_page,
#                     "pages": (total + per_page - 1) // per_page
#                 },
#                 message="Overdue invoices retrieved successfully",
#                 status_code=HTTPStatus.OK
#             )
#         except Exception as e:
#             logger.error(f"Error getting overdue invoices: {str(e)}")
#             return self._error_response(
#                 message=f"Failed to get overdue invoices",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
#                 errors=str(e)
#             ) 

@invoice_bp.route('/invoices/<invoice_id>/pay/chargily')
class ChargilyPaymentExample(BaseRoute):
    def get(self, invoice_id: str) -> Dict[str, Any]:
        """
        Get example Chargily payment parameters for the given invoice.
        This route helps with testing the Chargily payment integration.
        """
        try:
            # Get invoice service and fetch the invoice
            invoice_service = get_invoice_service()
            invoice_query = GetInvoiceQuery(id=invoice_id)
            
            try:
                invoice = invoice_service.get_invoice(invoice_query)
            except Exception as e:
                return self._error_response(
                    message=f"Invoice not found: {invoice_id}",
                    status_code=HTTPStatus.NOT_FOUND
                )
            
            # Get host URL for webhooks and redirects
            base_url = request.host_url.rstrip('/')
            
            # Create example payment parameters
            example_payment = {
                "payment_method": "edahabia",
                "amount": float(invoice.total_amount),
                "currency": "dzd",
                "success_url": f"{base_url}/invoice/payment/success",
                "failure_url": f"{base_url}/invoice/payment/failure",
                "webhook_endpoint": f"{base_url}/webhooks/chargily",
                "description": f"Payment for invoice {invoice_id}",
                "locale": "en"
            }
            
            # Return the example payment data and instructions
            return self._success_response(
                data={
                    "invoice_id": invoice_id,
                    "example_payment": example_payment,
                    "curl_example": f"""
curl --request POST \\
  --url {base_url}/invoice/invoices/{invoice_id}/pay \\
  --header 'Content-Type: application/json' \\
  --data '{json.dumps(example_payment)}'
                    """.strip()
                },
                message="Example Chargily payment parameters",
                status_code=HTTPStatus.OK
            )
        except Exception as e:
            logger.error(f"Error generating payment example: {str(e)}")
            return self._error_response(
                message=f"Failed to generate payment example: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            ) 

@invoice_bp.route('/payment/success')
class PaymentSuccess(BaseRoute):
    def get(self) -> Dict[str, Any]:
        """
        Handle successful payment redirects from Chargily.
        This endpoint is called by Chargily after a successful payment.
        """
        checkout_id = request.args.get('checkout_id')
        invoice_id = request.args.get('invoice_id')
        
        return self._success_response(
            data={
                "checkout_id": checkout_id,
                "invoice_id": invoice_id,
                "status": "success"
            },
            message="Payment completed successfully",
            status_code=HTTPStatus.OK
        )

@invoice_bp.route('/payment/failure')
class PaymentFailure(BaseRoute):
    def get(self) -> Dict[str, Any]:
        """
        Handle failed payment redirects from Chargily.
        This endpoint is called by Chargily after a failed payment.
        """
        checkout_id = request.args.get('checkout_id')
        invoice_id = request.args.get('invoice_id')
        error = request.args.get('error')
        
        return self._error_response(
            message="Payment was not completed",
            errors={
                "checkout_id": checkout_id,
                "invoice_id": invoice_id,
                "error": error
            },
            status_code=HTTPStatus.PAYMENT_REQUIRED
        ) 