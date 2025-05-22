import logging
from datetime import datetime
from typing import List, Optional, Dict, Tuple, Any
from uuid import UUID

from app.dataBase import Database
from app.services.inventory_service.application.commands.adjust_stock_command import AdjustStockCommand
from app.services.inventory_service.application.commands.received_stock_command import ReceivedStockCommand
from app.services.inventory_service.application.commands.record_movement_command import RecordMovementCommand
from app.services.inventory_service.application.event_handlers.inventory_event_handlers import InventoryEventHandler
from app.services.inventory_service.application.events.inventory_create_requested_event import InventoryCreateRequestedEvent
from app.services.inventory_service.application.events.inventory_update_requested_event import InventoryUpdateRequestedEvent
from app.services.inventory_service.application.events.stock_release_requested_event import StockReleaseRequestedEvent
from app.services.inventory_service.application.use_cases.adjust_stock.adjust_stock import AdjustStockUseCase
from app.services.inventory_service.application.use_cases.receive_stock.receive_stock import ReceiveStockUseCase
from app.services.inventory_service.application.use_cases.record_movement.record_movement import RecordMovementUseCase
from app.services.inventory_service.application.use_cases.stock_check import StockCheckUseCase
from app.services.inventory_service.domain.entities.stock_movement_entity import StockMovementEntity
from app.services.inventory_service.infrastructure.adapters.incoming.get_inventory_by_id import GetInventoryAdapter
from app.services.inventory_service.infrastructure.adapters.incoming.stock_check_adapter import StockCheckAdapter
from app.services.inventory_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
from app.services.inventory_service.infrastructure.query_services.inventory_query_service import InventoryQueryService
from app.shared.application.events.event_bus import EventBus
from app.shared.contracts.inventory.stock_check import StockCheckRequestContract, StockCheckResponseContract
from app.shared.acl.unified_acl import UnifiedACL, ServiceContext, ServiceResponse
from app.shared.domain.enums.enums import ServiceType
# from app.services.inventory_service.infrastructure.errors.database_error_handler import DatabaseErrorHandler
from http import HTTPStatus

# Configure logger
logger = logging.getLogger(__name__)

