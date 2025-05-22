from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.entities.address_entity import AddressEntity
from ....domain.value_objects.address import Address as AddressVO
from ..models.address_model import AddressModel

class AddressRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, address: AddressEntity) -> AddressEntity:
        address_model = AddressModel(
            id=address.id,
            street=address.address.street,
            city=address.address.city,
            state=address.address.state,
            country=address.address.country,
            postal_code=address.address.postal_code,
            building_number=address.address.building_number,
            apartment_number=address.address.apartment_number,
            additional_info=address.address.additional_info,
            user_id=address.user_id,
            health_care_center_id=address.health_care_center_id,
            is_active=address.is_active
        )
        self._session.add(address_model)
        await self._session.flush()
        return self._to_entity(address_model)

    async def get_by_id(self, address_id: UUID) -> Optional[AddressEntity]:
        stmt = select(AddressModel).where(AddressModel.id == address_id)
        result = await self._session.execute(stmt)
        address_model = result.scalar_one_or_none()
        return self._to_entity(address_model) if address_model else None

    async def get_by_user_id(self, user_id: UUID) -> List[AddressEntity]:
        stmt = select(AddressModel).where(
            AddressModel.user_id == user_id,
            AddressModel.is_active == True
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars()]

    async def get_by_center_id(self, center_id: UUID) -> List[AddressEntity]:
        stmt = select(AddressModel).where(
            AddressModel.health_care_center_id == center_id,
            AddressModel.is_active == True
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars()]

    async def update(self, address: AddressEntity) -> AddressEntity:
        stmt = select(AddressModel).where(AddressModel.id == address.id)
        result = await self._session.execute(stmt)
        address_model = result.scalar_one()
        
        # Update fields
        address_model.street = address.address.street
        address_model.city = address.address.city
        address_model.state = address.address.state
        address_model.country = address.address.country
        address_model.postal_code = address.address.postal_code
        address_model.building_number = address.address.building_number
        address_model.apartment_number = address.address.apartment_number
        address_model.additional_info = address.address.additional_info
        address_model.is_active = address.is_active
        
        await self._session.flush()
        return self._to_entity(address_model)

    async def delete(self, address_id: UUID) -> None:
        stmt = select(AddressModel).where(AddressModel.id == address_id)
        result = await self._session.execute(stmt)
        address_model = result.scalar_one()
        address_model.is_active = False
        await self._session.flush()

    def _to_entity(self, model: AddressModel) -> AddressEntity:
        """Convert database model to domain entity"""
        address_vo = AddressVO(
            street=model.street,
            city=model.city,
            state=model.state,
            country=model.country,
            postal_code=model.postal_code,
            building_number=model.building_number,
            apartment_number=model.apartment_number,
            additional_info=model.additional_info
        )
        
        return AddressEntity(
            id=model.id,
            address=address_vo,
            user_id=model.user_id,
            health_care_center_id=model.health_care_center_id,
            is_active=model.is_active
        )
