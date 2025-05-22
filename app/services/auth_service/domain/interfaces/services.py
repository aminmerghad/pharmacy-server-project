from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class IPasswordHashService(ABC):
    @abstractmethod
    async def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass

class ITokenService(ABC):
    @abstractmethod
    async def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
        pass

    @abstractmethod
    async def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
        pass

    @abstractmethod
    async def verify_token(self, token: str) -> Dict[str, Any]:
        pass

class IEmailService(ABC):
    @abstractmethod
    async def send_verification_email(self, email: str, code: str) -> None:
        pass

    @abstractmethod
    async def send_password_reset_email(self, email: str, reset_token: str) -> None:
        pass