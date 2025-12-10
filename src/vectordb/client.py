"""Qdrant vector database client."""

import logging
from typing import Optional

from qdrant_client import AsyncQdrantClient, models

from src.config import get_settings

logger = logging.getLogger(__name__)


class QdrantManager:
    """Manages Qdrant collections with per-user isolation."""

    def __init__(self, client: AsyncQdrantClient):
        """Initialize Qdrant manager.

        Args:
            client: Qdrant async client
        """
        self.client = client
        self.settings = get_settings()

    def _get_collection_name(self, user_id: str) -> str:
        """Get collection name for a user.

        Args:
            user_id: User identifier

        Returns:
            Collection name
        """
        # Sanitize user_id for collection name
        safe_user_id = user_id.replace("@", "_at_").replace(".", "_")
        return f"codebase_{safe_user_id}"

    async def ensure_collection(self, user_id: str) -> str:
        """Ensure collection exists for user.

        Args:
            user_id: User identifier

        Returns:
            Collection name
        """
        collection_name = self._get_collection_name(user_id)

        # Check if collection exists
        collections = await self.client.get_collections()
        exists = any(c.name == collection_name for c in collections.collections)

        if not exists:
            # Create collection
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=self.settings.embedding_dimensions,
                    distance=models.Distance.COSINE,
                ),
            )
            logger.info(f"Created Qdrant collection: {collection_name}")

        return collection_name

    async def delete_collection(self, user_id: str) -> None:
        """Delete user's collection.

        Args:
            user_id: User identifier
        """
        collection_name = self._get_collection_name(user_id)
        await self.client.delete_collection(collection_name)
        logger.info(f"Deleted Qdrant collection: {collection_name}")

    async def upsert_documents(
        self,
        user_id: str,
        points: list[models.PointStruct],
    ) -> None:
        """Insert or update documents in user's collection.

        Args:
            user_id: User identifier
            points: List of points to upsert
        """
        collection_name = await self.ensure_collection(user_id)

        await self.client.upsert(
            collection_name=collection_name,
            points=points,
        )

        logger.debug(f"Upserted {len(points)} points to {collection_name}")

    async def search(
        self,
        user_id: str,
        query_vector: list[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> list[models.ScoredPoint]:
        """Search user's collection.

        Args:
            user_id: User identifier
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum score threshold

        Returns:
            List of scored points
        """
        collection_name = await self.ensure_collection(user_id)

        results = await self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )

        return results

    async def get_collection_info(self, user_id: str) -> Optional[models.CollectionInfo]:
        """Get information about user's collection.

        Args:
            user_id: User identifier

        Returns:
            Collection info if exists, None otherwise
        """
        collection_name = self._get_collection_name(user_id)

        try:
            info = await self.client.get_collection(collection_name)
            return info
        except Exception:
            return None

    async def health_check(self) -> bool:
        """Check if Qdrant is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            collections = await self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False


# Global Qdrant manager
_qdrant_manager: Optional[QdrantManager] = None


async def get_qdrant_manager() -> QdrantManager:
    """Get or create global Qdrant manager.

    Returns:
        QdrantManager instance
    """
    global _qdrant_manager

    if _qdrant_manager is None:
        settings = get_settings()
        client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        _qdrant_manager = QdrantManager(client)

    return _qdrant_manager
