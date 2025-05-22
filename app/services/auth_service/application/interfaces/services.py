from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ...domain.entities.user_entity import UserEntity

class IAuthenticationService(ABC):
    @abstractmethod
    async def register_user(self, user_data: Dict[str, Any]) -> UserEntity:
        pass

    @abstractmethod
    async def login(self, email: str, password: str) -> Dict[str, str]:
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        pass

    @abstractmethod
    async def validate_access_code(self, code: str) -> bool:
        pass

class IUserService(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> UserEntity:
        pass

    @abstractmethod
    async def assign_to_center(self, user_id: str, center_id: str) -> None:
        pass

class IAdminService(ABC):
    @abstractmethod
    async def create_admin(self, admin_data: Dict[str, Any]) -> UserEntity:
        pass

    @abstractmethod
    async def assign_role(self, user_id: str, role: str) -> None:
        pass 