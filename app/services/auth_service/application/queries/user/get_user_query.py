from dataclasses import dataclass

from sqlalchemy import UUID


@dataclass
class GetUserQuery:   
    email: str


