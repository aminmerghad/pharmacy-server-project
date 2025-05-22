from marshmallow import Schema, fields, validate
from datetime import datetime
from app.services.product_service.domain.enums.product_status import ProductStatus



class ProductFieldsSchema(Schema):
    id= fields.UUID(dump_only=True)
    name=fields.Str()
    description=fields.Str()    
    brand= fields.Str()
    category_id= fields.UUID()
    dosage_form= fields.Str()
    strength=fields.Str()
    package=fields.Str()
    image_url=fields.Str()
    status=fields.Enum(ProductStatus)
    created_at=fields.DateTime(dump_only=True)
    updated_at=fields.DateTime(dump_only=True)

class InventoryFieldsSchema(Schema):
    quantity=fields.Int()
    price=fields.Float()
    max_stock=fields.Int()
    min_stock=fields.Int()
    expiry_date=fields.Date()
    id= fields.UUID(dump_only=True)
    product_id= fields.UUID(dump_only=True)
    supplier_id=fields.UUID()

class ProductSchema(Schema):
    """Schema for product creation and update"""
    id = fields.UUID(dump_only=True, description="The product ID")
    product_fields=fields.Nested(ProductFieldsSchema)
    inventory_fields=fields.Nested(InventoryFieldsSchema)
    
class ProductFilterSchema(Schema):
    """Schema for product filtering"""
    name = fields.Str(description="Filter by product name (partial match)")
    category_id = fields.UUID(description="Filter by category ID")
    brand = fields.Str(description="Filter by brand (partial match)")
    is_prescription_required = fields.Bool(description="Filter by prescription requirement")
    is_active = fields.Bool(description="Filter by active status")
    min_stock = fields.Int(description="Filter by minimum stock level")
    has_stock = fields.Bool(description="Filter by stock availability")
    sort_by = fields.Str(
        description="Field to sort by", 
        validate=validate.OneOf(["name", "created_at", "brand"]),
        default="name"
    )
    sort_direction = fields.Str(
        description="Sort direction", 
        validate=validate.OneOf(["asc", "desc"]),
        default="asc"
    )
    page = fields.Int(description="Page number", default=1)
    items_per_page = fields.Int(description="Items per page", default=20)
    # Additional fields for advanced filtering
    min_price = fields.Float(description="Minimum price filter")
    max_price = fields.Float(description="Maximum price filter")
    status = fields.Enum(ProductStatus, description="Filter by product status")
    days_threshold = fields.Int(description="Days threshold for expiry filtering")
    threshold_percentage = fields.Float(description="Threshold percentage for low stock")

class ProductSearchSchema(Schema):
    """Schema for product search with advanced options"""
    search = fields.Str(description="Search term for name, description, brand")
    category_id = fields.UUID(description="Filter by category ID")
    brand = fields.Str(description="Filter by brand")
    min_price = fields.Float(description="Minimum price")
    max_price = fields.Float(description="Maximum price")
    status = fields.Enum(ProductStatus, description="Product status filter")
    in_stock_only = fields.Bool(description="Show only products in stock", default=False)
    page = fields.Int(description="Page number", default=1)
    page_size = fields.Int(description="Items per page", default=20)
    sort_by = fields.Str(
        description="Field to sort by", 
        validate=validate.OneOf(["name", "price", "created_at", "brand"]),
        default="name"
    )
    sort_direction = fields.Str(
        description="Sort direction", 
        validate=validate.OneOf(["asc", "desc"]),
        default="asc"
    )

class BulkProductSchema(Schema):
    """Schema for bulk product operations"""
    products = fields.List(
        fields.Nested(ProductSchema),
        description="List of products to create",
        required=True,
        validate=validate.Length(min=1, max=100)
    )

class ProductResponseSchema(Schema):
    """Schema for product response"""
    code = fields.Int()
    message = fields.Str()
    data = fields.Nested(ProductSchema)
    
    
class ProductPaginatedSchema(Schema):
    """Schema for paginated product response"""
    items = fields.List(fields.Nested(ProductSchema), description="List of products")
    total = fields.Int(description="Total number of products")
    page = fields.Int(description="Current page number")
    items_per_page = fields.Int(description="Items per page")
    total_pages = fields.Int(description="Total number of pages")

class ProductPaginatedResponseSchema(Schema):
    """Schema for product response"""
    code = fields.Int()
    message = fields.Str()
    data = fields.Nested(ProductPaginatedSchema)

class ProductExpiryReportSchema(Schema):
    """Schema for product expiry report"""
    product = fields.Nested(ProductResponseSchema, description="Product information")
    expiry_date = fields.DateTime(description="Expiry date")
    quantity = fields.Int(description="Quantity expiring")
    total_expiring = fields.Int(description="Total quantity expiring")

class ProductInventoryValueReportSchema(Schema):
    """Schema for product inventory value report"""
    product = fields.Nested(ProductResponseSchema, description="Product information")
    quantity = fields.Int(description="Current quantity")
    price = fields.Float(description="Unit price")
    total_value = fields.Float(description="Total inventory value")

class StockStatusSchema(Schema):
    """Schema for product stock status"""
    product_id = fields.UUID(description="Product ID")
    is_available = fields.Bool(description="Whether product is available")
    remaining_stock = fields.Int(description="Remaining stock quantity")
    warnings = fields.List(fields.Str(), description="Stock warnings")
    status = fields.List(fields.Str(), description="Stock status codes")
    days_until_expiry = fields.Int(description="Days until expiry", allow_none=True)
    
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
