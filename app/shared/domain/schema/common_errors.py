from marshmallow import Schema, fields

class ErrorResponseSchema(Schema):
    code = fields.Int(description="The HTTP status code of the error")
    status = fields.Str(description="The status of the response", default="error")
    message = fields.Str(description="A message describing the error")
    errors=fields.Str(description="A dict describing the error")
