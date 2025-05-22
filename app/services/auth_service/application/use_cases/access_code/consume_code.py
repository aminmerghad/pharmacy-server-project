from app.services.auth_service.application.commands import ConsumeAccessCodeCommand
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork


class ConsumeAccessCodeUseCase:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def execute(self, command: ConsumeAccessCodeCommand):
        access_code_entity = command.access_code
        access_code_entity.mark_as_used()
        self._uow.access_code.update(access_code_entity)

        return None



