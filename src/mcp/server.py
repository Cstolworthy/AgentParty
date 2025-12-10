"""MCP server implementation."""

import logging
from typing import Any

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, Resource

from src.config import get_settings
from src.mcp.tools import MCPTools
from src.session.auth import create_session, validate_session

logger = logging.getLogger(__name__)


def create_mcp_server() -> Server:
    """Create and configure MCP server.

    Returns:
        Configured MCP server instance
    """
    settings = get_settings()
    server = Server(settings.mcp_server_name)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available MCP tools."""
        return [
            Tool(
                name="get_available_jobs",
                description="List all jobs available for the current agent to work on",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                        "filter": {
                            "type": "string",
                            "description": "Optional filter (e.g., 'high-priority')",
                        },
                    },
                    "required": ["session_id"],
                },
            ),
            Tool(
                name="start_job",
                description="Initialize a job and load its workflow",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                        "job_id": {
                            "type": "string",
                            "description": "ID of the job to start",
                        },
                    },
                    "required": ["session_id", "job_id"],
                },
            ),
            Tool(
                name="get_current_task",
                description="Get the current task based on workflow state",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                    },
                    "required": ["session_id"],
                },
            ),
            Tool(
                name="submit_work",
                description="Submit completed work for the current step",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                        "work_description": {
                            "type": "string",
                            "description": "Description of completed work",
                        },
                        "artifacts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "File paths or references to created artifacts",
                        },
                    },
                    "required": ["session_id", "work_description"],
                },
            ),
            Tool(
                name="request_review",
                description="Request review/approval from another agent",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                        "review_context": {
                            "type": "string",
                            "description": "Additional context for the reviewer",
                        },
                    },
                    "required": ["session_id"],
                },
            ),
            Tool(
                name="query_context",
                description="Search the codebase vector database for relevant context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                        "query": {
                            "type": "string",
                            "description": "Natural language search query",
                        },
                        "limit": {
                            "type": "number",
                            "description": "Max results to return",
                            "default": 5,
                        },
                    },
                    "required": ["session_id", "query"],
                },
            ),
            Tool(
                name="get_agent_guidance",
                description="Ask another agent for guidance or consultation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "Agent to consult (e.g., 'manager', 'architect')",
                        },
                        "question": {
                            "type": "string",
                            "description": "Question to ask the agent",
                        },
                    },
                    "required": ["session_id", "agent_id", "question"],
                },
            ),
            Tool(
                name="get_workflow_status",
                description="Get current workflow status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                    },
                    "required": ["session_id"],
                },
            ),
            Tool(
                name="get_budget_status",
                description="Get budget status for current session",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier",
                        },
                    },
                    "required": ["session_id"],
                },
            ),
            Tool(
                name="create_session",
                description="Create a new session for a user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User identifier",
                        },
                    },
                    "required": ["user_id"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls."""
        import json

        try:
            # Extract session_id and validate
            session_id = arguments.get("session_id")
            user_id = None

            if name == "create_session":
                # Special case: creating a new session
                user_id = arguments.get("user_id")
                if not user_id:
                    return [TextContent(type="text", text=json.dumps({"error": "user_id required"}))]

                session = await create_session(user_id)
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "session_id": session.session_id,
                                "user_id": session.user_id,
                                "expires_at": session.expires_at.isoformat(),
                            }
                        ),
                    )
                ]

            # For all other tools, validate session
            if not session_id:
                return [TextContent(type="text", text=json.dumps({"error": "session_id required"}))]

            session = await validate_session(session_id)
            if not session:
                return [TextContent(type="text", text=json.dumps({"error": "Invalid or expired session"}))]

            user_id = session.user_id

            # Route to appropriate tool
            if name == "get_available_jobs":
                result = await MCPTools.get_available_jobs(
                    user_id=user_id,
                    filter_type=arguments.get("filter"),
                )
            elif name == "start_job":
                result = await MCPTools.start_job(
                    user_id=user_id,
                    job_id=arguments["job_id"],
                    session_id=session_id,
                )
            elif name == "get_current_task":
                result = await MCPTools.get_current_task(user_id=user_id)
            elif name == "submit_work":
                result = await MCPTools.submit_work(
                    user_id=user_id,
                    work_description=arguments["work_description"],
                    artifacts=arguments.get("artifacts"),
                    session_id=session_id,
                )
            elif name == "request_review":
                result = await MCPTools.request_review(
                    user_id=user_id,
                    session_id=session_id,
                    review_context=arguments.get("review_context"),
                )
            elif name == "query_context":
                result = await MCPTools.query_context(
                    user_id=user_id,
                    query=arguments["query"],
                    limit=arguments.get("limit", 5),
                )
            elif name == "get_agent_guidance":
                result = await MCPTools.get_agent_guidance(
                    user_id=user_id,
                    agent_id=arguments["agent_id"],
                    question=arguments["question"],
                    session_id=session_id,
                )
            elif name == "get_workflow_status":
                result = await MCPTools.get_workflow_status(user_id=user_id)
            elif name == "get_budget_status":
                result = await MCPTools.get_budget_status(session_id=session_id)
            else:
                result = {"error": f"Unknown tool: {name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            logger.error(f"Tool call error: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List available MCP resources.
        
        Resources expose agent definitions, workflows, and jobs as readable content.
        """
        from src.agents.registry import get_agent_registry
        from src.workflows.loader import list_available_workflows
        from src.jobs.manager import get_job_manager
        
        resources = []
        
        # System documentation resource
        resources.append(
            Resource(
                uri="agentparty://documentation",
                name="AgentParty System Documentation",
                description="Comprehensive technical documentation of the AgentParty MCP server, including all tools, resources, agents, workflows, and usage patterns",
                mimeType="text/markdown",
            )
        )
        
        # Agent definitions as resources
        agent_registry = get_agent_registry()
        for agent_id in agent_registry.list():
            resources.append(
                Resource(
                    uri=f"agent://{agent_id}",
                    name=f"Agent: {agent_id}",
                    description=f"Configuration and prompts for the {agent_id} agent",
                    mimeType="application/json",
                )
            )
        
        # Workflow definitions as resources
        for workflow_id in list_available_workflows():
            resources.append(
                Resource(
                    uri=f"workflow://{workflow_id}",
                    name=f"Workflow: {workflow_id}",
                    description=f"Complete workflow definition for {workflow_id} SDLC",
                    mimeType="application/yaml",
                )
            )
        
        # Job definitions as resources
        job_manager = get_job_manager()
        for job in job_manager.list_available():
            resources.append(
                Resource(
                    uri=f"job://{job.id}",
                    name=f"Job: {job.title}",
                    description=job.description,
                    mimeType="application/yaml",
                )
            )
        
        return resources

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a specific resource by URI.
        
        Supports:
        - agent://<agent-id> - Returns agent configuration and prompts
        - workflow://<workflow-id> - Returns workflow YAML definition
        - job://<job-id> - Returns job configuration and context
        """
        import json
        import yaml
        from pathlib import Path
        from src.agents.registry import get_agent_registry
        from src.workflows.loader import load_workflow_definition
        from src.jobs.manager import get_job_manager
        
        try:
            if uri == "agentparty://documentation":
                from src.mcp.documentation import get_full_documentation
                return get_full_documentation()
            
            elif uri.startswith("agent_unused://"):  # Old embedded doc removed
                doc = """# AgentParty MCP Server - Technical Documentation (UNUSED)

## Overview

AgentParty is a Model Context Protocol (MCP) server that orchestrates multi-agent software development workflows. It provides a complete SDLC automation platform using local LLMs through Ollama, with persistent workflow state stored in SQLite.

**Key Features:**
- 9 specialized AI agents for different SDLC roles
- 3 workflow definitions (C#, Node.js, Angular)
- Persistent workflow state (survives container restarts)
- Local LLM integration (zero API costs)
- Vector-based codebase search
- Budget and session management

**Technology Stack:**
- FastAPI for HTTP/SSE MCP transport
- SQLite for workflow persistence
- Qdrant for vector embeddings
- Redis for session storage
- Ollama for local LLM inference (qwen2.5-coder:7b)
- Docker Compose for orchestration

---

## MCP Tools

Tools are executable functions that perform actions in the AgentParty system.

### 1. `get_available_jobs`
**Purpose:** List all jobs available for the current agent.

**Parameters:**
- `session_id` (string, required): Session identifier
- `filter` (string, optional): Filter like 'high-priority'

**Returns:** Array of job objects with:
- `id`: Job identifier
- `title`: Human-readable job title
- `description`: What the job does
- `priority`: high/medium/low
- `workflow_id`: Associated workflow
- `assigned_to`: Agent or role

**Usage:** Call this to see what work is available before starting a job.

---

### 2. `start_job`
**Purpose:** Initialize a job and start its workflow.

**Parameters:**
- `session_id` (string, required): Session identifier
- `job_id` (string, required): ID of job to start

**Returns:**
- `status`: "started"
- `job_id`: Job identifier
- `job_title`: Job title
- `workflow_id`: Active workflow ID
- `current_step`: First workflow step ID
- `job_context`: Complete job context with requirements and specs

**What Happens:**
1. Loads job definition from `jobs/{job_id}/index.yaml`
2. Reads all context files (requirements, specs, etc.)
3. Creates workflow state in SQLite database
4. Sets first step to "in_progress"
5. Updates session context
6. Returns job context for the current step

**Persistence:** Workflow state is saved to SQLite at `./data/agentparty.db` and survives Docker restarts.

---

### 3. `get_current_task`
**Purpose:** Get the current workflow task and its requirements.

**Parameters:**
- `session_id` (string, required): Session identifier

**Returns:**
- `step_id`: Current step ID (e.g., "requirements")
- `step_name`: Human-readable name
- `description`: What needs to be done
- `agent`: Which agent should handle this
- `inputs`: Required inputs from previous steps
- `outputs`: Expected outputs
- `status`: Step status (in_progress, completed, etc.)
- `job_context`: Full job context and requirements

**Usage:** Call this to understand what you need to do next in the workflow.

---

### 4. `submit_work`
**Purpose:** Submit completed work for the current workflow step.

**Parameters:**
- `session_id` (string, required): Session identifier
- `work_description` (string, required): What you completed
- `artifacts` (array, required): List of file paths or deliverables

**Returns:**
- `status`: "submitted", "approved", "completed", etc.
- `message`: Human-readable status
- `next_step`: Next step info if workflow continues
- `requires_approval`: Boolean - if approval needed

**What Happens:**
1. Marks current step as completed
2. Checks if approvals are required
3. If approved, transitions to next step
4. Updates SQLite database
5. Records history entry

**Workflow Transitions:**
- With approval: Step → Approval Agent → Next Step
- Without approval: Step → Next Step
- If rejected: Returns to current step with feedback

---

### 5. `request_review`
**Purpose:** Request review from workflow-defined approval agent.

**Parameters:**
- `session_id` (string, required): Session identifier
- `review_context` (string, optional): Additional context for reviewer

**Returns:**
- `status`: "approved", "changes_requested"
- `reviewer`: Which agent reviewed
- `feedback`: Review comments
- `approved`: Boolean

**Approval Flow:**
Each workflow step can have approval requirements:
- Product Manager approves requirements
- Engineering Manager approves architecture
- Policy Gate approves security compliance

---

### 6. `get_agent_guidance`
**Purpose:** Ask another agent for consultation or guidance.

**Parameters:**
- `session_id` (string, required): Session identifier
- `agent_id` (string, required): Agent to consult (e.g., "architect")
- `question` (string, required): Your question

**Returns:**
- `agent`: Agent consulted
- `guidance`: Response from agent

**Usage:** When you need expert advice during your work, consult a specialist agent.

---

### 7. `query_context`
**Purpose:** Search the codebase vector database for relevant context.

**Parameters:**
- `session_id` (string, required): Session identifier
- `query` (string, required): Natural language search query
- `limit` (integer, optional): Max results (default 5)

**Returns:**
- `results`: Array of matching code chunks
- `count`: Number of results
- `message`: Status message

**Result Format:**
- `id`: Chunk identifier
- `score`: Relevance score (0-1)
- `content`: Code or text content
- `metadata`: File path, language, etc.

**Notes:**
- Returns helpful message if no index exists yet
- Uses local Ollama embeddings (nomic-embed-text)
- Searches across indexed codebase files

---

### 8. `get_workflow_status`
**Purpose:** Get current workflow status and progress.

**Parameters:**
- `session_id` (string, required): Session identifier

**Returns:**
- `workflow_id`: Active workflow
- `job_id`: Current job
- `current_step`: Current step ID
- `is_completed`: Boolean
- `started_at`: ISO timestamp
- `completed_at`: ISO timestamp or null
- `step_statuses`: Object mapping step IDs to statuses

**Step Statuses:**
- `pending`: Not started
- `in_progress`: Currently working
- `awaiting_approval`: Submitted, waiting for review
- `approved`: Approved, ready to proceed
- `changes_requested`: Needs rework
- `completed`: Finished
- `skipped`: Bypassed

---

### 9. `get_budget_status`
**Purpose:** Get session budget and LLM usage information.

**Parameters:**
- `session_id` (string, required): Session identifier

**Returns:**
- `tokens_used`: Total tokens consumed
- `cost_usd`: Estimated cost (always $0 with Ollama)
- `session_start`: When session started
- `budget_remaining`: Unlimited with local LLMs

**Note:** With Ollama, all costs are $0. This tracks usage for monitoring.

---

## MCP Resources

Resources are read-only content that can be accessed via URI schemes.

### 1. Agent Resources: `agent://<agent-id>`

**Format:** JSON

**Contains:**
- Agent configuration (name, description, model settings)
- LLM parameters (temperature, max tokens)
- Complete prompt content from all prompt files
- Expertise areas and focus areas

**Example:** `agent://architect` returns:
```json
{
  "id": "architect",
  "name": "Architect",
  "description": "System architect for technical design",
  "model": {
    "provider": "ollama",
    "model": "qwen2.5-coder:7b",
    "temperature": 0.6,
    "max_tokens": 4000
  },
  "prompts": {
    "system-prompt.md": "...",
    "principles.md": "...",
    "patterns.md": "...",
    "anti-patterns.md": "..."
  }
}
```

**Available Agents:**
- `architect`: System design and architecture patterns
- `requirements-engineer`: Requirements gathering and documentation
- `spec-author`: Technical specifications and API design
- `coding-standards-auditor`: Code review and standards enforcement
- `qa-engineer`: Testing strategy and test execution
- `policy-gate`: Security and compliance validation
- `engineering-manager`: Final review and approval
- `product-manager`: Business requirements validation
- `sdlc-orchestrator`: Workflow coordination

---

### 2. Workflow Resources: `workflow://<workflow-id>`

**Format:** YAML

**Contains:**
- Complete workflow definition
- All steps with names, descriptions, agents
- Input/output requirements per step
- Approval requirements
- Transition conditions

**Example:** `workflow://csharp` returns the C# development workflow with 9 steps.

**Available Workflows:**
- `csharp`: .NET/C# development workflow
- `node`: Node.js/TypeScript workflow
- `angular`: Angular frontend workflow

**Workflow Steps (typical):**
1. Requirements Analysis
2. Specification
3. Architecture Design
4. Implementation
5. Code Standards Audit
6. QA Testing
7. Security/Policy Gate
8. Final Review
9. Complete

---

### 3. Job Resources: `job://<job-id>`

**Format:** YAML

**Contains:**
- Job metadata (title, description, priority)
- Associated workflow
- Complete context file contents
- Deadline information

**Example:** `job://Calculator` returns:
```yaml
id: Calculator
title: C# Console Symbolic Calculator
description: Build a calculator with symbolic math
workflow_id: csharp
priority: high
context:
  overview.md: |
    # Project Overview
    ...
  requirements.md: |
    # Requirements
    ...
```

---

## Workflow Architecture

### State Machine

Workflows follow a state machine model:

```
START → Step 1 → [Approval?] → Step 2 → ... → COMPLETE
              ↓                    ↓
         Changes Requested    Changes Requested
              ↓                    ↓
            Step 1               Step 2
```

### Persistence

**Storage:** SQLite database at `./data/agentparty.db`

**Tables:**
- `workflows`: Current workflow state per user
- `workflow_history`: Audit trail of all step transitions

**Survival:** Workflow state persists across Docker restarts via volume mount `./data:/app/data`

---

## Agent System

### Agent Configuration

Each agent has:
- **Model Config**: LLM provider, model, temperature, token limits
- **Prompts**: System prompt, principles, patterns, guidelines
- **Expertise**: Specialized knowledge areas
- **Role**: Position in the SDLC workflow

### Local LLM

**Provider:** Ollama (local inference)
**Model:** qwen2.5-coder:7b (4.7GB)
**Embeddings:** nomic-embed-text (274MB)
**Cost:** $0 (completely free)

**Connection:**
- AgentParty runs in Docker
- Connects to Ollama on host via `http://host.docker.internal:11434`
- No API keys required

---

## Session Management

**Sessions track:**
- User identity
- Active job and workflow
- Budget usage (tokens, costs)
- Context and state

**Creation:** Call MCP tools to auto-create sessions
**Storage:** Redis (in-memory with persistence)
**Lifetime:** Configurable TTL

---

## Vector Search

**Purpose:** Semantic search across codebase

**Components:**
- Qdrant vector database
- Ollama embeddings (nomic-embed-text)
- Document chunking and indexing

**Usage:** Call `query_context` tool with natural language queries

**Status Check:** Returns helpful message if no index exists

---

## Getting Started

### 1. Start a Job
```
mcp1_start_job(session_id="...", job_id="Calculator")
```

### 2. Check Current Task
```
mcp1_get_current_task(session_id="...")
```

### 3. Do Your Work
- Read job context
- Consult agent guidance if needed
- Create deliverables

### 4. Submit Work
```
mcp1_submit_work(
  session_id="...",
  work_description="Completed requirements analysis",
  artifacts=["requirements.md"]
)
```

### 5. Move Through Workflow
- Get approvals as needed
- Progress through all steps
- Complete job

---

## Best Practices

1. **Always check current task** before doing work
2. **Read job context** thoroughly
3. **Consult specialist agents** when unsure
4. **Submit incremental work** for feedback
5. **Handle approval feedback** gracefully
6. **Check workflow status** to track progress

---

## Error Handling

**Common Errors:**
- "No active workflow" - Start a job first
- "No index exists" - Vector DB not populated yet
- "Invalid session" - Session expired or invalid

**Recovery:**
- Workflows persist across restarts
- Use workflow status to check state
- Resume from current step

---

## Architecture Summary

```
IDE (Windsurf) 
    ↓ MCP HTTP/SSE
AgentParty MCP Server (Docker)
    ↓ Local HTTP
Ollama (Host Machine)
    ↓ Inference
qwen2.5-coder:7b Model
```

**Data Flow:**
1. User calls MCP tool
2. Server validates session
3. Executes workflow logic
4. Calls Ollama for AI responses
5. Updates SQLite database
6. Returns result

---

## Technology Details

**FastAPI:** Python web framework for MCP endpoints
**Pydantic:** Data validation and serialization
**SQLite:** Workflow state persistence
**Redis:** Session and cache storage
**Qdrant:** Vector database for embeddings
**Ollama:** Local LLM inference engine
**Docker Compose:** Container orchestration

---

## Monitoring

**Logs:** Docker logs show all operations
**Database:** Query SQLite directly for workflow state
**Health:** HTTP endpoint at `/health`

---

## Extending the System

**Add New Agent:**
1. Create `agents/<agent-id>/index.yaml`
2. Add prompt markdown files
3. Restart server

**Add New Workflow:**
1. Create `workflows/<workflow-id>/workflow.yaml`
2. Define steps, agents, transitions
3. Restart server

**Add New Job:**
1. Create `jobs/<job-id>/index.yaml`
2. Add context files
3. Job appears in available jobs list

---

## Security

- No external API calls (all local)
- SQLite database persisted locally
- Session authentication via Redis
- Policy Gate agent validates security

---

## Cost & Performance

**Cost:** $0/month (local LLMs)
**Performance:** Depends on hardware
**Scalability:** Single-node, multi-user capable
**Persistence:** Full workflow state survival

---

This documentation describes AgentParty version 0.1.0 running locally with Ollama integration.
"""
                return doc
            
            elif uri.startswith("agent://"):
                agent_id = uri.replace("agent://", "")
                agent_registry = get_agent_registry()
                agent = agent_registry.get(agent_id)
                
                # Return agent configuration and prompts
                agent_data = {
                    "id": agent_id,
                    "name": agent.name,
                    "description": agent.description,
                    "model": {
                        "provider": agent.llm_config.provider,
                        "model": agent.llm_config.model,
                        "temperature": agent.llm_config.temperature,
                        "max_tokens": agent.llm_config.max_tokens,
                    },
                    "prompt_files": agent.prompt_files,
                    "prompts": {},
                }
                
                # Load prompt content
                agent_dir = Path(f"agents/{agent_id}")
                for prompt_file in agent.prompt_files:
                    prompt_path = agent_dir / prompt_file
                    if prompt_path.exists():
                        agent_data["prompts"][prompt_file] = prompt_path.read_text()
                
                return json.dumps(agent_data, indent=2)
            
            elif uri.startswith("workflow://"):
                workflow_id = uri.replace("workflow://", "")
                workflow_def = load_workflow_definition(workflow_id)
                
                # Return workflow as YAML
                workflow_data = {
                    "id": workflow_def.id,
                    "name": workflow_def.name,
                    "description": workflow_def.description,
                    "version": workflow_def.version,
                    "steps": [
                        {
                            "id": step.id,
                            "name": step.name,
                            "description": step.description,
                            "agent": step.agent,
                            "inputs": step.inputs,
                            "outputs": step.outputs,
                            "requires_approval": step.requires_approval,
                            "approval_agent": step.approval_agent,
                            "next_step": step.next_step,
                        }
                        for step in workflow_def.steps
                    ],
                    "metadata": workflow_def.metadata,
                }
                return yaml.dump(workflow_data, default_flow_style=False)
            
            elif uri.startswith("job://"):
                job_id = uri.replace("job://", "")
                from src.jobs.loader import load_job_definition
                job_def = load_job_definition(job_id)
                
                # Return job configuration
                job_data = {
                    "id": job_id,
                    "title": job_def.title,
                    "description": job_def.description,
                    "workflow_id": job_def.workflow_id,
                    "assigned_to": job_def.assigned_to,
                    "priority": job_def.priority,
                    "context_files": job_def.context_files,
                    "deadline": job_def.deadline.isoformat() if job_def.deadline else None,
                }
                
                # Include context file contents
                job_dir = Path(f"jobs/{job_id}")
                job_data["context"] = {}
                for context_file in job_def.context_files:
                    file_path = job_dir / context_file
                    if file_path.exists():
                        job_data["context"][context_file] = file_path.read_text()
                
                return yaml.dump(job_data, default_flow_style=False)
            
            else:
                return json.dumps({"error": f"Unknown resource URI scheme: {uri}"})
        
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}", exc_info=True)
            return json.dumps({"error": str(e)})

    logger.info("MCP server configured with tools and resources")
    return server
