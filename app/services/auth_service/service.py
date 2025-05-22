from app.services.auth_service.application.commands import LoginCommand,RegisterUserCommand,AdminRegistrationCommand,GenerateAccessCodeCommand
from app.services.auth_service.application.commands.health_care_center import create_center_command
from app.services.auth_service.application.commands.health_care_center.update_center_command import UpdateHealthCareCenterCommand
from app.services.auth_service.application.commands.health_care_center.delete_center_command import DeleteHealthCareCenterCommand
from app.services.auth_service.application.commands.access_code.delete_access_code_command import DeleteAccessCodeCommand
from app.services.auth_service.application.queries.health_care.list_centers_query import ListCentersByFilterQuery
from app.services.auth_service.application.queries.health_care.get_center_by_id_query import GetHealthCareCenterByIdQuery
from app.services.auth_service.application.queries.access_code.validate_access_code_query import ValidateAccessCodeQuery
from app.services.auth_service.application.queries.access_code.list_access_codes_query import ListAccessCodesQuery
from app.services.auth_service.application.use_cases.user.login_user import UserLoginUseCase
from app.services.auth_service.application.use_cases.token.refresh_token import RefreshTokenUseCase
from app.services.auth_service.application.use_cases.user.register_user import RegisterUserUseCase
from app.services.auth_service.application.use_cases.access_code.generate_code import GenerateAccessCodeUseCase
from app.services.auth_service.application.use_cases.access_code.validate_code import ValidateAccessCodeUseCase
from app.services.auth_service.application.use_cases.access_code.delete_code import DeleteAccessCodeUseCase
from app.services.auth_service.application.use_cases.access_code.list_codes import ListAccessCodesUseCase
from app.services.auth_service.application.use_cases.admin.register_admin import AdminRegisterUseCase
from app.services.auth_service.application.use_cases.health_care_center.create_center import CreateHealthCareCenterUseCase
from app.services.auth_service.application.use_cases.health_care_center.update_center import UpdateHealthCareCenterUseCase
from app.services.auth_service.application.use_cases.health_care_center.get_center_by_id import GetHealthCareCenterByIdUseCase
from app.services.auth_service.application.use_cases.health_care_center.delete_center import DeleteHealthCareCenterUseCase
from app.services.auth_service.infrastructure.query_services.access_code_query_service import AccessCodeQueryService
from app.services.auth_service.infrastructure.query_services.health_care_center_query_service import HealthCareCenterQueryService
from app.shared.domain.exceptions.common_errors import InitializeComponentsError
from app.services.auth_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
from app.services.auth_service.infrastructure.query_services.aurh_query_service import AuthQueryService
from app.shared.application.events.event_bus import EventBus
from app.dataBase import Database
from app.shared.infrastructure.db_error_handler import DatabaseErrorHandler

class AuthService:
    def __init__(self,db:Database,event_bus:EventBus):
        self._uow=None
        self._admin_register_use_case=None
        self._user_login_use_case=None
        self._refresh_token_use_case=None
        self._db_session=db.get_session()
        self._event_bus=event_bus
        self._auth_query_service=None
        self._access_code_query_service=None        
        self._init_resources()
        
    def _init_resources(self):
        try:            
            self._uow=SQLAlchemyUnitOfWork(self._db_session, self._event_bus)
            self._auth_query_service=AuthQueryService(self._uow)
            self._health_query_service=HealthCareCenterQueryService(self._uow)
            self._access_code_query_service=AccessCodeQueryService(self._uow)
            
            # User related use cases
            self._admin_register_use_case = AdminRegisterUseCase(self._uow)
            self._user_login_use_case = UserLoginUseCase(self._uow, self._auth_query_service)
            self._refresh_token_use_case= RefreshTokenUseCase(self._uow, self._auth_query_service)
            self._register_user_use_case = RegisterUserUseCase(self._uow, self._access_code_query_service)
            
            # Access code related use cases
            self._generate_access_code_use_case = GenerateAccessCodeUseCase(self._uow)
            self._validate_access_code_use_case = ValidateAccessCodeUseCase(self._uow, self._access_code_query_service)
            self._delete_access_code_use_case = DeleteAccessCodeUseCase(self._uow)
            self._list_access_codes_use_case = ListAccessCodesUseCase(self._uow, self._access_code_query_service)
            
            # Health care center related use cases
            self._create_health_care_center_use_case = CreateHealthCareCenterUseCase(self._uow)
            self._update_health_care_center_use_case = UpdateHealthCareCenterUseCase(self._uow)
            self._get_health_care_center_by_id_use_case = GetHealthCareCenterByIdUseCase(self._uow)
            self._delete_health_care_center_use_case = DeleteHealthCareCenterUseCase(self._uow)
        except Exception as e:
            raise InitializeComponentsError(f"Failed to initialize auth service: {str(e)}")
            
    @property
    def auth_query_service(self):
        return self._auth_query_service
        
    def register_admin(self, command: AdminRegistrationCommand):
        try:        
            return self._admin_register_use_case.execute(command)
        except Exception as e:            
            self._uow.rollback()
            raise e
            
    def login(self, command: LoginCommand):
        try:
            return self._user_login_use_case.execute(command)
        except Exception as e:
            self._uow.rollback()
            raise e
            
    def refresh_token(self):
        try:
            return self._refresh_token_use_case.execute()
        except Exception as e:
            self._uow.rollback()
            raise e
            
    def generate_access_code(self, command: GenerateAccessCodeCommand):
        """Generate a new access code for user registration"""
        try:
            return self._generate_access_code_use_case.execute(command)
        except Exception as e:
            self._uow.rollback()
            raise e
            
    def check_access_code_validation(self, code: str):
        """Check if an access code is valid"""
        try:
            query = ValidateAccessCodeQuery(code=code)
            return self._validate_access_code_use_case.execute(query)
        except Exception as e:
            raise e
            
    def delete_access_code(self, code: str):
        """Delete an access code"""
        try:
            command = DeleteAccessCodeCommand(code=code)
            return self._delete_access_code_use_case.execute(command)
        except Exception as e:
            self._uow.rollback()
            raise e
            
    def get_access_codes(self, query: ListAccessCodesQuery = None):
        """Get a list of access codes with optional filtering"""
        try:
            if not query:
                query = ListAccessCodesQuery()
            return self._list_access_codes_use_case.execute(query)
        except Exception as e:
            raise e
            
    @DatabaseErrorHandler.handle_service_operation()
    def register(self, command: RegisterUserCommand):
        return self._register_user_use_case.execute(command)
        
    def list_centers_by_filter(self, query: ListCentersByFilterQuery):
        return self._health_query_service.list_centers_by_filter(query)
        
    def create_health_care_center(self, command: create_center_command.CreateOrGetHealthCareCenterCommand):
        try:
            return self._create_health_care_center_use_case.execute(command)
        except Exception as e:
            self._uow.rollback()
            raise e
            
    def update_health_care_center(self, command: UpdateHealthCareCenterCommand):
        try:
            return self._update_health_care_center_use_case.execute(command)
        except Exception as e:
            self._uow.rollback()
            raise e
            
    def get_health_care_center(self, query: GetHealthCareCenterByIdQuery):
        try:
            return self._get_health_care_center_by_id_use_case.execute(query.id)
        except Exception as e:
            raise e
            
    def delete_health_care_center(self, command: DeleteHealthCareCenterCommand):
        try:
            return self._delete_health_care_center_use_case.execute(command.id)
        except Exception as e:
            self._uow.rollback()
            raise e




