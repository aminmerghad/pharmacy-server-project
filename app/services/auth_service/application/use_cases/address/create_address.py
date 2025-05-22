from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4

from ....domain.entities.address_entity import AddressEntity
from ....domain.value_objects.address import Address as AddressVO
from ....domain.interfaces.unit_of_work import UnitOfWork

@dataclass
class CreateAddressCommand:
    street: str
    city: str
    state: str
    country: str
    postal_code: str
    building_number: Optional[str] = None
    apartment_number: Optional[str] = None
    additional_info: Optional[str] = None
    user_id: Optional[UUID] = None
    health_care_center_id: Optional[UUID] = None

class CreateAddressUseCase:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, command: CreateAddressCommand) -> AddressEntity:
        """
        Create a new address for either a user or a health care center.
        
        Raises:
            ValueError: If neither user_id nor health_care_center_id is provided,
                      or if both are provided.
            ValueError: If the address validation fails.
        """
        # Validate owner assignment
        if not command.user_id and not command.health_care_center_id:
            raise ValueError("Address must be associated with either a user or a health care center")
        
        if command.user_id and command.health_care_center_id:
            raise ValueError("Address cannot be associated with both a user and a health care center")

        # Create value object (this will validate the address fields)
        address_vo = AddressVO(
            street=command.street,
            city=command.city,
            state=command.state,
            country=command.country,
            postal_code=command.postal_code,
            building_number=command.building_number,
            apartment_number=command.apartment_number,
            additional_info=command.additional_info
        )

        # Create entity
        address = AddressEntity(
            id=uuid4(),
            address=address_vo,
            user_id=command.user_id,
            health_care_center_id=command.health_care_center_id
        )

        async with self._uow:
            # If user_id is provided, verify user exists
            if command.user_id:
                user = await self._uow.users.get_by_id(command.user_id)
                if not user:
                    raise ValueError(f"User with id {command.user_id} not found")
                if not user.is_active:
                    raise ValueError(f"User with id {command.user_id} is not active")

            # If health_care_center_id is provided, verify center exists
            if command.health_care_center_id:
                center = await self._uow.health_care_centers.get_by_id(
                    command.health_care_center_id
                )
                if not center:
                    raise ValueError(
                        f"Health care center with id {command.health_care_center_id} not found"
                    )
                if not center.is_active:
                    raise ValueError(
                        f"Health care center with id {command.health_care_center_id} is not active"
                    )

            # Create address
            created_address = await self._uow.addresses.create(address)
            await self._uow.commit()

            return created_address
