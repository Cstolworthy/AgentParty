# AgentParty MCP Platform - Complete Architecture

## Overview

AgentParty is a Model Context Protocol (MCP) server that enables multi-agent LLM workflows for IDE-based development. The IDE (Windsurf/VS Code) connects as ONE agent (e.g., Programmer), while the MCP server orchestrates OTHER agents (Manager, QA, Product Manager) to guide, review, and approve work.

**Key Feature: Multi-User Isolation** - Each connected user has completely isolated context, workflow state, and agent interactions.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER 1 - VS Code/Windsurf                │
│                    (Programmer Agent via Claude)            │
└────────────────┬────────────────────────────────────────────┘
                 │ MCP Protocol (User Session Token)
                 │
┌─────────────────────────────────────────────────────────────┐
│                    USER 2 - VS Code/Windsurf                │
│                    (Programmer Agent via Claude)            │
└────────────────┬────────────────────────────────────────────┘
                 │ MCP Protocol (User Session Token)
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│               AgentParty MCP Server (FastAPI)               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Session Manager (Multi-User Isolation)             │   │
│  │  - User authentication & session tokens             │   │
│  │  - Per-user workflow state                          │   │
│  │  - Per-user job context                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  MCP Protocol Handler                               │   │
│  │  - Tools: get_jobs, start_job, submit_work, etc.    │   │
│  │  - Resources: job specs, agent prompts              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Workflow Engine (Per-User State Machine)           │   │
│  │  - Load workflow definitions                        │   │
│  │  - Track current step per user                      │   │
│  │  - Manage transitions & approvals                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Agent Manager (Multi-LLM Orchestration)            │   │
│  │  - Spawn agent instances per user request           │   │
│  │  - Load agent prompts (10-12 files)                 │   │
│  │  - Route agent-to-agent communication               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  LLM Adapter Layer                                  │   │
│  │  - OpenAI adapter                                   │   │
│  │  - Anthropic adapter                                │   │
│  │  - Azure OpenAI adapter                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Job & Prompt Loader                                │   │
│  │  - Load jobs (index.yaml + 10-12 .md files)         │   │
│  │  - Load workflows (YAML definitions)                │   │
│  │  - Load agent definitions (multi-file prompts)      │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Qdrant Vector Database                         │
│  - Per-user collections (user_id namespacing)               │
│  - Codebase embeddings with user_id filter                  │
│  - Semantic search with tenant isolation                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Checklist

### Phase 1: Foundation & Infrastructure
- [ ] **Project Structure**
  - [ ] Setup pyproject.toml with all dependencies
  - [ ] Create src/ directory structure
  - [ ] Create agents/, workflows/, jobs/ directories
  - [ ] Add .env.example for configuration
  - [ ] Create .dockerignore and .gitignore

- [ ] **Docker Setup**
  - [ ] Multi-stage Dockerfile (dev/prod targets)
  - [ ] docker-compose.yaml with MCP + Qdrant services
  - [ ] Development target with hot reload
  - [ ] Production target with health checks
  - [ ] Volume mounts for agents/workflows/jobs
  - [ ] Environment variable configuration

- [ ] **Configuration System**
  - [ ] Settings class using pydantic-settings
  - [ ] Environment variable loading
  - [ ] LLM provider configs (API keys, models)
  - [ ] Qdrant connection settings
  - [ ] Multi-user session configuration

### Phase 2: Multi-User Session Management
- [ ] **Authentication & Sessions**
  - [ ] User session token generation
  - [ ] Session storage (in-memory + optional Redis)
  - [ ] Session middleware for MCP requests
  - [ ] Per-user context isolation
  - [ ] Session cleanup/expiry

- [ ] **User State Management**
  - [ ] Per-user workflow state storage
  - [ ] Per-user job context tracking
  - [ ] User-scoped agent conversation history
  - [ ] Concurrent user request handling

### Phase 3: Vector Database Integration
- [ ] **Qdrant Setup**
  - [ ] Qdrant client initialization
  - [ ] Collection management (per-user or filtered)
  - [ ] User ID filtering strategy
  - [ ] Connection pooling for multi-user
  - [ ] Health check integration

