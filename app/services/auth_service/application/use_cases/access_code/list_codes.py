from app.services.auth_service.application.dtos.access_code_dtos import PaginatedAccessCodeListDTO
from app.services.auth_service.application.queries.access_code.list_access_codes_query import ListAccessCodesQuery
from app.services.auth_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
from app.services.auth_service.infrastructure.query_services.access_code_query_service import AccessCodeQueryService

class ListAccessCodesUseCase:
    def __init__(self, uow: SQLAlchemyUnitOfWork, access_code_query_service: AccessCodeQueryService):
        self._uow = uow
        self._access_code_query_service = access_code_query_service

    def execute(self, query: ListAccessCodesQuery) -> PaginatedAccessCodeListDTO:
        """List access codes with filtering and pagination"""
        return self._access_code_query_service.list_access_codes(query) 