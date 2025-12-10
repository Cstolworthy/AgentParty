"""SQLite database client for persistent storage."""

import logging
import os
from pathlib import Path
from typing import Optional

import aiosqlite

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager."""

    def __init__(self, db_path: str):
        """Initialize database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """Connect to database and create tables."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row

        await self._create_tables()
        logger.info(f"Connected to SQLite database: {self.db_path}")

    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Closed database connection")

    async def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workflows (
                user_id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                job_id TEXT NOT NULL,
                current_step TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                step_statuses TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                workflow_id TEXT NOT NULL,
                job_id TEXT NOT NULL,
                step_id TEXT NOT NULL,
                agent TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                artifacts TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        await self._connection.commit()
        logger.info("Database tables created/verified")

    @property
    def connection(self) -> aiosqlite.Connection:
        """Get database connection.

        Returns:
            Database connection

        Raises:
            RuntimeError: If not connected
        """
        if not self._connection:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._connection


# Global database instance
_database: Optional[Database] = None


async def get_database() -> Database:
    """Get or create global database instance.

    Returns:
        Database instance
    """
    global _database

    if _database is None:
        db_path = os.getenv("DATABASE_PATH", "./data/agentparty.db")
        _database = Database(db_path)
        await _database.connect()

    return _database
