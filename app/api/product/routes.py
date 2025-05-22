from http import HTTPStatus
from uuid import UUID

from app import container
from app.services.product_service.application.commands.create_product_command import CreateProductCommand
from app.services.product_service.application.commands.update_product_command import UpdateProductCommand
from app.services.product_service.application.commands.delete_product_command import DeleteProductCommand
from app.services.product_service.application.queries.get_product_by_id import GetProductByIdQuery
from app.services.product_service.application.queries.get_products_by_filter import GetProductsByFilterQuery
# from app.api.decorators.error_handler import handle_exceptions
from app.api import product_bp
from app.api.base_routes import BaseRoute
from app.api.product.product_shemas import ProductSchema, ProductResponseSchema, ProductFilterSchema, ProductPaginatedResponseSchema, ProductSearchSchema, BulkProductSchema
from typing import Tuple, Dict, Any

@product_bp.route('/')
class ProductCreateRoute(BaseRoute):
    """
    @require_admin
    @product_bp.arguments(ProductSchema)
    @product_bp.response(HTTPStatus.OK, ProductResponseSchema)   
    responses:
      201:
        description: Product created successfully
      400:
        description: Invalid input data
      401:
        description: Unauthorized
      403:
        description: Forbidden
    """     
    
    @product_bp.doc(description="Create a new product with inventory details")    
    @product_bp.arguments(ProductSchema) 
    @product_bp.response(HTTPStatus.CREATED, ProductResponseSchema)   
    def post(self, request_data: Dict[str, Any]) -> Tuple[dict, int]: 
        """Create a new product"""
        try:
            result = container.product_service().create_product(
                CreateProductCommand(**request_data)
            )        
            return self._success_response(
                data=result,
                message="Product created successfully",
                status_code=HTTPStatus.CREATED
            )
        except Exception as e:
            return self._error_response(
                message=f"Failed to create product: {str(e)}",
                status_code=HTTPStatus.BAD_REQUEST
            )

@product_bp.route('/<uuid:product_id>')
class ProductRoute(BaseRoute):
    """
    Get, update, or delete a specific product
    """
    
    @product_bp.doc(description="Get product details")
    @product_bp.response(HTTPStatus.OK, ProductResponseSchema)
    def get(self, product_id: UUID):
        result = container.product_service().get_product(
            GetProductByIdQuery(id=product_id)
            )
        
        if not result:
            return self._error_response(
                message="Product not found",
                status_code=HTTPStatus.NOT_FOUND
            )
            
        return self._success_response(
            data=result,
            message="Product retrieved successfully",
            status_code=HTTPStatus.OK
        )
    
    @product_bp.doc(description="Update a product")
    @product_bp.arguments(ProductSchema)
    @product_bp.response(HTTPStatus.OK, ProductResponseSchema)
    def put(self, request_data: Dict[str, Any],product_id: UUID ) -> Tuple[dict, int]:
        """Update an existing product"""
        try:
            # Add product_id to the command
            request_data['id'] = product_id
            
            result = container.product_service().update_product(
                UpdateProductCommand(**request_data)
            )
            
            return self._success_response(
                data=result,
                message="Product updated successfully",
                status_code=HTTPStatus.OK
            )
        except Exception as e:
            return self._error_response(
                message=f"Failed to update product: {str(e)}",
                status_code=HTTPStatus.BAD_REQUEST
            )
    
    @product_bp.doc(description="Delete a product")
    @product_bp.response(HTTPStatus.OK)
    def delete(self, product_id: UUID) -> Tuple[dict, int]:
        """Delete a product"""
        try:
            result = container.product_service().delete_product(
                DeleteProductCommand(id=product_id)
            )
            
            return self._success_response(
                data=result,
                message="Product deleted successfully",
                status_code=HTTPStatus.OK
            )
        except Exception as e:
            return self._error_response(
                message=f"Failed to delete product: {str(e)}",
                status_code=HTTPStatus.BAD_REQUEST
            )

