"""Codebase ingestion utilities for vector database."""

import logging
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from qdrant_client import models

from src.vectordb.client import get_qdrant_manager
from src.vectordb.embeddings import get_embedding_generator

logger = logging.getLogger(__name__)


class CodebaseIngestion:
    """Utilities for indexing codebases into vector database."""

    # File extensions to index
    CODE_EXTENSIONS = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".c", ".h",
        ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala",
        ".sh", ".bash", ".sql", ".yaml", ".yml", ".json", ".xml", ".html",
        ".css", ".scss", ".md", ".txt", ".toml", ".ini", ".env.example"
    }

    # Directories to skip
    SKIP_DIRS = {
        ".git", ".vscode", ".idea", "__pycache__", "node_modules",
        "venv", "env", ".env", "dist", "build", "target", ".pytest_cache",
        "coverage", ".coverage", ".mypy_cache", ".tox", "eggs", ".eggs"
    }

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize ingestion utility.

        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def index_codebase(
        self,
        user_id: str,
        repo_path: str,
        clear_existing: bool = False,
    ) -> dict:
        """Index a codebase into user's vector database.

        Args:
            user_id: User identifier
            repo_path: Path to repository
            clear_existing: Whether to clear existing vectors

        Returns:
            Ingestion statistics
        """
        qdrant = await get_qdrant_manager()
        embeddings = await get_embedding_generator()

        # Ensure collection exists
        collection_name = await qdrant.ensure_collection(user_id)

        # Clear existing if requested
        if clear_existing:
            await qdrant.delete_collection(user_id)
            collection_name = await qdrant.ensure_collection(user_id)
            logger.info(f"Cleared existing vectors for user {user_id}")

        # Scan files
        repo = Path(repo_path)
        if not repo.exists():
            raise FileNotFoundError(f"Repository not found: {repo_path}")

        files = self._scan_files(repo)
        logger.info(f"Found {len(files)} files to index")

        # Process files in batches
        total_chunks = 0
        batch_size = 10
        points_batch = []

        for i, file_path in enumerate(files):
            try:
                chunks = self._chunk_file(file_path, repo)

                for chunk_idx, chunk in enumerate(chunks):
                    # Generate embedding
                    embedding = await embeddings.generate(chunk["content"])

                    # Create point
                    point = models.PointStruct(
                        id=str(uuid4()),
                        vector=embedding,
                        payload={
                            "content": chunk["content"],
                            "metadata": {
                                "file_path": chunk["file_path"],
                                "relative_path": chunk["relative_path"],
                                "chunk_index": chunk_idx,
                                "total_chunks": len(chunks),
                                "language": chunk["language"],
                                "user_id": user_id,
                            },
                        },
                    )
                    points_batch.append(point)
                    total_chunks += 1

                    # Upload batch if full
                    if len(points_batch) >= batch_size:
                        await qdrant.upsert_documents(user_id, points_batch)
                        logger.debug(f"Uploaded batch of {len(points_batch)} chunks")
                        points_batch = []

                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(files)} files...")

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue

        # Upload remaining
        if points_batch:
            await qdrant.upsert_documents(user_id, points_batch)

        stats = {
            "user_id": user_id,
            "repository": str(repo_path),
            "files_indexed": len(files),
            "chunks_created": total_chunks,
            "collection": collection_name,
        }

        logger.info(f"Indexing complete: {stats}")
        return stats

    def _scan_files(self, repo_path: Path) -> List[Path]:
        """Scan repository for code files.

        Args:
            repo_path: Repository root path

        Returns:
            List of file paths to index
        """
        files = []

        for item in repo_path.rglob("*"):
            # Skip directories
            if item.is_dir():
                continue

            # Skip if in excluded directory
            if any(skip_dir in item.parts for skip_dir in self.SKIP_DIRS):
                continue

            # Check extension
            if item.suffix.lower() in self.CODE_EXTENSIONS:
                files.append(item)

        return files

    def _chunk_file(self, file_path: Path, repo_root: Path) -> List[dict]:
        """Chunk a file into smaller pieces.

        Args:
            file_path: Path to file
            repo_root: Repository root path

        Returns:
            List of chunks with metadata
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return []

        # Get relative path
        try:
            relative_path = str(file_path.relative_to(repo_root))
        except ValueError:
            relative_path = str(file_path)

        # Detect language
        language = self._detect_language(file_path)

        # If file is small enough, return as single chunk
        if len(content) <= self.chunk_size:
            return [
                {
                    "content": content,
                    "file_path": str(file_path),
                    "relative_path": relative_path,
                    "language": language,
                }
            ]

        # Split into chunks
        chunks = []
        start = 0

        while start < len(content):
            end = start + self.chunk_size

            # Try to break at newline
            if end < len(content):
                newline_pos = content.rfind("\n", start, end)
                if newline_pos != -1 and newline_pos > start + self.chunk_size // 2:
                    end = newline_pos + 1

            chunk_content = content[start:end]

            chunks.append(
                {
                    "content": chunk_content,
                    "file_path": str(file_path),
                    "relative_path": relative_path,
                    "language": language,
                }
            )

            # Move start forward with overlap
            start = end - self.chunk_overlap

        return chunks

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension.

        Args:
            file_path: File path

        Returns:
            Language name
        """
        ext = file_path.suffix.lower()

        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "shell",
            ".bash": "shell",
            ".sql": "sql",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".md": "markdown",
            ".txt": "text",
        }

        return language_map.get(ext, "unknown")


async def index_codebase_cli(
    user_id: str,
    repo_path: str,
    chunk_size: int = 1000,
    clear_existing: bool = False,
) -> None:
    """CLI function to index a codebase.

    Args:
        user_id: User identifier
        repo_path: Path to repository
        chunk_size: Maximum characters per chunk
        clear_existing: Whether to clear existing vectors
    """
    ingestion = CodebaseIngestion(chunk_size=chunk_size)
    stats = await ingestion.index_codebase(
        user_id=user_id,
        repo_path=repo_path,
        clear_existing=clear_existing,
    )

    print("\n=== Ingestion Complete ===")
    print(f"User: {stats['user_id']}")
    print(f"Repository: {stats['repository']}")
    print(f"Files indexed: {stats['files_indexed']}")
    print(f"Chunks created: {stats['chunks_created']}")
    print(f"Collection: {stats['collection']}")
