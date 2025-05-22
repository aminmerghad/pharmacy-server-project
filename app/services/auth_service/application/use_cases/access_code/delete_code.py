from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.services.auth_service.application.commands.access_code.delete_access_code_command import DeleteAccessCodeCommand
from app.services.auth_service.domain.exceptions.access_code_errors import AccessCodeNotFoundError
from app.services.auth_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork

@dataclass
class DeleteAccessCodeOutputDTO:
    """Output DTO for access code deletion"""
    id: Optional[UUID]
    code: str
    message: str
    success: bool

class DeleteAccessCodeUseCase:
    def __init__(self, uow: SQLAlchemyUnitOfWork):
        self._uow = uow

    def execute(self, command: DeleteAccessCodeCommand) -> DeleteAccessCodeOutputDTO:
        """Execute the use case to delete an access code"""
        
        # Get access code by code string
        access_code = self._uow.access_code.get_by_code(command.code)
        if not access_code:
            return DeleteAccessCodeOutputDTO(
                id=None,
                code=command.code,
                message="Access code not found",
                success=False
            )
        
        # Deactivate the access code (soft delete)
        deactivated_code = access_code.deactivate()
        result = self._uow.access_code.update(deactivated_code)
        self._uow.commit()
        
        # Return output DTO
        return DeleteAccessCodeOutputDTO(
            id=result.id,
            code=result.code,
            message="Access code successfully deactivated",
            success=True
        ) 