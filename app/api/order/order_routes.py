from http import HTTPStatus
from uuid import UUID
from app.api import order_bp
from app.api.base_routes import BaseRoute
from app.api.order.schemas import CreateOrderSchema, OrderFilterSchema, OrderListResponseSchema, OrderResponseSchema, UpdateOrderStatusSchema
from app.services.order_service.application.commands import CreateOrderCommand, UpdateOrderCommand, CancelOrderCommand
from app.services.order_service.application.dtos.order_dto import CreateOrderItemDTO
from app.services.order_service.application.queries.order_filter_query import OrderFilterQuery
from app.shared.domain.schema.common_errors import ErrorResponseSchema
from app.shared.utils.api_response import APIResponse
from app.extensions import container    
from flask_jwt_extended import jwt_required, get_jwt_identity


@order_bp.route('/orders')
class OrderFilterRoutes(BaseRoute):
    # @required_admin
    @order_bp.doc(summary="Get orders by filter", description="Get filtered orders with pagination")
    @order_bp.arguments(OrderFilterSchema)
    @order_bp.response(HTTPStatus.OK, OrderListResponseSchema, description="List of orders")
    def post(self, data):             
        # Get orders using the service
        result = container.order_service().get_orders(OrderFilterQuery(**data))        
        return self._success_response(
            message='Orders retrieved successfully',
            data=result,
            status_code=HTTPStatus.OK
        )

@order_bp.route('/order')
class OrderRoutes(BaseRoute):
    @order_bp.doc(summary="Create an order", description="Create an order")   
    @order_bp.arguments(CreateOrderSchema)
    @order_bp.response(HTTPStatus.NOT_FOUND, ErrorResponseSchema) #Inventory not found
    @order_bp.response(HTTPStatus.CONFLICT, ErrorResponseSchema) #when there is a stock issues
    @order_bp.response(HTTPStatus.CREATED, OrderResponseSchema)
    @jwt_required()
    def post(self, data):
        # Get the current user ID from the JWT token
        user_id = get_jwt_identity()        
        # Create command with user_id
        command = CreateOrderCommand(
            user_id=UUID(user_id),
            items=[CreateOrderItemDTO(**order) for order in data['items']],
            notes=data.get('notes')
        )
        
        order_data = container.order_service().create_order(command)
        return self._success_response(
            message='Order created successfully',
            data=order_data,
            status_code=HTTPStatus.CREATED
        )
# @order_bp.route('/orders/<uuid:order_id>/details')
# class OrderProductDetailsRoutes(BaseRoute):
#     @order_bp.doc(summary="Get order details with products", description="Get detailed order information including product details")
#     @order_bp.response(HTTPStatus.OK, schema=OrderResponseSchema)
#     @order_bp.response(HTTPStatus.NOT_FOUND, schema=ErrorResponseSchema)
#     def get(self, order_id):
#         """
#         Get complete order details with product information.
#         This is useful for presenting a complete view of an order.
#         """
#         # Get basic order
#         order = container.order_service().get_order(order_id)
        
#         if not order:
#             return self._error_response(
#                 message='Order not found',
#                 status_code=HTTPStatus.NOT_FOUND
#             )
        
#         # Enrich with product details if order items exist
#         if 'items' in order and order['items']:
#             product_service = container.product_service()
            
#             # Get product details for each item
#             for item in order['items']:
#                 if 'product_id' in item:
#                     try:
#                         product = product_service.get_product(UUID(item['product_id']))
#                         if product:
#                             item['product_details'] = product
#                     except Exception as e:
#                         # Just log error but don't fail if product info can't be retrieved
#                         import logging
#                         logging.error(f"Error getting product details: {str(e)}")
        
#         return self._success_response(
#             message='Order details retrieved successfully',
#             data=order,
#             status_code=HTTPStatus.OK
#         )
    
@order_bp.route('/orders/<uuid:order_id>')
class OrderDetailRoutes(BaseRoute):
    @order_bp.doc(summary="Get order by ID", description="Get detailed information about a specific order")
    @order_bp.response(HTTPStatus.OK, OrderResponseSchema)
    @order_bp.response(HTTPStatus.NOT_FOUND, ErrorResponseSchema)
    @jwt_required()
    def get(self, order_id):
        order = container.order_service().get_order(order_id)
        if not order:
            return self._error_response(
                message='Order not found',
                status_code=HTTPStatus.NOT_FOUND
            )
        
        return self._success_response(
            message='Order retrieved successfully',
            data=order,
            status_code=HTTPStatus.OK
        )
    
    @order_bp.doc(summary="Update order status", description="Update the status of an existing order")
     # @admin_required()
    @order_bp.arguments(UpdateOrderStatusSchema)
   
    @order_bp.alt_response(HTTPStatus.NOT_FOUND, schema=ErrorResponseSchema, description="Order not found")
    # @order_bp.alt_response(HTTPStatus.BAD_REQUEST, schema=ErrorResponseSchema, description="Invalid order status")
    # @order_bp.alt_response(HTTPStatus.INTERNAL_SERVER_ERROR, schema=ErrorResponseSchema, description="Server error")
    # @order_bp.alt_response(HTTPStatus.FORBIDDEN, schema=ErrorResponseSchema, description="Permission denied")
    @order_bp.response(HTTPStatus.OK, OrderResponseSchema)

    # @jwt_required()
    def put(self, data, order_id: UUID):
        # Create update command
        command = UpdateOrderCommand(
            id=order_id,
            status=data.get('status')
        )
        
        # Update order
        result = container.order_service().update_order_status(command)
        
        return self._success_response(
            message=f'Order {result.order_id} status updated successfully from {result.old_status.value} to {result.new_status.value}',
            data=result,
            status_code=HTTPStatus.OK
        )
    
    @order_bp.doc(summary="Cancel order", description="Cancel an existing order")
    @order_bp.response(HTTPStatus.OK, OrderResponseSchema)
    @order_bp.response(HTTPStatus.NOT_FOUND, ErrorResponseSchema)
    @order_bp.response(HTTPStatus.BAD_REQUEST, ErrorResponseSchema)
    @jwt_required()
    def delete(self, order_id):
        # Create cancel command
        command = CancelOrderCommand(order_id=order_id)
        
        # Cancel order
        result = container.order_service().cancel_order(command)
        
        return self._success_response(
            message='Order cancelled successfully',
            data=result,
            status_code=HTTPStatus.OK
        )

@order_bp.route('/user/orders')
class UserOrdersRoutes(BaseRoute):
    @order_bp.doc(summary="Get current user's orders", description="Get all orders for the current user")
    @jwt_required()
    def get(self):
        # Get the current user ID from the JWT token
        user_id = get_jwt_identity()
        
        # Get user's orders
        orders = container.order_service().get_user_orders(user_id)
        
        return self._success_response(
            message='User orders retrieved successfully',
            data=orders,
            status_code=HTTPStatus.OK
        )


    



