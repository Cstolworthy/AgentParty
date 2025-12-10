"""Session manager with Redis backend."""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from src.config import get_settings
from src.session.models import BudgetInfo, Session, UserContext

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user sessions with Redis backend."""

    def __init__(self, redis_client: Redis):
        """Initialize session manager.

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
        self.settings = get_settings()
        self._session_prefix = "session:"
        self._user_prefix = "user:"

    async def create_session(self, user_id: str) -> Session:
        """Create a new user session.

        Args:
            user_id: Unique user identifier

        Returns:
            Created session object
        """
        import uuid

        session_id = f"sess_{uuid.uuid4().hex}"
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self.settings.session_ttl_hours)

        # Create budget info
        budget = BudgetInfo(
            user_id=user_id,
            total_budget=self.settings.default_user_budget,
            used_budget=0.0,
            reset_date=self._calculate_reset_date(now),
            is_limited=True,
        )

        # Create session
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_active=now,
            expires_at=expires_at,
            context=UserContext(user_id=user_id),
            budget=budget,
        )

        # Store in Redis
        await self._save_session(session)

        logger.info(f"Created session {session_id} for user {user_id}")
        return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session object if found and valid, None otherwise
        """
        key = f"{self._session_prefix}{session_id}"
        data = await self.redis.get(key)

        if not data:
            return None

        session = Session.model_validate_json(data)

        if session.is_expired():
            await self.delete_session(session_id)
            return None

        # Update last active
        session.touch()
        await self._save_session(session)

        return session

    async def update_session(self, session: Session) -> None:
        """Update session data.

        Args:
            session: Session to update
        """
        session.touch()
        await self._save_session(session)

    async def delete_session(self, session_id: str) -> None:
        """Delete a session.

        Args:
            session_id: Session identifier
        """
        key = f"{self._session_prefix}{session_id}"
        await self.redis.delete(key)
        logger.info(f"Deleted session {session_id}")

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        pattern = f"{self._session_prefix}*"
        cursor = 0
        cleaned = 0

        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)

            for key in keys:
                data = await self.redis.get(key)
                if data:
                    session = Session.model_validate_json(data)
                    if session.is_expired():
                        await self.redis.delete(key)
                        cleaned += 1

            if cursor == 0:
                break

        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired sessions")

        return cleaned

    async def track_spending(self, session_id: str, amount: float) -> bool:
        """Track LLM API spending for a session.

        Args:
            session_id: Session identifier
            amount: Amount spent in USD

        Returns:
            True if spending was tracked, False if budget exceeded
        """
        session = await self.get_session(session_id)
        if not session or not session.budget:
            return False

        # Check if user can spend
        if not session.budget.can_spend(amount):
            logger.warning(
                f"Budget exceeded for user {session.user_id}: "
                f"tried to spend ${amount:.4f}, "
                f"remaining ${session.budget.remaining_budget:.4f}"
            )
            return False

        # Update budget
        session.budget.used_budget += amount
        await self.update_session(session)

        # Log warning if approaching limit
        if session.budget.usage_percentage >= self.settings.budget_warning_threshold * 100:
            logger.warning(
                f"User {session.user_id} at {session.budget.usage_percentage:.1f}% budget usage"
            )

        return True

    async def get_budget_info(self, session_id: str) -> Optional[BudgetInfo]:
        """Get budget information for a session.

        Args:
            session_id: Session identifier

        Returns:
            Budget info if session exists, None otherwise
        """
        session = await self.get_session(session_id)
        return session.budget if session else None

    async def reset_budget(self, user_id: str) -> None:
        """Reset user budget (called on schedule).

        Args:
            user_id: User identifier
        """
        # Find all sessions for this user
        pattern = f"{self._session_prefix}*"
        cursor = 0

        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)

            for key in keys:
                data = await self.redis.get(key)
                if data:
                    session = Session.model_validate_json(data)
                    if session.user_id == user_id and session.budget:
                        session.budget.used_budget = 0.0
                        session.budget.reset_date = self._calculate_reset_date(datetime.utcnow())
                        await self._save_session(session)

            if cursor == 0:
                break

        logger.info(f"Reset budget for user {user_id}")

    async def _save_session(self, session: Session) -> None:
        """Save session to Redis.

        Args:
            session: Session to save
        """
        key = f"{self._session_prefix}{session.session_id}"
        ttl = int((session.expires_at - datetime.utcnow()).total_seconds())

        await self.redis.setex(
            key,
            ttl,
            session.model_dump_json(),
        )

    def _calculate_reset_date(self, from_date: datetime) -> datetime:
        """Calculate next budget reset date.

        Args:
            from_date: Starting date

        Returns:
            Next reset date
        """
        if self.settings.budget_reset_period == "daily":
            return from_date + timedelta(days=1)
        elif self.settings.budget_reset_period == "weekly":
            return from_date + timedelta(weeks=1)
        else:  # monthly
            # Simple monthly: add 30 days
            return from_date + timedelta(days=30)


# Global session manager instance
_session_manager: Optional[SessionManager] = None


async def get_session_manager() -> SessionManager:
    """Get or create global session manager instance.

    Returns:
        SessionManager instance
    """
    global _session_manager

    if _session_manager is None:
        settings = get_settings()
        redis_client = await redis.from_url(
            settings.redis_url,
            password=settings.redis_password,
            db=settings.redis_db,
            encoding="utf-8",
            decode_responses=True,
        )
        _session_manager = SessionManager(redis_client)

    return _session_manager
