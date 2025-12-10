"""Job manager for user job instances."""

import logging
from typing import Optional

from src.jobs.job import Job
from src.jobs.loader import JobDefinition, list_available_jobs, load_job_definition

logger = logging.getLogger(__name__)


class JobManager:
    """Manages active job instances per user."""

    def __init__(self):
        """Initialize job manager."""
        self._active_jobs: dict[str, Job] = {}  # key: user_id

    def list_available(self, assigned_to: Optional[str] = None) -> list[JobDefinition]:
        """List available jobs.

        Args:
            assigned_to: Filter by assigned agent

        Returns:
            List of job definitions
        """
        job_ids = list_available_jobs(assigned_to=assigned_to)
        jobs = []

        for job_id in job_ids:
            try:
                job_def = load_job_definition(job_id)
                jobs.append(job_def)
            except Exception as e:
                logger.error(f"Failed to load job {job_id}: {e}")

        return jobs

    def start_job(self, user_id: str, job_id: str) -> Job:
        """Start a job for a user.

        Args:
            user_id: User identifier
            job_id: Job identifier

        Returns:
            Job instance

        Raises:
            FileNotFoundError: If job not found
            ValueError: If user already has an active job
        """
        if user_id in self._active_jobs:
            current_job = self._active_jobs[user_id]
            raise ValueError(
                f"User already has active job: {current_job.definition.id}. "
                "Complete or cancel it first."
            )

        # Load job definition
        job_def = load_job_definition(job_id)

        # Create job instance
        job = Job(definition=job_def, user_id=user_id)
        self._active_jobs[user_id] = job

        logger.info(f"Started job {job_id} for user {user_id}")
        return job

    def get_active_job(self, user_id: str) -> Optional[Job]:
        """Get user's active job.

        Args:
            user_id: User identifier

        Returns:
            Job instance if active, None otherwise
        """
        return self._active_jobs.get(user_id)

    def complete_job(self, user_id: str) -> None:
        """Mark user's job as complete.

        Args:
            user_id: User identifier
        """
        if user_id in self._active_jobs:
            job = self._active_jobs[user_id]
            del self._active_jobs[user_id]
            logger.info(f"Completed job {job.definition.id} for user {user_id}")

    def cancel_job(self, user_id: str) -> None:
        """Cancel user's job.

        Args:
            user_id: User identifier
        """
        if user_id in self._active_jobs:
            job = self._active_jobs[user_id]
            del self._active_jobs[user_id]
            logger.info(f"Cancelled job {job.definition.id} for user {user_id}")


# Global job manager
_job_manager: Optional[JobManager] = None


def get_job_manager() -> JobManager:
    """Get global job manager instance.

    Returns:
        JobManager instance
    """
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager
