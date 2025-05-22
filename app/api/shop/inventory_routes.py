from http import HTTPStatus
from flask import jsonify, make_response, request
from flask.views import MethodView
from marshmallow import Schema,fields
from pydantic import BaseModel
from app.api import inventory_bp
from app.api.base_routes import BaseRoute
from app.api.shop.dtos.stock_received_dto import ReceivedStockDto
from app.extensions import container

from app.services.inventory_service.application.commands.received_stock_command import ReceivedStockCommand

from app.shared.contracts.inventory.stock_check import StockCheckItemContract, StockCheckRequestContract



class StockCheckItemDto(BaseModel):
    product_id: str
    quantity: int
class StockCheckItemsDto(BaseModel):    
    items: list[StockCheckItemDto]

class StockChecResponseSchema(Schema):
    code = fields.Int(description="Stock Check code")
    message = fields.Str(description="Stock Check message")
    data = fields.Dict(description="Stock Check data")
class StockCheckItemRequestSchema(Schema):
    product_id=fields.UUID()
    quantity=fields.Int()

class StockCheckRequestSchema(Schema):
    items = fields.Nested(StockCheckItemRequestSchema, many=True)
    consumer_id=fields.UUID()






@inventory_bp.route('/stock/check')
class StockCheckRoute(BaseRoute):
    @inventory_bp.arguments(StockCheckRequestSchema)
    @inventory_bp.response(HTTPStatus.OK, StockChecResponseSchema)
    def post(self,stock_check_data):          
        result = container.inventory_service().stock_check(
            StockCheckRequestContract(
                items=[
                    StockCheckItemContract(
                        product_id=item["product_id"],
                        quantity=item["quantity"]
                    )
                    for item in stock_check_data.get("items")
                ],
                consumer_id=stock_check_data.get("consumer_id")

            )
        )
        return self._success_response(
            data=result.model_dump(),
            message="Sotck checked successfully",
            status_code=HTTPStatus.OK
        )

# @inventory_bp.route('/adjust/<UUID:inventory_id>')
# class StockAdjustmentRoute(BaseRoute):
# #     @stock_bp.arguments(StockMovementSchema)
# #     @stock_bp.response(200, StockMovementSchema)
# #     @require_auth
# #     def post(self, movement_data, inventory_id):
# #         """Adjust stock level"""
# #         result, status_code = container.inventory_service().adjust_stock(inventory_id, movement_data)
# #         if status_code != HTTPStatus.OK:
# #             return {"success": False, "message": result}, status_code
# #         return {"success": True, "data": result, "message": "Stock adjusted successfully"} 
#     def post(self): 
#         pass

class StockReceiveRequestSchema(Schema):
    product_id= fields.UUID()
    quantity = fields.Int()
    

@inventory_bp.route('/receive')
class StockReceiveRoute(BaseRoute):
    @inventory_bp.arguments(StockReceiveRequestSchema)
    # @inventory_bp.response(HTTPStatus.OK, StockReceiveResponseSchema)
    def post(self,stock_receive_data):
        result = container.inventory_service().receive_stock(
            ReceivedStockCommand(
                **stock_receive_data
            )
        )
        return self._success_response(
            data=result,
            message="Sotck checked successfully",
            status_code=HTTPStatus.OK
        )
                 

# @stock_bp.route('/movements/product/<int:product_id>')
# class ProductStockMovements(MethodView):
    
#     @stock_bp.response(200, StockMovementSchema(many=True))
#     def get(self, product_id):
#         """Get stock movements for a specific product"""
#         result, status_code = container.inventory_service().get_product_movements(product_id)
#         if status_code != HTTPStatus.OK:
#             return {"success": False, "message": result}, status_code
#         return {"success": True, "data": result, "message": "Product stock movements fetched successfully"}










   


