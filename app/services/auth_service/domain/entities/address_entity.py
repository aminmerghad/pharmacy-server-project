from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ..value_objects.address import Address as AddressVO

@dataclass(frozen=True)
class AddressEntity:
    id: UUID
    address: AddressVO
    user_id: Optional[UUID] = None
    health_care_center_id: Optional[UUID] = None
    is_active: bool = True

    def belongs_to_user(self, user_id: UUID) -> bool:
        return self.user_id == user_id

    def belongs_to_center(self, center_id: UUID) -> bool:
        return self.health_care_center_id == center_id

    def deactivate(self) -> 'AddressEntity':
        return AddressEntity(
            id=self.id,
            address=self.address,
            user_id=self.user_id,
            health_care_center_id=self.health_care_center_id,
            is_active=False
        )

    def update_address(self, new_address: AddressVO) -> 'AddressEntity':
        return AddressEntity(
            id=self.id,
            address=new_address,
            user_id=self.user_id,
            health_care_center_id=self.health_care_center_id,
            is_active=self.is_active
        )