- [ ] **Embeddings & Search**
  - [ ] Text embedding generation (OpenAI/local)
  - [ ] Document ingestion with user_id metadata
  - [ ] Semantic search with user isolation
  - [ ] Codebase indexing utilities
  - [ ] Search result ranking

### Phase 4: Agent System
- [ ] **Agent Definition Loading**
  - [ ] Agent directory scanner
  - [ ] index.yaml parser (model config)
  - [ ] Multi-file prompt loader (10-12 .md files)
  - [ ] Prompt template rendering (Jinja2)
  - [ ] Agent validation

- [ ] **Agent Runtime**
  - [ ] Agent class with LLM interface
  - [ ] Per-request agent instantiation
  - [ ] System prompt compilation from multiple files
  - [ ] Context injection (job, workflow, codebase)
  - [ ] Response streaming support

### Phase 5: LLM Adapter Layer
- [ ] **Provider Adapters**
  - [ ] Base LLM adapter interface
  - [ ] OpenAI adapter (GPT-4, GPT-3.5)
  - [ ] Anthropic adapter (Claude)
  - [ ] Azure OpenAI adapter
  - [ ] Error handling & retries (tenacity)

- [ ] **LLM Features**
  - [ ] Chat completion API
  - [ ] Streaming responses
  - [ ] Token counting (tiktoken)
  - [ ] Rate limiting per user
  - [ ] Cost tracking per user

### Phase 6: Job System
- [ ] **Job Definition Loading**
  - [ ] Job directory scanner
  - [ ] index.yaml parser (workflow reference, metadata)
  - [ ] Multi-file content loader (10-12 .md files)
  - [ ] Job validation
  - [ ] Job listing API

- [ ] **Job Execution**
  - [ ] Job initialization per user
  - [ ] Job context assembly
  - [ ] Job-workflow binding
  - [ ] Job completion tracking
  - [ ] Job state persistence

### Phase 7: Workflow Engine
- [ ] **Workflow Definition**
  - [ ] Workflow YAML schema definition
  - [ ] Workflow parser & validator
  - [ ] Step definitions (agents, approvals, transitions)
  - [ ] Conditional logic support
  - [ ] Workflow directory loading

- [ ] **Workflow Execution**
  - [ ] Per-user workflow state machine
  - [ ] Current step tracking
  - [ ] Step transition logic
  - [ ] Approval gates
  - [ ] Agent routing based on workflow step
  - [ ] Workflow completion detection

- [ ] **Agent Orchestration**
  - [ ] Agent-to-agent communication
  - [ ] Approval request handling
  - [ ] Internal agent consultation
  - [ ] Response aggregation
  - [ ] Timeout handling

### Phase 8: MCP Server Implementation
- [ ] **MCP Protocol**
  - [ ] MCP SDK integration
  - [ ] Server initialization
  - [ ] Transport layer (SSE/stdio)
  - [ ] User authentication in MCP context
  - [ ] Error handling

- [ ] **MCP Tools** (Exposed to IDE)
  - [ ] `get_available_jobs` - List jobs
  - [ ] `start_job` - Initialize job + workflow
  - [ ] `get_current_task` - Get next step
  - [ ] `submit_work` - Submit completed work
  - [ ] `request_review` - Trigger agent approval
  - [ ] `query_context` - Search vector DB
  - [ ] `get_agent_guidance` - Ask agent question
  - [ ] `get_workflow_status` - Check workflow state

- [ ] **MCP Resources** (Readable by IDE)
  - [ ] Job specifications
  - [ ] Agent definitions
  - [ ] Workflow descriptions
  - [ ] Codebase context

### Phase 9: API Layer
- [ ] **FastAPI Application**
  - [ ] Main application setup
  - [ ] CORS configuration
  - [ ] Health check endpoint
  - [ ] Metrics endpoint
  - [ ] API versioning

- [ ] **REST Endpoints** (Alternative to MCP)
  - [ ] User authentication endpoints
  - [ ] Job management endpoints
  - [ ] Workflow control endpoints
  - [ ] Agent interaction endpoints
  - [ ] Vector search endpoints

### Phase 10: Testing & Documentation
- [ ] **Testing**
  - [ ] Unit tests for core components
  - [ ] Integration tests for workflows
  - [ ] Multi-user concurrency tests
  - [ ] LLM adapter mocks
  - [ ] End-to-end workflow tests

