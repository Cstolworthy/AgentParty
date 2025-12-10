"""Embedding generation for vector search."""

import logging
import os
from typing import Optional

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for text using Ollama."""

    def __init__(self, model: str = "nomic-embed-text"):
        """Initialize embedding generator.

        Args:
            model: Embedding model name (Ollama model)
        """
        self.model = model
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.api_url = f"{self.base_url}/api/embeddings"
        self.settings = get_settings()

    async def generate(self, text: str) -> list[float]:
        """Generate embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    json={
                        "model": self.model,
                        "prompt": text
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["embedding"]
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    async def generate_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            async with httpx.AsyncClient(timeout=30.0) as client:
                for text in texts:
                    response = await client.post(
                        self.api_url,
                        json={
                            "model": self.model,
                            "prompt": text
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    embeddings.append(result["embedding"])
            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            raise

    def estimate_cost(self, num_tokens: int) -> float:
        """Estimate cost for embedding generation.

        Args:
            num_tokens: Number of tokens

        Returns:
            Estimated cost in USD (always 0 for local Ollama)
        """
        return 0.0  # Local embeddings are free!


# Global embedding generator
_embedding_generator: Optional[EmbeddingGenerator] = None


async def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create global embedding generator.

    Returns:
        EmbeddingGenerator instance
    """
    global _embedding_generator

    if _embedding_generator is None:
        # Use nomic-embed-text from Ollama (free, local)
        _embedding_generator = EmbeddingGenerator(
            model="nomic-embed-text"
        )

    return _embedding_generator
