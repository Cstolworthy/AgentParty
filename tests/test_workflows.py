"""Tests for workflow engine."""

from datetime import datetime

import pytest

from src.workflows.workflow import StepStatus, WorkflowState


def test_workflow_state_creation():
    """Test workflow state initialization."""
    state = WorkflowState(
        user_id="test-user",
        workflow_id="test-workflow",
        job_id="test-job",
        started_at=datetime.utcnow(),
    )

    assert state.user_id == "test-user"
    assert state.workflow_id == "test-workflow"
    assert state.is_completed is False
    assert state.completed_at is None


def test_step_status_management():
    """Test step status tracking."""
    state = WorkflowState(
        user_id="test-user",
        workflow_id="test-workflow",
        job_id="test-job",
        started_at=datetime.utcnow(),
    )

    # Set step status
    state.set_step_status("step1", StepStatus.IN_PROGRESS)
    assert state.get_step_status("step1") == StepStatus.IN_PROGRESS

    # Update to completed
    state.set_step_status("step1", StepStatus.COMPLETED)
    assert state.get_step_status("step1") == StepStatus.COMPLETED

    # Unknown step defaults to PENDING
    assert state.get_step_status("step999") == StepStatus.PENDING


def test_workflow_completion():
    """Test workflow completion."""
    state = WorkflowState(
        user_id="test-user",
        workflow_id="test-workflow",
        job_id="test-job",
        started_at=datetime.utcnow(),
    )

    assert state.is_completed is False
    assert state.completed_at is None

    state.mark_completed()

    assert state.is_completed is True
    assert state.completed_at is not None


def test_workflow_definition(sample_workflow_definition):
    """Test workflow definition model."""
    workflow = sample_workflow_definition

    assert workflow.id == "test-workflow"
    assert workflow.name == "Test Workflow"
    assert len(workflow.steps) == 2

    # Test get_step
    step1 = workflow.get_step("step1")
    assert step1 is not None
    assert step1.name == "First Step"
    assert step1.requires_approval is True

    # Test get_first_step
    first = workflow.get_first_step()
    assert first.id == "step1"
