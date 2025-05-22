from uuid import UUID

from ....domain.interfaces.unit_of_work import UnitOfWork

class DeleteUserUseCase:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, user_id: UUID) -> None:
        """
        Delete (deactivate) a user.
        
        Args:
            user_id: The ID of the user to delete
            
        Raises:
            ValueError: If user not found
            ValueError: If user is already inactive
        """
        async with self._uow:
            # Get existing user
            existing_user = await self._uow.users.get_by_id(user_id)
            if not existing_user:
                raise ValueError(f"User with id {user_id} not found")
            
            if not existing_user.is_active:
                raise ValueError(f"User with id {user_id} is already inactive")

            # Deactivate user
            deactivated_user = existing_user.deactivate()
            await self._uow.users.update(deactivated_user)

            # Also deactivate all user's addresses
            user_addresses = await self._uow.addresses.get_by_user_id(user_id)
            for address in user_addresses:
                if address.is_active:
                    deactivated_address = address.deactivate()
                    await self._uow.addresses.update(deactivated_address)

            await self._uow.commit()
