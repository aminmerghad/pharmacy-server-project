# # from app.api import inventory_bp
# # from app.api.base_routes import BaseRoute

# # @inventory_bp.route('/low')
# # class LowStockList(BaseRoute):  
# #     def post(self):
# #         pass  
    
# #     @inventory_bp.response(200)
# #     def get(self):
# #         """Get all products with low stock"""
# #         pass
# #         # result, status_code = container.inventory_service().get_low_stock_products()
# #         # if status_code != HTTPStatus.OK:
# #         #     return self._error_response(message=result, status_code=status_code)
# #         # return self._success_response(data=result, message="Low stock products fetched successfully")
    
# #     @inventory_bp.response(200)
# #     def put(self):
# #         """Update low stock threshold for multiple products"""
# #         pass
# #         # threshold_data = request.get_json()
# #         # result, status_code = container.inventory_service().update_low_stock_thresholds(threshold_data)
# #         # if status_code != HTTPStatus.OK:
# #         #     return self._error_response(message=result, status_code=status_code)
# #         # return self._success_response(data=result, message="Low stock thresholds updated successfully")

# # @inventory_bp.route('/low/<UUID:product_id>')
# # class LowStockProduct(BaseRoute):
# #     @inventory_bp.response(200)
# #     def get(self, product_id):
# #         """Get low stock details for a specific product"""
# #         pass
# #         # result, status_code = container.inventory_service().get_product_stock_status(product_id)
# #         # if status_code != HTTPStatus.OK:
# #         #     return self._error_response(message=result, status_code=status_code)
# #         # return self._success_response(data=result, message="Product stock status fetched successfully")
    
# #     @inventory_bp.response(200)
# #     def put(self, product_id):
# #         """Update low stock threshold for a specific product"""
# #         pass
# #         # threshold_data = request.get_json()
# #         # result, status_code = container.inventory_service().update_product_stock_threshold(product_id, threshold_data)
# #         # if status_code != HTTPStatus.OK:
# #         #     return self._error_response(message=result, status_code=status_code)
# #         # return self._success_response(data=result, message="Product stock threshold updated successfully")

# # @inventory_bp.route('/expiresoon')
# # class ExperingSoonList(BaseRoute):  
# #     def post(self):
# #         pass
    
# #     @inventory_bp.response(200)
# #     def get(self):
# #         pass
# #         # """Get all products expiring soon"""
# #         # days_threshold = request.args.get('days', 30, type=int)
# #         # result, status_code = container.inventory_service().get_expiring_soon_products(days_threshold)
# #         # if status_code != HTTPStatus.OK:
# #         #     return self._error_response(message=result, status_code=status_code)
# #         # return self._success_response(data=result, message="Expiring soon products fetched successfully")

# # @inventory_bp.route('/expiresoon/<UUID:product_id>')
# # class ExpiringSoonProduct(BaseRoute):
# #     @inventory_bp.response(200)
# #     def get(self, product_id):
# #         pass
# #         # """Get expiration details for a specific product"""
# #         # result, status_code = container.inventory_service().get_product_expiration_status(product_id)
# #         # if status_code != HTTPStatus.OK:
# #         #     return self._error_response(message=result, status_code=status_code)
# #         # return self._success_response(data=result, message="Product expiration status fetched successfully")

# from http import HTTPStatus
# from flask import jsonify, request
# from flask.views import MethodView
# from marshmallow import Schema, fields
# from uuid import UUID

# from app.api import inventory_bp
# from app.api.base_routes import BaseRoute
# from app.extensions import container
# from app.services.inventory_service.application.commands.record_movement_command import RecordMovementCommand
# from app.services.inventory_service.domain.enums.movement_type import MovementType
# from app.services.inventory_service.application.commands.adjust_stock_command import AdjustStockCommand
# from app.services.inventory_service.application.commands.transfer_stock_command import TransferStockCommand
# from app.services.inventory_service.application.commands.write_off_command import WriteOffCommand


# class MovementTypeField(fields.Field):
#     """Custom field for serializing/deserializing MovementType enum"""
    
#     def _serialize(self, value, attr, obj, **kwargs):
#         if value is None:
#             return None
#         return value.value
    
