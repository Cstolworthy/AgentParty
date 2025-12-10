"""Pytest configuration and fixtures."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import redis.asyncio as redis
from qdrant_client import AsyncQdrantClient

from src.config import Settings


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Test settings with safe defaults."""
    return Settings(
        environment="development",
        redis_url="redis://localhost:6379",
        redis_db=15,  # Use separate DB for tests
        qdrant_url="http://localhost:6333",
        openai_api_key="test-key",
        default_user_budget=10.00,
        session_ttl_hours=1,
        agents_dir="tests/fixtures/agents",
        workflows_dir="tests/fixtures/workflows",
        jobs_dir="tests/fixtures/jobs",
    )


@pytest.fixture
async def mock_redis() -> AsyncMock:
    """Mock Redis client."""
    mock = AsyncMock(spec=redis.Redis)
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.setex = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.scan = AsyncMock(return_value=(0, []))
    return mock


@pytest.fixture
async def mock_qdrant() -> AsyncMock:
    """Mock Qdrant client."""
    mock = AsyncMock(spec=AsyncQdrantClient)
    mock.get_collections = AsyncMock(return_value=MagicMock(collections=[]))
    mock.create_collection = AsyncMock(return_value=True)
    mock.upsert = AsyncMock(return_value=True)
    mock.search = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    from src.llm.base import LLMResponse

    return LLMResponse(
        content="This is a mock response from the LLM.",
        model="gpt-4-test",
        tokens_used=100,
        cost_usd=0.001,
    )


@pytest.fixture
def sample_agent_definition():
    """Sample agent definition for testing."""
    from src.agents.loader import AgentDefinition, ModelConfig

    return AgentDefinition(
        id="test-agent",
        name="Test Agent",
        description="Test agent for unit tests",
        llm_config=ModelConfig(
            provider="openai",
            model="gpt-4-test",
            temperature=0.7,
        ),
        prompt_files=["system-prompt.md"],
        system_prompt="You are a test agent.",
        metadata={},
    )


@pytest.fixture
def sample_workflow_definition():
    """Sample workflow definition for testing."""
    from src.workflows.loader import WorkflowDefinition, WorkflowStep

    return WorkflowDefinition(
        id="test-workflow",
        name="Test Workflow",
        version="1.0",
        steps=[
            WorkflowStep(
                id="step1",
                name="First Step",
                agent="programmer",
                requires_approval=True,
                approval_agent="manager",
                next_step="step2",
            ),
            WorkflowStep(
                id="step2",
                name="Second Step",
                agent="qa-engineer",
                requires_approval=False,
                next_step=None,
            ),
        ],
    )


@pytest.fixture
def sample_job_definition():
    """Sample job definition for testing."""
    from src.jobs.loader import JobDefinition

    return JobDefinition(
        id="test-job",
        title="Test Job",
        workflow_id="test-workflow",
        assigned_to="programmer",
        priority="medium",
        context_files=["overview.md"],
        context_content="Test job context",
    )
