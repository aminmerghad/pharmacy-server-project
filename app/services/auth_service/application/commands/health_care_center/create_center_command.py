from dataclasses import dataclass

@dataclass
class CreateOrGetHealthCareCenterCommand:
    name: str
    address: str
    phone: str
    email: str
    license_number: str 