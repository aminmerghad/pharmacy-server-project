from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.services.auth_service.application.queries.health_care.list_centers_query import ListCentersByFilterQuery
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork

from ...application.dtos.health_care_center_dtos import (
    HealthCareCenterDTO,
    HealthCareCenterDetailsDTO,
    HealthCareCenterListDTO,
    HealthCareCenterSummaryDTO,
    PaginatedHealthCareCenterListDTO
)
from ...application.dtos.address_dtos import AddressListDTO
from ...application.dtos.user_dtos import UserListDTO
from ..persistence.models.health_care_center_model import HealthCareCenterModel

class HealthCareCenterQueryService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    def list_centers_by_filter(self, query: ListCentersByFilterQuery) -> PaginatedHealthCareCenterListDTO:
        """
        List health care centers with filtering, search, and pagination
        """
        # Get all centers initially
        centers = self._uow.health_care_center.get_all()
        
        # Apply filters
        filtered_centers = []
        for center in centers:
            # Apply is_active filter
            if query.is_active is not None and center.is_active != query.is_active:
                continue
                
            # Apply name filter
            if query.name and query.name.lower() not in center.name.lower():
                continue
                
            # Apply email filter
            if query.email and query.email.lower() not in center.email.lower():
                continue
                
            # Apply license_number filter
            if query.license_number and query.license_number.lower() not in center.license_number.lower():
                continue
                
            # Apply search across multiple fields
            if query.search:
                search_term = query.search.lower()
                if (search_term not in center.name.lower() and 
                    search_term not in center.email.lower() and 
                    search_term not in center.license_number.lower() and
                    search_term not in center.address.lower()):
                    continue
                    
            # If all filters pass, include this center
            filtered_centers.append(center)
        
        # Sort results
        if query.sort_by:
            reverse = query.sort_order.lower() == "desc"
            if query.sort_by == "name":
                filtered_centers.sort(key=lambda c: c.name, reverse=reverse)
            elif query.sort_by == "email":
                filtered_centers.sort(key=lambda c: c.email, reverse=reverse)
            elif query.sort_by == "license_number":
                filtered_centers.sort(key=lambda c: c.license_number, reverse=reverse)
            elif query.sort_by == "created_at" and hasattr(filtered_centers[0], 'created_at'):
                filtered_centers.sort(key=lambda c: c.created_at, reverse=reverse)
        
        # Apply pagination
        total_count = len(filtered_centers)
        start_idx = (query.page - 1) * query.page_size
        end_idx = start_idx + query.page_size
        paginated_centers = filtered_centers[start_idx:end_idx]
        
        # Convert to DTOs
        items = [self._to_center_dto(center) for center in paginated_centers]
        
        # Return paginated response
        return {
            "items": items,
            "total": total_count,
            "page": query.page,
            "page_size": query.page_size,
            "pages": (total_count + query.page_size - 1) // query.page_size if query.page_size > 0 else 1
        }
        
    def _to_center_dto(self, center_entity) -> Dict[str, Any]:
        """Convert entity to DTO"""
        return {
            "id": str(center_entity.id),
            "name": center_entity.name,
            "address": center_entity.address,
            "phone": center_entity.phone,
            "email": center_entity.email,
            "license_number": center_entity.license_number,
            "is_active": center_entity.is_active,
            "created_at": center_entity.created_at.isoformat() if center_entity.created_at else None,
            "updated_at": center_entity.updated_at.isoformat() if center_entity.updated_at else None
        }

    # # async def get_center_by_id(
    # #     self, 
    # #     center_id: UUID
    # # ) -> Optional[HealthCareCenterDetailsDTO]:
    # #     stmt = (
    # #         select(HealthCareCenterModel)
    # #         .options(
    # #             joinedload(HealthCareCenterModel.addresses),
    # #             joinedload(HealthCareCenterModel.users)
    # #         )
    # #         .where(
    # #             HealthCareCenterModel.id == center_id,
    # #             HealthCareCenterModel.is_active == True
    # #         )
    # #     )
    # #     result = await self._session.execute(stmt)
    # #     model = result.unique().scalar_one_or_none()
    # #     return self._to_details_dto(model) if model else None

    
    # # async def search_centers(
    # #     self,
    # #     search_term: str,
    # #     skip: int = 0,
    # #     limit: int = 50
    # # ) -> List[HealthCareCenterListDTO]:
    # #     search_pattern = f"%{search_term}%"
    # #     stmt = (
    # #         select(HealthCareCenterModel)
    # #         .options(
    # #             joinedload(HealthCareCenterModel.addresses),
    # #             joinedload(HealthCareCenterModel.users)
    # #         )
    # #         .where(
    # #             HealthCareCenterModel.is_active == True,
    # #             (
    # #                 HealthCareCenterModel.name.ilike(search_pattern) |
    # #                 HealthCareCenterModel.description.ilike(search_pattern) |
    # #                 HealthCareCenterModel.license_number.ilike(search_pattern)
    # #             )
    # #         )
    # #         .offset(skip)
    # #         .limit(limit)
    # #     )
    # #     result = await self._session.execute(stmt)
    # #     return [self._to_list_dto(model) for model in result.scalars()]

    # # async def get_centers_by_type(
    # #     self,
    # #     center_type: str,
    # #     skip: int = 0,
    # #     limit: int = 50
    # # ) -> List[HealthCareCenterSummaryDTO]:
    # #     stmt = (
    # #         select(HealthCareCenterModel)
    # #         .options(
    # #             joinedload(HealthCareCenterModel.addresses),
    # #             joinedload(HealthCareCenterModel.users)
    # #         )
    # #         .where(
    # #             HealthCareCenterModel.is_active == True,
    # #             HealthCareCenterModel.center_type == center_type
    # #         )
    # #         .offset(skip)
    # #         .limit(limit)
    # #     )
    # #     result = await self._session.execute(stmt)
    # #     return [self._to_summary_dto(model) for model in result.scalars()]

    # def _to_dto(self, model: HealthCareCenterModel) -> HealthCareCenterDTO:
    #     """Convert database model to base DTO"""
    #     return HealthCareCenterDTO(
    #         id=model.id,
    #         name=model.name,
    #         description=model.description,
    #         center_type=model.center_type,
    #         license_number=model.license_number,
    #         is_active=model.is_active
    #     )

    # def _to_list_dto(self, model: HealthCareCenterModel) -> HealthCareCenterListDTO:
    #     """Convert database model to list DTO"""
    #     return HealthCareCenterListDTO(
    #         id=model.id,
    #         name=model.name,
    #         center_type=model.center_type,
    #         license_number=model.license_number,
    #         address_count=len(model.addresses),
    #         is_active=model.is_active
    #     )

    # def _to_summary_dto(self, model: HealthCareCenterModel) -> HealthCareCenterSummaryDTO:
    #     """Convert database model to summary DTO"""
    #     active_addresses = [addr for addr in model.addresses if addr.is_active]
    #     primary_address = self._address_to_dto(active_addresses[0]) if active_addresses else None
        
    #     return HealthCareCenterSummaryDTO(
    #         id=model.id,
    #         name=model.name,
    #         center_type=model.center_type,
    #         primary_address=primary_address,
    #         user_count=len([user for user in model.users if user.is_active]),
    #         is_active=model.is_active
    #     )

    # def _to_details_dto(self, model: HealthCareCenterModel) -> HealthCareCenterDetailsDTO:
    #     """Convert database model to detailed DTO including relationships"""
    #     base_dto = self._to_dto(model)
    #     return HealthCareCenterDetailsDTO(
    #         **base_dto.__dict__,
    #         address_count=len(model.addresses),
    #         user_count=len(model.users),
    #         addresses=[
    #             self._address_to_dto(addr) 
    #             for addr in model.addresses 
    #             if addr.is_active
    #         ],
    #         users=[
    #             self._user_to_dto(user) 
    #             for user in model.users 
    #             if user.is_active
    #         ]
    #     )

    # def _address_to_dto(self, model) -> AddressListDTO:
    #     """Convert address model to DTO"""
    #     return AddressListDTO(
    #         id=model.id,
    #         full_address=f"{model.street}, {model.city}",
    #         city=model.city,
    #         state=model.state,
    #         country=model.country,
    #         is_active=model.is_active
    #     )

    # def _user_to_dto(self, model) -> UserListDTO:
    #     """Convert user model to DTO"""
    #     return UserListDTO(
    #         id=model.id,
    #         name=model.name,
    #         email=model.email,
    #         role=model.role,
    #         is_active=model.is_active
    #     )
