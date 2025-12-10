"""Workflow definition loader."""

import logging
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field

from src.config import get_settings

logger = logging.getLogger(__name__)


class WorkflowStep(BaseModel):
    """Single workflow step definition."""

    id: str
    name: str
    description: Optional[str] = None
    agent: str  # Agent role for this step
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    requires_approval: bool = False
    approval_agent: Optional[str] = None  # Which agent approves
    next_step: Optional[str] = None  # Simple linear flow


class WorkflowDefinition(BaseModel):
    """Workflow definition loaded from directory."""

    id: str
    name: str
    version: str
    description: Optional[str] = None
    steps: list[WorkflowStep]
    metadata: dict[str, Any] = Field(default_factory=dict)

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get step by ID.

        Args:
            step_id: Step identifier

        Returns:
            WorkflowStep if found, None otherwise
        """
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_first_step(self) -> Optional[WorkflowStep]:
        """Get the first step in workflow.

        Returns:
            First step if exists, None otherwise
        """
        return self.steps[0] if self.steps else None


def load_workflow_definition(workflow_id: str) -> WorkflowDefinition:
    """Load workflow definition from directory.

    Args:
        workflow_id: Workflow identifier (directory name)

    Returns:
        WorkflowDefinition object

    Raises:
        FileNotFoundError: If workflow directory or workflow.yaml not found
        ValueError: If workflow definition is invalid
    """
    settings = get_settings()
    workflow_dir = Path(settings.workflows_dir) / workflow_id

    if not workflow_dir.exists():
        raise FileNotFoundError(f"Workflow directory not found: {workflow_dir}")

    # Load workflow.yaml
    workflow_file = workflow_dir / "workflow.yaml"
    if not workflow_file.exists():
        raise FileNotFoundError(f"Workflow file not found: {workflow_file}")

    with open(workflow_file, "r", encoding="utf-8") as f:
        workflow_data = yaml.safe_load(f)

    # Parse steps
    steps_data = workflow_data.get("steps", [])
    steps = []

    for step_data in steps_data:
        # Check if step has approvals defined
        approvals = step_data.get("approvals", [])
        requires_approval = len(approvals) > 0
        approval_agent = approvals[0].get("agent") if approvals else None

        # Get next step from transitions (simple linear for now)
        transitions = step_data.get("transitions", [])
        next_step = transitions[0].get("to") if transitions else None

        step = WorkflowStep(
            id=step_data["id"],
            name=step_data.get("name", step_data["id"]),
            description=step_data.get("description"),
            agent=step_data.get("agent", "programmer"),
            inputs=step_data.get("inputs", []),
            outputs=step_data.get("outputs", []),
            requires_approval=requires_approval,
            approval_agent=approval_agent,
            next_step=next_step,
        )
        steps.append(step)

    # Create workflow definition
    workflow_def = WorkflowDefinition(
        id=workflow_id,
        name=workflow_data.get("name", workflow_id),
        version=workflow_data.get("version", "1.0"),
        description=workflow_data.get("description"),
        steps=steps,
        metadata=workflow_data.get("metadata", {}),
    )

    logger.info(f"Loaded workflow definition: {workflow_id} with {len(steps)} steps")
    return workflow_def


def list_available_workflows() -> list[str]:
    """List all available workflow IDs.

    Returns:
        List of workflow IDs
    """
    settings = get_settings()
    workflows_dir = Path(settings.workflows_dir)

    if not workflows_dir.exists():
        return []

    # Find directories with workflow.yaml
    workflow_ids = []
    for item in workflows_dir.iterdir():
        if item.is_dir() and (item / "workflow.yaml").exists():
            workflow_ids.append(item.name)

    return sorted(workflow_ids)
