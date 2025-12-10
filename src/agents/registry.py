"""Agent registry for managing loaded agents."""

import logging
from typing import Optional

from src.agents.loader import AgentDefinition, list_available_agents, load_agent_definition

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for managing agent definitions."""

    def __init__(self):
        """Initialize agent registry."""
        self._agents: dict[str, AgentDefinition] = {}
        self._load_all_agents()

    def _load_all_agents(self) -> None:
        """Load all available agent definitions."""
        agent_ids = list_available_agents()
        logger.info(f"Found {len(agent_ids)} agent definitions")

        for agent_id in agent_ids:
            try:
                definition = load_agent_definition(agent_id)
                self._agents[agent_id] = definition
            except Exception as e:
                logger.error(f"Failed to load agent {agent_id}: {e}")

    def get(self, agent_id: str) -> Optional[AgentDefinition]:
        """Get agent definition by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentDefinition if found, None otherwise
        """
        return self._agents.get(agent_id)

    def list(self) -> list[str]:
        """List all registered agent IDs.

        Returns:
            List of agent IDs
        """
        return list(self._agents.keys())

    def reload(self, agent_id: Optional[str] = None) -> None:
        """Reload agent definition(s).

        Args:
            agent_id: Specific agent to reload, or None to reload all
        """
        if agent_id:
            try:
                definition = load_agent_definition(agent_id)
                self._agents[agent_id] = definition
                logger.info(f"Reloaded agent: {agent_id}")
            except Exception as e:
                logger.error(f"Failed to reload agent {agent_id}: {e}")
        else:
            self._agents.clear()
            self._load_all_agents()
            logger.info("Reloaded all agents")


# Global registry instance
_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get global agent registry instance.

    Returns:
        AgentRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
