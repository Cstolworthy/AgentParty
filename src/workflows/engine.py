"""Workflow execution engine."""

import logging
from datetime import datetime
from typing import Optional

from src.agents.agent import Agent
from src.agents.registry import get_agent_registry
from src.database.workflow_store import WorkflowStore
from src.session.manager import SessionManager
from src.workflows.loader import WorkflowDefinition, load_workflow_definition
from src.workflows.workflow import StepStatus, WorkflowState

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Manages workflow execution for users."""

    def __init__(self, session_manager: SessionManager, workflow_store: WorkflowStore):
        """Initialize workflow engine.

        Args:
            session_manager: Session manager for budget tracking
            workflow_store: Workflow persistence store
        """
        self.session_manager = session_manager
        self.workflow_store = workflow_store
        self._agent_registry = get_agent_registry()

    async def start_workflow(
        self,
        user_id: str,
        workflow_id: str,
        job_id: str,
    ) -> WorkflowState:
        """Start a workflow for a user.

        Args:
            user_id: User identifier
            workflow_id: Workflow identifier
            job_id: Job identifier

        Returns:
            Workflow state

        Raises:
            ValueError: If user already has an active workflow
        """
        # Check if user already has an active workflow
        existing = await self.workflow_store.load_workflow(user_id)
        if existing:
            raise ValueError(f"User {user_id} already has an active workflow")

        # Load workflow definition
        workflow_def = load_workflow_definition(workflow_id)

        # Get first step
        first_step = workflow_def.get_first_step()
        if not first_step:
            raise ValueError(f"Workflow {workflow_id} has no steps")

        # Create workflow state
        state = WorkflowState(
            user_id=user_id,
            workflow_id=workflow_id,
            job_id=job_id,
            current_step=first_step.id,
            started_at=datetime.utcnow(),
        )

        # Mark first step as in progress
        state.set_step_status(first_step.id, StepStatus.IN_PROGRESS)

        # Persist to database
        await self.workflow_store.save_workflow(user_id, state)
        logger.info(f"Started workflow {workflow_id} for user {user_id}")

        return state

    async def get_workflow_state(self, user_id: str) -> Optional[WorkflowState]:
        """Get user's workflow state.

        Args:
            user_id: User identifier

        Returns:
            Workflow state if active, None otherwise
        """
        return await self.workflow_store.load_workflow(user_id)

    def get_current_task(self, user_id: str) -> dict[str, any]:
        """Get current task for user.

        Args:
            user_id: User identifier

        Returns:
            Current task information

        Raises:
            ValueError: If no active workflow
        """
        state = self._workflows.get(user_id)
        if not state:
            raise ValueError(f"No active workflow for user {user_id}")

        if state.is_completed:
            return {"status": "completed", "message": "Workflow completed!"}

        # Load workflow definition
        workflow_def = load_workflow_definition(state.workflow_id)
        current_step = workflow_def.get_step(state.current_step)

        if not current_step:
            raise ValueError(f"Invalid step: {state.current_step}")

        return {
            "step_id": current_step.id,
            "step_name": current_step.name,
            "description": current_step.description,
            "agent": current_step.agent,
            "inputs": current_step.inputs,
            "outputs": current_step.outputs,
            "status": state.get_step_status(current_step.id).value,
        }

    async def submit_work(
        self,
        user_id: str,
        work_description: str,
        artifacts: Optional[list[str]] = None,
        session_id: Optional[str] = None,
    ) -> dict[str, any]:
        """Submit work for current step.

        Args:
            user_id: User identifier
            work_description: Description of work
            artifacts: List of artifacts
            session_id: Session ID for budget tracking

        Returns:
            Submission result

        Raises:
            ValueError: If no active workflow
        """
        state = self._workflows.get(user_id)
        if not state:
            raise ValueError(f"No active workflow for user {user_id}")

        # Load workflow definition
        workflow_def = load_workflow_definition(state.workflow_id)
        current_step = workflow_def.get_step(state.current_step)

        if not current_step:
            raise ValueError(f"Invalid step: {state.current_step}")

        # Store submission data
        state.store_step_data(
            current_step.id,
            {
                "work_description": work_description,
                "artifacts": artifacts or [],
                "submitted_at": datetime.utcnow().isoformat(),
            },
        )

        # Check if approval is required
        if current_step.requires_approval and current_step.approval_agent:
            state.set_step_status(current_step.id, StepStatus.AWAITING_APPROVAL)

            # Trigger approval (will be done via request_review)
            return {
                "status": "awaiting_approval",
                "message": f"Work submitted, awaiting approval from {current_step.approval_agent}",
                "requires_approval": True,
                "approval_agent": current_step.approval_agent,
            }
        else:
            # No approval needed, move to next step
            return await self._advance_to_next_step(user_id, state, workflow_def, current_step)

    async def request_review(
        self,
        user_id: str,
        session_id: Optional[str] = None,
    ) -> dict[str, any]:
        """Request review from approval agent.

        Args:
            user_id: User identifier
            session_id: Session ID for budget tracking

        Returns:
            Review result
        """
        state = self._workflows.get(user_id)
        if not state:
            raise ValueError(f"No active workflow for user {user_id}")

        # Load workflow definition
        workflow_def = load_workflow_definition(state.workflow_id)
        current_step = workflow_def.get_step(state.current_step)

        if not current_step or not current_step.requires_approval:
            raise ValueError("Current step does not require approval")

        # Get approval agent
        agent_def = self._agent_registry.get(current_step.approval_agent)
        if not agent_def:
            raise ValueError(f"Approval agent not found: {current_step.approval_agent}")

        # Create agent instance
        agent = Agent(
            definition=agent_def,
            session_manager=self.session_manager,
            user_id=user_id,
        )

        # Get submitted work
        step_data = state.get_step_data(current_step.id)

        # Request review
        review_result = await agent.review_work(
            work_description=step_data.get("work_description", ""),
            artifacts=step_data.get("artifacts"),
            session_id=session_id,
        )

        # Update step based on review
        if review_result["approved"]:
            state.set_step_status(current_step.id, StepStatus.APPROVED)
            # Advance to next step
            result = await self._advance_to_next_step(user_id, state, workflow_def, current_step)
            result["review"] = review_result
            return result
        else:
            state.set_step_status(current_step.id, StepStatus.CHANGES_REQUESTED)
            return {
                "status": "changes_requested",
                "message": "Changes requested by reviewer",
                "review": review_result,
            }

    async def _advance_to_next_step(
        self,
        user_id: str,
        state: WorkflowState,
        workflow_def: WorkflowDefinition,
        current_step: any,
    ) -> dict[str, any]:
        """Advance workflow to next step.

        Args:
            user_id: User identifier
            state: Workflow state
            workflow_def: Workflow definition
            current_step: Current step

        Returns:
            Advancement result
        """
        # Mark current step as completed
        state.set_step_status(current_step.id, StepStatus.COMPLETED)

        # Get next step
        if current_step.next_step:
            next_step = workflow_def.get_step(current_step.next_step)
            if next_step:
                state.current_step = next_step.id
                state.set_step_status(next_step.id, StepStatus.IN_PROGRESS)

                return {
                    "status": "advanced",
                    "message": f"Advanced to step: {next_step.name}",
                    "next_step": {
                        "id": next_step.id,
                        "name": next_step.name,
                        "agent": next_step.agent,
                    },
                }

        # No next step, workflow is complete
        state.mark_completed()
        del self._workflows[user_id]

        return {
            "status": "completed",
            "message": "Workflow completed successfully!",
        }


# Global workflow engine
_workflow_engine: Optional[WorkflowEngine] = None


async def get_workflow_engine() -> WorkflowEngine:
    """Get global workflow engine instance.

    Returns:
        WorkflowEngine instance
    """
    global _workflow_engine

    if _workflow_engine is None:
        from src.database.client import get_database
        from src.session.manager import get_session_manager

        session_manager = await get_session_manager()
        database = await get_database()
        workflow_store = WorkflowStore(database)
        
        _workflow_engine = WorkflowEngine(session_manager, workflow_store)

    return _workflow_engine
