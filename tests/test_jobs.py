"""Tests for job system."""

from datetime import datetime

import pytest

from src.jobs.job import Job


def test_job_initialization(sample_job_definition):
    """Test job creation."""
    job = Job(definition=sample_job_definition, user_id="test-user")

    assert job.definition.id == "test-job"
    assert job.user_id == "test-user"
    assert job.context.job_id == "test-job"
    assert job.context.user_id == "test-user"
    assert isinstance(job.context.started_at, datetime)


def test_job_context_generation(sample_job_definition):
    """Test job context compilation."""
    job = Job(definition=sample_job_definition, user_id="test-user")

    context = job.get_full_context()

    assert "Test Job" in context
    assert "test-job" in context
    assert "Test job context" in context


def test_job_step_update(sample_job_definition):
    """Test updating job step."""
    job = Job(definition=sample_job_definition, user_id="test-user")

    assert job.context.current_step is None
    assert len(job.context.step_history) == 0

    job.update_step("step1")
    assert job.context.current_step == "step1"

    job.update_step("step2")
    assert job.context.current_step == "step2"
    assert "step1" in job.context.step_history


def test_job_submission_recording(sample_job_definition):
    """Test recording work submission."""
    job = Job(definition=sample_job_definition, user_id="test-user")

    job.record_submission(
        work_description="Completed implementation",
        artifacts=["file1.py", "file2.py"],
    )

    assert job.context.submitted_work is not None
    assert job.context.submitted_work["description"] == "Completed implementation"
    assert len(job.context.submitted_work["artifacts"]) == 2
