from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.services.auth_service.application.commands import AssignUserToCenterCommand, RegisterUserCommand, CreateOrGetHealthCareCenterCommand, CreateUserCommand, ConsumeAccessCodeCommand
from app.services.auth_service.application.queries import AccessCodeValidationQuery
from app.services.auth_service.application.use_cases import CreateUserUseCase, AssignUserToCenterUseCase, ConsumeAccessCodeUseCase, CreateHealthCareCenterUseCase
from app.services.auth_service.domain.aggregators.access_code_aggregator import AccessCodeAggregator
from app.services.auth_service.domain.entities import AccessCodeEntity, HealthCareCenterEntity
from app.services.auth_service.domain.exceptions.access_code_errors import AccessCodeInactiveError, AccessCodeNotFoundError, AccessCodeUsedError
from app.services.auth_service.domain.exceptions.health_care_center_errors import HealthCareCenterError
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.auth_service.infrastructure.query_services.access_code_query_service import AccessCodeQueryService
from app.services.auth_service.infrastructure.query_services.health_care_center_query_service import HealthCareCenterQueryService


class HealthCareCenterDto(BaseModel):
    id: str
    name: str
    address: str
    phone: str
    email: str
    license_number: str

class UserInfoDto(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: str
    phone: str
    created_at: datetime
    code: str = None
    health_care_center: HealthCareCenterDto = None

    def final_update(self, code: str, health_care_center: Optional[HealthCareCenterDto] = None):
        self.code = code
        self.health_care_center = health_care_center


class RegisterUserUseCase:
    """Use case for registering a new user"""
    
    def __init__(self, uow: UnitOfWork, access_code_query_service: AccessCodeQueryService):
        self._uow = uow
        self._access_code_query_service = access_code_query_service
        self._create_user_use_case = None
        self._consume_access_code_use_case = None
        self._assign_user_to_center_use_case = None
        self._create_health_care_center_use_case = None
        self._initialize_use_cases()
        
    def _initialize_use_cases(self):
        self._create_user_use_case = CreateUserUseCase(self._uow)
        self._consume_access_code_use_case = ConsumeAccessCodeUseCase(self._uow)
        self._assign_user_to_center_use_case = AssignUserToCenterUseCase(self._uow)
        self._create_health_care_center_use_case = CreateHealthCareCenterUseCase(self._uow)
        
    def execute(self, command: RegisterUserCommand):

        # Validate access code
        validationDto = self._validate_access_code(command.access_code_query)

        
        # Get access code        
        access_code_aggregator = self._get_access_code(validationDto.access_code_entity)
        
        # Create user
        userInfoDto = self._create_user(command.user_command)
        
        # Consume access code
        self._consume_access_code(access_code_aggregator.access_code, userInfoDto.id)      
        # Get or create health care center
        centerInfoDto = self._get_or_create_health_care_center(access_code_aggregator, command.center_command)
        
        # Assign user to healthcare center
        if centerInfoDto:
            self._assign_user_to_center(userInfoDto.id, centerInfoDto.id)
        
        # Commit transaction
        self._uow.commit()

        # Final update
        userInfoDto.final_update(access_code_aggregator.access_code.code, centerInfoDto)

        return userInfoDto
    

    def _validate_access_code(self, access_code_query: AccessCodeValidationQuery):
        validationDto = self._access_code_query_service.validate_access_code(access_code_query)
        if not validationDto.access_code_entity:
            raise AccessCodeNotFoundError()
        if not validationDto.access_code_entity.is_active:
            raise AccessCodeInactiveError()
        if validationDto.access_code_entity.is_used:
            raise AccessCodeUsedError()
        # if not validationDto.is_valid:
        #     raise AccessCodeUnknownError()
        return validationDto

    def _create_user(self, user_register_command: CreateUserCommand) -> UserInfoDto:
        userInfoDto = self._create_user_use_case.execute(user_register_command)
        return UserInfoDto(
            id=userInfoDto.id,
            username=userInfoDto.username,
            email=userInfoDto.email,
            full_name=userInfoDto.full_name,
            phone=userInfoDto.phone,
            created_at=userInfoDto.created_at
        )

    def _get_access_code(self, access_code: AccessCodeEntity) -> AccessCodeAggregator:
        health_care_center = None
        if access_code.health_care_center_id:
            health_care_center = self._uow.health_care_center.get_by_id(access_code.health_care_center_id)
        return AccessCodeAggregator(
            access_code=access_code,
            health_care_center=health_care_center
        )

    def _consume_access_code(self, access_code: AccessCodeEntity, user_id: UUID) -> None:
        self._consume_access_code_use_case.execute(
            ConsumeAccessCodeCommand(
                access_code=access_code,
                used_by=user_id
            )
        )

    def _get_or_create_health_care_center(self,
                                          access_code_aggregator: AccessCodeAggregator,
                                          create_health_care_center_command: Optional[CreateOrGetHealthCareCenterCommand] = None
                                         ) -> Optional[HealthCareCenterEntity]:
        # If health care center is already associated with access code, return it
       
        if access_code_aggregator.health_care_center:
            return access_code_aggregator.health_care_center
        if create_health_care_center_command:
            return self._create_health_care_center_use_case.execute(create_health_care_center_command)
        return None
        
    def _assign_user_to_center(self, user_id: UUID, center_id: UUID) -> None:
        self._assign_user_to_center_use_case.execute(
            AssignUserToCenterCommand(
                user_id=user_id,
                center_id=center_id
            )
        )
     