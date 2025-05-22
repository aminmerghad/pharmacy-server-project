from app.services.auth_service.infrastructure.persistence.repositories.access_code_repository import AccessCodeRepository
from app.services.auth_service.infrastructure.persistence.repositories.health_care_center_repository import HealthCareCenterRepository
from app.services.auth_service.infrastructure.security.jwt_manager import JWTManager
from app.shared.application.events.event_bus import EventBus
from app.services.auth_service.domain.interfaces.unit_of_work import UnitOfWork
from sqlalchemy.orm import Session

from app.services.auth_service.infrastructure.persistence.repositories.user_repository import UserRepository


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: Session, event_bus: EventBus = None):
        self.db_session = session
        self.event_bus = event_bus
        self._user = None
        self._jwt_manager=None
        self._access_code=None
        self._health_care_center=None
    @property
    def jwt_manager(self):
        if not self._jwt_manager:
            self._jwt_manager = JWTManager()
        return self._jwt_manager
    
    @property
    def access_code(self):
        if not self._access_code:
            self._access_code = AccessCodeRepository(self.db_session)
        return self._access_code


    @property
    def user(self):
        if not self._user:
            self._user = UserRepository(self.db_session)
        return self._user

    @property
    def health_care_center(self):
        if not self._health_care_center:
            self._health_care_center = HealthCareCenterRepository(self.db_session)
        return self._health_care_center

    def commit(self):
        self.db_session.commit()

    def publish(self, event: any):
        self.event_bus.publish(event)

    def rollback(self):
        self.db_session.rollback()

    
