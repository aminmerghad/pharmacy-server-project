from dataclasses import dataclass
from typing import Optional

@dataclass
class UserRegisterDto:
    """DTO for user registration information"""
    username: str
    password: str
    email: str
    full_name: str
    phone: str
    access_code: str

@dataclass
class RegisterUserCommand:
    """Command for registering a new user"""
    dto: UserRegisterDto 