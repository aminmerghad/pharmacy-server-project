from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ....domain.entities.user_entity import UserEntity
from ....domain.value_objects.email import Email
from ....domain.interfaces.unit_of_work import UnitOfWork

@dataclass
class UpdateUserCommand:
    id: UUID
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    health_care_center_id: Optional[UUID] = None
    is_active: Optional[bool] = None

class UpdateUserUseCase:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, command: UpdateUserCommand) -> UserEntity:
        """
        Update an existing user.
        
        Args:
            command: The command containing updated user details
            
        Returns:
            The updated user entity
            
        Raises:
            ValueError: If user not found
            ValueError: If email already exists
            ValueError: If validation fails
        """
        async with self._uow:
            # Get existing user
            existing_user = await self._uow.users.get_by_id(command.id)
            if not existing_user:
                raise ValueError(f"User with id {command.id} not found")

            # If email is being updated, check uniqueness and validate format
            email = None
            if command.email and command.email != str(existing_user.email):
                # Check uniqueness
                user_with_email = await self._uow.users.get_by_email(command.email)
                if user_with_email:
                    raise ValueError(f"Email {command.email} already exists")
                # Create and validate email value object
                email = Email(command.email)

            # If health care center is being updated, verify it exists
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

            # Create updated entity
            updated_user = existing_user.update_profile(
                name=command.name,
                email=email,
                role=command.role,
                health_care_center_id=command.health_care_center_id
            )

            # If deactivation is requested
            if command.is_active is False and existing_user.is_active:
                updated_user = updated_user.deactivate()

            # Save changes
            result = await self._uow.users.update(updated_user)
            await self._uow.commit()

            return result