#     def _deserialize(self, value, attr, data, **kwargs):
#         try:
#             return MovementType(value)
#         except ValueError:
#             valid_types = [t.value for t in MovementType]
#             raise fields.ValidationError(
#                 f"Invalid movement type. Must be one of: {', '.join(valid_types)}"
#             )


# class RecordMovementSchema(Schema):
#     """Schema for recording stock movements"""
#     inventory_id = fields.UUID(required=True)
#     quantity = fields.Integer(required=True, validate=lambda n: n > 0)
#     movement_type = MovementTypeField(required=True)
#     reference_id = fields.UUID(required=False, allow_none=True)
#     batch_number = fields.String(required=False, allow_none=True)
#     reason = fields.String(required=False, allow_none=True)


# class MovementResponseSchema(Schema):
#     """Schema for movement response"""
#     id = fields.UUID()
#     inventory_id = fields.UUID()
#     quantity = fields.Integer()
#     movement_type = fields.String()
#     reference_id = fields.UUID(allow_none=True)
#     batch_number = fields.String(allow_none=True)
#     reason = fields.String(allow_none=True)
#     created_at = fields.DateTime()


# class AdjustStockSchema(Schema):
#     """Schema for stock adjustment requests"""
#     inventory_id = fields.UUID(required=True)
#     quantity = fields.Integer(required=True)  # Positive for increase, negative for decrease
#     reason = fields.String(required=True)
#     notes = fields.String(required=False, allow_none=True)


# class AdjustStockResponseSchema(Schema):
#     """Schema for stock adjustment responses"""
#     inventory_id = fields.UUID()
#     product_id = fields.UUID()
#     previous_quantity = fields.Integer()
#     adjustment_quantity = fields.Integer()
#     new_quantity = fields.Integer()
#     reason = fields.String()
#     movement_id = fields.UUID()


# class TransferStockSchema(Schema):
#     """Schema for stock transfer requests"""
#     inventory_id = fields.UUID(required=True)
#     quantity = fields.Integer(required=True)
#     source_location = fields.String(required=True)
#     destination_location = fields.String(required=True)
#     notes = fields.String(required=False, allow_none=True)


# class TransferStockResponseSchema(Schema):
#     """Schema for stock transfer responses"""
#     inventory_id = fields.UUID()
#     product_id = fields.UUID()
#     quantity = fields.Integer()
#     source_location = fields.String()
#     destination_location = fields.String()
#     source_movement_id = fields.UUID()
#     destination_movement_id = fields.UUID()


# class WriteOffSchema(Schema):
#     """Schema for inventory write-off requests"""
#     inventory_id = fields.UUID(required=True)
#     quantity = fields.Integer(required=True)
#     reason = fields.String(required=True)
#     movement_type = MovementTypeField(required=True)
#     notes = fields.String(required=False, allow_none=True)
#     batch_number = fields.String(required=False, allow_none=True)


# class WriteOffResponseSchema(Schema):
#     """Schema for inventory write-off responses"""
#     inventory_id = fields.UUID()
#     product_id = fields.UUID()
#     original_quantity = fields.Integer()
#     write_off_quantity = fields.Integer()
#     new_quantity = fields.Integer()
#     reason = fields.String()
#     movement_type = fields.String()
#     movement_id = fields.UUID()


# @inventory_bp.route('/movements')
# class StockMovementRoute(BaseRoute):
#     @inventory_bp.arguments(RecordMovementSchema)
#     @inventory_bp.response(HTTPStatus.CREATED, MovementResponseSchema)
#     def post(self, movement_data):
#         """
#         Record a stock movement.
        
#         This endpoint handles various types of stock movements including:
#         - Receiving stock from suppliers
#         - Dispensing stock to customers
#         - Adjusting stock levels
#         - Recording damaged or expired stock
#         - Transferring stock between locations
#         """
#         # Validate required fields based on movement type
#         movement_type = movement_data['movement_type']
        
#         # Check if reference_id is required but missing
#         if MovementType.requires_reference(movement_type) and not movement_data.get('reference_id'):
#             return self._error_response(
#                 message=f"Reference ID is required for {movement_type} movements",
#                 status_code=HTTPStatus.BAD_REQUEST
#             )
        
