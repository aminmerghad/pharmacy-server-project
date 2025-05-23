"""
Database-compatible types for cross-database support.

This module provides custom SQLAlchemy types that work across different
database backends, particularly for UUID support in SQLite.
"""

import uuid
from sqlalchemy import TypeDecorator, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID


class UUID(TypeDecorator):
    """
    A UUID type that works with both SQLite and PostgreSQL.
    
    For SQLite: Stores UUIDs as strings (VARCHAR)
    For PostgreSQL: Uses native UUID type
    """
    impl = String
    cache_ok = True

    def __init__(self, as_uuid=False):
        """Initialize UUID type with optional as_uuid parameter for compatibility"""
        super().__init__()
        self.as_uuid = as_uuid

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        else:
            # For SQLite and other databases, use String
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            # For SQLite, convert UUID to string
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            # For SQLite, convert string back to UUID
            if isinstance(value, str):
                return uuid.UUID(value)
            return value

    @staticmethod
    def as_uuid():
        """Return a UUID type configured to use UUID objects"""
        return UUID(as_uuid=True)