from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from app.services.auth_service.domain.entities import HealthCareCenterEntity
from app.services.auth_service.infrastructure.persistence.models.health_care_center_model import HealthCareCenterModel

class HealthCareCenterRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, entity: HealthCareCenterEntity) -> HealthCareCenterEntity:
        model = HealthCareCenterModel(
            name=entity.name,
            address=entity.address,
            phone=entity.phone,
            email=entity.email,
            license_number=entity.license_number
        )
        self._session.add(model)
        self._session.flush()
        return self._to_entity(model)

    def get_by_id(self, center_id: UUID) -> Optional[HealthCareCenterEntity]:
        model = self._session.query(HealthCareCenterModel).filter(
            HealthCareCenterModel.id == center_id
        ).first()
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> Optional[HealthCareCenterEntity]:
        model = self._session.query(HealthCareCenterModel).filter(
            HealthCareCenterModel.email == email
        ).first()
        return self._to_entity(model) if model else None
        
    def get_by_phone(self, phone: str) -> Optional[HealthCareCenterEntity]:
        model = self._session.query(HealthCareCenterModel).filter(
            HealthCareCenterModel.phone == phone
        ).first()
        return self._to_entity(model) if model else None
        
    def get_by_license_number(self, license_number: str) -> Optional[HealthCareCenterEntity]:
        model = self._session.query(HealthCareCenterModel).filter(
            HealthCareCenterModel.license_number == license_number
        ).first()
        return self._to_entity(model) if model else None

    def get_all(self) -> List[HealthCareCenterEntity]:
        models = self._session.query(HealthCareCenterModel).all()
        return [self._to_entity(model) for model in models]

    def update(self, entity: HealthCareCenterEntity) -> HealthCareCenterEntity:
        model = self._session.query(HealthCareCenterModel).filter(
            HealthCareCenterModel.id == entity.id
        ).first()
        
        if not model:
            raise ValueError(f"Health Care Center with id {entity.id} not found")

        model.name = entity.name
        model.address = entity.address
        model.phone = entity.phone
        model.email = entity.email
        model.license_number = entity.license_number
        model.is_active = entity.is_active
        
        self._session.flush()
        return self._to_entity(model)

    def _to_entity(self, model: HealthCareCenterModel) -> HealthCareCenterEntity:
        return HealthCareCenterEntity(
            id=model.id,
            name=model.name,
            address=model.address,
            phone=model.phone,
            email=model.email,
            license_number=model.license_number,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        ) 