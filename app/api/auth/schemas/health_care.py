from marshmallow import Schema, fields
from app.shared.domain.schema.common_errors import ErrorResponseSchema

class HealthCareCenterSchema(Schema):
    """Schema for creating or updating a health care center"""
    name = fields.String(required=True, description="Name of the health care center")
    address = fields.String(required=True, description="Address of the health care center")
    phone = fields.String(required=True, description="Contact phone number")
    email = fields.String(required=True, description="Contact email address")
    license_number = fields.String(required=True, description="License or registration number")
    is_active = fields.Boolean(default=True,description="Whether the center is active")

class HealthCareCenterResponseSchema(Schema):
    """Schema for health care center response"""
    id = fields.UUID(required=True, description="Health care center ID")
    name = fields.String(required=True, description="Name of the health care center")
    address = fields.String(required=True, description="Address of the health care center")
    phone = fields.String(required=True, description="Contact phone number")
    email = fields.String(required=True, description="Contact email address")
    license_number = fields.String(required=True, description="License or registration number")
    is_active = fields.Boolean(required=True, description="Whether the center is active")
    created_at = fields.DateTime(dump_only=True, description="Creation timestamp")
    updated_at = fields.DateTime(dump_only=True, description="Last update timestamp")

class HealthCareCenterFilterSchema(Schema):
    """Schema for filtering health care centers"""
    search = fields.String(description="Search term across name, email, and license number")
    name = fields.String(description="Filter by health care center name (partial match)")
    email = fields.String(description="Filter by email address (partial match)")
    license_number = fields.String(description="Filter by license number (partial match)")
    is_active = fields.Boolean(description="Filter by active status")
    page = fields.Integer(description="Page number for pagination", load_default=1)
    page_size = fields.Integer(description="Number of items per page", load_default=20)
    sort_by = fields.String(description="Field to sort by", load_default="name")
    sort_order = fields.String(description="Sort order (asc or desc)", load_default="asc")

class HealthCareCenterListItemSchema(Schema):
    """Schema for a health care center list item"""
    id = fields.UUID(required=True, description="Health care center ID")
    name = fields.String(required=True, description="Name of the health care center")
    address = fields.String(required=True, description="Address of the health care center")
    phone = fields.String(required=True, description="Contact phone number")
    email = fields.String(required=True, description="Contact email address")
    license_number = fields.String(required=True, description="License or registration number")
    is_active = fields.Boolean(required=True, description="Whether the center is active")

class HealthCareCenterListResponseSchema(Schema):
    """Schema for paginated list of health care centers"""
    items = fields.List(fields.Nested(HealthCareCenterListItemSchema), required=True, description="List of health care centers")
    total = fields.Integer(required=True, description="Total number of health care centers matching the filter")
    page = fields.Integer(required=True, description="Current page number")
    page_size = fields.Integer(required=True, description="Number of items per page")
    pages = fields.Integer(required=True, description="Total number of pages") 