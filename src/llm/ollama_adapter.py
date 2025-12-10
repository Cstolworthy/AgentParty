"""Ollama LLM adapter for local models."""

import logging
from typing import List, Optional

import httpx

from src.llm.base import BaseLLMAdapter, ChatMessage, LLMResponse

logger = logging.getLogger(__name__)


class OllamaAdapter(BaseLLMAdapter):
    """Adapter for Ollama local LLM server."""

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = None,
        **kwargs
    ):
        """Initialize Ollama adapter.
        
        Args:
            model: Model name (e.g., "llama3.2", "qwen2.5-coder")
            base_url: Ollama server URL
        """
        import os
        
        self.model = model
        
        # Get base URL from environment or use default
        if base_url is None:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/chat"

    async def chat_completion(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate chat completion using Ollama.
        
        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLM response
        """
        # Convert messages to Ollama format
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Build request
        request_data = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
        }

        if temperature is not None:
            request_data["options"] = {"temperature": temperature}
        
        if max_tokens is not None:
            if "options" not in request_data:
                request_data["options"] = {}
            request_data["options"]["num_predict"] = max_tokens

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.api_url,
                    json=request_data,
                )
                response.raise_for_status()
                result = response.json()

            # Extract response
            content = result["message"]["content"]
            
            # Ollama doesn't return token counts in non-streaming mode
            # Rough estimate: ~4 chars per token
            prompt_tokens = sum(len(m.content) for m in messages) // 4
            completion_tokens = len(content) // 4
            total_tokens = prompt_tokens + completion_tokens

            return LLMResponse(
                content=content,
                model=self.model,
                tokens_used=total_tokens,
                cost_usd=0.0,  # Local model - free!
            )

        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost (always 0 for local models)
        """
        return 0.0

    async def count_tokens(self, text: str) -> int:
        """Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count (~4 chars per token)
        """
        return len(text) // 4

    async def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Stream chat completion (not implemented for Ollama yet).
        
        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            Response chunks
        """
        # For now, just return the full response
        response = await self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        yield response.content
