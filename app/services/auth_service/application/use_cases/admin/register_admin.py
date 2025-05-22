from dataclasses import dataclass
from datetime import datetime
from app.config import Config
from app.services.auth_service.application.commands import AdminRegistrationCommand
from app.services.auth_service.domain.entities import UserEntity
from app.services.auth_service.domain.exceptions.auth_errors import AdminAlreadyExistsError, InvalidInitializationKey
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.auth_service.domain.value_objects import Email,Password



@dataclass
class AdminRegistrationDTO:
    id : str
    username : str
    email:str
    full_name:str
    phone:str
    created_at:datetime

    
class AdminRegisterUseCase:
    def __init__(self,uow:UnitOfWork):
        self._uow=uow
    
    def execute(self, command: AdminRegistrationCommand) -> AdminRegistrationDTO:
        # Check if admin already exists        
        self._check_existing_admin(command.username)

        #check if the initialization key is valid   
        self._check_init_key(command.initialization_key)         

        # Create admin user
        adminEntity= self._uow.user.add(UserEntity(
            username=command.username,
            password=Password(command.password),
            email=Email(command.email),
            full_name=command.full_name,
            phone=command.phone,
            is_active=True,
            is_admin=True
        ))
        

        self._uow.commit()
        return AdminRegistrationDTO(
            id=adminEntity.id,
            email=adminEntity.email.address,
            username=adminEntity.username,            
            full_name=adminEntity.full_name,
            phone=adminEntity.phone,
            created_at=adminEntity.created_at
        )
    def _check_init_key(self,initialization_key:str):
        if initialization_key != Config.ADMIN_INITIALIZATION_KEY:
            raise InvalidInitializationKey('the INIT_KEY provided is invalid')
    def _check_existing_admin(self,username:str):
        existing_admin = self._uow.user.is_existing_admin(username)            
        if existing_admin:
            raise AdminAlreadyExistsError(message='The admin already registred')