- [ ] **Documentation**
  - [ ] README.md with quick start
  - [ ] API documentation (OpenAPI)
  - [ ] Agent creation guide
  - [ ] Workflow creation guide
  - [ ] Job creation guide
  - [ ] Deployment guide (Azure)
  - [ ] Example agents/workflows/jobs

- [ ] **Examples**
  - [ ] Example: Software Development Lifecycle
  - [ ] Example: Virtual Store Management
  - [ ] Example: Content Review Workflow
  - [ ] Example: Code Review Process

---

## Directory Structure

```
AgentParty/
├── agents/                         # Agent definitions
│   ├── programmer/
│   │   ├── index.yaml             # Model config, metadata
│   │   ├── system-prompt.md       # Core behavior
│   │   ├── coding-standards.md    # Context file 1
│   │   ├── knowledge-base.md      # Context file 2
│   │   └── ...                    # Up to 10-12 files
│   ├── manager/
│   │   ├── index.yaml
│   │   ├── system-prompt.md
│   │   └── ...
│   ├── qa-engineer/
│   └── product-manager/
│
├── workflows/                      # Workflow definitions
│   ├── sdlc/
│   │   ├── workflow.yaml          # State machine definition
│   │   └── description.md
│   ├── code-review/
│   │   ├── workflow.yaml
│   │   └── description.md
│   └── virtual-store/
│       ├── workflow.yaml
│       └── description.md
│
├── jobs/                           # Job definitions
│   ├── build-auth-system/
│   │   ├── index.yaml             # Workflow ref, metadata
│   │   ├── overview.md
│   │   ├── requirements.md
│   │   ├── technical-specs.md
│   │   ├── constraints.md
│   │   └── ...                    # Up to 10-12 files
│   └── fix-login-bug/
│       ├── index.yaml
│       └── ...
│
├── src/
│   ├── main.py                    # FastAPI app entry
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Pydantic settings
│   │
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py              # MCP server implementation
│   │   ├── tools.py               # MCP tool definitions
│   │   └── resources.py           # MCP resource handlers
│   │
│   ├── session/
│   │   ├── __init__.py
│   │   ├── manager.py             # Session management
│   │   ├── auth.py                # Authentication
│   │   └── state.py               # Per-user state
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── loader.py              # Load agent definitions
│   │   ├── agent.py               # Agent runtime class
│   │   └── registry.py            # Agent registry
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py                # Base adapter interface
│   │   ├── openai_adapter.py
│   │   ├── anthropic_adapter.py
│   │   └── azure_adapter.py
│   │
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── loader.py              # Load job definitions
│   │   ├── job.py                 # Job class
│   │   └── manager.py             # Job execution
│   │
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── loader.py              # Load workflow YAML
│   │   ├── engine.py              # State machine engine
│   │   ├── workflow.py            # Workflow class
│   │   └── transitions.py         # Transition logic
│   │
│   ├── vectordb/
│   │   ├── __init__.py
│   │   ├── qdrant_client.py       # Qdrant integration
│   │   ├── embeddings.py          # Embedding generation
│   │   └── search.py              # Semantic search
│   │
│   ├── orchestration/
│   │   ├── __init__.py
│   │   ├── router.py              # Agent routing
│   │   └── communication.py       # Agent-to-agent
│   │
│   └── api/
│       ├── __init__.py
│       ├── routes/
│       │   ├── jobs.py
│       │   ├── workflows.py
│       │   └── agents.py
│       └── dependencies.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/
│   ├── guides/
│   │   ├── creating-agents.md
│   │   ├── creating-workflows.md
│   │   ├── creating-jobs.md
│   │   └── deployment-azure.md
│   └── examples/
│
├── .env.example
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yaml
├── pyproject.toml
├── README.md
└── ARCHITECTURE.md
```

---

## Multi-User Isolation Strategy

### Session Management
```python
# Each MCP connection gets a session token
{
    "session_id": "user-abc-123",
    "user_id": "john@example.com",
    "created_at": "2024-01-01T00:00:00Z",
    "active_job_id": "build-auth-system",
    "workflow_state": {...}
}
```

