from typing import Optional
from app.services.auth_service.application.queries import GetUserQuery
from app.services.auth_service.application.use_cases import UserGetUseCase
from app.services.auth_service.domain.entities import UserEntity
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork


class AuthQueryService:
    def __init__(self, uow: UnitOfWork):
       self.user_get_use_case=None
       self._queryInitialisation(uow)
    def _queryInitialisation(self, uow: UnitOfWork):
        self.user_get_use_case = UserGetUseCase(uow)

    def get_user(self, query: GetUserQuery) -> Optional[UserEntity]:
        return self.user_get_use_case.execute(query)
