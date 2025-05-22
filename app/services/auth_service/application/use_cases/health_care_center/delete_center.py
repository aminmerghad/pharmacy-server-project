from dataclasses import dataclass
from uuid import UUID

from app.services.auth_service.domain.exceptions.health_care_center_errors import HealthCareCenterNotFoundError
from app.services.auth_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork

@dataclass
class DeleteHealthCareCenterOutputDto:
    """Output DTO for health care center deletion/deactivation"""
    id: UUID
    name: str
    is_active: bool
    message: str

class DeleteHealthCareCenterUseCase:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    def execute(self, center_id: UUID) -> DeleteHealthCareCenterOutputDto:
        """Execute the use case to deactivate a health care center"""
        
        # Get center by ID
        center = self._uow.health_care_center.get_by_id(center_id)
        if not center:
            raise HealthCareCenterNotFoundError(f"Health care center with ID {center_id} not found")
        
        # Check if already inactive
        if not center.is_active:
            return DeleteHealthCareCenterOutputDto(
                id=center.id,
                name=center.name,
                is_active=False,
                message="Health care center was already inactive"
            )
        
        # Deactivate center
        deactivated_center = center.deactivate()
        result = self._uow.health_care_center.update(deactivated_center)
        self._uow.commit()
        
        # Return output DTO
        return DeleteHealthCareCenterOutputDto(
            id=result.id,
            name=result.name,
            is_active=False,
            message="Health care center successfully deactivated"
        ) 