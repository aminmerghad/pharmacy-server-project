from dataclasses import dataclass
from uuid import UUID

@dataclass
class GetHealthCareCenterByIdQuery:
    """Query for retrieving a specific health care center by its ID"""
    id: UUID 