from app.shared.domain.exceptions.common_errors import DomainError

class HealthCareCenterError(DomainError):
    """Base exception for health care center errors"""
    def __init__(self, message: str = "Health care center error"):
        super().__init__(message)

class HealthCareCenterNotFoundError(HealthCareCenterError):
    """Exception raised when a health care center cannot be found"""
    def __init__(self, message: str = "Health care center not found"):
        super().__init__(message)

class DuplicateHealthCareCenterError(HealthCareCenterError):
    """Exception raised when attempting to create a duplicate health care center"""
    def __init__(self, message: str = "Health care center with this email or license number already exists"):
        super().__init__(message)

class InvalidHealthCareCenterDataError(HealthCareCenterError):
    """Exception raised when health care center data is invalid"""
    def __init__(self, message: str = "Invalid health care center data"):
        super().__init__(message)

class CenterNotFoundError(HealthCareCenterError):
    """Exception raised when a health care center cannot be found"""
    def __init__(self, message: str = "Health care center not found"):
        super().__init__(message)
