from marshmallow import Schema, fields, validate

from app.services.order_service.domain.value_objects.order_status import OrderStatus

class OrderItemSchema(Schema):
    product_id = fields.UUID(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    price = fields.Float(required=False)  # Can be calculated on server if not provided
    
class OrderSchema(Schema):
    order_id = fields.Str(dump_only=True)
    consumer_id = fields.UUID(dump_only=True)
    items = fields.List(fields.Nested(OrderItemSchema))
    status = fields.Enum(enum=OrderStatus, by_value=True)
    total_amount = fields.Float()
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    completed_at = fields.DateTime(dump_only=True)

class OrderFilterSchema(Schema):
    user_id=fields.UUID(required=False, description="Filter by user ID"),
    status=fields.String(required=False, description="Filter by order status"),
    start_date=fields.DateTime(required=False, description="Filter by start date"),
    end_date=fields.DateTime(required=False, description="Filter by end date"),
    min_amount=fields.Float(required=False, description="Filter by minimum amount"),
    max_amount=fields.Float(required=False, description="Filter by maximum amount"),
    page=fields.Integer(required=False, missing=1, description="Page number"),
    per_page=fields.Integer(required=False, missing=10, description="Items per page")

class CreateOrderSchema(Schema):
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=validate.Length(min=1))
    notes = fields.Str(required=False, allow_none=True)

class UpdateOrderStatusSchema(Schema):
    status = fields.Enum(enum=OrderStatus, by_value=True, required=True)

class PaginationSchema(Schema):
    page=fields.Integer(required=False)
    pages=fields.Integer(required=False)
    per_page=fields.Integer(required=False)
    total=fields.Integer(required=False)

class OrderListSchema(Schema):
    orders = fields.Nested(OrderSchema,many=True)
    pagination=fields.Nested(PaginationSchema)

class OrderListResponseSchema(Schema):
    code = fields.Int(description="order code")
    message = fields.Str(description="order message")
    data = fields.Nested(OrderListSchema, description="order data")
    
class OrderResponseSchema(Schema):
    code = fields.Int(description="order code")
    message = fields.Str(description="order message")
    data = fields.Nested(OrderSchema, description="order data")


