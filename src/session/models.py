"""Session data models."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class UserContext(BaseModel):
    """Per-user context and state."""

    user_id: str
    active_job_id: Optional[str] = None
    workflow_id: Optional[str] = None
    current_step: Optional[str] = None
    step_history: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BudgetInfo(BaseModel):
    """User budget tracking."""

    user_id: str
    total_budget: float
    used_budget: float
    reset_date: datetime
    is_limited: bool = True

    @property
    def remaining_budget(self) -> float:
        """Calculate remaining budget."""
        return max(0.0, self.total_budget - self.used_budget)

    @property
    def usage_percentage(self) -> float:
        """Calculate budget usage percentage."""
        if self.total_budget == 0:
            return 0.0
        return (self.used_budget / self.total_budget) * 100

    def can_spend(self, amount: float) -> bool:
        """Check if user can spend the given amount."""
        if not self.is_limited:
            return True
        return self.remaining_budget >= amount


class Session(BaseModel):
    """User session data."""

    session_id: str
    user_id: str
    created_at: datetime
    last_active: datetime
    expires_at: datetime
    context: UserContext
    budget: Optional[BudgetInfo] = None

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at

    def touch(self) -> None:
        """Update last active timestamp."""
        self.last_active = datetime.utcnow()
