from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text
from math import ceil
import logging
from datetime import datetime, timedelta, timezone

from app.services.inventory_service.infrastructure.persistence.models.inventory_model import InventoryModel
from app.services.product_service.application.queries.get_product_by_id import GetProductByIdQuery
from app.services.product_service.application.queries.get_products_by_filter import GetProductsByFilterQuery
from app.services.product_service.application.use_cases.get_product import GetProductResponseDTO, GetProductUseCase
from app.services.product_service.domain.interfaces.unit_of_work import UnitOfWork
from app.services.product_service.infrastructure.persistence.models.product_model import ProductModel
from app.services.product_service.application.dtos.product_dto import ProductFieldsDto, InventoryFieldsDto

# Configure logger
logger = logging.getLogger(__name__)

class ProductQueryService:
    """
    Query service for optimized product read operations with advanced filtering and analytics.
    """
    
    def __init__(self, session: Session, uow: UnitOfWork):
        """
        Initialize the query service with a database session.
        
        Args:
            session: SQLAlchemy database session
            uow: Unit of Work for transaction management
        """
        self._session = session
        self._uow = uow
        self._get_product_use_case = GetProductUseCase(self._uow)
    
    def get_by_id(self, query: GetProductByIdQuery) -> GetProductResponseDTO:
        """Get a single product by ID with inventory data"""
        product_fields = self._get_product_use_case.execute(query)
        # Get inventory information if available
        product_model = self._session.query(ProductModel).filter(ProductModel.id == product_fields.id).first()
        inventory_data = self._get_inventory_data(product_model)
        # Create response DTO
        response = GetProductResponseDTO(
                id=product_fields.id,
                product_fields=product_fields,
                inventory_fields=inventory_data
            )
        return response
    
    def list(self, filters: GetProductsByFilterQuery) -> Dict[str, Any]:
        """List products with advanced filtering and pagination"""
        logger.info(f"Query service listing products with filters")
        # Build the query with filters
        query = self._session.query(ProductModel)
        
        query = self._apply_filters(query, filters)
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination
        offset = (filters.page - 1) * filters.items_per_page
        products = query.order_by(ProductModel.name).offset(offset).limit(filters.items_per_page).all()
        
        # Calculate pagination metadata
        total_pages = ceil(total_count / filters.items_per_page) if total_count > 0 else 1
        
        # Convert to DTOs
        items = [{           
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "price": self._get_inventory_data(product).price if self._get_inventory_data(product) else 0.0,
            "imageUrl": product.image_url,
            "inStock": self._get_inventory_data(product).quantity > 0 if self._get_inventory_data(product) else False,
            "stockQuantity": self._get_inventory_data(product).quantity if self._get_inventory_data(product) else 0,
            "category": "category",
            "manufacturer": product.brand,
            "metadata": {
              "prescription": False,
              "dosage": product.strength,
              "form": product.dosage_form,
            },
            }     
                 for product in products]
        
        # Build response
        result = {
            "items": items,
            "total_items": total_count,
            "page": filters.page,
            "page_size": filters.items_per_page,
            "total_pages": total_pages
        }
        
        logger.info(f"Query service found {total_count} products (page {filters.page} of {total_pages})")
        return result
    
    def search(self, query: GetProductsByFilterQuery) -> Dict[str, Any]:
        """
        Advanced search for products with multiple criteria.
        
        Args:
            query: Search query with filters
            
        Returns:
            Dictionary with search results and pagination information
        """
        logger.info(f"Query service searching products with advanced criteria")
        
        # Build the query with search filters
        sql_query = self._session.query(ProductModel)
        sql_query = self._apply_search_filters(sql_query, query)
        
        # Get total count for pagination
        total_count = sql_query.count()
        
        # Apply pagination
        offset = (query.page - 1) * query.items_per_page
        products = sql_query.order_by(ProductModel.name).offset(offset).limit(query.items_per_page).all()
        
        # Calculate pagination metadata
        total_pages = ceil(total_count / query.items_per_page) if total_count > 0 else 1
        
        # Convert to DTOs
        items = [self._to_dto(product) for product in products]
        
        # Build response
        result = {
            "items": items,
            "total_items": total_count,
            "page": query.page,
            "page_size": query.items_per_page,
            "total_pages": total_pages
        }
        
        logger.info(f"Search found {total_count} products (page {query.page} of {total_pages})")
        return result

    def get_low_stock_products(self, threshold_percentage: float = 100, page: int = 1, page_size: int = 20):
        """
        Get products with stock levels below the specified threshold.
        
        Args:
            threshold_percentage: Percentage of min_stock to use as threshold
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Dictionary with low stock products
        """
        logger.info(f"Getting low stock products with threshold: {threshold_percentage}%")
        
        # Query products with their inventory
        query = (
            self._session.query(ProductModel)
            .join(InventoryModel, ProductModel.id == InventoryModel.product_id)
            .filter(
                InventoryModel.quantity <= InventoryModel.min_stock * threshold_percentage / 100
            )
            .order_by(
                # Order by most critical first (lowest percentage of min stock)
                (InventoryModel.quantity / InventoryModel.min_stock)
            )
        )
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()
        
        # Calculate pagination metadata
        total_pages = ceil(total_count / page_size) if total_count > 0 else 1
        
        # Convert to DTOs with low stock information
        items = []
        for product in products:
            inventory = product.inventory
            item = self._to_dto(product)
            if inventory:
                item['low_stock_info'] = {
                    "current_quantity": inventory.quantity,
                    "min_stock": inventory.min_stock,
                    "percentage_of_min": round((inventory.quantity / inventory.min_stock) * 100, 2) if inventory.min_stock > 0 else 0,
                    "suggested_order_quantity": max(inventory.max_stock - inventory.quantity, 0)
                }
            items.append(item)
        
        result = {
            "items": items,
            "total_items": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
        
        logger.info(f"Found {total_count} low stock products")
        return result

    def get_expiring_products(self, days_threshold: int = 90, page: int = 1, page_size: int = 20):
        """
        Get products that will expire within the specified number of days.
        
        Args:
            days_threshold: Number of days to look ahead for expiring products
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Dictionary with expiring products
        """
        logger.info(f"Getting products expiring within {days_threshold} days")
        
        today = datetime.now(timezone.utc).date()
        expiry_cutoff = today + timedelta(days=days_threshold)
        
        # Query products with their inventory that are expiring
        query = (
            self._session.query(ProductModel)
            .join(InventoryModel, ProductModel.id == InventoryModel.product_id)
            .filter(
                InventoryModel.expiry_date.isnot(None),
                InventoryModel.expiry_date <= expiry_cutoff,
                InventoryModel.expiry_date >= today,  # Not yet expired
                InventoryModel.quantity > 0  # Has stock
            )
            .order_by(InventoryModel.expiry_date)  # Earliest expiring first
        )
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()
        
        # Calculate pagination metadata
        total_pages = ceil(total_count / page_size) if total_count > 0 else 1
        
        # Convert to DTOs with expiry information
        items = []
        for product in products:
            inventory = product.inventory
            item = self._to_dto(product)
            if inventory and inventory.expiry_date:
                days_until_expiry = (inventory.expiry_date - today).days
                item['expiry_info'] = {
                    "expiry_date": inventory.expiry_date.isoformat(),
                    "days_until_expiry": days_until_expiry,
                    "current_quantity": inventory.quantity
                }
            items.append(item)
        
        result = {
            "items": items,
            "total_items": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
        
        logger.info(f"Found {total_count} products expiring within {days_threshold} days")
        return result

    def get_product_stock_status(self, product_id: UUID):
        """
        Get detailed stock status for a specific product.
        
        Args:
            product_id: The ID of the product
            
        Returns:
            Detailed stock status information
        """
        logger.info(f"Getting stock status for product: {product_id}")
        
        # Get product and inventory
        product = self._session.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        inventory = product.inventory
        if not inventory:
            return {
                "product_id": str(product_id),
                "is_available": False,
                "remaining_stock": 0,
                "warnings": ["No inventory data available"],
                "status": ["OUT_OF_STOCK"],
                "days_until_expiry": None
            }
        
        # Calculate status
        warnings = []
        status = []
        is_available = True
        days_until_expiry = None
        
        # Check stock levels
        if inventory.quantity == 0:
            is_available = False
            warnings.append("Product is out of stock")
            status.append("OUT_OF_STOCK")
        elif inventory.quantity <= inventory.min_stock:
            warnings.append(f"Low stock alert: {inventory.quantity} units available (minimum: {inventory.min_stock})")
            status.append("LOW_STOCK")
        
        # Check expiry
        if inventory.expiry_date:
            today = datetime.now(timezone.utc).date()
            days_until_expiry = (inventory.expiry_date - today).days
            if days_until_expiry <= 0:
                is_available = False
                warnings.append(f"Product expired {abs(days_until_expiry)} days ago")
                status.append("EXPIRED")
            elif days_until_expiry <= 30:
                warnings.append(f"Product expires in {days_until_expiry} days")
                status.append("EXPIRING_SOON")
        
        # Check product status
        if product.status.value != "ACTIVE":
            is_available = False
            warnings.append(f"Product is not active (status: {product.status.value})")
            status.append("INACTIVE")
        
        if is_available and not status:
            status.append("AVAILABLE")
        
        result = {
            "product_id": str(product_id),
            "is_available": is_available,
            "remaining_stock": inventory.quantity,
            "warnings": warnings,
            "status": status,
            "days_until_expiry": days_until_expiry,
            "stock_details": {
                "current_quantity": inventory.quantity,
                "min_stock": inventory.min_stock,
                "max_stock": inventory.max_stock,
                "price": inventory.price,
                "expiry_date": inventory.expiry_date.isoformat() if inventory.expiry_date else None
            }
        }
        
        logger.info(f"Stock status retrieved for product: {product_id}")
        return result

    def get_product_analytics(self, product_id: UUID):
        """
        Get analytics data for a specific product.
        
        Args:
            product_id: The ID of the product
            
        Returns:
            Analytics data including sales, stock movements, etc.
        """
        logger.info(f"Getting analytics for product: {product_id}")
        
        # Get product
        product = self._session.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Basic analytics (can be expanded based on available data)
        result = {
            "product_id": str(product_id),
            "product_name": product.name,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
            "status": product.status.value,
            "inventory_analytics": self._get_inventory_analytics(product),
            # Future: Add sales analytics, movement history, etc.
        }
        
        logger.info(f"Analytics retrieved for product: {product_id}")
        return result

    def validate_product_availability(self, product_id: UUID, requested_quantity: int):
        """
        Validate if a product is available in the requested quantity.
        
        Args:
            product_id: The ID of the product
            requested_quantity: The quantity requested
            
        Returns:
            Validation result with availability status
        """
        logger.info(f"Validating availability for product {product_id}, quantity: {requested_quantity}")
        
        # Get stock status
        stock_status = self.get_product_stock_status(product_id)
        
        # Validate against requested quantity
        validation_result = {
            "product_id": str(product_id),
            "requested_quantity": requested_quantity,
            "is_available": False,
            "available_quantity": stock_status["remaining_stock"],
            "can_fulfill": False,
            "warnings": [],
            "status": stock_status["status"]
        }
        
        # Check if product is generally available
        if not stock_status["is_available"]:
            validation_result["warnings"].extend(stock_status["warnings"])
            validation_result["warnings"].append("Product is not available for ordering")
        else:
            validation_result["is_available"] = True
            
            # Check if we can fulfill the requested quantity
            if requested_quantity <= stock_status["remaining_stock"]:
                validation_result["can_fulfill"] = True
                
                # Check if fulfilling would bring stock below minimum
                remaining_after = stock_status["remaining_stock"] - requested_quantity
                if "stock_details" in stock_status and remaining_after < stock_status["stock_details"]["min_stock"]:
                    validation_result["warnings"].append(
                        f"Fulfilling this order would reduce stock below minimum threshold"
                    )
            else:
                shortage = requested_quantity - stock_status["remaining_stock"]
                validation_result["warnings"].append(
                    f"Insufficient stock. Requested: {requested_quantity}, Available: {stock_status['remaining_stock']}, Short by: {shortage}"
                )
        
        logger.info(f"Availability validation completed for product: {product_id}")
        return validation_result
    
    def _apply_filters(self, query, filters: GetProductsByFilterQuery):
        """Apply basic filters to a query"""
        filter_conditions = []
        
        # Name filter
        if filters.name:
            filter_conditions.append(ProductModel.name.ilike(f"%{filters.name}%"))
        
        # Brand filter
        if filters.brand:
            filter_conditions.append(ProductModel.brand.ilike(f"%{filters.brand}%"))
        
        # Category filter
        if filters.category_id:
            filter_conditions.append(ProductModel.category_id == filters.category_id)
        
        # Status filter
        if hasattr(filters, 'status') and filters.status:
            filter_conditions.append(ProductModel.status == filters.status)
        
        # Apply all filters
        if filter_conditions:
            query = query.filter(and_(*filter_conditions))
        
        return query

    def _apply_search_filters(self, query, search_query: GetProductsByFilterQuery):
        """Apply advanced search filters to a query"""
        filter_conditions = []
        
        # Text search across multiple fields
        if search_query.name:
            search_term = f"%{search_query.name}%"
            filter_conditions.append(
                or_(
                    ProductModel.name.ilike(search_term),
                    ProductModel.description.ilike(search_term),
                    ProductModel.brand.ilike(search_term),
                    ProductModel.dosage_form.ilike(search_term),
                    ProductModel.strength.ilike(search_term)
                )
            )
        
        # Category filter
        if search_query.category_id:
            filter_conditions.append(ProductModel.category_id == search_query.category_id)
        
        # Brand filter
        if search_query.brand:
            filter_conditions.append(ProductModel.brand.ilike(f"%{search_query.brand}%"))
        
        # Status filter
        if hasattr(search_query, 'status') and search_query.status:
            filter_conditions.append(ProductModel.status == search_query.status)
        
        # Price filters (requires joining with inventory)
        if hasattr(search_query, 'min_price') or hasattr(search_query, 'max_price'):
            query = query.join(InventoryModel, ProductModel.id == InventoryModel.product_id)
            
            if hasattr(search_query, 'min_price') and search_query.min_price:
                filter_conditions.append(InventoryModel.price >= search_query.min_price)
            
            if hasattr(search_query, 'max_price') and search_query.max_price:
                filter_conditions.append(InventoryModel.price <= search_query.max_price)
        
        # In stock only filter
        if hasattr(search_query, 'in_stock_only') and search_query.in_stock_only:
            # Check if we already joined inventory table
            joined_tables = [mapper.class_ for mapper in query.column_descriptions if hasattr(mapper, 'class_')]
            if InventoryModel not in joined_tables:
                query = query.join(InventoryModel, ProductModel.id == InventoryModel.product_id)
            filter_conditions.append(InventoryModel.quantity > 0)
        
        # Apply all filters
        if filter_conditions:
            query = query.filter(and_(*filter_conditions))
        
        return query
    
    def _to_dto(self, product_model) -> Dict[str, Any]:
        """Convert a product model to a DTO"""
        product_fields = ProductFieldsDto(
            id=product_model.id,
            name=product_model.name,
            description=product_model.description,
            brand=product_model.brand,
            category_id=product_model.category_id,
            dosage_form=product_model.dosage_form,
            strength=product_model.strength,
            package=product_model.package,
            image_url=product_model.image_url,
            status=product_model.status
        )
        
        # Get inventory data if available
        inventory_fields = self._get_inventory_data(product_model)
        
        return {
            "id": str(product_model.id),
            "product_fields": product_fields.model_dump(),
            "inventory_fields": inventory_fields.model_dump() if inventory_fields else None,
            "created_at": product_model.created_at.isoformat() if product_model.created_at else None,
            "updated_at": product_model.updated_at.isoformat() if product_model.updated_at else None
        }
    
    def _get_inventory_data(self, product: ProductModel) -> Optional[InventoryFieldsDto]:
        """Get inventory data for a product"""
        try:
            product_id = product.id
            inventory_model = product.inventory
            if inventory_model:
                return InventoryFieldsDto(
                    product_id=product_id,
                    price=getattr(inventory_model, 'price', 0.0),
                    quantity=getattr(inventory_model, 'quantity', 0),
                    max_stock=getattr(inventory_model, 'max_stock', 0),
                    min_stock=getattr(inventory_model, 'min_stock', 0),
                    expiry_date=getattr(inventory_model, 'expiry_date', None),
                    supplier_id=getattr(inventory_model, 'supplier_id', None)
                )
            return None
        except Exception as e:
            logger.warning(f"Error retrieving inventory data for product {product.id}: {str(e)}")
            return None

    def _get_inventory_analytics(self, product: ProductModel) -> Dict[str, Any]:
        """Get inventory analytics for a product"""
        inventory = product.inventory
        if not inventory:
            return {"status": "No inventory data available"}
        
        analytics = {
            "current_stock": inventory.quantity,
            "min_stock": inventory.min_stock,
            "max_stock": inventory.max_stock,
            "stock_level_percentage": round((inventory.quantity / inventory.max_stock) * 100, 2) if inventory.max_stock > 0 else 0,
            "days_until_expiry": None,
            "stock_status": "NORMAL"
        }
        
        # Calculate stock status
        if inventory.quantity == 0:
            analytics["stock_status"] = "OUT_OF_STOCK"
        elif inventory.quantity <= inventory.min_stock:
            analytics["stock_status"] = "LOW_STOCK"
        elif inventory.quantity >= inventory.max_stock * 0.9:
            analytics["stock_status"] = "HIGH_STOCK"
        
        # Calculate expiry information
        if inventory.expiry_date:
            today = datetime.now(timezone.utc).date()
            analytics["days_until_expiry"] = (inventory.expiry_date - today).days
            
            if analytics["days_until_expiry"] <= 0:
                analytics["stock_status"] = "EXPIRED"
            elif analytics["days_until_expiry"] <= 30:
                analytics["stock_status"] = "EXPIRING_SOON"
        
        return analytics 