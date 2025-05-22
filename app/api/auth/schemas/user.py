from marshmallow import Schema, fields, validates, ValidationError
from .health_care import HealthCareCenterSchema
import re

class UserBaseSchema(Schema):
    id = fields.UUID(dump_only=True, metadata={'description':"The user ID"})
    username = fields.Str(required=True, metadata={"description": "The user username"})
    password = fields.Str(load_only=True, required=True, metadata={"description": "The user password"})
    email = fields.Email(required=True, metadata={"description": "The user email"})
    full_name = fields.Str(required=True, metadata={"description": "The user full name"})
    phone = fields.Str(required=True, metadata={"description": "The user phone"})
    created_at = fields.DateTime(dump_only=True, metadata={"description": "The user created at"})
    updated_at = fields.DateTime(dump_only=True, metadata={"description": "The user updated at"})

    @validates('username')
    def validate_username(self, value):
        if len(value) < 3:
            raise ValidationError("Username must be at least 3 characters long")

    @validates('full_name')
    def validate_full_name(self, value):
        if len(value) < 3:
            raise ValidationError("Full name must be at least 3 characters long")

    @validates('password')
    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", value):
            raise ValidationError("Password must contain at least one uppercase letter")
            
        if not re.search(r"[a-z]", value):
            raise ValidationError("Password must contain at least one lowercase letter")
            
        if not re.search(r"\d", value):
            raise ValidationError("Password must contain at least one number")
    @validates('phone')
    def validate_phone(self, value):
        if not re.match(r"^\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4}$", value):
            raise ValidationError("Invalid phone number format")

class UserSchema(UserBaseSchema):
    health_care_center = fields.Nested(HealthCareCenterSchema, required=False, description="The health care center")
class UserRegistrationSchema(UserSchema):
    code = fields.Str(required=True, description="The user code")
#admin registration schema
class AdminRegistrationSchema(UserBaseSchema):
    initialization_key = fields.Str(required=True, description="Admin initialization key") 

