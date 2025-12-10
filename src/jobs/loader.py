"""Job definition loader."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field

from src.config import get_settings

logger = logging.getLogger(__name__)


class JobDefinition(BaseModel):
    """Job definition loaded from directory."""

    id: str
    title: str
    description: Optional[str] = None
    workflow_id: str
    assigned_to: str  # Which agent role this job is for
    priority: str = "medium"
    context_files: list[str] = Field(default_factory=list)
    context_content: str = ""  # Compiled from all context files
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    deadline: Optional[datetime] = None


def load_job_definition(job_id: str) -> JobDefinition:
    """Load job definition from directory.

    Args:
        job_id: Job identifier (directory name)

    Returns:
        JobDefinition object

    Raises:
        FileNotFoundError: If job directory or index.yaml not found
        ValueError: If job definition is invalid
    """
    settings = get_settings()
    job_dir = Path(settings.jobs_dir) / job_id

    if not job_dir.exists():
        raise FileNotFoundError(f"Job directory not found: {job_dir}")

    # Load index.yaml
    index_file = job_dir / "index.yaml"
    if not index_file.exists():
        raise FileNotFoundError(f"Job index.yaml not found: {index_file}")

    with open(index_file, "r", encoding="utf-8") as f:
        index_data = yaml.safe_load(f)

    # Get context files
    context_files = index_data.get("context_files", [])

    # Load and compile context files
    context_parts = []
    for context_file in context_files:
        context_path = job_dir / context_file
        if context_path.exists():
            with open(context_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    # Add file name as header
                    context_parts.append(f"## {context_file}\n\n{content}")
        else:
            logger.warning(f"Context file not found: {context_path}")

    # Compile context
    context_content = "\n\n---\n\n".join(context_parts)

    # Parse dates if present
    created_at = None
    deadline = None

    if "created_at" in index_data.get("metadata", {}):
        created_at = datetime.fromisoformat(index_data["metadata"]["created_at"])

    if "deadline" in index_data.get("metadata", {}):
        deadline = datetime.fromisoformat(index_data["metadata"]["deadline"])

    # Create job definition
    job_def = JobDefinition(
        id=job_id,
        title=index_data.get("title", job_id),
        description=index_data.get("description"),
        workflow_id=index_data["workflow"],
        assigned_to=index_data.get("assigned_to", "programmer"),
        priority=index_data.get("priority", "medium"),
        context_files=context_files,
        context_content=context_content,
        metadata=index_data.get("metadata", {}),
        created_at=created_at,
        deadline=deadline,
    )

    logger.info(f"Loaded job definition: {job_id}")
    return job_def


def list_available_jobs(assigned_to: Optional[str] = None) -> list[str]:
    """List all available job IDs.

    Args:
        assigned_to: Filter by assigned agent (optional)

    Returns:
        List of job IDs
    """
    settings = get_settings()
    jobs_dir = Path(settings.jobs_dir)

    if not jobs_dir.exists():
        return []

    # Find directories with index.yaml
    job_ids = []
    for item in jobs_dir.iterdir():
        if item.is_dir() and (item / "index.yaml").exists():
            # Filter by assigned_to if specified
            if assigned_to:
                try:
                    job_def = load_job_definition(item.name)
                    if job_def.assigned_to == assigned_to:
                        job_ids.append(item.name)
                except Exception as e:
                    logger.warning(f"Failed to load job {item.name}: {e}")
            else:
                job_ids.append(item.name)

    return sorted(job_ids)
