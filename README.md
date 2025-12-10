# AgentParty MCP Platform

A Model Context Protocol (MCP) server that enables multi-agent LLM workflows for IDE-based development. Connect your IDE (VS Code/Windsurf) as a Programmer agent and collaborate with AI Manager, QA, and Product Manager agents to complete structured workflows.

## Features

- 🤖 **Multi-Agent System**: Your IDE plays one role while MCP orchestrates other AI agents
- 🔄 **Workflow Engine**: Define complex software development lifecycles with YAML
- 📁 **Directory-Based Definitions**: Agents, workflows, and jobs defined in simple file structures
- 🧠 **Vector Database**: Semantic search over codebases with Qdrant
- 👥 **Multi-User Isolation**: Each user has isolated context and workflow state
- 💰 **Budget Controls**: Per-user spending limits for LLM API calls
- 🐳 **Docker-Based**: Easy deployment with Docker Compose

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI or Anthropic API key
- VS Code with MCP support or Windsurf

### Setup

1. **Clone and configure**
   ```bash
   cd c:/src/Playground/AgentParty
   cp .env.example .env
   # Edit .env and add your API keys
   ```

2. **Start development environment**
   ```bash
   docker-compose --profile dev up -d
   ```

3. **Verify services**
   ```bash
   # Check all services are healthy
   docker-compose ps
   
   # Test MCP server
   curl http://localhost:8000/health
   ```

4. **Connect your IDE**
   
   Add to your MCP settings (VS Code/Windsurf):
   ```json
   {
     "mcpServers": {
       "agentparty": {
         "url": "http://localhost:8000/mcp"
       }
     }
   }
   ```

## Architecture

```
Your IDE (Programmer Agent)
    ↓ MCP Protocol
AgentParty Server
    ├── Manager Agent (GPT-4)
    ├── QA Agent (GPT-4)
    └── Product Manager Agent (Claude)
    ↓
Vector DB (Qdrant) + Session Store (Redis)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete design documentation.

## Directory Structure

```
agents/          # Agent definitions with multi-file prompts
workflows/       # Workflow YAML definitions
jobs/            # Job specifications with context
src/             # Python source code
tests/           # Test suite
```

## Usage Example

**In your IDE:**

1. **Get available jobs**
   ```
   > What jobs can I work on?
   [MCP queries get_available_jobs]
   → "build-auth-system", "fix-login-bug"
   ```

2. **Start a job**
   ```
   > Start the build-auth-system job
   [MCP calls start_job("build-auth-system")]
   → Workflow loaded: "Software Development Lifecycle"
   → Current step: "Review specifications"
   ```

3. **Get your task**
   ```
   > What should I do?
   [MCP calls get_current_task]
   → "Implement authentication module per specs..."
   ```

4. **Submit work for review**
   ```
   > I've completed the auth module
   [MCP calls submit_work(...)]
   → Manager agent reviews code...
   → Manager: "Looks good, but add rate limiting"
   ```

## Creating Custom Agents

Create a directory in `agents/`:

```
agents/my-agent/
├── index.yaml              # Model config
├── system-prompt.md        # Core behavior
├── knowledge-base.md       # Domain knowledge
└── guidelines.md           # Additional context
```

See [docs/guides/creating-agents.md](docs/guides/creating-agents.md) for details.

## Creating Workflows

Create a directory in `workflows/`:

```
workflows/my-workflow/
├── workflow.yaml           # State machine definition
└── description.md          # Overview
```

See [docs/guides/creating-workflows.md](docs/guides/creating-workflows.md) for details.

## Creating Jobs

Create a directory in `jobs/`:

```
jobs/my-job/
├── index.yaml              # Workflow reference
├── overview.md             # What to build
├── requirements.md         # Specifications
└── context-*.md            # Supporting docs
```

See [docs/guides/creating-jobs.md](docs/guides/creating-jobs.md) for details.

## Development

### Run tests
```bash
docker-compose exec agentparty-dev pytest
```

### View logs
```bash
docker-compose logs -f agentparty-dev
```

### Hot reload
The dev container automatically reloads on code changes.

### Access services
- MCP Server: http://localhost:8000
- Qdrant UI: http://localhost:6333/dashboard
- Redis: localhost:6379

## Production Deployment

### Local Production Build
```bash
docker-compose --profile prod up -d
```

### Azure Deployment

See [docs/guides/deployment-azure.md](docs/guides/deployment-azure.md) for complete Azure deployment guide.

## Configuration

Key environment variables (see `.env.example`):

- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key  
- `DEFAULT_USER_BUDGET`: Per-user spending limit (USD)
- `SESSION_TTL_HOURS`: Session expiration time
- `REDIS_URL`: Redis connection string
- `QDRANT_URL`: Qdrant connection string

## MCP Tools

The server exposes these tools to your IDE:

- `get_available_jobs` - List available jobs
- `start_job` - Initialize a job and workflow
- `get_current_task` - Get next task
- `submit_work` - Submit completed work
- `request_review` - Request agent approval
- `query_context` - Search codebase
- `get_agent_guidance` - Ask another agent

## Budget Management

Each user has a configurable budget limit:

- Default: $100/month
- Warning at 80% usage
- Requests blocked at 100%
- Auto-resets monthly

View your usage:
```
> How much of my budget have I used?
[MCP queries budget status]
```

## Troubleshooting

### Services won't start
```bash
docker-compose down
docker-compose --profile dev up -d --build
```

### Cannot connect to MCP
- Check `.env` has valid API keys
- Verify all services are healthy: `docker-compose ps`
- Check logs: `docker-compose logs agentparty-dev`

### Agent not responding
- Check LLM API key is valid
- Verify agent definition exists in `agents/` directory
- Check logs for errors

## Contributing

Contributions welcome! Please:

1. Follow existing code style (Black, Ruff)
2. Add tests for new features
3. Update documentation
4. Submit PRs with clear descriptions

## License

MIT License - see LICENSE file

## Support

- GitHub Issues: [Report bugs](https://github.com/yourorg/agentparty/issues)
- Documentation: [Full docs](docs/)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Status:** In active development. See [ARCHITECTURE.md](ARCHITECTURE.md) for implementation checklist.
