"""File system watcher for hot-reloading agents."""

import logging
from pathlib import Path
from typing import Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from src.agents.registry import get_agent_registry

logger = logging.getLogger(__name__)


class AgentFileHandler(FileSystemEventHandler):
    """Handler for agent file changes."""

    def __init__(self, agents_dir: str):
        """Initialize handler.
        
        Args:
            agents_dir: Path to agents directory
        """
        self.agents_dir = Path(agents_dir)
        self.registry = get_agent_registry()

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification.
        
        Args:
            event: File system event
        """
        if event.is_directory:
            return
        
        self._handle_change(event.src_path, "modified")

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation.
        
        Args:
            event: File system event
        """
        if event.is_directory:
            # New agent directory created
            agent_id = Path(event.src_path).name
            logger.info(f"New agent directory detected: {agent_id}")
            self.registry.reload(agent_id)
        else:
            self._handle_change(event.src_path, "created")

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion.
        
        Args:
            event: File system event
        """
        self._handle_change(event.src_path, "deleted")

    def _handle_change(self, file_path: str, event_type: str) -> None:
        """Handle file change.
        
        Args:
            file_path: Path to changed file
            event_type: Type of change
        """
        path = Path(file_path)
        
        # Check if it's in an agent directory
        try:
            relative = path.relative_to(self.agents_dir)
            parts = relative.parts
            
            if len(parts) >= 1:
                agent_id = parts[0]
                file_name = path.name
                
                # Reload agent if it's a relevant file
                if file_name in ["index.yaml", "system-prompt.md", "principles.md", 
                                 "patterns.md", "anti-patterns.md", "validation-criteria.md",
                                 "documentation-standards.md", "spec-template.md", 
                                 "api-design-guide.md", "standards-checklist.md",
                                 "linting-rules.md", "code-review-guide.md",
                                 "testing-strategy.md", "test-cases.md",
                                 "review-criteria.md", "team-standards.md",
                                 "security-checklist.md", "compliance-rules.md",
                                 "validation-criteria.md", "prioritization-guide.md",
                                 "workflow-management.md"]:
                    logger.info(f"Agent file {event_type}: {agent_id}/{file_name}")
                    logger.info(f"Hot-reloading agent: {agent_id}")
                    self.registry.reload(agent_id)
        except ValueError:
            # File not in agents directory
            pass


class AgentWatcher:
    """File system watcher for agent hot-reloading."""

    def __init__(self, agents_dir: str):
        """Initialize watcher.
        
        Args:
            agents_dir: Path to agents directory
        """
        self.agents_dir = agents_dir
        self.observer: Optional[PollingObserver] = None
        self.handler = AgentFileHandler(agents_dir)

    def start(self) -> None:
        """Start watching for file changes."""
        # Use PollingObserver for Docker volume compatibility
        self.observer = PollingObserver(timeout=1)
        self.observer.schedule(self.handler, self.agents_dir, recursive=True)
        self.observer.start()
        logger.info(f"Agent hot-reload watcher started for: {self.agents_dir}")

    def stop(self) -> None:
        """Stop watching for file changes."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Agent hot-reload watcher stopped")


# Global watcher instance
_watcher: Optional[AgentWatcher] = None


def start_agent_watcher(agents_dir: str) -> None:
    """Start the global agent watcher.
    
    Args:
        agents_dir: Path to agents directory
    """
    global _watcher
    
    if _watcher is None:
        _watcher = AgentWatcher(agents_dir)
        _watcher.start()


def stop_agent_watcher() -> None:
    """Stop the global agent watcher."""
    global _watcher
    
    if _watcher:
        _watcher.stop()
        _watcher = None
