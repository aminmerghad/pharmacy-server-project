from dataclasses import dataclass
from app.services.auth_service.domain.entities import AccessCodeEntity,HealthCareCenterEntity


@dataclass
class AccessCodeAggregator :
    access_code : AccessCodeEntity
    health_care_center: HealthCareCenterEntity = None
    
    