from dataclasses import dataclass
from passlib.hash import pbkdf2_sha256
from app.services.auth_service.domain.exceptions.auth_errors import InvalidPasswordError

@dataclass()
class Password:
    hashed: str

    def __init__(self, plain_password: str):
        self._validate(plain_password)
        self.hashed = pbkdf2_sha256.hash(plain_password)

    def _validate(self, password: str) -> None:
        if len(password) < 8:
            raise InvalidPasswordError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in password):
            raise InvalidPasswordError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in password):
            raise InvalidPasswordError("Password must contain at least one number")

    def verify(self, plain_password: str) -> bool:
        return pbkdf2_sha256.verify(plain_password, self.hashed)
    
    @staticmethod
    def from_hash(hashed_password: str) -> 'Password':
        # Create a Password instance with the provided hashed password
        password = Password.__new__(Password)  # Create an instance without calling __init__
        password.hashed = hashed_password  # Set the hashed password directly
        return password