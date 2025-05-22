from uuid import UUID
from app.services.inventory_service.application.commands.received_stock_command import ReceivedStockCommand
from app.services.inventory_service.application.events.stock_received_event import StockReceived
from app.services.inventory_service.application.use_cases.receive_stock.output_dto import ReceivedStockOutputDto
from app.services.inventory_service.domain.entities.inventory_entity import InventoryEntity
from app.services.inventory_service.domain.exceptions.inventory_errors import InventoryNotFoundError
from app.services.inventory_service.domain.interfaces.unit_of_work import UnitOfWork
class ReceiveStockUseCase :
    def __init__(self,uow:UnitOfWork):
        self._uow=uow
    def execute(self,command:ReceivedStockCommand) -> ReceivedStockOutputDto:
        

        entity = self._get_inventory_or_raise(command.product_id)
        
        entity.receive_stock(command.quantity)
        
        entity=self.update_inventory(entity)
        return ReceivedStockOutputDto(
                product_id=entity.product_id,
                quantity=entity.quantity                
            )
        # try:    
        #     entity=InventoryEntity(
        #         id=None,
        #         product_id=command.product_id,
        #         quantity=command.quantity
        #     )
        #     self._uow.inventory.add(entity)

        #     event=StockReceived(
        #     product_id=entity.product_id,
        #     quantity=entity.quantity
        #     )
        
        #     self._uow.publish(event)

        #     self._uow.commit()
        #     return ReceivedStockOutputDto(
        #      product_id=entity.product_id,
        #     quantity=entity.quantity)
        # except Exception as e:
        #     self._uow.rollback()
        #     raise e
    def _get_inventory_or_raise(self, product_id: UUID) -> InventoryEntity:
        """
        Get inventory or raise appropriate error.
        
        Args:
            product_id: The product ID to look up
            
        Returns:
            The inventory entity if found
            
        Raises:
            InventoryNotFoundError: If inventory not found for product
        """
        inventory = self._uow.inventory_repository.get_by_product_id(product_id)
        if not inventory:
            raise InventoryNotFoundError(
                f"Inventory for product {product_id} not found",
                error={"product_id": str(product_id)}
            )
        return inventory
    def update_inventory(self, entity):
        entity=self._uow.inventory_repository.update(entity)
        self._uow.commit()
        return entity
