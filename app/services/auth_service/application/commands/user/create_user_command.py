from dataclasses import dataclass


@dataclass
class CreateUserCommand:
    email: str
    username: str
    password: str
    full_name: str
    phone: str
    



