from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.services.inventory_service.domain.entities.inventory_entity import InventoryEntity
from app.services.inventory_service.domain.enums.stock_status import StockStatus
from app.services.inventory_service.domain.exceptions.inventory_errors import InventoryNotFoundError, ProductNotFoundError
from app.services.inventory_service.infrastructure.persistence.models.inventory_model import InventoryModel
from app.services.inventory_service.infrastructure.persistence.models.stock_movement_model import StockMovementModel
from app.services.inventory_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
from app.services.product_service.application.queries.get_inventory_by_id import GetInventoryByIdQuery
from app.services.product_service.application.queries.get_product_by_id import GetProductByIdQuery


class InventoryQueryService:
    """
    Query service for inventory reporting and monitoring.
    
    This service provides read-only access to inventory data
    for analysis, reporting, and monitoring purposes.
    """
    
    def __init__(self, session: Session,uow:SQLAlchemyUnitOfWork):
        self._session = session
        self._uow = uow
    def get_inventory_by_id(self,query:GetInventoryByIdQuery) -> InventoryEntity:
        product_id=query.product_id
        inventory_fields = self._uow.inventory_repository.get_by_product_id(product_id)
        if not inventory_fields:
            raise InventoryNotFoundError(message=f"inventory of product with ID {product_id} not found") 
        return inventory_fields
    # def get_product_by_id(self,query:GetProductByIdQuery):
    #     product_id=query.product_id
        
    #     product_fields = self._uow.product_repository.get_by_id(product_id)
        
    #     if not product_fields:
    #         raise ProductNotFoundError(message=f"Product with ID {product_id} not found")                
                
    #     inventory_fields = self._uow.inventory_repository.get_by_product_id(product_id)
                
                
    #     result = {
    #                 "id": product_id,
    #                 "product_fields":product_fields,
    #                 "inventory_fields":inventory_fields                   
    #             }
                
    #     return result
        # Calculate total stock across all inventory items
                # total_stock = sum(item.quantity for item in inventory_items) if inventory_items else 0
                
                # # Get batch information if available
                # batches = []
                # for item in inventory_items:
                #     item_batches = self._uow.batch_repository.get_by_inventory_id(item.id)
                #     if item_batches:
                #         batches.extend(item_batches)
                # "total_stock": total_stock,
                    # "inventory_items": [
                    #     {
                    #         "id": str(item.id),
                    #         "location_id": str(item.location_id) if item.location_id else None,
                    #         "quantity": item.quantity,
                    #         "price": float(item.price) if item.price else None,
                    #         "cost": float(item.cost) if item.cost else None
                    #     } for item in inventory_items
                    # ] if inventory_items else [],
                    # "batches": [
                    #     {
                    #         "id": str(batch.id),
                    #         "batch_number": batch.batch_number,
                    #         "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
                    #         "quantity": batch.quantity,
                    #         "manufacturing_date": batch.manufacturing_date.isoformat() if batch.manufacturing_date else None
                    #     } for batch in batches
                    # ] if batches else []
                # Format response
                
    

    # def get_products_by_filter(self,query:GetProductsByFilterQuery):
    #     q = self._session.query(ProductModel).join(InventoryModel, ProductModel.id == InventoryModel.product_id)
    #     l=q.all()
    #     total = len(l)
    #     page = query.page
    #     items_per_page= query.items_per_page
    #     total_pages = (total + query.items_per_page - 1) // query.items_per_page       
    #     return {
    #         "items":[
    #             {
    #              "id":product.id,
    #              "product_fields":ProductEntity(**product.to_json()),
    #              "inventory_fields":InventoryEntity(**(product.inventory[0].to_json())) 
    #              }
    #             for product in l],
    #         "total":total,
    #         "page":page,
    #         "items_per_page":items_per_page,
    #         "total_pages":total_pages           
    #     } 
            
         # Apply price filter
        # query = q.filter(InventoryModel.price < 4.88)
        # products, total = self._uow.product_repository.find_by_filter(
        #     name=query.name,
        #     category_id=query.category_id,
        #     brand=query.brand,
        #     is_prescription_required=query.is_prescription_required,
        #     is_active=query.is_active,
        #     min_stock=query.min_stock,
        #     has_stock=query.has_stock,
        #     sort_by=query.sort_by,
        #     sort_direction=query.sort_direction,
        #     page=query.page,
        #     items_per_page=query.items_per_page
        # )
        
                
        # # Calculate total pages
        # total_pages = (total + query.items_per_page - 1) // query.items_per_page
                
        # # Format response
        # result = {
        #     "items": [
        #         {
        #             "id": str(product.id),
        #             "name": product.name,
        #     "description": product.description,
        #             # "sku": product.sku,
        #             # "barcode": product.barcode,
        #             # "category_id": str(product.category_id) if product.category_id else None,
        #             # "subcategory_id": str(product.subcategory_id) if product.subcategory_id else None,
        #             # "brand": product.brand,
        #             # "dosage_form": product.dosage_form,
        #             # "strength": product.strength,
        #             # "is_prescription_required": product.is_prescription_required,
        #            # "tax_rate": product.tax_rate,
        #             # "is_active": product.is_active,
        #             # "package_size": product.package_size,
        #             # "image_url": product.image_url,
        #             # "created_at": product.created_at.isoformat() if product.created_at else None,
        #             # "updated_at": product.updated_at.isoformat() if product.updated_at else None
        #         } for product in products
        #     ],
        #     "total": total,
        #     # # "page": page,
        #             # # "items_per_page": items_per_page,
        #     # "total_pages": total_pages
        # }
                
        # return result
    
    # def get_low_stock_items(self, threshold_percentage: float = 100) -> List[Dict[str, Any]]:
    #     """
    #     Get inventory items with stock levels below or at their min_stock level.
        
    #     Args:
    #         threshold_percentage: Percentage of min_stock to use as threshold
    #                              (default 100% means at or below min_stock)
        
    #     Returns:
    #         List of inventory items with low stock, including product details
    #     """
    #     query = (
    #         self._session.query(
    #             InventoryModel, 
    #             ProductModel.name.label('product_name'),
    #             ProductModel.description.label('product_description')
    #         )
    #         .join(ProductModel, InventoryModel.product_id == ProductModel.id)
    #         .filter(
    #             InventoryModel.quantity <= InventoryModel.min_stock * threshold_percentage / 100
    #         )
    #         .order_by(
    #             # Order by most critical first (lowest percentage of min stock)
    #             (InventoryModel.quantity / InventoryModel.min_stock)
    #         )
    #     )
        
    #     results = []
    #     for row in query.all():
    #         inventory = row[0]
    #         product_name = row.product_name
    #         product_description = row.product_description
            
    #         # Calculate how much to order
    #         order_quantity = max(inventory.max_stock - inventory.quantity, 0)
            
    #         results.append({
    #             "inventory_id": inventory.id,
    #             "product_id": inventory.product_id,
    #             "product_name": product_name,
    #             "product_description": product_description,
    #             "current_quantity": inventory.quantity,
    #             "min_stock": inventory.min_stock,
    #             "max_stock": inventory.max_stock,
    #             "percentage_of_min": round((inventory.quantity / inventory.min_stock) * 100, 2) if inventory.min_stock > 0 else 0,
    #             "suggested_order_quantity": order_quantity,
    #             "price": inventory.price,
    #             "location_code": inventory.location_code,
    #             "last_restock_date": inventory.last_restock_date
    #         })
        
    #     return results
    
    # def get_expiring_items(self, days_threshold: int = 90) -> List[Dict[str, Any]]:
    #     """
    #     Get inventory items that will expire within the given threshold.
        
    #     Args:
    #         days_threshold: Number of days to look ahead for expiring items
            
    #     Returns:
    #         List of inventory items that will expire within the threshold,
    #         including product details
    #     """
    #     today = datetime.now(timezone.utc).date()
    #     expiry_cutoff = today + timedelta(days=days_threshold)
        
    #     query = (
    #         self._session.query(
    #             InventoryModel, 
    #             ProductModel.name.label('product_name'),
    #             ProductModel.description.label('product_description')
    #         )
    #         .join(ProductModel, InventoryModel.product_id == ProductModel.id)
    #         .filter(
    #             InventoryModel.expiry_date.isnot(None),
    #             InventoryModel.expiry_date <= expiry_cutoff,
    #             InventoryModel.expiry_date >= today,  # Not yet expired
    #             InventoryModel.quantity > 0  # Has stock
    #         )
    #         .order_by(InventoryModel.expiry_date)  # Earliest expiring first
    #     )
        
    #     results = []
    #     for row in query.all():
    #         inventory = row[0]
    #         product_name = row.product_name
    #         product_description = row.product_description
            
    #         days_until_expiry = (inventory.expiry_date - today).days
            
    #         results.append({
    #             "inventory_id": inventory.id,
    #             "product_id": inventory.product_id,
    #             "product_name": product_name,
    #             "product_description": product_description,
    #             "current_quantity": inventory.quantity,
    #             "expiry_date": inventory.expiry_date,
    #             "days_until_expiry": days_until_expiry,
    #             "batch_number": inventory.batch_number,
    #             "lot_number": inventory.lot_number,
    #             "price": inventory.price,
    #             "location_code": inventory.location_code
    #         })
        
    #     return results
    
    # def get_expired_items(self) -> List[Dict[str, Any]]:
    #     """
    #     Get inventory items that have already expired.
        
    #     Returns:
    #         List of expired inventory items, including product details
    #     """
    #     today = datetime.now(timezone.utc).date()
        
    #     query = (
    #         self._session.query(
    #             InventoryModel, 
    #             ProductModel.name.label('product_name'),
    #             ProductModel.description.label('product_description')
    #         )
    #         .join(ProductModel, InventoryModel.product_id == ProductModel.id)
    #         .filter(
    #             InventoryModel.expiry_date.isnot(None),
    #             InventoryModel.expiry_date < today,  # Already expired
    #             InventoryModel.quantity > 0  # Has stock
    #         )
    #         .order_by(InventoryModel.expiry_date)  # Earliest expired first
    #     )
        
    #     results = []
    #     for row in query.all():
    #         inventory = row[0]
    #         product_name = row.product_name
    #         product_description = row.product_description
            
    #         days_since_expiry = (today - inventory.expiry_date).days
            
    #         results.append({
    #             "inventory_id": inventory.id,
    #             "product_id": inventory.product_id,
    #             "product_name": product_name,
    #             "product_description": product_description,
    #             "current_quantity": inventory.quantity,
    #             "expiry_date": inventory.expiry_date,
    #             "days_since_expiry": days_since_expiry,
    #             "batch_number": inventory.batch_number,
    #             "lot_number": inventory.lot_number,
    #             "price": inventory.price,
    #             "location_code": inventory.location_code
    #         })
        
    #     return results
    
    # def get_inventory_summary(self) -> Dict[str, Any]:
    #     """
    #     Get a summary of the current inventory status.
        
    #     Returns:
    #         Summary statistics about inventory status
    #     """
    #     total_items_query = self._session.query(func.count(InventoryModel.id))
    #     total_items = total_items_query.scalar() or 0
        
    #     total_value_query = self._session.query(
    #         func.sum(InventoryModel.quantity * InventoryModel.price)
    #     )
    #     total_value = total_value_query.scalar() or 0
        
    #     expired_count_query = self._session.query(func.count(InventoryModel.id)).filter(
    #         InventoryModel.expiry_date.isnot(None),
    #         InventoryModel.expiry_date < datetime.now(timezone.utc).date(),
    #         InventoryModel.quantity > 0
    #     )
    #     expired_count = expired_count_query.scalar() or 0
        
    #     low_stock_count_query = self._session.query(func.count(InventoryModel.id)).filter(
    #         InventoryModel.quantity <= InventoryModel.min_stock
    #     )
    #     low_stock_count = low_stock_count_query.scalar() or 0
        
    #     # Count by stock status
    #     status_counts = {}
    #     for status in StockStatus:
    #         count_query = self._session.query(func.count(InventoryModel.id)).filter(
    #             InventoryModel.status == status
    #         )
    #         status_counts[status.value] = count_query.scalar() or 0
        
    #     return {
    #         "total_items": total_items,
    #         "total_value": total_value,
    #         "expired_count": expired_count,
    #         "low_stock_count": low_stock_count,
    #         "status_counts": status_counts
    #     }