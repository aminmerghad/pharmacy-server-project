from marshmallow import Schema, fields

class LoginSchema(Schema):
    email = fields.String(required=True, description="User email")
    password = fields.String(required=True, description="User password")

class LoginResponse(Schema):
    access_token = fields.Str(description="JWT access token")
    refresh_token = fields.Str(description="JWT refresh token")
    user_id = fields.Str(description="User ID")
    email = fields.Str(description="User email")

class AccessCodeGenerationSchema(Schema):
    """Schema for generating an access code"""
    id = fields.UUID(dump_only=True,description="Access code ID")
    code = fields.String(dump_only=True,description="Access code")
    referral_email = fields.String(description="Email of the referral")
    referral_phone = fields.String(description="Phone of the referral", allow_none=True)
    health_care_center_email = fields.String(description="Email of the health care center to find by email", allow_none=True)
    health_care_center_phone = fields.String(description="Phone of the health care center to find by phone", allow_none=True)
    health_care_center_id = fields.UUID(dump_only=True,description="ID of the health care center", allow_none=True)
    health_care_center_name = fields.String(dump_only=True,description="Name of the health care center", allow_none=True)
    expiry_days = fields.Integer(description="Number of days until the code expires", default=7)
    created_at = fields.String(dump_only=True,description="Creation date")
    expires_at = fields.String(dump_only=True,description="Expiration date")
    is_active = fields.Boolean(dump_only=True,description="Is active")

class AccessCodeFilterSchema(Schema):
    """Schema for filtering access codes"""
    search = fields.String(description="Search term across code, email, and phone")
    email = fields.String(description="Filter by email (partial match)")
    is_used = fields.Boolean(description="Filter by used status")
    is_active = fields.Boolean(description="Filter by active status")
    role = fields.String(description="Filter by role")
    page = fields.Integer(description="Page number for pagination", load_default=1)
    page_size = fields.Integer(description="Number of items per page", load_default=20)
    sort_by = fields.String(description="Field to sort by", load_default="created_at")
    sort_order = fields.String(description="Sort order (asc or desc)", load_default="desc") 