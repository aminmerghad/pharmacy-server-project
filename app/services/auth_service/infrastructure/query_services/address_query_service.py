from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ...application.dtos.address_dtos import AddressDTO, AddressDetailsDTO, AddressListDTO
from ..persistence.models.address_model import AddressModel

class AddressQueryService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_address_by_id(self, address_id: UUID) -> Optional[AddressDetailsDTO]:
        stmt = (
            select(AddressModel)
            .options(
                joinedload(AddressModel.user),
                joinedload(AddressModel.health_care_center)
            )
            .where(
                AddressModel.id == address_id,
                AddressModel.is_active == True
            )
        )
        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        return self._to_details_dto(model) if model else None

    async def list_addresses_by_user(
        self, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[AddressListDTO]:
        stmt = (
            select(AddressModel)
            .where(
                AddressModel.user_id == user_id,
                AddressModel.is_active == True
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._to_list_dto(model) for model in result.scalars()]

    async def list_addresses_by_center(
        self, 
        center_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[AddressListDTO]:
        stmt = (
            select(AddressModel)
            .where(
                AddressModel.health_care_center_id == center_id,
                AddressModel.is_active == True
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._to_list_dto(model) for model in result.scalars()]

    async def search_addresses(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[AddressListDTO]:
        search_pattern = f"%{search_term}%"
        stmt = (
            select(AddressModel)
            .where(
                AddressModel.is_active == True,
                (
                    AddressModel.street.ilike(search_pattern) |
                    AddressModel.city.ilike(search_pattern) |
                    AddressModel.state.ilike(search_pattern) |
                    AddressModel.country.ilike(search_pattern) |
                    AddressModel.postal_code.ilike(search_pattern)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._to_list_dto(model) for model in result.scalars()]

    def _to_dto(self, model: AddressModel) -> AddressDTO:
        """Convert database model to base DTO"""
        return AddressDTO(
            id=model.id,
            street=model.street,
            city=model.city,
            state=model.state,
            country=model.country,
            postal_code=model.postal_code,
            building_number=model.building_number,
            apartment_number=model.apartment_number,
            additional_info=model.additional_info,
            is_active=model.is_active
        )

    def _to_list_dto(self, model: AddressModel) -> AddressListDTO:
        """Convert database model to list DTO"""
        return AddressListDTO(
            id=model.id,
            full_address=f"{model.street}, {model.city}",
            city=model.city,
            state=model.state,
            country=model.country,
            is_active=model.is_active
        )

    def _to_details_dto(self, model: AddressModel) -> AddressDetailsDTO:
        """Convert database model to detailed DTO including relationships"""
        base_dto = self._to_dto(model)
        return AddressDetailsDTO(
            **base_dto.__dict__,
            user_id=model.user_id,
            user_name=model.user.name if model.user else None,
            health_care_center_id=model.health_care_center_id,
            health_care_center_name=model.health_care_center.name if model.health_care_center else None
        )
