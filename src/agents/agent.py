"""Agent runtime class."""

import logging
from typing import Optional

from src.agents.loader import AgentDefinition
from src.llm.base import BaseLLMAdapter, ChatMessage, LLMResponse
from src.llm.factory import get_llm_adapter
from src.session.manager import SessionManager

logger = logging.getLogger(__name__)


class Agent:
    """Runtime agent instance."""

    def __init__(
        self,
        definition: AgentDefinition,
        session_manager: Optional[SessionManager] = None,
        user_id: Optional[str] = None,
    ):
        """Initialize agent.

        Args:
            definition: Agent definition
            session_manager: Session manager for budget tracking
            user_id: User ID for budget tracking
        """
        self.definition = definition
        self.session_manager = session_manager
        self.user_id = user_id

        # Initialize LLM adapter
        self.llm = get_llm_adapter(
            provider=definition.llm_config.provider,
            model=definition.llm_config.model,
        )

    async def chat(
        self,
        message: str,
        context: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> LLMResponse:
        """Send message to agent and get response.

        Args:
            message: User message
            context: Optional additional context
            session_id: Session ID for budget tracking

        Returns:
            Agent response

        Raises:
            ValueError: If budget is exceeded
        """
        # Build messages
        messages = [ChatMessage(role="system", content=self.definition.system_prompt)]

        if context:
            messages.append(
                ChatMessage(
                    role="system",
                    content=f"Additional Context:\n{context}",
                )
            )

        messages.append(ChatMessage(role="user", content=message))

        # Check budget before making request
        if session_id and self.session_manager:
            # Estimate cost (rough approximation)
            total_chars = sum(len(m.content) for m in messages)
            estimated_tokens = total_chars // 4
            estimated_cost = self.llm.estimate_cost(estimated_tokens, estimated_tokens)

            # Check if user can afford this
            budget_info = await self.session_manager.get_budget_info(session_id)
            if budget_info and not budget_info.can_spend(estimated_cost):
                raise ValueError(
                    f"Budget exceeded. Remaining: ${budget_info.remaining_budget:.2f}, "
                    f"Estimated cost: ${estimated_cost:.4f}"
                )

        # Generate response
        response = await self.llm.chat_completion(
            messages=messages,
            temperature=self.definition.llm_config.temperature,
            max_tokens=self.definition.llm_config.max_tokens,
        )

        # Track spending
        if session_id and self.session_manager:
            await self.session_manager.track_spending(session_id, response.cost_usd)
            logger.info(
                f"Agent {self.definition.id} spent ${response.cost_usd:.4f} "
                f"for user {self.user_id}"
            )

        return response

    async def get_guidance(
        self,
        question: str,
        job_context: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """Get guidance from agent on a specific question.

        Args:
            question: Question to ask
            job_context: Optional job context
            session_id: Session ID for budget tracking

        Returns:
            Agent's guidance
        """
        response = await self.chat(
            message=question,
            context=job_context,
            session_id=session_id,
        )
        return response.content

    async def review_work(
        self,
        work_description: str,
        artifacts: Optional[list[str]] = None,
        session_id: Optional[str] = None,
    ) -> dict[str, any]:
        """Review submitted work.

        Args:
            work_description: Description of work done
            artifacts: List of artifacts/files
            session_id: Session ID for budget tracking

        Returns:
            Review result with approval status and feedback
        """
        # Build review prompt
        artifacts_str = "\n".join(artifacts) if artifacts else "No artifacts provided"
        review_prompt = f"""
Please review the following work:

Work Description:
{work_description}

Artifacts:
{artifacts_str}

Provide your review in the following format:
1. APPROVED or CHANGES_REQUESTED
2. Detailed feedback
3. Specific action items (if changes requested)
"""

        response = await self.chat(
            message=review_prompt,
            session_id=session_id,
        )

        # Parse response (simple parsing for now)
        content = response.content
        approved = "APPROVED" in content.split("\n")[0]

        return {
            "approved": approved,
            "feedback": content,
            "reviewer": self.definition.name,
            "cost": response.cost_usd,
        }
