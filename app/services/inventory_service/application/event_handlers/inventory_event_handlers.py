from datetime import datetime
import logging
from uuid import UUID

from app.services.inventory_service.application.commands.record_movement_command import RecordMovementCommand
from app.services.inventory_service.application.events.inventory_create_requested_event import InventoryCreateRequestedEvent
from app.services.inventory_service.application.events.inventory_update_requested_event import InventoryUpdateRequestedEvent
from app.services.inventory_service.application.events.stock_received_event import StockReceived
from app.services.inventory_service.application.events.stock_release_requested_event import StockReleaseRequestedEvent
from app.services.inventory_service.application.use_cases.record_movement.record_movement import RecordMovementUseCase
from app.services.inventory_service.domain.entities.inventory_entity import InventoryEntity
from app.services.inventory_service.domain.enums.movement_type import MovementType
from app.services.inventory_service.domain.interfaces.unit_of_work import UnitOfWork
from app.shared.contracts.inventory.stock_check import StockItemValidationContract

        
logger = logging.getLogger(__name__)

class InventoryEventHandler:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
        
    def handle_stock_received(self, event: StockReceived):
        pass
        # self._uow.inventory.add(event)
        # self._uow.commit()

    def handle_inventory_create_requested(self, event: InventoryCreateRequestedEvent) -> None:        
        inventory_data = event.model_dump()  # Assuming event has a method to serialize its data
        inventory_entity = InventoryEntity(**inventory_data)  # Create an InventoryEntity from the event data      
        self._uow.inventory_repository.add(inventory_entity)  # Add the inventory entity to the unit of work
        logger.info(f"Inventory created successfully for product ID: {inventory_entity.product_id}")
    def handle_inventory_update_requested(self,event:InventoryUpdateRequestedEvent):
        inventory_data = event.model_dump()  
        
        inventory_entity = InventoryEntity(**inventory_data)
        
        self._uow.inventory_repository.update(inventory_entity)
        logger.info(f"Inventory updated successfully for product ID: {inventory_entity.product_id}")
            
    def handle_stock_release_requested(self, event: StockReleaseRequestedEvent):
        """
        Handle stock release request from order service.
        Process each item to check stock availability and release if possible.
        Publishes a result event indicating success or failure.
        
        Args:
            event: StockReleaseRequestedEvent containing order_id and items
        """
        order_id = event.order_id
        all_items_processed = True
        processed_items = []
        try:
                
            # with self._uow:
                for item in event.items:
                    product_id = item['product_id']
                    quantity = item['quantity']
                    item_result = self._process_stock_release_item(product_id, quantity, order_id)
                    processed_items.append(item_result)
                    
                    # if not item_result['success']:
                    #     all_items_processed = False
               
                

                # If any item failed, we need to rollback any already processed items
                if not all_items_processed:
                    
                    self._uow.rollback()
                    # Publish failure event
                    # self._uow.publish_event(StockReleaseProcessedEvent(
                    #     order_id=order_id,
                    #     success=False,
                    #     items=processed_items
                    # ))
                else:
                    self._uow.commit()
                    # Publish success event
                    # self._uow.publish_event(StockReleaseProcessedEvent(
                    #     order_id=order_id,
                    #     success=True,
                    #     items=processed_items
                    # ))
        except Exception as e:
            self._uow.rollback()
            # Publish failure event with error
            # self._uow.publish_event(StockReleaseProcessedEvent(
            #     order_id=order_id,
            #     success=False,
            #     items=[{
            #         'product_id': item['product_id'],
            #         'quantity': item['quantity'],
            #         'success': False,
            #         'message': str(e)
            #     } for item in event.items]
            # ))
            
    def _process_stock_release_item(self, product_id: UUID, quantity: int, order_id: str) -> dict:
        """
        Process a single item from the stock release request.
        
        Args:
            product_id: The ID of the product
            quantity: The quantity to release
            order_id: The ID of the related order
            
        Returns:
            Dictionary with processing result
        """
        try:
            # Get inventory item for the product
            inventory_item = self._uow.inventory_repository.get_by_product_id(
                UUID(product_id))
            
            inventory_item.quantity = inventory_item.quantity-quantity

            self._uow.inventory_repository.update(
                inventory_item
            )            
            
            # # Create movement command
            # command = RecordMovementCommand(
            #     inventory_id=str(inventory_item.id),
            #     quantity=quantity,
            #     movement_type=MovementType.OUT.value,
            #     reference_id=order_id,
            #     reference_type="order",
            #     notes=f"Stock release for order {order_id}"
            # )
            
            # # Record the movement using the use case
            # movement_use_case = RecordMovementUseCase(self._uow)
            # movement_use_case.execute(command)
            
            return {
                'product_id': product_id,
                'quantity': quantity,
                'success': True,
                'message': 'Stock released successfully'
            }
            
        except Exception as e:
            return {
                'product_id': product_id,
                'quantity': quantity,
                'success': False,
                'message': str(e)
            }