from dataclasses import dataclass


@dataclass
class LoginCommand:
    email: str
    password: str