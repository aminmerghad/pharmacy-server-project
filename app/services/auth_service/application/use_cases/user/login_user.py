from dataclasses import dataclass
from app.services.auth_service.application.commands import LoginCommand
from app.services.auth_service.application.queries import GetUserQuery
from app.services.auth_service.domain.exceptions.auth_errors import InvalidCredentialsError
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.auth_service.domain.value_objects.password import Password
from app.services.auth_service.infrastructure.query_services.aurh_query_service import AuthQueryService
@dataclass
class LoginResponseDto:
    access_token: str
    refresh_token: str
    user_id: str
    email: str

class UserLoginUseCase:
    def __init__(self, uow:UnitOfWork,query_service:AuthQueryService):
        self._uow=uow
        self._query_service=query_service
    def _get_user(self,email:str):
        try:
            user = self._query_service.get_user(GetUserQuery(
                email=email
                ))
            return user
        except Exception:
            raise InvalidCredentialsError("Invalid username or password.")
        
    def _check_credentials(self,email:str,password:str):
        user = self._get_user(email)            
        if not user.verify_password(password):
            raise InvalidCredentialsError("Invalid username or password.")
        return user

    def execute(self, command: LoginCommand) -> LoginResponseDto:
       
        user = self._check_credentials(command.email,command.password)
        # Generate tokens
        access_token = self._uow.jwt_manager.create_access_token(user)
        refresh_token = self._uow.jwt_manager.create_refresh_token(user)

        return LoginResponseDto(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            email=user.email.address
        )