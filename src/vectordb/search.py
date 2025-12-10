"""Semantic search functionality."""

import logging
from typing import Any, Optional

from pydantic import BaseModel

from src.vectordb.client import get_qdrant_manager
from src.vectordb.embeddings import get_embedding_generator

logger = logging.getLogger(__name__)


class SearchResult(BaseModel):
    """Search result model."""

    id: str
    score: float
    content: str
    metadata: dict[str, Any]


async def search_codebase(
    user_id: str,
    query: str,
    limit: int = 5,
    score_threshold: Optional[float] = 0.7,
) -> list[SearchResult]:
    """Search user's codebase with semantic search.

    Args:
        user_id: User identifier
        query: Search query
        limit: Maximum results
        score_threshold: Minimum similarity score

    Returns:
        List of search results (empty if no index exists)
    """
    try:
        # Generate query embedding
        embedding_gen = await get_embedding_generator()
        query_vector = await embedding_gen.generate(query)

        # Search Qdrant
        qdrant = await get_qdrant_manager()
        
        # Check if collection exists and has documents
        collection_info = await qdrant.get_collection_info(user_id)
        if not collection_info:
            logger.info(f"No index found for user {user_id}")
            return []
        
        if collection_info.points_count == 0:
            logger.info(f"Index exists but is empty for user {user_id}")
            return []
        
        points = await qdrant.search(
            user_id=user_id,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )

        # Convert to SearchResult
        results = []
        for point in points:
            results.append(
                SearchResult(
                    id=str(point.id),
                    score=point.score,
                    content=point.payload.get("content", ""),
                    metadata=point.payload.get("metadata", {}),
                )
            )

        logger.info(f"Search returned {len(results)} results for user {user_id}")
        return results
    
    except Exception as e:
        logger.warning(f"Search failed for user {user_id}: {e}")
        # Return empty results instead of failing
        return []
