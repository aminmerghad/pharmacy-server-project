from typing import Optional
from uuid import UUID
from app.services.auth_service.domain.entities import UserEntity
from app.services.auth_service.domain.value_objects import Email,Password
from app.services.auth_service.infrastructure.persistence.models.user_model import UserModel

class UserRepository:
    def __init__(self, session):
        self._session = session

    def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        user = self._session.query(UserModel).filter_by(id=user_id).first()
        return self._to_entity(user) if user else None

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        user = self._session.query(UserModel).filter_by(username=username).first()
        return self._to_entity(user) if user else None

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        user = self._session.query(UserModel).filter_by(email=email).first()
        return self._to_entity(user) if user else None
    
    def get_by_phone(self, phone: str) -> Optional[UserEntity]:
        user = self._session.query(UserModel).filter_by(phone=phone).first()
        return self._to_entity(user) if user else None



    def add(self, user: UserEntity) -> UserEntity:

        user_model = UserModel(
            username=user.username,
            email=user.email.address,
            full_name=user.full_name,
            phone=user.phone,
            password=user.password.hashed,
            is_admin=user.is_admin,
            is_active=user.is_active
        )    
        self._session.add(user_model)
        self._session.flush()
                
        return self._to_entity(user_model)
    def is_existing_admin(self,username: str) -> bool:
        user = UserModel.query.filter_by(
            username=username, 
            is_admin=True
        ).first()        
        return True if user else False
    def update(self,user:UserEntity):
        user_model=UserModel.query.filter_by(id=user.id).first()
        user_model.health_care_center_id=user.health_care_center_id
        self._session.flush()



    def _to_entity(self, model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            username=model.username,
            email=Email(model.email),
            password=Password.from_hash(model.password),
            full_name=model.full_name,
            phone=model.phone,
            is_admin=model.is_admin,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            health_care_center_id=model.health_care_center_id
        )