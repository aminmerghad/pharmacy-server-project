from dataclasses import dataclass
from uuid import UUID

from app.services.auth_service.domain.exceptions.health_care_center_errors import HealthCareCenterNotFoundError
from app.services.auth_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork

@dataclass
class GetHealthCareCenterByIdOutputDto:
    """Output DTO for health care center retrieval"""
    id: UUID
    name: str
    address: str
    phone: str
    email: str
    license_number: str
    is_active: bool
    created_at: str = None
    updated_at: str = None

class GetHealthCareCenterByIdUseCase:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    def execute(self, center_id: UUID) -> GetHealthCareCenterByIdOutputDto:
        """Execute the use case to get a health care center by ID"""
        
        # Get center by ID
        center = self._uow.health_care_center.get_by_id(center_id)
        if not center:
            raise HealthCareCenterNotFoundError(f"Health care center with ID {center_id} not found")
        
        # Return output DTO
        return GetHealthCareCenterByIdOutputDto(
            id=center.id,
            name=center.name,
            address=center.address,
            phone=center.phone,
            email=center.email,
            license_number=center.license_number,
            is_active=center.is_active,
            created_at=center.created_at.isoformat() if center.created_at else None,
            updated_at=center.updated_at.isoformat() if center.updated_at else None
        ) 