#         # Check if reason is required but missing
#         if MovementType.requires_reason(movement_type) and not movement_data.get('reason'):
#             return self._error_response(
#                 message=f"Reason is required for {movement_type} movements",
#                 status_code=HTTPStatus.BAD_REQUEST
#             )
        
#         try:
#             # Create and execute the command
#             command = RecordMovementCommand(**movement_data)
#             result = container.inventory_service().record_movement(command)
            
#             return self._success_response(
#                 data=result.model_dump(),
#                 message="Stock movement recorded successfully",
#                 status_code=HTTPStatus.CREATED
#             )
#         except ValueError as e:
#             return self._error_response(
#                 message=str(e),
#                 status_code=HTTPStatus.BAD_REQUEST
#             )
#         except Exception as e:
#             return self._error_response(
#                 message=f"Error recording stock movement: {str(e)}",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#             )


# @inventory_bp.route('/movements/inventory/<uuid:inventory_id>')
# class InventoryMovementsRoute(BaseRoute):
#     @inventory_bp.response(HTTPStatus.OK, MovementResponseSchema(many=True))
#     def get(self, inventory_id):
#         """
#         Get all movements for a specific inventory item.
        
#         This endpoint returns the complete movement history for an inventory item,
#         allowing for detailed tracking and auditing of stock changes.
#         """
#         try:
#             movements = container.inventory_service().get_inventory_movements(inventory_id)
            
#             return self._success_response(
#                 data=[m.model_dump() for m in movements],
#                 message="Inventory movements retrieved successfully",
#                 status_code=HTTPStatus.OK
#             )
#         except Exception as e:
#             return self._error_response(
#                 message=f"Error retrieving inventory movements: {str(e)}",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#             )


# @inventory_bp.route('/adjust')
# class StockAdjustmentRoute(BaseRoute):
#     @inventory_bp.arguments(AdjustStockSchema)
#     @inventory_bp.response(HTTPStatus.OK, AdjustStockResponseSchema)
#     def post(self, adjustment_data):
#         """
#         Adjust inventory stock levels.
        
#         This endpoint allows for increasing or decreasing stock levels
#         with proper tracking and validation. A reason must be provided
#         for audit purposes.
        
#         For stock increases, use a positive quantity.
#         For stock decreases, use a negative quantity.
#         """
#         try:
#             command = AdjustStockCommand(**adjustment_data)
#             result = container.inventory_service().adjust_stock(command)
            
#             return self._success_response(
#                 data=result.to_json(),
#                 message="Stock adjusted successfully",
#                 status_code=HTTPStatus.OK
#             )
#         except ValueError as e:
#             return self._error_response(
#                 message=str(e),
#                 status_code=HTTPStatus.BAD_REQUEST
#             )
#         except Exception as e:
#             return self._error_response(
#                 message=f"Error adjusting stock: {str(e)}",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#             )


# @inventory_bp.route('/low')
# class LowStockRoute(BaseRoute):
#     @inventory_bp.response(HTTPStatus.OK)
#     def get(self):
#         """
#         Get inventory items with low stock levels.
        
#         This endpoint returns items with stock levels at or below their minimum
#         stock threshold. The threshold can be adjusted using the 'threshold_percentage'
#         query parameter.
        
#         Query Parameters:
#             threshold_percentage (optional): Percentage of min_stock to use as threshold.
#                                            Default is 100%, meaning at or below min_stock.
#         """
#         threshold_percentage = request.args.get('threshold_percentage', default=100, type=float)
        
#         try:
#             items = container.inventory_service().get_low_stock_items(threshold_percentage)
            
#             return self._success_response(
#                 data=items,
#                 message=f"Retrieved {len(items)} low stock items",
#                 status_code=HTTPStatus.OK
#             )
#         except Exception as e:
#             return self._error_response(
#                 message=f"Error retrieving low stock items: {str(e)}",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#             )


# @inventory_bp.route('/expiring')
# class ExpiringItemsRoute(BaseRoute):
#     @inventory_bp.response(HTTPStatus.OK)
#     def get(self):
#         """
#         Get inventory items that are approaching expiration.
        
