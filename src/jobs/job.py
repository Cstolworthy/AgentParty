"""Job runtime class."""

import logging
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.jobs.loader import JobDefinition

logger = logging.getLogger(__name__)


class JobContext(BaseModel):
    """Runtime job context."""

    job_id: str
    user_id: str
    started_at: datetime
    current_step: Optional[str] = None
    step_history: list[str] = Field(default_factory=list)
    submitted_work: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Job:
    """Runtime job instance."""

    def __init__(self, definition: JobDefinition, user_id: str):
        """Initialize job.

        Args:
            definition: Job definition
            user_id: User ID
        """
        self.definition = definition
        self.user_id = user_id
        self.context = JobContext(
            job_id=definition.id,
            user_id=user_id,
            started_at=datetime.utcnow(),
        )

    def get_full_context(self) -> str:
        """Get full job context for agents.

        Returns:
            Compiled context string
        """
        parts = [
            f"# Job: {self.definition.title}",
            f"**Job ID:** {self.definition.id}",
            f"**Priority:** {self.definition.priority}",
        ]

        if self.definition.description:
            parts.append(f"\n## Description\n{self.definition.description}")

        if self.definition.context_content:
            parts.append(f"\n## Context\n{self.definition.context_content}")

        if self.definition.deadline:
            parts.append(f"\n**Deadline:** {self.definition.deadline.isoformat()}")

        return "\n\n".join(parts)

    def update_step(self, step_id: str) -> None:
        """Update current workflow step.

        Args:
            step_id: Step identifier
        """
        if self.context.current_step:
            self.context.step_history.append(self.context.current_step)
        self.context.current_step = step_id
        logger.info(f"Job {self.definition.id} moved to step: {step_id}")

    def record_submission(self, work_description: str, artifacts: Optional[list[str]] = None) -> None:
        """Record work submission.

        Args:
            work_description: Description of work
            artifacts: List of artifacts
        """
        self.context.submitted_work = {
            "description": work_description,
            "artifacts": artifacts or [],
            "timestamp": datetime.utcnow().isoformat(),
            "step": self.context.current_step,
        }
