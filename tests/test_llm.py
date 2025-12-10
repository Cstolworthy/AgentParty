"""Tests for LLM adapters."""

import pytest

from src.llm.base import ChatMessage, LLMResponse


def test_chat_message():
    """Test chat message model."""
    msg = ChatMessage(role="user", content="Hello, agent!")

    assert msg.role == "user"
    assert msg.content == "Hello, agent!"


def test_llm_response():
    """Test LLM response model."""
    response = LLMResponse(
        content="Hello! How can I help?",
        model="gpt-4",
        tokens_used=150,
        cost_usd=0.0045,
    )

    assert response.content == "Hello! How can I help?"
    assert response.model == "gpt-4"
    assert response.tokens_used == 150
    assert response.cost_usd == 0.0045


def test_openai_cost_estimation():
    """Test OpenAI cost estimation."""
    from src.llm.openai_adapter import OpenAIAdapter

    adapter = OpenAIAdapter(api_key="test-key", model="gpt-4-turbo-preview")

    # Test cost calculation
    cost = adapter.estimate_cost(input_tokens=1000, output_tokens=500)

    # GPT-4 Turbo: $10/1M input, $30/1M output
    expected = (1000 / 1_000_000 * 10) + (500 / 1_000_000 * 30)
    assert abs(cost - expected) < 0.0001


def test_anthropic_cost_estimation():
    """Test Anthropic cost estimation."""
    from src.llm.anthropic_adapter import AnthropicAdapter

    adapter = AnthropicAdapter(api_key="test-key", model="claude-3-sonnet-20240229")

    # Test cost calculation
    cost = adapter.estimate_cost(input_tokens=1000, output_tokens=500)

    # Claude Sonnet: $3/1M input, $15/1M output
    expected = (1000 / 1_000_000 * 3) + (500 / 1_000_000 * 15)
    assert abs(cost - expected) < 0.0001
