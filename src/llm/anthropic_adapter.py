"""Anthropic (Claude) LLM adapter."""

import logging
from typing import AsyncIterator, Optional

from anthropic import AsyncAnthropic

from src.llm.base import BaseLLMAdapter, ChatMessage, LLMResponse

logger = logging.getLogger(__name__)


class AnthropicAdapter(BaseLLMAdapter):
    """Anthropic Claude API adapter."""

    # Pricing per 1M tokens (as of Dec 2024)
    PRICING = {
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-2.1": {"input": 8.00, "output": 24.00},
        "claude-2.0": {"input": 8.00, "output": 24.00},
    }

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        """Initialize Anthropic adapter.

        Args:
            api_key: Anthropic API key
            model: Model name
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def chat_completion(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> LLMResponse:
        """Generate chat completion.

        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream (ignored, use chat_completion_stream)

        Returns:
            LLM response
        """
        # Separate system message from other messages
        system_msg = None
        chat_messages = []

        for msg in messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                chat_messages.append({"role": msg.role, "content": msg.content})

        # Call Anthropic API
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens or 4000,
            temperature=temperature,
            system=system_msg,
            messages=chat_messages,
        )

        # Extract response
        content = response.content[0].text if response.content else ""
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        tokens_used = input_tokens + output_tokens

        # Calculate cost
        cost = self.estimate_cost(input_tokens, output_tokens)

        return LLMResponse(
            content=content,
            model=self.model,
            tokens_used=tokens_used,
            cost_usd=cost,
        )

    async def chat_completion_stream(
        self,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Generate streaming chat completion.

        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Response chunks
        """
        # Separate system message
        system_msg = None
        chat_messages = []

        for msg in messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                chat_messages.append({"role": msg.role, "content": msg.content})

        # Call Anthropic API with streaming
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens or 4000,
            temperature=temperature,
            system=system_msg,
            messages=chat_messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def count_tokens(self, text: str) -> int:
        """Count tokens in text (approximation).

        Args:
            text: Input text

        Returns:
            Approximate token count
        """
        # Anthropic doesn't provide a tokenizer, approximate as chars/4
        return len(text) // 4

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        # Get pricing for model
        pricing = self.PRICING.get(
            self.model,
            self.PRICING.get("claude-3-sonnet-20240229"),  # Default pricing
        )

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost
