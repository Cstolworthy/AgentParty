"""Workflow state management."""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class StepStatus(str, Enum):
    """Workflow step status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class WorkflowStatus(str, Enum):
    """Workflow status."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowState(BaseModel):
    """Runtime workflow state for a user."""

    user_id: str
    workflow_id: str
    job_id: str
    current_step: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.IN_PROGRESS
    step_statuses: dict[str, StepStatus] = Field(default_factory=dict)
    step_data: dict[str, dict[str, Any]] = Field(default_factory=dict)
    started_at: datetime
    completed_at: Optional[datetime] = None
    is_completed: bool = False

    def get_step_status(self, step_id: str) -> StepStatus:
        """Get status of a step.

        Args:
            step_id: Step identifier

        Returns:
            Step status
        """
        return self.step_statuses.get(step_id, StepStatus.PENDING)

    def set_step_status(self, step_id: str, status: StepStatus) -> None:
        """Set status of a step.

        Args:
            step_id: Step identifier
            status: New status
        """
        self.step_statuses[step_id] = status
        logger.debug(f"Step {step_id} status: {status}")

    def store_step_data(self, step_id: str, data: dict[str, Any]) -> None:
        """Store data for a step.

        Args:
            step_id: Step identifier
            data: Data to store
        """
        self.step_data[step_id] = data

    def get_step_data(self, step_id: str) -> dict[str, Any]:
        """Get data for a step.

        Args:
            step_id: Step identifier

        Returns:
            Step data
        """
        return self.step_data.get(step_id, {})

    def mark_completed(self) -> None:
        """Mark workflow as completed."""
        self.is_completed = True
        self.status = WorkflowStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        logger.info(f"Workflow {self.workflow_id} completed for user {self.user_id}")
