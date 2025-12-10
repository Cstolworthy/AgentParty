"""Database module for persistent storage."""

from src.database.client import get_database, Database

__all__ = ["get_database", "Database"]
