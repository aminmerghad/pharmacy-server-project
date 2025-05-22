from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta

from app.dataBase import Database
from app.services.product_service.application.commands.create_product_command import CreateProductCommand
from app.services.product_service.application.commands.update_product_command import UpdateProductCommand
from app.services.product_service.application.commands.delete_product_command import DeleteProductCommand
from app.services.product_service.application.queries.get_product_by_id import GetProductByIdQuery
from app.services.product_service.application.queries.get_products_by_filter import GetProductsByFilterQuery
from app.services.product_service.application.use_cases.create_product import CreateProductUseCase
from app.services.product_service.application.use_cases.update_product import UpdateProductUseCase
from app.services.product_service.application.use_cases.delete_product import DeleteProductUseCase
from app.services.product_service.application.use_cases.get_product import GetProductUseCase
from app.services.product_service.application.use_cases.list_products import ListProductsUseCase
from app.services.product_service.infrastructure.persistence.unit_of_work.sqlalchemy_unit_of_work import SQLAlchemyUnitOfWork
from app.services.product_service.infrastructure.query_services.product_query_service import ProductQueryService
from app.services.product_service.infrastructure.adapters.product_event_adapter import ProductEventAdapter
from app.shared.acl.unified_acl import UnifiedACL
from app.shared.application.events.event_bus import EventBus

# Configure logger
logger = logging.getLogger(__name__)