class InventoryService:
    def __init__(self, db: Database, event_bus: EventBus, 
                 acl: UnifiedACL = None):
        self._db_session = db.get_session()
        self._acl = acl
        self._event_bus = event_bus
        self._product_service_adapter = None
        self._init_resources()
        self._register_event_handlers()

    def _init_resources(self):
        self._uow = SQLAlchemyUnitOfWork(self._db_session,self._event_bus)
        self._stock_check_adapter = StockCheckAdapter(StockCheckUseCase(self._uow))
        self._inventory_query_service = InventoryQueryService(self._db_session,self._uow)
        self._receive_stock_use_case = ReceiveStockUseCase(self._uow)
        self._record_movement_use_case = RecordMovementUseCase(self._uow)
        self._adjust_stock_use_case = AdjustStockUseCase(self._uow)
        self._event_handler = InventoryEventHandler(self._uow)
        self._get_inventory_adapter = GetInventoryAdapter(self._inventory_query_service)

    def _register_event_handlers(self):
        """Register event handlers with the event bus."""
        # Register handler for StockReleaseRequestedEvent
        if self._event_bus:
            self._event_bus.subscribe(StockReleaseRequestedEvent, self._event_handler.handle_stock_release_requested)
            self._event_bus.subscribe(InventoryCreateRequestedEvent,self._event_handler.handle_inventory_create_requested)
            self._event_bus.subscribe(InventoryUpdateRequestedEvent,self._event_handler.handle_inventory_update_requested)
            

    def stock_check(self, request: StockCheckRequestContract) -> StockCheckResponseContract:
        return self._stock_check_adapter.stock_check(request) #stock check in api or external service inventory service
    
    def get_inventory_by_id(self,request):
        return self._get_inventory_adapter.get_inventory_by_id(request)
    
    
   
        
    # def receive_stock(self, command: ReceivedStockCommand):
    #     return self._receive_stock_use_case.execute(command)
    
    # def record_movement(self, command: RecordMovementCommand) -> StockMovementEntity:
    #     """
    #     Record a stock movement in the inventory system.
        
    #     This method handles various types of stock movements including:
    #     - Receiving stock from suppliers
    #     - Dispensing stock to customers
    #     - Adjusting stock levels
    #     - Recording damaged or expired stock
    #     - Transferring stock between locations
        
    #     Args:
    #         command: The command containing movement details
            
    #     Returns:
    #         The created stock movement entity
            
    #     Raises:
    #         ValueError: If the movement data is invalid
    #     """
    #     return self._record_movement_use_case.execute(command)
    
    # def get_inventory_movements(self, inventory_id: UUID) -> List[StockMovementEntity]:
    #     """
    #     Get all movements for a specific inventory item.
        
    #     Args:
    #         inventory_id: The UUID of the inventory item
            
    #     Returns:
    #         A list of stock movement entities
    #     """
    #     with self._uow:
    #         movements = self._uow.stock_movement_repository.get_by_inventory_id(inventory_id)
    #     return movements

    # def adjust_stock(self, command: AdjustStockCommand):
    #     """
    #     Adjust stock levels for an inventory item.
        
    #     This method allows for increasing or decreasing stock levels
    #     with proper tracking and validation.
        
    #     Args:
    #         command: The adjustment command with details about the adjustment
            
    #     Returns:
    #         Result of the adjustment operation
            
    #     Raises:
    #         InventoryNotFoundError: If the inventory item doesn't exist
    #         ValueError: If the adjustment would result in invalid stock levels
    #     """
    #     return self._adjust_stock_use_case.execute(command)

    # def get_low_stock_items(self, threshold_percentage: float = 100) -> List[Dict[str, Any]]:
    #     """
    #     Get inventory items with low stock levels.
        
    #     Args:
    #         threshold_percentage: Percentage of min_stock to use as threshold
    #                              (default 100% means at or below min_stock)
            
    #     Returns:
    #         List of inventory items with low stock, including product details
    #     """
    #     return self._inventory_query_service.get_low_stock_items(threshold_percentage)
    
    # def get_expiring_items(self, days_threshold: int = 90) -> List[Dict[str, Any]]:
    #     """
    #     Get inventory items that will expire within the given threshold.
        
    #     Args:
    #         days_threshold: Number of days to look ahead for expiring items
            
    #     Returns:
    #         List of inventory items that will expire within the threshold
    #     """
    #     return self._inventory_query_service.get_expiring_items(days_threshold)
    
    # def get_expired_items(self) -> List[Dict[str, Any]]:
    #     """
    #     Get inventory items that have already expired.
        
    #     Returns:
    #         List of expired inventory items
    #     """
    #     return self._inventory_query_service.get_expired_items()
    
    # def get_inventory_summary(self) -> Dict[str, Any]:
    #     """
    #     Get a summary of the current inventory status.
        
    #     Returns:
    #         Summary statistics about inventory status
    #     """
    #     return self._inventory_query_service.get_inventory_summary()

    # def transfer_stock(self, command: TransferStockCommand):
    #     """
    #     Transfer stock between locations.
        
    #     This method handles the transfer of stock from one location to another,
    #     recording both outgoing and incoming movements for proper tracking.
        
    #     Args:
    #         command: The transfer command with details about the transfer
            
    #     Returns:
    #         Result of the transfer operation
            
    #     Raises:
    #         InventoryNotFoundError: If the inventory item doesn't exist
    #         ValueError: If the transfer would result in invalid stock levels
    #                   or if locations are invalid
    #     """
    #     return self._transfer_stock_use_case.execute(command)

    # def write_off_inventory(self, command: WriteOffCommand):
    #     """
    #     Write off inventory due to expiry, damage, or other reasons.
        
    #     This method handles writing off inventory with proper tracking
    #     of the reason and movement type for audit purposes.
        
    #     Args:
    #         command: The write-off command with details
            
    #     Returns:
    #         Result of the write-off operation
            
    #     Raises:
    #         InventoryNotFoundError: If the inventory item doesn't exist
    #         ValueError: If the write-off would result in invalid stock levels
    #     """
    #     return self._write_off_use_case.execute(command)

    # def add_batch(self, command: AddBatchCommand) -> BatchEntity:
    #     """
    #     Add a new batch to an inventory item.
        
    #     This method handles adding a new batch with its own tracking information,
    #     updating the inventory quantity, and recording the appropriate movement.
        
    #     Args:
    #         command: The command containing batch details
            
    #     Returns:
    #         The created batch entity
            
    #     Raises:
    #         InventoryNotFoundError: If the inventory item doesn't exist
    #         ValueError: If the batch data is invalid
    #     """
    #     return self._add_batch_use_case.execute(command)
    
    # def get_batches_for_inventory(self, inventory_id: UUID) -> List[BatchEntity]:
    #     """
    #     Get all batches for a specific inventory item.
        
    #     Args:
    #         inventory_id: The ID of the inventory item
            
    #     Returns:
    #         List of batch entities for the inventory item
    #     """
    #     with self._uow:
    #         return self._uow.batch_repository.get_by_inventory_id(inventory_id)
    
    # def get_expiring_batches(self, days: int = 90) -> List[BatchEntity]:
    #     """
    #     Get all batches expiring within the specified number of days.
        
    #     Args:
    #         days: Number of days to look ahead
            
    #     Returns:
    #         List of batch entities expiring within the threshold
    #     """
    #     with self._uow:
    #         return self._uow.batch_repository.get_expiring_batches(days)
    
    # def get_expired_batches(self) -> List[BatchEntity]:
    #     """
    #     Get all expired batches that still have stock.
        
    #     Returns:
    #         List of expired batch entities
    #     """
    #     with self._uow:
    #         return self._uow.batch_repository.get_expired_batches()

    # def get_product_by_id(self, query: GetProductByIdQuery) -> Dict[str, Any]:
    #     """
    #     Get a product by its ID using the ACL
        
    #     Args:
    #         query: Query containing the product ID
            
    #     Returns:
    #         Dict containing the product data and status code
    #     """
    #     if self._acl:
    #         try:
    #             context = ServiceContext(
    #                 service_type=ServiceType.PRODUCT,
    #                 operation="GET_PRODUCT",
    #                 data={"product_id": query.product_id}
    #             )
    #             response = self._acl.execute_service_operation(context)
    #             if response.success:
    #                 return response.data, 200
    #             return {"error": response.error}, 404
    #         except Exception as e:
    #             logger.error(f"Error getting product through ACL: {str(e)}")
    #             return {"error": str(e)}, 500
    #     return {"error": "Product service unavailable"}, 503
    
    
    
                
    
    # def get_expiring_products_report(self, days_threshold: int = 90) -> Tuple[List[Dict[str, Any]], int]:
    #     """
    #     Get a report of products expiring within the specified number of days
        
    #     Args:
    #         days_threshold: Number of days to look ahead for expiring products
            
    #     Returns:
    #         Tuple containing the list of expiring products and HTTP status code
    #     """
    #     try:
    #         # This is still an inventory function, so we keep it
    #         # But we'll need to enhance it to fetch product details via the adapter
    #         expiring_items = self._inventory_query_service.get_expiring_items(days_threshold)
            
    #         # If we have a product service adapter, fetch product details for each item
    #         if self._acl:
    #             for item in expiring_items:
    #                 product_id = item.get('product_id')
    #                 if product_id:
    #                     product_info, _ = self.get_product_by_id(GetProductByIdQuery(product_id))
    #                     if product_info:
    #                         item['product'] = product_info
            
    #         return expiring_items, 200
    #     except Exception as e:
    #         return [], 500
    
    # def get_expired_products_report(self) -> Tuple[List[Dict[str, Any]], int]:
    #     """
    #     Get a report of products that have already expired
        
    #     Returns:
    #         Tuple containing the list of expired products and HTTP status code
    #     """
    #     try:
    #         # This is still an inventory function, so we keep it
    #         # But we'll need to enhance it to fetch product details via the adapter
    #         expired_items = self._inventory_query_service.get_expired_items()
            
    #         # If we have a product service adapter, fetch product details for each item
    #         if self._acl:
    #             for item in expired_items:
    #                 product_id = item.get('product_id')
    #                 if product_id:
    #                     product_info, _ = self.get_product_by_id(GetProductByIdQuery(product_id))
    #                     if product_info:
    #                         item['product'] = product_info
            
    #         return expired_items, 200
    #     except Exception as e:
    #         return [], 500
    
    # def get_inventory_value_report(self, category_id: Optional[UUID] = None, include_zero_stock: bool = False) -> Tuple[Dict[str, Any], int]:
    #     """
    #     Get a report of inventory value by product
        
    #     Args:
    #         category_id: Optional category ID to filter by
    #         include_zero_stock: Whether to include products with zero stock
            
    #     Returns:
    #         Tuple containing the inventory value report and HTTP status code
    #     """
    #     try:
    #         with self._uow as uow:
    #             # Get all products
    #             if category_id:
    #                 if self._acl:
    #                     products = self.get_products_by_filter(GetProductsByFilterQuery(category_id=category_id))
    #                 else:
    #                     products = [p for p in uow.products.get_all() if p.category_id == category_id]
    #             else:
    #                 if self._acl:
    #                     products = self.get_all_products()
    #                 else:
    #                     products = uow.products.get_all()
                
    #             report_items = []
    #             total_value = 0.0
                
    #             for product in products:
    #                 # Get inventory items for this product
    #                 inventory_items = uow.inventory.get_by_product_id(product.id)
                    
    #                 if not inventory_items:
    #                     if include_zero_stock:
    #                         report_items.append({
    #                             "product": {
    #                                 "id": str(product.id),
    #                                 "name": product.name,
    #                                 "sku": product.sku,
    #                                 "brand": product.brand
    #                             },
    #                             "quantity": 0,
    #                             "price": 0.0,
    #                             "total_value": 0.0
    #                         })
    #                     continue
                    
    #                 for item in inventory_items:
    #                     if item.quantity == 0 and not include_zero_stock:
    #                         continue
                            
    #                     price = float(item.price) if item.price else 0.0
    #                     item_value = item.quantity * price
    #                     total_value += item_value
                        
    #                     report_items.append({
    #                         "product": {
    #                             "id": str(product.id),
    #                             "name": product.name,
    #                             "sku": product.sku,
    #                             "brand": product.brand
    #                         },
    #                         "location_id": str(item.location_id) if item.location_id else None,
    #                         "quantity": item.quantity,
    #                         "price": price,
    #                         "total_value": item_value
    #                     })
                
    #             # Format response
    #             result = {
    #                 "items": report_items,
    #                 "summary": {
    #                     "total_items": len(report_items),
    #                     "total_value": total_value
    #                 }
    #             }
                
    #             return result, HTTPStatus.OK
                
    #     except Exception as e:
    #         self._logger.error(f"Error generating inventory value report: {str(e)}")
    #         return f"Error generating inventory value report: {str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR

    # def get_product_movement_history(self, product_id: UUID, 
    #                                  start_date: Optional[datetime] = None,
    #                                  end_date: Optional[datetime] = None, 
    #                                  movement_types: Optional[List[str]] = None) -> Tuple[Dict[str, Any], int]:
    #     """
    #     Get movement history for a specific product
        
    #     Args:
    #         product_id: UUID of the product
    #         start_date: Optional start date for filtering movements
    #         end_date: Optional end date for filtering movements
    #         movement_types: Optional list of movement types to filter by
            
    #     Returns:
    #         Tuple containing the movement history data and HTTP status code
    #     """
    #     try:
    #         with self._uow as uow:
    #             # Check if product exists
    #             if self._acl:
    #                 product = self.get_product_by_id(GetProductByIdQuery(product_id))
    #             else:
    #                 product = uow.products.get_by_id(product_id)
    #             if not product:
    #                 return f"Product with ID {product_id} not found", HTTPStatus.NOT_FOUND
                
    #             # Get inventory items for this product
    #             inventory_items = uow.inventory.get_by_product_id(product_id)
    #             if not inventory_items:
    #                 return {
    #                     "product": {
    #                         "id": str(product.id),
    #                         "name": product.name,
    #                         "sku": product.sku
    #                     },
    #                     "movements": [],
    #                     "total_in": 0,
    #                     "total_out": 0,
    #                     "current_stock": 0
    #                 }, HTTPStatus.OK
                
    #             # Get movements for each inventory item
    #             all_movements = []
    #             for item in inventory_items:
    #                 movements = uow.stock_movement_repository.get_by_inventory_id(item.id)
    #                 all_movements.extend(movements)
                
    #             # Filter by date if provided
    #             if start_date:
    #                 all_movements = [m for m in all_movements if m.created_at >= start_date]
    #             if end_date:
    #                 all_movements = [m for m in all_movements if m.created_at <= end_date]
                    
    #             # Filter by movement type if provided
    #             if movement_types:
    #                 all_movements = [m for m in all_movements if m.movement_type in movement_types]
                
    #             # Sort by date (newest first)
    #             all_movements.sort(key=lambda x: x.created_at, reverse=True)
                
    #             # Calculate totals
    #             total_in = sum(m.quantity for m in all_movements if m.quantity > 0)
    #             total_out = sum(abs(m.quantity) for m in all_movements if m.quantity < 0)
    #             current_stock = sum(item.quantity for item in inventory_items)
                
    #             # Format response
    #             result = {
    #                 "product": {
    #                     "id": str(product.id),
    #                     "name": product.name,
    #                     "sku": product.sku,
    #                     "description": product.description,
    #                     "brand": product.brand,
    #                     "dosage_form": product.dosage_form,
    #                     "strength": product.strength
    #                 },
    #                 "movements": [
    #                     {
    #                         "id": str(movement.id),
    #                         "movement_type": movement.movement_type,
    #                         "quantity": movement.quantity,
    #                         "reference": movement.reference,
    #                         "notes": movement.notes,
    #                         "created_at": movement.created_at.isoformat() if movement.created_at else None,
    #                         "created_by": str(movement.created_by) if movement.created_by else None
    #                     } for movement in all_movements
    #                 ],
    #                 "total_in": total_in,
    #                 "total_out": total_out,
    #                 "current_stock": current_stock
    #             }
                
    #             return result, HTTPStatus.OK
                
    #     except Exception as e:
    #         self._logger.error(f"Error retrieving product movement history: {str(e)}")
    #         return f"Error retrieving product movement history: {str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR
    
    # def get_out_of_stock_products_report(self, category_id: Optional[UUID] = None, 
    #                                      days_since_out_of_stock: int = 30) -> Tuple[Dict[str, Any], int]:
    #     """
    #     Get a report of out-of-stock products
        
    #     Args:
    #         category_id: Optional category ID to filter by
    #         days_since_out_of_stock: Number of days to look back for products that went out of stock
            
    #     Returns:
    #         Tuple containing the out-of-stock products report and HTTP status code
    #     """
    #     try:
    #         with self._uow as uow:
    #             # Get all active products
    #             if category_id:
    #                 if self._acl:
    #                     products = self.get_products_by_filter(GetProductsByFilterQuery(category_id=category_id))
    #                 else:
    #                     products = [p for p in uow.products.get_all() if p.category_id == category_id and p.is_active]
    #             else:
    #                 if self._acl:
    #                     products = self.get_all_products()
    #                 else:
    #                     products = [p for p in uow.products.get_all() if p.is_active]
                
    #             # Check stock status
    #             out_of_stock_products = []
    #             for product in products:
    #                 inventory_items = uow.inventory.get_by_product_id(product.id)
    #                 total_stock = sum(item.quantity for item in inventory_items) if inventory_items else 0
                    
    #                 if total_stock == 0:
    #                     # Check when it went out of stock if we have movement history
    #                     last_movement = None
    #                     if inventory_items:
    #                         for item in inventory_items:
    #                             movements = uow.stock_movement_repository.get_by_inventory_id(item.id)
    #                             if movements:
    #                                 # Get the most recent movement
    #                                 movements.sort(key=lambda x: x.created_at, reverse=True)
    #                                 item_last_movement = movements[0]
                                    
    #                                 if not last_movement or item_last_movement.created_at > last_movement.created_at:
    #                                     last_movement = item_last_movement
                        
    #                     # If we have a last movement, check if it's within our days threshold
    #                     if not last_movement or (datetime.now() - last_movement.created_at).days <= days_since_out_of_stock:
    #                         out_of_stock_products.append({
    #                             "id": str(product.id),
    #                             "name": product.name,
    #                             "description": product.description,
    #                             "sku": product.sku,
    #                             "barcode": product.barcode,
    #                             "category_id": str(product.category_id) if product.category_id else None,
    #                             "brand": product.brand,
    #                             "dosage_form": product.dosage_form,
    #                             "strength": product.strength,
    #                             "last_movement_date": last_movement.created_at.isoformat() if last_movement else None
    #                         })
                
    #             # Format response
    #             result = {
    #                 "products": out_of_stock_products,
    #                 "total_count": len(out_of_stock_products),
    #                 "last_updated": datetime.now().isoformat()
    #             }
                
    #             return result, HTTPStatus.OK
                
    #     except Exception as e:
    #         self._logger.error(f"Error retrieving out of stock products: {str(e)}")
    #         return f"Error retrieving out of stock products: {str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR
    
    # def get_product_sales_report(self, start_date: datetime, end_date: datetime, 
    #                             category_id: Optional[UUID] = None, 
    #                             top_n: int = 10) -> Tuple[List[Dict[str, Any]], int]:
    #     """
    #     Get a report of product sales within a date range
        
    #     Args:
    #         start_date: Start date for the report
    #         end_date: End date for the report
    #         category_id: Optional category ID to filter by
    #         top_n: Number of top products to include in the report
            
    #     Returns:
    #         Tuple containing the product sales report and HTTP status code
    #     """
    #     try:
    #         with self._uow as uow:
    #             # Get all active products
    #             if category_id:
    #                 if self._acl:
    #                     products = self.get_products_by_filter(GetProductsByFilterQuery(category_id=category_id))
    #                 else:
    #                     products = [p for p in uow.products.get_all() if p.category_id == category_id and p.is_active]
    #             else:
    #                 if self._acl:
    #                     products = self.get_all_products()
    #                 else:
    #                     products = [p for p in uow.products.get_all() if p.is_active]
                
    #             # Collect sales data for each product
    #             product_sales = []
    #             for product in products:
    #                 inventory_items = uow.inventory.get_by_product_id(product.id)
                    
    #                 if not inventory_items:
    #                     continue
                        
    #                 total_quantity = 0
    #                 total_revenue = 0.0
    #                 sale_count = 0
                    
    #                 for item in inventory_items:
    #                     # Get all outgoing movements (sales)
    #                     movements = uow.stock_movement_repository.get_by_inventory_id(item.id)
    #                     sale_movements = [
    #                         m for m in movements 
    #                         if m.movement_type in ['SALE', 'DISPENSE'] 
    #                         and m.quantity < 0
    #                         and m.created_at >= start_date
    #                         and m.created_at <= end_date
    #                     ]
                        
    #                     if not sale_movements:
    #                         continue
                            
    #                     # Calculate sales metrics
    #                     item_quantity = sum(abs(m.quantity) for m in sale_movements)
    #                     item_revenue = item_quantity * (float(item.price) if item.price else 0.0)
                        
    #                     total_quantity += item_quantity
    #                     total_revenue += item_revenue
    #                     sale_count += len(sale_movements)
                    
    #                 if total_quantity > 0:
    #                     product_sales.append({
    #                         "product": {
    #                             "id": str(product.id),
    #                             "name": product.name,
    #                             "description": product.description,
    #                             "sku": product.sku,
    #                             "brand": product.brand,
    #                             "dosage_form": product.dosage_form,
    #                             "strength": product.strength
    #                         },
    #                         "total_quantity": total_quantity,
    #                         "total_revenue": total_revenue,
    #                         "average_price": total_revenue / total_quantity if total_quantity > 0 else 0,
    #                         "sale_count": sale_count
    #                     })
                
    #             # Sort by total revenue (highest first) and take top N
    #             product_sales.sort(key=lambda x: x['total_revenue'], reverse=True)
    #             product_sales = product_sales[:top_n] if top_n > 0 else product_sales
                
    #             return product_sales, HTTPStatus.OK
                
    #     except Exception as e:
    #         self._logger.error(f"Error generating product sales report: {str(e)}")
    #         return f"Error generating product sales report: {str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR
    
    # def get_product_batches(self, product_id: UUID) -> Tuple[List[Dict[str, Any]], int]:
    #     """
    #     Get all batches for a specific product
        
    #     Args:
    #         product_id: UUID of the product
            
    #     Returns:
    #         Tuple containing the batch data and HTTP status code
    #     """
    #     try:
    #         with self._uow as uow:
    #             # Check if product exists
    #             if self._acl:
    #                 product = self.get_product_by_id(GetProductByIdQuery(product_id))
    #             else:
    #                 product = uow.products.get_by_id(product_id)
    #             if not product:
    #                 return f"Product with ID {product_id} not found", HTTPStatus.NOT_FOUND
                
    #             # Get inventory items for this product
    #             inventory_items = uow.inventory.get_by_product_id(product_id)
    #             if not inventory_items:
    #                 return [], HTTPStatus.OK
                
    #             # Get batches for each inventory item
    #             all_batches = []
    #             for item in inventory_items:
    #                 batches = uow.batches.get_by_inventory_id(item.id)
    #                 if batches:
    #                     all_batches.extend(batches)
                
    #             # Format response
    #             result = [
    #                 {
    #                     "id": str(batch.id),
    #                     "batch_number": batch.batch_number,
    #                     "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
    #                     "manufacturing_date": batch.manufacturing_date.isoformat() if batch.manufacturing_date else None,
    #                     "quantity": batch.quantity,
    #                     "supplier": batch.supplier_name if hasattr(batch, 'supplier_name') else None,
    #                     "cost": float(batch.cost) if hasattr(batch, 'cost') and batch.cost else None,
    #                     "is_active": not (batch.expiry_date and batch.expiry_date < datetime.now())
    #                 } for batch in all_batches
    #             ]
                
    #             return result, HTTPStatus.OK
                
    #     except Exception as e:
    #         self._logger.error(f"Error retrieving product batches: {str(e)}")
    #         return f"Error retrieving product batches: {str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR

    # def add_stock(
    #     self,
    #     medication_id: UUID,
    #     batch_number: str,
    #     quantity: int,
    #     unit_cost: Decimal,
    #     supplier_id: UUID,
    #     manufacturing_date: datetime,
    #     expiry_date: datetime,
    #     storage_location: str
    # ) -> StockDTO:
    #     """Add new stock to inventory"""
    #     stock = StockEntity(
    #         medication_id=medication_id,
    #         batch_number=batch_number,
    #         quantity=quantity,
    #         unit_cost=unit_cost,
    #         supplier_id=supplier_id,
    #         manufacturing_date=manufacturing_date,
    #         expiry_date=expiry_date,
    #         storage_location=storage_location
    #     )
    #     return self._inventory_repo.add_stock(stock)

    # def register_supplier(
    #     self,
    #     name: str,
    #     contact_person: str,
    #     email: str,
    #     phone: str,
    #     address: str,
    #     tax_id: str,
    #     payment_terms: str
    # ) -> SupplierDTO:
    #     """Register a new supplier"""
    #     supplier = SupplierEntity(
    #         name=name,
    #         contact_person=contact_person,
    #         email=email,
    #         phone=phone,
    #         address=address,
    #         tax_id=tax_id,
    #         payment_terms=payment_terms
    #     )
    #     return self._inventory_repo.add_supplier(supplier)

    # def record_stock_movement(
    #     self,
    #     medication_id: UUID,
    #     movement_type: str,
    #     quantity: int,
    #     reference_id: UUID,
    #     notes: str
    # ) -> StockMovementDTO:
    #     """Record stock movement (in/out)"""
    #     movement = StockMovement(
    #         medication_id=medication_id,
    #         movement_type=movement_type,
    #         quantity=quantity,
    #         reference_id=reference_id,
    #         notes=notes
    #     )
    #     return self._inventory_repo.record_movement(movement)

    # def set_reorder_policy(
    #     self,
    #     medication_id: UUID,
    #     min_quantity: int,
    #     reorder_quantity: int,
    #     preferred_supplier_id: UUID
    # ) -> ReorderPolicyDTO:
    #     """Set reorder policy for a medication"""
    #     policy = ReorderPolicy(
    #         medication_id=medication_id,
    #         min_quantity=min_quantity,
    #         reorder_quantity=reorder_quantity,
    #         preferred_supplier_id=preferred_supplier_id
    #     )
    #     return self._inventory_repo.set_reorder_policy(policy)

    # def get_stock_level(
    #     self,
    #     medication_id: UUID,
    #     include_expired: bool = False
    # ) -> int:
    #     """Get current stock level for a medication"""
    #     return self._inventory_repo.get_stock_level(medication_id, include_expired)

    # def get_expiring_stock(
    #     self,
    #     days_threshold: int = 90
    # ) -> List[StockDTO]:
    #     """Get stock items expiring within threshold"""
    #     return self._inventory_repo.get_expiring_stock(days_threshold)

    # def get_low_stock_alerts(self) -> List[InventoryAlertDTO]:
    #     """Get alerts for items below reorder level"""
    #     return self._inventory_repo.get_low_stock_alerts()

    # def get_stock_movements(
    #     self,
    #     medication_id: UUID,
    #     start_date: Optional[datetime] = None,
    #     end_date: Optional[datetime] = None
    # ) -> List[StockMovementDTO]:
    #     """Get stock movement history"""
    #     return self._inventory_repo.get_stock_movements(
    #         medication_id,
    #         start_date,
    #         end_date
    #     )

    # def adjust_stock(
    #     self,
    #     medication_id: UUID,
    #     adjustment_quantity: int,
    #     reason: str,
    #     adjusted_by: UUID
    # ) -> StockDTO:
    #     """Adjust stock level with audit trail"""
    #     return self._inventory_repo.adjust_stock(
    #         medication_id,
    #         adjustment_quantity,
    #         reason,
    #         adjusted_by
    #     )

    # def transfer_stock(
    #     self,
    #     medication_id: UUID,
    #     quantity: int,
    #     from_location: str,
    #     to_location: str,
    #     reason: str
    # ) -> StockDTO:
    #     """Transfer stock between locations"""
    #     return self._inventory_repo.transfer_stock(
    #         medication_id,
    #         quantity,
    #         from_location,
    #         to_location,
    #         reason
    #     )

    # def generate_inventory_report(
    #     self,
    #     start_date: datetime,
    #     end_date: datetime
    # ) -> dict:
    #     """Generate comprehensive inventory report"""
    #     return {
    #         'stock_levels': self._inventory_repo.get_stock_levels_report(),
    #         'movements': self._inventory_repo.get_movements_report(start_date, end_date),
    #         'adjustments': self._inventory_repo.get_adjustments_report(start_date, end_date),
    #         'expiry_summary': self._inventory_repo.get_expiry_summary(),
    #         'valuation': self._inventory_repo.get_inventory_valuation(),
    #         'turnover': self._inventory_repo.get_inventory_turnover(start_date, end_date)
    #     }

    # def get_supplier_performance(
    #     self,
    #     supplier_id: UUID,
    #     start_date: datetime,
    #     end_date: datetime
    # ) -> dict:
    #     """Get supplier performance metrics"""
    #     return self._inventory_repo.get_supplier_performance(
    #         supplier_id,
    #         start_date,
    #         end_date
    #     )
