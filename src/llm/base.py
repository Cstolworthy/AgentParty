"""Base LLM adapter interface."""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Literal, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Chat message model."""

    role: Literal["system", "user", "assistant"]
    content: str


class LLMResponse(BaseModel):
    """LLM response model."""

    content: str
    model: str
    tokens_used: int
    cost_usd: float


class BaseLLMAdapter(ABC):
    """Base class for LLM adapters."""

    @abstractmethod
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
            stream: Whether to stream the response

        Returns:
            LLM response
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Input text

        Returns:
            Token count
        """
        pass

    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        pass
