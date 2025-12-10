"""LLM adapter factory."""

import logging
from typing import Optional

from src.llm.anthropic_adapter import AnthropicAdapter
from src.llm.base import BaseLLMAdapter
from src.llm.ollama_adapter import OllamaAdapter
from src.llm.openai_adapter import OpenAIAdapter

logger = logging.getLogger(__name__)


def get_llm_adapter(
    provider: str,
    model: str,
    api_key: Optional[str] = None,
    **kwargs
) -> BaseLLMAdapter:
    """Get LLM adapter for specified provider.
    
    Args:
        provider: Provider name (openai, anthropic, azure, ollama)
        model: Model name
        api_key: API key (optional if in environment or ollama)
        **kwargs: Additional adapter arguments
        
    Returns:
        LLM adapter instance
        
    Raises:
        ValueError: If provider is not supported
    """
    if provider == "openai":
        return OpenAIAdapter(api_key=api_key, model=model, **kwargs)
    
    elif provider == "anthropic":
        return AnthropicAdapter(api_key=api_key, model=model, **kwargs)
    
    elif provider == "ollama":
        return OllamaAdapter(model=model, **kwargs)
    
    elif provider == "azure":
        # TODO: Implement Azure adapter
        raise NotImplementedError("Azure OpenAI adapter not yet implemented")

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
