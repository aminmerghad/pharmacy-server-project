from dataclasses import dataclass
from uuid import UUID


@dataclass
class AssignUserToCenterCommand:
    user_id:UUID
    center_id:UUID