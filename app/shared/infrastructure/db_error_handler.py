from typing import Any, Callable
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.shared.domain.exceptions.database_errors import DatabaseError
from functools import wraps

class DatabaseErrorHandler:
    @staticmethod
    def handle_integrity_error(error: IntegrityError, context: dict[str, Any]) -> None:
        """
        Handle SQLAlchemy integrity errors with specific field checking
        """
        error_msg = str(error).lower()
        
        if 'unique constraint' not in error_msg:
            raise DatabaseError("Database integrity error occurred") from error
            
        # Map of field names to their error messages
        unique_field_errors = {
            'email': lambda: f"User with email {context.get('email')} already exists",
            'username': lambda: f"Username {context.get('username')} is already taken",
            'phone': lambda: f"Phone number {context.get('phone')} is already registered"
        }
        
        # Check each field and raise appropriate error
        for field, error_msg_fn in unique_field_errors.items():
            if field in error_msg:
                from app.shared.domain.exceptions.user_errors import UserAlreadyExistsError
                raise UserAlreadyExistsError(error_msg_fn())
                
        # If no specific field error is found, raise generic database error
        raise DatabaseError("Database integrity error occurred") from error

    @staticmethod
    def handle_db_operation(
        # unit_of_work: Any = None
        ) -> Callable:
        """
        Decorator for handling database operations and their potential errors
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                try:
                    
                    return func(*args, **kwargs)
                except IntegrityError as e:
                    # Extract context from args or kwargs based on your needs
                    context = {}
                    if len(args) > 1 and hasattr(args[1], '__dict__'):
                        context = args[1].__dict__
                    DatabaseErrorHandler.handle_integrity_error(e, context)
                except SQLAlchemyError as e:
                    # if unit_of_work:
                    #     unit_of_work.rollback()
                    raise DatabaseError("An unexpected database error occurred") from e
            return wrapper
        return decorator 
    @staticmethod
    def handle_service_operation() -> Callable:
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(self, *args, **kwargs) -> Any:
                try:                    
                    return func(self, *args, **kwargs)
                except Exception as e:
                    if self._uow:
                        self._uow.rollback()
                    raise e
            return wrapper
        return decorator
