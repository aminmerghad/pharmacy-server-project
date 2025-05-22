from dataclasses import dataclass
from uuid import UUID
from app.services.auth_service.application.commands import CreateOrGetHealthCareCenterCommand
from app.services.auth_service.domain.entities import HealthCareCenterEntity
from app.services.auth_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork

@dataclass
class CreateHealthCareCenterOutputDto:
    id: UUID
    name: str
    address: str
    phone: str
    email: str
    license_number: str
    is_active: bool

class CreateHealthCareCenterUseCase:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    def execute(self, command: CreateOrGetHealthCareCenterCommand) -> CreateHealthCareCenterOutputDto:
        
            # Check if center with same email exists
            # existing_center = self._uow.health_care_center.get_by_email(command.email)
            # if existing_center:
            #     raise HealthCareCenterError("Health care center with this email already exists")

        center_entity = HealthCareCenterEntity(
                id=None,
                name=command.name,
                address=command.address,
                phone=command.phone,
                email=command.email,
                license_number=command.license_number
            )
            
        created_center = self._uow.health_care_center.add(center_entity)
        return CreateHealthCareCenterOutputDto(
                id=created_center.id,
                name=created_center.name,
                address=created_center.address,
                phone=created_center.phone,
                email=created_center.email,
                license_number=created_center.license_number,
                is_active=created_center.is_active
            )
        