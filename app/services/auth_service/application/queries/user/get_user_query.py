from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetUserQuery:   
    email: str


