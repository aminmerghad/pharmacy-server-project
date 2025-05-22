from http import HTTPStatus
from uuid import UUID

from app import container
from app.services.category_service.application.commands.create_category_command import CreateCategoryCommand
from app.services.category_service.application.commands.update_category_command import UpdateCategoryCommand
from app.services.category_service.application.commands.delete_category_command import DeleteCategoryCommand
from app.services.category_service.application.queries.get_category_by_id import GetCategoryByIdQuery
from app.services.category_service.application.queries.get_categories_by_filter import GetCategoriesByFilterQuery
from app.api import category_bp
from app.api.base_routes import BaseRoute
from app.api.category.category_schemas import CategorySchema, CategoryResponseSchema, CategoryFilterSchema, CategoryPaginatedResponseSchema
from typing import Tuple, Dict, Any

@category_bp.route('/')
class CategoryCreateRoute(BaseRoute):
    """
    Route for creating a new category
    """
    
    @category_bp.doc(description="Create a new category")    
    @category_bp.arguments(CategorySchema) 
    @category_bp.response(HTTPStatus.OK, CategoryResponseSchema)   
    def post(self, request_data: Dict[str, Any]) -> Tuple[dict, int]: 
        result = container.category_service().create_category(
            CreateCategoryCommand(
                **request_data
            )
        )        
        return self._success_response(
            data=result,
            message="Category created successfully",
            status_code=HTTPStatus.CREATED
        )

@category_bp.route('/<uuid:category_id>')
class CategoryRoute(BaseRoute):
    """
    Get, update, or delete a specific category
    """
    
    @category_bp.doc(description="Get category details")
    @category_bp.response(HTTPStatus.OK, CategoryResponseSchema)
    def get(self, category_id: UUID) -> Tuple[dict, int]:
        result = container.category_service().get_category(
            GetCategoryByIdQuery(id=category_id)
        )
        
        if not result:
            return self._error_response(
                message="Category not found",
                status_code=HTTPStatus.NOT_FOUND
            )
            
        return self._success_response(
            data=result,
            message="Category retrieved successfully",
            status_code=HTTPStatus.OK
        )
    
    @category_bp.doc(description="Update a category")
    @category_bp.arguments(CategorySchema)
    @category_bp.response(HTTPStatus.OK, CategoryResponseSchema)
    def put(self, request_data: Dict[str, Any], category_id: UUID) -> Tuple[dict, int]:
        # Add category_id to the command
        request_data['id'] = category_id
        
        result = container.category_service().update_category(
            UpdateCategoryCommand(
                **request_data
            )
        )
        
        return self._success_response(
            data=result,
            message="Category updated successfully",
            status_code=HTTPStatus.OK
        )
    
    @category_bp.doc(description="Delete a category")
    def delete(self, category_id: UUID) -> Tuple[dict, int]:
        result = container.category_service().delete_category(
            DeleteCategoryCommand(
                id=category_id
            )
        )
        
        return self._success_response(
            data=result,
            message="Category deleted successfully",
            status_code=HTTPStatus.OK
        )

@category_bp.route('/list')
class CategoryListRoute(BaseRoute):
    """
    List categories with filtering and pagination
    """
    
    @category_bp.doc(description="List categories with filtering and pagination")
    @category_bp.arguments(CategoryFilterSchema, location="query")
    @category_bp.response(HTTPStatus.OK, CategoryPaginatedResponseSchema)
    def get(self, filter_args: Dict[str, Any]) -> Tuple[dict, int]:
        result = container.category_service().list_categories(
            GetCategoriesByFilterQuery(
                **filter_args
            )
        )
        
        return self._success_response(
            data=result,
            message="Categories retrieved successfully",
            status_code=HTTPStatus.OK
        ) 