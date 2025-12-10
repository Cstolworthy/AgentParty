"""Workflow state persistence."""

import json
import logging
from datetime import datetime
from typing import Optional

from src.database.client import Database
from src.workflows.workflow import StepStatus, WorkflowState, WorkflowStatus

logger = logging.getLogger(__name__)


class WorkflowStore:
    """Persists workflow state to SQLite."""

    def __init__(self, database: Database):
        """Initialize workflow store.

        Args:
            database: Database instance
        """
        self.db = database

    async def save_workflow(self, user_id: str, workflow: WorkflowState) -> None:
        """Save workflow state.

        Args:
            user_id: User identifier
            workflow: Workflow state to save
        """
        # Serialize step statuses
        step_statuses_json = json.dumps(
            {step_id: status.value for step_id, status in workflow.step_statuses.items()}
        )

        await self.db.connection.execute(
            """
            INSERT OR REPLACE INTO workflows (
                user_id, workflow_id, job_id, current_step, status,
                started_at, completed_at, step_statuses, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                user_id,
                workflow.workflow_id,
                workflow.job_id,
                workflow.current_step,
                workflow.status.value,
                workflow.started_at.isoformat(),
                workflow.completed_at.isoformat() if workflow.completed_at else None,
                step_statuses_json,
            ),
        )
        await self.db.connection.commit()
        logger.debug(f"Saved workflow for user {user_id}")

    async def load_workflow(self, user_id: str) -> Optional[WorkflowState]:
        """Load workflow state for user.

        Args:
            user_id: User identifier

        Returns:
            Workflow state if exists, None otherwise
        """
        async with self.db.connection.execute(
            "SELECT * FROM workflows WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()

        if not row:
            return None

        # Deserialize step statuses
        step_statuses_data = json.loads(row["step_statuses"])
        step_statuses = {
            step_id: StepStatus(status) for step_id, status in step_statuses_data.items()
        }

        return WorkflowState(
            user_id=user_id,
            workflow_id=row["workflow_id"],
            job_id=row["job_id"],
            current_step=row["current_step"],
            status=WorkflowStatus(row["status"]),
            started_at=datetime.fromisoformat(row["started_at"]),
            completed_at=(
                datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
            ),
            step_statuses=step_statuses,
        )

    async def delete_workflow(self, user_id: str) -> None:
        """Delete workflow state for user.

        Args:
            user_id: User identifier
        """
        await self.db.connection.execute("DELETE FROM workflows WHERE user_id = ?", (user_id,))
        await self.db.connection.commit()
        logger.debug(f"Deleted workflow for user {user_id}")

    async def add_history_entry(
        self,
        user_id: str,
        workflow_id: str,
        job_id: str,
        step_id: str,
        agent: str,
        status: str,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        artifacts: Optional[list[str]] = None,
    ) -> None:
        """Add workflow history entry.

        Args:
            user_id: User identifier
            workflow_id: Workflow identifier
            job_id: Job identifier
            step_id: Step identifier
            agent: Agent name
            status: Step status
            started_at: Start time
            completed_at: Completion time
            artifacts: List of artifacts
        """
        await self.db.connection.execute(
            """
            INSERT INTO workflow_history (
                user_id, workflow_id, job_id, step_id, agent,
                status, started_at, completed_at, artifacts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                workflow_id,
                job_id,
                step_id,
                agent,
                status,
                started_at.isoformat() if started_at else None,
                completed_at.isoformat() if completed_at else None,
                json.dumps(artifacts) if artifacts else None,
            ),
        )
        await self.db.connection.commit()
        logger.debug(f"Added history entry for {user_id}/{step_id}")
