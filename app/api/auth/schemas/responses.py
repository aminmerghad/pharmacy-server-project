from marshmallow import Schema, fields
from app.shared.domain.schema.common_errors import ErrorResponseSchema
from .user import UserSchema
from .auth import AccessCodeGenerationSchema, LoginResponse

class AdminRegistrationResponseSchema(Schema):
    code = fields.Int(description="Admin registration code")
    message = fields.Str(description="Admin registration message")
    data = fields.Nested(UserSchema, description="Admin registration data")
    
    

class LogInResponseSchema(Schema):
    code = fields.Int(description="Login code")
    message = fields.Str(description="Login message")
    data = fields.Nested(LoginResponse, description="Login data")


class UserResponseSchema(Schema):
    data = fields.Nested(UserSchema, description="User data")
    message = fields.Str(description="User message")
    success = fields.Bool(description="User success")

class AccessCodeResponseSchema(Schema):
    data = fields.Nested(AccessCodeGenerationSchema, description="Access code data")
    message = fields.Str(description="Response message")
    success = fields.Bool(description="Success status")

class AdminRegistrationErrorResponseSchema(ErrorResponseSchema):
    errors = fields.Dict(required=False,description="The errors of the response") 

class AccessCodeEntitySchema(Schema):
    code = fields.Str(description="Access code")
    created_at = fields.Str(description="Created at")
    expires_at = fields.Str(description="Expires at")
    health_care_center_id = fields.Str(description="Health care center id")
    id = fields.Str(description="Id")
    is_active = fields.Bool(description="Is active")
    is_used = fields.Bool(description="Is used")
    updated_at = fields.Str(description="Updated at")
    
class AccessCodeItemSchema(Schema):
    access_code_entity = fields.Nested(AccessCodeEntitySchema, description="Access code entity")
    health_care_center_name = fields.Str(description="Health care center name")
    is_valid = fields.Bool(description="Is valid")
    message = fields.Str(description="Message")


    
class AccessCodeValidationResponseSchema(Schema):
    data = fields.Nested(AccessCodeItemSchema, description="Access code data")
    message = fields.Str(description="Response message")
    success = fields.Bool(description="Success status")

class AccessCodeListResponseSchema(Schema):
    data = fields.List(fields.Nested(AccessCodeItemSchema), description="Access code list")
    message = fields.Str(description="Response message")
    success = fields.Bool(description="Success status")

