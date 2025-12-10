"""Tests for agent system."""

import pytest

from src.agents.loader import AgentDefinition, ModelConfig


def test_agent_definition_creation(sample_agent_definition):
    """Test agent definition model."""
    agent = sample_agent_definition

    assert agent.id == "test-agent"
    assert agent.name == "Test Agent"
    assert agent.llm_config.provider == "openai"
    assert agent.llm_config.model == "gpt-4-test"
    assert "test agent" in agent.system_prompt.lower()


def test_model_config():
    """Test model configuration."""
    config = ModelConfig(
        provider="anthropic",
        model="claude-3-sonnet",
        temperature=0.5,
        max_tokens=2000,
    )

    assert config.provider == "anthropic"
    assert config.model == "claude-3-sonnet"
    assert config.temperature == 0.5
    assert config.max_tokens == 2000


@pytest.mark.asyncio
async def test_agent_chat(sample_agent_definition, mock_llm_response, mocker):
    """Test agent chat functionality."""
    from src.agents.agent import Agent

    # Mock the LLM adapter
    mock_llm = mocker.MagicMock()
    mock_llm.chat_completion = mocker.AsyncMock(return_value=mock_llm_response)

    agent = Agent(definition=sample_agent_definition)
    agent.llm = mock_llm

    response = await agent.chat(message="Test question")

    assert response.content == "This is a mock response from the LLM."
    assert response.tokens_used == 100
    mock_llm.chat_completion.assert_called_once()
