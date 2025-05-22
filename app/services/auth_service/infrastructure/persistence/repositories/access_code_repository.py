from typing import List, Optional
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.services.auth_service.domain.entities.access_code_entity import AccessCodeEntity
from app.services.auth_service.infrastructure.persistence.models.access_code_model import AccessCodeModel

class AccessCodeRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, entity: AccessCodeEntity) -> AccessCodeEntity:
        """Add a new access code"""
        model = AccessCodeModel(
            code=entity.code,
            health_care_center_id=entity.health_care_center_id,
            is_used=entity.is_used,
            is_active=entity.is_active,
            expires_at=entity.expires_at
        )
        self._session.add(model)
        self._session.flush()
        return self._to_entity(model)

    def get_by_id(self, access_code_id: UUID) -> Optional[AccessCodeEntity]:
        """Get access code by ID"""
        model = self._session.query(AccessCodeModel).filter(
            AccessCodeModel.id == access_code_id
        ).first()
        return self._to_entity(model) if model else None

    def get_by_code(self, code: str) -> Optional[AccessCodeEntity]:
        """Get access code by code string"""
        model = self._session.query(AccessCodeModel).filter(
            AccessCodeModel.code == code
        ).first()
        return self._to_entity(model) if model else None

    def get_all(self, active_only: bool = True) -> List[AccessCodeEntity]:
        """Get all access codes"""
        query = self._session.query(AccessCodeModel)
        
        if active_only:
            query = query.filter(AccessCodeModel.is_active == True)
            
        models = query.order_by(desc(AccessCodeModel.created_at)).all()
        return [self._to_entity(model) for model in models]

    def update(self, entity: AccessCodeEntity) -> AccessCodeEntity:
        """Update an access code"""
        model = self._session.query(AccessCodeModel).filter(
            AccessCodeModel.id == entity.id
        ).first()
        
        if not model:
            raise ValueError(f"Access code with id {entity.id} not found")

        model.health_care_center_id = entity.health_care_center_id
        model.is_used = entity.is_used
        model.is_active = entity.is_active
        model.updated_at = datetime.now()
        model.expires_at = entity.expires_at
        
        self._session.flush()
        return self._to_entity(model)

    def _to_entity(self, model: AccessCodeModel) -> AccessCodeEntity:
        """Convert model to entity"""
        return AccessCodeEntity(
            id=model.id,
            code=model.code,
            health_care_center_id=model.health_care_center_id,
            is_used=model.is_used,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            expires_at=model.expires_at
        )
        

        
