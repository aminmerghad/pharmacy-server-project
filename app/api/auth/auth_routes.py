from http import HTTPStatus
from uuid import UUID

from pydantic import BaseModel
from app.api import auth_bp
from flask_smorest import abort
from app.api.auth.dto.auth_dto import UserRegisterDto
from app.api.base_routes import BaseRoute
from flask_jwt_extended import jwt_required
from app.extensions import container
from app.api.auth.schemas import AdminRegistrationErrorResponseSchema, AdminRegistrationResponseSchema, AdminRegistrationSchema, LogInResponseSchema, LoginSchema, UserRegistrationSchema, UserResponseSchema
from app.services.auth_service.application.commands import CreateUserCommand, CreateOrGetHealthCareCenterCommand, LoginCommand, RegisterUserCommand, UserUpdateCommand,RegisterUserCommand, UserUpdateCommand,AdminRegistrationCommand
from app.services.auth_service.application.queries import AccessCodeValidationQuery
from app.services.auth_service.infrastructure.persistence.models.user_model import UserModel
from app.shared.domain.schema.common_errors import ErrorResponseSchema
from app.shared.utils.api_response import APIResponse


@auth_bp.route('/admin/register')
class AdminRegister(BaseRoute):

    @auth_bp.doc(summary="Register admin",description="Register an admin user with secure initialization key")
    @auth_bp.arguments(AdminRegistrationSchema)
    @auth_bp.response(HTTPStatus.UNAUTHORIZED, AdminRegistrationErrorResponseSchema)
    @auth_bp.response(HTTPStatus.CONFLICT, AdminRegistrationErrorResponseSchema)
    @auth_bp.response(HTTPStatus.CREATED, AdminRegistrationResponseSchema)
    def post(self, admin_data):
        """Register an admin user with secure initialization key"""
        command = AdminRegistrationCommand(**admin_data)   
        adminCreatedDTO = container.auth_service().register_admin(command)
        return self._success_response(
            data=adminCreatedDTO,
            message="Admin registered successfully",
            status_code=HTTPStatus.CREATED
        )

@auth_bp.route('/login')
class UserLogin(BaseRoute):
    @auth_bp.doc(summary="Login user",description="Login a user using username and password")
    @auth_bp.arguments(LoginSchema)
    @auth_bp.response(HTTPStatus.UNAUTHORIZED, ErrorResponseSchema)
    @auth_bp.response(HTTPStatus.OK, LogInResponseSchema)
    def post(self, user_data):
        command = LoginCommand(**user_data)
        login_response = container.auth_service().login(command)
        return self._success_response(
            data=login_response,
            message="User logged in successfully",
            status_code=HTTPStatus.OK            
        )

@auth_bp.route('/register')
class UserRegister(BaseRoute):   
    @auth_bp.doc(summary="Register user",description="Register a user with a valid access code")
    @auth_bp.arguments(UserRegistrationSchema)
    @auth_bp.response(HTTPStatus.NOT_FOUND, ErrorResponseSchema,description="Access code not found/Expired access code")
    @auth_bp.response(HTTPStatus.CONFLICT, ErrorResponseSchema,description="User already exists")
    @auth_bp.response(HTTPStatus.CREATED, UserResponseSchema,description="User registered successfully")    
    def post(self, user_data):
        dto = UserRegisterDto(**user_data)
        register_user_command = RegisterUserCommand(dto)
        user_registered = container.auth_service().register(register_user_command)
        return self._success_response(
            data=user_registered,
            message="User registered successfully",
            status_code=HTTPStatus.CREATED
        )

@auth_bp.route('/refresh')
class TokenRefresh(BaseRoute):
    @jwt_required(refresh=True)
    @auth_bp.response(HTTPStatus.OK, UserResponseSchema)
    def post(self):
        """Refresh access token"""
        result = container.auth_service().refresh_token()
        return self._success_response(
            data=result,
            message="Token refreshed successfully",
            status_code=HTTPStatus.OK
        )

@auth_bp.route('/user/<uuid:user_id>')
class UserUpdate(BaseRoute):
    @jwt_required()
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message="User not found")
        return APIResponse.success(data=user, message="User fetched successfully")

    @jwt_required()
    def put(self, user_id, user_data):
        command = UserUpdateCommand(**user_data)
        user_updated = container.auth_service().update_user(user_id, command)
        return self._success_response(
            data=user_updated,
            message="User updated successfully",
            status_code=HTTPStatus.OK
        )

    @jwt_required()
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message="User not found")
        user.deactivate()
        return APIResponse.success(message="User deleted successfully")

class UserDto(BaseModel):
    id: UUID
    username: str
    full_name: str
    phone: str
    email: str

@auth_bp.route('/users')
class UserList(BaseRoute):
    def get(self):
        users = UserModel.query.all()
        users_dto = [UserDto(
            id=user.id,
            username=user.username, 
            full_name=user.full_name, 
            phone=user.phone, 
            email=user.email           
           ).model_dump() for user in users]
        return APIResponse.success(data=users_dto, message="Users fetched successfully")
    





