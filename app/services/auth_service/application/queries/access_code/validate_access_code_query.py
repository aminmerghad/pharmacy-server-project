from dataclasses import dataclass

@dataclass
class ValidateAccessCodeQuery:
    """Query for validating an access code"""
    code: str 