class ProductService:
    """
    Service for managing products in the pharmacy system.
    """
    
    def __init__(self, db: Database, event_bus: EventBus, acl: UnifiedACL):
        self._db_session = db.get_session()
        self._acl = acl
        self._event_bus = event_bus
        self._init_resources()
        logger.info("Product service initialized")
        
    def _init_resources(self):
        # Normally this would come from configuration
        
        self._uow = SQLAlchemyUnitOfWork(
            self._db_session, 
            self._event_bus, 
            self._acl
        )
        self._query_service = ProductQueryService(self._db_session,self._uow)
        self._create_product_use_case = CreateProductUseCase(self._uow)
        self._update_product_use_case = UpdateProductUseCase(self._uow)
        self._delete_product_use_case = DeleteProductUseCase(self._uow)        
        self._list_products_use_case = ListProductsUseCase(self._uow)
        
    
    def create_product(self, command: CreateProductCommand):
        """Create a new product with inventory"""
        logger.info(f"Creating product with name: {command.product_fields.name}")
        try:
            result = self._create_product_use_case.execute(command)
            logger.info(f"Product created successfully with ID: {result.id}")
            return result
        except Exception as e:
            self._uow.rollback()
            logger.error(f"Failed to create product: {str(e)}", exc_info=True)
            raise
    
    def update_product(self, command: UpdateProductCommand):
        """Update an existing product"""
        logger.info(f"Updating product with ID: {command.id}")
        try:
            result = self._update_product_use_case.execute(command)
            logger.info(f"Product updated successfully: {result.id}")
            return result
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise
    
    def delete_product(self, command: DeleteProductCommand):
        """Delete a product"""        
        logger.info(f"Deleting product with ID: {command.id}")
        try:
            result = self._delete_product_use_case.execute(command)
            logger.info(f"Product deleted successfully: {command.id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            raise
    
    def get_product(self, query: GetProductByIdQuery):
        """Get a product by ID"""
        product_id = query.id
        
        logger.info(f"Getting product with ID: {product_id}")
        try:
            result = self._query_service.get_by_id(query)
            if result:
                logger.info(f"Product found: {product_id}")
            else:
                logger.info(f"Product not found: {product_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting product: {str(e)}")
            raise
    
    def list_products(self, query: GetProductsByFilterQuery):
        """List products with filtering and pagination"""        
        logger.info(f"Listing products")
        try:
            result = self._query_service.list(query)
            return result
        except Exception as e:
            logger.error(f"Error listing products: {str(e)}")
            raise
    
    def search_products(self, search_term: str, page: int = 1, page_size: int = 20, filters: Optional[Dict[str, Any]] = None):
        """
        Search for products by name, description, or brand with advanced filtering.
        
        Args:
            search_term: The search term to look for
            page: Page number (1-indexed)
            page_size: Number of items per page
            filters: Additional filters to apply
            
        Returns:
            Product list DTO with pagination information
        """
        logger.info(f"Searching products with term: {search_term}")
        try:
            # Create search query with advanced filters
            search_filters = filters or {}
            search_filters['search'] = search_term
            
            query = GetProductsByFilterQuery(
                name=search_filters.get('search'),
                category_id=search_filters.get('category_id'),
                brand=search_filters.get('brand'),
                min_price=search_filters.get('min_price'),
                max_price=search_filters.get('max_price'),
                status=search_filters.get('status'),
                in_stock_only=search_filters.get('in_stock_only', False),
                page=page,
                items_per_page=page_size,
                sort_by=search_filters.get('sort_by', 'name'),
                sort_direction=search_filters.get('sort_direction', 'asc')
            )
            
            result = self._query_service.search(query)
            logger.info(f"Found products matching '{search_term}'")
            return result
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            raise

    def create_bulk_products(self, products_data: List[Dict[str, Any]]):
        """
        Create multiple products in a single operation.
        
        Args:
            products_data: List of product data dictionaries
            
        Returns:
            Dictionary with created products and any errors
        """
        logger.info(f"Creating {len(products_data)} products in bulk")
        
        created_products = []
        errors = []
        
        try:
            for i, product_data in enumerate(products_data):
                try:
                    command = CreateProductCommand(**product_data)
                    result = self._create_product_use_case.execute(command)
                    created_products.append(result)
                    logger.info(f"Bulk product {i+1} created successfully: {result.id}")
                except Exception as e:
                    error_info = {
                        "index": i,
                        "product_data": product_data,
                        "error": str(e)
                    }
                    errors.append(error_info)
                    logger.error(f"Failed to create bulk product {i+1}: {str(e)}")
            
            # Commit all successful operations
            if created_products:
                self._uow.commit()
            
            result = {
                "created": created_products,
                "errors": errors,
                "total_attempted": len(products_data),
                "total_created": len(created_products),
                "total_errors": len(errors)
            }
            
            logger.info(f"Bulk creation completed: {len(created_products)} created, {len(errors)} errors")
            return result
            
        except Exception as e:
            self._uow.rollback()
            logger.error(f"Bulk product creation failed: {str(e)}")
            raise

    def get_low_stock_products(self, threshold_percentage: float = 100, page: int = 1, page_size: int = 20):
        """
        Get products with stock levels below the specified threshold.
        
        Args:
            threshold_percentage: Percentage of min_stock to use as threshold
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Product list DTO with low stock products
        """
        logger.info(f"Getting low stock products with threshold: {threshold_percentage}%")
        try:
            result = self._query_service.get_low_stock_products(
                threshold_percentage=threshold_percentage,
                page=page,
                page_size=page_size
            )
            logger.info(f"Found {result.get('total_items', 0)} low stock products")
            return result
        except Exception as e:
            logger.error(f"Error getting low stock products: {str(e)}")
            raise

    def get_expiring_products(self, days_threshold: int = 90, page: int = 1, page_size: int = 20):
        """
        Get products that will expire within the specified number of days.
        
        Args:
            days_threshold: Number of days to look ahead for expiring products
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Product list DTO with expiring products
        """
        logger.info(f"Getting products expiring within {days_threshold} days")
        try:
            result = self._query_service.get_expiring_products(
                days_threshold=days_threshold,
                page=page,
                page_size=page_size
            )
            logger.info(f"Found {result.get('total_items', 0)} products expiring within {days_threshold} days")
            return result
        except Exception as e:
            logger.error(f"Error getting expiring products: {str(e)}")
            raise

    def get_product_stock_status(self, product_id: UUID):
        """
        Get detailed stock status for a specific product.
        
        Args:
            product_id: The ID of the product to check
            
        Returns:
            Detailed stock status information
        """
        logger.info(f"Getting stock status for product: {product_id}")
        try:
            result = self._query_service.get_product_stock_status(product_id)
            logger.info(f"Stock status retrieved for product: {product_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting product stock status: {str(e)}")
            raise

    def get_products_by_category(self, category_id: UUID, page: int = 1, page_size: int = 20):
        """
        Get all products in a specific category.
        
        Args:
            category_id: The ID of the category
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Product list DTO with products in the specified category
        """
        logger.info(f"Getting products for category: {category_id}")
        try:
            query = GetProductsByFilterQuery(
                category_id=category_id,
                page=page,
                items_per_page=page_size
            )
            result = self._query_service.list(query)
            logger.info(f"Found {result.get('total_items', 0)} products in category {category_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting products by category: {str(e)}")
            raise

    def get_product_analytics(self, product_id: UUID):
        """
        Get analytics data for a specific product.
        
        Args:
            product_id: The ID of the product
            
        Returns:
            Analytics data including sales, stock movements, etc.
        """
        logger.info(f"Getting analytics for product: {product_id}")
        try:
            result = self._query_service.get_product_analytics(product_id)
            logger.info(f"Analytics retrieved for product: {product_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting product analytics: {str(e)}")
            raise

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
        try:
            result = self._query_service.validate_product_availability(product_id, requested_quantity)
            logger.info(f"Availability validation completed for product: {product_id}")
            return result
        except Exception as e:
            logger.error(f"Error validating product availability: {str(e)}")
            raise