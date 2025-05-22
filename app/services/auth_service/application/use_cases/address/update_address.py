from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.services.auth_service.domain.entities.address_entity import AddressEntity
from app.services.auth_service.domain.value_objects.address import Address as AddressVO
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork

@dataclass
class UpdateAddressCommand:
    id: UUID
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    building_number: Optional[str] = None
    apartment_number: Optional[str] = None
    additional_info: Optional[str] = None
    is_active: Optional[bool] = None

class UpdateAddressUseCase:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, command: UpdateAddressCommand) -> AddressEntity:
        """
        Update an existing address.
        
        Raises:
            ValueError: If the address is not found
            ValueError: If the address validation fails
            ValueError: If trying to update an inactive address
        """
        async with self._uow:
            # Get existing address
            existing_address = await self._uow.addresses.get_by_id(command.id)
            if not existing_address:
                raise ValueError(f"Address with id {command.id} not found")
            
            if not existing_address.is_active:
                raise ValueError(f"Cannot update inactive address with id {command.id}")

            # Create new value object with updated fields
            address_vo = AddressVO(
                street=command.street or existing_address.address.street,
                city=command.city or existing_address.address.city,
                state=command.state or existing_address.address.state,
                country=command.country or existing_address.address.country,
                postal_code=command.postal_code or existing_address.address.postal_code,
                building_number=command.building_number if command.building_number is not None 
                    else existing_address.address.building_number,
                apartment_number=command.apartment_number if command.apartment_number is not None 
                    else existing_address.address.apartment_number,
                additional_info=command.additional_info if command.additional_info is not None 
                    else existing_address.address.additional_info
            )

            # Create updated entity
            updated_address = AddressEntity(
                id=existing_address.id,
                address=address_vo,
                user_id=existing_address.user_id,
                health_care_center_id=existing_address.health_care_center_id,
                is_active=command.is_active if command.is_active is not None 
                    else existing_address.is_active
            )

            # Update address
            result = await self._uow.addresses.update(updated_address)
            await self._uow.commit()

            return result

    async def deactivate(self, address_id: UUID) -> None:
        """
        Deactivate an address.
        
        Raises:
            ValueError: If the address is not found
            ValueError: If the address is already inactive
        """
        async with self._uow:
            existing_address = await self._uow.addresses.get_by_id(address_id)
            if not existing_address:
                raise ValueError(f"Address with id {address_id} not found")
            
            if not existing_address.is_active:
                raise ValueError(f"Address with id {address_id} is already inactive")

            deactivated_address = existing_address.deactivate()
            await self._uow.addresses.update(deactivated_address)
            await self._uow.commit()