### Vector DB Isolation
```python
# Option A: Per-user collections
collection_name = f"codebase_{user_id}"

# Option B: Shared collection with user_id filter
qdrant.search(
    collection_name="codebase",
    query_filter={"user_id": user_id},
    query_vector=embedding
)
```

### Workflow State Isolation
```python
# Per-user workflow state
workflow_states = {
    "user-abc-123": {
        "job_id": "build-auth-system",
        "workflow_id": "sdlc",
        "current_step": "code_implementation",
        "step_history": [...]
    }
}
```

### Agent Instance Isolation
```python
# Agents are spawned per request with user context
agent = Agent(
    definition=manager_agent_def,
    user_id=user_id,
    session_context=session.context
)
```

---

## Key Design Decisions

### 1. Multi-File Prompt System
**Rationale:** Complex agents need contextual knowledge organized in separate files.

**Structure:**
```yaml
# agents/manager/index.yaml
name: "Engineering Manager"
model:
  provider: "openai"
  model: "gpt-4-turbo"
  temperature: 0.7
prompt_files:
  - system-prompt.md       # Core behavior
  - coding-standards.md    # Team standards
  - review-criteria.md     # What to check
  - escalation-policy.md   # When to escalate
  - company-values.md      # Cultural context
```

### 2. Workflow YAML Schema
**Rationale:** Declarative workflows are easier to create and modify than code.

**Example:**
```yaml
# workflows/sdlc/workflow.yaml
name: "Software Development Lifecycle"
version: "1.0"

steps:
  - id: "requirements"
    name: "Requirements Gathering"
    agent: "product-manager"
    outputs: ["requirements_doc"]
    transitions:
      - to: "design"
        condition: "approved_by_manager"

  - id: "design"
    name: "Technical Design"
    agent: "architect"
    inputs: ["requirements_doc"]
    outputs: ["design_doc"]
    transitions:
      - to: "implementation"
        condition: "approved_by_manager"

  - id: "implementation"
    name: "Code Implementation"
    agent: "programmer"  # This is the IDE
    inputs: ["design_doc"]
    outputs: ["code"]
    approvals:
      - agent: "manager"
        type: "review"
    transitions:
      - to: "testing"
        condition: "manager_approved"

  - id: "testing"
    name: "QA Testing"
    agent: "qa-engineer"
    inputs: ["code"]
    approvals:
      - agent: "manager"
        type: "sign_off"
    transitions:
      - to: "complete"
        condition: "tests_passed"
```

### 3. Job Definition Schema
**Rationale:** Jobs bind work to workflows and provide all necessary context.

**Example:**
```yaml
# jobs/build-auth-system/index.yaml
id: "build-auth-system"
title: "Build Authentication System"
workflow: "sdlc"
priority: "high"
assigned_to: "programmer"  # Which agent can claim this

context_files:
  - overview.md
  - requirements.md
  - technical-specs.md
  - security-requirements.md
  - api-contracts.md
  - database-schema.md
  - testing-criteria.md

metadata:
  created_by: "product-manager-agent"
  created_at: "2024-01-01T00:00:00Z"
  deadline: "2024-01-15T00:00:00Z"
```

### 4. LLM Provider Abstraction
**Rationale:** Support multiple LLM providers without changing agent logic.

**Interface:**
```python
class BaseLLMAdapter(ABC):
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[str, AsyncIterator[str]]:
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        pass
```

### 5. Concurrent User Handling
**Rationale:** Multiple users working simultaneously must not interfere.

**Strategy:**
- FastAPI async handlers
- Per-request session lookup
- User-scoped state storage
- Qdrant filtering by user_id
- Independent LLM API calls per user

---

## MCP Tool Specifications

### Tool: `get_available_jobs`
```json
{
  "name": "get_available_jobs",
  "description": "List all jobs available for the current agent to work on",
  "inputSchema": {
    "type": "object",
    "properties": {
      "filter": {
        "type": "string",
        "description": "Optional filter (e.g., 'high-priority')"
      }
    }
  }
}
```

### Tool: `start_job`
```json
{
  "name": "start_job",
  "description": "Initialize a job and load its workflow",
  "inputSchema": {
    "type": "object",
    "properties": {
      "job_id": {
        "type": "string",
        "description": "ID of the job to start"
      }
    },
    "required": ["job_id"]
  }
}
```