@product_bp.route('/list')
class ProductListRoute(BaseRoute):
    """
    Product listing with filtering and pagination
    """
    
    @product_bp.doc(description="List products with advanced filtering and pagination")
    @product_bp.arguments(ProductFilterSchema, location="query")
    @product_bp.response(HTTPStatus.OK, ProductPaginatedResponseSchema)
    def get(self, filter_args: Dict[str, Any]) -> Tuple[dict, int]:
        """List products with filtering and pagination"""
        try:
            result = container.product_service().list_products(
                GetProductsByFilterQuery(**filter_args)
            )

            return self._success_response(
                data=result,
                message="Products retrieved successfully",
                status_code=HTTPStatus.OK
            )
        except Exception as e:
            return self._error_response(
                message=f"Failed to retrieve products: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

@product_bp.route('/search')
class ProductSearchRoute(BaseRoute):
    """
    Advanced product search functionality
    """
    
    @product_bp.doc(description="Search products by name, description, brand, or other attributes")
    @product_bp.arguments(ProductSearchSchema, location="query")
    @product_bp.response(HTTPStatus.OK, ProductPaginatedResponseSchema)
    def get(self, search_args: Dict[str, Any]) -> Tuple[dict, int]:
        """Search products with advanced criteria"""
        try:
            result = container.product_service().search_products(
                search_term=search_args.get('search', ''),
                page=search_args.get('page', 1),
                page_size=search_args.get('page_size', 20),
                filters=search_args
            )
            
            return self._success_response(
                data=result,
                message="Product search completed successfully",
                status_code=HTTPStatus.OK
            )
        except Exception as e:
            return self._error_response(
                message=f"Search failed: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

@product_bp.route('/bulk')
class ProductBulkRoute(BaseRoute):
    """
    Bulk operations for products
    """
    
    @product_bp.doc(description="Create multiple products in a single operation")
    @product_bp.arguments(BulkProductSchema)
    @product_bp.response(HTTPStatus.CREATED, ProductPaginatedResponseSchema)
    def post(self, request_data: Dict[str, Any]) -> Tuple[dict, int]:
        """Create multiple products at once"""
        try:
            results = container.product_service().create_bulk_products(
                request_data.get('products', [])
            )
            
            return self._success_response(
                data=results,
                message=f"Successfully created {len(results['created'])} products",
                status_code=HTTPStatus.CREATED
            )
        except Exception as e:
            return self._error_response(
                message=f"Bulk creation failed: {str(e)}",
                status_code=HTTPStatus.BAD_REQUEST
            )

@product_bp.route('/categories/<uuid:category_id>')
class ProductByCategoryRoute(BaseRoute):
    """
    Get products by category
    """
    
    @product_bp.doc(description="Get all products in a specific category")
    @product_bp.arguments(ProductFilterSchema, location="query")
    @product_bp.response(HTTPStatus.OK, ProductPaginatedResponseSchema)
    def get(self, category_id: UUID, filter_args: Dict[str, Any]) -> Tuple[dict, int]:
        """Get products by category with optional additional filtering"""
        try:
            # Add category filter to existing filters
            filter_args['category_id'] = category_id
            
            result = container.product_service().list_products(
                GetProductsByFilterQuery(**filter_args)
            )
            
            return self._success_response(
                data=result,
                message=f"Products retrieved for category {category_id}",
                status_code=HTTPStatus.OK
            )
        except Exception as e:
            return self._error_response(
                message=f"Failed to retrieve category products: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

@product_bp.route('/low-stock')
class LowStockProductsRoute(BaseRoute):
    """
    Get products with low stock levels
    """
    
    @product_bp.doc(description="Get products that are running low on stock")
    @product_bp.arguments(ProductFilterSchema, location="query")
    @product_bp.response(HTTPStatus.OK, ProductPaginatedResponseSchema)
    def get(self, filter_args: Dict[str, Any]) -> Tuple[dict, int]:
        """Get products with stock below minimum threshold"""
        try:
            result = container.product_service().get_low_stock_products(
                threshold_percentage=filter_args.get('threshold_percentage', 100),
                page=filter_args.get('page', 1),
                page_size=filter_args.get('page_size', 20)
            )
            
            return self._success_response(
                data=result,
                message="Low stock products retrieved successfully",
                status_code=HTTPStatus.OK
            )
        except Exception as e:
            return self._error_response(
                message=f"Failed to retrieve low stock products: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

@product_bp.route('/expiring')
class ExpiringProductsRoute(BaseRoute):
    """
    Get products that are expiring soon
    """
    
    @product_bp.doc(description="Get products that will expire within specified days")
    @product_bp.arguments(ProductFilterSchema, location="query")
    @product_bp.response(HTTPStatus.OK, ProductPaginatedResponseSchema)
    def get(self, filter_args: Dict[str, Any]) -> Tuple[dict, int]:
        """Get products expiring within specified timeframe"""
        try:
            result = container.product_service().get_expiring_products(
                days_threshold=filter_args.get('days_threshold', 90),
                page=filter_args.get('page', 1),
                page_size=filter_args.get('page_size', 20)
            )
            
            return self._success_response(
                data=result,
                message="Expiring products retrieved successfully",
                status_code=HTTPStatus.OK
            )
        except Exception as e:
            return self._error_response(
                message=f"Failed to retrieve expiring products: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

@product_bp.route('/<uuid:product_id>/stock-status')
class ProductStockStatusRoute(BaseRoute):
    """
    Get detailed stock status for a product
    """
    
    @product_bp.doc(description="Get detailed stock status and availability for a product")
    @product_bp.response(HTTPStatus.OK)
    def get(self, product_id: UUID) -> Tuple[dict, int]:
        """Get detailed stock status for a specific product"""
        try:
            result = container.product_service().get_product_stock_status(product_id)
            
            return self._success_response(
                data=result,
                message="Product stock status retrieved successfully",
                status_code=HTTPStatus.OK
            )
        except Exception as e:
            return self._error_response(
                message=f"Failed to retrieve stock status: {str(e)}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )
