from dataclasses import dataclass

@dataclass
class DeleteAccessCodeCommand:
    """Command for deleting an access code"""
    code: str 