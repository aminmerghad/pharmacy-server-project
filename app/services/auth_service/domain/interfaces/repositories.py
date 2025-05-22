from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.user_entity import UserEntity
from ..aggregators.access_code_aggregator import AccessCodeAggregator

class IUserRepository(ABC):
    @abstractmethod
    async def save(self, user: UserEntity) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def update(self, user: UserEntity) -> None:
        pass

class IAccessCodeRepository(ABC):
    @abstractmethod
    async def save(self, access_code: AccessCodeAggregator) -> None:
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[AccessCodeAggregator]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[AccessCodeAggregator]:
        pass

    @abstractmethod
    async def update(self, access_code: AccessCodeAggregator) -> None:
        pass 