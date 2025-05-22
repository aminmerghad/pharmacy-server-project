from http import HTTPStatus
from typing import Dict, Any, Tuple
from uuid import UUID

from flask_smorest import abort
from flask_jwt_extended import jwt_required
from pydantic import BaseModel

from app.api import auth_bp
from app.api.base_routes import BaseRoute
from app.extensions import container
from app.services.auth_service.application.queries.health_care.list_centers_query import ListCentersByFilterQuery
from app.services.auth_service.application.queries.health_care.get_center_by_id_query import GetHealthCareCenterByIdQuery
from app.shared.utils.api_response import APIResponse
from app.api.auth.schemas.health_care import HealthCareCenterSchema, HealthCareCenterFilterSchema, HealthCareCenterResponseSchema, HealthCareCenterListResponseSchema
from app.services.auth_service.application.commands.health_care_center.create_center_command import CreateOrGetHealthCareCenterCommand
from app.services.auth_service.application.commands.health_care_center.update_center_command import UpdateHealthCareCenterCommand
from app.services.auth_service.application.commands.health_care_center.delete_center_command import DeleteHealthCareCenterCommand
from app.services.auth_service.infrastructure.persistence.models.health_care_center_model import HealthCareCenterModel
from app.shared.domain.schema.common_errors import ErrorResponseSchema


class HealthCareCenterDto(BaseModel):
    id: UUID
    name: str
    address: str
    phone: str
    email: str
    license_number: str
    is_active: bool


@auth_bp.route('/health-care-centers')
class HealthCareCenterList(BaseRoute):
    @auth_bp.doc(summary="Get all health care centers", description="Get a list of all health care centers with optional filtering")
    @auth_bp.arguments(HealthCareCenterFilterSchema, location="query")
    @auth_bp.response(HTTPStatus.OK, HealthCareCenterListResponseSchema)
    @jwt_required()
    def get(self, filter_args: Dict[str, Any]) -> Tuple[dict, int]:
        """Get all health care centers with optional filtering"""
        result = container.auth_service().list_centers_by_filter(
            ListCentersByFilterQuery(**filter_args)
        )
        
        return self._success_response(
            data=result,
            message=f"Retrieved {len(result['items'] if 'items' in result else [])} health care centers",
            status_code=HTTPStatus.OK
        )
    
    @auth_bp.doc(summary="Create health care center", description="Create a new health care center")
    @auth_bp.arguments(HealthCareCenterSchema)
    @auth_bp.response(HTTPStatus.CONFLICT, ErrorResponseSchema, description="Health care center already exists")
    @auth_bp.response(HTTPStatus.CREATED, HealthCareCenterResponseSchema)
    @jwt_required()
    def post(self, center_data: Dict[str, Any]) -> Tuple[dict, int]:
        """Create a new health care center"""
        result = container.auth_service().create_health_care_center(
            CreateOrGetHealthCareCenterCommand(**center_data)
        )
        
        return self._success_response(
            data=result,
            message="Health care center created successfully",
            status_code=HTTPStatus.CREATED
        )


@auth_bp.route('/health-care-centers/<uuid:center_id>')
class HealthCareCenter(BaseRoute):
    @auth_bp.doc(summary="Get health care center", description="Get a health care center by ID")
    @auth_bp.response(HTTPStatus.NOT_FOUND, ErrorResponseSchema, description="Health care center not found")
    @auth_bp.response(HTTPStatus.OK, HealthCareCenterResponseSchema)
    @jwt_required()
    def get(self, center_id: UUID) -> Tuple[dict, int]:
        """Get a health care center by ID"""
        result = container.auth_service().get_health_care_center(
            GetHealthCareCenterByIdQuery(id=center_id)
        )
        
        if not result:
            return self._error_response(
                message="Health care center not found",
                status_code=HTTPStatus.NOT_FOUND
            )
        
        return self._success_response(
            data=result,
            message="Health care center retrieved successfully",
            status_code=HTTPStatus.OK
        )
    
    @auth_bp.doc(summary="Update health care center", description="Update a health care center by ID")
    @auth_bp.arguments(HealthCareCenterSchema)
    @auth_bp.response(HTTPStatus.NOT_FOUND, ErrorResponseSchema, description="Health care center not found")
    @auth_bp.response(HTTPStatus.OK, HealthCareCenterResponseSchema)
    @jwt_required()
    def put(self, center_data: Dict[str, Any], center_id: UUID) -> Tuple[dict, int]:
        """Update a health care center by ID"""
        # Add ID to the data
        center_data['id'] = center_id
        
        # Create command and execute
        result = container.auth_service().update_health_care_center(
            UpdateHealthCareCenterCommand(**center_data)
        )
        
        return self._success_response(
            data=result,
            message="Health care center updated successfully",
            status_code=HTTPStatus.OK
        )
    
    @auth_bp.doc(summary="Delete health care center", description="Deactivate a health care center by ID")
    @auth_bp.response(HTTPStatus.NOT_FOUND, ErrorResponseSchema, description="Health care center not found")
    @auth_bp.response(HTTPStatus.OK, HealthCareCenterResponseSchema)
    @jwt_required()
    def delete(self, center_id: UUID) -> Tuple[dict, int]:
        """Deactivate a health care center by ID"""
        result = container.auth_service().delete_health_care_center(
            DeleteHealthCareCenterCommand(id=center_id)
        )
        
        return self._success_response(
            data=result,
            message="Health care center deactivated successfully",
            status_code=HTTPStatus.OK
        )


@auth_bp.route('/health-care-centers/search')
class HealthCareCenterSearch(BaseRoute):
    @auth_bp.doc(summary="Search health care centers", description="Search health care centers by name, email, or license number")
    @auth_bp.arguments(HealthCareCenterFilterSchema, location="query")
    @auth_bp.response(HTTPStatus.OK, HealthCareCenterListResponseSchema)
    @jwt_required()
    def get(self, search_args: Dict[str, Any]) -> Tuple[dict, int]:
        """Search health care centers"""
        # Extract search term from arguments
        search_term = search_args.get('search', '')
        
        # Add search term to query parameters
        result = container.auth_service().list_centers_by_filter(
            ListCentersByFilterQuery(search=search_term, **search_args)
        )
        
        return self._success_response(
            data=result,
            message=f"Found {len(result['items'] if 'items' in result else [])} health care centers matching search criteria",
            status_code=HTTPStatus.OK
        )