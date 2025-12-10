"""Shared comprehensive documentation for AgentParty MCP server."""


def get_full_documentation() -> str:
    """Get complete technical documentation.
    
    Returns:
        Complete documentation as markdown string
    """
    return """# AgentParty MCP Server - Complete Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [MCP Tools Reference](#mcp-tools)
3. [MCP Resources](#mcp-resources)
4. [Workflow Architecture](#workflow-architecture)
5. [Agent System](#agent-system)
6. [Getting Started](#getting-started)
7. [Best Practices](#best-practices)
8. [Error Handling](#error-handling)
9. [Architecture Details](#architecture-summary)
10. [Extending the System](#extending-the-system)

---

## Overview

AgentParty is a Model Context Protocol (MCP) server that orchestrates multi-agent software development workflows. It provides a complete SDLC automation platform using local LLMs through Ollama, with persistent workflow state stored in SQLite.

**Key Features:**
- 9 specialized AI agents for different SDLC roles
- 3 workflow definitions (C#, Node.js, Angular)
- Persistent workflow state (survives container restarts)
- Local LLM integration (zero API costs)
- Vector-based codebase search
- Budget and session management
- **Hot-swappable agents** (auto-reload on file changes)

**Technology Stack:**
- FastAPI for HTTP/SSE MCP transport
- SQLite for workflow persistence
- Qdrant for vector embeddings
- Redis for session storage
- Ollama for local LLM inference (qwen2.5-coder:7b)
- Docker Compose for orchestration
- Watchdog for agent hot-reloading

**Connection:**
- MCP Server URL: `http://localhost:8000/mcp`
- Health Check: `http://localhost:8000/health`
- Ollama: `http://host.docker.internal:11434`

---

## MCP Tools

Tools are executable functions that perform actions in the AgentParty system.

### 1. create_session
**Purpose:** Create a new user session for workflow tracking.

**Parameters:**
- `user_id` (string, required): User identifier

**Returns:**
```json
{
  "session_id": "sess_abc123...",
  "user_id": "user123",
  "expires_at": "2024-01-01T12:00:00Z"
}
```

**Usage:**
```python
mcp1_create_session(user_id="developer1")
```

---

### 2. get_available_jobs
**Purpose:** List all jobs available for the current agent.

**Parameters:**
- `session_id` (string, required): Session identifier
- `filter` (string, optional): Filter like 'high-priority'

**Returns:**
```json
[
  {
    "id": "Calculator",
    "title": "C# Console Symbolic Calculator",
    "description": "Build a calculator with symbolic math",
    "priority": "high",
    "workflow_id": "csharp",
    "assigned_to": "programmer"
  }
]
```

**Usage:** Call this to see what work is available before starting a job.

**Example:**
```python
jobs = mcp1_get_available_jobs(session_id="sess_abc123")
print(f"Found {len(jobs)} available jobs")
```

---

### 3. start_job
**Purpose:** Initialize a job and start its workflow.

**Parameters:**
- `session_id` (string, required): Session identifier
- `job_id` (string, required): ID of job to start

**Returns:**
```json
{
  "status": "started",
  "job_id": "Calculator",
  "job_title": "C# Console Symbolic Calculator",
  "workflow_id": "csharp",
  "current_step": "requirements",
  "job_context": "# Complete job context with all requirements..."
}
```

**What Happens:**
1. Loads job definition from `jobs/{job_id}/index.yaml`
2. Reads all context files (requirements, specs, etc.)
3. Creates workflow state in SQLite database
4. Sets first step to "in_progress"
5. Updates session context
6. Returns job context for the current step

**Persistence:** Workflow state is saved to SQLite at `./data/agentparty.db` and survives Docker restarts.

**Example:**
```python
result = mcp1_start_job(
    session_id="sess_abc123",
    job_id="Calculator"
)
print(f"Started workflow: {result['workflow_id']}")
print(f"Current step: {result['current_step']}")
```

---

### 4. get_current_task
**Purpose:** Get the current workflow task and its requirements.

**Parameters:**
- `session_id` (string, required): Session identifier

**Returns:**
```json
{
  "step_id": "requirements",
  "step_name": "Requirements Analysis",
  "description": "Gather and document requirements",
  "agent": "requirements-engineer",
  "inputs": [],
  "outputs": ["requirements.md"],
  "status": "in_progress",
  "job_context": "# Full job context..."
}
```

**Usage:** Call this to understand what you need to do next in the workflow.

**Example:**
```python
task = mcp1_get_current_task(session_id="sess_abc123")
print(f"Current task: {task['step_name']}")
print(f"Agent: {task['agent']}")
print(f"Expected outputs: {task['outputs']}")
```

---

### 5. submit_work
**Purpose:** Submit completed work for the current workflow step.

**Parameters:**
- `session_id` (string, required): Session identifier
- `work_description` (string, required): What you completed
- `artifacts` (array, required): List of file paths or deliverables

**Returns:**
```json
{
  "status": "submitted",
  "message": "Work submitted for approval",
  "next_step": "specification",
  "requires_approval": true
}
```

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

**Example:**
```python
result = mcp1_submit_work(
    session_id="sess_abc123",
    work_description="Completed requirements analysis",
    artifacts=["requirements.md", "use-cases.md"]
)
print(result['message'])
```

---

### 6. request_review
**Purpose:** Request review from workflow-defined approval agent.

**Parameters:**
- `session_id` (string, required): Session identifier

**Returns:**
```json
{
  "status": "approved",
  "reviewer": "product-manager",
  "feedback": "Requirements look complete and well-structured",
  "approved": true
}
```

**Approval Flow:**
Each workflow step can have approval requirements:
- Product Manager approves requirements
- Engineering Manager approves architecture
- Policy Gate approves security compliance

**Example:**
```python
review = mcp1_request_review(session_id="sess_abc123")
if review['approved']:
    print(f"Approved by {review['reviewer']}")
else:
    print(f"Changes requested: {review['feedback']}")
```

---

### 7. get_agent_guidance
**Purpose:** Ask another agent for consultation or guidance.

**Parameters:**
- `session_id` (string, required): Session identifier
- `agent_id` (string, required): Agent to consult (e.g., "architect")
- `question` (string, required): Your question

**Returns:**
```json
{
  "agent": "architect",
  "guidance": "For this calculator, I recommend..."
}
```

**Usage:** When you need expert advice during your work, consult a specialist agent.

**Example:**
```python
guidance = mcp1_get_agent_guidance(
    session_id="sess_abc123",
    agent_id="architect",
    question="What design pattern should I use for the calculator?"
)
print(guidance['guidance'])
```

---

### 8. query_context
**Purpose:** Search the codebase vector database for relevant context.

**Parameters:**
- `session_id` (string, required): Session identifier
- `query` (string, required): Natural language search query
- `limit` (integer, optional): Max results (default 5)

**Returns:**
```json
{
  "results": [
    {
      "id": "chunk_123",
      "score": 0.89,
      "content": "public class Calculator...",
      "metadata": {
        "file_path": "src/Calculator.cs",
        "language": "csharp"
      }
    }
  ],
  "count": 5,
  "message": "Found 5 relevant code chunks"
}
```

**Notes:**
- Returns helpful message if no index exists yet
- Uses local Ollama embeddings (nomic-embed-text)
- Searches across indexed codebase files
- Semantic search with relevance scoring

**Example:**
```python
results = mcp1_query_context(
    session_id="sess_abc123",
    query="calculator implementation examples",
    limit=5
)
for result in results['results']:
    print(f"Score: {result['score']} - {result['metadata']['file_path']}")
```

---

### 9. get_workflow_status
**Purpose:** Get current workflow status and progress.

**Parameters:**
- `session_id` (string, required): Session identifier

**Returns:**
```json
{
  "workflow_id": "csharp",
  "job_id": "Calculator",
  "current_step": "implementation",
  "is_completed": false,
  "started_at": "2024-01-01T10:00:00Z",
  "completed_at": null,
  "step_statuses": {
    "requirements": "completed",
    "specification": "completed",
    "implementation": "in_progress"
  }
}
```

**Step Statuses:**
- `pending`: Not started
- `in_progress`: Currently working
- `awaiting_approval`: Submitted, waiting for review
- `approved`: Approved, ready to proceed
- `changes_requested`: Needs rework
- `completed`: Finished
- `skipped`: Bypassed

**Example:**
```python
status = mcp1_get_workflow_status(session_id="sess_abc123")
print(f"Progress: {status['current_step']}")
for step, state in status['step_statuses'].items():
    print(f"  {step}: {state}")
```

---

### 10. get_budget_status
**Purpose:** Get session budget and LLM usage information.

**Parameters:**
- `session_id` (string, required): Session identifier

**Returns:**
```json
{
  "tokens_used": 150000,
  "cost_usd": 0.0,
  "session_start": "2024-01-01T10:00:00Z",
  "budget_remaining": "unlimited"
}
```

**Note:** With Ollama, all costs are $0. This tracks usage for monitoring.

---

## MCP Resources

Resources are read-only content that can be accessed via URI schemes.

### Resource Types

#### 1. System Documentation: `agentparty://documentation`
**Format:** Markdown
**Contains:** This complete documentation
**Usage:** Query to understand the entire system

#### 2. Agent Resources: `agent://<agent-id>`
**Format:** JSON
**Contains:**
- Agent configuration (name, description, model settings)
- LLM parameters (temperature, max tokens)
- Complete prompt content from all prompt files
- Expertise areas and focus areas

**Example Response:**
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
    "system-prompt.md": "You are a Software Architect...",
    "principles.md": "SOLID, Clean Architecture...",
    "patterns.md": "Repository, Factory, Strategy...",
    "anti-patterns.md": "God objects, circular deps..."
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

**Hot-Reload:** Agents automatically reload when files change (1 second polling)

#### 3. Workflow Resources: `workflow://<workflow-id>`
**Format:** YAML
**Contains:**
- Complete workflow definition
- All steps with names, descriptions, agents
- Input/output requirements per step
- Approval requirements
- Transition conditions

**Example Response:**
```yaml
id: csharp
name: C# Development Workflow
version: "1.0"
steps:
  - id: requirements
    name: Requirements Analysis
    agent: requirements-engineer
    requires_approval: true
    approval_agent: product-manager
    next_step: specification
```

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

#### 4. Job Resources: `job://<job-id>`
**Format:** YAML
**Contains:**
- Job metadata (title, description, priority)
- Associated workflow
- Complete context file contents
- Deadline information

**Example Response:**
```yaml
id: Calculator
title: C# Console Symbolic Calculator
workflow_id: csharp
priority: high
context:
  overview.md: |
    # Project Overview...
  requirements.md: |
    # Requirements...
  technical-specs.md: |
    # Technical Specifications...
```

---

## Workflow Architecture

### State Machine Model

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

**Schema:**
```sql
CREATE TABLE workflows (
    user_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    current_step TEXT,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    step_statuses TEXT NOT NULL  -- JSON
);

CREATE TABLE workflow_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    workflow_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    status TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    data TEXT  -- JSON
);
```

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

### Hot-Swappable Agents

**How it works:**
1. Watchdog monitors `agents/` directory
2. Detects changes to `.md` and `.yaml` files
3. Automatically reloads affected agents
4. Changes available immediately (1 second polling)

**To add a new agent:**
1. Create `agents/my-agent/` folder
2. Add `index.yaml` with configuration
3. Add prompt files (`.md`)
4. Agent appears automatically in resources
5. Query via `agent://my-agent`

**No restart required!**

---

## Session Management

**Sessions track:**
- User identity
- Active job and workflow
- Budget usage (tokens, costs)
- Context and state

**Creation:** Call `create_session` tool
**Storage:** Redis (in-memory with persistence)
**Lifetime:** Configurable TTL (default 24 hours)

---

## Vector Search

**Purpose:** Semantic search across codebase

**Components:**
- Qdrant vector database
- Ollama embeddings (nomic-embed-text)
- Document chunking and indexing

**Usage:** Call `query_context` tool with natural language queries

**Status Check:** Returns helpful message if no index exists

**Indexing:**
```bash
# Run indexing script
docker exec agentparty-dev python scripts/index_codebase.py <path>
```

---

## Getting Started

### 1. Create a Session
```python
session = mcp1_create_session(user_id="developer1")
session_id = session['session_id']
```

### 2. Check Available Jobs
```python
jobs = mcp1_get_available_jobs(session_id=session_id)
for job in jobs:
    print(f"{job['id']}: {job['title']} (priority: {job['priority']})")
```

### 3. Start a Job
```python
result = mcp1_start_job(
    session_id=session_id,
    job_id="Calculator"
)
print(f"Started: {result['job_title']}")
print(f"First step: {result['current_step']}")
```

### 4. Get Current Task
```python
task = mcp1_get_current_task(session_id=session_id)
print(f"Task: {task['step_name']}")
print(f"Agent: {task['agent']}")
print(f"Outputs: {task['outputs']}")
```

### 5. Do Your Work
- Read job context from task response
- Consult agent guidance if needed (`get_agent_guidance`)
- Query codebase context (`query_context`)
- Create deliverables

### 6. Submit Work
```python
result = mcp1_submit_work(
    session_id=session_id,
    work_description="Completed requirements analysis",
    artifacts=["requirements.md"]
)
print(result['message'])
```

### 7. Handle Approvals
```python
if result['requires_approval']:
    review = mcp1_request_review(session_id=session_id)
    if review['approved']:
        print("Approved! Moving to next step")
    else:
        print(f"Changes requested: {review['feedback']}")
```

### 8. Check Progress
```python
status = mcp1_get_workflow_status(session_id=session_id)
print(f"Current step: {status['current_step']}")
print(f"Completed: {status['is_completed']}")
```

---

## Best Practices

### 1. Always Check Current Task
Before doing work, call `get_current_task` to understand requirements.

### 2. Read Job Context Thoroughly
The job context contains all requirements, specs, and constraints.

### 3. Consult Specialist Agents
When unsure, use `get_agent_guidance` to ask expert agents.

### 4. Submit Incremental Work
Don't wait until everything is done - submit progress for feedback.

### 5. Handle Approval Feedback Gracefully
If changes are requested, review feedback carefully and iterate.

### 6. Check Workflow Status Regularly
Use `get_workflow_status` to track progress and understand state.

### 7. Use Vector Search
Query `query_context` to find relevant code examples and patterns.

### 8. Monitor Budget
Call `get_budget_status` to track token usage (even though it's free with Ollama).

---

## Error Handling

### Common Errors

#### "No active workflow"
**Cause:** You haven't started a job yet
**Solution:** Call `start_job` first

#### "No index exists"
**Cause:** Vector database hasn't been populated
**Solution:** Run the indexing script or accept the empty response

#### "Invalid session"
**Cause:** Session expired or never created
**Solution:** Call `create_session` to get a new session

#### "Agent not found"
**Cause:** Agent ID doesn't exist
**Solution:** Check available agents via resources list

#### "Job not found"
**Cause:** Job ID doesn't exist
**Solution:** Call `get_available_jobs` to see valid job IDs

### Recovery Strategies

**Workflow State Lost:**
- Workflows persist in SQLite
- Restart Docker - state survives
- Check `get_workflow_status` to verify

**Agent Guidance Timeout:**
- Ollama may be slow on first request (model loading)
- Retry after 30 seconds
- Check Ollama logs: `docker logs agentparty-dev`

**Resource Not Found:**
- List resources first to see what's available
- Check URI format: `agent://`, `workflow://`, `job://`

---

## Architecture Summary

### System Diagram

```
IDE (Windsurf) 
    ↓ MCP HTTP/SSE
AgentParty MCP Server (Docker)
    ↓ Local HTTP
Ollama (Host Machine)
    ↓ Inference
qwen2.5-coder:7b Model
```

### Data Flow

1. User calls MCP tool (via Windsurf)
2. Server validates session (Redis)
3. Executes workflow logic
4. Calls Ollama for AI responses
5. Updates SQLite database
6. Returns result to user

### Storage Layers

**SQLite (Persistent):**
- Workflow states
- Workflow history
- Job assignments

**Redis (Cache):**
- Session data
- Budget tracking
- Temporary state

**Qdrant (Vector DB):**
- Code embeddings
- Semantic search index

**File System:**
- Agent definitions
- Workflow definitions
- Job definitions

---

## Technology Details

### Core Framework
- **FastAPI**: Python web framework for MCP endpoints
- **Pydantic**: Data validation and serialization
- **SQLite**: Workflow state persistence (aiosqlite)
- **Redis**: Session and cache storage
- **Qdrant**: Vector database for embeddings
- **Ollama**: Local LLM inference engine
- **Docker Compose**: Container orchestration
- **Watchdog**: File system monitoring for hot-reload

### MCP Protocol
- **Transport**: HTTP/SSE (Server-Sent Events)
- **Format**: JSON-RPC 2.0
- **Capabilities**: Tools + Resources
- **Version**: 2024-11-05

### Python Dependencies
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
mcp>=0.9.0
redis>=5.0.0
qdrant-client>=1.7.0
ollama (via httpx)
aiosqlite>=0.19.0
watchdog>=3.0.0
```

---

## Monitoring

### Logs
**View logs:**
```bash
docker logs agentparty-dev --tail 100 -f
```

**Log levels:** DEBUG, INFO, WARNING, ERROR

### Database
**Query workflow state:**
```bash
docker exec agentparty-dev sqlite3 /app/data/agentparty.db "SELECT * FROM workflows;"
```

### Health Check
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "agentparty-mcp",
  "version": "0.1.0"
}
```

---

## Extending the System

### Add New Agent

1. **Create directory:**
```bash
mkdir -p agents/my-agent
```

2. **Create `index.yaml`:**
```yaml
name: My Agent
description: Agent description
model:
  provider: ollama
  model: qwen2.5-coder:7b
  temperature: 0.7
  max_tokens: 4000
prompt_files:
  - system-prompt.md
  - guidelines.md
```

3. **Create prompt files:**
```bash
echo "# My Agent System Prompt" > agents/my-agent/system-prompt.md
```

4. **Agent appears automatically** (hot-reload within 1 second)

5. **Query via resource:**
```python
# Resource URI: agent://my-agent
```

### Add New Workflow

1. **Create directory:**
```bash
mkdir -p workflows/my-workflow
```

2. **Create `workflow.yaml`:**
```yaml
id: my-workflow
name: My Custom Workflow
version: "1.0"
description: Custom workflow description
steps:
  - id: step1
    name: First Step
    agent: architect
    requires_approval: false
    next_step: step2
  - id: step2
    name: Second Step
    agent: qa-engineer
    requires_approval: true
    approval_agent: engineering-manager
```

3. **Create `description.md`:**
```markdown
# My Workflow Description
Detailed explanation...
```

4. **Restart server** to load workflow

5. **Query via resource:**
```python
# Resource URI: workflow://my-workflow
```

### Add New Job

1. **Create directory:**
```bash
mkdir -p jobs/MyJob
```

2. **Create `index.yaml`:**
```yaml
id: MyJob
title: My Job Title
description: Job description
workflow_id: csharp
assigned_to: programmer
priority: high
deadline: "2024-12-31T23:59:59Z"
context_files:
  - overview.md
  - requirements.md
```

3. **Create context files:**
```bash
echo "# Overview" > jobs/MyJob/overview.md
echo "# Requirements" > jobs/MyJob/requirements.md
```

4. **Job appears in available jobs** immediately

5. **Start via tool:**
```python
mcp1_start_job(session_id="...", job_id="MyJob")
```

---

## Security

**Isolation:**
- No external API calls (all local)
- SQLite database persisted locally
- No network exposure except MCP endpoint

**Authentication:**
- Session-based auth via Redis
- Session validation on every tool call

**Validation:**
- Policy Gate agent validates security
- Code review by coding-standards-auditor
- All inputs validated via Pydantic

**Best Practices:**
- Never commit API keys (not needed with Ollama)
- Keep SQLite database in secure location
- Use Docker network isolation

---

## Cost & Performance

**Cost:**
- **$0/month** (local LLMs via Ollama)
- No API fees
- No cloud charges

**Performance:**
- Depends on local hardware
- First LLM request: 10-30 seconds (model loading)
- Subsequent requests: 1-5 seconds
- Vector search: <500ms
- Workflow operations: <100ms

**Scalability:**
- Single-node deployment
- Multi-user capable
- Concurrent workflows supported
- SQLite handles 100+ concurrent reads

**Resource Usage:**
- RAM: 8-16GB recommended (for Ollama)
- Disk: 10GB+ (models + data)
- CPU: 4+ cores recommended

---

## Troubleshooting

### Ollama Not Responding
```bash
# Check Ollama status on host
ollama list
ollama ps

# Restart Ollama
ollama serve
```

### Agent Not Reloading
```bash
# Check watcher logs
docker logs agentparty-dev | grep watcher

# Manually reload all agents
docker restart agentparty-dev
```

### Workflow State Corrupted
```bash
# Check database
docker exec agentparty-dev sqlite3 /app/data/agentparty.db ".dump workflows"

# Reset workflow (if needed)
docker exec agentparty-dev sqlite3 /app/data/agentparty.db "DELETE FROM workflows WHERE user_id='<user>';"
```

### Redis Connection Failed
```bash
# Check Redis status
docker ps | grep redis

# Restart Redis
docker-compose restart redis
```

---

## FAQ

**Q: Can I use cloud LLMs instead of Ollama?**
A: Yes! Change the agent model config from `ollama` to `openai` or `anthropic` and set API keys.

**Q: How do I backup workflow state?**
A: Copy `./data/agentparty.db` file. It contains all workflow history.

**Q: Can I run multiple workflows simultaneously?**
A: Yes, each user_id can have one active workflow. Use different user_ids for parallel work.

**Q: How do I index my codebase?**
A: Run `docker exec agentparty-dev python scripts/index_codebase.py /path/to/code`

**Q: Can agents call other agents?**
A: Yes, use `get_agent_guidance` tool to consult specialist agents.

**Q: Do I need to restart after adding an agent?**
A: No! Agents hot-reload automatically within 1 second.

**Q: How do I see agent prompts?**
A: Query the agent resource: `agent://<agent-id>` - includes full prompt content.

**Q: Can I customize workflows?**
A: Yes! Edit YAML files in `workflows/` directory and restart server.

---

## Support & Contributing

**Issues:**
- GitHub: https://github.com/Cstolworthy/AgentParty

**Documentation Updates:**
- This doc is in `src/mcp/documentation.py`
- Edit and restart to apply changes

**Community:**
- Built with MCP Protocol standard
- Compatible with Windsurf, Claude Desktop, and other MCP clients

---

**Version:** 0.1.0
**Last Updated:** December 2024
**License:** MIT (modify as needed)

---

This documentation describes a complete, production-ready multi-agent SDLC automation platform with zero API costs and full persistence.
"""
