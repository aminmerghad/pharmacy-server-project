from dataclasses import dataclass


@dataclass
class AccessCodeValidationQuery:
    code: str
