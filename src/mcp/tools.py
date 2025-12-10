"""MCP tool implementations."""

import logging
from typing import Any, Optional

from src.agents.agent import Agent
from src.agents.registry import get_agent_registry
from src.jobs.manager import get_job_manager
from src.session.manager import get_session_manager
from src.vectordb.search import search_codebase
from src.workflows.engine import get_workflow_engine

logger = logging.getLogger(__name__)


class MCPTools:
    """MCP tool implementations."""

    @staticmethod
    async def get_available_jobs(
        user_id: str,
        filter_type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """List all jobs available for the current agent to work on.

        Args:
            user_id: User identifier
            filter_type: Optional filter (e.g., 'high-priority')

        Returns:
            List of available jobs
        """
        job_manager = get_job_manager()

        # Get jobs assigned to 'programmer' (the IDE agent)
        jobs = job_manager.list_available(assigned_to="programmer")

        # Convert to dict format
        result = []
        for job in jobs:
            # Apply filter if specified
            if filter_type and filter_type not in job.priority:
                continue

            result.append(
                {
                    "id": job.id,
                    "title": job.title,
                    "description": job.description,
                    "priority": job.priority,
                    "workflow": job.workflow_id,
                    "deadline": job.deadline.isoformat() if job.deadline else None,
                }
            )

        logger.info(f"User {user_id} retrieved {len(result)} available jobs")
        return result

    @staticmethod
    async def start_job(user_id: str, job_id: str, session_id: str) -> dict[str, Any]:
        """Initialize a job and load its workflow.

        Args:
            user_id: User identifier
            job_id: ID of the job to start
            session_id: Session identifier

        Returns:
            Job start result with workflow info
        """
        job_manager = get_job_manager()
        workflow_engine = await get_workflow_engine()

        # Start the job
        job = job_manager.start_job(user_id, job_id)

        # Start the workflow
        workflow_state = await workflow_engine.start_workflow(
            user_id=user_id,
            workflow_id=job.definition.workflow_id,
            job_id=job_id,
        )

        # Update session context
        session_manager = await get_session_manager()
        session = await session_manager.get_session(session_id)
        if session:
            session.context.active_job_id = job_id
            session.context.workflow_id = job.definition.workflow_id
            await session_manager.update_session(session)

        logger.info(f"User {user_id} started job {job_id}")

        return {
            "status": "started",
            "job_id": job_id,
            "job_title": job.definition.title,
            "workflow_id": job.definition.workflow_id,
            "current_step": workflow_state.current_step,
            "job_context": job.get_full_context(),
        }

    @staticmethod
    async def get_current_task(user_id: str) -> dict[str, Any]:
        """Get the current task based on workflow state.

        Args:
            user_id: User identifier

        Returns:
            Current task information
        """
        workflow_engine = await get_workflow_engine()
        job_manager = get_job_manager()

        # Get current workflow task
        task = workflow_engine.get_current_task(user_id)

        # Get job context
        job = job_manager.get_active_job(user_id)
        if job:
            task["job_context"] = job.get_full_context()

        logger.info(f"User {user_id} retrieved current task: {task.get('step_name')}")
        return task

    @staticmethod
    async def submit_work(
        user_id: str,
        work_description: str,
        artifacts: Optional[list[str]] = None,
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Submit completed work for the current step.

        Args:
            user_id: User identifier
            work_description: Description of completed work
            artifacts: File paths or references to created artifacts
            session_id: Session identifier for budget tracking

        Returns:
            Submission result
        """
        workflow_engine = await get_workflow_engine()
        job_manager = get_job_manager()

        # Submit work to workflow
        result = await workflow_engine.submit_work(
            user_id=user_id,
            work_description=work_description,
            artifacts=artifacts,
            session_id=session_id,
        )

        # Record submission in job
        job = job_manager.get_active_job(user_id)
        if job:
            job.record_submission(work_description, artifacts)

        logger.info(f"User {user_id} submitted work: {result.get('status')}")
        return result

    @staticmethod
    async def request_review(
        user_id: str,
        session_id: str,
        review_context: Optional[str] = None,
    ) -> dict[str, Any]:
        """Request review/approval from another agent.

        Args:
            user_id: User identifier
            session_id: Session identifier for budget tracking
            review_context: Additional context for the reviewer

        Returns:
            Review result
        """
        workflow_engine = await get_workflow_engine()

        # Request review from workflow-defined agent
        result = await workflow_engine.request_review(
            user_id=user_id,
            session_id=session_id,
        )

        logger.info(f"User {user_id} requested review: {result.get('status')}")
        return result

    @staticmethod
    async def query_context(
        user_id: str,
        query: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        """Search the codebase vector database for relevant context.

        Args:
            user_id: User identifier
            query: Natural language search query
            limit: Max results to return

        Returns:
            Search results with metadata
        """
        results = await search_codebase(
            user_id=user_id,
            query=query,
            limit=limit,
        )

        logger.info(f"User {user_id} searched codebase: {len(results)} results")

        if not results:
            return {
                "results": [],
                "count": 0,
                "message": "No codebase context indexed yet. The vector database is empty. You can work with the job context provided in the current task."
            }

        return {
            "results": [
                {
                    "id": r.id,
                    "score": r.score,
                    "content": r.content,
                    "metadata": r.metadata,
                }
                for r in results
            ],
            "count": len(results),
            "message": f"Found {len(results)} relevant context items"
        }

    @staticmethod
    async def get_agent_guidance(
        user_id: str,
        agent_id: str,
        question: str,
        session_id: str,
    ) -> dict[str, Any]:
        """Ask another agent for guidance or consultation.

        Args:
            user_id: User identifier
            agent_id: Agent to consult (e.g., 'manager', 'architect')
            question: Question to ask the agent
            session_id: Session identifier for budget tracking

        Returns:
            Agent's guidance
        """
        # Get agent definition
        agent_registry = get_agent_registry()
        agent_def = agent_registry.get(agent_id)

        if not agent_def:
            return {"error": f"Agent not found: {agent_id}"}

        # Get job context
        job_manager = get_job_manager()
        job = job_manager.get_active_job(user_id)
        job_context = job.get_full_context() if job else None

        # Create agent instance
        session_manager = await get_session_manager()
        agent = Agent(
            definition=agent_def,
            session_manager=session_manager,
            user_id=user_id,
        )

        # Get guidance
        response = await agent.get_guidance(
            question=question,
            job_context=job_context,
            session_id=session_id,
        )

        logger.info(f"User {user_id} consulted agent {agent_id}")

        return {
            "agent": agent_def.name,
            "guidance": response,
        }

    @staticmethod
    async def get_workflow_status(user_id: str) -> dict[str, Any]:
        """Get current workflow status.

        Args:
            user_id: User identifier

        Returns:
            Workflow status
        """
        workflow_engine = await get_workflow_engine()
        state = await workflow_engine.get_workflow_state(user_id)

        if not state:
            return {"status": "no_active_workflow"}

        return {
            "workflow_id": state.workflow_id,
            "job_id": state.job_id,
            "current_step": state.current_step,
            "is_completed": state.is_completed,
            "started_at": state.started_at.isoformat(),
            "completed_at": state.completed_at.isoformat() if state.completed_at else None,
            "step_statuses": {k: v.value for k, v in state.step_statuses.items()},
        }

    @staticmethod
    async def get_budget_status(session_id: str) -> dict[str, Any]:
        """Get budget status for current session.

        Args:
            session_id: Session identifier

        Returns:
            Budget information
        """
        session_manager = await get_session_manager()
        budget = await session_manager.get_budget_info(session_id)

        if not budget:
            return {"error": "Session not found"}

        return {
            "total_budget": budget.total_budget,
            "used_budget": budget.used_budget,
            "remaining_budget": budget.remaining_budget,
            "usage_percentage": budget.usage_percentage,
            "reset_date": budget.reset_date.isoformat(),
        }
