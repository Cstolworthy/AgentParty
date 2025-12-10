"""Authentication helpers."""

import logging
from typing import Optional

from src.session.manager import get_session_manager
from src.session.models import Session

logger = logging.getLogger(__name__)


async def create_session(user_id: str) -> Session:
    """Create a new session for a user.

    Args:
        user_id: User identifier

    Returns:
        Created session
    """
    manager = await get_session_manager()
    return await manager.create_session(user_id)


async def validate_session(session_id: str) -> Optional[Session]:
    """Validate and retrieve a session.

    Args:
        session_id: Session identifier

    Returns:
        Session if valid, None otherwise
    """
    manager = await get_session_manager()
    return await manager.get_session(session_id)
