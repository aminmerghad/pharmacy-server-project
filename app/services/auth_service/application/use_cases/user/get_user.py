import logging
from typing import Optional
from uuid import UUID

from app.services.auth_service.application.queries import GetUserQuery
from app.services.auth_service.domain.entities import UserEntity
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.auth_service.domain.exceptions.auth_errors import UserNotFoundError

# logger = logging.getLogger(__name__)
class UserGetUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, query: GetUserQuery) -> Optional[UserEntity]:
        """
            Retrieve a user by their unique identifier.

            Args:
                query (UserQueryGetter): The query instance to access user data.
        
            Returns:
                Optional[UserEntity]: The user entity if found, else None.
        
            Raises:
                UserNotFoundError: If no user is found with the provided user_id.
        """
        user = self.uow.user.get_by_email(query.email)
        if not user:
            raise UserNotFoundError(f"User with email {query.email} does not exist.")
        return user

