from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from ...dtos.address_dtos import AddressListDTO
from ....infrastructure.query_services.address_query_service import AddressQueryService

@dataclass
class ListAddressesQuery:
    user_id: Optional[UUID] = None
    health_care_center_id: Optional[UUID] = None
    search_term: Optional[str] = None
    skip: int = 0
    limit: int = 50

class ListAddressesQueryHandler:
    def __init__(self, query_service: AddressQueryService):
        self._query_service = query_service

    async def execute(self, query: ListAddressesQuery) -> List[AddressListDTO]:
        """
        List addresses based on query parameters.
        
        Args:
            query: The query parameters including filters and pagination
            
        Returns:
            List of address DTOs matching the query criteria
            
        Note:
            - If user_id is provided, returns addresses for that user
            - If health_care_center_id is provided, returns addresses for that center
            - If search_term is provided, performs a search across all addresses
            - If no specific filter is provided, returns empty list
        """
        if query.user_id:
            return await self._query_service.list_addresses_by_user(
                user_id=query.user_id,
                skip=query.skip,
                limit=query.limit
            )
        
        if query.health_care_center_id:
            return await self._query_service.list_addresses_by_center(
                center_id=query.health_care_center_id,
                skip=query.skip,
                limit=query.limit
            )
        
        if query.search_term:
            return await self._query_service.search_addresses(
                search_term=query.search_term,
                skip=query.skip,
                limit=query.limit
            )
        
        # If no specific filter is provided, return empty list
        # This is a business decision - we don't want to accidentally
        # return all addresses when no filter is specified
        return []
