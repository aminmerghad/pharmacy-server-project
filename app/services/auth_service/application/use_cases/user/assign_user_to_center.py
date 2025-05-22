from app.services.auth_service.application.commands import AssignUserToCenterCommand
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.auth_service.domain.exceptions.auth_errors import UserNotFoundError
from app.services.auth_service.domain.exceptions.health_care_center_errors import CenterNotFoundError

class AssignUserToCenterUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, command: AssignUserToCenterCommand):
        # Retrieve the user by ID
        user = self.uow.user.get_by_id(command.user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {command.user_id} not found")

        # Retrieve the health care center by ID
        center = self.uow.health_care_center.get_by_id(command.center_id)
        if not center:
            raise CenterNotFoundError(f"Health care center with ID {command.center_id} not found")

        user.health_care_center_id=center.id

        self.uow.user.update(user)     

       