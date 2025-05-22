from dataclasses import dataclass
from uuid import UUID

from app.services.auth_service.domain.entities import AccessCodeEntity


@dataclass
class ConsumeAccessCodeCommand:
    access_code:AccessCodeEntity
    used_by:UUID