from marshmallow import Schema, fields, validate
from datetime import datetime

class CategoryFieldsSchema(Schema):
    """Schema for category fields"""
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    parent_id = fields.UUID(allow_none=True)
    image_url = fields.Str(allow_none=True)
    is_active = fields.Bool(default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class CategorySchema(Schema):
    """Schema for category creation and update"""
    id = fields.UUID(dump_only=True, description="The category ID")
    category_fields = fields.Nested(CategoryFieldsSchema)

class CategoryFilterSchema(Schema):
    """Schema for category filtering"""
    name = fields.Str(description="Filter by category name (partial match)")
    parent_id = fields.UUID(description="Filter by parent category ID")
    is_active = fields.Bool(description="Filter by active status")
    sort_by = fields.Str(
        description="Field to sort by",
        validate=validate.OneOf(["name", "created_at"]),
        default="name"
    )
    sort_direction = fields.Str(
        description="Sort direction",
        validate=validate.OneOf(["asc", "desc"]),
        default="asc"
    )
    page = fields.Int(description="Page number", default=1)
    items_per_page = fields.Int(description="Items per page", default=20)

class CategoryResponseSchema(Schema):
    """Schema for category response"""
    code = fields.Int()
    message = fields.Str()
    data = fields.Nested(CategorySchema)

class CategoryPaginatedSchema(Schema):
    """Schema for paginated category response"""
    items = fields.List(fields.Nested(CategorySchema), description="List of categories")
    total_items = fields.Int(description="Total number of categories")
    page = fields.Int(description="Current page number")
    page_size = fields.Int(description="Items per page")
    total_pages = fields.Int(description="Total number of pages")

class CategoryPaginatedResponseSchema(Schema):
    """Schema for category response"""
    code = fields.Int()
    message = fields.Str()
    data = fields.Nested(CategoryPaginatedSchema)

class ErrorResponseSchema(Schema):
    """Schema for error responses"""
    success = fields.Bool(description="Indicates if the request was successful")
    message = fields.Str(description="A message describing the error")
    errors = fields.Dict(description="Detailed error messages")

class SuccessResponseSchema(Schema):
    """Schema for success responses"""
    success = fields.Bool(description="Indicates if the request was successful")
    message = fields.Str(description="A message describing the success")
    data = fields.Dict(description="Response data") 