### Tool: `get_current_task`
```json
{
  "name": "get_current_task",
  "description": "Get the current task based on workflow state",
  "inputSchema": {
    "type": "object",
    "properties": {}
  }
}
```

### Tool: `submit_work`
```json
{
  "name": "submit_work",
  "description": "Submit completed work for the current step",
  "inputSchema": {
    "type": "object",
    "properties": {
      "work_description": {
        "type": "string",
        "description": "Description of completed work"
      },
      "artifacts": {
        "type": "array",
        "items": {"type": "string"},
        "description": "File paths or references to created artifacts"
      }
    },
    "required": ["work_description"]
  }
}
```

### Tool: `request_review`
```json
{
  "name": "request_review",
  "description": "Request review/approval from another agent",
  "inputSchema": {
    "type": "object",
    "properties": {
      "reviewer_agent": {
        "type": "string",
        "description": "Agent to request review from (default: workflow-defined)"
      },
      "review_context": {
        "type": "string",
        "description": "Additional context for the reviewer"
      }
    }
  }
}
```

### Tool: `query_context`
```json
{
  "name": "query_context",
  "description": "Search the codebase vector database for relevant context",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Natural language search query"
      },
      "limit": {
        "type": "number",
        "description": "Max results to return",
        "default": 5
      }
    },
    "required": ["query"]
  }
}
```

### Tool: `get_agent_guidance`
```json
{
  "name": "get_agent_guidance",
  "description": "Ask another agent for guidance or consultation",
  "inputSchema": {
    "type": "object",
    "properties": {
      "agent_id": {
        "type": "string",
        "description": "Agent to consult (e.g., 'manager', 'architect')"
      },
      "question": {
        "type": "string",
        "description": "Question to ask the agent"
      }
    },
    "required": ["agent_id", "question"]
  }
}
```

---

## Azure Deployment Architecture

### Components
```
Azure Container Registry
  ↓
Azure Container Instances / AKS
  ├── AgentParty Container (FastAPI MCP Server)
  └── Qdrant Container
  
Azure Storage Account
  └── Blob Storage (agents/, workflows/, jobs/)
  
Azure Key Vault
  └── LLM API Keys, Secrets
  
Azure Monitor
  └── Logs, Metrics, Alerts
```

### Scaling Strategy
- **Horizontal Scaling:** Multiple MCP server instances behind load balancer
- **Session Affinity:** Sticky sessions or Redis-based session store
- **Qdrant Clustering:** Qdrant cluster for high availability
- **Caching:** Redis for workflow states, agent definitions

---

## Security Considerations

### Multi-User Isolation
- [ ] Session token validation on every request
- [ ] User ID verification in all DB queries
- [ ] No cross-user data leakage in vector search
- [ ] Audit logging per user action

### API Security
- [ ] API key authentication for MCP connections
- [ ] Rate limiting per user
- [ ] Input validation on all tools
- [ ] LLM API key rotation

### Data Protection
- [ ] Encryption at rest (Azure Storage)
- [ ] Encryption in transit (TLS)
- [ ] Secrets in Azure Key Vault
- [ ] No PII in logs

---

## Performance Targets

- **MCP Tool Latency:** < 2s for simple queries, < 10s for agent consultations
- **Vector Search:** < 500ms for semantic search
- **Concurrent Users:** Support 50+ simultaneous users
- **LLM Request Timeout:** 60s max
- **Session TTL:** 24 hours

---

## Next Steps

1. **Review this architecture document** and confirm all requirements are captured
2. **Prioritize checklist items** - which phases to implement first
3. **Create example definitions** - sample agent, workflow, and job
4. **Begin implementation** starting with Phase 1

---

## Open Questions

1. **Authentication Method:** API keys, OAuth, or simple tokens for MCP connections?
2. **Session Storage:** In-memory only or Redis for persistence?
3. **Qdrant Strategy:** Per-user collections or shared collection with filters?
4. **LLM Cost Controls:** Budget limits per user? Default models?
5. **Workflow Complexity:** Do we need parallel steps, loops, or conditional branching?

---

**Status:** Architecture defined, awaiting approval to proceed with implementation.
