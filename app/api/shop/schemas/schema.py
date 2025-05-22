from marshmallow import Schema, fields



class SuccessResponseSchema(Schema):
    status = fields.Str(description="The status of the response", default="success")
    message = fields.Str(description="A message describing the success")
    data = fields.Dict(description="The data returned by the API")

# Base response schema
class APIResponseSchema(Schema):
    status = fields.Str(description="The status of the response")
    message = fields.Str(description="A message describing the response")

class ProductSchema(Schema):
    id = fields.Int(description="The product ID")
    name = fields.Str(description="The product name")
    price = fields.Float(description="The product price")
    description = fields.Str(description="The product description")
    max_stock = fields.Int(description="The maximum stock level")
    min_stock = fields.Int(description="The minimum stock level")
    quantity = fields.Int(description="The quantity of the product")

# Product-specific response schema
class ProductSchemaResponse(APIResponseSchema):
    data = fields.Nested(ProductSchema, description="The product data")


