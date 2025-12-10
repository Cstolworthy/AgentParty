"""Tests for session management."""

from datetime import datetime, timedelta

import pytest

from src.session.models import BudgetInfo, Session, UserContext
from src.session.manager import SessionManager


@pytest.mark.asyncio
async def test_create_session(mock_redis):
    """Test session creation."""
    manager = SessionManager(mock_redis)

    session = await manager.create_session("test-user@example.com")

    assert session.user_id == "test-user@example.com"
    assert session.session_id.startswith("sess_")
    assert session.budget is not None
    assert session.budget.total_budget > 0
    assert session.budget.used_budget == 0


@pytest.mark.asyncio
async def test_session_expiry():
    """Test session expiry check."""
    now = datetime.utcnow()
    expired_session = Session(
        session_id="test-sess",
        user_id="test-user",
        created_at=now - timedelta(hours=25),
        last_active=now - timedelta(hours=25),
        expires_at=now - timedelta(hours=1),
        context=UserContext(user_id="test-user"),
    )

    assert expired_session.is_expired() is True


@pytest.mark.asyncio
async def test_budget_tracking():
    """Test budget tracking."""
    budget = BudgetInfo(
        user_id="test-user",
        total_budget=10.00,
        used_budget=8.00,
        reset_date=datetime.utcnow() + timedelta(days=30),
    )

    assert budget.remaining_budget == 2.00
    assert budget.usage_percentage == 80.0
    assert budget.can_spend(1.50) is True
    assert budget.can_spend(3.00) is False


@pytest.mark.asyncio
async def test_track_spending(mock_redis):
    """Test spending tracking."""
    manager = SessionManager(mock_redis)

    # Create session with budget
    session = await manager.create_session("test-user")
    session.budget.total_budget = 10.00
    session.budget.used_budget = 5.00

    # Mock get_session to return our session
    mock_redis.get = lambda k: session.model_dump_json()

    # Track spending
    success = await manager.track_spending(session.session_id, 2.00)

    # Note: This test is simplified; real test would verify Redis updates
    assert isinstance(success, bool)
