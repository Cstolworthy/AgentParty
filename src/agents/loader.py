"""Agent definition loader."""

import logging
from pathlib import Path
from typing import Any, Literal, Optional

import yaml
from pydantic import BaseModel, Field

from src.config import get_settings

logger = logging.getLogger(__name__)


class ModelConfig(BaseModel):
    """LLM model configuration."""

    provider: Literal["openai", "anthropic", "azure", "ollama"]
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class AgentDefinition(BaseModel):
    """Agent definition loaded from directory."""

    id: str
    name: str
    description: Optional[str] = None
    llm_config: ModelConfig  # Renamed from model_config (reserved in Pydantic v2)
    prompt_files: list[str] = Field(default_factory=list)
    system_prompt: str = ""  # Compiled from all prompt files
    metadata: dict[str, Any] = Field(default_factory=dict)


def load_agent_definition(agent_id: str) -> AgentDefinition:
    """Load agent definition from directory.

    Args:
        agent_id: Agent identifier (directory name)

    Returns:
        AgentDefinition object

    Raises:
        FileNotFoundError: If agent directory or index.yaml not found
        ValueError: If agent definition is invalid
    """
    settings = get_settings()
    agent_dir = Path(settings.agents_dir) / agent_id

    if not agent_dir.exists():
        raise FileNotFoundError(f"Agent directory not found: {agent_dir}")

    # Load index.yaml
    index_file = agent_dir / "index.yaml"
    if not index_file.exists():
        raise FileNotFoundError(f"Agent index.yaml not found: {index_file}")

    with open(index_file, "r", encoding="utf-8") as f:
        index_data = yaml.safe_load(f)

    # Parse LLM config
    llm_config = ModelConfig(**index_data.get("model", {}))

    # Get prompt files
    prompt_files = index_data.get("prompt_files", [])

    # Load and compile prompt files
    system_prompt_parts = []
    for prompt_file in prompt_files:
        prompt_path = agent_dir / prompt_file
        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    system_prompt_parts.append(content)
        else:
            logger.warning(f"Prompt file not found: {prompt_path}")

    # Compile system prompt
    system_prompt = "\n\n---\n\n".join(system_prompt_parts)

    # Create agent definition
    agent_def = AgentDefinition(
        id=agent_id,
        name=index_data.get("name", agent_id),
        description=index_data.get("description"),
        llm_config=llm_config,
        prompt_files=prompt_files,
        system_prompt=system_prompt,
        metadata=index_data.get("metadata", {}),
    )

    logger.info(f"Loaded agent definition: {agent_id}")
    return agent_def


def list_available_agents() -> list[str]:
    """List all available agent IDs.

    Returns:
        List of agent IDs
    """
    settings = get_settings()
    agents_dir = Path(settings.agents_dir)

    if not agents_dir.exists():
        return []

    # Find directories with index.yaml
    agent_ids = []
    for item in agents_dir.iterdir():
        if item.is_dir() and (item / "index.yaml").exists():
            agent_ids.append(item.name)

    return sorted(agent_ids)
