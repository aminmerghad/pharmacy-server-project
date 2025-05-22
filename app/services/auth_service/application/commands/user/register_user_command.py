from dataclasses import dataclass
from app.services.auth_service.application.commands import CreateUserCommand,CreateOrGetHealthCareCenterCommand
from app.services.auth_service.application.queries import AccessCodeValidationQuery


@dataclass
class RegisterUserCommand:
    user_command: CreateUserCommand    
    access_code_query: AccessCodeValidationQuery
    center_command: CreateOrGetHealthCareCenterCommand = None

    def __init__(self,user_data):
        self.user_command = CreateUserCommand(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            username=user_data.email
        )
        self.access_code_query = AccessCodeValidationQuery(user_data.code)
        self.center_command = CreateOrGetHealthCareCenterCommand(
            name=user_data.health_care_center.name,
            address=user_data.health_care_center.address,
            phone=user_data.health_care_center.phone,
            email=user_data.health_care_center.email,
            license_number=user_data.health_care_center.license_number
        ) if user_data.health_care_center else None