#         This endpoint returns items that will expire within the specified
#         number of days. The days threshold can be adjusted using the 'days_threshold'
#         query parameter.
        
#         Query Parameters:
#             days_threshold (optional): Number of days to look ahead for expiring items.
#                                      Default is 90 days.
#         """
#         days_threshold = request.args.get('days_threshold', default=90, type=int)
        
#         try:
#             items = container.inventory_service().get_expiring_items(days_threshold)
            
#             return self._success_response(
#                 data=items,
#                 message=f"Retrieved {len(items)} items expiring within {days_threshold} days",
#                 status_code=HTTPStatus.OK
#             )
#         except Exception as e:
#             return self._error_response(
#                 message=f"Error retrieving expiring items: {str(e)}",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#             )


# @inventory_bp.route('/expired')
# class ExpiredItemsRoute(BaseRoute):
#     @inventory_bp.response(HTTPStatus.OK)
#     def get(self):
#         """
#         Get inventory items that have already expired.
        
#         This endpoint returns all items in inventory that have passed their
#         expiration date but still have stock.
#         """
#         try:
#             items = container.inventory_service().get_expired_items()
            
#             return self._success_response(
#                 data=items,
#                 message=f"Retrieved {len(items)} expired items",
#                 status_code=HTTPStatus.OK
#             )
#         except Exception as e:
#             return self._error_response(
#                 message=f"Error retrieving expired items: {str(e)}",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#             )


# @inventory_bp.route('/summary')
# class InventorySummaryRoute(BaseRoute):
#     @inventory_bp.response(HTTPStatus.OK)
#     def get(self):
#         """
#         Get a summary of the current inventory status.
        
#         This endpoint returns summary statistics about the inventory,
#         including total items, value, and counts by status.
#         """
#         try:
#             summary = container.inventory_service().get_inventory_summary()
            
#             return self._success_response(
#                 data=summary,
#                 message="Retrieved inventory summary",
#                 status_code=HTTPStatus.OK
#             )
#         except Exception as e:
#             return self._error_response(
#                 message=f"Error retrieving inventory summary: {str(e)}",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#             )


# @inventory_bp.route('/transfer')
# class StockTransferRoute(BaseRoute):
#     @inventory_bp.arguments(TransferStockSchema)
#     @inventory_bp.response(HTTPStatus.OK, TransferStockResponseSchema)
#     def post(self, transfer_data):
#         """
#         Transfer inventory stock between locations.
        
#         This endpoint allows for transferring stock from one location to another
#         with proper tracking of both source and destination movements.
#         """
#         try:
#             command = TransferStockCommand(**transfer_data)
#             result = container.inventory_service().transfer_stock(command)
            
#             return self._success_response(
#                 data=result.to_json(),
#                 message="Stock transferred successfully",
#                 status_code=HTTPStatus.OK
#             )
#         except ValueError as e:
#             return self._error_response(
#                 message=str(e),
#                 status_code=HTTPStatus.BAD_REQUEST
#             )
#         except Exception as e:
#             return self._error_response(
#                 message=f"Error transferring stock: {str(e)}",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#             )


# @inventory_bp.route('/write-off')
# class InventoryWriteOffRoute(BaseRoute):
#     @inventory_bp.arguments(WriteOffSchema)
#     @inventory_bp.response(HTTPStatus.OK, WriteOffResponseSchema)
#     def post(self, write_off_data):
#         """
#         Write off inventory due to expiry, damage, or other reasons.
        
#         This endpoint allows for writing off inventory items with proper
#         tracking of the reason and type of write-off (expired, damaged, etc.).
#         """
#         try:
#             command = WriteOffCommand(**write_off_data)
#             result = container.inventory_service().write_off_inventory(command)
            
#             return self._success_response(
#                 data=result.to_json(),
#                 message="Inventory written off successfully",
#                 status_code=HTTPStatus.OK
#             )
#         except ValueError as e:
#             return self._error_response(
#                 message=str(e),
#                 status_code=HTTPStatus.BAD_REQUEST
#             )
#         except Exception as e:
#             return self._error_response(
#                 message=f"Error writing off inventory: {str(e)}",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#             )



    
