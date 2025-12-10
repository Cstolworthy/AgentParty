"""Tests for vector database."""

import pytest

from src.vectordb.search import SearchResult


def test_search_result():
    """Test search result model."""
    result = SearchResult(
        id="doc-123",
        score=0.95,
        content="This is a code snippet",
        metadata={"file_path": "/src/main.py", "language": "python"},
    )

    assert result.id == "doc-123"
    assert result.score == 0.95
    assert "code snippet" in result.content
    assert result.metadata["language"] == "python"


@pytest.mark.asyncio
async def test_qdrant_manager(mock_qdrant):
    """Test Qdrant manager initialization."""
    from src.vectordb.client import QdrantManager

    manager = QdrantManager(mock_qdrant)

    # Test collection name generation
    collection_name = manager._get_collection_name("test@example.com")
    assert collection_name == "codebase_test_at_example_com"


def test_ingestion_language_detection():
    """Test language detection from file extension."""
    from pathlib import Path

    from src.vectordb.ingestion import CodebaseIngestion

    ingestion = CodebaseIngestion()

    assert ingestion._detect_language(Path("test.py")) == "python"
    assert ingestion._detect_language(Path("test.js")) == "javascript"
    assert ingestion._detect_language(Path("test.ts")) == "typescript"
    assert ingestion._detect_language(Path("test.go")) == "go"
    assert ingestion._detect_language(Path("test.unknown")) == "unknown"


def test_ingestion_file_filtering():
    """Test file filtering in ingestion."""
    from pathlib import Path

    from src.vectordb.ingestion import CodebaseIngestion

    ingestion = CodebaseIngestion()

    # Test extension filtering
    assert ".py" in ingestion.CODE_EXTENSIONS
    assert ".js" in ingestion.CODE_EXTENSIONS
    assert ".exe" not in ingestion.CODE_EXTENSIONS

    # Test skip directories
    assert "node_modules" in ingestion.SKIP_DIRS
    assert ".git" in ingestion.SKIP_DIRS
    assert "__pycache__" in ingestion.SKIP_DIRS
