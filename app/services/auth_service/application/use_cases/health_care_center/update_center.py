from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.services.auth_service.application.commands.health_care_center.update_center_command import UpdateHealthCareCenterCommand
from app.services.auth_service.domain.exceptions.health_care_center_errors import HealthCareCenterNotFoundError, DuplicateHealthCareCenterError
from app.services.auth_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork

@dataclass
class UpdateHealthCareCenterOutputDto:
    """Output DTO for health care center update"""
    id: UUID
    name: str
    address: str
    phone: str
    email: str
    license_number: str
    is_active: bool

class UpdateHealthCareCenterUseCase:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    def execute(self, command: UpdateHealthCareCenterCommand) -> UpdateHealthCareCenterOutputDto:
        """Execute the use case to update a health care center"""
        
        # Get existing center
        center = self._uow.health_care_center.get_by_id(command.id)
        if not center:
            raise HealthCareCenterNotFoundError(f"Health care center with ID {command.id} not found")
        
        # If email is being updated, check uniqueness
        if command.email and command.email != center.email:
            existing_center = self._uow.health_care_center.get_by_email(command.email)
            if existing_center:
                raise DuplicateHealthCareCenterError(f"Health care center with email {command.email} already exists")
        
        # If license number is being updated, check uniqueness
        if command.license_number and command.license_number != center.license_number:
            existing_center = self._uow.health_care_center.get_by_license_number(command.license_number)
            if existing_center:
                raise DuplicateHealthCareCenterError(f"Health care center with license number {command.license_number} already exists")
        
        # Update center properties
        updated_center = center.update(
            name=command.name,
            address=command.address,
            phone=command.phone,
            email=command.email,
            license_number=command.license_number
        )
        
        # If is_active is provided and different from current value, update it
        if command.is_active is not None and command.is_active != center.is_active:
            if command.is_active:
                # Activate
                updated_center = updated_center.update(is_active=True)
            else:
                # Deactivate
                updated_center = updated_center.deactivate()
        
        # Save changes
        result = self._uow.health_care_center.update(updated_center)
        self._uow.commit()
        
        # Return output DTO
        return UpdateHealthCareCenterOutputDto(
            id=result.id,
            name=result.name,
            address=result.address,
            phone=result.phone,
            email=result.email,
            license_number=result.license_number,
            is_active=result.is_active
        )

    
