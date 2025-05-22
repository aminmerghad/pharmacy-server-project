from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str
    country: str
    postal_code: str
    building_number: Optional[str] = None
    apartment_number: Optional[str] = None
    additional_info: Optional[str] = None

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.street or len(self.street.strip()) < 2:
            raise ValueError("Street must be at least 2 characters long")
        
        if not self.city or len(self.city.strip()) < 2:
            raise ValueError("City must be at least 2 characters long")
        
        if not self.state or len(self.state.strip()) < 2:
            raise ValueError("State must be at least 2 characters long")
        
        if not self.country or len(self.country.strip()) < 2:
            raise ValueError("Country must be at least 2 characters long")
        
        if not self.postal_code or not self._is_valid_postal_code():
            raise ValueError("Invalid postal code format")

    def _is_valid_postal_code(self) -> bool:
        # This is a simple validation - enhance based on your requirements
        return len(self.postal_code.strip()) >= 4

    def format(self) -> str:
        """Returns a formatted string representation of the address"""
        parts = [
            f"{self.building_number} {self.street}" if self.building_number else self.street,
            f"Apt {self.apartment_number}" if self.apartment_number else None,
            self.city,
            self.state,
            self.postal_code,
            self.country,
            self.additional_info
        ]
        return ", ".join(part for part in parts if part)
