from dataclasses import dataclass


@dataclass
class AdminRegistrationCommand:
    initialization_key: str
    username: str
    password: str
    email:str
    full_name:str
    phone:str
