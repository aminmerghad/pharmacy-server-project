from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from app.services.auth_service.application.commands import CreateUserCommand
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.auth_service.domain.entities import UserEntity
from app.services.auth_service.domain.value_objects import Email,Password
from app.shared.infrastructure.db_error_handler import DatabaseErrorHandler

@dataclass
class CreateUserResponseDto:
    id:UUID
    username: str
    email: str
    full_name: str
    phone: str
    created_at: datetime

class CreateUserUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    """
        # except IntegrityError as e:
        #     if 'unique constraint' in str(e).lower():
        #         if 'email' in str(e).lower():
        #             raise UserAlreadyExistsError(f"User with email {command.email} already exists")
        #         if 'username' in str(e).lower():
        #             raise UserAlreadyExistsError(f"Username {command.username} is already taken")
        #         if 'phone' in str(e).lower():
        #             raise UserAlreadyExistsError(f"Phone number {command.phone} is already registered")
        #     raise DatabaseError("Database integrity error occurred") from e
        # except SQLAlchemyError as e:
        #     self.uow.rollback()
        #     raise DatabaseError("An unexpected database error occurred") from e
    """
    
    @DatabaseErrorHandler.handle_db_operation()    
    def execute(self, command: CreateUserCommand):
        user = self.uow.user.add(UserEntity(            
                email=Email(command.email),
                password=Password(command.password),
                username=command.username,
                full_name=command.full_name,
                phone=command.phone
            ))
        
        return CreateUserResponseDto(
            id=user.id,
            username=user.username,
            email=user.email.address,
            full_name=user.full_name,
            phone=user.phone,
            created_at=user.created_at
        )
        



