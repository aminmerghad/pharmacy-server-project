from app.services.auth_service.application.dtos.access_code_dtos import AccessCodeValidationOutputDTO
from app.services.auth_service.application.queries.access_code.validate_access_code_query import ValidateAccessCodeQuery
from app.services.auth_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
from app.services.auth_service.infrastructure.query_services.access_code_query_service import AccessCodeQueryService

class ValidateAccessCodeUseCase:
    def __init__(self, uow: SQLAlchemyUnitOfWork, access_code_query_service: AccessCodeQueryService):
        self._uow = uow
        self._access_code_query_service = access_code_query_service

    def execute(self, query: ValidateAccessCodeQuery) -> AccessCodeValidationOutputDTO:
        """Validate an access code"""
        return self._access_code_query_service.validate_access_code(query)
        


