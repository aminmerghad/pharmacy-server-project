from dataclasses import dataclass

from app.services.auth_service.domain.exceptions.auth_errors import InvalidCredentialsError
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.auth_service.infrastructure.query_services.aurh_query_service import AuthQueryService


@dataclass
class RefreshTokenResponse:
    access_token: str
    refresh_token: str
    user_id: str
    username: str

class RefreshTokenUseCase:
    def __init__(self, uow: UnitOfWork, query_service: AuthQueryService):
        self._uow = uow
        self._query_service = query_service

    def execute(self) -> RefreshTokenResponse:
        refresh_token = self._uow.jwt_manager.decode_refresh_token()
        if not refresh_token:
            raise InvalidCredentialsError("Invalid refresh token.")

        user = self._query_service.get_user_by_refresh_token(refresh_token)
        if not user:
            raise InvalidCredentialsError("User not found.")

        access_token = self._uow.jwt_manager.create_access_token(user)
        new_refresh_token = self._uow.jwt_manager.create_refresh_token(user)

        return RefreshTokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            user_id=str(user.id),
            username=user.username
        )
