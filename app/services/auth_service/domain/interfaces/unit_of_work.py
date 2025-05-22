from sqlalchemy.orm import Session
from app.services.auth_service.infrastructure.persistence.repositories.access_code_repository import AccessCodeRepository
from app.services.auth_service.infrastructure.persistence.repositories.health_care_center_repository import HealthCareCenterRepository
from app.services.auth_service.infrastructure.security.jwt_manager import JWTManager
from app.shared.application.events.event_bus import EventBus
from app.services.auth_service.infrastructure.persistence.repositories.user_repository import UserRepository

class UnitOfWork:
    def __init__(self, session: Session, event_bus: EventBus):
        pass
    user: UserRepository
    jwt_manager: JWTManager
    access_code: AccessCodeRepository
    health_care_center:HealthCareCenterRepository
    def commit(self):
        pass
    
    def publish(self, event: any):
        pass
    
    def rollback(self):
        pass