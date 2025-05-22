from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Email:
    address: str

    def __post_init__(self) -> None:
        if not self.is_valid_email(self.address):
            raise ValueError(f"Invalid email address: {self.address}")

    @staticmethod
    def is_valid_email(email: str) -> bool:
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(email_regex, email) is not None
