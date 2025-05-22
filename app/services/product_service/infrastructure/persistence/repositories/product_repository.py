from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, desc, asc, func
import logging

from app.services.product_service.domain.entities.product_entity import ProductEntity
from app.services.product_service.infrastructure.persistence.models.product_model import ProductModel
from app.services.product_service.domain.interfaces.repository import ProductRepository as ProductRepositoryInterface

# Configure logger
logger = logging.getLogger(__name__)

class ProductRepository(ProductRepositoryInterface):
    def __init__(self, session: Session):
        self._session = session

    def add(self, entity: ProductEntity) -> ProductEntity:
        """Add a new product to the database"""
        logger.info(f"Adding product with name: {entity.name}")
        model = ProductModel(
            name=entity.name,
            description=entity.description,
            category_id=entity.category_id,
            brand=entity.brand,
            dosage_form=entity.dosage_form,
            strength=entity.strength,
            package=entity.package,
            image_url=entity.image_url,
            status=entity.status
        )
        self._session.add(model)
        self._session.flush()
        logger.info(f"Product added with ID: {model.id}")
        return self._to_domain(model)

    def _to_domain(self, model: ProductModel) -> Optional[ProductEntity]:
        """Convert database model to domain entity"""
        if not model:
            return None
            
        return ProductEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            brand=model.brand,
            dosage_form=model.dosage_form,
            package=model.package,
            image_url=model.image_url,
            strength=model.strength,
            category_id=model.category_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            status=model.status
        )

    def get_by_id(self, product_id: UUID) -> Optional[ProductEntity]:
        """Get a product by ID"""
        logger.info(f"Getting product with ID: {product_id}")
        model = self._session.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not model:
            logger.info(f"Product with ID {product_id} not found")
            return None
        
        logger.info(f"Product found: {model.name}")
        return self._to_domain(model)

    def update(self, entity: ProductEntity) -> ProductEntity:
        """Update an existing product"""
        logger.info(f"Updating product with ID: {entity.id}")
        model = self._session.query(ProductModel).filter(ProductModel.id == entity.id).first()
        
        if not model:
            logger.error(f"Product with ID {entity.id} not found for update")
            raise ValueError(f"Product with ID {entity.id} not found")

        model.name = entity.name
        model.description = entity.description
        model.category_id = entity.category_id
        model.brand = entity.brand
        model.dosage_form = entity.dosage_form
        model.strength = entity.strength
        model.package = entity.package
        model.image_url = entity.image_url
        model.status = entity.status
        model.updated_at = datetime.utcnow()
        
        self._session.flush()
        logger.info(f"Product updated successfully: {model.id}")
        return self._to_domain(model)

    def delete(self, product_id: UUID) -> bool:
        """Delete a product by its ID"""
        logger.info(f"Deleting product with ID: {product_id}")
        model = self._session.query(ProductModel).filter(ProductModel.id == product_id).first()
        
        if not model:
            logger.info(f"Product with ID {product_id} not found for deletion")
            return False
        
        # Hard delete approach
        self._session.delete(model)
        self._session.flush()
        logger.info(f"Product deleted successfully: {product_id}")
        return True

    def list(self, filters: Optional[Dict[str, Any]] = None, 
             page: int = 1, 
             page_size: int = 20) -> List[ProductEntity]:
        """
        List products with optional filtering and pagination.
        
        Args:
            filters: Optional dictionary of filter criteria
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            List of product entities matching the criteria
        """
        logger.info(f"Listing products with filters: {filters}, page: {page}, page_size: {page_size}")
        try:
            query = self._session.query(ProductModel)
            
            if filters:
                filter_conditions = []
                
                # Apply filters
                if 'name' in filters:
                    filter_conditions.append(ProductModel.name.ilike(f"%{filters['name']}%"))
                
                if 'brand' in filters:
                    filter_conditions.append(ProductModel.brand.ilike(f"%{filters['brand']}%"))
                
                if 'category_id' in filters:
                    filter_conditions.append(ProductModel.category_id == filters['category_id'])
                
                if 'status' in filters:
                    filter_conditions.append(ProductModel.status == filters['status'])
                
                if 'search' in filters:
                    search_term = f"%{filters['search']}%"
                    filter_conditions.append(
                        or_(
                            ProductModel.name.ilike(search_term),
                            ProductModel.description.ilike(search_term),
                            ProductModel.brand.ilike(search_term),
                            ProductModel.dosage_form.ilike(search_term)
                        )
                    )
                
                if filter_conditions:
                    query = query.filter(and_(*filter_conditions))
            
            # Get total items count before pagination for metadata
            total_items = query.count()
            
            # Apply pagination
            offset = (page - 1) * page_size
            query = query.order_by(ProductModel.name).offset(offset).limit(page_size)
            
            # Convert models to entities
            results = [self._to_domain(model) for model in query.all()]
            
            logger.info(f"Listed {len(results)} products (page {page}, page_size {page_size}, total items: {total_items})")
            return results
            
        except Exception as e:
            logger.error(f"Error listing products: {str(e)}", exc_info=True)
            raise

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count products matching the specified filters.
        
        Args:
            filters: Optional dictionary of filter criteria
            
        Returns:
            Count of products matching the criteria
        """
        logger.info(f"Counting products with filters: {filters}")
        try:
            query = self._session.query(func.count(ProductModel.id))
            
            if filters:
                filter_conditions = []
                
                # Apply the same filters as list method
                if 'name' in filters:
                    filter_conditions.append(ProductModel.name.ilike(f"%{filters['name']}%"))
                
                if 'brand' in filters:
                    filter_conditions.append(ProductModel.brand.ilike(f"%{filters['brand']}%"))
                
                if 'category_id' in filters:
                    filter_conditions.append(ProductModel.category_id == filters['category_id'])
                
                if 'status' in filters:
                    filter_conditions.append(ProductModel.status == filters['status'])
                
                if 'search' in filters:
                    search_term = f"%{filters['search']}%"
                    filter_conditions.append(
                        or_(
                            ProductModel.name.ilike(search_term),
                            ProductModel.description.ilike(search_term),
                            ProductModel.brand.ilike(search_term),
                            ProductModel.dosage_form.ilike(search_term)
                        )
                    )
                
                if filter_conditions:
                    query = query.filter(and_(*filter_conditions))
            
            count = query.scalar()
            logger.info(f"Counted {count} products matching filters")
            return count
            
        except Exception as e:
            logger.error(f"Error counting products: {str(e)}", exc_info=True)
            raise

    # def get_by_sku(self, sku: str) -> Optional[ProductEntity]:
    #     """Get a product by SKU"""
    #     model = self._session.query(ProductModel).filter(ProductModel.sku == sku).first()
    #     return self._to_domain(model) if model else None

    # def get_by_barcode(self, barcode: str) -> Optional[ProductEntity]:
    #     """Get a product by barcode"""
    #     model = self._session.query(ProductModel).filter(ProductModel.barcode == barcode).first()
    #     return self._to_domain(model) if model else None

    # def get_all(self) -> List[ProductEntity]:
    #     """Get all active products"""
    #     models = self._session.query(ProductModel).filter(ProductModel.is_active == True).all()
    #     return [self._to_domain(model) for model in models]

    # def hard_delete(self, id: UUID) -> bool:
    #     """Hard delete a product (use with caution)"""
    #     model = self._session.query(ProductModel).filter(ProductModel.id == id).first()
    #     if not model:
    #         return False
    #     self._session.delete(model)
    #     return True

    # def get_expiring_products(self, days_threshold: int = 90) -> List[Dict[str, Any]]:
    #     """Get products with batches expiring within the specified days"""
    #     expiry_date = datetime.utcnow() + timedelta(days=days_threshold)
        
    #     query = self._session.query(
    #         ProductModel,
    #         BatchModel.expiry_date,
    #         BatchModel.quantity,
    #         func.sum(BatchModel.quantity).label('total_expiring')
    #     ).join(
    #         InventoryModel, ProductModel.id == InventoryModel.product_id
    #     ).join(
    #         BatchModel, InventoryModel.id == BatchModel.inventory_id
    #     ).filter(
    #         BatchModel.expiry_date <= expiry_date,
    #         BatchModel.expiry_date > datetime.utcnow(),
    #         BatchModel.quantity > 0,
    #         ProductModel.is_active == True
    #     ).group_by(
    #         ProductModel.id, BatchModel.expiry_date, BatchModel.quantity
    #     ).order_by(
    #         BatchModel.expiry_date
    #     )
        
    #     results = []
    #     for product, expiry_date, quantity, total_expiring in query.all():
    #         results.append({
    #             'product': self._to_domain(product),
    #             'expiry_date': expiry_date,
    #             'quantity': quantity,
    #             'total_expiring': total_expiring
    #         })
            
    #     return results
    
    # def get_expired_products(self) -> List[Dict[str, Any]]:
    #     """Get products with expired batches that still have stock"""
    #     query = self._session.query(
    #         ProductModel,
    #         BatchModel.expiry_date,
    #         BatchModel.quantity,
    #         func.sum(BatchModel.quantity).label('total_expired')
    #     ).join(
    #         InventoryModel, ProductModel.id == InventoryModel.product_id
    #     ).join(
    #         BatchModel, InventoryModel.id == BatchModel.inventory_id
    #     ).filter(
    #         BatchModel.expiry_date < datetime.utcnow(),
    #         BatchModel.quantity > 0,
    #         ProductModel.is_active == True
    #     ).group_by(
    #         ProductModel.id, BatchModel.expiry_date, BatchModel.quantity
    #     ).order_by(
    #         BatchModel.expiry_date
    #     )
        
    #     results = []
    #     for product, expiry_date, quantity, total_expired in query.all():
    #         results.append({
    #             'product': self._to_domain(product),
    #             'expiry_date': expiry_date,
    #             'quantity': quantity,
    #             'total_expired': total_expired
    #         })
            
    #     return results